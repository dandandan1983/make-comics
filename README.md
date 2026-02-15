# make-comics Python backend

Minimal FastAPI backend + simple frontend to generate and store comic images locally.

Setup

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Environment variables (create a `.env` file)

- `OPENAI_API_KEY` (optional) — for OpenAI Images API
- `OLLAMA_IMAGE_URL` (optional) — if you have a local/remote image generation service supporting simple POST returning base64 images

Run

```bash
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000` to use the simple frontend.

Storage

Generated images are saved under `comix_images/{year}/{month}/{day}/{hh_mm_ss}/`.
