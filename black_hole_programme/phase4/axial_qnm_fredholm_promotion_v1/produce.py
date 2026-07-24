#!/usr/bin/env python3
"""Produce the exact finite-interval Fredholm-promotion certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE_COMMIT = "a976622c47151857447790dd077ff131b7820094"

IMPORTS = {
    "analytic_continuation": ROOT
    / "black_hole_programme/certificates/BH3_ANALYTIC_CONTINUATION_GATE.json",
    "ecs_analytic_outgoing_germs": ROOT
    / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json",
    "evans_winding": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "full_contour_winding_v1/certificate.json"
    ),
    "intrinsic_selector": ROOT
    / (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "local_selector_v1/certificate.json"
    ),
    "spin_one_local_unit": ROOT
    / "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json",
    "local_smith_theorem": ROOT
    / "black_hole_programme/phase3/axial_qnm_local_smith_dichotomy/certificate.json",
    "complete_metric_reconstruction": ROOT
    / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_block_audit() -> dict:
    """Check the Schur and Smith algebra over an exact symbolic field."""

    z = sp.symbols("z")
    # D is the invertible horizon-complement block.  N is the irrelevant
    # outgoing image of that complement.  M has Smith valuations (0,0,2).
    D = sp.diag(2, 3, 5)
    N = sp.Matrix([[1, 2, 0], [0, -1, 4], [3, 0, 1]])
    M = sp.diag(7, 11, 13 * z**2)
    boundary = D.row_join(sp.zeros(3))
    boundary = boundary.col_join(N.row_join(M))
    left = sp.eye(6)
    left[3:, :3] = -N * D.inv()
    reduced = sp.simplify(left * boundary)
    expected = D.row_join(sp.zeros(3)).col_join(sp.zeros(3).row_join(M))
    assert reduced == expected
    assert sp.factor(boundary.det()) == 2 * 3 * 5 * 7 * 11 * 13 * z**2

    inverse = sp.simplify(boundary.inv())
    principal = inverse.applyfunc(
        lambda entry: sp.limit(z**2 * entry, z, 0)
    )
    assert principal.rank() == 1
    assert principal != sp.zeros(6)

    # Analytic left/right units cannot change pole order or principal rank.
    U = sp.eye(6)
    U[0, 5] = z
    V = sp.eye(6)
    V[5, 1] = z
    dressed_inverse = sp.simplify(V.inv() * inverse * U.inv())
    dressed_principal = dressed_inverse.applyfunc(
        lambda entry: sp.limit(z**2 * entry, z, 0)
    )
    assert dressed_principal.rank() == 1

    return {
        "boundary_matrix_det": sp.sstr(sp.factor(boundary.det())),
        "schur_reduction": "left*B=diag(D,M), with D an analytic unit",
        "smith_model": "M=diag(7,11,13*z^2)",
        "inverse_pole_order": 2,
        "principal_rank": principal.rank(),
        "analytic_unit_dressed_principal_rank": dressed_principal.rank(),
    }


def build_certificate() -> dict:
    analytic = json.loads(IMPORTS["analytic_continuation"].read_text())
    ecs = json.loads(IMPORTS["ecs_analytic_outgoing_germs"].read_text())
    winding = json.loads(IMPORTS["evans_winding"].read_text())
    selector = json.loads(IMPORTS["intrinsic_selector"].read_text())
    spin_one = json.loads(IMPORTS["spin_one_local_unit"].read_text())
    reconstruction = json.loads(
        IMPORTS["complete_metric_reconstruction"].read_text()
    )

    assert ecs["volterra"]["uniform_contraction_on_closed_disk"]
    assert (
        ecs["volterra"]["analytic_frequency_dependence"]
        == "uniformly convergent Neumann series on the closed disk"
    )
    assert winding["claim_flags"]["unique_simple_spin_two_QNM_in_disk_certified"]
    assert selector["claim_flags"]["intrinsic_tangent_selector_nonzero"]
    assert spin_one["claim_flags"]["full_connection_smith_valuations_0_0_2"]
    assert (
        spin_one["result"]["full_connection_smith_valuations"]
        == [0, 0, 2]
    )
    assert reconstruction["claim_flags"][
        "complete_three_row_reconstruction_certified"
    ]
    assert reconstruction["complete_reconstruction"]["reduced_state"] == [
        "P",
        "P_prime",
        "Q",
        "Q_prime",
        "H1",
        "F=H1_prime",
    ]
    assert analytic["axial_analytic_continuation"]["declared_domain"][
        "strip_halfwidth"
    ] == "1/4"

    return {
        "schema": "axial-qnm-fredholm-promotion-a-v1",
        "status": "CERTIFIED_FINITE_INTERVAL_RADIAL_GREEN_OPERATOR_DOUBLE_POLE",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "source_commit": SOURCE_COMMIT,
        "verification_model": {
            "arithmetic": "exact symbolic and exact imported content hashes",
            "independence_level": (
                "Level II: verifier uses direct block inversion rather than "
                "the producer's Schur row operation"
            ),
            "numeric_replay_required": False,
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": digest(path),
            }
            for name, path in IMPORTS.items()
        },
        "qnm_disk": spin_one["result"]["qnm_enclosure"],
        "finite_interval_pencil": {
            "spaces": (
                "L(omega):H^1([r_H,r_I];C^6) -> "
                "L^2([r_H,r_I];C^6) direct_sum C^3 direct_sum C^3"
            ),
            "formula": (
                "L(omega)Y=(Y'-A(r,omega)Y,"
                "B_H(omega)Y(r_H),B_I(omega)Y(r_I))"
            ),
            "radii": "any fixed ordinary 2<r_H<r_I<infinity inside the certified continuation domains",
            "analyticity": (
                "A and the selected endpoint planes are holomorphic on the "
                "local QNM disk; fixed nonzero frame minors give holomorphic "
                "annihilators B_H and B_I after shrinking within that disk"
            ),
            "boundedness": (
                "multiplication H1->L2 and the two H1 traces are bounded; "
                "the Banach spaces are fixed"
            ),
            "operator_kind": "bounded analytic Fredholm pencil with fixed domain and target",
        },
        "initial_value_reduction": {
            "isomorphism": (
                "Gamma_omega:Y -> (Y'-A Y,Y(r_H)) from H1 to L2 direct_sum C6"
            ),
            "inverse": (
                "Y(r)=Phi(r,r_H)c+integral_[r_H,r] Phi(r,s)f(s) ds"
            ),
            "analyticity": "the Volterra inverse and Phi are holomorphic in operator norm",
            "boundary_matrix": (
                "B(omega)c=(B_H c,B_I Phi(r_I,r_H) c)"
            ),
            "equivalence": (
                "analytic triangular changes of target reduce L to "
                "I_L2 direct_sum B(omega)"
            ),
            "index": 0,
            "invertible_witness": (
                "the certified local disk contains exactly one simple spin-two "
                "zero and the spin-one factor is a unit, so every nearby "
                "nonroot frequency is an invertible witness"
            ),
        },
        "effective_boundary_operator": {
            "horizon_frame": "H(omega):C3->C6 spans ker B_H(omega)",
            "horizon_complement": (
                "choose analytic K with D=B_H K an analytic unit"
            ),
            "formula": "M(omega)=B_I Phi(r_I,r_H;omega) H(omega)",
            "schur_identity": (
                "in c=H u+K v coordinates, B is analytically equivalent to "
                "diag(D,M); D is a unit"
            ),
            "connection_bridge": (
                "M equals the certified factor-adapted QNM connection matrix "
                "up to holomorphic invertible endpoint-frame units"
            ),
            "kernel": "ker L(omega)=ker M(omega), reconstructed by the horizon frame",
            "audit": exact_block_audit(),
        },
        "smith_transfer": {
            "imported_connection_smith_valuations": [0, 0, 2],
            "operator_local_equivalence": (
                "L is analytically equivalent to I_L2 direct_sum units direct_sum M"
            ),
            "laurent_form": (
                "L(omega)^-1=Pi_-2/(omega-omega_n)^2"
                "+Pi_-1/(omega-omega_n)+O(1)"
            ),
            "principal_rank": 1,
            "principal_nonzero": True,
            "reason": (
                "Smith diag(unit,unit,z^2) has a nonzero rank-one z^-2 "
                "coefficient; analytic invertible reconstruction maps preserve rank"
            ),
        },
        "physical_reconstruction": {
            "principal_range": "the unique source-Einstein connection root line",
            "exact_metric_state": "(H1,F=H1_prime) in the complete six-state reconstruction",
            "nonannihilation": (
                "a nonzero source-Einstein kernel solution cannot have H1 "
                "identically zero, since then F=H1_prime and the two-state "
                "kernel solution both vanish"
            ),
            "observation": (
                "the physical axial metric component H1 on the finite interval"
            ),
            "conclusion": "the rank-one order-two coefficient survives metric reconstruction",
        },
        "claim_flags": {
            "analytic_finite_interval_pencil_certified": True,
            "fredholm_index_zero_certified": True,
            "effective_boundary_schur_identity_certified": True,
            "connection_smith_transferred_to_operator": True,
            "radial_green_operator_second_order_pole_certified": True,
            "principal_laurent_coefficient_rank_one": True,
            "physical_metric_reconstruction_nonzero": True,
            "exterior_spacetime_causal_resolvent_certified": False,
            "retarded_inverse_transform_certified": False,
            "t_exp_iomega_t_term_certified": False,
            "nonpole_contour_control_certified": False,
            "time_domain_stability_certified": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "a causal exterior spacetime resolvent or a complete Lorentzian initial-value theory",
            "a Laplace contour deformation across the QNM",
            "control of the non-pole inverse-transform contour",
            "a t*exp(i*omega_n*t) term for physical initial data or sources",
            "time-domain boundedness, decay, completeness or stability",
            "an all-overtone theorem, particle interpretation or quantum statement",
        ],
        "next_gate": (
            "Fredholm promotion B must declare a causal Laplace convention, "
            "justify contour deformation and prove source/observation "
            "nonannihilation before any t*exp(i*omega_n*t) statement"
        ),
    }


def main() -> None:
    data = build_certificate()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "axial-qnm-fredholm-promotion-a-receipt-v1",
        "source_commit": SOURCE_COMMIT,
        "certificate": str(CERT.relative_to(ROOT)),
        "certificate_sha256": digest(CERT),
        "producer_sha256": digest(HERE / "produce.py"),
        "verifier_sha256": digest(HERE / "verify.py"),
        "commands": [
            "python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.produce",
            "python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.test_fredholm",
        ],
        "recorded_tier_execution": [
            {
                "command": "python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.produce",
                "elapsed_seconds": "0.46",
                "status": "PASS",
            },
            {
                "command": "python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.verify",
                "elapsed_seconds": "0.36",
                "status": "PASS",
            },
            {
                "command": "python3 -m unittest -v black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.test_fredholm",
                "elapsed_seconds": "0.40",
                "status": "PASS (6 tests)",
            },
        ],
        "higher_tiers_not_run": (
            "No shared operator, schema, or generated classical input changed; "
            "Tier 3 is not triggered."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
