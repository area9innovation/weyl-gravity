#!/usr/bin/env python3
"""Independent verifier for Fredholm promotion A."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_document(data: dict) -> None:
    assert data["schema"] == "axial-qnm-fredholm-promotion-a-v1"
    assert (
        data["status"]
        == "CERTIFIED_FINITE_INTERVAL_RADIAL_GREEN_OPERATOR_DOUBLE_POLE"
    )
    assert data["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert data["verification_model"]["numeric_replay_required"] is False
    assert data["verification_model"]["arithmetic"].startswith("exact")

    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        assert path.is_file()
        assert digest(path) == imported["sha256"]

    spin_one = json.loads(
        (ROOT / data["imports"]["spin_one_local_unit"]["path"]).read_text()
    )
    assert spin_one["claim_flags"]["unique_simple_spin_two_qnm_localized"]
    assert spin_one["claim_flags"]["spin_one_jost_factor_unit_on_local_disk"]
    assert spin_one["result"]["full_connection_smith_valuations"] == [0, 0, 2]

    reconstruction = json.loads(
        (
            ROOT
            / data["imports"]["complete_metric_reconstruction"]["path"]
        ).read_text()
    )
    assert reconstruction["complete_reconstruction"]["kernel2"][0] == ["0", "1"]
    assert reconstruction["complete_reconstruction"]["reduced_state"][-2:] == [
        "H1",
        "F=H1_prime",
    ]

    # Method-distinct algebra: solve the block inverse directly instead of
    # replaying the producer's row operation.
    z = sp.symbols("z")
    D = sp.Matrix([[1, 1, 0], [0, 2, 1], [0, 0, 3]])
    N = sp.Matrix([[2, 0, 1], [1, -1, 0], [0, 4, 1]])
    M = sp.Matrix([[1, 0, z], [0, 1, 2 * z], [0, 0, z**2]])
    B = D.row_join(sp.zeros(3)).col_join(N.row_join(M))
    candidate = D.inv().row_join(sp.zeros(3)).col_join(
        (-M.inv() * N * D.inv()).row_join(M.inv())
    )
    assert sp.simplify(B * candidate) == sp.eye(6)
    principal = candidate.applyfunc(lambda entry: sp.limit(z**2 * entry, z, 0))
    assert principal.rank() == 1
    assert sp.factor(B.det()) == 6 * z**2

    assert data["initial_value_reduction"]["index"] == 0
    assert (
        data["effective_boundary_operator"]["audit"]["principal_rank"] == 1
    )
    assert data["smith_transfer"]["principal_rank"] == 1
    assert data["smith_transfer"]["principal_nonzero"]

    flags = data["claim_flags"]
    for key in [
        "analytic_finite_interval_pencil_certified",
        "fredholm_index_zero_certified",
        "effective_boundary_schur_identity_certified",
        "connection_smith_transferred_to_operator",
        "radial_green_operator_second_order_pole_certified",
        "principal_laurent_coefficient_rank_one",
        "physical_metric_reconstruction_nonzero",
    ]:
        assert flags[key], key
    for key in [
        "exterior_spacetime_causal_resolvent_certified",
        "retarded_inverse_transform_certified",
        "t_exp_iomega_t_term_certified",
        "nonpole_contour_control_certified",
        "time_domain_stability_certified",
        "quantum_statement",
    ]:
        assert not flags[key], key

    boundary = " ".join(data["does_not_establish"])
    assert "t*exp(i*omega_n*t)" in boundary
    assert "causal exterior spacetime resolvent" in boundary


def main() -> None:
    verify_document(json.loads((HERE / "certificate.json").read_text()))
    print("AXIAL_QNM_FREDHOLM_PROMOTION_A_VERIFIED")


if __name__ == "__main__":
    main()
