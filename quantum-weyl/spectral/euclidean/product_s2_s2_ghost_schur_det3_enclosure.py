#!/usr/bin/env python3
"""Enclose the regular-complement Schur det_3 sum on S2(1) x S2(2)."""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-det3-enclosure-v1.schema.json"
DEPENDENCIES = {
    "product_spectrum": HERE
    / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json",
}

CUTOFF = 2400
LARGE_K_THRESHOLD = Fraction(1, 100)
LARGE_TAYLOR_ORDER = 100
SMALL_TAYLOR_ORDER = 8
ROUNDING_CUSHION = Fraction(1, 10_000_000_000)
LARGE_MODE_LAMBDA_BOUND = 137
BINARY64_UNIT_ROUNDOFF = Fraction(1, 2**53)
TERM_RELATIVE_ERROR_BOUND = Fraction(1, 10**12)
SMALL_EXACT_SUM_ENVELOPE = Fraction(1, 500)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction | int) -> dict[str, int]:
    rational = Fraction(value)
    return {"numerator": rational.numerator, "denominator": rational.denominator}


def _decimal(value: Fraction, digits: int = 70) -> Decimal:
    with localcontext() as context:
        context.prec = digits
        return Decimal(value.numerator) / Decimal(value.denominator)


def _k_fraction(ell: int, emm: int) -> Fraction:
    """Positive K=s_lm-1 on the regular S2(1) x S2(2) complement."""

    if (ell, emm) in {(0, 0), (1, 0), (0, 1)}:
        raise ValueError("K is absent or singular on the exceptional mode")
    a = ell * (ell + 1)
    b = 2 * emm * (emm + 1)
    lam = a + b
    value = Fraction(0)
    if ell:
        value += Fraction(2 * a, lam * (lam - 2))
    if emm:
        value += Fraction(4 * b, lam * (lam - 4))
    return value / 3


def _large_mode_interval() -> tuple[Fraction, Fraction, list[tuple[int, int]], str, str]:
    lower = Fraction(0)
    upper = Fraction(0)
    modes: list[tuple[int, int]] = []
    # K<=4/[3(lambda-4)] implies K>1/100 only if lambda<=137.
    # Search that finite ellipse exactly instead of scanning the full cutoff
    # rectangle with Fraction arithmetic.
    for ell in range(CUTOFF + 1):
        a = ell * (ell + 1)
        if a > LARGE_MODE_LAMBDA_BOUND:
            break
        for emm in range(CUTOFF + 1):
            b = 2 * emm * (emm + 1)
            if a + b > LARGE_MODE_LAMBDA_BOUND:
                break
            if (ell, emm) in {(0, 0), (1, 0), (0, 1)}:
                continue
            k_value = _k_fraction(ell, emm)
            if k_value <= LARGE_K_THRESHOLD:
                continue
            modes.append((ell, emm))
            degeneracy = (2 * ell + 1) * (2 * emm + 1)
            partial = sum(
                (
                    (Fraction(1) if order % 2 else Fraction(-1))
                    * k_value**order
                    / order
                    for order in range(3, LARGE_TAYLOR_ORDER + 1)
                ),
                Fraction(0),
            )
            lower += degeneracy * partial
            upper += degeneracy * (
                partial + k_value ** (LARGE_TAYLOR_ORDER + 1) / (LARGE_TAYLOR_ORDER + 1)
            )
    lower_text = f"{lower.numerator}/{lower.denominator}"
    upper_text = f"{upper.numerator}/{upper.denominator}"
    return (
        lower,
        upper,
        modes,
        hashlib.sha256(lower_text.encode()).hexdigest(),
        hashlib.sha256(upper_text.encode()).hexdigest(),
    )


def _small_mode_binary64_partial() -> tuple[float, int]:
    """Ordinary positive sum of the even Taylor lower bound on K<=1/100."""

    total = 0.0
    count = 0
    threshold = float(LARGE_K_THRESHOLD)
    for ell in range(CUTOFF + 1):
        a = ell * (ell + 1)
        for emm in range(CUTOFF + 1):
            if (ell, emm) in {(0, 0), (1, 0), (0, 1)}:
                continue
            b = 2 * emm * (emm + 1)
            lam = a + b
            k_value = 0.0
            if ell:
                k_value += 2.0 * a / (lam * (lam - 2))
            if emm:
                k_value += 4.0 * b / (lam * (lam - 4))
            k_value /= 3.0
            if k_value > threshold:
                continue
            power = k_value * k_value * k_value
            partial = power / 3.0
            for order in range(4, SMALL_TAYLOR_ORDER + 1):
                power *= k_value
                partial += (1.0 if order % 2 else -1.0) * power / order
            term = (2 * ell + 1) * (2 * emm + 1) * partial
            total += term
            count += 1
    return total, count


def _gamma(operation_count: int) -> Fraction:
    product = operation_count * BINARY64_UNIT_ROUNDOFF
    return product / (1 - product)


def _binary64_rounding_bound(count: int, observed_sum: float) -> tuple[Fraction, dict[str, Any]]:
    """Derive a conservative absolute bound for the finite binary64 sum."""

    summation_gamma = _gamma(count)
    term_gamma = _gamma(40)
    polynomial_condition_bound = Fraction(51, 50)
    # Every integer entering K is below 2^53, every arithmetic result is
    # normal, the two K summands are positive, and on K<=1/100 the absolute
    # coefficient sum divided by P_8(K) is below 51/50. Forty rounded
    # operations therefore give a much smaller relative error than 10^-12.
    assert term_gamma * polynomial_condition_bound < TERM_RELATIVE_ERROR_BOUND
    observed = Fraction.from_float(observed_sum)
    assert observed < (
        SMALL_EXACT_SUM_ENVELOPE
        * (1 - summation_gamma)
        * (1 - TERM_RELATIVE_ERROR_BOUND)
    )
    absolute_bound = SMALL_EXACT_SUM_ENVELOPE * (
        summation_gamma * (1 + TERM_RELATIVE_ERROR_BOUND)
        + TERM_RELATIVE_ERROR_BOUND
    )
    assert absolute_bound < ROUNDING_CUSHION
    return absolute_bound, {
        "binary64_unit_roundoff": _q(BINARY64_UNIT_ROUNDOFF),
        "ordinary_positive_addition_count": count,
        "summation_gamma_bound": _q(summation_gamma),
        "per_term_operation_count_upper": 40,
        "per_term_gamma_bound": _q(term_gamma),
        "alternating_polynomial_condition_upper": _q(polynomial_condition_bound),
        "per_term_relative_error_bound": _q(TERM_RELATIVE_ERROR_BOUND),
        "exact_small_sum_envelope": _q(SMALL_EXACT_SUM_ENVELOPE),
        "derived_absolute_rounding_bound": _q(absolute_bound),
        "declared_cushion": _q(ROUNDING_CUSHION),
        "proof": "positive ordinary summation gives gamma_N; exact integer inputs are below 2^53; no K cancellation occurs; P8 conditioning is below 51/50; the observed rounded sum proves the exact sum is below 1/500",
    }


def _small_taylor_error_bound() -> Fraction:
    # On K<=1/100, K^9 <= 10^-12 K^3.  The global K^3 sum is bounded by
    # 64/(27 c^3) times the product-lattice comparison sum, with c=8/27.
    global_k3_bound = Fraction(14_145, 8)
    return Fraction(1, 100) ** 6 * global_k3_bound / 9


def _rectangular_tail_bound() -> Fraction:
    # For x=l+1/2, y=m+1/2 and q=x^2+2y^2,
    # K <= 4/[3(lambda-4)] and lambda-4 >= c q outside the rectangle.
    x0 = Fraction(2 * CUTOFF + 3, 2)
    sum_x3 = x0**-3 + Fraction(1, 2) * x0**-2
    sum_x4 = x0**-4 + Fraction(1, 3) * x0**-3
    first_factor_tail = Fraction(1, 2) * sum_x3 + Fraction(125, 162) * sum_x4
    second_factor_tail = Fraction(1, 4) * sum_x3 + Fraction(125, 432) * sum_x4
    q_min = x0 * x0 + Fraction(1, 2)
    comparison = 1 - Fraction(19, 4) / q_min
    return Fraction(64, 81) * (first_factor_tail + second_factor_tail) / comparison**3


def _enclosure() -> dict[str, Any]:
    large_lower, large_upper, large_modes, lower_hash, upper_hash = _large_mode_interval()
    small_partial, small_count = _small_mode_binary64_partial()
    small_decimal = Decimal.from_float(small_partial)
    _, rounding_proof = _binary64_rounding_bound(small_count, small_partial)
    tail = _rectangular_tail_bound()
    taylor_error = _small_taylor_error_bound()
    with localcontext() as context:
        context.prec = 70
        lower = _decimal(large_lower) + small_decimal - _decimal(ROUNDING_CUSHION)
        upper = (
            _decimal(large_upper)
            + small_decimal
            + _decimal(ROUNDING_CUSHION)
            + _decimal(taylor_error)
            + _decimal(tail)
        )
    lower_text = format(lower, "f")
    upper_text = format(upper, "f")
    common = []
    for left, right in zip(lower_text, upper_text):
        if left != right:
            break
        common.append(left)
    return {
        "definition": "log det_3(I+K)=sum_regular d_lm[log(1+K_lm)-K_lm+K_lm^2/2]",
        "rectangular_cutoff": CUTOFF,
        "regular_mode_domain": "all ell,m>=0 except (0,0),(1,0),(0,1)",
        "large_K_threshold": _q(LARGE_K_THRESHOLD),
        "large_mode_search_proof": "K>1/100 and K<=4/[3(lambda-4)] imply lambda<=137",
        "large_mode_count": len(large_modes),
        "large_modes": [[ell, emm] for ell, emm in large_modes],
        "large_mode_exact_taylor_order": LARGE_TAYLOR_ORDER,
        "large_mode_lower_fraction_sha256": lower_hash,
        "large_mode_upper_fraction_sha256": upper_hash,
        "large_mode_lower_decimal": format(_decimal(large_lower), "f"),
        "large_mode_upper_decimal": format(_decimal(large_upper), "f"),
        "small_mode_count": small_count,
        "small_mode_even_taylor_order": SMALL_TAYLOR_ORDER,
        "small_mode_binary64_lower_sum": format(small_decimal, "f"),
        "binary64_rounding_cushion": _q(ROUNDING_CUSHION),
        "binary64_rounding_proof": rounding_proof,
        "small_mode_taylor_error_bound": _q(taylor_error),
        "rectangular_infinite_tail_bound": _q(tail),
        "lower_endpoint_decimal": lower_text,
        "upper_endpoint_decimal": upper_text,
        "interval_width_decimal": format(upper - lower, "f"),
        "certified_common_decimal_prefix": "".join(common).rstrip("."),
        "exceptional_correction_not_in_det3": "3^-6=1/729; retained for the later coupled vector-Schur determinant",
    }


def build() -> dict[str, Any]:
    spectrum = json.loads(DEPENDENCIES["product_spectrum"].read_text())
    if (
        spectrum.get("primed_mode_policy", {}).get("total_exceptional_correction")
        != "3^-6"
        or spectrum.get("claim_flags", {}).get("PRODUCT_SPECTRAL_MEASURE_SUPPLIED")
        is not True
    ):
        raise ValueError("product spectral dependency drifted")
    enclosure = _enclosure()
    if not enclosure["certified_common_decimal_prefix"].startswith("0.3263039"):
        raise AssertionError("product det3 enclosure drifted")
    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-schur-det3-enclosure-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE",
        "result_state": "PRODUCT_S2_S2_REGULAR_SCHUR_DET3_RIGOROUSLY_ENCLOSED",
        "lifecycle_state": "BACKGROUND_SPECIFIC_DET3_COMPUTED_WEIGHTED_FINITE_ROWS_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": spectrum["classical_commit"],
        "scope": {
            "background": "S2(1) x S2(2)",
            "operator": "regular-complement normalized longitudinal scalar Schur factor I+K",
            "mode_policy": "constant absent; six matched vector-zero/Schur-pole modes excluded from det3 and retained as coupled correction 3^-6",
            "regularization": "canonical third modified Fredholm determinant on the regular complement",
        },
        "det3_enclosure": enclosure,
        "tail_proof": {
            "coordinates": "x=ell+1/2, y=m+1/2, q=x^2+2y^2, lambda-4=q-19/4",
            "K_bound": "0<K<=4/[3(lambda-4)] on the regular complement",
            "log_bound": "0<log(1+K)-K+K^2/2<=K^3/3",
            "first_tail_slice": "sum_m 4xy/q^3 <= 1/(2x^3)+125/(162x^4)",
            "second_tail_slice": "sum_l 4xy/q^3 <= 1/(4y^3)+125/(432y^4)",
            "union_policy": "sum the two tail slices; the doubly-exterior corner may be overcounted",
        },
        "claim_flags": {
            "PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED": True,
            "MATCHED_EXCEPTIONAL_CORRECTION_RETAINED": True,
            "PRODUCT_WEIGHTED_R_K_COMPUTED": False,
            "PRODUCT_FINITE_PART_R_K2_COMPUTED": False,
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED": False,
            "GENERIC_BACKGROUND_SCHUR_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "ANALYTICALLY_CONTINUE_PRODUCT_WEIGHTED_R_K_AND_FINITE_PART_R_K2_THEN_COMBINE_WITH_MINIMAL_VECTOR_AND_REMAINING_BV_SECTORS",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate rigorously encloses the canonical det_3 value of the normalized scalar Schur factor on the regular complement of S2(1) x S2(2). It retains, but does not fold into det_3, the separate coupled exceptional correction 3^-6. The finite rectangle uses exact rational alternating bounds for every K>1/100 mode, an even Taylor lower sum with explicit truncation and binary64 cushions for the remaining modes, and an analytic rational double-tail bound. It does not compute weighted R(K), the finite part of R(K^2), the minimal-vector determinant, the full coupled ghost determinant, arbitrary-background form factors, remaining BV sectors, Gamma1/Q1, a Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED",
        "MATCHED_EXCEPTIONAL_CORRECTION_RETAINED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")


def emit(*, check: bool) -> None:
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale product det3 enclosure: {OUTPUT}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit(check=False)
    if args.check:
        emit(check=True)
    if not args.emit and not args.check:
        print(json.dumps(build(), indent=2, sort_keys=True))
    print("PRODUCT S2xS2 GHOST SCHUR DET3: RIGOROUS ENCLOSURE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
