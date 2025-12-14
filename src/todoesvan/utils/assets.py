from pathlib import Path

# src/todoesvan/utils/assets.py
BASE_DIR = Path(__file__).resolve().parents[2]  # .../src
ASSETS_DIR = BASE_DIR / "assets"

def asset_path(relative_path: str) -> str:
    """
    Returns an absolute path to an asset inside src/assets.
    """
    return str(ASSETS_DIR / relative_path)
