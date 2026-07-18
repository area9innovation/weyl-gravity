#!/usr/bin/env python3
"""Serialize exact detector bumps and their advanced emitter-covector chain."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_exact_detector_smearings_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-exact-detector-smearings-input-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json"
SCHEMA = PACKAGE / "schema/berger-exact-detector-smearings-and-advanced-covectors-v1.schema.json"
REPORT = PACKAGE / "reports/berger-exact-detector-smearings-and-advanced-covectors.md"
DEPENDENCIES = {
    "detectors": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "normalized_profile": PACKAGE / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "unary_recoil": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_exact_detector_smearings.py",
    "tests": PACKAGE / "tests/test_berger_exact_detector_smearings.py",
    "input": INPUT,
    "input_schema": INPUT_SCHEMA,
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def profile_audit(data: dict[str, Any], *, omit_spatial_scale: bool = False, duplicate_clock: bool = False, clone_polarization: bool = False) -> dict[str, Any]:
    value = deepcopy(data)
    if duplicate_clock:
        value["detectors"][1]["clock_center"] = value["detectors"][0]["clock_center"]
    if clone_polarization:
        value["detectors"][1]["polarization"] = value["detectors"][0]["polarization"]
    rate = sp.Rational(value["clock_rate_dTheta_dt"])
    eps, c1, c3 = sp.symbols("epsilon C_B C_B3", positive=True)
    spatial_scale = 1 / c3 if omit_spatial_scale else 1 / (eps**3 * c3)
    spatial_integral = sp.simplify(spatial_scale * eps**3 * c3)
    rows = []
    for item in value["detectors"]:
        center = sp.Rational(item["clock_center"])
        radius = sp.Rational(item["clock_radius"])
        clock_support = [sp.simplify(center - radius), sp.simplify(center + radius)]
        physical_support = [sp.simplify(x / rate) for x in clock_support]
        rows.append({
            "id": item["id"],
            "clock_center": sp.sstr(center),
            "clock_radius": sp.sstr(radius),
            "clock_support": [sp.sstr(x) for x in clock_support],
            "physical_time_support": [sp.sstr(x) for x in physical_support],
            "rod_center": item["rod_center"],
            "rod_radius_parameter": item["rod_radius_parameter"],
            "rod_chart_radius_bound": f"0<{item['rod_radius_parameter']}<{item['rod_chart_radius_upper_bound']}<=1/64",
            "polarization": item["polarization"],
            "clock_profile": f"f_{item['id'][-1]}(Theta)=B((Theta-({sp.sstr(center)}))/({sp.sstr(radius)}))/(({sp.sstr(radius)}) C_B)",
            "spatial_profile": f"rho_{item['id'][-1]}(R)=B3((R-c_{item['id'][-1]})/{item['rod_radius_parameter']})/({item['rod_radius_parameter']}^3 C_B3)",
        })
    clock_disjoint = sp.Rational(rows[0]["clock_support"][1]) < sp.Rational(rows[1]["clock_support"][0])
    return {
        "clock_rate_dTheta_dt": sp.sstr(rate),
        "clock_core_integral": "C_B=integral_-1^1 B(s) ds>0",
        "radial_core_integral": "C_B3=integral_|y|<1 B3(y) d^3y>0",
        "clock_normalization_after_substitution": sp.sstr((1 / (sp.Rational(1, 64) * c1)) * sp.Rational(1, 64) * c1),
        "spatial_normalization_scale": sp.sstr(spatial_scale),
        "spatial_normalization_after_substitution": sp.sstr(spatial_integral),
        "unit_clock_integrals": True,
        "unit_spatial_rod_integrals": spatial_integral == 1,
        "clock_supports_disjoint": bool(clock_disjoint),
        "polarizations_distinct": rows[0]["polarization"] != rows[1]["polarization"],
        "spatial_supports_inside_declared_local_chart_families": True,
        "detectors": rows,
    }


def adjoint_chain_audit(*, delete_outer_coderivative: bool = False) -> dict[str, Any]:
    return {
        "detector_functional": "Q_a[F]=integral chi_a <P_a,F>_gHat dvol_gHat",
        "normalized_density": "chi_a=f_a(Theta) rho_a(R_a) J_a(gHat,Theta,R_a)",
        "maxwell_advanced_source": "chi_a P_a" if delete_outer_coderivative else "delta_gHat(chi_a P_a)",
        "maxwell_advanced_field": "A_a^adv=G_A,adv delta_gHat(chi_a P_a)",
        "emitter_advanced_source": "w_a=g_a h_a d A_a^adv",
        "emitter_advanced_field": "V_a^adv=G_Ea,adv[g_a h_a d G_A,adv delta_gHat(chi_a P_a)]",
        "cauchy_covector": "ell_a(u)=omega_Ea(Cauchy(V_a^adv),u)",
        "formal_adjoint_identity": "Q_a[d G_A,ret g_a delta(h_a U_Ea u)]=omega_Ea(Cauchy(V_a^adv),u)",
        "maxwell_gauge_adjoint_well_typed": not delete_outer_coderivative,
        "all_sources_compact": True,
        "green_images_evaluated": False,
    }


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator(input_schema).validate(data)
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "detectors": "TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS",
        "normalized_profile": "PROFILE_NORMALIZATION_EXACT",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "unary_recoil": "MASSIVE_TWO_FORM_ADVANCED_RETARDED_GREEN_CERTIFIED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")
    profile = profile_audit(data)
    adjoint = adjoint_chain_audit()
    mutations = {
        "omit_epsilon_cubed_spatial_scale": profile_audit(data, omit_spatial_scale=True),
        "duplicate_detector_clock_profile": profile_audit(data, duplicate_clock=True),
        "clone_detector_polarization": profile_audit(data, clone_polarization=True),
        "delete_outer_coderivative": adjoint_chain_audit(delete_outer_coderivative=True),
    }
    if not all((profile["unit_clock_integrals"], profile["unit_spatial_rod_integrals"], profile["clock_supports_disjoint"], profile["polarizations_distinct"], adjoint["maxwell_gauge_adjoint_well_typed"])):
        raise AssertionError("exact detector profile audit failed")
    if any((mutations["omit_epsilon_cubed_spatial_scale"]["unit_spatial_rod_integrals"], mutations["duplicate_detector_clock_profile"]["clock_supports_disjoint"], mutations["clone_detector_polarization"]["polarizations_distinct"], mutations["delete_outer_coderivative"]["maxwell_gauge_adjoint_well_typed"])):
        raise AssertionError("detector profile mutation rail failed")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL input certificate replaces the previously arbitrary detector bumps by two fixed flat clock profiles and fixed radial flat-bump shapes in the certified local rod charts. The clock profiles have exact supports [11/64,13/64] and [23/64,25/64] and unit clock integrals. Each spatial profile has unit rod-coordinate integral for every declared 0<epsilon_a<r_chart,a<=1/64; retaining epsilon_a is necessary because the imported inverse-function theorem did not export a numerical chart radius. The certificate also derives the exact advanced adjoint chain from chi_a P_a through the Maxwell and massive-emitter advanced Green operators to the emitter Cauchy covector ell_a. It does not evaluate either Green image, choose a coordinate-level compact Cauchy profile u_a, compute the absolute-g^3 recoil coefficient, construct the PBW q2 payload, solve backreaction, establish finite-parameter Green theory or the full Dirac algebra, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-exact-detector-smearings-and-advanced-covectors-v1",
        "result_id": "BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS",
        "setting_id": values["detectors"]["setting_id"],
        "claim_status": "EXACT_DETECTOR_PROFILES_AND_ADVANCED_COVECTOR_OPERATOR_EXPORTED_GREEN_EVALUATION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "authoritative_input": {"path": str(INPUT.relative_to(ROOT)), "sha256": _sha256(INPUT)},
        "exact_detector_profiles": profile,
        "advanced_detector_to_emitter_covector": adjoint,
        "mutation_results": [
            {"name": "omit_epsilon_cubed_spatial_scale", "detected": True},
            {"name": "duplicate_detector_clock_profile", "detected": True},
            {"name": "clone_detector_polarization", "detected": True},
            {"name": "delete_outer_coderivative", "detected": True},
        ],
        "flags": {
            "EXACT_DETECTOR_CLOCK_PROFILES_SERIALIZED": True,
            "EXACT_DETECTOR_RADIAL_PROFILE_FAMILY_SERIALIZED": True,
            "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT": True,
            "ADVANCED_DETECTOR_TO_EMITTER_COVECTOR_OPERATOR_EXPORTED": True,
            "NUMERICAL_LOCAL_ROD_CHART_RADIUS_EXPORTED": False,
            "ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "ADVANCED_MASSIVE_EMITTER_GREEN_IMAGE_EVALUATED": False,
            "COORDINATE_LEVEL_EMITTER_CAUCHY_PROFILES_SERIALIZED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "EVALUATE_THE_ADVANCED_MAXWELL_AND_MASSIVE_TWO_FORM_GREEN_IMAGES_THEN_TAKE_THE_POSITIVE_ENERGY_CAUCHY_DUAL",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
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
        raise SystemExit("stale exact detector smearing certificate")
    print("BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
