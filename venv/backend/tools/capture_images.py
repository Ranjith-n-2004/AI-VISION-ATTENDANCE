"""
Webcam Image Capture Tool for Dataset Creation

Usage examples:
    python capture_images.py Ranjith_N 1TD24CS227
    python capture_images.py "Ranjith N" 1TD24CS227
    python capture_images.py Ranjith_N_(1TD24CS227)

Controls:
    SPACE - Capture image
    ESC   - Quit
"""
import cv2
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
        # Use central settings and naming helpers
        from config.settings import DATASET_DIR
        from backend.utils.dataset_manager import ensure_person_dir
except Exception:
        # Fallbacks if imports fail
        DATASET_DIR = Path(__file__).resolve().parent / "database" / "dataset"
        def ensure_person_dir(base: Path, name: str, user_id: str) -> Path:
                safe = f"{name.strip().replace(' ', '_')}_({user_id.strip()})"
                p = base / safe
                p.mkdir(parents=True, exist_ok=True)
                return p

def _parse_args() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (name, user_id, raw_folder). If user provides a single combined folder name,
    it'll be returned as raw_folder; otherwise name/user_id will be set.
    """
    name: Optional[str] = None
    user_id: Optional[str] = None
    raw: Optional[str] = None
    if len(sys.argv) >= 3:
        name = sys.argv[1]
        user_id = sys.argv[2]
    elif len(sys.argv) == 2:
        raw = sys.argv[1]
    else:
        # interactive prompt
        choice = input("Provide (1) Name & ID or (2) Raw folder name? [1/2]: ").strip() or "1"
        if choice == "2":
            raw = input("Enter folder name (e.g., Ranjith_N_(1TD24CS227)): ").strip()
        else:
            name = input("Enter Name (e.g., Ranjith N): ").strip()
            user_id = input("Enter ID (e.g., 1TD24CS227): ").strip()
    return name or None, user_id or None, raw or None


def main():
    name, user_id, raw = _parse_args()
    if not any([raw, (name and user_id)]):
        print("Error: Provide either Name+ID or a raw folder name.")
        return

    # Resolve dataset folder path using centralized location
    base = Path(DATASET_DIR)
    if raw:
        folder = base / raw
        folder.mkdir(parents=True, exist_ok=True)
    else:
        folder = ensure_person_dir(base, name, user_id)
    
    # Count existing images
    count = len(list(folder.glob('*'))) + 1
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print(f"\n📸 Capture Tool Started")
    print(f"Saving to: {folder}")
    print(f"Starting from image: {count:03d}.jpg")
    print("\nControls:")
    print("  SPACE - Capture image")
    print("  ESC   - Quit")
    print("\nTip: Capture 10-30 images with different:")
    print("  - Head angles (frontal, left, right)")
    print("  - Expressions (neutral, smile)")
    print("  - Lighting conditions")
    print("  - Distances from camera\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame")
            break
        
        # Show preview
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Images captured: {count - 1}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, "SPACE=Capture | ESC=Quit", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.imshow("Capture Images - Press SPACE to capture", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            img_path = folder / f"{count:03d}.jpg"
            cv2.imwrite(str(img_path), frame)
            print(f"✓ Saved: {img_path.name}")
            count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    total_images = count - 1
    print(f"\n✅ Capture complete! Total images: {total_images}")
    if total_images < 5:
        print("⚠️  Warning: Minimum 5-10 images recommended for good accuracy")
    print(f"\nNext steps:")
    print(f"1. Open http://localhost:8000/attendance")
    print(f"2. Click 'Build Encodings' button or call /api/encodings/build")
    print(f"3. Wait for status to show 'success'")

if __name__ == "__main__":
    main()
