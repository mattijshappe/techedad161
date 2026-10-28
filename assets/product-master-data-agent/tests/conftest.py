"""Test configuration: ensure app/ is on sys.path for peer-level imports at collection time."""
import sys
from pathlib import Path

# Add app/ to sys.path at collection time so imports resolve before fixtures run.
_app_path = str(Path(__file__).parent.parent / "app")
if _app_path not in sys.path:
    sys.path.insert(0, _app_path)
