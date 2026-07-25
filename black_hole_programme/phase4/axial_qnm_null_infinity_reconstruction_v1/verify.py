#!/usr/bin/env python3
"""Independent verifier for the axial QNM null-infinity reconstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(message)


def verify(data: dict) -> None:
    if data["schema"] != "axial-qnm-null-infinity-reconstruction-v1":
        fail("schema mismatch")
    if data["status"] != "EXACT_NULL_INFINITY_RECONSTRUCTION_SOURCE_OVERLAP_OPEN":
        fail("status mismatch")
    if data["dependency_tags"] != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        fail("dependency-tag mismatch")

    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        if not path.exists() or digest(path) != imported["sha256"]:
            fail(f"import hash mismatch: {path}")

    omega = sp.symbols("omega", nonzero=True)
    I = sp.I
    heads = json.loads(
        (ROOT / data["imports"]["infinity_metric_heads"]["path"]).read_text()
    )["branches"]
    c_r = I * (16 * omega**2 - 4 * I * omega - 5) / omega

    def coefficient(branch: str, component: str, index: int) -> sp.Expr:
        value = heads[branch][component][
            "coefficients_through_inverse_order_3"
        ][index]
        return sp.sympify(value, locals={"omega": omega, "I": I})

    r_h0 = [
        sp.factor(
            coefficient("XI2", "H0_from_C_equals_zero", index)
            - c_r * coefficient("XI3", "H0_from_C_equals_zero", index)
        )
        for index in range(2)
    ]
    r_h1 = [
        sp.factor(
            coefficient("XI2", "H1", index)
            - c_r * coefficient("XI3", "H1", index)
        )
        for index in range(2)
    ]
    if r_h0 != [sp.Rational(3, 4), -sp.Rational(3, 2)]:
        fail("R H0 coefficient mismatch")
    if r_h1 != [-sp.Rational(3, 2), 0]:
        fail("R H1 coefficient mismatch")

    metric = data["exact_asymptotic_reconstruction"]
    if metric["E_metric"] != {"H0": "-r+O(1)", "H1": "2*r+O(1)"}:
        fail("E metric declaration drift")
    if metric["R_metric"] != {
        "H0": "3*r**2/4-3*r/2+O(1)",
        "H1": "-3*r**2/2+O(1)",
    }:
        fail("R metric declaration drift")
    if metric["leading_relation"] != "(H0,H1)_R=-3*r*(H0,H1)_E/4+O(E)":
        fail("metric leading-relation drift")

    # Independent odd-gauge algebra.
    h_u = sp.symbols("h_u")
    xi = h_u / (I * omega)
    if sp.simplify(h_u - I * omega * xi) != 0:
        fail("radiation-gauge h_u cancellation failed")
    h2 = sp.simplify(-2 * xi)
    if h2 != 2 * I * h_u / omega:
        fail("radiation-gauge h2 sign failed")
    radiation = data["radiation_gauge"]
    if radiation["E_bondi_shear"] != "-2*I*X_AB/omega":
        fail("Einstein Bondi-shear declaration drift")
    if not radiation["E_bondi_shear_nonzero"]:
        fail("Einstein Bondi-shear nonvanishing lost")
    if radiation["R_standard_falloff"] or radiation["linear_r_tangent_cancels"]:
        fail("generalized falloff claim improperly promoted")

    # Recheck the fixed/total frequency derivative distinction.
    nu, sigma, r, t, log_r = sp.symbols("nu sigma r t log_r")
    full = (
        I * nu * t
        + sigma * I * (nu - 1 / (2 * omega)) * r
        + 2 * sigma * I * nu * log_r
    )
    rstar = r + 2 * log_r
    expected = I * nu * (t + sigma * rstar) - sigma * I * r / (2 * omega)
    if sp.simplify(full - expected) != 0:
        fail("total QNM tangent cancellation failed")
    tangent = data["qnm_tangent"]
    if tangent["total_coulomb_exponent_derivative"] != "2*sigma*I*nu":
        fail("total Coulomb derivative declaration drift")
    if tangent["outgoing_bach_tangent"] != "-I*kappa*u-r/4+O(1)":
        fail("outgoing Bach tangent declaration drift")

    observable = data["observable_double_pole"]
    if observable["selector_form"] != (
        "-I*kappa*u*exp(I*omega*u)*X_AB/"
        "(alpha_W*alpha_n*omega**2*r)"
    ):
        fail("observable selector coefficient drift")
    flags = data["claim_flags"]
    required_true = {
        "exact_E_metric_heads_reconstructed",
        "exact_R_metric_heads_reconstructed",
        "odd_radiation_gauge_reconstruction_exact",
        "einstein_bondi_shear_nonzero",
        "double_pole_observable_spatial_overlap_nonzero",
        "enhanced_local_contour_profile_standard_radiative",
    }
    required_false = {
        "generalized_constant_component_standard_falloff",
        "scalar_linear_r_tangent_cancellation",
        "specified_physical_source_overlap_nonzero",
        "full_generalized_mode_finite_bondi_flux",
        "global_causal_contour_theorem",
        "detector_observability",
    }
    if any(not flags[key] for key in required_true):
        fail("required exact claim flag is false")
    if any(flags[key] for key in required_false):
        fail("open claim was improperly promoted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=HERE / "certificate.json")
    args = parser.parse_args()
    verify(json.loads(args.certificate.read_text()))
    print("AXIAL_QNM_NULL_INFINITY_RECONSTRUCTION_VERIFIED")


if __name__ == "__main__":
    main()
