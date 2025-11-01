from pathlib import Path
from datetime import datetime, timedelta
import csv
from typing import Optional


def resolve_csv_path(base_path: Path, daily_split: bool = False, for_date: Optional[datetime] = None) -> Path:
    """Return the CSV file path. If daily_split is True, use attendance_YYYY-MM-DD.csv next to base_path.
    base_path is used when daily_split is False (e.g., backend/attendance.csv)."""
    if not daily_split:
        return base_path
    date_obj = for_date or datetime.now()
    folder = base_path.parent
    filename = f"attendance_{date_obj.strftime('%Y-%m-%d')}.csv"
    return folder / filename


def _ensure_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "ID", "Time", "Date"])  # header


def write_attendance(path: Path, name: str, user_id: str, when: Optional[datetime] = None):
    """Append a row to the attendance CSV."""
    _ensure_file(path)
    now = when or datetime.now()
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([name, user_id, now.strftime('%I:%M:%S %p'), now.strftime('%Y-%m-%d')])


def last_logged_time(path: Path, name: str, user_id: str) -> Optional[datetime]:
    """Return the latest datetime for this name/id pair in the CSV, or None."""
    if not path.exists():
        return None
    try:
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            last_dt = None
            for row in reader:
                if row.get('Name') == name and row.get('ID') == user_id:
                    try:
                        t = row.get('Time') or ''
                        d = row.get('Date') or ''
                        dt = datetime.strptime(d + ' ' + t, '%Y-%m-%d %I:%M:%S %p')
                        if last_dt is None or dt > last_dt:
                            last_dt = dt
                    except Exception:
                        continue
            return last_dt
    except Exception:
        return None


def log_if_needed(path: Path, name: str, user_id: str, dedup_minutes: int = 10) -> bool:
    """Log attendance if last log is older than dedup_minutes. Returns True if logged."""
    prev = last_logged_time(path, name, user_id)
    now = datetime.now()
    if prev is None or now - prev >= timedelta(minutes=dedup_minutes):
        write_attendance(path, name, user_id, now)
        return True
    return False
