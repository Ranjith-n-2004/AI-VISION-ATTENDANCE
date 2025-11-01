from pathlib import Path
from typing import List
import shutil
import uuid


def person_dir(base: Path, name: str, user_id: str) -> Path:
    safe = f"{name.strip().replace(' ', '_')}_({user_id.strip()})"
    return base / safe


def ensure_person_dir(base: Path, name: str, user_id: str) -> Path:
    p = person_dir(base, name, user_id)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_image_bytes(folder: Path, content: bytes, ext: str = 'jpg') -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    file = folder / f"{uuid.uuid4().hex}.{ext}"
    with open(file, 'wb') as f:
        f.write(content)
    return file


def bulk_save_images(folder: Path, images: List[bytes], ext: str = 'jpg') -> List[Path]:
    return [save_image_bytes(folder, b, ext) for b in images]
