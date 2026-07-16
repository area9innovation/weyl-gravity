"""Schema verifier for the exhaustive axial full-tensor fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)


def verify_certificate() -> dict[str, object]:
    payload = build_certificate()
    jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(payload)
    if json.loads(DEFAULT_OUTPUT.read_text()) != payload:
        raise RuntimeError("committed axial full-tensor fixture is stale")
    return payload


if __name__ == "__main__":
    result = verify_certificate()
    print(result["result_id"])
