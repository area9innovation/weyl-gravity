"""Independent verifier for the exceptional axial ell=1 operator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell1_k0_operator.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]
    theorem = payload["operator_theorem"]
    w = sp.symbols("omega")
    reduced = sp.Matrix([[sp.sympify(value, locals={"omega": w}) for value in row] for row in theorem["nonzero_frequency_gauge_slice"]["matrix"]])
    assert sp.factor(reduced.det() - w**2 * (w**2 - 4) * (3 * w**2 - 4)) == 0
    assert theorem["zero_frequency_fibre"]["left_cokernel_dimension"] == 2
    c = payload["classification"]
    assert c["extra_fourth_order_ell1_shell_discovered"] is True
    assert c["extra_shell_frequency_squared"] == "4/3"
    assert c["ell1_positive_frequency_Lee_Wald_inertia_of_extra_mode"] is False


if __name__ == "__main__":
    verify_certificate()
