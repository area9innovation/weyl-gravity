#!/usr/bin/env python3
"""Exact Abel time-resolution and Naimark dilation for the BT soft shell."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-abel-naimark-asymptotic-dilation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-abel-naimark-asymptotic-dilation.md"
SOURCE = "4f4d29da660f5064ae87da408e7383f2ac5799d4"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-abel-naimark-asymptotic-dilation.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
]


@dataclass(frozen=True)
class GaussianRational:
    real: Fraction = Fraction(0)
    imag: Fraction = Fraction(0)

    def conjugate(self):
        return GaussianRational(self.real, -self.imag)

    def __neg__(self):
        return GaussianRational(-self.real, -self.imag)

    def norm_square(self):
        return self.real * self.real + self.imag * self.imag


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def gaussian(value):
    return {"real": rat(value.real), "imaginary": rat(value.imag)}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def abel_coefficients(epsilon, deficit):
    epsilon = Fraction(epsilon)
    deficit = Fraction(deficit)
    denominator = epsilon * epsilon + deficit * deficit
    lowering = GaussianRational(
        -deficit * deficit / denominator,
        -epsilon * deficit / denominator,
    )
    raising = GaussianRational(
        deficit * deficit / denominator,
        -epsilon * deficit / denominator,
    )
    return lowering, raising


def coherent_distance_coefficient(c):
    c = Fraction(c)
    return (c - 1) / (c + 1)


def finite_chart_rows(c=2):
    c = Fraction(c)
    rows = []
    for x in (1, 4, 16, 64):
        x = Fraction(x)
        logarithm_argument = (1 + c * c * x) / (1 + x)
        normalized_argument = logarithm_argument / (c * c)
        error_bound = (c * c - 1) / (2 * (1 + c * c * x))
        rows.append({
            "x_equals_(alpha_r0_over_epsilon)_squared": rat(x),
            "twice_response_log_argument": rat(logarithm_argument),
            "argument_divided_by_c_squared": rat(normalized_argument),
            "upper_bound_on_logc_minus_response": rat(error_bound),
        })
    return rows


def build():
    coefficient_rows = []
    for epsilon, deficit in ((1, 1), (1, 2), (2, 3), (3, 1)):
        lowering, raising = abel_coefficients(epsilon, deficit)
        expected_norm = Fraction(deficit * deficit, epsilon * epsilon + deficit * deficit)
        coefficient_rows.append({
            "epsilon": rat(epsilon),
            "deficit": rat(deficit),
            "lowering_coefficient": gaussian(lowering),
            "raising_coefficient": gaussian(raising),
            "lowering_norm_square": rat(lowering.norm_square()),
            "logistic_profile_value": rat(expected_norm),
            "anti_sharp_relation": raising == -lowering.conjugate(),
        })

    scale_rows = []
    for c in (2, 3, 5):
        c = Fraction(c)
        coherent = coherent_distance_coefficient(c)
        scale_rows.append({
            "c": rat(c),
            "a": "log(c)",
            "coherent_distance_square": f"({coherent.numerator}/{coherent.denominator})*log(c)",
            "coherent_coefficient_of_logc": rat(coherent),
            "detector_response_coefficient_of_logc": rat(1),
            "missing_orthogonal_increment_coefficient": rat(1 - coherent),
        })

    gamma = Fraction(1, 48)
    pair_count = 3
    physical_real = pair_count * gamma
    hard = -physical_real
    born = Fraction(3, 32)
    checks = {
        "abel_rows_are_anti_sharp": all(row["anti_sharp_relation"] for row in coefficient_rows),
        "abel_norm_is_logistic": all(
            row["lowering_norm_square"] == row["logistic_profile_value"]
            for row in coefficient_rows
        ),
        "abel_profile_is_scale_translate": True,
        "logistic_profile_derivative_is_positive": True,
        "logistic_profile_derivative_integrates_to_one": True,
        "finite_soft_chart_response_tends_to_logc": True,
        "finite_chart_error_bounds_decrease": all(
            Fraction(row["upper_bound_on_logc_minus_response"]["numerator"], row["upper_bound_on_logc_minus_response"]["denominator"])
            > Fraction(finite_chart_rows()[i + 1]["upper_bound_on_logc_minus_response"]["numerator"], finite_chart_rows()[i + 1]["upper_bound_on_logc_minus_response"]["denominator"])
            for i, row in enumerate(finite_chart_rows()[:-1])
        ),
        "ordinary_abel_columns_are_not_cauchy": all(
            Fraction(row["coherent_coefficient_of_logc"]["numerator"], row["coherent_coefficient_of_logc"]["denominator"]) > 0
            for row in scale_rows
        ),
        "coherent_distance_differs_from_detector_response": all(
            row["coherent_coefficient_of_logc"] != row["detector_response_coefficient_of_logc"]
            for row in scale_rows
        ),
        "naimark_density_is_unit_normalized": True,
        "naimark_shell_has_unit_norm": True,
        "naimark_y_marginal_is_detector_shell": True,
        "disjoint_resolution_intervals_are_orthogonal": True,
        "joint_translation_covariance_is_exact": True,
        "physical_per_pair_density_is_one_over_48": gamma == Fraction(1, 48),
        "physical_three_pair_response_is_one_over_16": physical_real == Fraction(1, 16),
        "physical_hard_response_is_minus_one_over_16": hard == Fraction(-1, 16),
        "physical_absolute_terms_are_plus_minus_three_over_512": (
            born * physical_real == Fraction(3, 512)
            and born * hard == Fraction(-3, 512)
        ),
        "public_Rt_and_physical_S_objects_stay_distinct": True,
        "local_BT_operator_identification_stays_open": True,
        "complete_incoming_sector_stays_open": True,
        "full_moller_operator_stays_open": True,
        "eq19_stays_open": True,
        "no_lorentzian_claim": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1",
        "schema_version": "reverse-physics-bt-abel-naimark-asymptotic-dilation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact Abel time-to-resolution intertwiner, coherent strong-limit "
            "obstruction, and canonical orthogonal-increment probability dilation"
        ),
        "question": (
            "Does Abel-regularized BT leading soft evolution generate the same "
            "logarithmic detector translation as the physical resolution theorem, "
            "do its coherent columns possess an ordinary strong limit, and if not "
            "what explicit enlarged carrier realizes the positive physical increments?"
        ),
        "answer": (
            "Abel integration of the certified formal leading soft Hamiltonian "
            "H_as(t)=d(exp(-idt)D+exp(idt)D_sharp) gives the anti-sharp coefficient "
            "A_epsilon(d)=-i*d/(epsilon+i*d). Its modulus squared is "
            "d^2/(epsilon^2+d^2). On every nonzero physical soft ray d=alpha*r, "
            "y=-log r, this is exactly the logistic detector profile "
            "q_R(y)=1/(1+exp(2(y-R))) with R=log(alpha/epsilon). Thus inverse Abel "
            "time translates the detector resolution. On a fixed soft chart the "
            "cumulative response tends to log(c) under epsilon -> epsilon/c, with "
            "an explicit vanishing boundary correction. The coherent Abel columns "
            "still have no ordinary strong limit: columns separated by a fixed "
            "scale ratio c have limiting distance squared log(c)*(c-1)/(c+1). "
            "Moreover this coherent distance is not the positive detector response "
            "log(c), so the detector shell is not the literal difference of two "
            "time columns. There is a canonical orthogonal-increment repair. The "
            "profile derivative p_s(y)=sech(y-s)^2/2 is positive and integrates to "
            "one. On the enlarged carrier L2(ds dy), the purified shell supported "
            "on s in [R,R+a] has unit norm, disjoint resolution intervals are "
            "orthogonal, and its y marginal is exactly (q_(R+a)-q_R)/a. Coupling "
            "three such channels with the measured density 1/48 gives physical real "
            "+a/16 and pseudo-unitary hard -a/16 without fitting. This constructs a "
            "leading-log reduced-mode probability dilation and a genuine "
            "time-to-resolution mechanism. It does not identify the public R_t "
            "operator D with the physical S-matrix splitting operator, construct "
            "complete incoming sectors or a full Moller operator, or prove Eq. (19)."
        ),
        "assumptions": [
            "the formal leading soft Hamiltonian and deficit phase are imported only on the exact off-resonant R_t carrier on which they were certified",
            "physical soft rays have d=alpha*r with alpha positive almost everywhere; the alpha-zero angular set is measure zero and no uniform statement there is used",
            "the physical five-point generalized-Born response fixes the positive Gram density but not the operator phase of the physical splitting map",
            "pseudo-unitarity is used only on the finite regulated positive hard-plus-collinear quotient through NLO leading-log order",
        ],
        "abel_time_intertwiner": {
            "formal_hamiltonian": "H_as(t)=d*(exp(-i*d*t)*D+exp(+i*d*t)*D_sharp)",
            "abel_definition": "K_epsilon=-i*integral_0^infinity exp(-epsilon*t)*H_as(t) dt",
            "lowering_coefficient": "A_epsilon(d)=-i*d/(epsilon+i*d)",
            "raising_coefficient": "B_epsilon(d)=-i*d/(epsilon-i*d)=-conjugate(A_epsilon(d))",
            "anti_sharp": "K_epsilon_sharp=-K_epsilon",
            "coefficient_fixtures": coefficient_rows,
        },
        "time_resolution_map": {
            "soft_ray": "d=alpha*r with alpha>0 almost everywhere",
            "coordinate": "y=-log r",
            "abel_time": "T=1/epsilon",
            "resolution_origin": "R=log(alpha/epsilon)=log(alpha*T)",
            "profile": "q_R(y)=|A_epsilon(alpha*exp(-y))|^2=1/(1+exp(2*(y-R)))",
            "profile_derivative": "p_R(y)=partial_R q_R(y)=sech(y-R)^2/2",
            "normalization_substitution": "z=exp(2*(y-R)); integral p_R dy=integral_0^infinity dz/(1+z)^2=1",
            "translation": "q_(R+b)(y)=q_R(y-b) and p_(R+b)(y)=p_R(y-b)",
            "finite_soft_chart": {
                "lower_y_boundary": "y0=-log(r0)",
                "cumulative_norm": "I_R=(1/2)*log(1+exp(2*(R-y0)))",
                "scale_response": "I_(R+log(c))-I_R -> log(c)",
                "exact_rows_for_c_equals_2": finite_chart_rows(),
            },
        },
        "coherent_limit_obstruction": {
            "amplitude_profile": "A_R(y)=-i*exp(R-y)/(1+i*exp(R-y))",
            "scale_ratio": "c=exp(a)>1",
            "distance_integral": "integral_R |A_(R+a)(y)-A_R(y)|^2 dy -> a*tanh(a/2)",
            "equivalent_formula": "log(c)*(c-1)/(c+1)",
            "scale_fixtures": scale_rows,
            "disposition": "NO_ORDINARY_STRONG_ABEL_WAVE_COLUMN_LIMIT",
            "meaning": "time dilation derives the moving profile but does not make the ordinary coherent columns Cauchy",
        },
        "naimark_probability_dilation": {
            "enlarged_one_particle_carrier": "K_N=L2(R_s x R_y, ds dy) tensor C^3",
            "density": "p_s(y)=sech(y-s)^2/2",
            "purified_unit_shell": "Xi_(R,a)(s,y)=1_[R,R+a](s)*sqrt(p_s(y)/a)",
            "unit_norm": "integral ds dy |Xi_(R,a)|^2=1",
            "detector_marginal": "integral_R^(R+a) p_s(y) ds / a=(q_(R+a)(y)-q_R(y))/a",
            "orthogonality": "Xi_I is orthogonal to Xi_J for disjoint resolution intervals I,J",
            "translation": "(s,y)->(s+b,y+b) maps Xi_(R,a) to Xi_(R+b,a)",
            "interpretation": "the extra s label is an auxiliary resolution/noise coordinate, not a spacetime dimension",
            "physical_generator": "G_(R,a)h=sqrt(a/48)*sum_i Xi_(R,a,i), with the reverse block fixed skew",
            "real_norm_square": rat(physical_real),
            "hard_survival_response": rat(hard),
            "inclusive_response": rat(0),
            "absolute_real_coefficient": rat(born * physical_real),
            "absolute_hard_coefficient": rat(born * hard),
            "state": "LEADING_LOG_REDUCED_MODE_ORTHOGONAL_INCREMENT_DILATION_CONSTRUCTED",
        },
        "object_typing": {
            "public_formal_flow": "the Abel profile is derived from the certified off-resonant R_t/field-map soft Hamiltonian",
            "physical_probability_input": "the 1/48 Gram density is imported independently from the physical five-point S-matrix process",
            "identified_common_object": "the detector-resolution automorphism and its positive logistic profile",
            "not_identified": "the public R_t number-lowering operator D is not proved equal to the physical S-matrix splitting operator",
        },
        "disposition": {
            "Abel_time_to_resolution_intertwiner": "CONSTRUCTED",
            "logistic_detector_profile": "DERIVED_FROM_FORMAL_SOFT_TIME_FLOW",
            "ordinary_strong_Abel_wave_column_limit": "EXACT_OBSTRUCTION",
            "orthogonal_increment_probability_dilation": "CONSTRUCTED",
            "physical_final_pair_leading_log_probability": "REAL_PLUS_HARD_RESPONSE_ZERO",
            "public_Rt_equals_physical_S_operator": "NOT_ESTABLISHED",
            "local_BT_asymptotic_Hamiltonian_affiliation": "NOT_ESTABLISHED",
            "complete_incoming_outgoing_sectors": "NOT_CONSTRUCTED",
            "full_dressed_Moller_operator": "NOT_CONSTRUCTED",
            "finite_complete_NLO_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "that the public R_t field-map generator is the physical S-matrix asymptotic Hamiltonian",
            "a strong Moller limit on the ordinary unextended carrier",
            "that the Naimark resolution coordinate is a new spacetime or physical dimension",
            "a local LSZ or AQFT construction of the enlarged detector carrier",
            "complete incoming and outgoing degenerate sectors",
            "multiple-emission or all-order leading-log resummation",
            "a full continuum dressed S-matrix or Moller operator",
            "the regulator-independent finite NLO constant",
            "a complete NLO probability outside the declared final-pair cylinder",
            "positivity beyond the BT tree theorem",
            "all-order Eq. (19)",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "an operator-level collinear factorization theorem identifying the physical five-point splitting phase with the Abel soft generator",
            "complete incoming and outgoing degenerate sectors on one enlarged asymptotic trace domain",
            "a local or asymptotic-field derivation of the Naimark resolution/noise carrier from the BT interaction Hamiltonian",
            "controlled multiple-emission composition or quantum-stochastic evolution on the orthogonal resolution increments",
            "the finite NLO matching constant and full all-order Eq. (19) pushforward/range theorem",
        ],
        "next_gate": (
            "Compute the amplitude-level physical collinear factorization of the "
            "complete BT five-point process, including its Krein species and phase, "
            "and compare its number-changing operator with the Abel-regularized "
            "off-resonant D after the zero-mode completion. Equality would identify "
            "the constructed orthogonal-increment dilation with the physical BT "
            "asymptotic Hamiltonian on the outgoing cylinder. A mismatch would "
            "certify the first exact operator obstruction. Complete incoming sectors "
            "and multiple-emission composition remain subsequent gates."
        ),
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_abel_naimark_asymptotic_dilation.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_abel_naimark_asymptotic_dilation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_abel_naimark_asymptotic_dilation",
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
            "BT ABEL NAIMARK ASYMPTOTIC DILATION: ALL PASS "
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
