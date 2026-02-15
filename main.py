import os
import uuid
import base64
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiofiles
from utils import make_output_dir
from image_generators import generate_images_openai, generate_images_ollama
from llm import refine_prompt_openai, refine_prompt_ollama

app = FastAPI()

# Serve saved images
os.makedirs("comix_images", exist_ok=True)
app.mount("/comix_images", StaticFiles(directory="comix_images"), name="comix_images")


class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = "openai"  # image provider: openai or ollama
    n: Optional[int] = 1
    model: Optional[str] = None
    # LLM options for refining prompt
    refine: Optional[bool] = True
    llm_provider: Optional[str] = "openai"  # llm provider: openai or ollama
    llm_model: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index():
    path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
        content = await f.read()
    return HTMLResponse(content)


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if not req.prompt:
        raise HTTPException(status_code=400, detail="prompt required")

    out_dir = make_output_dir()
    images_b64: List[str] = []

    # Optionally refine the prompt server-side using an LLM
    final_prompt = req.prompt
    if req.refine:
        try:
            if req.llm_provider == "openai":
                final_prompt = await refine_prompt_openai(req.prompt, model=req.llm_model or "gpt-4o-mini")
            elif req.llm_provider == "ollama":
                final_prompt = await refine_prompt_ollama(req.prompt, model=req.llm_model)
            else:
                # unknown llm provider; keep original prompt
                final_prompt = req.prompt
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM refine error: {e}")

    try:
        if req.provider == "openai":
            images_b64 = await generate_images_openai(final_prompt, n=req.n or 1)
        elif req.provider == "ollama":
            images_b64 = await generate_images_ollama(final_prompt, n=req.n or 1, model=req.model)
        else:
            raise HTTPException(status_code=400, detail="unknown provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    saved_urls = []
    for idx, b64 in enumerate(images_b64):
        try:
            image_bytes = base64.b64decode(b64)
        except Exception:
            # if provider returned a URL instead of b64, try to fetch it
            if b64.startswith("http"):
                # fetch and save
                import httpx

                r = httpx.get(b64, timeout=30.0)
                r.raise_for_status()
                image_bytes = r.content
            else:
                continue

        filename = f"img_{idx + 1}.jpg"
        filepath = os.path.join(out_dir, filename)
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(image_bytes)

        # build public URL
        rel_path = filepath.replace("\\", "/")
        public_url = f"/comix_images/{rel_path.split('/comix_images/',1)[1]}"
        saved_urls.append(public_url)

    return JSONResponse({"images": saved_urls, "dir": out_dir})
