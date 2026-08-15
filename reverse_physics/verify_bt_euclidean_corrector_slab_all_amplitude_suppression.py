#!/usr/bin/env python3
"""Independent verifier for BT all-large-amplitude slab suppression."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_ALL_AMPLITUDE_SUPPRESSION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-all-amplitude-suppression-v1.schema.json")
ZERO = (0, 0, 0, 0, 0)
MATRIX = {
    time: ((0, 0, 1, -1) if time == 1 else (0, 1, 0, -1) if time == 2 else (0, 0, 0, 0))
    for time in range(-1, 5)
}
VARIABLES = (
    ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0)),
    ((0, -1, 0, 0, 0), (0, 0, 1, 0, 0)),
    ((0, 0, -1, 0, 0), (0, 0, 0, 1, 0)),
    ((0, 0, 0, -1, 0), (0, 0, 0, 0, 1)),
)
EDGE = (Fraction(199, 200), Fraction(200, 199))
ANCHOR = Fraction(8)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def digest(relative: str) -> str:
    result = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# Numeric interval rail for the four finite second-octave bins.
def nproduct(left, right):
    values = (left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1])
    return min(values), max(values)


def nappend(polynomial, exponent, interval):
    old = polynomial.get(exponent, (Fraction(0), Fraction(0)))
    polynomial[exponent] = old[0] + interval[0], old[1] + interval[1]


def npoly_product(left, right):
    result = {}
    for le, li in left.items():
        for re, ri in right.items():
            nappend(result, tuple(x + y for x, y in zip(le, re)), nproduct(li, ri))
    return result


def nfactor(low, high, exponent):
    values = [(base**exponent if exponent >= 0 else Fraction(1) / base ** (-exponent)) - 1 for base in (low, high)]
    return min(values), max(values)


def numeric_translation(low: Fraction, high: Fraction) -> dict:
    result = {}
    for time, (left, right) in enumerate(VARIABLES):
        for space in range(4):
            residual = {ZERO: (Fraction(-8), Fraction(-8))}
            for exponent in (left, right, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO):
                nappend(residual, exponent, EDGE)
            delta = {}
            here = MATRIX[time][space]
            for other_time, other_space, exponent in (
                (time - 1, space, left),
                (time + 1, space, right),
                (time, (space - 1) % 4, ZERO),
                (time, (space + 1) % 4, ZERO),
            ):
                factor = nfactor(low, high, MATRIX[other_time][other_space] - here)
                if factor != (Fraction(0), Fraction(0)):
                    nappend(delta, exponent, nproduct(EDGE, factor))
            doubled = {exponent: nproduct(bounds, (Fraction(2), Fraction(2))) for exponent, bounds in residual.items()}
            for contribution in (npoly_product(doubled, delta), npoly_product(delta, delta)):
                for exponent, bounds in contribution.items():
                    nappend(result, exponent, bounds)
    return result


def numeric_summary(index: int, low: Fraction, high: Fraction) -> dict:
    polynomial = numeric_translation(low, high)
    square = ((0, 2, 0, 0, 0), (0, 0, 0, -2, 0))
    linear = ((0, 1, 0, 0, 0), (0, 0, 0, -1, 0))
    special = {ZERO, *square, *linear}
    discarded = [bounds[0] for exponent, bounds in polynomial.items() if exponent not in special]
    require(all(value >= 0 for value in discarded), "finite-bin discarded sign failed")
    alpha = min(polynomial[exponent][0] for exponent in square)
    beta = max(Fraction(0), *(-polynomial[exponent][0] for exponent in linear))
    constant = polynomial[ZERO][0]
    gap = constant - beta**2 / (2 * alpha)
    require(alpha > 0 and gap > 0, "finite-bin completion failed")
    return {
        "index": index,
        "amplitude_low": enc(low),
        "amplitude_high": enc(high),
        "square_floor_alpha": enc(alpha),
        "negative_linear_magnitude_beta": enc(beta),
        "constant_floor": enc(constant),
        "residual_square_gap": enc(gap),
        "discarded_coefficient_count": len(discarded),
        "all_discarded_lower_coefficients_nonnegative": True,
    }


# Separate symbolic Laurent rail for every B>=8.
def qclean(polynomial):
    return {power: value for power, value in polynomial.items() if value}


def qadd(left, right):
    result = dict(left)
    for power, value in right.items():
        result[power] = result.get(power, Fraction(0)) + value
    return qclean(result)


def qscale(polynomial, coefficient):
    return qclean({power: Fraction(coefficient) * value for power, value in polynomial.items()})


def qmultiply(left, right):
    result = {}
    for lp, lv in left.items():
        for rp, rv in right.items():
            result[lp + rp] = result.get(lp + rp, Fraction(0)) + lv * rv
    return qclean(result)


def qvalue(polynomial, value=ANCHOR):
    return sum((coefficient * value**power for power, coefficient in polynomial.items()), Fraction(0))


def qshift(polynomial):
    minimum = min(polynomial, default=0)
    coefficients = {}
    for power, value in polynomial.items():
        degree = power - minimum
        for shifted in range(degree + 1):
            coefficients[shifted] = coefficients.get(shifted, Fraction(0)) + value * comb(degree, shifted) * ANCHOR ** (degree - shifted)
    return minimum, [coefficients.get(power, Fraction(0)) for power in range(max(coefficients, default=0) + 1)]


def qrecord(polynomial):
    base, shifted = qshift(polynomial)
    return {
        "laurent_terms": [{"power": power, "coefficient": enc(value)} for power, value in sorted(polynomial.items())],
        "shift_anchor": enc(ANCHOR),
        "clearing_power": -base,
        "shifted_coefficients": [enc(value) for value in shifted],
        "all_shifted_coefficients_nonnegative": all(value >= 0 for value in shifted),
    }


QBRANCHES = []


def qextreme(candidates, minimum, label):
    selected_index = (min if minimum else max)(range(len(candidates)), key=lambda index: qvalue(candidates[index]))
    selected = candidates[selected_index]
    differences = []
    for candidate in candidates:
        difference = qadd(candidate, qscale(selected, -1)) if minimum else qadd(selected, qscale(candidate, -1))
        record = qrecord(difference)
        require(record["all_shifted_coefficients_nonnegative"], f"symbolic branch failed: {label}")
        differences.append(record)
    QBRANCHES.append({
        "label": label,
        "extreme": "minimum" if minimum else "maximum",
        "selected_index": selected_index,
        "candidate_difference_records": differences,
    })
    return selected


def qiadd(left, right):
    return qadd(left[0], right[0]), qadd(left[1], right[1])


def qiscale(interval, coefficient):
    coefficient = Fraction(coefficient)
    return (qscale(interval[0], coefficient), qscale(interval[1], coefficient)) if coefficient >= 0 else (qscale(interval[1], coefficient), qscale(interval[0], coefficient))


def qimultiply(left, right, label):
    candidates = [qmultiply(left[0], right[0]), qmultiply(left[0], right[1]), qmultiply(left[1], right[0]), qmultiply(left[1], right[1])]
    return qextreme(candidates, True, label + ":lower"), qextreme(candidates, False, label + ":upper")


def qconstant(low, high=None):
    low = Fraction(low)
    high = low if high is None else Fraction(high)
    return {0: low}, {0: high}


def qfactor(exponent, inverse):
    effective = -exponent if inverse else exponent
    if effective == 0:
        return qconstant(0)
    if effective > 0:
        return ({effective: Fraction(1), 0: Fraction(-1)}, {effective: Fraction(2**effective), 0: Fraction(-1)})
    return ({effective: Fraction(1, 2 ** (-effective)), 0: Fraction(-1)}, {effective: Fraction(1), 0: Fraction(-1)})


def qpadd(polynomial, exponent, interval):
    polynomial[exponent] = qiadd(polynomial.get(exponent, qconstant(0)), interval)


def qpoly_product(left, right, label):
    result = {}
    for le, li in left.items():
        for re, ri in right.items():
            exponent = tuple(x + y for x, y in zip(le, re))
            qpadd(result, exponent, qimultiply(li, ri, f"{label}:{le}:{re}"))
    return result


def symbolic_translation(inverse):
    result = {}
    edge = qconstant(*EDGE)
    orientation = "inverse" if inverse else "positive"
    for time, (left, right) in enumerate(VARIABLES):
        for space in range(4):
            residual = {ZERO: qconstant(-8)}
            for exponent in (left, right, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO):
                qpadd(residual, exponent, edge)
            delta = {}
            here = MATRIX[time][space]
            for other_time, other_space, exponent in (
                (time - 1, space, left),
                (time + 1, space, right),
                (time, (space - 1) % 4, ZERO),
                (time, (space + 1) % 4, ZERO),
            ):
                factor = qfactor(MATRIX[other_time][other_space] - here, inverse)
                if factor != qconstant(0):
                    qpadd(delta, exponent, qimultiply(edge, factor, f"{orientation}:edge-factor:{time}:{space}:{exponent}"))
            doubled = {exponent: qiscale(bounds, 2) for exponent, bounds in residual.items()}
            for name, contribution in (
                ("cross", qpoly_product(doubled, delta, f"{orientation}:cross:{time}:{space}")),
                ("square", qpoly_product(delta, delta, f"{orientation}:square:{time}:{space}")),
            ):
                for exponent, bounds in contribution.items():
                    qpadd(result, exponent, bounds)
    return result


def symbolic_summary(inverse):
    polynomial = symbolic_translation(inverse)
    for sample in (Fraction(8), Fraction(25, 2), Fraction(17), Fraction(100)):
        numeric = numeric_translation(Fraction(1, 2 * sample), Fraction(1, sample)) if inverse else numeric_translation(sample, 2 * sample)
        require(
            all((qvalue(bounds[0], sample), qvalue(bounds[1], sample)) == numeric[exponent] for exponent, bounds in polynomial.items()),
            f"symbolic/numeric cross-check failed at B={sample}",
        )
    squares = ((0, 2, 0, 0, 0), (0, 0, 0, -2, 0))
    linears = ((0, 1, 0, 0, 0), (0, 0, 0, -1, 0))
    alpha = qextreme([polynomial[exponent][0] for exponent in squares], True, "alpha")
    beta = qextreme([qscale(polynomial[exponent][0], -1) for exponent in linears], False, "beta")
    constant = polynomial[ZERO][0]
    special = {ZERO, *squares, *linears}
    discarded = []
    for exponent, bounds in sorted(polynomial.items()):
        if exponent not in special:
            record = {"monomial": list(exponent), "lower": qrecord(bounds[0])}
            require(record["lower"]["all_shifted_coefficients_nonnegative"], "discarded symbolic sign failed")
            discarded.append(record)
    remainder = qadd(constant, {4: Fraction(-9, 10)})
    gap_numerator = qadd(qscale(qmultiply(alpha, remainder), 2), qscale(qmultiply(beta, beta), -1))
    require(qvalue(alpha) > 0 and all(value >= 0 for value in qshift(alpha)[1]), "symbolic alpha failed")
    require(qvalue(beta) > 0 and all(value >= 0 for value in qshift(beta)[1]), "symbolic beta failed")
    require(qvalue(gap_numerator) > 0 and all(value >= 0 for value in qshift(gap_numerator)[1]), "symbolic gap failed")
    return {
        "orientation": "b in [B,2B]" if not inverse else "b in [1/(2B),1/B]",
        "scope": "every real B>=8",
        "coefficient_count": len(polynomial),
        "discarded_coefficient_count": len(discarded),
        "discarded_ledger_sha256": canonical_digest(discarded),
        "all_discarded_lower_coefficients_nonnegative": True,
        "square_floor_alpha": qrecord(alpha),
        "negative_linear_magnitude_beta": qrecord(beta),
        "constant_floor": qrecord(constant),
        "gap_numerator_for_nine_tenths_B4": qrecord(gap_numerator),
        "gap_lower_bound": "constant-beta^2/(2 alpha)>=(9/10)B^4",
        "status": "EXACT_FULL_DYADIC_OCTAVE_GAP",
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(digest(item["path"]) == item["sha256"] for item in cert["provenance"]["inputs"]), "input hash drift")

        middle = cert["middle_octave_certificate"]
        positive = [numeric_summary(index, Fraction(4 + 2 * index), Fraction(6 + 2 * index)) for index in range(2)]
        inverse = [numeric_summary(index, Fraction(1, 8) + index * Fraction(1, 16), Fraction(3, 16) + index * Fraction(1, 16)) for index in range(2)]
        require(middle["positive_bins"] == positive and middle["inverse_bins"] == inverse, "middle-bin ledger drift")
        minimum = min(positive + inverse, key=lambda item: frac(item["residual_square_gap"]))
        require(minimum == middle["minimum_witness"], "middle witness drift")
        middle_gap = Fraction(477200043180364512192613499, 3808294587860368619520000)
        require(frac(middle["uniform_residual_square_gap"]) == middle_gap == frac(minimum["residual_square_gap"]), "middle gap drift")

        QBRANCHES.clear()
        positive_symbolic = symbolic_summary(False)
        inverse_symbolic = symbolic_summary(True)
        asymptotic = cert["asymptotic_octave_certificate"]
        require(asymptotic["positive_orientation"] == positive_symbolic, "positive symbolic certificate drift")
        require(asymptotic["inverse_orientation"] == inverse_symbolic, "inverse symbolic certificate drift")
        require(asymptotic["symbolic_interval_branch_count"] == len(QBRANCHES), "branch count drift")
        require(asymptotic["symbolic_interval_branch_ledger_sha256"] == canonical_digest(QBRANCHES), "branch ledger drift")

        first_gap = Fraction(5042236776703616766188323, 11848410086135937585570000)
        first_exponent = Fraction(25, 32) * first_gap
        union = cert["all_amplitude_union"]
        require(frac(union["adaptive_event_radius"]) == Fraction(1, 800), "adaptive radius drift")
        require(frac(union["representative_cylinder_radius"]) == Fraction(1, 400), "representative radius drift")
        require(frac(union["lambda_point_four_first_octave_exponent"]) == first_exponent, "first exponent drift")
        require(frac(union["lambda_point_four_middle_octave_exponent"]) == Fraction(25, 32) * middle_gap, "middle exponent drift")
        require(frac(union["lambda_point_four_outer_first_exponent"]) == 2880, "outer exponent drift")
        require(union["total_prefactor"] == 3208 and frac(union["dominant_exponent"]) == first_exponent, "global union bound drift")

        disposition = cert["method_disposition"]
        require(disposition["all_large_amplitude_slab_union_probability"] == "PROVED_EXPONENTIALLY_SUPPRESSED", "all-amplitude theorem omitted")
        require(disposition["arbitrary_large_corrector_has_slab_morphology"] == "OPEN", "slab family promoted to all correctors")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == "NOT_ESTABLISHED", "continuum promoted")
        require(disposition["born_rule"] == "NOT_ESTABLISHED", "Born promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein promoted")
        require(disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "Lorentzian promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, ZeroDivisionError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT corrector-slab all-amplitude suppression: PASS" if ok else "BT corrector-slab all-amplitude suppression: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
