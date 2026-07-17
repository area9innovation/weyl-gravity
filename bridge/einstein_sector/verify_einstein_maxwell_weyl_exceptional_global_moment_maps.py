"""Independent verifier for standard exceptional/global moment maps."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_global_moment_maps.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]

    M = sp.Matrix([[0, 2, 0, -1, 0, 0], [-2, 0, 1, 0, 0, 0], [0, -1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, -2], [0, 0, 0, 0, 2, 0]])
    a, b, c, d, q, w = sp.symbols("a b c d q w", real=True)
    u = sp.Matrix([a, b, c, d, q, w])
    hu = sp.Matrix([b, 0, d, 2 * a, 0, q])
    assert sp.expand((u.T * M * hu)[0] / 2) == -a**2 - b**2 + b * d - q**2

    twist = sp.Matrix([[0, -4], [4, 0]])
    A, B = sp.symbols("A B", real=True)
    assert sp.expand((sp.Matrix([A, B]).T * twist * sp.Matrix([B, 0]))[0] / 2) == 2 * B**2
    classification = payload["classification"]
    assert classification["electric_charge_first_order_role_classified"] is True
    assert classification["extra_fourth_order_exceptional_modes_classified"] is False


if __name__ == "__main__":
    verify_certificate()
