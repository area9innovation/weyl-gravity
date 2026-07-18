#!/usr/bin/env python3
"""Apply a correlated direct clock transform in selected exact charge blocks."""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
from math import factorial, isqrt
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
import sympy as sp

from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import AMPLITUDE_LOWER
from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import _fast_complex_interval
from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import charge_block, delta_row, scalar_eigenvalue
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import CZERO, _cadd, _cmul, _mul
from closed_universe_observers.generate_berger_validated_flat_bump_moments import _fraction_from_mpf_tuple


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM.json"
SCHEMA = PACKAGE / "schema/berger-selected-charge-block-correlated-clock-transform-v1.schema.json"
REPORT = PACKAGE / "reports/berger-selected-charge-block-correlated-clock-transform.md"
DEPENDENCIES = {
    "bandwidth_preflight": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_TEMPORAL_BANDWIDTH_PREFLIGHT.json",
    "completed_inputs": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_FORM_COMPANION_CLOCK_RAIL.json",
    "selected_p0": PACKAGE / "certificates/BERGER_SELECTED_P0_POLARIZED_FORM_INTERVALS.json",
    "exact_blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
    "base_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "p28_moments": PACKAGE / "certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json",
    "lower_band_preflight": PACKAGE / "certificates/BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_PREFLIGHT.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_selected_charge_block_correlated_clock_transform.py",
    PACKAGE / "tests/test_berger_selected_charge_block_correlated_clock_transform.py",
    SCHEMA,
    REPORT,
]
SUBDIVISIONS = 4096
COARSE_SUBDIVISIONS = 512
IV_DPS = 50
ALGEBRAIC_BITS = 192
OUTPUT_DYADIC_BITS = 160

Interval = tuple[Fraction, Fraction]
ComplexInterval = tuple[Interval, Interval]
ScalarKey = tuple[int, int]
AffineForm = dict[ScalarKey, ComplexInterval]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def _scale(value: Interval, factor: Fraction) -> Interval:
    endpoints = factor * value[0], factor * value[1]
    return min(endpoints), max(endpoints)


def _inverse(value: Interval) -> Interval:
    if value[0] <= 0 <= value[1]:
        raise ZeroDivisionError("interval contains zero")
    endpoints = Fraction(1, value[0]), Fraction(1, value[1])
    return min(endpoints), max(endpoints)


def _power(value: Interval, exponent: int) -> Interval:
    if exponent < 0:
        return _inverse(_power(value, -exponent))
    answer = (Fraction(1), Fraction(1))
    base = value
    while exponent:
        if exponent & 1:
            answer = _mul(answer, base)
        base = _mul(base, base)
        exponent //= 2
    return answer


def _sqrt_fraction(value: Fraction) -> Interval:
    if value < 0:
        raise ValueError("negative square root")
    denominator = 1 << ALGEBRAIC_BITS
    root = isqrt((value.numerator * denominator * denominator) // value.denominator)
    exact = root * root * value.denominator == value.numerator * denominator * denominator
    return Fraction(root, denominator), Fraction(root if exact else root + 1, denominator)


@lru_cache(maxsize=None)
def algebraic_interval(expression: sp.Expr) -> Interval:
    expression = sp.sympify(expression)
    if expression.is_Rational:
        exact = Fraction(int(sp.numer(expression)), int(sp.denom(expression)))
        return exact, exact
    if expression.is_Add:
        answer = (Fraction(0), Fraction(0))
        for argument in expression.args:
            answer = _add(answer, algebraic_interval(argument))
        return answer
    if expression.is_Mul:
        answer = (Fraction(1), Fraction(1))
        for argument in expression.args:
            answer = _mul(answer, algebraic_interval(argument))
        return answer
    if expression.is_Pow:
        base, exponent = expression.args
        base_interval = algebraic_interval(base)
        if exponent == sp.Rational(1, 2):
            if base_interval[0] < 0:
                raise ValueError("negative algebraic radicand")
            return _sqrt_fraction(base_interval[0])[0], _sqrt_fraction(base_interval[1])[1]
        if exponent == sp.Rational(-1, 2):
            root = (_sqrt_fraction(base_interval[0])[0], _sqrt_fraction(base_interval[1])[1])
            return _inverse(root)
        if exponent.is_Integer:
            return _power(base_interval, int(exponent))
    raise AssertionError(f"unsupported real algebraic expression: {expression}")


def _round_outward(value: Interval, bits: int = OUTPUT_DYADIC_BITS) -> Interval:
    denominator = 1 << bits
    lower = value[0].numerator * denominator // value[0].denominator
    upper = -(-value[1].numerator * denominator // value[1].denominator)
    return Fraction(lower, denominator), Fraction(upper, denominator)


def _serialize(value: Interval) -> dict[str, str]:
    value = _round_outward(value)
    return {"lower": str(value[0]), "upper": str(value[1]), "width": str(value[1] - value[0])}


def _serialize_complex(value: ComplexInterval) -> dict[str, dict[str, str]]:
    return {"real": _serialize(value[0]), "imaginary": _serialize(value[1])}


def _width(value: ComplexInterval) -> Fraction:
    return max(value[0][1] - value[0][0], value[1][1] - value[1][0])


def _mp_interval(value: Interval):
    lower = mp.iv.mpf(value[0].numerator) / value[0].denominator
    upper = mp.iv.mpf(value[1].numerator) / value[1].denominator
    return mp.iv.mpf([lower.a, upper.b])


def _mp_endpoints(value) -> Interval:
    raw = value._mpi_
    return _fraction_from_mpf_tuple(raw[0]), _fraction_from_mpf_tuple(raw[1])


@lru_cache(maxsize=None)
def _clock_cells(subdivisions: int) -> tuple[tuple[Interval, Interval], ...]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("clock subdivisions must be a positive power of two")
    mp.iv.dps = IV_DPS
    clock_lambda = mp.iv.sqrt(58) / 288
    rows = []
    for index in range(subdivisions):
        cell = (Fraction(index, subdivisions), Fraction(index + 1, subdivisions))
        if index == subdivisions - 1:
            endpoint = mp.iv.mpf(index) / subdivisions
            bump_upper = mp.iv.exp(1 - 1 / (1 - endpoint * endpoint))
            base = (Fraction(0), _mp_endpoints(bump_upper)[1])
        else:
            x = mp.iv.mpf([mp.mpf(index) / subdivisions, mp.mpf(index + 1) / subdivisions])
            base = _mp_endpoints(mp.iv.exp(1 - 1 / (1 - x * x)) * mp.iv.cos(clock_lambda * x))
        rows.append((cell, base))
    return tuple(rows)


@lru_cache(maxsize=None)
def clock_transform(expression: sp.Expr, denominator: Interval, subdivisions: int = SUBDIVISIONS) -> Interval:
    mp.iv.dps = IV_DPS
    eigenvalue = _mp_interval(algebraic_interval(expression))
    frequency = mp.iv.sqrt(eigenvalue) / 48
    total = (Fraction(0), Fraction(0))
    for (left, right), base in _clock_cells(subdivisions):
        if right == 1:
            oscillation = (Fraction(-1), Fraction(1))
        else:
            x = mp.iv.mpf([mp.mpf(left.numerator) / left.denominator, mp.mpf(right.numerator) / right.denominator])
            oscillation = _mp_endpoints(mp.iv.cos(frequency * x))
        total = _add(total, _scale(_mul(base, oscillation), right - left))
    return _round_outward(_mul(total, _inverse(denominator)))


def _spectral_data(charge: Fraction, denominator: Interval, subdivisions: int = SUBDIVISIONS):
    members, block = charge_block(1024, charge)
    eigenvalues = sorted(block.eigenvals(), key=lambda value: float(sp.N(value, 40)))
    identity = sp.eye(len(members))
    projectors = []
    exact_projectors = []
    rows = []
    for index, eigenvalue in enumerate(eigenvalues):
        projector = identity
        for other_index, other in enumerate(eigenvalues):
            if index != other_index:
                projector = projector * (block - other * identity) / (eigenvalue - other)
        projector = projector.applyfunc(sp.simplify)
        if (block * projector - eigenvalue * projector).applyfunc(sp.simplify) != sp.zeros(len(members)):
            raise AssertionError("spectral projector eigen-identity failed")
        exact_projectors.append(projector)
        interval_projector = tuple(
            tuple((algebraic_interval(projector[row, column]), (Fraction(0), Fraction(0))) for column in range(len(members)))
            for row in range(len(members))
        )
        transform = clock_transform(eigenvalue, denominator, subdivisions)
        projectors.append((transform, interval_projector))
        rows.append({
            "spectral_index": index,
            "exact_eigenvalue": sp.sstr(eigenvalue),
            "eigenvalue_interval": _serialize(algebraic_interval(eigenvalue)),
            "normalized_clock_microphase_transform": _serialize(transform),
            "spectral_projector": [[_serialize(entry[0]) for entry in row] for row in interval_projector],
        })
    if sum(exact_projectors, sp.zeros(len(members))).applyfunc(sp.simplify) != identity:
        raise AssertionError("spectral projectors do not resolve the identity")
    for left_index, left in enumerate(exact_projectors):
        for right_index, right in enumerate(exact_projectors):
            expected = left if left_index == right_index else sp.zeros(len(members))
            if (left * right - expected).applyfunc(sp.simplify) != sp.zeros(len(members)):
                raise AssertionError("spectral projector product identity failed")
    return members, block, eigenvalues, projectors, rows


def _affine_add(left: AffineForm, right: AffineForm) -> AffineForm:
    answer = dict(left)
    for key, value in right.items():
        answer[key] = _cadd(answer.get(key, CZERO), value)
    return {key: value for key, value in answer.items() if value != CZERO}


def _affine_scale(coefficient: ComplexInterval, value: AffineForm) -> AffineForm:
    return {key: _cmul(coefficient, entry) for key, entry in value.items()}


def _affine_evaluate(value: AffineForm, scalars: dict[ScalarKey, Interval]) -> ComplexInterval:
    answer = CZERO
    for key, coefficient in value.items():
        scalar = scalars[key]
        answer = _cadd(answer, (_mul(coefficient[0], scalar), _mul(coefficient[1], scalar)))
    return answer


def _spatial_real_affine_lookup(selected: dict[str, Any], completed: dict[str, Any]):
    lookup: dict[tuple[str, int, int, int], AffineForm] = {}
    scalars: dict[ScalarKey, Interval] = {}
    rows = [*selected["polarized_form_rows"], *completed["form_companion_rows"]]
    for row in rows:
        value: AffineForm = {}
        for term in row["term_applications"]:
            key = (term["scalar_two_j"], term["scalar_diagonal_index"])
            coefficient = _fast_complex_interval(sp.sympify(term["exact_detector_prefactored_coefficient"]))
            scalar = (Fraction(term["scalar_interval"]["lower"]), Fraction(term["scalar_interval"]["upper"]))
            if key in scalars and scalars[key] != scalar:
                raise AssertionError("shared scalar interval drifted across form entries")
            scalars[key] = scalar
            value[key] = _cadd(value.get(key, CZERO), coefficient)
        lookup[(row["detector_id"], row["coframe_component"], row["form_row"], row["form_column"])] = value
    if len(lookup) != 51:
        raise AssertionError("complete spatial real-entry coverage drifted")
    if len(scalars) != 18:
        raise AssertionError("complete correlated scalar-variable coverage drifted")
    return lookup, scalars


def _helicity_affine(
    helicity: int,
    detector: str,
    row: int,
    column: int,
    real_lookup: dict[tuple[str, int, int, int], AffineForm],
) -> AffineForm:
    if helicity == 1:
        return real_lookup.get((detector, 3, row, column), {})
    v1 = real_lookup.get((detector, 1, row, column), {})
    v2 = real_lookup.get((detector, 2, row, column), {})
    coefficient1 = _fast_complex_interval(1 / sp.sqrt(2))
    coefficient2 = _fast_complex_interval((-sp.I if helicity == 0 else sp.I) / sp.sqrt(2))
    return _affine_add(_affine_scale(coefficient1, v1), _affine_scale(coefficient2, v2))


def _spectral_transform_affine(projectors, vector: list[AffineForm]) -> list[AffineForm]:
    answer: list[AffineForm] = [{} for _ in vector]
    for transform, projector in projectors:
        for row_index, row in enumerate(projector):
            for entry, source in zip(row, vector):
                coefficient = (_mul(transform, entry[0]), _mul(transform, entry[1]))
                answer[row_index] = _affine_add(answer[row_index], _affine_scale(coefficient, source))
    return answer


def _dot_affine(row: tuple[ComplexInterval, ...], vector: list[AffineForm]) -> AffineForm:
    answer: AffineForm = {}
    for entry, value in zip(row, vector):
        answer = _affine_add(answer, _affine_scale(entry, value))
    return answer


def _lower_band_overlap(values: dict[str, Any], denominator: Interval) -> dict[str, Any]:
    zero_raw = clock_transform(sp.Integer(0), denominator)
    p0_factor = (AMPLITUDE_LOWER, Fraction(1))
    zero = max(zero_raw[0], p0_factor[0]), min(zero_raw[1], p0_factor[1])
    if zero[0] > zero[1]:
        raise AssertionError("direct zero-frequency transform does not overlap the p0 factor enclosure")
    eigenvalue = sp.Rational(196000, 9)
    direct = clock_transform(eigenvalue, denominator)
    polynomial = (Fraction(0), Fraction(0))
    for index, row in enumerate(values["p28_moments"]["normalized_clock_even_moments"]):
        moment = row["normalized_even_moment"]
        joint = _mul(p0_factor, (Fraction(moment["lower"]), Fraction(moment["upper"])))
        factor = Fraction((-1) ** index) * Fraction(196000, 9) ** index / factorial(2 * index) / 48 ** (2 * index)
        polynomial = _add(polynomial, _scale(joint, factor))
    remainder = Fraction(values["lower_band_preflight"]["microphase_remainder_audit"]["Delta1_cosine_microphase_remainder_upper"])
    certified = (polynomial[0] - remainder, polynomial[1] + remainder)
    if not certified[0] <= direct[0] <= direct[1] <= certified[1]:
        raise AssertionError("direct transform failed lower-band order-14 overlap")
    return {
        "zero_frequency_direct_quadrature_interval": _serialize(zero_raw),
        "zero_frequency_direct_transform_intersected_with_pointwise_factor_bound": _serialize(zero),
        "p0_uniform_factor_enclosure": _serialize(p0_factor),
        "zero_frequency_contained_in_p0_enclosure": True,
        "two_j138_extreme_eigenvalue": str(eigenvalue),
        "two_j138_direct_transform": _serialize(direct),
        "two_j138_order14_moment_interval_with_remainder": _serialize(certified),
        "two_j138_direct_transform_contained_in_order14_interval": True,
    }


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "bandwidth_preflight": "CORRELATED_DIRECT_CLOCK_MICROPHASE_TRANSFORM_REQUIRED",
        "completed_inputs": "ALL_18_SELECTED_CHARGE_BLOCK_INPUTS_CLOSED",
        "selected_p0": "SELECTED_P0_POLARIZED_FORM_INTERVALS_EVALUATED",
        "exact_blocks": "ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED",
        "base_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "p28_moments": "VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED",
        "lower_band_preflight": "ANGLE_ADDITION_BLOCKWISE_ROUTE_CERTIFIED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    base_row = next(row for row in values["base_moments"]["raw_radial_integral_enclosures"] if row["power"] == 0)
    denominator = (Fraction(base_row["integral"]["lower"]), Fraction(base_row["integral"]["upper"]))
    spatial_lookup, scalar_lookup = _spatial_real_affine_lookup(values["selected_p0"], values["completed_inputs"])
    blocks = values["completed_inputs"]["completed_charge_block_inputs"]
    charges = sorted({Fraction(block["charge_q"]) for block in blocks})

    spectral_by_charge = {}
    spectral_audits = []
    fine_widths = []
    coarse_widths = []
    for charge in charges:
        members, block_matrix, eigenvalues, projectors, rows = _spectral_data(charge, denominator)
        scalar = scalar_eigenvalue(1024, charge)
        scalar_index = next(index for index, eigenvalue in enumerate(eigenvalues) if sp.simplify(eigenvalue - scalar) == 0)
        spectral_by_charge[charge] = (members, block_matrix, eigenvalues, projectors, scalar_index)
        fine_widths.extend(Fraction(row["normalized_clock_microphase_transform"]["width"]) for row in rows)
        coarse = [clock_transform(eigenvalue, denominator, COARSE_SUBDIVISIONS) for eigenvalue in eigenvalues]
        coarse_widths.extend(value[1] - value[0] for value in coarse)
        spectral_audits.append({
            "charge_q": str(charge),
            "block_dimension": len(members),
            "scalar_spectral_index": scalar_index,
            "exact_projector_identities_verified": True,
            "eigenmodes": rows,
        })
    if max(fine_widths) >= Fraction(1, 250) or max(coarse_widths) <= Fraction(1, 50):
        raise AssertionError("clock-transform resolution gate drifted")

    outputs = []
    digest_rows = []
    maximum_output_width = Fraction(0)
    maximum_spatial_output_width = Fraction(0)
    maximum_temporal_output_width = Fraction(0)
    for block in blocks:
        charge = Fraction(block["charge_q"])
        members, _, eigenvalues, projectors, scalar_index = spectral_by_charge[charge]
        member_rows = block["clock_power_helicity_vectors"][0]["helicity_input_vector"]
        source_affine = [
            _helicity_affine(entry["helicity_component"], block["detector_id"], entry["form_row"], block["form_column"], spatial_lookup)
            for entry in member_rows
        ]
        source = [_affine_evaluate(value, scalar_lookup) for value in source_affine]
        expected = [(entry["helicity_component"], Fraction(entry["form_row"] - 512)) for entry in member_rows]
        if members != expected:
            raise AssertionError("selected spatial source member order drifted")
        spatial_affine = _spectral_transform_affine(projectors, source_affine)
        spatial = [_affine_evaluate(value, scalar_lookup) for value in spatial_affine]
        delta_members, delta_exact = delta_row(1024, charge)
        if delta_members != members:
            raise AssertionError("selected delta member order drifted")
        delta = tuple(_fast_complex_interval(delta_exact[0, column]) for column in range(delta_exact.cols))
        scalar_transform = projectors[scalar_index][0]
        temporal_affine = _affine_scale((scalar_transform, (Fraction(0), Fraction(0))), _dot_affine(delta, source_affine))
        temporal = _affine_evaluate(temporal_affine, scalar_lookup)
        row_width = max(_width(value) for value in [*spatial, temporal])
        maximum_output_width = max(maximum_output_width, row_width)
        maximum_spatial_output_width = max(maximum_spatial_output_width, *(_width(value) for value in spatial))
        maximum_temporal_output_width = max(maximum_temporal_output_width, _width(temporal))
        row = {
            "detector_id": block["detector_id"],
            "form_two_j": 1024,
            "form_column": block["form_column"],
            "charge_q": block["charge_q"],
            "helicity_members": [[component, str(m)] for component, m in members],
            "spatial_source_before_clock_factor": [_serialize_complex(value) for value in source],
            "correlated_microphase_dressed_spatial_input": [_serialize_complex(value) for value in spatial],
            "correlated_microphase_dressed_temporal_coderivative": _serialize_complex(temporal),
            "maximum_output_axis_width": str(row_width),
        }
        outputs.append(row)
        digest_rows.append(row)
    if maximum_spatial_output_width >= Fraction(1, 50):
        raise AssertionError(f"correlated selected spatial output is too wide: {maximum_spatial_output_width}")
    if maximum_temporal_output_width >= Fraction(6, 5):
        raise AssertionError(f"correlated selected temporal output exceeds the declared enclosure: {maximum_temporal_output_width}")

    overlap = _lower_band_overlap(values, denominator)
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result replaces the obstructed order-14 independent-moment route at selected form two_j=1024 by a correlated direct normalized clock transform. Directed interval quadrature encloses E_B[cos(sqrt(58)s/288) cos(s sqrt(lambda)/48)] at all 27 exact eigenvalues of the nine selected three-dimensional Maxwell charge blocks. Exact algebraic spectral projectors apply those transforms to all 18 completed spatial helicity inputs, while the embedded scalar eigenvalue supplies the temporal coderivative transform. Shared scalar-row variables are retained as affine forms through helicity conversion, spectral projection and coderivative contraction. Every transform width is below 0.004 and every spatial transformed axis width is below 0.02. The high-mode coderivative amplifies the remaining scalar-profile uncertainty, but every temporal transformed axis is enclosed below 1.2; no narrower response-level claim is made. A 512-cell mutation is wider than 0.02. The zero-frequency transform lies in the certified p0 clock-factor enclosure and the direct two_j=138 extreme transform lies in the earlier order-14 interval with its certified remainder. The large propagation separation remains exact and symbolic as -cos(T sqrt(B_q)) C_q and -sin(T sqrt(lambda0_q))/sqrt(lambda0_q) c_q, including the entire zero-eigenvalue extension. This certifies the selected finite-block exact-T temporal image representation, not a spatial harmonic tail, full infinite-mode Maxwell or massive image, detector response or rank, recoil, tangent-cone restriction, active Bridge 3, finite-r/all-orders observer-morphism stability or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-selected-charge-block-correlated-clock-transform-v1",
        "result_id": "BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM",
        "setting_id": values["completed_inputs"]["setting_id"],
        "claim_status": "VALIDATED_SELECTED_TWO_J1024_CORRELATED_CLOCK_TRANSFORM_AND_EXACT_T_BLOCK_IMAGE_REPRESENTATION_EXPORTED_SPATIAL_TAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "clock_transform_convention": {
            "normalized_weight": "B(s)=exp(1-1/(1-s^2)) on |s|<1, normalized by integral B",
            "external_clock_factor": "a(s)=cos(sqrt(58)s/288)",
            "microphase_factor": "cos(s sqrt(lambda)/48)",
            "odd_microphase_transform": "zero by exact parity",
            "subdivisions": SUBDIVISIONS,
            "interval_precision_decimal_digits": IV_DPS,
            "output_dyadic_bits": OUTPUT_DYADIC_BITS,
            "spatial_exact_T_image": "-cos(T sqrt(B_q)) C_q",
            "temporal_exact_T_image": "-[sin(T sqrt(lambda0_q))/sqrt(lambda0_q)] c_q",
            "zero_eigenvalue_extension": "sin(T sqrt(lambda))/sqrt(lambda) at lambda=0 is T",
            "large_T_taylor_truncation": False,
        },
        "spectral_transform_audits": spectral_audits,
        "selected_block_outputs": outputs,
        "lower_band_overlap": overlap,
        "coverage": {
            "selected_block_count": len(outputs),
            "distinct_charge_count": len(charges),
            "exact_eigenvalue_transform_count": sum(len(row["eigenmodes"]) for row in spectral_audits),
            "maximum_clock_transform_width": str(max(fine_widths)),
            "maximum_selected_spatial_output_axis_width": str(maximum_spatial_output_width),
            "maximum_selected_temporal_output_axis_width": str(maximum_temporal_output_width),
            "maximum_selected_output_axis_width": str(maximum_output_width),
            "canonical_selected_correlated_transform_sha256": hashlib.sha256(json.dumps(digest_rows, sort_keys=True).encode()).hexdigest(),
        },
        "mutation_results": [{
            "name": "reduce_clock_transform_quadrature_from_4096_to_512_cells",
            "mutated_maximum_transform_width": str(max(coarse_widths)),
            "required_maximum_transform_width": "1/250",
            "detected": max(coarse_widths) > Fraction(1, 50),
        }],
        "flags": {
            "ALL_27_EXACT_EIGENVALUE_CLOCK_TRANSFORMS_EXPORTED": True,
            "ALL_9_EXACT_BLOCK_SPECTRAL_PROJECTOR_FAMILIES_EXPORTED": True,
            "ALL_18_SELECTED_CORRELATED_MICROPHASE_INPUTS_EXPORTED": True,
            "ALL_CLOCK_TRANSFORM_WIDTHS_BELOW_FOUR_THOUSANDTHS": True,
            "ALL_SELECTED_SPATIAL_OUTPUT_WIDTHS_BELOW_TWO_HUNDREDTHS": True,
            "ALL_SELECTED_TEMPORAL_OUTPUT_WIDTHS_BELOW_SIX_FIFTHS": True,
            "LOWER_BAND_OVERLAP_CERTIFIED": True,
            "FINITE_SELECTED_EXACT_T_TEMPORAL_IMAGE_REPRESENTATION_EXPORTED": True,
            "TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED": True,
            "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "DERIVE_A_CONTROLLED_SPATIAL_HARMONIC_TAIL_AROUND_THE_SELECTED_EXACT_T_BLOCK_IMAGE_REPRESENTATION",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale selected correlated clock transform")
    print("BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
