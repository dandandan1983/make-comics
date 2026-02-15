import os
import base64
from typing import List, Dict, Any, Optional
import httpx

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OLLAMA_IMAGE_URL = os.environ.get("OLLAMA_IMAGE_URL")

async def generate_images_openai(prompt: str, n: int = 1, size: str = "1024x1024") -> List[str]:
    """Return list of base64-encoded images using OpenAI Images API.

    If `OPENAI_API_KEY` is not set this will raise.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")

    url = "https://api.openai.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "n": n, "size": size, "response_format": "b64_json"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

    images_b64: List[str] = []
    for item in data.get("data", []):
        b64 = item.get("b64_json") or item.get("b64")
        if not b64:
            continue
        images_b64.append(b64)
    return images_b64

async def generate_images_ollama(prompt: str, n: int = 1, model: Optional[str] = None) -> List[str]:
    """Call a user-provided Ollama or local image generation HTTP endpoint.

    This function expects `OLLAMA_IMAGE_URL` to be set (e.g. http://localhost:PORT/generate-image)
    and that endpoint returns JSON {"images": ["<base64>", ...]}.
    """
    url = OLLAMA_IMAGE_URL or os.environ.get("OLLAMA_IMAGE_URL")
    if not url:
        raise RuntimeError("OLLAMA_IMAGE_URL not configured")

    payload: Dict[str, Any] = {"prompt": prompt, "n": n}
    if model:
        payload["model"] = model

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()

    images = data.get("images") or data.get("results") or []
    return images
