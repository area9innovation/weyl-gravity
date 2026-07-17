"""Independent verifier for the exceptional polar ell=1 quotient."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell1_k0_operator.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    source = payload["provenance"]["input"]
    assert _sha256(ROOT / source["path"]) == source["sha256"]
    omega = sp.symbols("omega")
    raw = sp.Matrix([[sp.sympify(value) for value in row] for row in payload["operator_theorem"]["raw_action_Hessian"]])
    gauge = sp.Matrix([sp.sympify(value) for value in payload["exceptional_harmonic_geometry"]["gauge_column"]])
    assert (raw * gauge).applyfunc(sp.factor) == sp.zeros(4, 1)
    reduced = raw[:3, :3]
    assert sp.factor(reduced.det()) == (omega - 2) * (omega + 2) * (3 * omega**2 - 4) / 2
    assert reduced.subs(omega, 0).det() != 0
    assert payload["operator_theorem"]["zero_frequency_fibre"]["left_cokernel_dimension"] == 0


if __name__ == "__main__":
    verify_certificate()
