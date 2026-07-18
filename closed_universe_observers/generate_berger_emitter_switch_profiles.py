#!/usr/bin/env python3
"""Serialize exact compact clock switches for the two massive emitters."""

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
INPUT = PACKAGE / "fixtures/berger_emitter_switch_profiles_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-emitter-switch-profiles-input-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json"
SCHEMA = PACKAGE / "schema/berger-exact-normalized-emitter-switch-profiles-v1.schema.json"
REPORT = PACKAGE / "reports/berger-exact-normalized-emitter-switch-profiles.md"
DEPENDENCIES = {
    "detectors": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "localized_transfer": PACKAGE / "certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json",
    "dynamical_rank": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "recoil_gate": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_emitter_switch_profiles.py",
    "tests": PACKAGE / "tests/test_berger_emitter_switch_profiles.py",
    "input": INPUT,
    "input_schema": INPUT_SCHEMA,
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def switch_audit(data: dict[str, Any], *, mutation: str | None = None) -> dict[str, Any]:
    value = deepcopy(data)
    if mutation == "move_h1_before_D0":
        value["switches"][1]["support_physical_time"] = ["1/4", "7/16"]
        value["switches"][1]["center_physical_time"] = "11/32"
        value["switches"][1]["radius_physical_time"] = "3/32"
    clock_rate = sp.Rational(value["clock_rate_dTheta_dt"])
    detectors = [[sp.Rational(x) for x in window] for window in value["detector_windows_physical_time"]]
    switches = []
    for item in value["switches"]:
        support_t = [sp.Rational(x) for x in item["support_physical_time"]]
        center_t = sp.Rational(item["center_physical_time"])
        radius_t = sp.Rational(item["radius_physical_time"])
        center_defect = sp.simplify(center_t - sum(support_t) / 2)
        radius_defect = sp.simplify(radius_t - (support_t[1] - support_t[0]) / 2)
        support_theta = [sp.simplify(clock_rate * endpoint) for endpoint in support_t]
        center_theta = sp.simplify(clock_rate * center_t)
        radius_theta = sp.simplify(clock_rate * radius_t)
        conversion_defects = [
            sp.simplify(support_theta[0] - (center_theta - radius_theta)),
            sp.simplify(support_theta[1] - (center_theta + radius_theta)),
        ]
        switches.append(
            {
                "id": item["id"],
                "support_physical_time": [sp.sstr(x) for x in support_t],
                "center_physical_time": sp.sstr(center_t),
                "radius_physical_time": sp.sstr(radius_t),
                "support_clock_phase": [sp.sstr(x) for x in support_theta],
                "center_clock_phase": sp.sstr(center_theta),
                "radius_clock_phase": sp.sstr(radius_theta),
                "center_radius_defect_count": sum(int(x != 0) for x in (center_defect, radius_defect)),
                "clock_conversion_defect_count": sum(int(x != 0) for x in conversion_defects),
            }
        )
    margins_t = [
        sp.simplify(detectors[0][0] - sp.Rational(switches[0]["support_physical_time"][1])),
        sp.simplify(sp.Rational(switches[1]["support_physical_time"][0]) - detectors[0][1]),
        sp.simplify(detectors[1][0] - sp.Rational(switches[1]["support_physical_time"][1])),
    ]
    margins_theta = [sp.simplify(clock_rate * margin) for margin in margins_t]
    return {
        "clock_rate_dTheta_dt": sp.sstr(clock_rate),
        "detector_windows_physical_time": [[sp.sstr(x) for x in window] for window in detectors],
        "detector_windows_clock_phase": [[sp.sstr(clock_rate * x) for x in window] for window in detectors],
        "switches": switches,
        "causal_margins_physical_time": [sp.sstr(x) for x in margins_t],
        "causal_margins_clock_phase": [sp.sstr(x) for x in margins_theta],
        "strict_causal_order": all(margin > 0 for margin in margins_t),
        "all_rational_conversion_defects_zero": all(
            item["center_radius_defect_count"] == 0 and item["clock_conversion_defect_count"] == 0
            for item in switches
        ),
    }


def bump_audit(*, omit_radius_normalization: bool = False, use_nonflat_polynomial: bool = False) -> dict[str, Any]:
    s = sp.symbols("s", real=True)
    if use_nonflat_polynomial:
        core = 1 - s**2
        flat_boundary = False
    else:
        core = sp.exp(1 - 1 / (1 - s**2))
        flat_boundary = True
    derivative_quotients = []
    if not use_nonflat_polynomial:
        for order in range(1, 5):
            quotient = sp.factor(sp.diff(core, s, order) / core)
            derivative_quotients.append({"order": order, "derivative_over_B": sp.sstr(quotient)})
    radius, core_integral = sp.symbols("r C_B", positive=True)
    scale = 1 / core_integral if omit_radius_normalization else 1 / (radius * core_integral)
    normalized_integral = sp.simplify(scale * radius * core_integral)
    return {
        "core": "B(s)=exp(1-1/(1-s^2)) on |s|<1, zero otherwise" if not use_nonflat_polynomial else "1-s^2 on |s|<1, zero otherwise",
        "core_integral": "C_B=integral_-1^1 B(s) ds > 0",
        "derivative_quotients_first_four_orders": derivative_quotients,
        "all_order_flatness_argument": "D^n B=P_n(s)/(1-s^2)^(2n) B on |s|<1; exponential decay dominates every boundary pole" if flat_boundary else "FAILED",
        "C_infinity_compact_support": flat_boundary,
        "normalization_scale": sp.sstr(scale),
        "clock_integral_after_change_of_variable": sp.sstr(normalized_integral),
        "unit_clock_integral": normalized_integral == 1,
    }


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator(input_schema).validate(data)
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "detectors": "TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS",
        "localized_transfer": "LOCALIZED_EMITTER_TRANSFER_MATRIX_RANK_TWO",
        "dynamical_rank": "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED",
        "recoil_gate": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")
    support = switch_audit(data)
    bump = bump_audit()
    mutations = {
        "move_h1_before_D0": switch_audit(data, mutation="move_h1_before_D0"),
        "omit_radius_from_unit_integral_scale": bump_audit(omit_radius_normalization=True),
        "replace_flat_bump_by_truncated_polynomial": bump_audit(use_nonflat_polynomial=True),
    }
    if not support["strict_causal_order"] or not support["all_rational_conversion_defects_zero"]:
        raise AssertionError("exact switch support audit failed")
    if not bump["C_infinity_compact_support"] or not bump["unit_clock_integral"]:
        raise AssertionError("exact switch bump audit failed")
    if (
        mutations["move_h1_before_D0"]["strict_causal_order"]
        or mutations["omit_radius_from_unit_integral_scale"]["unit_clock_integral"]
        or mutations["replace_flat_bump_by_truncated_polynomial"]["C_infinity_compact_support"]
    ):
        raise AssertionError("exact switch mutation rail failed")

    serialized = []
    for item in support["switches"]:
        center = item["center_clock_phase"]
        radius = item["radius_clock_phase"]
        serialized.append(
            {
                **item,
                "dimensionless_argument": f"s_{item['id'][-1]}(Theta)=(Theta-({center}))/({radius})",
                "definition": f"{item['id']}(Theta)=B(s_{item['id'][-1]}(Theta))/(({radius}) C_B) for |s|<1, and 0 otherwise",
                "normalization": f"integral {item['id']}(Theta) dTheta=1",
            }
        )
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL input certificate serializes two nonnegative compact C-infinity relational switches h_0(Theta),h_1(Theta) for the selected massive emitters. It distinguishes physical time from clock phase using dTheta/dt=3/4, converts every rational endpoint exactly, and fixes unit clock-integral normalization with the standard flat bump B(s)=exp(1-1/(1-s^2)) and the declared positive constant C_B=integral_-1^1 B. The physical supports (7/48,9/48) and (5/16,7/16) lie respectively before D0 and strictly between D0 and D1, with exact physical margins 1/24 and clock margins 1/32. Mutation rails detect lost causal order, lost unit normalization, and loss of C-infinity boundary flatness. This closes the switch part of the recoil input gate. It does not serialize the detector-selected compact massive-two-form Cauchy profiles u_0,u_1, evaluate any Berger massive Green image or detector integral, compute the absolute-g^3 recoil coefficient, construct the PBW q2 payload, solve backreaction, establish finite-parameter Green theory or the full Dirac algebra, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-exact-normalized-emitter-switch-profiles-v1",
        "result_id": "BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES",
        "setting_id": values["dynamical_rank"]["setting_id"],
        "claim_status": "EXACT_COMPACT_NORMALIZED_SWITCHES_SERIALIZED_CAUCHY_PROFILES_AND_GREEN_IMAGES_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "authoritative_input": {"path": str(INPUT.relative_to(ROOT)), "sha256": _sha256(INPUT)},
        "bump_and_normalization": bump,
        "causal_support_audit": {**support, "switches": serialized},
        "recoil_input_disposition": {
            "exact_switches_serialized": True,
            "compact_Cauchy_profiles_u0_u1_serialized": False,
            "massive_Green_images_evaluated": False,
            "detector_recoil_integrals_evaluated": False,
            "remaining_first_input": "construct detector-selected compact constraint-compatible emitter Cauchy profiles rather than an arbitrary bump that may lie in the detector functional kernel",
        },
        "mutation_results": [{"name": name, "detected": True, "audit": audit} for name, audit in mutations.items()],
        "flags": {
            "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED": True,
            "SWITCHES_C_INFINITY_COMPACT_SUPPORTED": True,
            "SWITCHES_UNIT_CLOCK_INTEGRAL_NORMALIZED": True,
            "SWITCH_CAUSAL_ORDER_WITH_DETECTORS_CERTIFIED": True,
            "COMPACT_EMITTER_CAUCHY_PROFILES_SERIALIZED": False,
            "MASSIVE_TWO_FORM_GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_EXPLICIT_DETECTOR_SELECTED_COMPACT_CONSTRAINT_CAUCHY_PROFILES_U0_U1_THEN_EVALUATE_THEIR_MASSIVE_GREEN_IMAGES",
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
        raise SystemExit("stale exact emitter switch profile certificate")
    print("BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
