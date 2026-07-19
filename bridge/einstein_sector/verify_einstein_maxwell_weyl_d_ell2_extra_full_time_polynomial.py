"""Independent verifier for the full-time d times ell2-extra polynomial."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    inputs = {}
    for name, record in provenance["inputs"].items():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        inputs[name] = json.loads(path.read_text(encoding="utf-8"))

    locals_ = {"c": sp.Integer(1), "omega": 4 / sp.sqrt(3), "I": sp.I, "sqrt": sp.sqrt}
    polar_static = sp.Matrix(
        [[sp.sympify(item, locals=locals_) for item in row] for row in inputs["static_c_primitive"]["transport_primitive"]["polar"]["source_columns"]]
    )
    assert polar_static[:, 0] == sp.zeros(8, 1)
    assert polar_static[:, 1] != sp.zeros(8, 1)
    d, z2 = sp.symbols("d z2")
    expected = d * z2 * polar_static[:, 1]
    recorded = sp.Matrix([sp.sympify(item, locals={"d": d, "z2": z2, "I": sp.I, "sqrt": sp.sqrt}) for item in value["full_time_polynomial"]["polar_combined_t_coefficient"]])
    assert (recorded - expected).applyfunc(sp.factor) == sp.zeros(8, 1)
    assert value["full_time_polynomial"]["polynomial_zero_locus_for_d_times_polar_extra_alone"] == "d*z2=0"
    classification = value["classification"]
    assert classification["polar_e2_d_extra_t_coefficient_nonzero"] is True
    assert classification["old_d_constant_adjoint_isomorphism_retained"] is True
    assert classification["old_d_result_was_complete_bounded_column"] is False
    assert classification["full_bounded_cone_solved"] is False


if __name__ == "__main__":
    main()
