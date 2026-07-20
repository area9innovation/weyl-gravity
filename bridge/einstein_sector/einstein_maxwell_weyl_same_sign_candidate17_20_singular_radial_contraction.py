"""Certify the radial contraction of candidate-17/20 singular components."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.schema.json"
INPUTS = {
    "common_square": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient.json",
    "connected_hub": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.json",
    "singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "component_incidence": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contraction_identity() -> dict[str, object]:
    omega_minus, omega_plus = sp.symbols("omega_minus omega_plus", positive=True)
    a_minus, a_plus, b_minus, b_plus = sp.symbols(
        "A_minus A_plus B_minus B_plus", nonnegative=True
    )
    t = sp.symbols("t", real=True)
    alpha = omega_plus * a_plus - omega_minus * a_minus
    beta = omega_plus * b_plus - omega_minus * b_minus
    delta = sp.expand(alpha + beta)
    square_coefficient = sp.expand(
        omega_plus * (a_plus + (1 - t**2) * b_plus)
        - omega_minus * (a_minus + (1 - t**2) * b_minus)
    )
    # At t=1, active rotation zero says M_K=-alpha*mu_square. Scaling both
    # K-factor node amplitudes by t multiplies its moment by t^2.
    total_coefficient = sp.expand(square_coefficient - t**2 * alpha)
    if sp.factor(total_coefficient - (1 - t**2) * delta) != 0:
        raise AssertionError("radial-transfer moment identity changed")
    for occupation in (a_minus, a_plus):
        if sp.expand(
            occupation
            + (1 - t**2) * (b_minus if occupation == a_minus else b_plus)
            + t**2 * (b_minus if occupation == a_minus else b_plus)
            - (occupation + (b_minus if occupation == a_minus else b_plus))
        ) != 0:
            raise AssertionError("radial-transfer occupation conservation changed")
    return {
        "allocation": {
            "square_negative": "A_minus(t)=A_minus+(1-t^2)*B_minus",
            "square_positive": "A_plus(t)=A_plus+(1-t^2)*B_plus",
            "kernel_negative": "B_minus(t)=t^2*B_minus",
            "kernel_positive": "B_plus(t)=t^2*B_plus",
        },
        "active_frequency_weight": "delta=omega_plus*(A_plus+B_plus)-omega_minus*(A_minus+B_minus)",
        "initial_zero_relation": "M_K=-alpha*mu_square with alpha=omega_plus*A_plus-omega_minus*A_minus",
        "exact_residual": "mu_rotation(t)=(1-t^2)*delta*mu_square",
        "endpoint": "at t=0 the arbitrary K factor is its vertex and the point lies in S_plus x S_minus",
        "occupation_conservation_checked": True,
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    common = records["common_square"]["classification"]
    if not (
        common["candidate20_rotation_balance_divisor_nonempty"]
        and common["candidate20_on_balance_common_square_rotation_zero_quotient_closed_interval"]
        and common["candidate17_rotation_coefficient_strictly_negative_on_complete_nonzero_active_cone"]
    ):
        raise AssertionError("frequency-weighted balance input changed")
    hub = records["connected_hub"]["classification"]
    if not (
        hub["candidate17_double_singular_rotation_zero_hub_connected"]
        and hub["candidate20_double_singular_rotation_zero_hub_connected"]
    ):
        raise AssertionError("connected hub input changed")
    product = records["singular_locus"]["two_parity_product"]
    if product["singular_locus"] != "(S_plus x K_minus) union (K_plus x S_minus)":
        raise AssertionError("singular union changed")
    incidence = records["component_incidence"]["classification"]
    if not (
        incidence["candidate17_positive_occupation_singular_component_images_intersect"]
        and incidence["candidate20_positive_occupation_singular_component_images_intersect"]
    ):
        raise AssertionError("singular component incidence changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-singular-radial-contraction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_SINGULAR_RADIAL_CONTRACTION",
        "result_state": "CANDIDATE20_BALANCE_DIVISOR_COMPLETE_SINGULAR_UNION_CONTRACTS_TO_CONNECTED_HUB",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_TWO_PARITY_SINGULAR_UNION_ON_CANDIDATE20_BALANCE_DIVISOR",
        "scope": {
            **records["singular_locus"]["scope"],
            "background": "candidates 17 and 20 separately; the complete-union conclusion is candidate 20 on its exact active balance divisor",
            "carrier": "the complete fixed-positive-active-occupation singular union (S_plus x K_minus) union (K_plus x S_minus), after both common node phases",
            "correction_class": "bounded or finite-quasiperiodic second-order tangent cone",
        },
        "radial_transfer": contraction_identity(),
        "resonance_and_group_checks": {
            "resonance": "T3 is bilinear, so independent nonnegative scaling of the two K-factor node vectors preserves T3(f,g)=0; the receiving factor remains common-square",
            "node_phases": "the contraction uses real nonnegative scale factors and is well defined after the two common node-phase quotients",
            "reality": "the path is performed on positive-frequency coefficients and commutes with conjugate reality completion",
            "component_symmetry": "the same construction applies after exchanging the plus and minus parity-factor labels",
        },
        "candidate20_balance_theorem": {
            "balance_divisor_nonempty": True,
            "every_rotation_zero_point_in_each_singular_component_has_radial_path_to_hub": True,
            "complete_singular_union_rotation_zero_fibre_connected": True,
            "proof": "delta=0 annihilates the exact residual for all t; every point attaches by a path to the already connected nonempty double-singular hub",
        },
        "off_balance_obstruction": {
            "residual": "(1-t^2)*delta*mu_square",
            "canonical_radial_contraction_condition": "delta=0 or mu_square=0",
            "phase_real_alternative": "mu_square=0 iff the common-square direction is phase-real",
            "candidate17": "delta is never zero on the nonzero active cone, so this contraction is certified only on its phase-real square-direction sublocus",
            "candidate20_off_balance": "the same phase-real sublocus contracts; no general off-balance contraction is certified",
            "nonradial_no_go_proved": False,
        },
        "classification": {
            "exact_radial_transfer_identity_certified": True,
            "candidate20_balance_complete_singular_union_contracts_to_hub": True,
            "candidate20_balance_complete_singular_rotation_zero_fibre_connected": True,
            "candidate17_phase_real_common_square_sublocus_contracts_to_hub": True,
            "candidate20_off_balance_phase_real_common_square_sublocus_contracts_to_hub": True,
            "candidate17_complete_singular_rotation_zero_fibre_connected": False,
            "candidate20_off_balance_complete_singular_rotation_zero_fibre_connected": False,
            "off_balance_nonradial_contraction_no_go": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The candidate-20 balance divisor is a genuine simplifying stratum, not merely a larger endpoint quotient. On it, every point of both singular components contracts explicitly to their connected common hub, so the complete singular rotation-zero fibre is connected. Off balance the same canonical contraction leaves the exact residual (1-t^2)*delta*mu_square; this isolates the missing hypothesis without claiming that every nonradial contraction is impossible.",
        "next_gate": "on candidate 17 and candidate-20 off balance, either construct a nonradial contraction that changes the square direction and K-factor moment jointly, or exhibit a quotient invariant separating a rotation-zero component from the connected hub",
        "claim_boundary": "This completely classifies the fixed-occupation singular union only on candidate 20's exact balance divisor and the phase-real radial subloci off balance. It does not prove an off-balance no-go, glue occupation strata, classify the full smooth-plus-singular zero fibre, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("singular radial-contraction certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_SINGULAR_RADIAL_CONTRACTION: PASS")


if __name__ == "__main__":
    main()
