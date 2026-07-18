#!/usr/bin/env python3
"""Enclose the clock-zero-moment detector polarization coefficients."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from math import isqrt
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    MAX_TWO_J, PACKAGE, Y0, Y1, Y2, Y3, expected_term_reduction,
    radial_moment_intervals, representation_matrix,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import C, d_matrix

CERTIFICATE = PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json"
SCHEMA = PACKAGE / "schema/berger-clock-integrated-form-profile-coefficients-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-integrated-form-profile-coefficients.md"
DEPENDENCIES = {
    "scalar": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_clock_integrated_form_profile_coefficients.py",
    "tests": PACKAGE / "tests/test_berger_clock_integrated_form_profile_coefficients.py",
    "schema": SCHEMA,
    "report": REPORT,
}
BITS = 160
A2 = Fraction(1, 128**2 * 4)
B2 = Fraction(10, 9 * 128**2)
AMPLITUDE_LOWER = Fraction(82915, 82944)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _interval(row: dict[str, str]) -> tuple[Fraction, Fraction]:
    return Fraction(row["lower"]), Fraction(row["upper"])


def _serialize(value: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {"lower": str(value[0]), "upper": str(value[1]), "width": str(value[1] - value[0])}


def _add(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0] + b[0], a[1] + b[1]


def _mul(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    values = [x * y for x in a for y in b]
    return min(values), max(values)


def _algebraic_interval(value: sp.Expr) -> tuple[Fraction, Fraction]:
    value = sp.simplify(value)
    if value == 0:
        return Fraction(0), Fraction(0)
    if value.is_Rational:
        q = Fraction(int(sp.numer(value)), int(sp.denom(value)))
        return q, q
    square = sp.simplify(value * value)
    if square.is_Rational is not True or value.is_real is not True:
        raise AssertionError(f"coefficient is not a signed square root of Q: {value}")
    q = Fraction(int(sp.numer(square)), int(sp.denom(square)))
    denominator = 2**BITS
    n = isqrt((q.numerator * denominator * denominator) // q.denominator)
    exact = n * n * q.denominator == q.numerator * denominator * denominator
    lo, hi = Fraction(n, denominator), Fraction(n if exact else n + 1, denominator)
    if value.is_negative:
        return -hi, -lo
    if value.is_positive:
        return lo, hi
    raise AssertionError(f"coefficient sign is undecidable: {value}")


def _complex_interval(value: sp.Expr) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    return _algebraic_interval(sp.re(value).expand(complex=True)), _algebraic_interval(sp.im(value).expand(complex=True))


def _complex_mul(a, b):
    ar, ai = a; br, bi = b
    return _add(_mul(ar, br), (-_mul(ai, bi)[1], -_mul(ai, bi)[0])), _add(_mul(ar, bi), _mul(ai, br))


def odd_secant_moments(scalar: dict[str, Any]) -> dict[int, tuple[Fraction, Fraction]]:
    even = {row["k"]: _interval(row["expectation_secant_power_2k"]) for row in scalar["clock_secant_moment_enclosures"]}
    result = {0: (AMPLITUDE_LOWER, Fraction(1))}
    for k in range(1, 7):
        result[k] = (even[k - 1][0], even[k][1])
    return result


def _coefficient(expression: sp.Expr, radial, odd_clock):
    terms, remainder_expr = expected_term_reduction(sp.expand(expression))
    real = (Fraction(0), Fraction(0)); imag = (Fraction(0), Fraction(0))
    for (k, ap, bp), coefficient in terms.items():
        positive = _mul(radial[k], (A2**ap * B2**bp, A2**ap * B2**bp))
        positive = _mul(positive, odd_clock[k])
        cr, ci = _complex_interval(coefficient)
        real = _add(real, _mul(cr, positive)); imag = _add(imag, _mul(ci, positive))
    remainder = _algebraic_interval(remainder_expr)[1] if remainder_expr else Fraction(0)
    real = (real[0] - remainder, real[1] + remainder)
    imag = (imag[0] - remainder, imag[1] + remainder)
    return real, imag, remainder, len(terms)


def _gradient(detector: str) -> list[sp.Expr]:
    # dR=a(s) sum_i gradient_i theta^i in detector-centred SU(2) coordinates.
    if detector == "D0":
        return [-C * Y2, C * Y1, Y0]       # R0_1
    if detector == "D1":
        return [Y0, -Y3, Y2 / C]           # R1_2
    raise ValueError(detector)


def _apply_spatial_codifferential(two_j: int, components):
    n = two_j + 1
    delta = d_matrix(two_j, 0).conjugate().T
    output = []
    for row in range(n):
        for column in range(n):
            total = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0)))
            for a in range(3):
                for k in range(n):
                    factor = _complex_interval(delta[row, a * n + k])
                    total = tuple(_add(x, y) for x, y in zip(total, _complex_mul(factor, components[a][k][column])))
            if total != ((0, 0), (0, 0)):
                output.append({"row": row, "column": column, "real": _serialize(total[0]), "imag": _serialize(total[1])})
    return output


def detector_mode(detector: str, two_j: int, radial, odd_clock) -> dict[str, Any]:
    matrix = representation_matrix(two_j).conjugate().T
    n = two_j + 1
    components = []
    serialized = []
    for a, gradient in enumerate(_gradient(detector)):
        block = [[None for _ in range(n)] for _ in range(n)]
        entries = []
        for row in range(n):
            for column in range(n):
                real, imag, remainder, count = _coefficient(matrix[row, column] * gradient, radial, odd_clock)
                block[row][column] = (real, imag)
                if real != (0, 0) or imag != (0, 0):
                    entries.append({"row": row, "column": column, "real": _serialize(real), "imag": _serialize(imag), "remainder_bound": str(remainder), "term_count": count, "global_right_phase": f"exp(2*i*({sp.sstr(-sp.Rational(two_j,2)+column)})*{('sqrt(10)/12' if detector=='D0' else 'sqrt(10)/6')})"})
        components.append(block)
        serialized.append({"coframe_component": a + 1, "entries": entries})
    return {"two_j": two_j, "dimension": n, "polarization_one_form_components": serialized, "spatial_codifferential_coefficients": _apply_spatial_codifferential(two_j, components)}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {"scalar": "CLOCK_INTEGRATED_SCALAR_COEFFICIENTS_TWO_J0_TO_4_EXPORTED", "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED", "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT", "rods": "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED", "spectral": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED"}
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    polarizations = [row["polarization"] for row in values["profiles"]["exact_detector_profiles"]["detectors"]]
    if polarizations != ["dTheta_wedge_dR0_1", "dTheta_wedge_dR1_2"]:
        raise AssertionError("detector polarizations drifted")
    radial = radial_moment_intervals(values["moments"]); odd = odd_secant_moments(values["scalar"])
    detectors = [{"detector_id": detector, "polarization": "dTheta_wedge_" + ("dR0_1" if detector == "D0" else "dR1_2"), "modes": [detector_mode(detector, j, radial, odd) for j in range(MAX_TWO_J + 1)]} for detector in ("D0", "D1")]
    if any(row["modes"][0]["spatial_codifferential_coefficients"] for row in detectors):
        raise AssertionError("spin-zero spatial coderivative must vanish")
    if not all(any(mode["spatial_codifferential_coefficients"] for mode in row["modes"][1:]) for row in detectors):
        raise AssertionError("nonconstant coderivative blocks vanished")
    mutation_detected = _gradient("D0") != _gradient("D1")
    boundary = "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate applies the two distinct detector polarizations to the normalized clock/spatial bump and interval-encloses their spatial one-form Peter-Weyl coefficients through two_j=4. The exact detector-centred gradients are dR0_1=a(-c y2 theta1+c y1 theta2+y0 theta3) and dR1_2=a(y0 theta1-y3 theta2+c^-1 y2 theta3). Existing even secant moments rigorously bracket the required odd powers sec(lambda s)^(2k-1), and exact de Rham blocks give the spatial coderivative coefficient. This is the clock-zero-moment polarization block and spatial-divergence part only. The time derivative in the four-dimensional coderivative must be integrated against each mode Green kernel; modes above two_j=4, an evaluated tail, full advanced images, recoil, interacting theorems, and quantum claims remain open."
    return {"schema": "closed-universe-berger-clock-integrated-form-profile-coefficients-v1", "result_id": "BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS", "setting_id": values["scalar"]["setting_id"], "claim_status": "VALIDATED_CLOCK_ZERO_MOMENT_FORM_COEFFICIENTS_THROUGH_TWO_J4_EXPORTED_TIME_KERNEL_AND_TAIL_OPEN", "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"], "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()}, "coefficient_convention": {"fourier": "integral profile(g) D_j(g)^* dSigma", "spatial_coframe": ["theta1", "theta2", "theta3"], "global_translation": "right multiplication by D_j(g_a)^*", "odd_secant_bound": "E[sec^(2k-2)] <= E[sec^(2k-1)] <= E[sec^(2k)] for k>=1; 82915/82944 <= E[cos] <= 1 for k=0"}, "odd_secant_moment_enclosures": [{"k": k, "power": 2*k-1, "enclosure": _serialize(odd[k])} for k in range(7)], "detectors": detectors, "mutation_results": [{"name": "identify_D0_and_D1_polarizations", "detected": mutation_detected}], "flags": {"DISTINCT_FORM_POLARIZATIONS_APPLIED": True, "CLOCK_ZERO_MOMENT_FORM_COEFFICIENTS_TWO_J0_TO_4_EXPORTED": True, "SPATIAL_CODERIVATIVE_COEFFICIENTS_TWO_J0_TO_4_EXPORTED": True, "FULL_FOUR_DIMENSIONAL_TIME_KERNEL_WEIGHTED_SOURCE_COEFFICIENTS_EVALUATED": False, "VALIDATED_INFINITE_MODE_TAIL_BOUND_EXPORTED": False, "ADVANCED_GREEN_IMAGES_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "QUANTUM_CLAIM": False}, "next_gate": "INTEGRATE_THE_TEMPORAL_CODERIVATIVE_AGAINST_EACH_EXACT_MODE_GREEN_KERNEL_AND_EXPORT_AN_EVALUATED_INFINITE_TAIL", "claim_boundary": boundary, "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    value = build(); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered): raise SystemExit("stale clock-integrated form profile certificate")
    print("BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS generation: PASS"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
