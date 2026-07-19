#!/usr/bin/env python3
"""Independently verify the temporal clock BV cotangent lift."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_nonlinear_clock_temporal_cotangent_f2_f3 import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    canonical_sha256,
    cotangent_operators,
    deserialize_cotangent_operator,
    inverse_and_adjoint_audit,
    serialize_cotangent_operator,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    operators = cotangent_operators()
    audit = inverse_and_adjoint_audit()
    f2 = serialize_cotangent_operator(operators["P2"], 2)
    f3 = serialize_cotangent_operator(operators["P3"], 3)
    assert value["formal_adjoint_and_inverse_audit"] == audit
    assert value["taylor_payload"]["F2"] == f2
    assert value["taylor_payload"]["F3"] == f3
    assert value["taylor_payload"]["canonical_sha256"] == canonical_sha256({"F2": f2, "F3": f3})
    assert deserialize_cotangent_operator(f2, 2) == operators["P2"]
    assert deserialize_cotangent_operator(f3, 3) == operators["P3"]
    assert deserialize_cotangent_operator(f2, 2, use_full_arity_factorial=True) != operators["P2"]
    assert deserialize_cotangent_operator(f3, 3, use_full_arity_factorial=True) != operators["P3"]
    assert audit["formal_adjoint_involution_defect"]["linear"]["operator_key_count"] == 0
    assert audit["formal_adjoint_involution_defect"]["quadratic"]["operator_key_count"] == 0
    assert audit["canonical_one_form_inverse_defect"]["degree_2"]["operator_key_count"] == 0
    assert audit["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] == 0
    assert inverse_and_adjoint_audit(pointwise=True)["canonical_one_form_inverse_defect"]["degree_2"]["operator_key_count"] > 0
    assert inverse_and_adjoint_audit(omit_quadratic_inverse=True)["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] > 0
    assert inverse_and_adjoint_audit(drop_structure=True)["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] > 0
    print("BERGER_NONLINEAR_CLOCK_TEMPORAL_COTANGENT_F2_F3 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
