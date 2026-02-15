import os
from typing import Optional
import httpx

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OLLAMA_LLM_URL = os.environ.get("OLLAMA_LLM_URL") or os.environ.get("OLLAMA_IMAGE_URL")


async def refine_prompt_openai(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """Call OpenAI Chat Completions to expand/refine a user prompt into a detailed image prompt.

    Returns the refined prompt as a string.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    system = (
        "You are an image prompt engineer. Convert the user's short description into a detailed,"
        " vivid image prompt optimized for image generation models. Provide sensory details, lighting,"
        " camera/viewpoint, color palette, and any stylistic references. Reply with a single-line"
        " refined prompt only, without extra explanation."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": 300,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

    # Extract assistant content
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("No choices from OpenAI")
    content = choices[0].get("message", {}).get("content", "")
    return content.strip()


async def refine_prompt_ollama(prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
    """Call a local Ollama-like HTTP LLM endpoint to refine the prompt.

    Expected to POST JSON {"prompt": "...", "model": "...", "temperature": 0.7}
    and receive JSON {"text": "refined prompt"} or {"result": "refined prompt"}.
    """
    url = OLLAMA_LLM_URL
    if not url:
        raise RuntimeError("OLLAMA_LLM_URL not configured")

    payload = {"prompt": prompt, "temperature": temperature}
    if model:
        payload["model"] = model

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()

    # Try several common keys for returned text
    text = data.get("text") or data.get("result") or data.get("output") or ""
    if isinstance(text, list):
        text = text[0] if text else ""
    return (text or "").strip()
