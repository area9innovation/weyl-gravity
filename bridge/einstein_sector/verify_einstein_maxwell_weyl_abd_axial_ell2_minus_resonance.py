"""Independent verifier for the axial ell2 Einstein-minus global resonance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for key in ("generator", "direct_helper"):
        path = ROOT / value["provenance"][f"{key}_path"]
        assert value["provenance"][f"{key}_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    time = sp.symbols("t", real=True)
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    pivots = [
        12 * sp.I * (3 * root - 1) * frequency,
        24 * sp.I * (3 * root - 1) * frequency,
        12 * sp.I * (3 * root - 1) * frequency,
    ]
    assert all(pivot != 0 for pivot in pivots)
    a, b, d = sp.symbols("a b d")
    polynomials = value["shell_pairing"]["polynomials"]
    local = {"t": time, "sqrt": sp.sqrt, "I": sp.I}
    combined = sum(coefficient * sp.sympify(polynomials[name], locals=local) for coefficient, name in ((a, "a"), (b, "b"), (d, "d")))
    poly = sp.Poly(sp.expand(combined), time)
    assert poly.nth(2).coeff(b) != 0
    assert poly.nth(1).coeff(a) != 0
    assert sp.sympify(polynomials["d"], locals=local) != 0
    classification = value["classification"]
    assert classification["bounded_cross_ideal_classified"] is True
    assert classification["complete_bounded_cone_solved"] is False


if __name__ == "__main__":
    main()
