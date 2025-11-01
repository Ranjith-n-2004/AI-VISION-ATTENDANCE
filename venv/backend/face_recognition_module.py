"""Thin wrappers around face_recognition for detection/encodings."""
from typing import List, Tuple
import numpy as np


def detect_and_encode(frame_bgr: np.ndarray):
    import cv2
    try:
        import face_recognition
    except Exception:
        return [], []
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, boxes)
    return boxes, encs
