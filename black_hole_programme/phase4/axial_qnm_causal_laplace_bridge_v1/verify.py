#!/usr/bin/env python3
"""Independent verifier for the causal Laplace/resonance bridge."""

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
    assert data["schema"] == "phase4-axial-qnm-causal-laplace-bridge-v1"
    assert data["status"] == (
        "CERTIFIED_CAUSAL_RETARDED_TRANSFER_MEROMORPHIC_DOUBLE_POLE"
    )
    assert data["dependency_tags"] == ["REDUCED-MODE", "LORENTZIAN-CAUSAL"]
    assert data["lifecycle"] == "LORENTZIAN_CERTIFIED"

    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        assert path.is_file()
        assert digest(path) == imported["sha256"]

    jost = json.loads(
        (ROOT / data["imports"]["massive_jost"]["path"]).read_text()
    )
    ecs = json.loads(
        (ROOT / data["imports"]["global_ecs_fredholm"]["path"]).read_text()
    )
    assert jost["claim_flags"]["physical_squared_mass_qnm_velocity_nonzero"]
    assert ecs["claim_flags"]["global_ecs_second_order_pole_certified"]
    assert ecs["claim_flags"]["retarded_contour_deformation_certified"] is False

    # Independent scalar resolvent check with a different noncommuting model.
    w, m = sp.symbols("w m")
    H = sp.Matrix([[4 + w, 2], [1, 5 - w]])
    A = sp.Matrix([[0, 1], [-2, 3]])
    R = (H + m * A).inv()
    assert sp.simplify(
        R.diff(m).subs(m, 0) + H.inv() * A * H.inv()
    ) == sp.zeros(2)

    bridge = data["laplace_bridge"]
    assert bridge["fourier_convention"] == "exp(+i*omega*t)"
    assert bridge["initial_half_plane"].startswith("Im(omega)<")
    assert "(H_m-omega^2)^-1" in bridge["second_order_identity"]

    continuation = data["meromorphic_continuation"]
    assert continuation["principal_rank"] == 1
    assert continuation["principal_nonzero"]
    assert "nu_n=2*i*kappa_n/(3*omega_n)" in continuation["qnm_velocity"]

    flags = data["claim_flags"]
    for key in [
        "mode_reduced_retarded_green_operator_exists",
        "retarded_mass_derivative_identity_exact",
        "sequential_retarded_convolution_causal",
        "lower_half_plane_laplace_resolvent_bridge",
        "causal_cutoff_transfer_meromorphic_continuation_certified",
        "causal_transfer_second_order_resonance_pole_certified",
        "causal_transfer_principal_coefficient_rank_one_nonzero",
    ]:
        assert flags[key], key
    for key in [
        "full_metric_bv_retarded_propagator_certified",
        "real_causal_source_nonannihilation_certified",
        "bondi_trace_of_full_causal_solution_certified",
        "global_inverse_laplace_contour_deformation_certified",
        "threshold_branch_cut_high_frequency_control_certified",
        "complete_retarded_qnm_expansion_certified",
        "global_t_exp_iomega_t_ringdown_certified",
        "time_domain_stability_certified",
        "quantum_statement",
    ]:
        assert not flags[key], key

    exclusions = " ".join(data["does_not_establish"])
    assert "full off-shell metric BV" in exclusions
    assert "global inverse-Laplace contour deformation" in exclusions
    assert "global t*exp(i*omega_n*t)" in exclusions


def main() -> None:
    verify_document(json.loads((HERE / "certificate.json").read_text()))
    print("AXIAL_QNM_CAUSAL_LAPLACE_BRIDGE_VERIFIED")


if __name__ == "__main__":
    main()
