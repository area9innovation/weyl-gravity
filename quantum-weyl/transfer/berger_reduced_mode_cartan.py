"""Binary verdict layer for the pinned rational Berger reduced-mode import."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Sequence

try:
    from .arity_two_cartan import ArityTwoCartanData, ArityTwoCorrectionClassification, BilinearOperator
    from .berger_rational_fixture_q2_d_import import assemble_cartan_data, build_import
except ImportError:
    from arity_two_cartan import ArityTwoCartanData, ArityTwoCorrectionClassification, BilinearOperator
    from berger_rational_fixture_q2_d_import import assemble_cartan_data, build_import


def _rank(rows: Sequence[Sequence[Fraction]]) -> int:
    reduced = [list(row) for row in rows]
    pivot_row = 0
    for column in range(len(reduced[0])):
        selected = next((row for row in range(pivot_row, len(reduced)) if reduced[row][column]), None)
        if selected is None:
            continue
        reduced[pivot_row], reduced[selected] = reduced[selected], reduced[pivot_row]
        pivot = reduced[pivot_row][column]
        reduced[pivot_row] = [value / pivot for value in reduced[pivot_row]]
        for row in range(len(reduced)):
            if row != pivot_row and reduced[row][column]:
                factor = reduced[row][column]
                reduced[row] = [value - factor * pivot_value for value, pivot_value in zip(reduced[row], reduced[pivot_row])]
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    return pivot_row


def _det3(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def validate_import_receipt(receipt: object) -> dict[str, Any]:
    if not isinstance(receipt, dict):
        raise ValueError("Berger reduced-mode import receipt is not an object")
    if (
        receipt.get("schema") != "quantum-weyl-berger-rational-fixture-q2-d-import-v1"
        or receipt.get("result_id") != "ND2_REDUCED_MODE_FIXTURE_IMPORT"
        or receipt.get("claim_status") != "CERTIFIED_REDUCED_MODE_ND2_INPUT"
        or receipt.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise ValueError("Berger reduced-mode import identity drifted")
    block = receipt.get("imported_block", {})
    if (
        block.get("row_count") != 6
        or block.get("row_ids")
        != ["delta_u_w0", "delta_N_w0", "delta_rho_w0", "E_u_w0", "E_N_w0", "E_rho_w0"]
        or block.get("degrees") != [0, 0, 0, 1, 1, 1]
        or block.get("parities") != [0, 0, 0, 1, 1, 1]
        or block.get("input_D_weights") != [0] * 6
        or block.get("output_D_weights") != [0] * 6
        or block.get("q1_nonzero_count") != 9
        or block.get("q2_nonzero_canonical_count") != 18
        or block.get("coefficient_domain") != "Q"
    ):
        raise ValueError("Berger reduced-mode imported block drifted")
    checks = receipt.get("nd2_checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise ValueError("Berger reduced-mode ND2 check dropped")
    if receipt.get("nd2_classification", {}).get("status") != "ZERO_SOURCE":
        raise ValueError("Berger reduced-mode Cartan source drifted")
    authorization = receipt.get("authorization", {})
    if authorization != {
        "reduced_mode_solver_input": True,
        "full_support_local_q2": False,
        "nonzero_weight_D_equivariance": False,
        "physical_ND2_execution": False,
    }:
        raise ValueError("Berger reduced-mode authorization boundary was crossed")
    return receipt


@dataclass(frozen=True)
class BergerCartanVerdict:
    import_receipt: dict[str, Any]
    data: ArityTwoCartanData
    engine_classification: ArityTwoCorrectionClassification
    primitive: BilinearOperator
    q1_rank: int
    hessian_inertia: tuple[int, int, int]


def build_verdict() -> BergerCartanVerdict:
    """Run the existing exact solver on the authoritative imported block."""

    receipt = validate_import_receipt(build_import())
    data = assemble_cartan_data()
    classification = data.classify()
    if classification.status != "ZERO_SOURCE" or not classification.source.is_zero():
        raise ValueError("centered Berger block unexpectedly has a nonzero Cartan source")
    primitive = data.complex.solve_boundary(
        classification.source.scaled(-1, name="minus_A_D_2")
    )
    if primitive is None or not primitive.is_zero():
        raise AssertionError("exact solver did not return the canonical zero primitive")
    q1_rows = data.complex.q1.entries
    hessian = [list(row[:3]) for row in q1_rows[3:6]]
    if any(hessian[i][j] != hessian[j][i] for i in range(3) for j in range(3)):
        raise ValueError("Berger reduced Hessian is not symmetric")
    minors = (
        hessian[0][0],
        hessian[0][0] * hessian[1][1] - hessian[0][1] * hessian[1][0],
        _det3(hessian),
    )
    if any(value == 0 for value in minors):
        raise ValueError("Berger reduced Hessian is degenerate")
    signs = tuple(1 if value > 0 else -1 for value in minors)
    pivots = (signs[0], signs[1] * signs[0], signs[2] * signs[1])
    inertia = (pivots.count(1), pivots.count(-1), pivots.count(0))
    q1_rank = _rank(q1_rows)
    if q1_rank != 3 or inertia != (1, 2, 0):
        raise ValueError("Berger exact rank or Hessian inertia drifted")
    return BergerCartanVerdict(receipt, data, classification, primitive, q1_rank, inertia)
