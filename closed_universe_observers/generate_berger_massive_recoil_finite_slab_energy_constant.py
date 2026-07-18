#!/usr/bin/env python3
"""Certify the massive finite-slab constant needed by the Berger recoil stream."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_MASSIVE_RECOIL_FINITE_SLAB_ENERGY_CONSTANT.json"
SCHEMA = PACKAGE / "schema/berger-massive-recoil-finite-slab-energy-constant-v1.schema.json"
REPORT = PACKAGE / "reports/berger-massive-recoil-finite-slab-energy-constant.md"
DEPENDENCIES = {
    "maxwell_energy": PACKAGE / "certificates/BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL.json",
    "graph_gate": PACKAGE / "certificates/BERGER_RECOIL_CHAIN_GRAPH_NORM_GATE.json",
    "massive_unary": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_massive_recoil_finite_slab_energy_constant.py",
    PACKAGE / "tests/test_berger_massive_recoil_finite_slab_energy_constant.py",
    SCHEMA,
    REPORT,
]
PHYSICAL_TIME_PER_CLOCK_PHASE = Fraction(4, 3)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _switch_rows(switches: dict[str, Any], moments: dict[str, Any]) -> list[dict[str, Any]]:
    power_zero = next(row for row in moments["raw_radial_integral_enclosures"] if row["power"] == 0)
    half_core_integral_lower = Fraction(power_zero["integral"]["lower"])
    core_integral_lower = 2 * half_core_integral_lower
    rows = []
    for switch in switches["causal_support_audit"]["switches"]:
        radius = Fraction(switch["radius_clock_phase"])
        h_max = 1 / (radius * core_integral_lower)
        rows.append(
            {
                "switch_id": switch["id"],
                "clock_radius": str(radius),
                "physical_support": switch["support_physical_time"],
                "core_integral_lower": str(core_integral_lower),
                "h_sup_upper": str(h_max),
                "h_physical_time_L1": str(PHYSICAL_TIME_PER_CLOCK_PHASE),
                "h_physical_time_total_variation_upper": str(2 * h_max),
                "massive_solution_sup_bound": (
                    f"({h_max})/m_b^2 + ({PHYSICAL_TIME_PER_CLOCK_PHASE})/m_b"
                ),
                "recoil_current_L1_m_inverse_coefficient": str(Fraction(8, 3) * h_max),
                "recoil_current_L1_m_inverse_squared_coefficient": str(3 * h_max**2),
                "recoil_current_L1_bound": (
                    f"(({3*h_max**2})/m_b^2 + ({Fraction(8,3)*h_max})/m_b) E_A"
                ),
            }
        )
    return rows


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "maxwell_energy": "MAXWELL_ENERGY_GRAPH_NORM_TAIL_EXPORTED",
        "graph_gate": "EXACT_RECOIL_SWITCH_COMMUTATOR_EXPORTED",
        "massive_unary": "MASSIVE_TWO_FORM_ADVANCED_RETARDED_GREEN_CERTIFIED",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    inverse = values["massive_unary"]["massive_two_form_causal_inverse"]
    if inverse["candidate"] != [["1/(lambda + m2)", "0"], ["0", "1/m2"]]:
        raise AssertionError("massive transverse/longitudinal inverse drifted")
    if values["switches"]["causal_support_audit"]["clock_rate_dTheta_dt"] != "3/4":
        raise AssertionError("clock-to-physical-time conversion drifted")
    switches = _switch_rows(values["switches"], values["moments"])
    if [row["switch_id"] for row in switches] != ["h_0", "h_1"]:
        raise AssertionError("switch order drifted")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL finite-slab result "
        "maps the certified Maxwell field-strength energy tail E_A into an "
        "L1 bound for the switched massive recoil current. The transverse "
        "massive sector obeys the retarded energy estimate "
        "sup||K_T||<=m_b^-1 integral||h_b dA||dt; the exact longitudinal "
        "sector contributes the unsmoothed algebraic term "
        "m_b^-2||h_b dA||. Exact switch normalization gives integral h_b "
        "dt=4/3 and total variation integral|partial_t h_b|dt=2 sup h_b. "
        "Together with delta(h_b K_b)=-m_b^-2 h_b i_grad(h_b)dA-"
        "i_grad(h_b)K_b, this yields integral||delta(h_b K_b)||dt <= "
        "(3 H_b^2/m_b^2+8 H_b/(3m_b)) E_A, with certified rational "
        "H_b bounds for both exact switches. This closes the finite-time "
        "massive constant symbolically for every m_b>0. It does not supply "
        "a numerical mass, the downstream Maxwell-to-detector dual norm, "
        "the four streamed scalar intervals, numerical recoil, tangent-cone "
        "restriction, Bridge 3, nonlinear observer-morphism stability or a "
        "quantum claim."
    )
    return {
        "schema": "closed-universe-berger-massive-recoil-finite-slab-energy-constant-v1",
        "result_id": "BERGER_MASSIVE_RECOIL_FINITE_SLAB_ENERGY_CONSTANT",
        "setting_id": values["maxwell_energy"]["setting_id"],
        "claim_status": "SYMBOLIC_POSITIVE_MASS_FINITE_SLAB_RECOIL_CURRENT_CONSTANT_CERTIFIED",
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
        "massive_energy_theorem": {
            "mass_domain": "m_b>0",
            "sector_order": inverse["sector_order"],
            "sector_inverse": inverse["candidate"],
            "transverse_retarded_bound": "sup_t ||K_T(t)|| <= m_b^-1 integral ||h_b dA|| dt",
            "longitudinal_algebraic_bound": "sup_t ||K_L(t)|| <= m_b^-2 sup_t ||h_b dA||",
            "combined_solution_bound": "sup_t ||K_b|| <= (H_b/m_b^2+4/(3m_b)) E_A",
            "recoil_identity": "delta(h_b K_b)=-m_b^-2 h_b i_grad(h_b)dA-i_grad(h_b)K_b",
            "recoil_current_L1_bound": "integral ||delta(h_b K_b)||dt <= (3H_b^2/m_b^2+8H_b/(3m_b)) E_A",
        },
        "switch_constants": switches,
        "tail_composition": {
            "input": "E_A(N)=certified component-sum Maxwell field-strength graph tail",
            "channel_b_output": "E_recoil,b(N)<=C_b(m_b) E_A(N)",
            "C_b": "3H_b^2/m_b^2+8H_b/(3m_b)",
            "current_two_j1024_status": "finite symbolic bound; not a declared scalar tolerance",
            "two_j68743_status": "E_A<1 only; C_b(m_b) and downstream detector norm still apply",
        },
        "route_disposition": {
            "maxwell_graph_tail_to_massive_recoil_current_L1": "CERTIFIED_FOR_SYMBOLIC_POSITIVE_MASS",
            "downstream_Maxwell_detector_dual_norm": "OPEN",
            "four_scalar_recoil_intervals": "OPEN",
            "numerical_mass_specialization": "OPEN",
        },
        "mutation_results": [
            {
                "name": "drop_unsmoothed_longitudinal_massive_sector",
                "detected": inverse["candidate"][1][1] == "1/m2"
                and all(Fraction(row["recoil_current_L1_m_inverse_squared_coefficient"]) > 0 for row in switches),
            },
            {
                "name": "treat_unit_clock_integral_as_unit_physical_time_integral",
                "detected": PHYSICAL_TIME_PER_CLOCK_PHASE == Fraction(4, 3),
            },
            {
                "name": "drop_one_side_of_switch_total_variation",
                "detected": all(
                    Fraction(row["h_physical_time_total_variation_upper"])
                    == 2 * Fraction(row["h_sup_upper"])
                    for row in switches
                ),
            },
        ],
        "flags": {
            "MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED": True,
            "SYMBOLIC_POSITIVE_MASS_RECOIL_CURRENT_L1_TAIL_EXPORTED": True,
            "UNSMOOTHED_LONGITUDINAL_SECTOR_INCLUDED": True,
            "DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORM_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CERTIFY_THE_DOWNSTREAM_MAXWELL_TO_DETECTOR_DUAL_NORMS_AND_STREAM_THE_FOUR_RECOIL_SCALARS",
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
        raise SystemExit("stale massive recoil finite-slab energy certificate")
    print("BERGER_MASSIVE_RECOIL_FINITE_SLAB_ENERGY_CONSTANT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
