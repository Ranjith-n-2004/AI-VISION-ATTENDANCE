"""Utilities to build and load face encodings.

Primary backend: facenet-pytorch (GPU-friendly). Falls back to face_recognition if facenet is not available.
The encodings file is a pickle mapping: label -> list of numpy arrays (embeddings).
"""
from pathlib import Path
import pickle
import os
from typing import Dict, List

try:
    import torch
    from facenet_pytorch import InceptionResnetV1, MTCNN
    BACKEND = 'facenet'
except Exception:
    BACKEND = 'face_recognition'

import numpy as np
from PIL import Image


def build_encodings(dataset_dir: str, out_path: str, device: str = 'cpu') -> None:
    """Scan dataset_dir where each subfolder is label (name_usn) and compute embeddings.
    Saves the encodings to out_path (pickle).
    """
    dataset_dir = Path(dataset_dir)
    out_path = Path(out_path)
    encodings = {}

    if BACKEND == 'facenet':
        # Initialize MTCNN for detection + InceptionResnet for embeddings
        mtcnn = MTCNN(keep_all=False, device=device)
        resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

        for person_dir in dataset_dir.iterdir():
            if not person_dir.is_dir():
                continue
            label = person_dir.name
            embeddings = []
            for img_path in person_dir.glob('*'):
                try:
                    img = Image.open(img_path).convert('RGB')
                    # detect and crop face
                    face = mtcnn(img)
                    if face is None:
                        continue
                    # face is a tensor (C,H,W)
                    with torch.no_grad():
                        emb = resnet(face.unsqueeze(0).to(device))
                    emb = emb.detach().cpu().numpy().reshape(-1)
                    embeddings.append(emb)
                except Exception as e:
                    print(f"Skipping {img_path}: {e}")
            if embeddings:
                encodings[label] = [e.tolist() for e in embeddings]

    else:
        # Fallback: use face_recognition library
        import face_recognition
        for person_dir in dataset_dir.iterdir():
            if not person_dir.is_dir():
                continue
            label = person_dir.name
            embeddings = []
            for img_path in person_dir.glob('*'):
                try:
                    img = face_recognition.load_image_file(str(img_path))
                    locs = face_recognition.face_locations(img)
                    if not locs:
                        continue
                    enc = face_recognition.face_encodings(img, known_face_locations=locs)[0]
                    embeddings.append(enc.tolist())
                except Exception as e:
                    print(f"Skipping {img_path}: {e}")
            if embeddings:
                encodings[label] = embeddings

    # save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as f:
        pickle.dump({'backend': BACKEND, 'encodings': encodings}, f)

    print(f"Encodings saved to {out_path} using backend={BACKEND}")


def load_encodings(path: str):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Encodings file not found: {path}")
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data  # dict with 'backend' and 'encodings'
