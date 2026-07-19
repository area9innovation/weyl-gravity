"""Independent verifier for the polar ell2 Einstein-minus global resonance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    for key in ("generator", "direct_helper"):
        path = ROOT / provenance[f"{key}_path"]
        assert provenance[f"{key}_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    rows = value["direct_source"]["rows"]
    time = sp.symbols("t", real=True)
    local = {"t": time, "sqrt": sp.sqrt, "I": sp.I}
    assert sp.Poly(sp.sympify(rows["b"][0], locals=local), time).nth(3) == 66
    assert sp.Poly(sp.sympify(rows["a"][0], locals=local), time).nth(2) == 198
    assert sp.Poly(sp.sympify(rows["d"][0], locals=local), time).nth(1) == 198
    assert all(sp.sympify(value, locals=local) != 0 for value in value["shell_pairing"]["polynomials"].values())
    classification = value["classification"]
    assert value["linear_input"]["direct_action_row_remainder"] == ["0", "0", "0", "0"]
    assert classification["direct_linear_input_remainder_zero"] is True
    assert classification["bounded_cross_ideal_classified"] is True
    assert classification["all_m_promoted"] is False
    assert classification["complete_bounded_cone_solved"] is False


if __name__ == "__main__":
    main()
