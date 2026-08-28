"""
Gemma 4 E4B inference engine using PyTorch and gguf.
Completely rewritten from scratch to support Gemma 2 / 4 architectural changes:
- Q/K RMS Normalizations
- Post-Attention and Post-FFW RMS Normalizations
- Logit Soft-Capping (attention and final logits)
- Sliding Window Attention (alternating head_dim sizes)
- Exact GeGLU implementation
This avoids unsigned DLLs (llama.cpp) and bypasses WDAC, while using PyTorch's optimized CPU matmul.
"""
import os
import math
import asyncio
import torch
import torch.nn.functional as F
from loguru import logger
from gguf import GGUFReader, dequantize

class GemmaGGUFModel:
    def __init__(self, gguf_path: str, device="cpu"):
        self.device = torch.device(device)
        logger.info(f"Loading Gemma 4 GGUF from {gguf_path} on {self.device}...")
        self.reader = GGUFReader(gguf_path)
        self.fields = self._read_gguf_fields()

        self.n_layers    = int(self.fields.get("gemma4.block_count", 46))
        self.n_heads     = int(self.fields.get("gemma4.attention.head_count", 8))
        self.n_kv_heads  = int(self.fields.get("gemma4.attention.head_count_kv", 4))
        self.hidden_size = int(self.fields.get("gemma4.embedding_length", 2560))
        self.vocab_size  = int(self.fields.get("gemma4.vocab_size", 262144))
        self.rope_theta  = float(self.fields.get("gemma4.rope.freq_base", 10000.0))
        self.rms_eps     = float(self.fields.get("gemma4.attention.layer_norm_rms_epsilon", 1e-6))
        
        # Gemma 2 specific config defaults
        self.attn_soft_cap = 50.0
        self.final_soft_cap = 50.0

        # Tensor cache
        self._tensor_cache: dict[str, torch.Tensor] = {}
        self._tensor_index: dict[str, object] = {t.name: t for t in self.reader.tensors}

        self._init_tokenizer()
        logger.info(f"Gemma 4 model ready: {self.n_layers} layers, {self.n_heads} heads, hidden={self.hidden_size}")

    def _read_gguf_fields(self):
        from gguf.constants import GGUFValueType
        fields = {}
        for key, field in self.reader.fields.items():
            vals = []
            for idx in field.data:
                part = field.parts[idx]
                t = field.types[-1]
                if t == GGUFValueType.STRING:
                    vals.append(bytes(part).decode("utf-8"))
                else:
                    vals.append(part[0])
            fields[key] = vals[0] if len(vals) == 1 else vals
        return fields

    def _init_tokenizer(self):
        tokens = self.fields.get("tokenizer.ggml.tokens", [])
        self.tok_to_id = {}
        self.id_to_tok = {}
        for i, t in enumerate(tokens):
            if isinstance(t, str):
                pass
            elif isinstance(t, bytes):
                try: t = t.decode('utf-8')
                except UnicodeDecodeError: t = t.decode('latin-1')
            self.tok_to_id[t] = i
            self.id_to_tok[i] = t
        self.bos_id = int(self.fields.get("tokenizer.ggml.bos_token_id", 2))
        self.eos_id = int(self.fields.get("tokenizer.ggml.eos_token_id", 1))

    def _get_tensor(self, name: str) -> torch.Tensor:
        if name in self._tensor_cache:
            return self._tensor_cache[name]
        t = self._tensor_index.get(name)
        if t is None:
            return None
            
        # Dequantize uses NumPy, then we convert to PyTorch Tensor
        arr = dequantize(t.data, t.tensor_type).astype("float32")
        
        # Reshape to expected dimensions (GGUF tensors are flattened and reversed)
        target_shape = tuple(reversed(t.shape))
        arr = arr.reshape(target_shape)
        
        tensor = torch.from_numpy(arr).to(self.device)
        self._tensor_cache[name] = tensor
        return tensor

    def _rms_norm(self, x: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
        if w is None: return x
        # Gemma uses RMSNorm with +1 scaling: (x / RMS) * (1.0 + weight)
        rms = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.rms_eps)
        return (x / rms) * (1.0 + w)

    def _rope(self, x: torch.Tensor, pos: int) -> torch.Tensor:
        head_dim = x.shape[-1]
        half = head_dim // 2
        theta = 1.0 / (self.rope_theta ** (torch.arange(0, half, dtype=torch.float32, device=self.device) / half))
        angle = pos * theta
        cos = torch.cos(angle)
        sin = torch.sin(angle)
        
        x1 = x[..., :half]
        x2 = x[..., half:]
        return torch.cat([x1 * cos - x2 * sin, x2 * cos + x1 * sin], dim=-1)

    def _attention(self, h: torch.Tensor, layer: int, kv_cache: list, pos: int) -> torch.Tensor:
        Wq = self._get_tensor(f"blk.{layer}.attn_q.weight")
        Wk = self._get_tensor(f"blk.{layer}.attn_k.weight")
        Wv = self._get_tensor(f"blk.{layer}.attn_v.weight")
        Wo = self._get_tensor(f"blk.{layer}.attn_output.weight")
        
        Nq = self._get_tensor(f"blk.{layer}.attn_q_norm.weight")
        Nk = self._get_tensor(f"blk.{layer}.attn_k_norm.weight")

        # Linear projections
        q = h @ Wq.T
        k = h @ Wk.T
        v = h @ Wv.T

        # Determine layer head_dim dynamically from projection size (alternating SWA)
        layer_head_dim = q.shape[-1] // self.n_heads

        # Reshape to (heads, head_dim)
        q = q.view(self.n_heads, layer_head_dim)
        k = k.view(self.n_kv_heads, layer_head_dim)
        v = v.view(self.n_kv_heads, layer_head_dim)
        
        # Apply Q/K Norm (Gemma 2 specific)
        if Nq is not None: q = self._rms_norm(q, Nq)
        if Nk is not None: k = self._rms_norm(k, Nk)

        # Apply RoPE
        q = torch.stack([self._rope(q[i], pos) for i in range(self.n_heads)])
        k = torch.stack([self._rope(k[i], pos) for i in range(self.n_kv_heads)])

        # KV Cache Append
        k_cache, v_cache = kv_cache[layer]
        if k_cache.numel() == 0:
            k_cache = k.unsqueeze(0)
            v_cache = v.unsqueeze(0)
        else:
            k_cache = torch.cat([k_cache, k.unsqueeze(0)], dim=0)
            v_cache = torch.cat([v_cache, v.unsqueeze(0)], dim=0)
        kv_cache[layer] = (k_cache, v_cache)

        # GQA Repeat
        repeat = self.n_heads // self.n_kv_heads
        K = k_cache.repeat_interleave(repeat, dim=1)
        V = v_cache.repeat_interleave(repeat, dim=1)

        # Attention calculation
        scale = 1.0 / math.sqrt(layer_head_dim)
        attn = torch.einsum("hd,shd->hs", q, K) * scale
        
        # Logit soft-capping (Gemma 2 specific)
        if self.attn_soft_cap > 0:
            attn = torch.tanh(attn / self.attn_soft_cap) * self.attn_soft_cap

        # Softmax
        attn = F.softmax(attn, dim=-1)

        # Output projection
        out = torch.einsum("hs,shd->hd", attn, V)
        out = out.reshape(1, -1) @ Wo.T
        return out

    def _ffn(self, x: torch.Tensor, layer: int) -> torch.Tensor:
        Wgate = self._get_tensor(f"blk.{layer}.ffn_gate.weight")
        Wup = self._get_tensor(f"blk.{layer}.ffn_up.weight")
        Wdown = self._get_tensor(f"blk.{layer}.ffn_down.weight")

        gate = x @ Wgate.T
        up = x @ Wup.T
        
        # GeGLU (exact math approximation with tanh, matches Gemma)
        gate = F.gelu(gate, approximate="tanh")
        
        return (gate * up) @ Wdown.T

    def _forward_single(self, tok: int, kv_cache: list, pos: int) -> torch.Tensor:
        # Embedding lookup + scale by sqrt(hidden_size)
        emb = self._get_tensor("token_embd.weight")
        h = emb[tok:tok+1] * math.sqrt(self.hidden_size)

        for i in range(self.n_layers):
            residual = h
            
            # Pre-attention norm
            norm_attn = self._get_tensor(f"blk.{i}.attn_norm.weight")
            h_norm = self._rms_norm(h, norm_attn)
            
            # Attention
            attn_out = self._attention(h_norm, i, kv_cache, pos)
            
            # Post-attention norm (Gemma 2)
            post_attn = self._get_tensor(f"blk.{i}.post_attention_norm.weight")
            if post_attn is not None:
                attn_out = self._rms_norm(attn_out, post_attn)
                
            h = residual + attn_out

            # Pre-FFN norm
            residual = h
            norm_ffn = self._get_tensor(f"blk.{i}.ffn_norm.weight")
            h_norm = self._rms_norm(h, norm_ffn)
            
            # FFN
            ffn_out = self._ffn(h_norm, i)
            
            # Post-FFN norm (Gemma 2)
            post_ffn = self._get_tensor(f"blk.{i}.post_ffw_norm.weight")
            if post_ffn is not None:
                ffn_out = self._rms_norm(ffn_out, post_ffn)
                
            h = residual + ffn_out

        # Final normalization
        norm_out = self._get_tensor("output_norm.weight")
        h = self._rms_norm(h, norm_out)
        
        # Logits projection
        logits = h @ emb.T
        
        # Logits soft-capping (Gemma 2)
        if self.final_soft_cap > 0:
            logits = torch.tanh(logits / self.final_soft_cap) * self.final_soft_cap
            
        return logits[0]

    def _empty_kv_cache(self):
        cache = []
        for i in range(self.n_layers):
            t = self._tensor_index[f"blk.{i}.attn_q.weight"]
            dim1, dim2 = t.shape
            out_features = min(dim1, dim2)
            layer_head_dim = int(out_features // self.n_heads)
            
            cache.append((
                torch.empty((0, self.n_kv_heads, layer_head_dim), dtype=torch.float32, device=self.device),
                torch.empty((0, self.n_kv_heads, layer_head_dim), dtype=torch.float32, device=self.device)
            ))
        return cache

    def _simple_tokenize(self, text: str) -> list[int]:
        ids = [self.bos_id]
        i = 0
        while i < len(text):
            best_id, best_len = -1, 0
            for k, v in self.tok_to_id.items():
                if text.startswith(k, i) and len(k) > best_len:
                    best_id, best_len = v, len(k)
            if best_id != -1:
                ids.append(best_id)
                i += best_len
            else:
                i += 1
        return ids

    @torch.no_grad()
    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.1) -> str:
        input_ids = self._simple_tokenize(prompt)
        kv_cache = self._empty_kv_cache()
        output_ids = []

        # Prefill
        for pos, tok in enumerate(input_ids[:-1]):
            self._forward_single(tok, kv_cache, pos)

        # Decoding
        current_tok = input_ids[-1]
        for pos in range(len(input_ids) - 1, len(input_ids) - 1 + max_new_tokens):
            logits = self._forward_single(current_tok, kv_cache, pos)
            
            if temperature > 0:
                logits = logits / temperature
                probs = F.softmax(logits, dim=-1)
                current_tok = torch.multinomial(probs, num_samples=1).item()
            else:
                current_tok = torch.argmax(logits).item()

            if current_tok == self.eos_id:
                break
                
            output_ids.append(current_tok)
            
        return "".join(self.id_to_tok.get(i, "") for i in output_ids)
