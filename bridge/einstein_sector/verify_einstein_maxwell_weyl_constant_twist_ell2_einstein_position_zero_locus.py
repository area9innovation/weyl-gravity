"""Independent verifier for both ell=2 Einstein twist-position kernels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.schema.json"


def _vector(entries: list[str]) -> sp.Matrix:
    omega = sp.symbols("omega", positive=True, real=True)
    return sp.Matrix([sp.sympify(entry, locals={"sqrt": sp.sqrt, "omega": omega}) for entry in entries])


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    assert provenance["direct_source_sha256"] == hashlib.sha256((ROOT / provenance["direct_source_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    theorem = value["projection_theorem"]
    omega = sp.symbols("omega", positive=True, real=True)
    root = sp.sqrt(3)
    adjoints = {
        "minus": {
            "omega_squared": 6 - 2 * root,
            "axial": sp.Matrix([0, -2, 0, 2 * root]),
            "polar": sp.Matrix([12, 0, 12 - 24 * root, 6]),
        },
        "plus": {
            "omega_squared": 6 + 2 * root,
            "axial": sp.Matrix([0, -2, 0, -2 * root]),
            "polar": sp.Matrix([12, 0, 12 + 24 * root, 6]),
        },
    }
    expected = sp.Matrix([[0, sp.Rational(216, 5)], [sp.Rational(432, 5), 0]])
    for branch in ("minus", "plus"):
        columns = []
        for input_parity in ("axial", "polar"):
            column = []
            for output_parity in ("axial", "polar"):
                raw = _vector(theorem["raw_direct_rows"][branch][input_parity][output_parity])
                pairing = sp.factor((adjoints[branch][output_parity].T * raw)[0])
                column.append(sp.factor(pairing.subs(omega**2, adjoints[branch]["omega_squared"])))
            columns.append(sp.Matrix(column))
        matrix = sp.Matrix.hstack(*columns)
        assert matrix == expected
        assert matrix.det() == -sp.Rational(93312, 25)
        assert theorem[f"{branch}_position_matrix"] == [[str(entry) for entry in matrix.row(row)] for row in range(2)]

    coefficients = [clebsch_gordan(1, 2, 2, 0, m, m) for m in range(-2, 3)]
    assert coefficients == [-sp.Rational(m, 1) / sp.sqrt(6) for m in range(-2, 3)]
    shell_operator = sp.kronecker_product(sp.diag(*coefficients), expected)
    assert shell_operator.shape == (10, 10)
    assert shell_operator.rank() == 8
    assert len(shell_operator.nullspace()) == 2
    combined = sp.diag(shell_operator, shell_operator)
    assert combined.rank() == 16
    assert len(combined.nullspace()) == 4
    assert value["classification"]["simultaneous_moment_and_all_branch_resonance_zero_locus_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_EINSTEIN_POSITION_ZERO_LOCUS independent verification: PASS")


if __name__ == "__main__":
    main()
