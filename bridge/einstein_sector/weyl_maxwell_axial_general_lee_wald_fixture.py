"""Slow direct Lee--Wald samples for arbitrary axial coefficients."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import _sphere_integral
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import weyl_maxwell_current_time


ROOT = Path(__file__).resolve().parents[2]
GREEN_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_green_current.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/weyl_maxwell_axial_general_lee_wald_fixture.schema.json"


class GeneralAxialLeeWaldFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GeneralAxialLeeWaldFixtureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _variation(
    coefficients: tuple[sp.Symbol, ...],
    wave: sp.Expr,
    harmonic: sp.Expr,
    axial_one_form: sp.Expr,
) -> tuple[sp.Matrix, sp.Matrix]:
    metric = sp.zeros(4)
    metric[0, 3] = metric[3, 0] = coefficients[0] * wave * axial_one_form
    metric[1, 3] = metric[3, 1] = coefficients[1] * wave * axial_one_form
    potential = sp.zeros(4, 1)
    potential[0] = coefficients[2] * wave * harmonic
    potential[1] = coefficients[3] * wave * harmonic
    return metric, potential


def _reduced_matrix(ell: int, momentum: sp.Symbol, first_frequency: sp.Symbol, second_frequency: sp.Symbol) -> sp.Matrix:
    green = json.loads(GREEN_CERTIFICATE.read_text(encoding="utf-8"))
    result = sp.zeros(4)
    for term in green["reduced_current"]["time_current_terms"]:
        coefficient = sp.sympify(
            term["coefficient"].replace("lambda", "lam"),
            locals={"lam": sp.Integer(ell * (ell + 1))},
        )
        result[term["u_component"], term["v_component"]] += (
            coefficient
            * (-sp.I * first_frequency) ** term["u_t_order"]
            * (sp.I * momentum) ** term["u_x_order"]
            * (sp.I * second_frequency) ** term["v_t_order"]
            * (-sp.I * momentum) ** term["v_x_order"]
        )
    return result.applyfunc(sp.factor)


def _direct_matrix(ell: int) -> dict[str, Any]:
    _require(ell >= 2, "generic axial coefficient fixture requires ell>=2")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    momentum, first_frequency, second_frequency = sp.symbols(
        "k omega1 omega2", real=True
    )
    first_coefficients = sp.symbols("u0:4")
    second_coefficients = sp.symbols("v0:4")
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(ell, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    first_wave = sp.exp(sp.I * (momentum * space - first_frequency * time))
    second_wave = sp.exp(-sp.I * (momentum * space - second_frequency * time))
    phase = sp.exp(sp.I * (second_frequency - first_frequency) * time)
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    current = weyl_maxwell_current_time(
        metric,
        field,
        _variation(first_coefficients, first_wave, harmonic, axial_one_form),
        _variation(second_coefficients, second_wave, harmonic, axial_one_form),
        coordinates,
        sp.Integer(3),
    )
    integrated = sp.factor(_sphere_integral(current, theta, azimuth) / phase)
    direct_matrix = sp.Matrix(
        4,
        4,
        lambda left, right: sp.factor(
            sp.diff(integrated, first_coefficients[left], second_coefficients[right])
        ),
    )
    reduced_matrix = _reduced_matrix(ell, momentum, first_frequency, second_frequency)
    harmonic_norm = sp.Rational(4, 2 * ell + 1) * sp.pi
    remainder = (direct_matrix - harmonic_norm * reduced_matrix).applyfunc(sp.factor)
    _require(remainder == sp.zeros(4), f"ell={ell} direct/reduced current mismatch")
    return {
        "ell": ell,
        "lambda": ell * (ell + 1),
        "harmonic": f"P_{ell}(cos(theta))",
        "harmonic_norm": str(harmonic_norm),
        "coefficient_order": ["h_t", "h_x", "q_t", "q_x"],
        "direct_integrated_matrix": [
            [str(sp.factor(direct_matrix[row, column])) for column in range(4)]
            for row in range(4)
        ],
        "reduced_Green_matrix": [
            [str(sp.factor(reduced_matrix[row, column])) for column in range(4)]
            for row in range(4)
        ],
        "direct_minus_norm_times_reduced": [
            [str(remainder[row, column]) for column in range(4)] for row in range(4)
        ],
        "independent_frequencies_retained": True,
    }


def build_certificate() -> dict[str, Any]:
    green = json.loads(GREEN_CERTIFICATE.read_text(encoding="utf-8"))
    _require(green["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT", "Green-current input changed")
    return {
        "schema": "weyl-maxwell-axial-general-lee-wald-fixture-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "WEYL_MAXWELL_AXIAL_GENERAL_LEE_WALD_FIXTURE",
        "result_state": "DIRECT_4D_LEE_WALD_EQUALS_HARMONIC_NORM_TIMES_REDUCED_GREEN_AT_ELL2_ELL3_ELL4",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_AXIAL_DIRECT_LEE_WALD_SPECTRAL_SAMPLES",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "input": {"path": str(GREEN_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(GREEN_CERTIFICATE)},
        },
        "domain": "arbitrary off-shell axial coefficient pairs with independent temporal frequencies and common symbolic compact momentum, direct four-dimensional Weyl-Maxwell Lee-Wald current",
        "samples": {str(ell): _direct_matrix(ell) for ell in (2, 3, 4)},
        "classification": {
            "full_four_by_four_coefficient_matrix_checked": True,
            "independent_frequencies_checked": True,
            "ell2_ell3_ell4_direct_coordinate_checks": True,
            "branch_or_equations_of_motion_used": False,
            "generic_lambda_promotion_in_this_fixture": False,
        },
        "interpretation": "At three exact spherical eigenvalues, the complete directly varied four-dimensional Weyl-Maxwell Lee-Wald current equals the positive Legendre harmonic norm times the independently constructed reduced Green current for arbitrary off-shell axial coefficients and independent frequencies.",
        "claim_boundary": "This slow LOCAL-ALGEBRAIC/REDUCED-MODE fixture supplies exact spectral samples. Generic-lambda promotion and all physical interpretations are separate theorems.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.weyl_maxwell_axial_general_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_weyl_maxwell_axial_general_lee_wald_fixture",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale direct Lee-Wald fixture: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--ell", type=int)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.ell is not None:
        print(json.dumps(_direct_matrix(args.ell), indent=2, sort_keys=True))
    if not args.write and args.verify is None and args.ell is None:
        parser.error("one of --write, --verify, or --ell is required")


if __name__ == "__main__":
    main()
