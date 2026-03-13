from pathlib import Path
import shutil
from uuid import uuid4


ROOT_DIR = Path(__file__).resolve().parents[2]
TMP_ROOT = ROOT_DIR / "artifacts" / "test_tmp"


def make_temp_dir(test_case) -> Path:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"{test_case.__class__.__name__}_{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    test_case.addCleanup(shutil.rmtree, path, True)
    return path
