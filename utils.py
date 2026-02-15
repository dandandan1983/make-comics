import os
from datetime import datetime
from pathlib import Path
import uuid

def make_output_dir(base: str = "comix_images") -> str:
    now = datetime.utcnow()
    parts = [
        base,
        f"{now.year}",
        f"{now.month:02d}",
        f"{now.day:02d}",
        now.strftime("%H_%M_%S"),
    ]
    path = Path(os.path.join(*parts))
    path.mkdir(parents=True, exist_ok=True)
    # add short uuid suffix to avoid collisions when needed
    final = path / str(uuid.uuid4())
    final.mkdir(parents=True, exist_ok=True)
    return str(final)

def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
