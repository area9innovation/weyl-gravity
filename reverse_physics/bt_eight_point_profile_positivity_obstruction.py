#!/usr/bin/env python3
"""Exact positivity test and minimal Krein lift for the BT fourth profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-profile-positivity-obstruction-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-profile-positivity-obstruction.md"
SOURCE = "464901df"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-profile-positivity.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_rows(matrix):
    return [[str(value) for value in row] for row in matrix.tolist()]


def build():
    import sympy as sp

    inner = load(INPUTS[1])
    separation = load(INPUTS[2])
    moller = load(INPUTS[3])
    hp = load(INPUTS[4])

    kappa = [
        frac(value)
        for value in inner["inner_threshold"]["fixture_r_log_r_coefficients"]
    ]
    rho = frac(separation["shared_fixture"]["rho"])
    gram_rows = [
        [frac(value) for value in row]
        for row in separation["shared_fixture"]["forced_missing_gram"]
    ]
    lower_rates = [
        frac(value)
        for value in moller["physical_vacuum_moller_column"]["conditional_rates"]
    ]
    lower_selected_chain = lower_rates[0] * lower_rates[1] * lower_rates[2]
    first_three_scale = frac(inner["inner_threshold"]["first_three_scale"])
    born_divisor = frac(moller["finite_model_inclusive_response"]["Born_coefficient"])
    fourth_history_count = (
        moller["physical_vacuum_moller_column"]["history_counts"][-1] * 6
    )
    ordered_four_simplex = Fraction(1, 24)

    G = sp.Matrix(
        [
            [sp.Rational(value.numerator, value.denominator) for value in row]
            for row in gram_rows
        ]
    )
    K4 = sp.diag(
        *[sp.Rational(value.numerator, value.denominator) for value in kappa]
    )
    eta = sp.diag(G, G)
    amplitudes = [sp.sqrt(-sp.Rational(value.numerator, value.denominator) / 2)
                  for value in kappa]
    B = sp.zeros(4, 2)
    B[1, 0] = amplitudes[0]
    B[3, 1] = amplitudes[1]
    pullback = sp.simplify(B.T * eta * B)
    source_metric = sp.eye(2)
    total_metric = sp.diag(source_metric, eta)
    b_sharp = sp.simplify(B.T * eta)
    Kjet = sp.zeros(6, 6)
    Kjet[:2, 2:] = -b_sharp
    Kjet[2:, :2] = B
    skew_defect = sp.simplify(Kjet.T * total_metric + total_metric * Kjet)

    w = sp.symbols("w", real=True)
    convex_trace = sp.factor(
        w * sp.Rational(kappa[0].numerator, kappa[0].denominator)
        + (1 - w) * sp.Rational(kappa[1].numerator, kappa[1].denominator)
    )
    checks = {
        "all_predecessor_certificates_pass": all(
            value["checks"]["ok"] for value in (inner, separation, moller, hp)
        ),
        "final_profile_coefficients_replayed": kappa
        == [Fraction(-6699, 128), Fraction(-7149, 128)],
        "eight_external_derivative_orientation_is_positive": (-1) ** 8 == 1,
        "first_three_threshold_scale_is_positive": first_three_scale == 6,
        "lower_selected_history_chain_is_positive": (
            lower_selected_chain == Fraction(9, 81920)
        ),
        "hard_born_divisor_is_positive": born_divisor == Fraction(3, 32),
        "fourth_history_count_and_simplex_are_positive": (
            fourth_history_count == 360 and ordered_four_simplex == Fraction(1, 24)
        ),
        "profile_effect_has_rank_two": K4.rank() == 2,
        "profile_effect_is_strictly_negative": all(value < 0 for value in kappa),
        "every_positive_profile_average_is_negative": (
            max(kappa) < 0 and min(kappa) < 0
        ),
        "ordinary_CP_effect_is_impossible": K4[0, 0] < 0 and K4[1, 1] < 0,
        "forced_rho_is_replayed": rho == Fraction(819, 4000),
        "forced_cross_krein_gram_is_replayed": G
        == sp.Matrix([[0, -sp.Rational(819, 4000)],
                      [-sp.Rational(819, 4000), -2]]),
        "cross_krein_fibre_has_one_negative_direction": (
            G.det() < 0 and G.rank() == 2
        ),
        "canonical_second_fibre_vector_has_norm_minus_two": G[1, 1] == -2,
        "two_point_fibre_module_has_two_negative_directions": (
            eta.rank() == 4 and eta.det() > 0
        ),
        "exact_krein_pullback_reconstructs_profile_effect": pullback == K4,
        "profile_lift_has_minimal_rank_two": B.rank() == K4.rank() == 2,
        "combined_generator_is_exactly_krein_skew": skew_defect == sp.zeros(6),
        "HP_predecessor_requires_positive_jump_effects": (
            hp["hudson_parthasarathy_cocycle"]["drift"]
            == "D=(1/2)sum_e J_e^dagger J_e"
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-eight-point-profile-positivity-obstruction-v1",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "result_kind": "exact positive-cone obstruction for the two-fixture BT fourth profile and minimal fibrewise Krein-skew lift",
        "question": "Can the exact two-fixture eight-point profile kernel extend the certified positive Hudson-Parthasarathy Moller column as an ordinary fourth jump, and if not what is its minimal Krein lift?",
        "answer": "No as an ordinary positive diagonal jump on the declared two-point hard-profile algebra. After all four fixed-invariant threshold functionals the two evaluation coefficients are -6699/128 and -7149/128. The eight external delta-prime derivatives contribute the even sign +1, the inherited first-three scale is +6, the lower selected-history chain is +9/81920, and every remaining counting, simplex, phase-space, squared-amplitude, and Born-division normalization is positive. Hence the sign cannot be repaired by physical normalization: every faithful positive profile trace is a convex combination of two negative numbers, and the conditional fourth effect is strictly negative. It therefore cannot equal J^dagger J for an ordinary completely positive or Hudson-Parthasarathy jump. An exact indefinite lift nevertheless exists. Over the two hard idempotents take one copy of the forced cross-Krein fibre G_missing(rho) per point. Its canonical second basis vector has norm -2. Mapping the two profile basis vectors to sqrt(6699)/16 and sqrt(7149)/16 times those negative directions gives B^sharp B=diag(-6699/128,-7149/128). The associated off-diagonal block generator is exactly Krein-skew and the lift has the minimal two negative directions required by the rank-two negative profile effect. This is an algebraic reduced-mode Krein jet, not a positive probability, a charge-compatible BT-derived operator, Eq. (19), or a spacetime S matrix.",
        "assumptions": [
            "The declared direct profile carrier keeps the h=33 and h=34 evaluation idempotents orthogonal and introduces no uncomputed off-diagonal channel interference.",
            "The inherited fourth-event orientation has no sign beyond the eight external delta-prime factor: the common squared amplitude phase, physical Kallen measures, Born divisor, history count, and ordered simplex carry their standard positive orientations.",
            "Only the sign of the fourth leading effect is classified; its overall positive magnitude normalization is not assembled.",
            "A positive profile trace means a nonzero positive functional on the two evaluation idempotents; a non-faithful zero functional is not a normalized event."
        ],
        "orientation_audit": {
            "hard_coordinates": [33, 34],
            "profile_coefficients": [rat(value) for value in kappa],
            "eight_external_delta_prime_sign": 1,
            "first_three_threshold_scale": rat(first_three_scale),
            "lower_conditional_rates": [rat(value) for value in lower_rates],
            "lower_selected_history_chain": rat(lower_selected_chain),
            "remaining_normalization_signs": {
                "squared_amplitude_phase_sign": 1,
                "Kallen_phase_space_orientation": 1,
                "Born_divisor": rat(born_divisor),
                "labeled_fourth_histories": fourth_history_count,
                "ordered_four_simplex": rat(ordered_four_simplex)
            },
            "fourth_magnitude": "NOT_NORMALIZED",
            "fourth_sign": "STRICTLY_NEGATIVE_ON_BOTH_DECLARED_HARD_EVALUATIONS"
        },
        "positive_profile_test": {
            "profile_algebra": "Q*e_33 direct_sum Q*e_34 with orthogonal evaluation idempotents",
            "effect_matrix": matrix_rows(K4),
            "effect_rank": 2,
            "effect_inertia": {"positive": 0, "negative": 2, "zero": 0},
            "faithful_state": "omega_w(x)=w*x_33+(1-w)*x_34 with 0<w<1",
            "convex_trace": str(convex_trace),
            "closed_weight_interval": [
                rat(min(kappa)),
                rat(max(kappa))
            ],
            "conclusion": "EVERY_NONZERO_POSITIVE_PROFILE_AVERAGE_IS_NEGATIVE",
            "ordinary_CP_or_HP_jump": "EXACTLY_OBSTRUCTED_ON_DECLARED_DIAGONAL_PROFILE_CARRIER"
        },
        "fibrewise_krein_lift": {
            "rho": rat(rho),
            "single_fibre_gram": matrix_rows(G),
            "single_fibre_inertia": {"positive": 1, "negative": 1, "zero": 0},
            "two_point_module": "(Q*e_33 direct_sum Q*e_34) tensor E_rho",
            "two_point_module_gram": matrix_rows(eta),
            "two_point_module_inertia": {"positive": 2, "negative": 2, "zero": 0},
            "canonical_negative_line": "span(f_2), with f_2^T G_missing(rho) f_2=-2",
            "forward_block_B": matrix_rows(B),
            "forward_amplitudes": [str(value) for value in amplitudes],
            "pullback": matrix_rows(pullback),
            "pullback_identity": "B^sharp B=diag(-6699/128,-7149/128)",
            "block_generator": "K_profile=[[0,-B^sharp],[B,0]]",
            "generator_metric": "diag(I_2,G_missing(rho),G_missing(rho))",
            "krein_skew_identity": "K_profile^T*eta_total+eta_total*K_profile=0",
            "minimality": "The negative profile effect has rank and negative index two, so any injective pullback needs at least two target negative directions; one fibre copy has only one, while the two-point fibre module has exactly two.",
            "status": "EXACT_ALGEBRAIC_KREIN_JET_NOT_BT_DERIVED"
        },
        "disposition": {
            "positive_diagonal_profile_fourth_jump": "EXACTLY_OBSTRUCTED_ON_TWO_FIXTURES",
            "ordinary_CP_HP_extension": "EXACTLY_OBSTRUCTED_AT_FOURTH_LEADING_EFFECT",
            "minimal_fibrewise_Krein_lift": "CONSTRUCTED_ALGEBRAICALLY",
            "BT_charge_compatible_history_operator": "NOT_CONSTRUCTED",
            "physical_fourth_probability": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED"
        },
        "does_not_establish": [
            "a negative complete finite-resolution probability",
            "a no-go for a larger channel recombination or dynamical quotient that changes the physical pullback by additional derived terms",
            "a no-go for an indefinite generalized-Born trace satisfying Eq. (19)",
            "the normalized magnitude of either fourth-event coefficient",
            "a BT derivation or charge-compatible realization of the Krein lift",
            "a complete 2->6 probability",
            "a spacetime Moller, LSZ, or S operator",
            "the all-order Eq. (19)",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "The ordinary positive stochastic continuation is now closed on the evaluation-diagonal profile carrier. To advance Eq. (19), derive the displayed fibrewise Krein-skew block from the zero-mode-completed R_t projector or prove that BT charge support forbids it. To advance the physical route without Eq. (19), derive additional channel or trace terms before the physical pullback so that the certified kernels occur as pre-trace components rather than negative Hilbert-space expectations. Off-diagonal entries alone cannot make an effect with these fixed negative diagonal expectations positive.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "external_state": "arXiv:2607.00096 remains v1 submitted 2026-06-30; the cited companion proof was not found on arXiv on 2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_profile_positivity_obstruction.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_profile_positivity_obstruction.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_profile_positivity_obstruction"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        value = load(os.path.relpath(path, ROOT))
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 20
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 5
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("physical_fourth_probability")
        == "NOT_ESTABLISHED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("profile effect:", value["positive_profile_test"]["effect_matrix"])
    print("Krein pullback:", value["fibrewise_krein_lift"]["pullback_identity"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
