# -*- mode: python ; coding: utf-8 -*-
# CI-friendly spec (relative paths, onedir). Built by .github/workflows/release.yml
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

ROOT = os.getcwd()

datas = [
    (os.path.join(ROOT, 'config'), 'config'),
    (os.path.join(ROOT, 'assets'), 'assets'),
]
seed = os.path.join(ROOT, 'knowledge_base', 'seed_documents')
if os.path.isdir(seed):
    datas.append((seed, 'knowledge_base/seed_documents'))

binaries = []
hiddenimports = [
    'PySide6', 'chromadb', 'chromadb.telemetry.product.posthog',
    'chromadb.api.segment', 'hnswlib', 'pydantic', 'uvicorn', 'fastapi',
    'onnxruntime', 'llama_cpp', 'sse_starlette',
    'huggingface_hub', 'tokenizers',
    'chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2',
    'llm.local_engine', 'llm.model_bootstrap', 'llm.server_client',
]

for pkg in ('chromadb', 'llama_cpp', 'tokenizers', 'huggingface_hub'):
    try:
        d, b, h = collect_all(pkg)
        datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass

# onnxruntime: only the runtime libs + data, NOT collect_all (which drags in the
# heavy 'onnx' package whose import crashes PyInstaller's analysis).
try:
    binaries += collect_dynamic_libs('onnxruntime')
    datas += collect_data_files('onnxruntime')
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=['rthook_llama.py'],
    excludes=['torch', 'transformers', 'scipy', 'sentence-transformers', 'numpy.array_api',
              'onnx', 'onnx.reference', 'onnxscript', 'sqlcipher3'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='MediAssistPro',
    debug=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, name='MediAssistPro',
)
