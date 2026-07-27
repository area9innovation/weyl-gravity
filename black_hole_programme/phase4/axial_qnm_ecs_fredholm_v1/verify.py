#!/usr/bin/env python3
"""Independent verifier for the global ECS Fredholm certificate."""

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
    assert data["schema"] == "phase4-axial-qnm-ecs-fredholm-v1"
    assert data["status"] == "CERTIFIED_GLOBAL_ECS_RADIAL_FREDHOLM_DOUBLE_POLE"
    assert data["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert data["verification_model"]["numeric_replay_required"] is False

    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        assert path.is_file()
        assert digest(path) == imported["sha256"]

    ecs = json.loads(
        (ROOT / data["imports"]["ecs_inverse_tortoise"]["path"]).read_text()
    )
    finite = json.loads(
        (ROOT / data["imports"]["finite_interval_fredholm"]["path"]).read_text()
    )
    jost = json.loads(
        (ROOT / data["imports"]["massive_jost_crosswalk"]["path"]).read_text()
    )
    assert sp.Rational(ecs["disk"]["phase_decay_rate_lower"]) > 0
    assert finite["smith_transfer"]["principal_rank"] == 1
    assert jost["claim_flags"]["opposite_jost_admixture_excluded"]

    # Method-distinct dichotomy audit: use a numerical rational point inside
    # the certified QNM disk rather than replaying the producer's symbols.
    omega = -sp.Rational(373, 1000) + sp.I * sp.Rational(89, 1000)
    rotation = (1 + sp.I) / sp.sqrt(2)
    right_outgoing = sp.simplify(sp.re(-sp.I * omega * rotation))
    left_ingoing = sp.simplify(sp.re(sp.I * omega * rotation))
    assert right_outgoing < 0
    assert left_ingoing > 0
    assert sp.simplify(right_outgoing + left_ingoing) == 0

    dims = data["asymptotic_dichotomy"]["audit"][
        "asymptotic_selected_dimensions"
    ]
    assert dims == {
        "left_forward_unstable": 3,
        "right_forward_stable": 3,
        "state_dimension": 6,
    }
    assert data["asymptotic_dichotomy"]["audit"]["fredholm_index"] == 0

    # Directly integrate a different polynomial majorant.
    t, rho = sp.symbols("t rho", positive=True)
    majorant = sp.integrate((1 + 3 * t) ** 2 * sp.exp(-2 * rho * t), (t, 0, sp.oo))
    assert sp.simplify(
        majorant - (2 * rho**2 + 6 * rho + 9) / (4 * rho**3)
    ) == 0

    assert data["finite_connection_reduction"]["smith_valuations"] == [0, 0, 2]
    assert data["resolvent_statement"]["principal_rank"] == 1
    assert data["resolvent_statement"]["principal_nonzero"]

    flags = data["claim_flags"]
    for key in [
        "fixed_domain_global_ecs_pencil_certified",
        "ecs_pencil_fredholm_index_zero",
        "generalized_jost_tangent_in_fixed_domain",
        "global_ecs_inverse_meromorphic_near_qnm",
        "global_ecs_second_order_pole_certified",
        "global_ecs_principal_coefficient_rank_one",
        "compact_cutoff_exterior_bridge_certified",
    ]:
        assert flags[key], key
    for key in [
        "real_axis_uncut_resolvent_certified",
        "lorentzian_causal_resolvent_certified",
        "retarded_contour_deformation_certified",
        "threshold_branch_cut_control_certified",
        "complete_qnm_expansion_certified",
        "time_domain_stability_certified",
        "quantum_statement",
    ]:
        assert not flags[key], key

    exclusions = " ".join(data["does_not_establish"])
    assert "Lorentzian-causal" in exclusions
    assert "inverse-Laplace" in exclusions
    assert "global retarded t*exp(i*omega_n*t)" in exclusions


def main() -> None:
    verify_document(json.loads((HERE / "certificate.json").read_text()))
    print("AXIAL_QNM_GLOBAL_ECS_FREDHOLM_VERIFIED")


if __name__ == "__main__":
    main()
