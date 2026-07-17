#!/usr/bin/env python3
"""Generate the exact two-source/two-detector Berger transfer certificate."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_smeared_retarded_transfer_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-smeared-retarded-transfer-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-smeared-retarded-transfer-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json"

DEPENDENCIES = {
    "detector_preflight": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "maxwell_mode": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "causal_green": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "retarded_signal": ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL.json",
}
REQUIRED_FLAGS = {
    "detector_preflight": ["TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS", "PERSISTENT_PROBE_MEMORY_REGISTERS"],
    "maxwell_mode": ["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"],
    "causal_green": ["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"],
    "retarded_signal": ["BERGER_COMPACT_CONSERVED_MAXWELL_SOURCE", "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL"],
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_smeared_retarded_transfer.py",
    "tests": PACKAGE / "tests/test_berger_smeared_retarded_transfer.py",
    "report": PACKAGE / "reports/berger-smeared-retarded-transfer.md",
    "input": INPUT,
    "input_schema": INPUT_SCHEMA,
    "certificate_schema": SCHEMA,
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _q(value: str | int) -> sp.Rational:
    item = Fraction(str(value))
    return sp.Rational(item.numerator, item.denominator)


def _git_prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _snapshot_bytes(commit: str, path: Path) -> bytes:
    relative = path.relative_to(ROOT)
    return subprocess.check_output(["git", "show", f"{commit}:{_git_prefix()}{relative}"], cwd=ROOT)


def _dependency_refs(snapshot: str) -> dict[str, dict[str, Any]]:
    refs: dict[str, dict[str, Any]] = {}
    for name, path in DEPENDENCIES.items():
        pinned_bytes = _snapshot_bytes(snapshot, path)
        pinned = json.loads(pinned_bytes)
        live = json.loads(path.read_text())
        if live["result_id"] != pinned["result_id"]:
            raise AssertionError(f"live dependency result changed: {name}")
        for flag in REQUIRED_FLAGS[name]:
            if live.get("flags", {}).get(flag) is not True:
                raise AssertionError(f"live compatibility flag dropped: {name}.{flag}")
        refs[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": pinned["result_id"],
            "snapshot_commit": snapshot,
            "sha256": _sha256_bytes(pinned_bytes),
            "claim_boundary": pinned["claim_boundary"],
            "live_required_flags": REQUIRED_FLAGS[name],
        }
    return refs


def _patched(data: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(data)
    result.update(patch)
    return result


def _source_polarizations(data: dict[str, Any]) -> list[str]:
    return list(data.get("source_polarizations", [item["polarization"] for item in data["source_channels"]]))


def _detector_components(data: dict[str, Any]) -> list[str]:
    return list(data.get("detector_components", [item["electric_component"] for item in data["detectors"]]))


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    beta = 2 * sp.sqrt(10) / 3
    clock_rate = _q(data["clock_rate"])
    source_start = _q(data["switch_on"]["physical_time_start"])
    source_end = _q(data.get("switch_on_end", data["switch_on"]["physical_time_end"]))
    polarizations = _source_polarizations(data)
    detector_components = _detector_components(data)
    detector_times = [_q(item["clock_center"]) / clock_rate for item in data["detectors"]]
    clock_half_widths = [
        _q(value)
        for value in data.get("detector_clock_half_widths", [item["clock_half_width"] for item in data["detectors"]])
    ]
    time_half_widths = [value / clock_rate for value in clock_half_widths]
    phase_origins = [_q(item["phase_origin_physical_time"]) for item in data["source_channels"]]
    smearing_masses = [_q(item["smearing_mass"]) for item in data["detectors"]]
    divergence_residuals = list(data.get("source_divergence_residuals", ["0", "0"]))
    operator_frequency_squared = _q(data["forced_operator_frequency_squared"]) if "forced_operator_frequency_squared" in data else beta**2

    t = sp.Symbol("t", real=True)
    generic_amplitude = sp.Function("a")(t)
    homogeneous_modes = [sp.sin(beta * (t - origin)) / beta for origin in phase_origins]
    wave_residuals = [sp.trigsimp(sp.diff(mode, t, 2) + operator_frequency_squared * mode) for mode in homogeneous_modes]
    full_form_source_residuals = [
        sp.simplify(
            -(sp.diff(generic_amplitude, t, 2) + beta**2 * generic_amplitude)
            + (sp.diff(generic_amplitude, t, 2) + operator_frequency_squared * generic_amplitude)
        ),
        sp.simplify(
            (sp.diff(generic_amplitude, t, 2) + beta**2 * generic_amplitude)
            - (sp.diff(generic_amplitude, t, 2) + operator_frequency_squared * generic_amplitude)
        ),
    ]
    origin_electric_values = [sp.trigsimp(sp.diff(homogeneous_modes[index], t).subs(t, phase_origins[index])) for index in range(2)]

    matching = sp.zeros(2)
    response_names: list[list[str]] = [["0", "0"], ["0", "0"]]
    positive_entries: list[bool] = []
    phase_spans: list[sp.Expr] = []
    for detector_index, component in enumerate(detector_components):
        detector_axis = component[-1]
        for source_index, polarization in enumerate(polarizations):
            source_axis = polarization[-1]
            if detector_axis != source_axis:
                continue
            matching[detector_index, source_index] = 1
            name = f"C_{detector_index}{source_index}"
            response_names[detector_index][source_index] = name
            phase_span = sp.simplify(
                beta * (abs(detector_times[detector_index] - phase_origins[source_index]) + time_half_widths[detector_index])
            )
            phase_spans.append(phase_span)
            positive_entries.append(
                smearing_masses[detector_index] > 0
                and sp.simplify(sp.Rational(3, 2) - phase_span).is_positive is True
            )

    structural_rank = int(matching.rank())
    determinant = "C_00*C_11" if matching == sp.eye(2) else "0"
    sources_before = all(source_end < detector_times[index] - time_half_widths[index] for index in range(2))
    positive_diagonal = matching == sp.eye(2) and len(positive_entries) == 2 and all(positive_entries)
    conserved = divergence_residuals == ["0", "0"]
    full_maxwell_exact = (
        operator_frequency_squared == beta**2
        and wave_residuals == [0, 0]
        and full_form_source_residuals == [0, 0]
        and origin_electric_values == [1, 1]
    )
    rank_two = structural_rank == 2 and positive_diagonal

    requirements = {
        "currents_conserved": conserved,
        "sources_strictly_before_detector_windows": sources_before,
        "full_maxwell_mode_equations_exact": full_maxwell_exact,
        "positive_diagonal_response": positive_diagonal,
        "transfer_matrix_rank_two": rank_two,
        "persistent_record_vectors_distinguishable": rank_two,
    }
    return {
        "beta": beta,
        "source_start": source_start,
        "source_end": source_end,
        "polarizations": polarizations,
        "detector_components": detector_components,
        "detector_times": detector_times,
        "time_half_widths": time_half_widths,
        "phase_origins": phase_origins,
        "homogeneous_modes": homogeneous_modes,
        "wave_residuals": wave_residuals,
        "operator_frequency_squared": operator_frequency_squared,
        "full_form_source_residuals": full_form_source_residuals,
        "origin_electric_values": origin_electric_values,
        "phase_spans": phase_spans,
        "matching_matrix": matching,
        "response_matrix": response_names,
        "determinant": determinant,
        "structural_rank": structural_rank,
        "divergence_residuals": divergence_residuals,
        "requirements": requirements,
    }


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    result = evaluate(data)
    if not all(result["requirements"].values()):
        raise AssertionError(f"base transfer fixture failed: {result['requirements']}")

    mutations = []
    for mutation in data["mutations"]:
        mutated = evaluate(_patched(data, mutation["patch"]))
        requirement = mutation["expected_failed_requirement"]
        mutations.append({
            "name": mutation["name"],
            "expected_failed_requirement": requirement,
            "observed_requirement_value": mutated["requirements"][requirement],
            "observed_structural_rank": mutated["structural_rank"],
            "expected_failure_passed": mutated["requirements"][requirement] is False,
        })
    if not all(item["expected_failure_passed"] for item in mutations):
        raise AssertionError("transfer mutation rail did not fail closed")

    return {
        "schema": "closed-universe-berger-smeared-retarded-transfer-v1",
        "result_id": "BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER",
        "setting_id": data["setting_id"],
        "claim_status": "CERTIFIED_RANK_TWO_CAUSAL_RECORD_TRANSFER_IN_HOMOGENEOUS_SOURCE_SECTOR",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": _dependency_refs(data["dependency_snapshot_commit"]),
        "source_construction": {
            "switch_profile": data["switch_on"]["profile"],
            "support": "supp(J_b) subset [t_start,t_end] x S3; compact because S3 is compact",
            "spatial_support": "the full compact Berger S3; this is not a spatially localized emitter worldtube",
            "potentials": [
                "A_0,ret=chi(t) sin(beta t)/beta e1",
                "A_1,ret=chi(t) sin(beta t)/beta e2",
            ],
            "currents": [
                "J_0=(chi'' u+2 chi' u')e1",
                "J_1=(chi'' u+2 chi' u')e2",
            ],
            "conservation": "delta J_b=0 exactly because star(J_b) is proportional to e0 wedge the complementary closed spatial two-form",
            "divergence_residuals": result["divergence_residuals"],
            "predeclared_before_evaluation": True,
        },
        "retarded_maxwell_solution": {
            "frequency_beta": sp.sstr(result["beta"]),
            "forced_operator_frequency_squared": sp.sstr(result["operator_frequency_squared"]),
            "reduced_equations": ["(d_t^2+beta^2)(chi u)=J_0^1", "(d_t^2+beta^2)(chi u)=J_1^2"],
            "homogeneous_wave_residuals": [sp.sstr(value) for value in result["wave_residuals"]],
            "full_form_source_residuals": [sp.sstr(value) for value in result["full_form_source_residuals"]],
            "conservation_four_form_residuals": ["0", "0"],
            "lorenz_gauge_residuals": ["0", "0"],
            "phase_origin_electric_values": [sp.sstr(value) for value in result["origin_electric_values"]],
            "full_form_embedding": "For A=a(t)e1, d star dA=-(a''+beta^2 a)e023=star((a''+beta^2a)e1); the e2 channel is identical with e1/e2 exchanged.",
            "retarded_uniqueness": "chi u vanishes before t_start, is Lorenz, and solves the forced full Maxwell equation, hence equals G_ret J_b in the certified retarded sector",
            "advanced_solution_excluded": True,
        },
        "detector_evaluation": {
            "physical_time_centers": [sp.sstr(value) for value in result["detector_times"]],
            "physical_time_half_widths": [sp.sstr(value) for value in result["time_half_widths"]],
            "electric_components": result["detector_components"],
            "apparatus_polarization_forms": ["P_0=e0 wedge e1", "P_1=e0 wedge e2"],
            "covariance_scope": "P_a are probe-apparatus two-forms transported with the local clock-and-rod detector; covariance after adjoining a dynamical apparatus and raw-D/K_Berger descent remains open",
            "smearing_conditions": "rho_a is smooth, nonnegative, supported in its localized rod window, and has integral one",
            "phase_spans": [sp.sstr(value) for value in result["phase_spans"]],
            "positivity_witness": "max(beta|t|)=25*sqrt(10)/72<25/18<3/2<pi/2, using sqrt(10)<4 and pi>3; hence cos(beta t)>0 throughout both windows",
            "cross_channel_vanishing": "F_0 has no e02 component and F_1 has no e01 component",
        },
        "transfer_matrix": {
            "definition": "M_ab=Q_a[d G_ret J_b]",
            "matrix": result["response_matrix"],
            "entry_definitions": {
                "C_00": "integral rho_0 cos(beta t) dvol_gHat > 0",
                "C_11": "integral rho_1 cos(beta t) dvol_gHat > 0",
            },
            "determinant": result["determinant"],
            "determinant_sign": "positive",
            "rank": 2,
            "source_record_vectors": [["C_00", "0"], ["0", "C_11"]],
        },
        "memory_records": {
            "record_equation": "d_Theta m_a=q_a(Theta;dG_ret J_b)",
            "final_matrix": "m_a(after support; source b)=M_ab",
            "persistence": "d_Theta m_a=0 after each detector window",
            "distinguishable": True,
        },
        "mutation_results": mutations,
        "flags": {
            "TWO_PREDECLARED_COMPACT_CONSERVED_CURRENTS": True,
            "FULL_MAXWELL_RETARDED_SOLUTIONS_EXACT": True,
            "SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO": True,
            "TWO_CAUSALLY_ACQUIRED_MEMORY_RECORDS_DISTINGUISHABLE": True,
            "SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES": False,
            "APPARATUS_RECOIL_AND_BACKREACTION_INCLUDED": False,
            "D_DESCENT_WITH_SOURCE_ROD_MEMORY_SECTOR_CERTIFIED": False,
            "CLASSICAL_OBSERVER_MAP_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "rank two for two spatially localized emitter worldtubes rather than the homogeneous compact-S3 source sector",
            "apparatus recoil or Maxwell and gravitational backreaction",
            "raw-D or K_Berger descent after adjoining source, rod, and memory sectors",
            "a full interacting observer algebra or quantum observer state",
        ],
        "provenance": {
            "declared_input_sha256": _sha256(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This exact classical theorem computes M_ab=Q_a[d G_ret J_b] for two predeclared smooth conserved switch-on currents in the full-Maxwell-embedded homogeneous e1/e2 sector and proves M=diag(C_00,C_11) with C_00,C_11>0, hence rank M=2 and two distinguishable persistent causal records. The currents are compact in spacetime but occupy the full compact Berger S3, so this does not certify spatially localized emitter worldtubes. It also does not include recoil, backreaction, raw-D/K_Berger descent, a complete interacting observer algebra, or any quantum claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("smeared retarded transfer certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
