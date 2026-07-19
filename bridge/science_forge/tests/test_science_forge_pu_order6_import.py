from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_science_forge_pu_order6_import.py"
SPEC = spec_from_file_location("verify_science_forge_pu_order6_import", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_import_certificate() -> None:
    MODULE.verify()
