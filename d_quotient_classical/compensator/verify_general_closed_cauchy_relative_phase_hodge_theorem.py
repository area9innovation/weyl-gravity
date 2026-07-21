#!/usr/bin/env python3
"""Independent exact replay of the general closed-Cauchy Hodge/Gauss theorem."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/compensator/"
    "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_PAYLOAD_V1.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _mat(rows: list[list[object]], nrows: int, ncols: int) -> sp.Matrix:
    if nrows == 0 or ncols == 0:
        return sp.zeros(nrows, ncols)
    return sp.Matrix(nrows, ncols, lambda i, j: sp.Rational(str(rows[i][j])))


def _smith(matrix: sp.Matrix) -> list[int]:
    diagonal = smith_normal_form(matrix, domain=sp.ZZ)
    return [
        abs(int(diagonal[i, i]))
        for i in range(min(diagonal.rows, diagonal.cols))
        if diagonal[i, i] != 0
    ]


def _torsion_kernel_count(q: sp.Matrix, moduli: list[int]) -> int:
    answer = 1
    for modulus in moduli:
        kernel = [
            vector
            for vector in itertools.product(range(modulus), repeat=q.cols)
            if all(
                sum(int(q[i, j]) * vector[j] for j in range(q.cols)) % modulus == 0
                for i in range(q.rows)
            )
        ]
        answer *= len(kernel)
    return answer


def _check_topology(topology: dict[str, object]) -> None:
    c0, c1, c2, c3 = [int(value) for value in topology["cell_ranks_C0_C1_C2_C3"]]
    d3 = _mat(topology["boundary_d3"], c2, c3)
    d2 = _mat(topology["boundary_d2"], c1, c2)
    d1 = _mat(topology["boundary_d1"], c0, c1)
    if d2 * d3 != sp.zeros(c1, c3) or d1 * d2 != sp.zeros(c0, c2):
        raise AssertionError("cellular boundary-square failure")
    b1 = c1 - int(d1.rank()) - int(d2.rank())
    if b1 != int(topology["betti_1"]):
        raise AssertionError("cellular b1 mismatch")

    # All shipped fixtures have d3=0, so H^2=coker(d2^T).  The nonunit
    # Smith entries are precisely the torsion invariant factors.
    if d3 == sp.zeros(c2, c3):
        torsion = [value for value in _smith(d2.T) if value > 1]
        if torsion != topology["torsion_H2_invariant_factors"]:
            raise AssertionError("fixture Tor H2 mismatch")
    if math.prod(topology["torsion_H2_invariant_factors"]) != int(
        topology["flat_U1_component_count"]
    ):
        raise AssertionError("flat U1 component count mismatch")


def _check_fixture(row: dict[str, object]) -> None:
    _check_topology(row["topology"])
    n, r, rank = int(row["n"]), int(row["r"]), int(row["rank_Q"])
    q = _mat(row["Q"], n, r)
    m = _mat(row["phase_kinetic_M"], n, n)
    k_form = _mat(row["gauge_kinetic_K"], r, r)
    relative = _mat(row["relative_character_basis_N"], n, n - rank)
    active0 = _mat(row["active_gauge_complement_S"], r, rank)
    kernel = _mat(row["matter_kernel_basis_T"], r, r - rank)
    smith = _smith(q)
    if int(q.rank()) != rank or smith != row["smith_invariants"]:
        raise AssertionError(f"charge invariants failed: {row['fixture_id']}")
    if q.T * relative != sp.zeros(r, n - rank) or q * kernel != sp.zeros(n, r - rank):
        raise AssertionError(f"charge kernel failed: {row['fixture_id']}")

    if r - rank:
        k0 = kernel.T * k_form * kernel
        active = active0 - kernel * k0.inv() * kernel.T * k_form * active0
    else:
        active = active0
    ka = active.T * k_form * active
    qa = q * active
    vertical = qa.T * m * qa
    inverse_relative = relative.T * m.inv() * relative
    grel = inverse_relative.inv() if n - rank else sp.zeros(0, 0)
    horizontal = m.inv() * relative * grel if n - rank else sp.zeros(n, 0)
    lam = sp.Rational(str(row["topology"]["sample_positive_scalar_eigenvalue"]))
    nu = sp.Rational(str(row["topology"]["sample_positive_coexact_eigenvalue"]))
    longitudinal = (
        (ka.inv() + lam * vertical.inv()).inv() if rank else sp.zeros(0, 0)
    )
    longitudinal_frequency = (
        lam * sp.eye(rank) + ka.inv() * vertical if rank else sp.zeros(0, 0)
    )
    mass = q.T * m * q
    coexact_frequency = nu * sp.eye(r) + k_form.inv() * mass
    harmonic_frequency = k_form.inv() * mass
    comparisons = (
        (_mat(row["K_orthogonal_active_basis_Sperp"], r, rank), active),
        (_mat(row["effective_active_gauge_kinetic_Ka"], rank, rank), ka),
        (_mat(row["vertical_phase_Gram_V"], rank, rank), vertical),
        (_mat(row["relative_metric_Grel"], n - rank, n - rank), grel),
        (_mat(row["relative_horizontal_lift_H"], n, n - rank), horizontal),
        (_mat(row["sample_longitudinal_kinetic_after_Gauss"], rank, rank), longitudinal),
        (
            _mat(row["sample_longitudinal_frequency_squared_operator"], rank, rank),
            longitudinal_frequency,
        ),
        (_mat(row["sample_coexact_frequency_squared_operator"], r, r), coexact_frequency),
        (_mat(row["harmonic_frequency_squared_operator"], r, r), harmonic_frequency),
    )
    if any(left != right for left, right in comparisons):
        raise AssertionError(f"serialized exact matrix mismatch: {row['fixture_id']}")
    if kernel.T * k_form * active != sp.zeros(r - rank, rank):
        raise AssertionError(f"K-orthogonal split failed: {row['fixture_id']}")
    if relative.T * horizontal != sp.eye(n - rank):
        raise AssertionError(f"relative lift failed: {row['fixture_id']}")

    b1 = int(row["topology"]["betti_1"])
    smith_order = math.prod(smith)
    expected_counts = {
        "harmonic_connection_tangent_dimension": r * b1,
        "massive_harmonic_family_count": rank * b1,
        "kernel_Wilson_family_count": (r - rank) * b1,
        "relative_winding_free_rank": (n - rank) * b1,
        "finite_winding_sector_order": smith_order**b1,
    }
    if any(int(row[key]) != value for key, value in expected_counts.items()):
        raise AssertionError(f"topological count failed: {row['fixture_id']}")
    if int(row["admissible_torsion_bundle_kernel_order"]) != _torsion_kernel_count(
        q, row["topology"]["torsion_H2_invariant_factors"]
    ):
        raise AssertionError(f"torsion bundle kernel failed: {row['fixture_id']}")
    stabilizer = row["constant_gauge_stabilizer"]
    if (
        int(stabilizer["identity_torus_dimension"]) != r - rank
        or stabilizer["component_invariant_factors"] != smith
        or int(stabilizer["component_count"]) != smith_order
    ):
        raise AssertionError(f"compact stabilizer failed: {row['fixture_id']}")
    if not all(row["exact_checks"].values()):
        raise AssertionError(f"producer check ledger failed: {row['fixture_id']}")


def _check_presentation_invariance() -> None:
    """Independent unimodular charge-basis and relative-basis census."""
    q = sp.Matrix([[1, 0], [1, 0], [0, 0]])
    left = sp.Matrix([[1, 1, 0], [0, 1, 0], [0, 0, -1]])
    right = sp.Matrix([[1, 2], [0, 1]])
    transformed = left * q * right
    if abs(int(left.det())) != 1 or abs(int(right.det())) != 1:
        raise AssertionError("test basis is not unimodular")
    if _smith(q) != _smith(transformed) or q.rank() != transformed.rank():
        raise AssertionError("Smith/rank presentation invariance failed")

    m = sp.diag(2, 3, 5)
    n = sp.Matrix([[1, 0], [-1, 0], [0, 1]])
    change = sp.Matrix([[1, 1], [0, 1]])
    g = (n.T * m.inv() * n).inv()
    changed = ((n * change).T * m.inv() * (n * change)).inv()
    expected = change.inv() * g * change.inv().T
    if changed != expected:
        raise AssertionError("relative metric congruence failed")


def _check_s3_regression(result: dict[str, object]) -> None:
    imported = result["import"]
    path = ROOT / imported["path"]
    predecessor = json.loads(path.read_text())
    if (
        _sha(path) != imported["sha256"]
        or imported["actual_sha256"] != imported["sha256"]
        or imported["oracle_fields_consumed"] != []
        or predecessor["result_id"] != imported["result_id"]
    ):
        raise AssertionError("S3 predecessor import failed")
    predecessor_payload_path = ROOT / predecessor["payload_ref"]["path"]
    predecessor_payload = json.loads(predecessor_payload_path.read_text())
    row = next(
        fixture
        for fixture in predecessor_payload["fixtures"]
        if fixture["fixture_id"] == "rank_one_two_phase_counterflow_ell1"
    )
    q = _mat(row["Q"], 2, 1)
    m = _mat(row["phase_kinetic_M"], 2, 2)
    k_form = _mat(row["gauge_kinetic_K"], 1, 1)
    n = _mat(row["relative_character_basis_N"], 2, 1)
    grel = (n.T * m.inv() * n).inv()
    vertical = q.T * m * q
    lam, nu = sp.Integer(3), sp.Integer(4)
    longitudinal = (k_form.inv() + lam * vertical.inv()).inv()
    longitudinal_frequency = lam * sp.eye(1) + k_form.inv() * vertical
    coexact_frequency = nu * sp.eye(1) + k_form.inv() * vertical
    comparisons = (
        (_mat(row["relative_metric_Grel"], 1, 1), grel),
        (_mat(row["longitudinal_kinetic_after_Gauss"], 1, 1), longitudinal),
        (_mat(row["longitudinal_frequency_squared_operator"], 1, 1), longitudinal_frequency),
        (_mat(row["coexact_frequency_squared_operator"], 1, 1), coexact_frequency),
    )
    if any(left != right for left, right in comparisons):
        raise AssertionError("general theorem did not reproduce the S3 ell=1 matrix")


def verify() -> None:
    result = json.loads(RESULT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if _sha(PAYLOAD) != result["payload_ref"]["sha256"]:
        raise AssertionError("payload byte hash failed")
    canonical = _digest({key: value for key, value in payload.items() if key != "content_sha256"})
    if payload["content_sha256"] != canonical:
        raise AssertionError("payload canonical hash failed")
    for row in payload["fixtures"]:
        _check_fixture(row)
    if not any(int(row["topology"]["betti_1"]) > 0 for row in payload["fixtures"]):
        raise AssertionError("no b1-positive independent fixture")
    _check_presentation_invariance()
    _check_s3_regression(result)

    forbidden = (
        "MODEL_SPECIFIC_ACTION",
        "FULL_BV_CAUSAL_PARENT",
        "GLOBAL_GREEN_HYPERBOLICITY",
        "GRAVITY_OR_D_GAUGE",
        "HADAMARD_OR_QUANTUM",
        "CONFLUX_VERDICT",
    )
    if any(result["claim_flags"][key] for key in forbidden):
        raise AssertionError("claim boundary promoted")
    expected_hashes = {
        "hodge_sha256": _digest(result["hodge_theorem"]),
        "gauss_sha256": _digest(result["gauss_reduction"]),
        "lattice_sha256": _digest(result["integral_lattice_quotient"]),
        "mode_sha256": _digest(result["mode_theorem"]),
        "positivity_sha256": _digest(result["positivity_and_hyperbolicity"]),
        "topological_obstruction_sha256": _digest(result["topological_obstruction"]),
        "terminal_sha256": _digest(result["terminal_verdict"]),
        "claim_boundary_sha256": _digest(result["claim_boundary"]),
    }
    if result["content_hashes"] != expected_hashes:
        raise AssertionError("certificate content hash failed")
    print("GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1 independent exact replay: PASS")


if __name__ == "__main__":
    verify()
