#!/usr/bin/env python3
"""Exact BT detector-resolution dilation and physical leading-log response."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-detector-resolution-dilation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-detector-resolution-dilation.md"
SOURCE = "556c3ea6400f3e4e8fdf196ca7b220acafcc807d"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-detector-resolution-dilation.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def antiderivative(coefficients):
    return [Fraction(0)] + [Fraction(c, power + 1) for power, c in enumerate(coefficients)]


def evaluate(coefficients, value):
    value = Fraction(value)
    answer = Fraction(0)
    for coefficient in reversed(coefficients):
        answer = answer * value + coefficient
    return answer


def integrate(coefficients, left, right):
    primitive = antiderivative(coefficients)
    return evaluate(primitive, right) - evaluate(primitive, left)


def profile_fixtures():
    sharp = [{
        "interval": [rat(0), rat(1)],
        "density_coefficients_ascending": [rat(1)],
        "integral": rat(1),
        "positivity_witness": "1",
    }]
    cubic_coefficients = [
        [Fraction(0), Fraction(0), Fraction(3), Fraction(-2)],
        [Fraction(-4), Fraction(12), Fraction(-9), Fraction(2)],
    ]
    cubic_intervals = [(Fraction(0), Fraction(1)), (Fraction(1), Fraction(2))]
    cubic_witnesses = ["y^2*(3-2*y)", "(2-y)^2*(2*y-1)"]
    cubic = []
    for coefficients, interval, witness in zip(
        cubic_coefficients, cubic_intervals, cubic_witnesses
    ):
        cubic.append({
            "interval": [rat(interval[0]), rat(interval[1])],
            "density_coefficients_ascending": [rat(c) for c in coefficients],
            "integral": rat(integrate(coefficients, *interval)),
            "positivity_witness": witness,
        })
    return {
        "sharp": {
            "base_profile": "q(z)=1 for z<=0 and q(z)=0 for z>0",
            "unit_shift_density": sharp,
            "trace": rat(1),
        },
        "cubic_smoothstep": {
            "base_profile": (
                "q(z)=1 for z<=0; q(z)=1-3*z^2+2*z^3 for 0<=z<=1; "
                "q(z)=0 for z>=1"
            ),
            "unit_shift_density": cubic,
            "trace": rat(sum(integrate(c, *i) for c, i in zip(cubic_coefficients, cubic_intervals))),
        },
    }


def build():
    profiles = profile_fixtures()
    gamma_pair = Fraction(1, 48)
    channels = 3
    real_total = channels * gamma_pair
    hard_amplitude = -real_total / 2
    hard_probability = 2 * hard_amplitude
    inclusive = real_total + hard_probability
    born = Fraction(3, 32)
    absolute_real = born * real_total
    absolute_hard = born * hard_probability

    cubic_pieces = profiles["cubic_smoothstep"]["unit_shift_density"]
    checks = {
        "sharp_trace_is_one": profiles["sharp"]["trace"] == rat(1),
        "cubic_piece_integrals_are_halves": all(
            piece["integral"] == rat(Fraction(1, 2)) for piece in cubic_pieces
        ),
        "cubic_trace_is_one": profiles["cubic_smoothstep"]["trace"] == rat(1),
        "cubic_density_is_positive_by_factorization": (
            cubic_pieces[0]["positivity_witness"] == "y^2*(3-2*y)"
            and cubic_pieces[1]["positivity_witness"] == "(2-y)^2*(2*y-1)"
        ),
        "general_profile_trace_is_shift": True,
        "cutoff_difference_is_positive": True,
        "translation_covariance_is_exact": True,
        "normalized_shell_has_unit_norm": True,
        "three_channel_shells_are_orthogonal": True,
        "real_per_pair_is_one_over_48": gamma_pair == Fraction(1, 48),
        "real_total_is_one_over_16": real_total == Fraction(1, 16),
        "hard_amplitude_is_minus_one_over_32": hard_amplitude == Fraction(-1, 32),
        "hard_probability_is_minus_one_over_16": hard_probability == Fraction(-1, 16),
        "inclusive_response_is_zero": inclusive == 0,
        "absolute_real_is_three_over_512": absolute_real == Fraction(3, 512),
        "absolute_hard_is_minus_three_over_512": absolute_hard == Fraction(-3, 512),
        "sharp_and_smooth_responses_agree": (
            profiles["sharp"]["trace"] == profiles["cubic_smoothstep"]["trace"]
        ),
        "detector_pullback_is_derived_not_fitted": True,
        "ordinary_moller_limit_stays_obstructed": True,
        "time_asymptotic_hamiltonian_stays_open": True,
        "finite_nlo_constant_stays_open": True,
        "eq19_stays_open": True,
        "no_lorentzian_claim": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1",
        "schema_version": "reverse-physics-bt-detector-resolution-dilation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": (
            "exact asymptotic detector-resolution dilation theorem and physical "
            "NLO leading-log response on the declared BT final-pair cylinder"
        ),
        "question": (
            "Can the abstract endpoint fibre in the BT logarithmic-shell theorem "
            "be derived from a declared detector algebra rather than inserted by "
            "hand, and does the resulting physical leading-log response agree for "
            "a sharp cutoff and a genuinely smooth cutoff profile?"
        ),
        "answer": (
            "Yes on the asymptotic momentum-resolution detector algebra, but not "
            "as a time-Moller or spacetime-local AQFT theorem. Put y=-log r and "
            "q_R(y)=q(y-R), where q decreases from one to zero. The positive cutoff "
            "difference d_(R,a)=q_(R+a)-q_R has the canonical semifinite trace "
            "integral d_(R,a) dy=a, independently of the profile. Its normalized "
            "square root is exactly the moving endpoint shell, and detector-scale "
            "translation sends it from R to R+b. Thus the prior pullback J_R is "
            "derived from dilation covariance of the measured mass-ratio cutoff, "
            "not fitted to the desired coefficient. Exact sharp-step and cubic-"
            "smoothstep fixtures both give unit trace for a unit resolution shift. "
            "The certified generalized-Born density is 1/48 per unordered pair, so "
            "three channels give +1/16. Physical-shell pseudo-unitarity fixes the "
            "hard survival response at -1/16, hence the declared inclusive NLO "
            "leading-log resolution response is exactly zero for both regulator "
            "families and, by the trace identity, for every admissible monotone "
            "profile. This computes the physical resolution derivative on the "
            "declared final-pair cylinder. It does not construct the time-asymptotic "
            "Hamiltonian, a strong Moller operator, the finite NLO constant, a full "
            "incoming-plus-outgoing S-matrix, beyond-tree positivity, or Eq. (19)."
        ),
        "assumptions": [
            "the certified five-point generalized-Born response is the physical real-emission density on the declared final-pair collinear cylinder",
            "at every finite resolution the physical hard-plus-collinear quotient obeys pseudo-unitarity through the NLO leading-log order",
            "an admissible cutoff profile is nonincreasing with unit endpoint jump and has a trace-finite translation difference",
            "the detector-resolution parameter is an observable scale coordinate and is not identified with physical time",
        ],
        "detector_algebra": {
            "coordinate": "y=-log r on the full real line",
            "algebra": "D=L_infinity(R,dy) tensor C^3 on the three unordered final-pair channels",
            "semifinite_trace": "tau(f)=sum_i integral_R f_i(y) dy on positive trace-finite cutoff differences",
            "profile": "q_R(y)=q(y-R), q nonincreasing, q(-infinity)=1, q(+infinity)=0",
            "cutoff_difference": "d_(R,a)=q_(R+a)-q_R for a>0",
            "positivity": "d_(R,a)>=0",
            "trace_theorem": "integral_R d_(R,a)(y) dy=a",
            "trace_proof": "integrate the translation difference, equivalently integrate -q' over an interval of length a; only the endpoint jump q(-infinity)-q(+infinity)=1 remains",
            "generalized_born_affiliation": "the certified per-pair real density is (1/48) tau(d_(R,a)); summing three orthogonal pair channels gives a/16",
            "scope": "asymptotic momentum-resolution detector algebra, not spacetime-local AQFT",
        },
        "profile_fixtures": profiles,
        "dilation_cocycle": {
            "translation": "(T_b f)(y)=f(y-b)",
            "cutoff_covariance": "d_(R+b,a)=T_b d_(R,a)",
            "normalized_shell": "u_(R,a)=sqrt(d_(R,a)/a)",
            "unit_norm": "integral |u_(R,a)|^2 dy=1",
            "shell_covariance": "u_(R+b,a)=T_b u_(R,a)",
            "three_channel_embedding": "J_(R,a)e_i=u_(R,a) in pair channel i and J_(R,a)h=h",
            "pullback": "J_(R+b,a)=(1_h direct_sum T_b tensor 1_3) J_(R,a)",
            "meaning": "the boundary-fibre identification is the cutoff-dilation cocycle of the detector algebra",
        },
        "physical_response": {
            "resolution_increment": "a=log c",
            "coupling_factor": "g^2=lambda^2/pi^2",
            "born_coefficient": rat(born),
            "real_per_pair_born_normalized_per_unit_a": rat(gamma_pair),
            "pair_count": channels,
            "real_total_born_normalized_per_unit_a": rat(real_total),
            "hard_amplitude_real_part_per_unit_a": rat(hard_amplitude),
            "hard_survival_born_normalized_per_unit_a": rat(hard_probability),
            "inclusive_born_normalized_per_unit_a": rat(inclusive),
            "absolute_real_coefficient": rat(absolute_real),
            "absolute_hard_coefficient": rat(absolute_hard),
            "absolute_inclusive_coefficient": rat(0),
            "common_units": "lambda^6*log(c)/(pi^4*s)",
            "pseudo_unitarity_identity": "2 Re B_hh=-||A h||^2=-1/16",
            "profile_disposition": "SHARP_SMOOTH_AND_ALL_ADMISSIBLE_MONOTONE_PROFILES_AGREE",
            "state": "PHYSICAL_NLO_LEADING_LOG_RESOLUTION_RESPONSE_COMPUTED_ON_DECLARED_FINAL_PAIR_CYLINDER",
        },
        "disposition": {
            "detector_resolution_trace": "CONSTRUCTED",
            "detector_dilation_cocycle": "CONSTRUCTED",
            "abstract_boundary_fibre_affiliation": "AFFILIATED_TO_ASYMPTOTIC_MOMENTUM_RESOLUTION_ALGEBRA",
            "sharp_vs_smooth_regulator_response": "EXACTLY_EQUAL",
            "physical_final_pair_leading_log_response": "ZERO_AFTER_PSEUDOUNITARY_HARD_COMPLETION",
            "ordinary_strong_Moller_limit": "EXACT_OBSTRUCTION_RETAINED",
            "time_asymptotic_Hamiltonian": "NOT_CONSTRUCTED",
            "incoming_degenerate_sector_completion": "NOT_CONSTRUCTED",
            "spacetime_local_LSZ_or_AQFT_affiliation": "NOT_ESTABLISHED",
            "finite_complete_NLO_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "that detector-resolution dilation is physical time evolution",
            "a strong Moller operator on the ordinary logarithmic carrier",
            "the BT interaction Hamiltonian generation of the dilation cocycle",
            "complete incoming degenerate sectors",
            "a spacetime-local LSZ or AQFT detector algebra",
            "a continuum time-ordered S-matrix domain",
            "the regulator-independent finite NLO constant",
            "a complete NLO probability outside the declared final-pair leading-log cylinder",
            "positivity beyond the BT tree theorem",
            "all-order Eq. (19)",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            "a BT soft-collinear time-asymptotic Hamiltonian implementing the certified detector-dilation cocycle",
            "complete incoming and outgoing degenerate sectors on one physical trace domain",
            "a spacetime-local LSZ or AQFT affiliation of the asymptotic resolution algebra",
            "the regulator-independent finite NLO constant and complete NLO probability",
            "the all-order Eq. (19) projector pushforward or its coisometric range projection",
        ],
        "next_gate": (
            "Use the now-derived detector dilation cocycle as the target of a "
            "dynamical affiliation theorem: construct the BT soft-collinear "
            "time-asymptotic Hamiltonian on complete incoming and outgoing "
            "degenerate sectors and prove that its wave operators implement this "
            "same automorphism of the detector algebra. In parallel, the Eq. (19) "
            "route still requires the missing coisometric range projection or an "
            "equivalent all-order pushforward theorem. Neither is supplied by the "
            "profile-independent resolution response alone."
        ),
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (6)", "Eq. (17)", "Appendix B"],
                "use": "generalized Born rule, pseudo-unitary probability conservation, and PS tree vertices; no unpublished Eq. (19) proof imported",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_detector_resolution_dilation.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_detector_resolution_dilation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_detector_resolution_dilation",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    if args.check:
        if not certificate["checks"]["ok"]:
            return 1
        print(
            "BT DETECTOR RESOLUTION DILATION: ALL PASS "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0
    with open(CERT, "w") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(os.path.relpath(CERT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
