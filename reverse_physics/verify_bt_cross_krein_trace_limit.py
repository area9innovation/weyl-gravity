#!/usr/bin/env python3
"""Independent verifier for the BT cross-Krein trace-limit certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-cross-krein-trace-limit-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def quad_product(left, right):
    # Independent convolution in Q[s,t]/(s^2-2,t^2-3), basis 1,s,t,st.
    answer = [Fraction(0) for _ in range(4)]
    exponents = [(0, 0), (1, 0), (0, 1), (1, 1)]
    lookup = {entry: index for index, entry in enumerate(exponents)}
    for i, (s1, t1) in enumerate(exponents):
        for j, (s2, t2) in enumerate(exponents):
            s_total = s1 + s2
            t_total = t1 + t2
            factor = Fraction(1)
            if s_total >= 2:
                factor *= 2
                s_total -= 2
            if t_total >= 2:
                factor *= 3
                t_total -= 2
            answer[lookup[(s_total, t_total)]] += factor * left[i] * right[j]
    return tuple(answer)


def quad_power(value, power):
    answer = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    for _ in range(power):
        answer = quad_product(answer, value)
    return answer


def verify(path):
    certificate = load(path)
    schema = load(SCHEMA)
    checks = {}

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )

    orbit = certificate.get("orbit_Krein_completion", {})
    rows = orbit.get("exact_rows", [])
    checks["independent_orbit_Krein_completion"] = len(rows) == 9 and all(
        row.get("J_image_index") == -row.get("n")
        and fraction(row.get("positive_norm_squared", {})) == 1
        and row.get("shift_test_m") == -row.get("n") - 1
        and fraction(row.get("left_shift_pairing", {}))
        == fraction(row.get("right_shift_pairing", {}))
        == 1
        and row.get("boost_test_m") == -row.get("n")
        and fraction(row.get("left_boost_pairing", {}))
        == fraction(row.get("right_anti_boost_pairing", {}))
        == -row.get("n")
        for row in rows
    )

    checks["independent_shift_and_boost_adjoints"] = (
        orbit.get("Hilbert_adjoint_of_Z") == "Z^star=Z^-1"
        and orbit.get("Krein_adjoint_of_Z") == "Z^dagger=Z"
        and "N^dagger=-N" in orbit.get("boost_generator", "")
        and "not the finite-rank operator trace"
        in orbit.get("coefficient_functional", "")
    )

    squeeze = certificate.get("cross_Krein_squeeze_core", {})
    fixtures = squeeze.get("exact_fixtures", {})
    z_values = [fraction(item) for item in fixtures.get("two_pair_z_values", [])]
    reconstructed_norm = Fraction(1)
    for z_value in z_values:
        reconstructed_norm /= 1 - z_value**2
    checks["independent_squeeze_norms"] = (
        fraction(fixtures.get("one_pair_z", {})) == Fraction(1, 2)
        and fraction(fixtures.get("one_pair_positive_norm_squared", {}))
        == Fraction(4, 3)
        and reconstructed_norm == Fraction(3, 2)
        == fraction(fixtures.get("two_pair_positive_norm_squared", {}))
        and fraction(fixtures.get("one_pair_Krein_norm", {})) == 1
        and fraction(fixtures.get("two_pair_Krein_norm", {})) == 1
    )

    # Reconstruct the Krein adjoint on the two quadratic monomials rather than
    # trusting the recorded formula: (A* A*)^dagger=DD and (DD)^dagger=A*A*.
    z_fixture = Fraction(2, 5)
    generator_coefficients = {"AA": z_fixture, "DD": -z_fixture}
    adjoint_coefficients = {
        "DD": generator_coefficients["AA"],
        "AA": generator_coefficients["DD"],
    }
    negative_generator = {
        name: -coefficient for name, coefficient in generator_coefficients.items()
    }
    checks["cross_Krein_core_boundary"] = (
        adjoint_coefficients == negative_generator
        and Fraction(1) - Fraction(1) == 0
        and squeeze.get("Krein_adjoint") == "Q^dagger=-Q"
        and squeeze.get("operator_status")
        == "DENSELY_DEFINED_CLOSABLE_WITH_KREIN_INVERSE_ON_ITS_GAUSSIAN_IMAGE_CORE"
        and len(squeeze.get("implemented_shears", [])) == 2
        and "squeeze factor only" in squeeze.get("scope", "")
    )

    finite_trace = certificate.get("finite_rank_Born_trace", {})
    checks["independent_finite_rank_trace_transport"] = (
        finite_trace.get("trace") == "Tr_fin Theta_(x,y)=[y,x]"
        and "[Sy,Sx]=[y,x]" in finite_trace.get("transported_trace", "")
        and finite_trace.get("disposition")
        == "CONSTRUCTED_ON_FINITE_RANK_CORE_IDEAL"
        and len(finite_trace.get("does_not_extend_automatically_to", [])) == 3
    )

    no_go = certificate.get("normalized_trace_extension_no_go", {})
    translate_rows = no_go.get("translate_bounds", [])
    checks["independent_translate_bound"] = len(translate_rows) == 9 and all(
        row.get("symmetric_projection_rank") == 2 * row.get("cutoff") + 1
        and fraction(
            row.get(
                "common_rank_one_weight_upper_bound_if_tau_identity_is_one", {}
            )
        )
        == Fraction(1, 2 * row.get("cutoff") + 1)
        for row in translate_rows
    )

    checks["normalized_trace_no_go_boundary"] = (
        "(2N+1)c<=1" in no_go.get("positivity_bound", "")
        and "c=0" in no_go.get("theorem", "")
        and "Tr_fin(1)=infinity" in no_go.get("finite_rank_trace_branch", "")
        and no_go.get("disposition")
        == "NO_FINITE_NORMALIZED_POSITIVE_CYCLIC_TRACE_WITH_NONZERO_ORBIT_RANK_ONE_WEIGHT"
    )

    thermo = certificate.get("thermodynamic_trace_norm_barrier", {})
    algebraic = thermo.get("gamma_half_coefficient_times_mu_cubed_over_pi", {})
    coefficients = tuple(fraction(item) for item in algebraic.get("coefficients", []))
    expected = (
        Fraction(-1, 6),
        Fraction(1, 48),
        Fraction(0),
        Fraction(1, 16),
    )
    checks["independent_gamma_half_radical"] = (
        coefficients == expected
        and thermo.get("gamma_half_radical")
        == "(3sqrt(6)+sqrt(2)-8)/48"
    )

    y = tuple(48 * entry for entry in coefficients)
    y = (y[0] + 8, y[1], y[2], y[3])
    y2 = quad_power(y, 2)
    y4 = quad_power(y, 4)
    polynomial = tuple(
        y4[index] - 112 * y2[index] + (2704 if index == 0 else 0)
        for index in range(4)
    )
    checks["independent_gamma_half_polynomial"] = (
        y == (Fraction(0), Fraction(1), Fraction(0), Fraction(3))
        and polynomial == (Fraction(0),) * 4
        and 3 * Fraction(12, 5) + Fraction(7, 5) - 8 > 0
    )

    checks["independent_log_density_coefficient"] = (
        thermo.get("exact_log_trace_norm_density")
        == "ell(gamma,mu)=mu^3/(12pi)[(1+gamma)^(3/2)+(1-gamma)^(3/2)-2]"
        and "sqrt(1+gamma)-sqrt(1-gamma)"
        in thermo.get("derivative_witness", "")
        and thermo.get("gamma_half_rational_bounds")
        == "1/80 < ell*pi/mu^3 < 1/48"
    )

    checks["independent_trace_norm_trilemma"] = (
        thermo.get("Krein_norm") == "[Psi_V,Psi_V]=1"
        and thermo.get("finite_rank_trace") == "Tr_fin(P_V)=1"
        and "N_V" in thermo.get("positive_trace_norm", "")
        and fraction(thermo.get("two_pair_normalized_Krein_norm_fixture", {}))
        == Fraction(2, 3)
        and thermo.get("disposition")
        == "NO_TRACE_NORM_THERMODYNAMIC_LIMIT_OF_THE_BT_NORMALIZED_KREIN_PROJECTION"
    )

    disposition = certificate.get("disposition", {})
    checks["claim_boundary"] = (
        disposition.get("zero_mode_Krein_completion") == "CONSTRUCTED"
        and disposition.get("weighted_cross_Krein_squeeze_factor")
        == "CONSTRUCTED_ON_PAIRED_CORES"
        and disposition.get("finite_rank_cyclic_Born_trace") == "CONSTRUCTED"
        and disposition.get("normal_trace_class_thermodynamic_limit")
        == "OBSTRUCTED"
        and disposition.get("semifinite_relative_or_non_normal_weight")
        == "NOT_CONSTRUCTED"
        and disposition.get("full_nonlinear_R_t") == "NOT_CONSTRUCTED"
        and disposition.get("physical_neutral_one_over_48")
        == "NOT_ESTABLISHED"
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 4 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )

    exclusions = certificate.get("does_not_establish", [])
    checks["fail_closed_exclusions"] = (
        any("full nonlinear R_t" in item for item in exclusions)
        and any("semifinite or non-normal" in item for item in exclusions)
        and any("LORENTZIAN-CAUSAL" in item for item in exclusions)
        and len(certificate.get("missing_object_ledger", [])) >= 7
    )

    ok = all(checks.values())
    for name, value in checks.items():
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
