"""Independent verifier for the axial ell2 all-m bounded completion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.schema.json"


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
    s0, s1 = sp.symbols("S0 S1")
    zero = sp.Matrix([[2, 0, 2, 0], [0, -2, 0, -2], [2, 0, 2, 0], [0, -2, 0, -2]])
    correction = sp.Matrix([s0 / 2, -s1 / 2, 0, 0])
    assert zero * correction == sp.Matrix([s0, s1, s0, s1])
    assert value["second_order_theorem"]["bounded_or_finite_quasiperiodic"] is True
    assert value["classification"]["prior_polynomial_Jordan_caveat_removed"] is True
    assert value["classification"]["polar_input_parity_classified"] is False


if __name__ == "__main__":
    main()
