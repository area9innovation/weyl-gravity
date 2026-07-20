"""Independent verifier for the fixed-occupation node-phase-reduced divisors."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_augmented_normal_lemma() -> None:
    hermitian = sp.diag(2, -3, 5, -7, 11)
    augmented = sp.Matrix([[1, 2, 0, 1, 0], [0, 1, 1, -1, 2], [1, 0, 0, 0, 1]])
    horizontal = sp.Matrix.hstack(*augmented.nullspace())
    restricted = horizontal.T * hermitian * horizontal
    normal = augmented * hermitian.inv() * augmented.T
    assert augmented.rank() == 3
    assert restricted.cols - restricted.rank() == normal.cols - normal.rank()


def transvectant_jacobian(point: tuple[int, ...]) -> sp.Matrix:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    equations = sp.Matrix(
        [
            [-f[3], 3 * f[2], -3 * f[1], f[0], 0],
            [-f[4], 2 * f[3], 0, -2 * f[1], f[0]],
            [0, -f[4], 3 * f[3], -3 * f[2], f[1]],
        ]
    ) * sp.Matrix(g)
    substitution = dict(zip((*f, *g), point))
    assert equations.subs(substitution) == sp.zeros(3, 1)
    return equations.jacobian((*f, *g)).subs(substitution)


def transvectant_augmented(point: tuple[int, ...]) -> tuple[sp.Matrix, sp.Matrix]:
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    ratio = sp.Rational(1, 16)
    block = sp.diag(*list((-angular).diagonal()), *list((ratio * angular).diagonal()))
    hermitian = sp.diag(block, block)
    jacobian = transvectant_jacobian(point)
    augmented = sp.zeros(8, 20)
    augmented[:3, :10] = jacobian
    augmented[3:6, 10:] = jacobian
    f = sp.Matrix(point[:5])
    g = sp.Matrix(point[5:])
    augmented[6, :5] = -f.T * angular
    augmented[6, 10:15] = -f.T * angular
    augmented[7, 5:10] = ratio * g.T * angular
    augmented[7, 15:20] = ratio * g.T * angular
    return hermitian, augmented


def verify_candidate17_20(payload: dict[str, object]) -> None:
    witness = (1, 0, 0, 0, 1, 1, 0, 1, 0, 1)
    hermitian, augmented = transvectant_augmented(witness)
    normal = augmented * hermitian.inv() * augmented.T
    horizontal = sp.Matrix.hstack(*augmented.nullspace())
    restricted = horizontal.T * hermitian * horizontal
    assert augmented.rank() == 8
    assert normal.rank() == 6
    assert horizontal.cols == 12 and restricted.rank() == 10
    assert normal.cols - normal.rank() == restricted.cols - restricted.rank() == 2

    control = (1, 1, 0, 0, 0, 1, 0, 0, 0, 0)
    control_h, control_a = transvectant_augmented(control)
    control_normal = control_a * control_h.inv() * control_a.T
    assert control_a.rank() == control_normal.rank() == 8
    assert sp.factor(control_normal.det()) == -3845153895680

    stored = payload["candidate17_20"]
    assert stored["exact_bounded_witness"]["augmented_normal_rank"] == 6
    assert stored["exact_bounded_witness"]["reduced_current_radical_complex_dimension"] == 2
    assert stored["exact_nondegenerate_control"]["augmented_normal_determinant"] == "-3845153895680"
    assert "not the product" in stored["important_nonfactorization"]


def rank_one_augmented(
    a: sp.Expr,
    c: sp.Expr,
    b: sp.Expr,
    t_first: sp.Expr,
    t_second: sp.Expr,
    *,
    alpha: int,
    second_sign: int = 1,
) -> tuple[sp.Matrix, sp.Matrix]:
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    internal = sp.Matrix([[a, c], [c, a]])
    hermitian = sp.diag(
        sp.eye(10),
        sp.kronecker_product(internal, angular),
        sp.kronecker_product(-b * sp.eye(2), angular),
    )
    point = sp.zeros(30, 1)
    point[10 + alpha] = 1
    point[15 + alpha] = second_sign
    point[20 + alpha] = t_first
    point[25 + alpha] = second_sign * t_second
    augmented = sp.zeros(10, 30)
    for channel, (f_offset, g_offset) in enumerate(((10, 20), (15, 25))):
        row = 4 * channel
        for index in range(5):
            if index == alpha:
                continue
            augmented[row, g_offset + index] = point[f_offset + alpha]
            augmented[row, f_offset + alpha] = point[g_offset + index]
            augmented[row, f_offset + index] = -point[g_offset + alpha]
            augmented[row, g_offset + alpha] = -point[f_offset + index]
            row += 1
    covector = point.T * hermitian
    augmented[8, :20] = covector[:, :20]
    augmented[9, 20:] = covector[:, 20:]
    return hermitian, augmented


def verify_candidate18(payload: dict[str, object]) -> None:
    a, c, b, t_first, t_second = sp.symbols("a c b t_1 t_2", positive=True)
    hermitian, augmented = rank_one_augmented(a, c, b, t_first, t_second, alpha=2)
    normal = sp.simplify(augmented * hermitian.inv() * augmented.T)
    determinant = sp.factor(normal.det())
    internal = a**2 - a * b * (t_first**2 + t_second**2) + b**2 * t_first**2 * t_second**2 - c**2
    expected = -sp.Rational(128, 9) * (t_first**2 + t_second**2) * internal**4 / (
        b**7 * (a - c) ** 4 * (a + c) ** 3
    )
    assert sp.factor(determinant - expected) == 0

    for sign, root in ((1, (a + c) / b), (-1, (a - c) / b)):
        branch_h, branch_a = rank_one_augmented(
            a,
            c,
            b,
            sp.sqrt(root),
            sp.sqrt(root),
            alpha=2,
            second_sign=sign,
        )
        branch_normal = sp.simplify(branch_a * branch_h.inv() * branch_a.T)
        assert branch_a.rank() == 10 and branch_normal.rank() == 6

    control = sp.factor(internal.subs({t_first: 0, t_second: 1}))
    assert control == a**2 - a * b - c**2
    stored = payload["candidate18"]
    assert stored["rank_one_chart_atlas"]["product_chart_count"] == 100
    stored_determinant = sp.sympify(
        stored["aligned_central_angular_section"]["augmented_normal_determinant"],
        locals={"a": a, "c": c, "b": b, "t_1": t_first, "t_2": t_second},
    )
    assert sp.factor(stored_determinant - expected) == 0
    assert [row["augmented_normal_rank"] for row in stored["aligned_central_angular_section"]["branch_rows"]] == [6, 6]
    assert stored["aligned_central_angular_section"]["nondegenerate_control"]["verdict"] == "STRICTLY_NEGATIVE_AND_NONZERO"


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    verify_augmented_normal_lemma()
    verify_candidate17_20(payload)
    verify_candidate18(payload)
    flags = payload["classification"]
    assert flags["common_node_phase_coupling_retained"]
    assert flags["candidate18_positive_spectators_retained"]
    assert flags["constant_corank_local_leaf_quotient_classified"]
    assert not flags["lifted_rotation_reduction_classified"]
    assert not flags["global_leaf_space_or_Hausdorff_quotient_classified"]
    assert not flags["occupation_strata_glued"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_PHASE_REDUCED_PRESYMPLECTIC_DIVISORS verifier: PASS")


if __name__ == "__main__":
    verify()
