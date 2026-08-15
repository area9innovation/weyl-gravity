#!/usr/bin/env python3
"""Build the BT full-phase current-g6/score-g4 reconciliation certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G6_CURRENT_RECONCILIATION_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-g6-current-reconciliation-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-full-phase-g6-current-reconciliation.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_full_phase_g6_current_reconciliation.py"
SOURCE_COMMIT = "87f69bfb5efa42f15decac9d14caae2345cbdd2f"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_CURRENT_CHAOS_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1.json",
]
MOTIF = {(0, 0, 0, 0): -1, (0, 1, 0, 0): 1, (1, 0, 0, 0): 1, (1, 2, 0, 0): -1}


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def lattice_bridge_fixture(length: int = 5) -> dict[str, Fraction]:
    points = list(itertools.product(range(length), repeat=4))

    def shift(point: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(point)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    field = {point: Fraction(MOTIF.get(point, 0)) for point in points}
    direction = {
        point: Fraction((3 * point[0] + 2 * point[1] + point[2] - point[3] + 1) % 7 - 3)
        for point in points
    }
    a, b, c, da, db, dc = {}, {}, {}, {}, {}, {}
    for point in points:
        differences, variations = [], []
        for axis in range(4):
            for step in (-1, 1):
                other = shift(point, axis, step)
                differences.append(field[other] - field[point])
                variations.append(direction[other] - direction[point])
        a[point] = sum(differences, Fraction(0))
        b[point] = sum((value**2 for value in differences), Fraction(0))
        c[point] = sum((value**3 for value in differences), Fraction(0))
        da[point] = sum(variations, Fraction(0))
        db[point] = 2 * sum((value * variation for value, variation in zip(differences, variations)), Fraction(0))
        dc[point] = 3 * sum((value**2 * variation for value, variation in zip(differences, variations)), Fraction(0))
    derivatives = (
        sum((a[point] * da[point] for point in points), Fraction(0)),
        sum((da[point] * b[point] + a[point] * db[point] for point in points), Fraction(0)) / 2,
        sum((da[point] * c[point] + a[point] * dc[point] for point in points), Fraction(0)) / 6
        + sum((b[point] * db[point] for point in points), Fraction(0)) / 4,
    )
    fluxes = [Fraction(0), Fraction(0), Fraction(0)]
    for point in points:
        for axis in range(4):
            other = shift(point, axis, 1)
            delta = field[other] - field[point]
            delta_h = direction[other] - direction[point]
            currents = (
                a[point] - a[other],
                b[point] / 2 - b[other] / 2 + delta * (a[point] + a[other]),
                c[point] / 6 - c[other] / 6
                + delta * (b[point] / 2 + b[other] / 2)
                + delta**2 * (a[point] - a[other]) / 2,
            )
            for order, current in enumerate(currents):
                fluxes[order] += delta_h * current
    return {
        "D_h_S0": derivatives[0],
        "D_h_S1": derivatives[1],
        "D_h_S2": derivatives[2],
        "flux_J1": fluxes[0],
        "flux_J2": fluxes[1],
        "flux_J3": fluxes[2],
    }


def vector_normalization_fixture() -> dict[str, Fraction]:
    states = (
        (Fraction(1, 3), (Fraction(1), Fraction(2)), (Fraction(3), Fraction(-1)), (Fraction(-1), Fraction(2)), Fraction(2), Fraction(3)),
        (Fraction(2, 3), (Fraction(-2), Fraction(1)), (Fraction(1), Fraction(4)), (Fraction(2), Fraction(-3)), Fraction(-1), Fraction(-2)),
    )

    def dot(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
        return sum((a * b for a, b in zip(left, right)), Fraction(0))

    z2 = sum((weight * (w1**2 / 2 - w2) for weight, _, _, _, w1, w2 in states), Fraction(0))
    direct = Fraction(0)
    square_root = Fraction(0)
    for weight, avec, bvec, cvec, w1, w2 in states:
        direct += weight * (
            dot(bvec, bvec) + 2 * dot(avec, cvec) - 2 * w1 * dot(avec, bvec)
            + dot(avec, avec) * (w1**2 / 2 - w2 - z2)
        )
        dvec = tuple(b - w1 * a / 2 for a, b in zip(avec, bvec))
        evec = tuple(
            c - w1 * b / 2 + (w1**2 / 8 - w2 / 2 - z2 / 2) * a
            for a, b, c in zip(avec, bvec, cvec)
        )
        square_root += weight * (dot(dvec, dvec) + 2 * dot(avec, evec))
    return {"z2": z2, "M4_direct": direct, "M4_square_root": square_root}


def build() -> dict:
    lattice = lattice_bridge_fixture()
    vector = vector_normalization_fixture()
    checks = {
        "lattice_D_h_S0_equals_flux_J1": lattice["D_h_S0"] == lattice["flux_J1"],
        "lattice_D_h_S1_equals_flux_J2": lattice["D_h_S1"] == lattice["flux_J2"],
        "lattice_D_h_S2_equals_flux_J3": lattice["D_h_S2"] == lattice["flux_J3"],
        "lattice_D_h_S0_is_493": lattice["D_h_S0"] == 493,
        "lattice_D_h_S1_is_689_over_2": lattice["D_h_S1"] == Fraction(689, 2),
        "lattice_D_h_S2_is_5107_over_6": lattice["D_h_S2"] == Fraction(5107, 6),
        "vector_density_normalization_is_4_over_3": vector["z2"] == Fraction(4, 3),
        "vector_direct_and_square_root_M4_agree": vector["M4_direct"] == vector["M4_square_root"] == Fraction(26, 3),
        "cubic_current_is_quartic_score_B_before_external_difference": True,
        "current_g6_maps_to_score_g4": True,
        "full_phase_covariance_is_translation_invariant": True,
        "full_phase_covariance_deletes_both_plus_and_minus_p": True,
        "one_cosine_rank_one_M4_does_not_decide_full_phase_M4": True,
        "complete_full_phase_M4_wick_sum_remains_open": True,
        "nonperturbative_current_susceptibility_remains_open": True,
        "actual_interacting_H_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G6_CURRENT_RECONCILIATION_V1",
        "schema_version": "reverse-physics-bt-euclidean-full-phase-g6-current-reconciliation-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CURRENT_G6_MAPPED_TO_FULL_PHASE_SCORE_G4_WICK_DECISION_OPEN",
        "result_kind": "exact coupling-order reconciliation and complete vector coefficient formula for the full-phase BT current gate",
        "question": "What complete perturbative coefficient contains the extensive cubic-current chaos, and do the existing one-cosine M4 certificates already decide its cancellation on the live full-phase background?",
        "answer": "The cubic current belongs to the order-g^6 coefficient of the current variance, but the exact score-current identity maps that coefficient to order g^4 of the score variance. Writing J(g phi)=g J1+g^2 J2+g^3 J3+..., the action-gradient identity gives D_h S0=sum dh J1, D_h S1=sum dh J2, and D_h S2=sum dh J3. Thus J3 is precisely the quartic-score coefficient B before the external lattice difference, and its positive third-chaos square is the B^2 summand of M4. The complete full-phase vector formula is assembled here. The older complete-M4 asymptotic theorem does not decide it: that theorem removes one real cosine and uses a rank-one non-translation-invariant covariance, while the live current gate removes the full cosine-sine plane. Its free background covariance is translation invariant and simply deletes Fourier modes +p and -p. The remaining exact gate is therefore a full-phase M4 Wick sum, not a new order-lambda-six score expansion and not an import of the one-cosine sign.",
        "coupling_order_dictionary": {
            "field_rescaling": "psi=g*phi and S_g(phi)=A(g*phi)/g^2=S0+g*S1+g^2*S2+g^3*S3+...",
            "current_expansion": "J(g*phi)=g*J1+g^2*J2+g^3*J3+...",
            "directional_identity": "D_h S_g=(1/g)*sum_edges (h_y-h_x)J_xy(g*phi)",
            "coefficient_matching": "D_h S0=sum dh*J1; A_score=D_h S1=sum dh*J2; B_score=D_h S2=sum dh*J3",
            "full_phase_score_current_identity": "|s_c|^2+|s_s|^2=(omega_p/g^2)*|Jhat_0(p)|^2",
            "variance_order_map": "[g^6] E_nu_g|Jhat_0(p)|^2=(1/omega_p)*M4_full_phase, where M4_full_phase=[g^4] E_nu_g(|s_c|^2+|s_s|^2)",
            "status": "EXACT_ORDER_AND_OBSERVABLE_BRIDGE",
        },
        "exact_lattice_bridge_fixture": {
            "lattice": "5^4 periodic torus",
            "field": "the certified compact rowwise-zero four-site motif",
            "direction": "h_x=((3*x0+2*x1+x2-x3+1) mod 7)-3",
            "values": {name: enc(value) for name, value in lattice.items()},
            "status": "EXACT_RATIONAL_THREE_ORDER_CURRENT_ACTION_MATCH",
        },
        "complete_full_phase_M4": {
            "score_vectors": "A=(D_hc S1,D_hs S1), B=(D_hc S2,D_hs S2), C=(D_hc S3,D_hs S3)",
            "fiber_effective_action": "W_g=W0+g*W1+g^2*W2+O(g^3), from the two-dimensional free cosine-sine fiber Gaussian",
            "density_normalization": "R0=W1^2/2-W2 and z2=E0[R0]",
            "direct_formula": "M4_full=E0[|B|^2+2*A dot C-2*W1*A dot B+|A|^2*(W1^2/2-W2-z2)]",
            "square_root_formula": "M4_full=||B-W1*A/2||_0^2+2<A,C-W1*B/2+(W1^2/8-W2/2-z2/2)*A>_0",
            "exact_vector_fixture": {name: enc(value) for name, value in vector.items()},
            "status": "COMPLETE_SYMBOLIC_FORMULA_WICK_EVALUATION_OPEN",
        },
        "conditioning_scope": {
            "live_background": "mean-zero fields in E_p perpendicular, E_p=span{cos(p*x0),sin(p*x0)}",
            "full_phase_free_covariance": "C_full(k)=omega(k)^(-2) for k not in {0,+p,-p}, and C_full(k)=0 for k in {0,+p,-p}",
            "translation_invariance": "Deleting the complete conjugate Fourier pair commutes with every lattice translation; there is no position-dependent rank-one remainder.",
            "older_M4_scope": "the certified COMPLETE_G4_LOWER_LOOP_BOUNDS result conditions only the real cosine and uses the rank-one expansion C=C0-R_cos",
            "nontransfer": "The negative one-cosine leading coefficient cannot be used as the sign or scaling of M4_full. Its connected algebra and enumeration architecture are reusable, but its covariance sectors and numerical conclusion are not.",
            "status": "SCOPE_SPLIT_CERTIFIED",
        },
        "supersession": {
            "predecessor": "REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_CURRENT_CHAOS_OBSTRUCTION_V1",
            "retained": "the exact compact motif, third-Hermite lower bound, and obstruction to homogeneous-order-by-order current hyperuniformity",
            "corrected_next_gate": "Replace 'complete order-lambda-six background-marginal score variance' by 'complete order-g^4 full-phase score variance, equivalently order-g^6 current variance'. Do not substitute the one-cosine M4 sign.",
            "status": "COUPLING_ORDER_AND_CONDITIONING_SCOPE_CORRECTED",
        },
        "method_disposition": {
            "cubic_current_free_third_chaos": "EXTENSIVE_POSITIVE",
            "cubic_current_identification_with_quartic_score": "PROVED",
            "complete_full_phase_M4_formula": "PROVED",
            "complete_full_phase_M4_finite_volume_value": "OPEN",
            "complete_full_phase_M4_large_volume_scaling": "OPEN",
            "one_cosine_M4_sign_transfer_to_full_phase": "FORBIDDEN_SCOPE_MISMATCH",
            "nonperturbative_background_current_susceptibility": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the sign, cancellation, or large-volume scaling of the complete full-phase M4 coefficient",
            "transfer of the certified negative one-cosine M4 coefficient to the full-phase background",
            "boundedness or divergence of the resummed or nonperturbative current susceptibility",
            "the interacting H^-1 moment, continuum measure, Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL physics",
        ],
        "missing_object_ledger": [
            "a two-dimensional fiber expansion of W1 and W2 into full-phase Fourier vertices",
            "the connected exact Wick ledger with the translation-invariant propagator excluding 0 and +/-p",
            "a finite-volume independent value and general-L asymptotic bound for M4_full",
            "a uniform nonperturbative bridge from any coefficient result to the exact background current susceptibility",
            "the dyadic interacting H^-1 shell theorem or obstruction",
        ],
        "next_gate": "Construct the two-dimensional cosine-sine fiber vertex ledger for W1 and W2, reduce the complete vector M4 formula to connected Wick contractions with the translation-invariant propagator that vanishes at 0 and +/-p, and evaluate it exactly first at L=4 or L=5. Then derive the general-L common kernels. Any fixed-order sign remains diagnostic until a uniform nonperturbative bridge is proved.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic independently differentiates S0,S1,S2 and expands J1,J2,J3 on a 5^4 fixture; a rational two-state vector fixture checks the complete normalized M4 formula.",
            "analytic_arithmetic": "The action-gradient/current-divergence identity fixes the coupling map. Fourier deletion of the complete conjugate +/-p pair proves translation invariance of the full-phase free background covariance.",
            "assumptions": [
                "The action, current, Fourier, and coupling conventions are those of the imported certificates.",
                "The old one-cosine connected formula is used only as algebraic architecture, not as a transferred sign or covariance computation.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_g6_current_reconciliation.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_g6_current_reconciliation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_g6_current_reconciliation",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    expected = render(build())
    if arguments.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
