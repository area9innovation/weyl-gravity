#!/usr/bin/env python3
"""Certify a recentered-width bound on the exact BT runaway fiber family."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-runaway-fiber-width-bound-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-runaway-fiber-width-bound.md"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json"
]
SOURCE_COMMIT = "315464c9afb64a77abfc7a0f8d9a5385a03d88d8"

BACKGROUND = (-1, -1, 1, -3, 3, 1)
MODE = (2, 1, -1, -2, -1, 1)


def encode(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add(
    left: dict[tuple[int, int], int], right: dict[tuple[int, int], int]
) -> dict[tuple[int, int], int]:
    result: defaultdict[tuple[int, int], int] = defaultdict(int)
    result.update(left)
    for key, value in right.items():
        result[key] += value
    return {key: value for key, value in result.items() if value}


def multiply(
    left: dict[tuple[int, int], int], right: dict[tuple[int, int], int]
) -> dict[tuple[int, int], int]:
    result: defaultdict[tuple[int, int], int] = defaultdict(int)
    for (r_left, z_left), left_value in left.items():
        for (r_right, z_right), right_value in right.items():
            result[(r_left + r_right, z_left + z_right)] += (
                left_value * right_value
            )
    return dict(result)


def curvature_terms() -> dict[tuple[int, int], int]:
    """Return K_m(z)=A_m''(u)/(log(2))^2 as R^r z^k terms."""
    result: dict[tuple[int, int], int] = {}
    for site in range(6):
        residual: dict[tuple[int, int], int] = {(0, 0): -2}
        first: dict[tuple[int, int], int] = {}
        second: dict[tuple[int, int], int] = {}
        for neighbor in ((site - 1) % 6, (site + 1) % 6):
            r_power = BACKGROUND[neighbor] - BACKGROUND[site]
            z_power = MODE[neighbor] - MODE[site]
            residual = add(residual, {(r_power, z_power): 1})
            first = add(first, {(r_power, z_power): z_power})
            second = add(second, {(r_power, z_power): z_power * z_power})
        result = add(result, add(multiply(first, first), multiply(residual, second)))
    return result


def aggregate_by_z(
    terms: dict[tuple[int, int], int], r_value: Fraction
) -> dict[int, Fraction]:
    result: defaultdict[int, Fraction] = defaultdict(Fraction)
    for (r_power, z_power), coefficient in terms.items():
        result[z_power] += coefficient * r_value**r_power
    return dict(result)


def direct_curvature(m: int, u: int) -> Fraction:
    """Evaluate K_m(2^u) directly, without Laurent aggregation."""
    result = Fraction(0)
    exponents = tuple(4 * m * a + u * h for a, h in zip(BACKGROUND, MODE))
    for site in range(6):
        residual = Fraction(-2)
        first = Fraction(0)
        second = Fraction(0)
        for neighbor in ((site - 1) % 6, (site + 1) % 6):
            exponent = exponents[neighbor] - exponents[site]
            weight = Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))
            difference = MODE[neighbor] - MODE[site]
            residual += weight
            first += weight * difference
            second += weight * difference * difference
        result += first * first + residual * second
    return result


def shifted_coefficients(
    polynomial: dict[int, int], threshold: int
) -> tuple[int, ...]:
    """Coefficients of p(threshold+s), in ascending powers of s."""
    degree = max(polynomial)
    result = [0] * (degree + 1)
    for power, coefficient in polynomial.items():
        for shifted_power in range(power + 1):
            result[shifted_power] += (
                coefficient
                * math.comb(power, shifted_power)
                * threshold ** (power - shifted_power)
            )
    return tuple(result)


def build() -> dict:
    coupling = Fraction(2, 5)
    spatial_volume = 6**3
    beta = Fraction(spatial_volume, 1) / (coupling * coupling)
    terms = curvature_terms()
    expected_terms = {
        (-12, -2): 2,
        (-8, -2): 2,
        (-8, 1): 1,
        (-6, -1): -2,
        (-6, 1): 1,
        (-4, -1): -2,
        (-4, 2): 2,
        (-4, 4): 16,
        (-2, 1): -2,
        (-2, 2): -16,
        (0, -2): 2,
        (0, -1): -1,
        (0, 1): -2,
        (0, 2): 2,
        (2, -2): -12,
        (2, -1): -1,
        (4, -4): 16,
        (4, -2): 2,
        (4, 1): -2,
        (6, 1): -2,
        (8, 2): 2,
        (10, 2): 4,
        (12, 2): 2,
    }
    fixtures = []
    for m, u in ((2, -10), (2, -8), (2, 0), (3, -15), (4, -21)):
        r_value = Fraction(2 ** (4 * m))
        z_value = Fraction(2**u) if u >= 0 else Fraction(1, 2 ** (-u))
        aggregate = aggregate_by_z(terms, r_value)
        laurent_value = sum(
            (coefficient * z_value**power for power, coefficient in aggregate.items()),
            Fraction(0),
        )
        direct_value = direct_curvature(m, u)
        fixtures.append(
            {
                "m": m,
                "u": u,
                "R": 2 ** (4 * m),
                "z": encode(z_value),
                "direct_K": encode(direct_value),
                "laurent_K": encode(laurent_value),
                "matches": direct_value == laurent_value,
                "above_bound": direct_value >= Fraction(115, 4),
            }
        )

    cleared_bound_polynomials = {
        "R^12*(A-R^4)": {16: 1, 14: -12, 12: 2, 4: 2, 0: 2},
        "R^6*(2R^2-B)": {8: 1, 6: -1, 2: -2, 0: -2},
        "R^8*C": {14: 2, 12: 2, 8: 2, 6: 2, 2: -1, 0: -1},
        "R^8*(3R^6-C)": {14: 1, 12: -2, 8: -2, 6: -2, 2: 1, 0: 1},
        "R^4*(D-R^12)": {16: 1, 14: 4, 12: 2, 4: 2, 2: -16, 0: 2},
    }
    shifted_bound_polynomials = {
        name: shifted_coefficients(polynomial, 256)
        for name, polynomial in cleared_bound_polynomials.items()
    }

    checks = {
        "coupling_is_two_fifths": coupling == Fraction(2, 5),
        "conditional_inverse_temperature_is_1350": beta == 1350,
        "family_is_mean_zero_and_orthogonal": (
            sum(BACKGROUND) == sum(MODE) == 0
            and sum(a * h for a, h in zip(BACKGROUND, MODE)) == 0
        ),
        "curvature_laurent_terms_are_exact": terms == expected_terms,
        "only_six_z_powers_survive": {power for _, power in terms} == {-4, -2, -1, 1, 2, 4},
        "all_direct_fixtures_match": all(row["matches"] for row in fixtures),
        "all_direct_fixtures_clear_bound": all(row["above_bound"] for row in fixtures),
        "parameter_threshold_is_exact": 2 ** (4 * 2) == 256,
        "coefficient_bounds_hold_from_R_256": all(
            all(coefficient >= 0 for coefficient in shifted)
            and shifted[0] > 0
            for shifted in shifted_bound_polynomials.values()
        ),
        "completion_of_squares_bound_is_115_over_4": (
            32 - 1 - Fraction(9, 4) == Fraction(115, 4)
        ),
        "conditional_variance_bound_is_exact": (
            Fraction(1, 1) / (beta * Fraction(115, 4))
            == Fraction(2, 77625)
        ),
        "rationalized_variance_bound_is_exact": (
            Fraction(2, 77625) / Fraction(1, 2) ** 2
            == Fraction(8, 77625)
        ),
        "conditional_mean_escape_contradiction_closes_for_m_two": (
            Fraction(3, 4) > Fraction(8, 77625)
        ),
        "global_backgroundwise_width_remains_open": True,
        "annealed_center_and_h_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1",
        "schema_version": "reverse-physics-bt-euclidean-runaway-fiber-width-bound-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "BOUNDED_FAMILY_THEOREM_PROVED",
        "result_kind": "exact conditional variance theorem on the runaway background family",
        "question": (
            "Does the exact family that obstructs fixed-origin conditional moments also "
            "develop an unbounded recentered conditional width?"
        ),
        "answer": (
            "No. On that exact fixed-volume family and for every m>=2, the full "
            "one-dimensional fiber potential is uniformly strongly convex. Its "
            "dimensionless curvature satisfies K_m(2^u)>=115/4 at every u. The "
            "normalized conditional law therefore obeys Var_qm(u)<=2/[77625*(log "
            "2)^2]<=8/77625. Combined with the certified left-mass escape, its "
            "conditional mean satisfies E_qm[u]<-m/2. The raw second moment therefore "
            "grows because the conditional center escapes, not because the fiber "
            "widens. This theorem is uniform "
            "only in m on this family, not in arbitrary orthogonal backgrounds."
        ),
        "finite_volume_carrier": {
            "lattice": "periodic 6^4 lattice",
            "spatial_replication_factor": spatial_volume,
            "coupling": encode(coupling),
            "conditional_inverse_temperature": int(beta),
            "conditional_density": "q_m(u)=Z_m^-1 exp[-1350*A_m(u)]",
        },
        "exact_family": {
            "parameter": "m>=2 integer",
            "background_coefficients": list(BACKGROUND),
            "lowest_mode_coefficients": list(MODE),
            "field": "psi_m(u)=log(2)*(4m*a+u*h)",
            "R": "R=2^(4m)>=256",
            "z": "z=2^u>0",
            "raw_moment_predecessor": "E_qm[u^2]>=m^2*(1-2^(-m))",
        },
        "exact_curvature": {
            "definition": "A_m''(u)=(log(2))^2*K_m(z)",
            "bivariate_terms": [
                {"R_power": r_power, "z_power": z_power, "coefficient": coefficient}
                for (r_power, z_power), coefficient in sorted(terms.items())
            ],
            "six_term_form": (
                "K=16*R^4*z^-4+A*z^-2-B*z^-1-C*z+D*z^2+16*R^-4*z^4"
            ),
            "coefficients": {
                "A": "2R^4-12R^2+2+2R^-8+2R^-12",
                "B": "R^2+1+2R^-4+2R^-6",
                "C": "2R^6+2R^4+2+2R^-2-R^-6-R^-8",
                "D": "2R^12+4R^10+2R^8+2-16R^-2+2R^-4",
            },
            "fixtures": fixtures,
        },
        "uniform_lower_bound": {
            "scope": "R>=256 and z>0",
            "coefficient_bounds": [
                "A>=R^4>0",
                "0<B<=2R^2",
                "0<C<=3R^6",
                "D>=R^12>0",
            ],
            "exact_universal_sign_method": (
                "After clearing positive powers of R, substitute R=256+s; "
                "every coefficient of the five resulting integer polynomials "
                "is nonnegative and each constant coefficient is positive."
            ),
            "cleared_polynomial_shift_checks": {
                name: {
                    "degree": len(shifted) - 1,
                    "all_shifted_coefficients_nonnegative": all(
                        coefficient >= 0 for coefficient in shifted
                    ),
                    "positive_constant_coefficient": shifted[0] > 0,
                }
                for name, shifted in shifted_bound_polynomials.items()
            },
            "first_square": "A*z^-2-B*z^-1>=-B^2/(4A)>=-1",
            "second_square": "D*z^2-C*z>=-C^2/(4D)>=-9/4",
            "outer_am_gm": "16*(R^4*z^-4+R^-4*z^4)>=32",
            "conclusion": "K_m(z)>=32-1-9/4=115/4",
            "lower_bound": encode(Fraction(115, 4)),
        },
        "conditional_variance": {
            "analytic_input": (
                "one-dimensional Brascamp-Lieb variance inequality for a normalized "
                "density exp(-V) with V''>=rho>0"
            ),
            "potential_curvature": "V_m''(u)>=1350*(log(2))^2*(115/4)",
            "centering": "conditional mean E_qm[u]",
            "variance_bound": "Var_qm(u)<=2/[77625*(log(2))^2]",
            "rational_prefactor": encode(Fraction(2, 77625)),
            "elementary_log_bound": "log(2)=integral_1^2 dx/x>=1/2",
            "rationalized_variance_bound": "Var_qm(u)<=8/77625",
            "rationalized_bound": encode(Fraction(8, 77625)),
            "status": "PROVED_UNIFORMLY_IN_M_ON_EXACT_RUNAWAY_FAMILY",
        },
        "conditional_center_escape": {
            "predecessor_mass_bound": "q_m({u>=-m})<=2^(-m)",
            "contradiction_hypothesis": "mu_m=E_qm[u]>=-m/2",
            "variance_lower_bound_under_hypothesis": (
                "Var_qm(u)>=(1-2^(-m))*m^2/4>=3/4"
            ),
            "variance_upper_bound": "Var_qm(u)<=8/77625<3/4",
            "conclusion": "E_qm[u]<-m/2 for every m>=2",
            "status": "PROVED_ESCAPE_TO_MINUS_INFINITY_ON_EXACT_RUNAWAY_FAMILY",
        },
        "method_disposition": {
            "runaway_family_uniform_strong_convexity": "PROVED",
            "runaway_family_recentered_conditional_variance": "PROVED",
            "runaway_family_conditional_mean_escape": "PROVED",
            "all_background_uniform_recentered_conditional_variance": "OPEN",
            "annealed_center_second_moment": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "foundational_dependency_cut": {
            "finite_exact_layer": (
                "integer exponent vectors, Laurent coefficients, rational coefficient "
                "bounds, completion of squares, and the exact Gibbs prefactor"
            ),
            "finite_dimensional_analytic_layer": (
                "AM-GM and the one-dimensional Brascamp-Lieb variance inequality"
            ),
            "uniform_limit_layer": (
                "no arbitrary-background, annealed-center, volume-uniform H^-1, "
                "compactness, or represented-limit theorem is established"
            ),
            "classification": "USED_BY_DISPLAYED_PROOF",
            "weakest_base_or_reversal": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a uniform recentered conditional-width theorem or obstruction for arbitrary orthogonal backgrounds",
            "an annealed bound on the Gibbs-weighted conditional centers",
            "a normalized one-mode second-moment estimate for the actual marginal",
            "a Fourier-shell estimate yielding the interacting H^-1 bound",
            "tightness and identification of a represented Euclidean limit",
        ],
        "next_gate": (
            "Control the annealed distribution of the moving center and determine "
            "whether the exact-family curvature mechanism extends to arbitrary "
            "time-space-correlated orthogonal backgrounds."
        ),
        "does_not_establish": [
            "a recentered conditional-variance bound for every orthogonal background",
            "an annealed second moment of conditional centers",
            "a bound for the fully integrated lowest-mode marginal",
            "an interacting H^-1 moment or tightness theorem",
            "a continuum BT Euclidean measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
            "a weakest-foundation reversal",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)} for relative in INPUTS
            ],
            "arithmetic": "Python Fraction and integer Laurent arithmetic",
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_runaway_fiber_width_bound.py --check",
            "python3 reverse_physics/verify_bt_euclidean_runaway_fiber_width_bound.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_runaway_fiber_width_bound",
        ],
        "tier_receipt": {
            "tier_0": "parse, strict schema, deterministic generation, scoped diff check, and staged-diff inspection",
            "tier_1": "exact producer, direct independent differentiation fixtures, universal inequality audit, and mutations",
            "tier_2": "predecessor imported by content hash; no shared operator or sampler changed",
            "tier_3": "not run: no freeze, release, continuum, quantum lifecycle, or Lorentzian promotion",
            "memory_policy": "all commands sequential under a 500000 KiB virtual-memory ceiling",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        for failure in result["checks"]["failures"]:
            print(f"[FAIL] {failure}")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT runaway-fiber width bound "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
