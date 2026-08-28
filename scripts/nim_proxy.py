import os
import sys
import json
import httpx
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add parent dir to path to import nim package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.local_client import LocalLLMClient, ROLE_MODEL_MAP

load_dotenv()

app = FastAPI(title="NIM OpenAI Proxy", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the 7 keys from env
keys = [
    os.environ.get(f"NIM_API_KEY_{i}")
    for i in range(1, 8)
]
key_manager = NIMKeyManager(keys)

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

def determine_role(model_name: str) -> ModelRole:
    model_name = model_name.lower()
    if "coder" in model_name or "copilot" in model_name:
        return ModelRole.CODER
    elif "gpt-4" in model_name or "claude-3-opus" in model_name or "pro" in model_name or "glm" in model_name:
        return ModelRole.COMPLEX
    elif "gpt-3" in model_name or "mini" in model_name or "haiku" in model_name or "minimax" in model_name:
        return ModelRole.EFFICIENT
    else:
        # Default to coder for unlimited experimentation
        return ModelRole.CODER

@app.get("/v1/models")
async def list_models():
    models = []
    # Return both the standard models and aliases
    for role, model_id in ROLE_MODEL_MAP.items():
        models.append({"id": model_id, "object": "model", "owned_by": "nvidia", "role": role.value})
    
    # Add common aliases for Copilot/IDEs
    models.append({"id": "gpt-4o", "object": "model", "owned_by": "nvidia-proxy"})
    models.append({"id": "gpt-3.5-turbo", "object": "model", "owned_by": "nvidia-proxy"})
    models.append({"id": "claude-3.5-sonnet", "object": "model", "owned_by": "nvidia-proxy"})
    
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model", "qwen/qwen2.5-coder-32b-instruct")
    
    # Route model if it's an alias
    if model_name not in ROLE_MODEL_MAP.values():
        role = determine_role(model_name)
        actual_model = ROLE_MODEL_MAP[role]
        body["model"] = actual_model
    else:
        # Find the role for the requested actual model
        role = next((r for r, m in ROLE_MODEL_MAP.items() if m == model_name), ModelRole.CODER)
    
    # Get the best key for this role
    api_key = key_manager.get_key_for_role(role)
    if not api_key:
        raise HTTPException(status_code=503, detail="No healthy API keys available")

    headers = {
        "Authorization": f"Bearer {api_key.key_value}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream" if body.get("stream") else "application/json"
    }

    async def stream_generator():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST", 
                f"{NIM_BASE_URL}/chat/completions",
                headers=headers,
                json=body
            ) as response:
                if response.status_code != 200:
                    api_key.mark_unhealthy()
                    error_msg = await response.aread()
                    yield f"data: {{\"error\": \"Proxy error: {response.status_code}\"}}\n\n"
                    return
                    
                async for chunk in response.aiter_text():
                    yield chunk

    if body.get("stream"):
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{NIM_BASE_URL}/chat/completions",
                headers=headers,
                json=body
            )
            if response.status_code != 200:
                api_key.mark_unhealthy()
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
