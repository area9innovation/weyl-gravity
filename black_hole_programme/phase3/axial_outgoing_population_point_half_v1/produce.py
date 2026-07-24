#!/usr/bin/env python3
"""Assemble the exact outgoing-population theorem from certified inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
SOURCES = {
    "scalar_reflection": ROOT
    / "black_hole_programme/phase3/axial_scalar_reflection_point_half_v1"
    / "certificate.json",
    "triangular_factorization": ROOT
    / "black_hole_programme/phase3/axial_rw_lx_triangular_preflight"
    / "certificate.json",
    "boundary_devissage": ROOT
    / "black_hole_programme/phase3/axial_boundary_devissage_no_growth"
    / "certificate.json",
    "outgoing_gram": ROOT
    / "black_hole_programme/phase3/axial_null_flux_gram"
    / "certificate.json",
    "transport_free_stokes": ROOT
    / "black_hole_programme/phase3"
    / "axial_transport_free_outgoing_defect_preflight_v1"
    / "certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def produce() -> dict:
    inputs = {name: load(path) for name, path in SOURCES.items()}
    reflection = inputs["scalar_reflection"]
    triangular = inputs["triangular_factorization"]
    devissage = inputs["boundary_devissage"]
    gram = inputs["outgoing_gram"]
    stokes = inputs["transport_free_stokes"]

    assert reflection["scope"]["frequency"] == "1/2"
    assert reflection["claim_flags"][
        "spin_one_reflection_nonzero_at_omega_half"
    ]
    assert reflection["claim_flags"][
        "spin_two_reflection_nonzero_at_omega_half"
    ]
    assert triangular["carrier_exact_sequence"]["exact_sequence"] == (
        "0 -> M_RW -> M_A4 -> M_x -> 0"
    )
    outgoing_germs = devissage["local_boundary_maps"][
        "pure_outgoing_infinity"
    ]
    assert outgoing_germs["germ_sequence"].startswith(
        "0 -> O_RW_metric -> O_full"
    )
    gplus = gram["endpoint_grams"]["Iplus"]["classification"]
    assert gplus["rank"] == 3 and gplus["radical_dimension"] == 0
    assert gplus["inertia_for_alpha_W_positive"] == {
        "negative": 2,
        "positive": 1,
        "zero": 0,
    }
    tier_a = stokes["tier_A_transport_free_determinant"]
    assert tier_a["determinant_equivalence"].startswith(
        "det(O)=det(Gplus)*abs(det(Tplus))^2"
    )

    getcontext().prec = 60
    l1 = Decimal(
        reflection["certified_lower_bounds"]["spin_1"]["abs_A_out_lower"]
    )
    l2 = Decimal(
        reflection["certified_lower_bounds"]["spin_2"]["abs_A_out_lower"]
    )
    factor_det_lower = l2 * l2 * l1
    factor_det_squared_lower = factor_det_lower * factor_det_lower

    return {
        "schema": "phase3-axial-outgoing-population-point-half-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF",
        "status": "VALIDATED_POINTWISE_FULL_OUTGOING_POPULATION_AT_OMEGA_HALF",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "frequency": "1/2",
            "coupling_sign": "alpha_W>0 for the stated inertia",
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in SOURCES.items()
        },
        "certified_scalar_inputs": {
            "spin_two_abs_A_out_lower": str(l2),
            "spin_one_abs_A_out_lower": str(l1),
            "intrinsic_factor_diagonal_product_lower": str(
                factor_det_lower
            ),
            "intrinsic_factor_diagonal_product_squared_lower": str(
                factor_det_squared_lower
            ),
            "normalization_scope": (
                "The product bounds the scalar factor-normalized diagonal "
                "product A_out_2^2*A_out_1. No numerical lower bound for a "
                "raw six-state endpoint-frame determinant is claimed."
            ),
        },
        "boundary_devissage_proof": {
            "filtration": (
                "0 subset F_metric subset F_carrier subset F_full, with "
                "successive outgoing quotients RW_metric, RW_carrier, spin_one"
            ),
            "endpoint_exactness": (
                "The certified pure-outgoing germ sequence preserves the "
                "inclusions and quotient maps at omega=1/2."
            ),
            "step_1": (
                "If a future-horizon-regular datum lies in ker(Tplus), its "
                "spin-one outgoing quotient is zero. Since A_out_1 is nonzero, "
                "the spin-one quotient solution vanishes, so the datum lies "
                "in the carrier spin-two subfiltration."
            ),
            "step_2": (
                "The carrier spin-two outgoing quotient is then zero. Since "
                "A_out_2 is nonzero, that quotient vanishes, leaving the "
                "metric spin-two submodule."
            ),
            "step_3": (
                "The remaining metric spin-two outgoing coefficient is again "
                "A_out_2 times a nonzero endpoint-frame unit, hence the "
                "metric solution vanishes."
            ),
            "kernel_conclusion": "ker(Tplus(1/2))={0}",
            "finite_dimensional_conclusion": (
                "Tplus(1/2) is a 3x3 map with zero kernel, hence belongs to "
                "GL(3,C)."
            ),
            "extension_reading": (
                "The nonsplit off-diagonal extension cannot create a kernel; "
                "the quotient factors are removed successively rather than "
                "diagonalizing the system."
            ),
        },
        "transport_free_outgoing_defect": {
            "definition": "O=Tminus^dagger*Gminus*Tminus-Hout",
            "stokes_identity": "O=Tplus^dagger*Gplus*Tplus",
            "determinant_identity": (
                "det(O)=det(Gplus)*abs(det(Tplus))^2"
            ),
            "Gplus_rank": 3,
            "Gplus_inertia_for_alpha_W_positive": {
                "positive": 1,
                "negative": 2,
                "zero": 0,
            },
            "det_O_nonzero_at_omega_half": True,
            "O_inertia_for_alpha_W_positive_at_omega_half": {
                "positive": 1,
                "negative": 2,
                "zero": 0,
            },
            "reading": (
                "Nondegeneracy and inertia follow exactly from Tplus "
                "invertibility, the nondegenerate outgoing Gram and Sylvester "
                "congruence. O is not numerically assembled in a raw frame."
            ),
        },
        "claim_flags": {
            "spin_one_outgoing_nonzero_at_omega_half": True,
            "spin_two_outgoing_nonzero_at_omega_half": True,
            "Tplus_invertible_at_omega_half": True,
            "full_outgoing_trace_space_populated_at_omega_half": True,
            "det_O_nonzero_at_omega_half": True,
            "O_inertia_1_2_0_at_omega_half": True,
            "explicit_Tplus_entries_certified": False,
            "outgoing_extension_amplitudes_certified": False,
            "whole_pilot_interval_outgoing_population_certified": False,
            "time_domain_or_quantum_claim": False,
        },
        "does_not_establish": [
            "invertibility of Tplus on an interval or at every positive frequency",
            "the explicit 3x3 Tplus entries or extension mixing amplitudes",
            "a raw-frame numerical determinant enclosure for O",
            "reflection nonvanishing away from omega=1/2",
            "uniform direct-integral bounds, limiting absorption or decay",
            "a QNM Smith selector or Green-resolvent pole",
            "positivity, particles, ghosts, CPT or quantum unitarity",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = produce()
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("certificate drift")
        print("PASS outgoing-population point-half reproduction")
        return 0
    CERTIFICATE.write_text(rendered)
    print(CERTIFICATE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
