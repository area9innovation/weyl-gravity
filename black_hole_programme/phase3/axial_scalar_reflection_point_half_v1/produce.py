#!/usr/bin/env python3
"""Produce the validated omega=1/2 scalar-reflection certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .rigorous import run_all


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SCHEMA = "phase3-axial-scalar-reflection-point-half-v1"

IMPORTS = {
    "incoming_connection": (
        "black_hole_programme/phase3/"
        "axial_incoming_connection_analytic/certificate.json"
    ),
    "triangular_factorization": (
        "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    rails = run_all()
    lower_bounds = {}
    for spin in (1, 2):
        values = [
            float(
                rails[name][f"spin_{spin}"]["bounds"]["abs_A_out_lower"]
            )
            for name in rails
        ]
        squared_values = [
            float(
                rails[name][f"spin_{spin}"]["bounds"][
                    "abs_A_out_squared_lower"
                ]
            )
            for name in rails
        ]
        lower_bounds[f"spin_{spin}"] = {
            "abs_A_out_lower": repr(min(values)),
            "abs_A_out_squared_lower": repr(min(squared_values)),
            "both_rails_exclude_zero": all(value > 0.0 for value in values),
        }

    imports = {
        name: {"path": path, "sha256": sha256(ROOT / path)}
        for name, path in IMPORTS.items()
    }
    return {
        "schema": SCHEMA,
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "status": (
            "VALIDATED_POINTWISE_SPIN_ONE_AND_SPIN_TWO_"
            "OUTGOING_REFLECTION_NONVANISHING_AT_OMEGA_HALF"
        ),
        "scope": {
            "background": "Schwarzschild M=1",
            "parity": "axial",
            "ell": 2,
            "frequency": "1/2",
            "channels": ["spin_one", "spin_two"],
        },
        "imports": imports,
        "convention_crosswalk": {
            "time_phase": "exp(+I*omega*t)",
            "future_horizon_phase": "exp(+I*omega*rstar)",
            "infinity_expansion": (
                "psi=A_in_s*exp(+I*omega*rstar)"
                "+A_out_s*exp(-I*omega*rstar)"
            ),
            "interaction_coordinates": (
                "psi=a*exp(+I*omega*x)+b*exp(-I*omega*x)"
            ),
            "horizon_initial_line": "(a,b)=(1,0)",
            "asymptotic_reading": "A_in_s=lim a; A_out_s=lim b",
            "factor_filtration_reading": (
                "In an endpoint-compatible triangular factor frame, the "
                "three outgoing diagonal quotient coefficients are a "
                "nonzero analytic frame unit times "
                "(A_out_2,A_out_2,A_out_1). Therefore the two certified "
                "scalar nonvanishing statements exclude a diagonal zero "
                "independently of the extension off-diagonal entries."
            ),
        },
        "exact_equations": {
            "tortoise_map": "x=r+2*Log(r/2-1)",
            "inverse": "r(x)=2*(1+LambertW(exp(x/2-1)))",
            "potential_spin_one": "6*(r-2)/r**3",
            "potential_spin_two": "6*(r-2)*(r-1)/r**4",
            "interaction_system_at_omega_half": {
                "a_prime": "-I*V*(a+b*exp(-I*x))",
                "b_prime": "+I*V*(a*exp(+I*x)+b)",
            },
            "horizon_tail_integrals": {
                "spin_one": "Integral_-infinity^x0 V dx=3-6/r(x0)",
                "spin_two": (
                    "Integral_-infinity^x0 V dx="
                    "9/4-6/r(x0)+3/r(x0)^2"
                ),
            },
            "infinity_tail_integrals": {
                "spin_one": "Integral_x1^infinity V dx=6/r(x1)",
                "spin_two": (
                    "Integral_x1^infinity V dx=6/r(x1)-3/r(x1)^2"
                ),
            },
            "tail_error_law": (
                "For max norm and m=2*Integral V dx, "
                "norm(Phi-I)<=exp(m)-1"
            ),
        },
        "validated_method": {
            "backend": "python-flint Arb/Acb ball arithmetic",
            "point_frequency_only": True,
            "coefficient_analyticity_domain": (
                "complex x rectangles of radius 1/4; exp(x/2-1) stays "
                "in the right half-plane and principal LambertW is analytic"
            ),
            "local_method": (
                "Taylor recurrence plus explicit polynomial defect; "
                "Cauchy coefficient-tail enclosure and Gronwall propagation"
            ),
            "directed_rounding": (
                "Arb supplies coefficient and modulus enclosures. Every "
                "conversion to binary64 is moved one ulp outward with "
                "nextafter; every nonnegative sum/product/exponential used "
                "in an upper bound is again moved outward."
            ),
            "independent_geometries": [
                "h=1/8, Taylor order 24",
                "h=1/16, Taylor order 20",
            ],
            "rails": rails,
        },
        "certified_lower_bounds": lower_bounds,
        "claim_flags": {
            "spin_one_reflection_nonzero_at_omega_half": True,
            "spin_two_reflection_nonzero_at_omega_half": True,
            "strict_scalar_reflection_lower_bounds_certified": True,
            "whole_frequency_cell_certified": False,
            "explicit_full_Tplus_matrix_certified": False,
            "extension_offdiagonal_entries_certified": False,
        },
        "does_not_establish": [
            "reflection nonvanishing on a frequency interval",
            "the explicit full 3x3 outgoing Bach connection matrix",
            "outgoing extension amplitudes or channel mixing",
            "time-domain boundedness, limiting absorption or decay",
            "a QNM Smith selector or Green-resolvent pole",
        ],
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build()
    content = render(data)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != content:
            raise RuntimeError("certificate drift")
        print("PASS scalar reflection point-half reproduction")
        return 0
    OUTPUT.write_text(content)
    receipt = {
        "schema": "phase3-axial-scalar-reflection-point-half-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "producer": "produce.py",
        "commands": [
            (
                "python3 -m black_hole_programme.phase3."
                "axial_scalar_reflection_point_half_v1.produce --check"
            ),
            (
                "python3 -m black_hole_programme.phase3."
                "axial_scalar_reflection_point_half_v1.verify"
            ),
            (
                "python3 -m unittest black_hole_programme.phase3."
                "axial_scalar_reflection_point_half_v1.tests."
                "test_reflection"
            ),
            (
                "python3 -m jsonschema -i black_hole_programme/phase3/"
                "axial_scalar_reflection_point_half_v1/certificate.json "
                "black_hole_programme/phase3/"
                "axial_scalar_reflection_point_half_v1/schema.json"
            ),
        ],
        "claim_boundary": (
            "pointwise scalar diagonal reflection nonvanishing at omega=1/2; "
            "no whole-cell, explicit Tplus, off-diagonal or time-domain claim"
        ),
    }
    RECEIPT.write_text(render(receipt))
    print("PASS spin-one and spin-two reflection nonzero at omega=1/2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
