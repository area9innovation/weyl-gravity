"""Independent verifier for the constant-twist ell2 extra position kernel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.schema.json"


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

    matrix = sp.Matrix([[sp.sympify(entry, locals={"sqrt": sp.sqrt}) for entry in row] for row in value["multiplicity_matrix"]["P_position"]])
    kernel = [sp.Matrix([0, 0, 1, 0]), sp.Matrix([-4 * sp.sqrt(3), 0, 0, 15])]
    assert matrix.rank() == 2
    assert all(matrix * vector == sp.zeros(4, 1) for vector in kernel)
    coefficients = [clebsch_gordan(1, 2, 2, 0, m, m) for m in range(-2, 3)]
    assert coefficients == [-sp.Rational(m, 1) / sp.sqrt(6) for m in range(-2, 3)]
    operator = sp.kronecker_product(sp.diag(*coefficients), matrix)
    assert operator.shape == (20, 20)
    assert operator.rank() == 8
    assert len(operator.nullspace()) == 12
    assert value["complete_zero_locus"]["kernel_positive_frequency_complex_dimension"] == 12
    assert value["classification"]["Einstein_q_primary_twist_position_map_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
