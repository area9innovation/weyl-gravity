#!/usr/bin/env python3
"""Independent witness verifier for the replacement-112 mixed obstruction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION.json"
X = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-executable-unary-mixed-nilpotency-obstruction-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha(X) == certificate["payload_ref"]["sha256"]
    for reference in certificate["dependency_refs"].values():
        assert sha(ROOT / reference["path"]) == reference["sha256"]

    carrier = payload["carrier"]
    assert carrier["row_count"] == carrier["pairing_rank"] == carrier["pairing_entry_count"] == 112
    rows = carrier["rows"]
    witness = payload["mixed_nilpotency_obstruction"]["first_exact_witness"]
    assert witness["output_index"] == 27 and rows[27]["row_id"] == witness["output_row_id"] == "h_hat_star_00"
    assert witness["input_index"] == 4 and rows[4]["row_id"] == witness["input_row_id"] == "sigma"
    assert witness["input_pbw_word"] == [] and witness["time_mode"] == -2

    fixture = payload["exact_fixture"]
    assert fixture["unit_circle_checks"] == {"ca_squared_plus_sa_squared": "1", "cu_squared_plus_su_squared": "1"}
    assert fixture["nonzero_parameter_product"] != "0"
    obstruction = payload["mixed_nilpotency_obstruction"]
    assert obstruction["rod_wave_defect_count"] == 0
    assert obstruction["quotient_defect_count"] == len(obstruction["defect_entries"]) == 132
    assert obstruction["quotient_defect_matrix_position_count"] == len(obstruction["typed_defect_positions"]) == 28

    r10, r58, j = sp.symbols("r10 r58 j")
    x0, x1, x2, x3 = sp.symbols("x0 x1 x2 x3")
    expression = sp.sympify(witness["coefficient"], locals={"r10": r10, "r58": r58, "j": j, "x0": x0, "x1": x1, "x2": x2, "x3": x3})
    point = {x0: sp.Rational(3, 5), x1: sp.Rational(4, 5), x2: 0, x3: 0}
    point_value = sp.expand(expression.subs(point))
    polynomial = sp.Poly(point_value, r10, r58, j, domain=sp.QQ)
    ideal = sp.groebner([r10**2 - 10, r58**2 - 58, j**2 + 1], r10, r58, j, domain=sp.QQ)
    normal = ideal.reduce(polynomial.as_expr())[1]
    assert normal != 0
    assert sp.sstr(normal) == obstruction["first_witness_point_value"]
    assert payload["gate_disposition"]["complete_executable_replacement112_q1"] == "NO_CERTIFIED_MAP"
    print("BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION independent witness verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
