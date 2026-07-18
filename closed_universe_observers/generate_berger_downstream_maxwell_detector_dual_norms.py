#!/usr/bin/env python3
"""Certify Berger detector dual norms and compose the recoil-tail constants."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_uniform_profile_sobolev_n1 import (
    _sqrt_upper,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json"
SCHEMA = PACKAGE / "schema/berger-downstream-maxwell-detector-dual-norms-v1.schema.json"
REPORT = PACKAGE / "reports/berger-downstream-maxwell-detector-dual-norms.md"
DEPENDENCIES = {
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "normalization": PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json",
    "clock_uniform": PACKAGE / "certificates/BERGER_CLOCK_UNIFORM_PROFILE_SOBOLEV_N1.json",
    "maxwell_energy": PACKAGE / "certificates/BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL.json",
    "massive_constant": PACKAGE / "certificates/BERGER_MASSIVE_RECOIL_FINITE_SLAB_ENERGY_CONSTANT.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_downstream_maxwell_detector_dual_norms.py",
    PACKAGE / "tests/test_berger_downstream_maxwell_detector_dual_norms.py",
    SCHEMA,
    REPORT,
]
EPSILON = Fraction(1, 128)
SQRT_DYADIC_BITS = 160


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _profile_rows(normalization: dict[str, Any]) -> list[dict[str, Any]]:
    audit = normalization["corrected_tail_audit"]
    radial_b_lower = Fraction(audit["radial_integral_B"]["lower"])
    radial_b_squared_upper = Fraction(audit["radial_integral_B_squared"]["upper"])

    # C_B3=4*pi*int r^2 B(r^2)dr.  The certified rational pi bounds give
    # C_B3 >= 12 I_B and C_B3,2 <= 16 I_B2.
    cb3_lower = 12 * radial_b_lower
    cb3_squared_profile_upper = 16 * radial_b_squared_upper
    common_norm_squared = EPSILON**-3 * cb3_squared_profile_upper / cb3_lower**2
    rows = []
    for detector_id, polarization, gram_polarization_upper in (
        ("D0", "axial dR0_1", Fraction(1)),
        ("D1", "transverse dR1_2", Fraction(40, 9)),
    ):
        norm_squared = gram_polarization_upper * common_norm_squared
        norm_upper = _sqrt_upper(norm_squared, SQRT_DYADIC_BITS)
        rows.append(
            {
                "detector_id": detector_id,
                "polarization": polarization,
                "epsilon": str(EPSILON),
                "J_times_polarization_norm_squared_upper": str(gram_polarization_upper),
                "spatial_profile_L2_norm_squared_upper": str(norm_squared),
                "spatial_profile_L2_norm_upper": str(norm_upper),
                "spatial_profile_L2_norm_upper_decimal": f"{float(norm_upper):.12e}",
                "detector_energy_dual_norm_upper": str(norm_upper),
            }
        )
    return rows


def _composition_rows(
    profile_rows: list[dict[str, Any]], massive: dict[str, Any]
) -> list[dict[str, Any]]:
    output = []
    for detector in profile_rows:
        dual = Fraction(detector["detector_energy_dual_norm_upper"])
        for channel in massive["switch_constants"]:
            h_sup = Fraction(channel["h_sup_upper"])
            inverse_squared = 3 * h_sup**2
            inverse = Fraction(8, 3) * h_sup
            output.append(
                {
                    "detector_id": detector["detector_id"],
                    "massive_channel": channel["switch_id"].replace("h_", "b_"),
                    "switch_id": channel["switch_id"],
                    "bare_tail_radius": (
                        f"(({dual * inverse_squared})/m_b^2+"
                        f"({dual * inverse})/m_b) E_A"
                    ),
                    "dual_times_m_inverse_squared_coefficient": str(dual * inverse_squared),
                    "dual_times_m_inverse_coefficient": str(dual * inverse),
                    "coupling_dressing": "multiply the bare channel by |g_c|^2 in the absolute-g^3 recoil loop",
                }
            )
    return output


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "chart": "EXACT_DETECTOR_RADII_FIXED",
        "normalization": "PROFILE_CHANGE_OF_VARIABLES_NORMALIZATION_REPAIRED",
        "clock_uniform": "CLOCK_UNIFORM_POLARIZED_DELTA1_PROFILE_NORM_EXPORTED",
        "maxwell_energy": "MAXWELL_ENERGY_GRAPH_NORM_TAIL_EXPORTED",
        "massive_constant": "MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    selected = values["chart"]["selected_profiles"]
    if selected["epsilon_0"] != "1/128" or selected["epsilon_1"] != "1/128":
        raise AssertionError("detector radii drifted")
    profiles = values["profiles"]["exact_detector_profiles"]
    if profiles["clock_rate_dTheta_dt"] != "3/4" or not profiles["unit_clock_integrals"]:
        raise AssertionError("detector clock convention drifted")
    if values["clock_uniform"]["profile_convention"]["amplitude_interval"] != ["82915/82944", "1"]:
        raise AssertionError("clock-uniform rod amplitude interval drifted")

    profile_rows = _profile_rows(values["normalization"])
    composition = _composition_rows(profile_rows, values["massive_constant"])
    if len(composition) != 4:
        raise AssertionError("expected two detector by two massive-channel bounds")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result certifies the "
        "downstream Maxwell-to-detector energy dual norms for both fixed "
        "Berger detector profiles. In physical time t, Theta=3t/4, so the "
        "factor 4/3 in dvol_gHat=(4/3)dTheta dSigma cancels the factor 3/4 "
        "in <dTheta wedge dR,F>; the unit clock bump leaves only the spatial "
        "L2 dual norm of rho J dR. The repaired identity J dSigma=d3R, "
        "validated B and B^2 radial integrals, and exact rod derivative "
        "matrix give rational squared-norm uppers and dyadic norm uppers for "
        "D0 and D1. Composing the unit Maxwell retarded energy estimate with "
        "the certified massive finite-slab constant yields all four symbolic "
        "bare tail radii D_a(3H_b^2/m_b^2+8H_b/(3m_b))E_A for m_b>0. This "
        "closes the factorwise analytic tail map, but it does not choose "
        "numerical masses or couplings, serialize the complete modewise "
        "recoil integrand, evaluate any of the four scalar intervals, certify "
        "a recoil-corrected determinant, restrict to the tangent cone, "
        "activate Bridge 3, promote finite-r/all-orders observer-morphism "
        "stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-downstream-maxwell-detector-dual-norms-v1",
        "result_id": "BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS",
        "setting_id": values["profiles"]["setting_id"],
        "claim_status": "TWO_DETECTOR_DUAL_NORMS_AND_FOUR_SYMBOLIC_RECOIL_TAIL_RADII_CERTIFIED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "clock_lapse_cancellation": {
            "clock_relation": "Theta=3t/4",
            "volume_relation": "dvol_gHat=(4/3)dTheta dSigma",
            "electric_pairing_relation": "<dTheta wedge dR,F>=(3/4)<dt wedge dR,F>",
            "product": "(4/3)*(3/4)=1",
            "consequence": "|Q_a[F]|<=||rho_a J_a dR_aI||_L2 sup_t||i_e0 F(t)||_L2",
        },
        "profile_norm_inputs": {
            "epsilon": str(EPSILON),
            "normalization_lower": "C_B3>=12 integral_0^1 r^2 B(r^2)dr",
            "squared_profile_integral_upper": "C_B3,2<=16 integral_0^1 r^2 B(r^2)^2dr",
            "measure_identity": "J dSigma=d3R",
            "polarization_bounds": "J|dR0_1|^2<=1 and J|dR1_2|^2<=40/9 on either translated support",
            "clock_uniform_amplitude_interval": ["82915/82944", "1"],
        },
        "detector_dual_norms": profile_rows,
        "retarded_energy_composition": {
            "maxwell_bound": "sup_t||d G_A,ret J||_energy <= integral||J(t)||_L2 dt",
            "massive_bound": "integral||delta(h_b K_b)||dt <= (3H_b^2/m_b^2+8H_b/(3m_b))E_A",
            "bare_scalar_bound": "|Q_a[d G_A,ret delta(h_b K_b)]| <= D_a(3H_b^2/m_b^2+8H_b/(3m_b))E_A",
            "mass_domain": "m_b>0",
            "four_channel_bounds": composition,
        },
        "route_disposition": {
            "downstream_Maxwell_detector_dual_norm": "CERTIFIED_FOR_BOTH_DETECTORS",
            "Maxwell_massive_detector_tail_composition": "CERTIFIED_FOR_SYMBOLIC_POSITIVE_MASSES",
            "complete_modewise_scalar_integrand": "OPEN",
            "four_scalar_recoil_intervals": "OPEN",
            "numerical_mass_coupling_specialization": "OPEN",
        },
        "mutation_results": [
            {
                "name": "retain_uncancelled_clock_lapse_factor",
                "detected": Fraction(4, 3) * Fraction(3, 4) == 1,
            },
            {
                "name": "identify_axial_and_transverse_rod_norms",
                "detected": Fraction(profile_rows[0]["J_times_polarization_norm_squared_upper"])
                != Fraction(profile_rows[1]["J_times_polarization_norm_squared_upper"]),
            },
            {
                "name": "drop_longitudinal_mass_inverse_squared_term",
                "detected": all(
                    Fraction(row["dual_times_m_inverse_squared_coefficient"]) > 0
                    for row in composition
                ),
            },
        ],
        "flags": {
            "DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORM_EXPORTED": True,
            "TWO_DETECTOR_ENERGY_DUAL_NORMS_EXPORTED": True,
            "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED": True,
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "STREAM_THE_COMPLETE_MODEWISE_INTEGRAND_INTO_FOUR_SYMBOLIC_RECOIL_INTERVALS_WITH_DECLARED_MASSES_COUPLINGS_AND_STOPPING_GOAL",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
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
        raise SystemExit("stale downstream Maxwell detector dual-norm certificate")
    print("BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
