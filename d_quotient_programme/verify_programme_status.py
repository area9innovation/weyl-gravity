#!/usr/bin/env python3
"""Generate and verify the cross-programme D-quotient status dossier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "d_quotient_programme"
CERTIFICATE = PACKAGE / "certificates" / "D_QUOTIENT_PROGRAMME_STATUS.json"
REPORT = PACKAGE / "reports" / "consolidated-status.md"
GENERATOR_REGISTRY = PACKAGE / "registry" / "generators.json"
PHASE_REGISTRY = PACKAGE / "registry" / "phase_spaces.json"

TEAM_PATHS = {
    "classical": "d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json",
    "einstein_boundary": "bridge/certificates/d_quotient_asymptotic_seed.json",
    "nonlinear": "quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json",
    "quantum": "quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _last_commit(relative: str) -> str:
    return _git("log", "-1", "--format=%H", "--", relative)


def _committed_bytes(commit: str, relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:./{relative}"], cwd=ROOT
    )


def _team_input(relative: str) -> dict[str, str]:
    commit = _last_commit(relative)
    committed_hash = _sha256_bytes(_committed_bytes(commit, relative))
    return {"path": relative, "commit": commit, "sha256": committed_hash}


def _load_team_input(relative: str) -> dict[str, Any]:
    commit = _last_commit(relative)
    return json.loads(_committed_bytes(commit, relative).decode("utf-8"))


def _assert_team_inputs(data: dict[str, dict[str, Any]]) -> None:
    classical = data["classical"]
    if not (
        classical.get("schema") == "pure-weyl-classical-d-quotient-status-v1"
        and classical.get("claim_state") == "PARTIAL"
    ):
        raise AssertionError("classical D-quotient input drifted")
    compact = classical["settings"][0]
    if not (
        compact["setting_id"] == "vacuum_cylinder"
        and compact["verdict"] == "SECTOR_DEPENDENT"
        and {row["verdict"] for row in compact["sector_results"]}
        == {"D_CHARGED", "D_GAUGE"}
    ):
        raise AssertionError("compact classical sector split drifted")

    einstein = data["einstein_boundary"]
    if not (
        einstein.get("result_state") == "KINEMATICS_PROVED_PHASE_SPACE_OPEN"
        and einstein.get("verdicts")
        == {
            "asymptotically_flat_D": "PHASE_SPACE_NOT_CLOSED",
            "einstein_sector": "EINSTEIN_OPEN",
        }
    ):
        raise AssertionError("Einstein/boundary generator gate drifted")

    nonlinear = data["nonlinear"]
    if not (
        nonlinear.get("result_state")
        == "ENGINE_READY_HT1_RESIDUAL_AND_LOCAL_SEEDS_COMPUTED_INPUT_BLOCKED"
        and nonlinear.get("classical_freeze_gate") == "FAIL_CLOSED"
    ):
        raise AssertionError("nonlinear transfer gate drifted")

    quantum = data["quantum"]
    if not (
        quantum.get("result_state")
        == "ALGEBRAIC_ENGINE_READY_PHYSICAL_CANDIDATES_INPUT_BLOCKED"
        and quantum["input_gates"]["pure_weyl_QME"] == "NOT_RESTORED"
        and quantum["setting_ledger"][0]["verdict"]
        == "ANALYTIC_FRAMEWORK_MISSING"
    ):
        raise AssertionError("quantum Cartan/QME gate drifted")

    classical_hash = _sha256_bytes(
        _committed_bytes(
            _last_commit(TEAM_PATHS["classical"]), TEAM_PATHS["classical"]
        )
    )
    imported_hash = quantum["provenance"]["dependency_manifest"].get(
        "classical_D_quotient_status"
    )
    if imported_hash != classical_hash:
        raise AssertionError("quantum team has not imported the current classical split")


def build_certificate(base_commit: str | None = None) -> dict[str, Any]:
    team_data = {team: _load_team_input(path) for team, path in TEAM_PATHS.items()}
    _assert_team_inputs(team_data)
    inputs = {team: _team_input(path) for team, path in TEAM_PATHS.items()}
    return {
        "schema": "pure-weyl-d-quotient-programme-status-v1",
        "result_id": "D_QUOTIENT_PROGRAMME_STATUS",
        "programme_base_commit": base_commit or _git("rev-parse", "HEAD"),
        "result_state": "CROSS_PROGRAMME_DOSSIER_ACTIVE_RESULTS_SECTOR_INDEXED",
        "claim_key": [
            "generator_id",
            "phase_space_id",
            "boundary_conditions",
            "lifecycle_layer",
        ],
        "registry_hashes": {
            "generator_registry": _sha256(GENERATOR_REGISTRY),
            "phase_space_registry": _sha256(PHASE_REGISTRY),
        },
        "team_inputs": inputs,
        "team_status": [
            {
                "team_id": "classical",
                "result_state": "PARTIAL_WITH_COMPACT_SECTOR_SPLIT_CERTIFIED",
                "verdict": "SECTOR_DEPENDENT",
                "established": "D_compact is charged on compact_P_lin and gauge on compact_P_Taub0/compact_P_der.",
                "next_gate": "canonical conformal-scalar clock model and total improved D charge",
            },
            {
                "team_id": "einstein_boundary",
                "result_state": "KINEMATICS_PROVED_PHASE_SPACE_OPEN",
                "verdict": "PHASE_SPACE_NOT_CLOSED",
                "established": "H_ESU, D_M, D_rad, and P_0 cannot be silently identified in the real asymptotic problem.",
                "next_gate": "complete a boundary-preserving full Bach phase space and calculate charge and flux",
            },
            {
                "team_id": "nonlinear",
                "result_state": "ENGINE_READY_INPUT_BLOCKED",
                "verdict": "INPUT_GATE_BLOCKED",
                "established": "exact transfer engine, selected residual cubic bracket, and local Bach seeds",
                "next_gate": "complete support-local q2 export and compute the interacting D-Cartan defect",
            },
            {
                "team_id": "quantum",
                "result_state": "ALGEBRAIC_ENGINE_READY_ANALYTIC_FRAMEWORK_MISSING",
                "verdict": "ANALYTIC_FRAMEWORK_MISSING",
                "established": "classical sector split imported by content hash without quantum promotion",
                "next_gate": "construct the renormalized observable algebra and classify the first D-Ward obstruction",
            },
        ],
        "setting_ledger": [
            {
                "setting_id": "compact_unrestricted",
                "generator_id": "D_compact",
                "phase_space_id": "compact_P_lin",
                "boundary_conditions": "closed S3; no residual zero-charge restriction",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_CHARGED",
            },
            {
                "setting_id": "compact_taub_zero",
                "generator_id": "D_compact",
                "phase_space_id": "compact_P_Taub0",
                "boundary_conditions": "closed S3; all fifteen moment maps constrained to zero",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_derived_residual",
                "generator_id": "D_compact",
                "phase_space_id": "compact_P_der",
                "boundary_conditions": "selected closed-universe derived quotient",
                "lifecycle_layer": "CLASSICAL_CARTAN",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_scalar_clock",
                "generator_id": "D_compact",
                "phase_space_id": "compact_scalar_clock",
                "boundary_conditions": "not yet declared",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "OPEN",
                "verdict": None,
            },
            {
                "setting_id": "compact_interacting",
                "generator_id": "D_compact",
                "phase_space_id": "compact_interacting",
                "boundary_conditions": "closed S3; support-local nonlinear export incomplete",
                "lifecycle_layer": "INTERACTING",
                "status": "BLOCKED",
                "verdict": "INPUT_GATE_BLOCKED",
            },
            {
                "setting_id": "compact_quantum",
                "generator_id": "D_compact",
                "phase_space_id": "compact_quantum",
                "boundary_conditions": "renormalized observable algebra not constructed",
                "lifecycle_layer": "QUANTUM",
                "status": "BLOCKED",
                "verdict": "ANALYTIC_FRAMEWORK_MISSING",
            },
            {
                "setting_id": "asymptotic_real_cylinder_time",
                "generator_id": "H_ESU",
                "phase_space_id": "asymptotically_flat_full_Bach",
                "boundary_conditions": "fixed Minkowski null boundary",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "OPEN",
                "verdict": "PHASE_SPACE_NOT_CLOSED",
            },
            {
                "setting_id": "asymptotic_dilation",
                "generator_id": "D_M",
                "phase_space_id": "asymptotically_flat_full_Bach",
                "boundary_conditions": "full null-infinity data not yet closed",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "OPEN",
                "verdict": None,
            },
            {
                "setting_id": "asymptotic_time_translation",
                "generator_id": "P_0",
                "phase_space_id": "asymptotically_flat_full_Bach",
                "boundary_conditions": "Bondi/ADM boundary conditions not yet completed for pure Weyl",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "OPEN",
                "verdict": None,
            },
            {
                "setting_id": "lorentzian_dS_AdS",
                "generator_id": "UNSELECTED",
                "phase_space_id": "lorentzian_dS_AdS",
                "boundary_conditions": "not specified",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "NOT_TESTED",
                "verdict": None,
            },
        ],
        "dependency_gate": [
            "the selected generator preserves the declared phase space and boundary data",
            "the generator is Hamiltonian with an integrable normalized charge",
            "the charge vanishes on the exact sector proposed for quotienting",
            "the zero-charge transformations close as a Lie algebra or declared algebroid",
            "the classical Cartan and causal homotopies exist in the declared support category",
            "interacting promotion requires a corrected Cartan homotopy",
            "quantum promotion requires a restored QME and renormalized Ward identity",
        ],
        "publication_plan": {
            "current_form": "CROSS_PROGRAMME_VALIDATION_DOSSIER",
            "papers_VII_VIII": "completed theorem retained with explicit compact phase-space scope",
            "paper_IX": {
                "status": "RESERVED_NOT_STARTED",
                "working_title": "When Is Cylinder Time Gauge? Taub Constraints, Relational Clocks, and Residual Reduction in Weyl Gravity",
                "promotion_gate": "scalar-clock theorem plus at least one boundary or interaction theorem",
            },
            "paper_X": {
                "status": "RESERVED_NOT_STARTED",
                "working_title": "Interaction and Quantum Stability of the Residual D-Quotient",
                "promotion_gate": "complete classical nonlinear export and applicable QME/Ward gate",
            },
        },
        "next_shared_gate": {
            "gate_id": "SCALAR_CLOCK_VERTICAL_SLICE",
            "owner_order": ["classical", "nonlinear", "quantum", "einstein_boundary"],
            "rule": "Define one canonical conformal-scalar BV model and clock domain; downstream teams import it by hash rather than rebuilding it.",
        },
        "claim_boundary": (
            "The dossier consolidates sector-indexed results. It does not promote a "
            "universal D-gauge verdict, an interacting Cartan theorem, a quantum "
            "anomaly result, or an asymptotic charge theorem."
        ),
    }


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "pure-weyl-d-quotient-programme-status-v1":
        errors.append("unsupported schema")
    if data.get("claim_key") != [
        "generator_id",
        "phase_space_id",
        "boundary_conditions",
        "lifecycle_layer",
    ]:
        errors.append("claim key drifted")
    teams = data.get("team_status", [])
    if [row.get("team_id") for row in teams] != [
        "classical",
        "einstein_boundary",
        "nonlinear",
        "quantum",
    ]:
        errors.append("four-team inventory drifted")
    ledger = {row.get("setting_id"): row for row in data.get("setting_ledger", [])}
    required = {
        "compact_unrestricted": "D_CHARGED",
        "compact_taub_zero": "D_GAUGE",
        "compact_derived_residual": "D_GAUGE",
    }
    for setting, verdict in required.items():
        if ledger.get(setting, {}).get("verdict") != verdict:
            errors.append(f"{setting} verdict drifted")
    if ledger.get("compact_quantum", {}).get("verdict") != "ANALYTIC_FRAMEWORK_MISSING":
        errors.append("quantum verdict promoted before QME")
    if data.get("publication_plan", {}).get("paper_IX", {}).get("status") != "RESERVED_NOT_STARTED":
        errors.append("Paper IX promoted before its gate")
    return errors


def render_report(data: dict[str, Any]) -> str:
    team_rows = "\n".join(
        f"| {row['team_id']} | `{row['verdict']}` | {row['established']} | {row['next_gate']} |"
        for row in data["team_status"]
    )
    setting_rows = "\n".join(
        f"| {row['setting_id']} | `{row['generator_id']}` | `{row['phase_space_id']}` | {row['lifecycle_layer']} | `{row['status']}` | `{row['verdict'] if row['verdict'] is not None else 'OPEN'}` |"
        for row in data["setting_ledger"]
    )
    evidence_rows = "\n".join(
        f"- `{team}`: `{record['path']}` at `{record['commit']}`, SHA-256 `{record['sha256']}`"
        for team, record in data["team_inputs"].items()
    )
    return rf"""# Consolidated \(D\)-quotient programme status

## Interpretation

There is no universal yes/no verdict for \(D\).  The authoritative claim key is

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

The compact result is sector-dependent: \(D\) is charged on the unrestricted
locally reduced linearized space, and it becomes gauge only after restriction
to the full Taub/moment-map zero fibre and the selected derived quotient.
Boundary, nonlinear, and quantum questions are separate gates.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
{team_rows}

## Setting ledger

| Setting | Generator | Phase space | Layer | Status | Verdict |
|---|---|---|---|---|---|
{setting_rows}

## Shared dependency gate

""" + "\n".join(
        f"{index}. {gate}" for index, gate in enumerate(data["dependency_gate"], 1)
    ) + f"""

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: {data['publication_plan']['paper_IX']['promotion_gate']}.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`{data['next_shared_gate']['gate_id']}`: define one canonical conformal-scalar
BV/clock model, then make every downstream team import it by content hash.

## Imported evidence

{evidence_rows}

## Claim boundary

{data['claim_boundary']}

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
"""


def _check_inputs_against_certificate(data: dict[str, Any]) -> None:
    for team, record in data["team_inputs"].items():
        relative = record["path"]
        if relative != TEAM_PATHS[team]:
            raise AssertionError(f"{team} input path drifted")
        if _sha256_bytes(_committed_bytes(record["commit"], relative)) != record["sha256"]:
            raise AssertionError(f"{team} committed evidence hash drifted")
    if _sha256(GENERATOR_REGISTRY) != data["registry_hashes"]["generator_registry"]:
        raise AssertionError("generator registry drifted")
    if _sha256(PHASE_REGISTRY) != data["registry_hashes"]["phase_space_registry"]:
        raise AssertionError("phase-space registry drifted")


def mutation_guards(data: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def reject(name: str, mutant: dict[str, Any]) -> None:
        if not validate(mutant):
            failures.append(name)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_unrestricted")["verdict"] = "D_GAUGE"
    reject("erase_compact_charge", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_quantum")["verdict"] = "CARTAN_QUANTUM_EXACT"
    reject("promote_quantum_before_QME", mutant)

    mutant = deepcopy(data)
    mutant["publication_plan"]["paper_IX"]["status"] = "ACTIVE_THEOREM_PAPER"
    reject("promote_paper_IX_before_gate", mutant)

    mutant = deepcopy(data)
    mutant["claim_key"] = ["team_id"]
    reject("replace_sector_key_with_team_vote", mutant)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    if args.emit:
        data = build_certificate()
        errors = validate(data)
        if errors:
            raise AssertionError("; ".join(errors))
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(render_report(data), encoding="utf-8")
        print("wrote", CERTIFICATE)
        print("wrote", REPORT)
        return 0

    data = _load(CERTIFICATE)
    errors = validate(data)
    if errors:
        raise AssertionError("; ".join(errors))
    _check_inputs_against_certificate(data)
    expected = build_certificate(data["programme_base_commit"])
    if data != expected:
        raise AssertionError("programme certificate does not match exact regeneration")
    if REPORT.read_text(encoding="utf-8") != render_report(data):
        raise AssertionError("consolidated report drifted")
    if args.guards:
        failures = mutation_guards(data)
        if failures:
            raise AssertionError("mutation guards failed: " + ", ".join(failures))
        print("mutation guards: 4/4 PASS")
    print(CERTIFICATE, "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
