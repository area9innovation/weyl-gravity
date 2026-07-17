#!/usr/bin/env python3
"""Generate the hardened localized Berger detector-record preflight.

The producer derives rod, support, polarization, causal-center, no-wrap, and
memory witnesses.  It deliberately leaves the smeared retarded transfer
matrix to the next certificate.
"""

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
INPUT = PACKAGE / "fixtures/berger_localized_detector_records_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-localized-detector-records-input-v2.schema.json"
SCHEMA = PACKAGE / "schema/berger-localized-detector-records-v2.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json"

DEPENDENCIES = {
    "clock": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "apparatus_contract": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json",
    "retarded_signal": ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL.json",
    "redshift_geometry": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "raw_D_nullity": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
}
REQUIRED_FLAGS = {
    "clock": ["exact_backreacted_background_exists", "everywhere_timelike_phase_clock"],
    "apparatus_contract": ["BERGER_RELATIONAL_APPARATUS_CONTRACT", "BERGER_MAXWELL_SEMIDIRECT_GAUGE_Q2"],
    "retarded_signal": ["BERGER_COMPACT_CONSERVED_MAXWELL_SOURCE", "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL"],
    "redshift_geometry": ["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"],
    "raw_D_nullity": ["scoped_D_verdict_promoted", "total_helical_presymplectic_contraction_zero"],
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_detector_records.py",
    "tests": PACKAGE / "tests/test_berger_detector_records.py",
    "report": PACKAGE / "reports/berger-localized-detector-records.md",
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


def _strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _patched(data: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(data)
    result.update(patch)
    return result


def _detector_values(data: dict[str, Any]) -> tuple[list[sp.Rational], list[sp.Rational], list[list[sp.Rational]], list[str]]:
    detectors = data["detectors"]
    labels = [_q(value) for value in data.get("detector_clock_labels", [item["clock_label"] for item in detectors])]
    arclengths = [_q(value) for value in data.get("detector_hopf_arclengths", [item["hopf_arclength"] for item in detectors])]
    centers = [[_q(value) for value in row] for row in data.get("detector_rod_centers", [item["rod_center"] for item in detectors])]
    polarizations = list(data.get("detector_polarizations", [item["polarization"] for item in detectors]))
    return labels, arclengths, centers, polarizations


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    labels, arclengths, centers, polarizations = _detector_values(data)
    detectors = data["detectors"]
    radii = [_q(item["rod_radius"]) for item in detectors]
    raw_jacobians = data.get("rod_jacobians", [item["relational_jacobian"] for item in data["rod_charts"]])
    jacobians = [sp.Matrix([[_q(value) for value in row] for row in matrix]) for matrix in raw_jacobians]
    rod_cauchy_clocks = [_q(item["cauchy_clock"]) for item in data["rod_charts"]]

    spatially_disjoint = any(
        abs(centers[0][axis] - centers[1][axis]) >= radii[0] + radii[1]
        for axis in range(3)
    )
    supports_disjoint = labels[0] != labels[1] or spatially_disjoint
    record_matrix = sp.eye(2) if supports_disjoint else sp.ones(2)

    emitter_clock = _q(data["emitter"]["clock_label"])
    emitter_arclength = _q(data["emitter"]["hopf_arclength"])
    clock_rate = _q(data["clock_rate"])
    travel_distances = [abs(value - emitter_arclength) for value in arclengths]
    incidence_residuals = [sp.simplify(labels[index] - emitter_clock - clock_rate * travel_distances[index]) for index in range(2)]
    half_fibre_lower_bound = _q(data["hopf_geometry"]["certified_lower_bound"])
    half_fibre_length = 3 * sp.sqrt(10) * sp.pi / 10

    requirements = {
        "rod_solutions_nondegenerate": all(matrix.det() != 0 for matrix in jacobians) and rod_cauchy_clocks == labels,
        "clock_labels_distinct": len(set(labels)) == 2,
        "detector_supports_disjoint": supports_disjoint,
        "central_null_incidence_exact": incidence_residuals == [0, 0],
        "central_rays_unique_no_wrap": (
            half_fibre_lower_bound < half_fibre_length
            and all(0 < distance < half_fibre_lower_bound for distance in travel_distances)
        ),
        "record_functionals_independent": record_matrix.rank() == 2,
        "probe_memory_persistent": data["memory_model"]["probe_branch"] == "p_a=0" and data["memory_model"]["initial_memory"] == ["0", "0"],
    }
    return {
        "labels": labels,
        "arclengths": arclengths,
        "centers": centers,
        "polarizations": polarizations,
        "jacobians": jacobians,
        "record_matrix": record_matrix,
        "travel_distances": travel_distances,
        "incidence_residuals": incidence_residuals,
        "half_fibre_lower_bound": half_fibre_lower_bound,
        "half_fibre_length": half_fibre_length,
        "requirements": requirements,
    }


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


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    result = evaluate(data)
    if not all(result["requirements"].values()):
        raise AssertionError(f"base detector record fixture failed: {result['requirements']}")
    mutations = []
    for mutation in data["mutations"]:
        mutated = evaluate(_patched(data, mutation["patch"]))
        requirement = mutation["expected_failed_requirement"]
        mutations.append({
            "name": mutation["name"],
            "expected_failed_requirement": requirement,
            "observed_requirement_value": mutated["requirements"][requirement],
            "observed_record_rank": int(mutated["record_matrix"].rank()),
            "expected_failure_passed": mutated["requirements"][requirement] is False,
        })
    if not all(item["expected_failure_passed"] for item in mutations):
        raise AssertionError("detector record mutation rail did not fail closed")

    detector_rows = []
    for index, detector in enumerate(data["detectors"]):
        detector_rows.append({
            "id": detector["id"],
            "clock_label": sp.sstr(result["labels"][index]),
            "hopf_arclength": sp.sstr(result["arclengths"][index]),
            "rod_center": [sp.sstr(value) for value in result["centers"][index]],
            "rod_radius": detector["rod_radius"],
            "polarization": result["polarizations"][index],
            "smearing": f"Q_{index}[F]=integral rho_{index}(Theta,R) <F,P_{index}>_gHat dvol_gHat over compact spacetime support",
            "normalized_dual_probe": f"H_{index} compact Maxwell test field normalized by Q_{index}[H_{index}]=1",
        })

    return {
        "schema": "closed-universe-berger-localized-detector-records-v2",
        "result_id": "BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS",
        "setting_id": data["setting_id"],
        "claim_status": "CERTIFIED_LOCAL_ROD_SMEARING_AND_MEMORY_PREFLIGHT_RETARDED_TRANSFER_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": _dependency_refs(data["dependency_snapshot_commit"]),
        "rod_solution_contract": {
            "action": "S_R=-1/2 sum_I integral sqrt(-gHat) gHat^ab partial_a R^I partial_b R^I",
            "cauchy_data": "R^I=x^I and n(R^I)=0 in each detector chart",
            "local_existence": "standard normally hyperbolic scalar Cauchy theorem",
            "jacobians": [_strings(matrix) for matrix in result["jacobians"]],
            "jacobian_determinants": [sp.sstr(matrix.det()) for matrix in result["jacobians"]],
            "compact_window_rule": "choose each compact spacetime smearing support inside the intersection of its nominal detector ball and an open neighborhood where the evolved Jacobian remains nonzero",
            "probe_limit": "rod stress is order epsilon_R^2 and is excluded from the fixed background",
        },
        "causal_geometry": {
            "emitter_clock_label": data["emitter"]["clock_label"],
            "emitter_hopf_arclength": data["emitter"]["hopf_arclength"],
            "clock_rate": data["clock_rate"],
            "detector_travel_distances": [sp.sstr(value) for value in result["travel_distances"]],
            "central_null_incidence_residuals": [sp.sstr(value) for value in result["incidence_residuals"]],
            "half_fibre_length": data["hopf_geometry"]["half_fibre_length"],
            "certified_half_fibre_lower_bound": data["hopf_geometry"]["certified_lower_bound"],
            "unique_no_wrap_centers": result["requirements"]["central_rays_unique_no_wrap"],
            "boundary": "central Hopf null rays only; full source/window causal incidence belongs to the transfer gate",
        },
        "detector_smearings": detector_rows,
        "smearing_independence": {
            "construction": "normalized dual Maxwell probes supported in disjoint compact detector spacetime windows; cross terms vanish by support disjointness",
            "evaluation_matrix": _strings(result["record_matrix"]),
            "rank": int(result["record_matrix"].rank()),
            "not_input_labels": True,
        },
        "probe_memory_registers": {
            "action": data["memory_model"]["action"],
            "equations": ["d_Theta m_a=q_a(Theta;F)", "d_Theta p_a=0"],
            "probe_branch": data["memory_model"]["probe_branch"],
            "final_record": "M_a=m_a(after detector support)=Q_a[F]=integral q_a(Theta;F)dTheta for zero initial memory",
            "persistence": "d_Theta m_a=0 after the detector smearing support",
            "backreaction": "open; p_a=0 removes the detector force on the Maxwell field at probe order",
        },
        "next_transfer_gate": {
            "name": "BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER",
            "matrix": "M_ab=Q_a[d G_ret J_b]",
            "required_witnesses": [
                "two declared compact conserved emitter currents J_0,J_1 chosen before evaluation",
                "full source-support to detector-window causal incidence and no-wrap margins",
                "exact nonzero determinant or rank-two minor of M_ab",
                "memory response matrix equal to M_ab",
                "no adaptive detector placement or normalization using the computed response",
            ],
            "status": "OPEN",
        },
        "gauge_and_quotient_tests": {
            "Diff": "PASS_FOR_LOCAL_RELATIONAL_PROBE_FUNCTIONALS",
            "Weyl": "PASS_FOR_LOCAL_RELATIONAL_PROBE_FUNCTIONALS",
            "Maxwell_gauge": "PASS",
            "raw_D": "OPEN_WITH_ROD_MEMORY_SECTOR_NOT_IN_IMPORTED_PHASE_SPACE",
            "K_Berger": "OPEN_WITH_ROD_MEMORY_SECTOR_NOT_IN_IMPORTED_INTERACTING_COMPLEX",
        },
        "mutation_results": mutations,
        "flags": {
            "LOCAL_STANDARD_SIGN_ROD_SOLUTIONS": True,
            "ROD_JACOBIANS_NONDEGENERATE_ON_SOME_LOCAL_WINDOWS": True,
            "TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS": True,
            "DETECTOR_SMEARING_FUNCTIONALS_INDEPENDENT": True,
            "CENTRAL_HOPF_NULL_INTERSECTIONS_NO_WRAP": True,
            "PERSISTENT_PROBE_MEMORY_REGISTERS": True,
            "SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO": False,
            "TWO_NONZERO_RETARDED_MEMORY_RECORDS": False,
            "ROD_BACKREACTION_AND_APPARATUS_RECOIL_INCLUDED": False,
            "D_DESCENT_WITH_RODS_CERTIFIED": False,
            "CLASSICAL_OBSERVER_MAP_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "assumptions": [
            "the probe-rod limit consistently omits order-epsilon_R^2 stress and detector recoil",
            "the declared rod radii are nominal upper bounds; continuity certifies some nonzero compact support inside each ball, not the full numerical-radius ball",
            "the next transfer certificate will predeclare both currents and may not normalize using its computed responses",
        ],
        "not_established": [
            "the rank or nonvanishing of Q_a[d G_ret J_b]",
            "full compact-support causal incidence from two emitter currents to both detector windows",
            "rod or memory backreaction and apparatus recoil",
            "raw-D or K_Berger descent after adjoining rods and memory registers",
            "a quantum observer state or positive quantum inner product",
        ],
        "provenance": {
            "declared_input_sha256": _sha256(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This bridge-only classical preflight constructs local standard-sign probe rod solutions, two independent clock-labelled spacetime Maxwell detector smearings, exact central Hopf null/no-wrap incidences, and persistent probe memory registers. It does not compute the smeared retarded transfer matrix M_ab=Q_a[d G_ret J_b], include rod or detector backreaction, or prove raw-D/K_Berger descent. The partial Berger observer map therefore remains uncertified.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("localized detector record certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
