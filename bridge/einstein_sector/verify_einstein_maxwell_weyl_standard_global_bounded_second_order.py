"""Independent verifier for the standard global bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_standard_global_bounded_second_order.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    inputs = {
        name: json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
        for name, record in provenance["inputs"].items()
    }
    t = sp.symbols("t", real=True)
    a, b, charge, position, velocity = sp.symbols("a b Q_e A B", real=True)
    local_symbols = {"t": t, "a": a, "b": b, "Q_e": charge, "A": position, "B": velocity}
    homogeneous = inputs["homogeneous"]
    rows = {
        name: sp.sympify(expression, locals=local_symbols)
        for name, expression in zip(
            homogeneous["quadratic_source"]["row_order"],
            homogeneous["quadratic_source"]["rows"],
            strict=True,
        )
    }
    assert sp.factor(sp.expand(rows["E11"]).coeff(t, 2)) == sp.Rational(15, 2) * b**2
    assert sp.factor(sp.expand(rows["Maxwell1"].subs(b, 0)).coeff(t, 1)) == charge * a
    twist_expression = inputs["twist_source"]["theorem"]["projected_source"]["polar_L2"]["metric_00"]
    twist_row = sp.sympify(twist_expression, locals=local_symbols)
    assert sp.factor(sp.expand(twist_row).coeff(t, 2)) == -7 * velocity**2

    bx, by, bz = sp.symbols("B_x B_y B_z", real=True)
    vector = sp.Matrix([bx, by, bz])
    square = sp.expand(vector.dot(vector))
    stf = vector * vector.T - sp.eye(3) * square / 3
    assert sp.factor(sp.trace(stf.T * stf)) == sp.Rational(2, 3) * square**2
    assert value["polynomial_growth_ideal"]["real_polynomial_zero_locus"] == "b=0, B=0, Q_e*a=0"
    assert value["moment_map_intersection"]["complete_bounded_tangent_cone"] == "Z2_global^bounded={(c,d,W_x,A): c,d,W_x real, A in R^3}"
    classes = value["correction_classes"]
    assert classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    assert classes["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    classification = value["classification"]
    assert classification["universal_b_twist_velocity_and_Qe_a_elimination_on_complete_finite_carrier"] is True
    assert "Q_e*a=0" in value["universal_complete_carrier_corollary"]["statement"]
    assert classification["complete_finite_bounded_common_zero_locus_solved"] is False


if __name__ == "__main__":
    main()
