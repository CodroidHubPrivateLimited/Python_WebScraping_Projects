import importlib.util
from pathlib import Path


def _load_legacy_module():
    project_root = Path(__file__).resolve().parents[2]
    legacy_path = project_root / "Flask Backend.py"
    spec = importlib.util.spec_from_file_location("legacy_backend", legacy_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


legacy = _load_legacy_module()
