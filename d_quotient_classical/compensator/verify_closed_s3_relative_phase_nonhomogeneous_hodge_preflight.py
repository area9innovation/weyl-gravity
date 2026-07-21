#!/usr/bin/env python3
"""Independent exact replay of the nonhomogeneous S3 Hodge/Gauss theorem."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json"
)
PAYLOAD = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PAYLOAD_V1.json"
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
    return sp.Matrix(
        nrows,
        ncols,
        lambda i, j: sp.Rational(str(rows[i][j])),
    )


def _check_fixture(row: dict[str, object]) -> None:
    n = int(row["n"])
    r = int(row["r"])
    rank = int(row["rank_Q"])
    q = _mat(row["Q"], n, r)
    m = _mat(row["phase_kinetic_M"], n, n)
    k = _mat(row["gauge_kinetic_K"], r, r)
    relative = _mat(row["relative_character_basis_N"], n, n - rank)
    active0 = _mat(row["active_gauge_complement_S"], r, rank)
    kernel = _mat(row["matter_kernel_basis_T"], r, r - rank)
    if int(q.rank()) != rank or q.T * relative != sp.zeros(r, n - rank):
        raise AssertionError(f"charge/relative rank failed: {row['fixture_id']}")
    if q * kernel != sp.zeros(n, r - rank):
        raise AssertionError(f"matter-kernel basis failed: {row['fixture_id']}")

    if r - rank:
        k0 = kernel.T * k * kernel
        active = active0 - kernel * k0.inv() * kernel.T * k * active0
    else:
        k0 = sp.zeros(0, 0)
        active = active0
    qa = q * active
    ka = active.T * k * active
    vertical = qa.T * m * qa
    inverse_relative = relative.T * m.inv() * relative
    grel = inverse_relative.inv() if n - rank else sp.zeros(0, 0)
    horizontal = m.inv() * relative * grel if n - rank else sp.zeros(n, 0)
    if (
        kernel.T * k * active != sp.zeros(r - rank, rank)
        or relative.T * horizontal != sp.eye(n - rank)
        or q.T * m * horizontal != sp.zeros(r, n - rank)
    ):
        raise AssertionError(f"orthogonal split failed: {row['fixture_id']}")

    ell = int(row["ell"])
    lam = sp.Integer(ell * (ell + 2))
    mu = sp.Integer((ell + 1) ** 2)
    if rank:
        longitudinal = (ka.inv() + lam * vertical.inv()).inv()
        schur = ka - lam * ka * (vertical + lam * ka).inv() * ka
        frequency = lam * sp.eye(rank) + ka.inv() * vertical
        if longitudinal != schur or not longitudinal.is_positive_definite:
            raise AssertionError(f"Gauss Schur reduction failed: {row['fixture_id']}")
    else:
        longitudinal = sp.zeros(0, 0)
        frequency = sp.zeros(0, 0)
    coexact = mu * sp.eye(r) + k.inv() * (q.T * m * q)
    comparisons = (
        (_mat(row["K_orthogonal_active_basis_Sperp"], r, rank), active),
        (_mat(row["effective_active_gauge_kinetic_Ka"], rank, rank), ka),
        (_mat(row["matter_kernel_gauge_kinetic_K0"], r - rank, r - rank), k0),
        (_mat(row["vertical_phase_Gram_V"], rank, rank), vertical),
        (_mat(row["relative_inverse_metric_A"], n - rank, n - rank), inverse_relative),
        (_mat(row["relative_metric_Grel"], n - rank, n - rank), grel),
        (_mat(row["relative_horizontal_lift_H"], n, n - rank), horizontal),
        (_mat(row["longitudinal_kinetic_after_Gauss"], rank, rank), longitudinal),
        (_mat(row["longitudinal_frequency_squared_operator"], rank, rank), frequency),
        (_mat(row["coexact_frequency_squared_operator"], r, r), coexact),
    )
    if any(left != right for left, right in comparisons):
        raise AssertionError(f"serialized matrix mismatch: {row['fixture_id']}")
    if n - rank and not grel.is_positive_definite:
        raise AssertionError(f"relative positivity failed: {row['fixture_id']}")
    if mu != lam + 1 or not all(row["exact_checks"].values()):
        raise AssertionError(f"Hodge/check ledger failed: {row['fixture_id']}")


def _small_charge_census() -> None:
    """Method-distinct rank-one census; no fixture coefficients imported."""
    m = sp.diag(2, 3)
    for q1, q2 in itertools.product(range(-3, 4), repeat=2):
        if q1 == q2 == 0:
            continue
        divisor = math.gcd(abs(q1), abs(q2))
        q = sp.Matrix([[q1], [q2]])
        n = sp.Matrix([[q2 // divisor], [-q1 // divisor]])
        a = (n.T * m.inv() * n)[0]
        if q.T * n != sp.zeros(1, 1) or a <= 0 or sp.Rational(1, 1) / a <= 0:
            raise AssertionError("rank-one all-charge census failed")


def verify() -> None:
    result = json.loads(RESULT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    imported = result["import"]
    import_path = ROOT / imported["path"]
    homogeneous = json.loads(import_path.read_text())
    if (
        _sha(import_path) != imported["sha256"]
        or imported["actual_sha256"] != imported["sha256"]
        or imported["oracle_fields_consumed"] != []
        or homogeneous["result_id"] != imported["result_id"]
    ):
        raise AssertionError("homogeneous import replay failed")
    if _sha(PAYLOAD) != result["payload_ref"]["sha256"]:
        raise AssertionError("payload byte hash failed")
    expected_payload_hash = _digest(
        {key: value for key, value in payload.items() if key != "content_sha256"}
    )
    if payload["content_sha256"] != expected_payload_hash:
        raise AssertionError("payload canonical hash failed")
    for row in payload["fixtures"]:
        _check_fixture(row)

    # Independent ell=0 reconstruction, then comparison to the imported
    # homogeneous fixture (not to its terminal verdict).
    q0 = sp.Matrix([[1], [1]])
    m0 = sp.diag(2, 3)
    n0 = sp.Matrix([[1], [-1]])
    g0 = ((n0.T * m0.inv() * n0).inv())[0]
    imported_fixture = next(
        item
        for item in homogeneous["exact_fixtures"]
        if item["fixture_id"] == "two_equal_charges_counterflow_clock"
    )
    if q0.T * n0 != sp.zeros(1, 1) or g0 != sp.Rational(6, 5):
        raise AssertionError("independent ell=0 derivation failed")
    if imported_fixture["reduced_metric_Grel_equals_Ainv"] != [[str(g0)]]:
        raise AssertionError("ell=0 homogeneous crosscheck failed")

    ell = sp.symbols("ell", integer=True, nonnegative=True)
    if sp.expand((ell + 1) ** 2 - ell * (ell + 2) - 1) != 0:
        raise AssertionError("all-ell Hodge identity failed")
    _small_charge_census()

    deficient = next(
        row
        for row in payload["fixtures"]
        if row["fixture_id"].startswith("rank_deficient")
    )
    coexact = _mat(deficient["coexact_frequency_squared_operator"], 2, 2)
    if sorted(coexact.eigenvals().keys()) != [sp.Integer(9), sp.Integer(12)]:
        raise AssertionError("massless/massive rank-deficient split failed")
    if _mat(deficient["longitudinal_frequency_squared_operator"], 1, 1) != sp.Matrix([[11]]):
        raise AssertionError("rank-deficient longitudinal frequency failed")

    forbidden = (
        "CONFLUX_VERDICT",
        "MODEL_SPECIFIC_ACTION_SELECTED",
        "FULL_BV_CAUSAL_PARENT",
        "GRAVITY_COUPLING",
        "HADAMARD_OR_QUANTUM",
    )
    if any(result["claim_flags"][key] for key in forbidden):
        raise AssertionError("claim boundary promoted")
    expected_hashes = {
        "hodge_sha256": _digest(result["hodge_decomposition"]),
        "gauss_sha256": _digest(result["gauss_reduction"]),
        "mode_theorem_sha256": _digest(result["mode_theorem"]),
        "positivity_sha256": _digest(result["positivity_and_hyperbolicity"]),
        "zero_modes_sha256": _digest(result["zero_mode_ledger"]),
        "terminal_sha256": _digest(result["terminal_verdict"]),
        "claim_boundary_sha256": _digest(result["claim_boundary"]),
    }
    if result["content_hashes"] != expected_hashes:
        raise AssertionError("certificate content hash failed")
    print(
        "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1 "
        "independent exact replay: PASS"
    )


if __name__ == "__main__":
    verify()
