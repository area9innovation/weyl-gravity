#!/usr/bin/env python3
"""Assemble the outgoing-population cell theorem from certified inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCES = {
    "scalar_reflection_cell": ROOT
    / "black_hole_programme/phase3/axial_scalar_reflection_cell_half_v1"
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


def build() -> dict:
    inputs = {name: load(path) for name, path in SOURCES.items()}
    reflection = inputs["scalar_reflection_cell"]
    triangular = inputs["triangular_factorization"]
    devissage = inputs["boundary_devissage"]
    gram = inputs["outgoing_gram"]
    stokes = inputs["transport_free_stokes"]

    interval = reflection["scope"]["frequency_interval"]
    assert interval == ["0.49995", "0.50005"]
    flags = reflection["claim_flags"]
    assert flags["spin_one_reflection_nonzero_on_cell"]
    assert flags["spin_two_reflection_nonzero_on_cell"]
    assert flags["full_declared_cell_certified"]
    assert triangular["carrier_exact_sequence"]["exact_sequence"] == (
        "0 -> M_RW -> M_A4 -> M_x -> 0"
    )
    outgoing_germs = devissage["local_boundary_maps"][
        "pure_outgoing_infinity"
    ]
    assert outgoing_germs["germ_sequence"].startswith(
        "0 -> O_RW_metric -> O_full"
    )
    assert outgoing_germs["metric_spin_two_outgoing_amplitude"] == "1/2"
    assert outgoing_germs["carrier_spin_two_outgoing_amplitude"] == "1"
    assert outgoing_germs["spin_one_outgoing_amplitude"] == "-2*I*omega"
    gplus = gram["endpoint_grams"]["Iplus"]["classification"]
    assert gplus["rank"] == 3 and gplus["radical_dimension"] == 0
    assert gplus["inertia_for_alpha_W_positive"] == {
        "negative": 2,
        "positive": 1,
        "zero": 0,
    }
    assert stokes["tier_A_transport_free_determinant"][
        "determinant_equivalence"
    ].startswith("det(O)=det(Gplus)*abs(det(Tplus))^2")

    getcontext().prec = 80
    l1 = Decimal(
        reflection["certified_lower_bounds"]["spin_1"]["abs_A_out_lower"]
    )
    l2 = Decimal(
        reflection["certified_lower_bounds"]["spin_2"]["abs_A_out_lower"]
    )
    factor_det_lower = l2 * l2 * l1
    factor_det_squared_lower = factor_det_lower * factor_det_lower
    return {
        "schema": "phase3-axial-outgoing-population-cell-half-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF",
        "status": "VALIDATED_FULL_OUTGOING_POPULATION_ON_REAL_CELL",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "frequency_interval": interval,
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
                "The product bounds A_out_2^2*A_out_1 uniformly in the "
                "intrinsic triangular factor frame. It is not a raw "
                "six-state endpoint determinant bound."
            ),
        },
        "boundary_devissage_proof": {
            "filtration": (
                "0 subset F_metric subset F_carrier subset F_full, with "
                "successive pure-outgoing quotients RW_metric, RW_carrier, "
                "spin_one"
            ),
            "endpoint_units": (
                "The metric and carrier outgoing frame factors are 1/2 and "
                "1; the spin-one factor is -2*I*omega, which is nonzero "
                "throughout the positive real cell."
            ),
            "uniform_kernel_conclusion": (
                "For every omega in [0.49995,0.50005], successive quotient "
                "projection removes spin one, carrier spin two and metric "
                "spin two, so ker(Tplus(omega))={0}."
            ),
            "finite_dimensional_conclusion": (
                "Tplus(omega) is a 3x3 map with zero kernel at every "
                "frequency in the cell, hence belongs to GL(3,C) pointwise "
                "throughout the cell."
            ),
        },
        "transport_free_outgoing_defect": {
            "definition": "O=Tminus^dagger*Gminus*Tminus-Hout",
            "stokes_identity": "O=Tplus^dagger*Gplus*Tplus",
            "determinant_identity": (
                "det(O)=det(Gplus)*abs(det(Tplus))^2"
            ),
            "uniform_conclusion": (
                "det(O(omega)) is nonzero and inertia(O(omega))=(1,2,0) "
                "for every omega in the declared cell."
            ),
        },
        "analytic_corollaries": {
            "hypothesis": (
                "The scalar outgoing Jost coefficients and the typed "
                "factor connection are holomorphic in connected complex "
                "neighbourhoods of every positive real frequency, away "
                "from the separate threshold omega=0."
            ),
            "exceptional_set": (
                "The positive-real zeros of A_out_2 and A_out_1 form a "
                "locally finite set Zplus. Tplus is invertible on "
                "(0,infinity) minus Zplus, an open dense full-measure set."
            ),
            "certified_cell_multiplier": (
                "On I0=[0.49995,0.50005], multiplication by Tplus is a "
                "bounded isomorphism of L2(I0;C^3). Thus every L2 outgoing "
                "packet in the cell has a unique horizon-regular preimage."
            ),
            "arbitrary_compact_band": (
                "On every compact I contained in (0,infinity), "
                "multiplication by Tplus is injective with dense range. "
                "It is a bounded isomorphism when I contains no point of "
                "Zplus; if I contains an actual reflection zero, its range "
                "is dense and nonclosed."
            ),
            "band_limited_stokes": (
                "On I0 the pointwise Stokes identity integrates to an "
                "exact pseudo-isometry of the band-limited coefficient "
                "spaces. This is not a full time-domain stability theorem."
            ),
        },
        "claim_flags": {
            "Tplus_invertible_on_declared_cell": True,
            "full_outgoing_trace_space_populated_on_declared_cell": True,
            "det_O_nonzero_on_declared_cell": True,
            "O_inertia_1_2_0_on_declared_cell": True,
            "generic_positive_real_outgoing_population_off_discrete_set": True,
            "cell_L2_multiplier_bounded_isomorphism": True,
            "compact_positive_band_dense_range": True,
            "whole_pilot_interval_outgoing_population_certified": False,
            "absence_of_positive_real_reflection_zeros_certified": False,
            "uniform_full_positive_axis_inverse_bound_certified": False,
            "explicit_Tplus_entries_certified": False,
            "outgoing_extension_amplitudes_certified": False,
            "QNM_or_time_domain_claim": False,
        },
        "does_not_establish": [
            "absence or location of isolated reflection zeros outside the declared cell",
            "pointwise invertibility of Tplus at every frequency of the complete pilot interval",
            "the explicit 3x3 Tplus entries or extension mixing amplitudes",
            "a raw-frame numerical determinant enclosure for O",
            "a QNM Smith selector or Green-resolvent pole",
            "a uniform inverse bound on the full positive real axis",
            "limiting absorption, full time-domain boundedness or decay",
            "positivity, particles, ghosts, CPT or quantum unitarity",
        ],
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render(build())
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != content:
            raise RuntimeError("certificate drift")
        print("PASS outgoing-population cell-half reproduction")
        return 0
    CERTIFICATE.write_text(content)
    RECEIPT.write_text(
        render(
            {
                "schema": (
                    "phase3-axial-outgoing-population-cell-half-receipt-v1"
                ),
                "certificate": CERTIFICATE.name,
                "certificate_sha256": sha256(CERTIFICATE),
                "commands": [
                    (
                        "python3 -m black_hole_programme.phase3."
                        "axial_outgoing_population_cell_half_v1.produce "
                        "--check"
                    ),
                    (
                        "python3 -m black_hole_programme.phase3."
                        "axial_outgoing_population_cell_half_v1.verify"
                    ),
                    (
                        "python3 -m unittest -v black_hole_programme.phase3."
                        "axial_outgoing_population_cell_half_v1."
                        "test_population_cell"
                    ),
                ],
                "claim_boundary": (
                    "full outgoing population and a bounded L2 multiplier "
                    "isomorphism on [0.49995,0.50005]; analyticity gives "
                    "generic positive-real population off a locally finite "
                    "exceptional set and dense range on compact bands, but "
                    "no all-frequency pointwise, explicit-amplitude, QNM "
                    "or full time-domain claim"
                ),
            }
        )
    )
    print("PASS full outgoing population on declared real cell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
