"""Independent verifier for the ell=2 constant-twist moment/resonance cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.schema.json"


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"sqrt": sp.sqrt, "I": sp.I}) for value in row] for row in rows])


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

    coordinates = value["action_normalized_coordinates"]
    gram = _matrix(coordinates["extra_Gram_G"])
    kernel = _matrix(coordinates["K_basis_columns"])
    neutral = _matrix(coordinates["K_orthogonal_neutral_basis_columns"])
    assert gram == sp.diag(1296, sp.Rational(208, 3), 9, 22464)
    assert kernel.T * gram * neutral == sp.zeros(2)
    assert sp.Matrix.hstack(kernel, neutral).rank() == 4
    assert kernel.T * gram * kernel == sp.diag(9, 5116608)
    assert neutral.T * gram * neutral == sp.diag(sp.Rational(208, 3), 5542992)

    generators = value["spin_two_generators"]
    j_plus = _matrix(generators["J_plus"])
    j_x = _matrix(generators["J_x"])
    j_y = _matrix(generators["J_y"])
    j_z = _matrix(generators["J_z"])
    assert j_x.H == j_x and j_y.H == j_y and j_z.H == j_z
    assert (j_x * j_y - j_y * j_x - sp.I * j_z).applyfunc(sp.simplify) == sp.zeros(5)
    assert j_plus == j_x + sp.I * j_y

    columns = [sp.zeros(4, 1) for _ in range(5)]
    columns[0] = kernel[:, 0]
    columns[4] = kernel[:, 0]
    amplitudes = sp.Matrix.hstack(*columns)
    density = amplitudes.T * gram * amplitudes
    assert density.trace() == 18
    assert [(density * generator).trace().simplify() for generator in (j_x, j_y, j_z)] == [0, 0, 0]
    root = sp.sqrt(3)
    minus_occupation = sp.radsimp(sp.Rational(16, 3) * density.trace() / (6 - 2 * root))
    assert sp.simplify(minus_occupation - (24 + 8 * root)) == 0

    jacobian = value["regularity_witness"]["Jacobian_diagonal"]
    diagonal = [sp.sympify(entry, locals={"sqrt": sp.sqrt}) for entry in jacobian]
    assert all(sp.simplify(entry) != 0 for entry in diagonal)
    assert value["regularity_witness"]["rank"] == 4
    assert value["common_zero_cone"]["generic_smooth_stratum_real_dimension"] == 28
    assert value["classification"]["bounded_full_second_order_equation_solved_on_common_cone"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_MOMENT_RESONANCE_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
