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
CLASSICAL_SCALAR_CLOCK_CONTRIBUTION = PACKAGE / "contributions" / "classical-scalar-clock-vertical-slice.json"
CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION = PACKAGE / "contributions" / "classical-neutral-conformal-clock-pair.json"
CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION = PACKAGE / "contributions" / "classical-neutral-clock-bv-health.json"
CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION = PACKAGE / "contributions" / "classical-homogeneous-positive-stealth-clock.json"
CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION = PACKAGE / "contributions" / "classical-standard-conformal-stealth-clock-no-go.json"
CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION = PACKAGE / "contributions" / "classical-positive-berger-clock-background.json"
NONLINEAR_ND1_CONTRIBUTION = PACKAGE / "contributions" / "nonlinear-nd1-selected-residual-d-derivation.json"
EINSTEIN_ED1A_CONTRIBUTION = PACKAGE / "contributions" / "einstein-ed1a-asymptotic-generator-gate.json"

TEAM_PATHS = {
    "classical": "d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json",
    "einstein_boundary": "bridge/certificates/d_quotient_asymptotic_seed.json",
    "nonlinear": "quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json",
    "quantum": "quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json",
}
PRE_SCALAR_CLASSICAL_STATUS_HASH = (
    "495de6865c8aa7bceb32a55769cd4f912da6d67035e899b8571843ab504457af"
)


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
    scalar_setting = next(
        row
        for row in classical["settings"]
        if row["setting_id"] == "cylinder_scalar_clock"
    )
    if not (
        scalar_setting["assessment_status"] == "OPEN"
        and scalar_setting["verdict"] is None
        and classical["work_packages"]["relational_clock"]["status"]
        == "PARTIAL"
        and classical["work_packages"]["relational_clock"]["evidence_refs"]
        == [
            "scalar_clock_vertical_slice",
            "neutral_conformal_clock_pair",
            "neutral_clock_bv_health_audit",
            "homogeneous_positive_conformal_stealth_clock",
            "inhomogeneous_conformal_stealth_clock_no_go",
            "positive_berger_clock_background",
        ]
    ):
        raise AssertionError("classical scalar-clock obstruction scope drifted")
    neutral_setting = next(
        row
        for row in classical["settings"]
        if row["setting_id"] == "cylinder_neutral_clock_pair"
    )
    if not (
        neutral_setting["assessment_status"] == "CERTIFIED"
        and neutral_setting["verdict"] == "D_GAUGE"
        and neutral_setting["claim_scope"] == "REDUCED_MODE"
        and neutral_setting["phase_space"]
        .startswith("compact_neutral_clock_pair_homogeneous")
    ):
        raise AssertionError("classical neutral-clock scope drifted")
    berger_setting = next(
        row
        for row in classical["settings"]
        if row["setting_id"] == "positive_berger_clock"
    )
    if not (
        berger_setting["assessment_status"] == "OPEN"
        and berger_setting["verdict"] is None
        and berger_setting["claim_scope"] == "REDUCED_MODE"
        and berger_setting["charge_test"]["status"] == "OPEN"
        and berger_setting["phase_space"].startswith(
            "positive_rotating_scalar_berger_background"
        )
    ):
        raise AssertionError("classical positive Berger background was promoted to a charge verdict")

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
    if imported_hash not in {classical_hash, PRE_SCALAR_CLASSICAL_STATUS_HASH}:
        raise AssertionError("quantum team classical import is neither current nor the certified pre-scalar baseline")
    if imported_hash != classical_hash and quantum["setting_ledger"][0]["verdict"] != "ANALYTIC_FRAMEWORK_MISSING":
        raise AssertionError("quantum result promoted without importing the current scalar-clock status")


def _nonlinear_nd1_contribution() -> dict[str, Any]:
    contribution = _load(NONLINEAR_ND1_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "nonlinear"
        and contribution.get("setting_id") == "compact_selected_residual_HT1_q2"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id") == "compact_selected_residual_HT1"
        and contribution.get("lifecycle_layer") == "INTERACTING"
        and contribution.get("claim_status") == "PARTIAL"
        and contribution.get("verdict")
        == "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("nonlinear ND1 contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("nonlinear ND1 contribution evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("nonlinear ND1 contribution evidence hash drifted")
    return contribution


def _classical_scalar_clock_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_SCALAR_CLOCK_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_scalar_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id") == "compact_scalar_clock"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical scalar-clock contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical scalar-clock evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical scalar-clock evidence hash drifted")
    return contribution


def _classical_neutral_clock_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_neutral_clock_pair"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "compact_neutral_clock_pair_homogeneous"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "D_GAUGE"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical neutral-clock contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical neutral-clock evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical neutral-clock evidence hash drifted")
    return contribution


def _classical_neutral_clock_health_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_neutral_clock_pair_local_health"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "compact_neutral_clock_pair_local_extension"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical neutral-clock health contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical neutral-clock health evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical neutral-clock health evidence hash drifted")
    return contribution


def _classical_homogeneous_stealth_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_homogeneous_positive_stealth_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "compact_homogeneous_positive_stealth_scalar"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical homogeneous stealth contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical homogeneous stealth evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical homogeneous stealth evidence hash drifted")
    return contribution


def _classical_standard_stealth_no_go_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_standard_conformal_stealth_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "standard_conformal_scalar_stealth_clock_sector"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical standard stealth no-go contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical standard stealth no-go evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical standard stealth no-go evidence hash drifted")
    return contribution


def _classical_positive_berger_clock_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_positive_berger_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_rotating_scalar_berger_background"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical positive Berger-clock contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical positive Berger-clock evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical positive Berger-clock evidence hash drifted")
    return contribution


def _einstein_ed1a_contribution() -> dict[str, Any]:
    contribution = _load(EINSTEIN_ED1A_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id") == "asymptotic_real_cylinder_time"
        and contribution.get("generator_id") == "H_ESU"
        and contribution.get("phase_space_id") == "asymptotically_flat_full_Bach"
        and contribution.get("lifecycle_layer") == "LORENTZIAN_CAUSAL"
        and contribution.get("claim_status") == "PARTIAL"
        and contribution.get("verdict") == "PHASE_SPACE_NOT_CLOSED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("Einstein E-D1a contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("Einstein E-D1a contribution evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("Einstein E-D1a contribution evidence hash drifted")
    return contribution


def build_certificate(base_commit: str | None = None) -> dict[str, Any]:
    team_data = {team: _load_team_input(path) for team, path in TEAM_PATHS.items()}
    _assert_team_inputs(team_data)
    inputs = {team: _team_input(path) for team, path in TEAM_PATHS.items()}
    scalar_clock_contribution = _classical_scalar_clock_contribution()
    neutral_clock_contribution = _classical_neutral_clock_contribution()
    neutral_clock_health_contribution = _classical_neutral_clock_health_contribution()
    homogeneous_stealth_contribution = _classical_homogeneous_stealth_contribution()
    standard_stealth_no_go_contribution = _classical_standard_stealth_no_go_contribution()
    positive_berger_clock_contribution = _classical_positive_berger_clock_contribution()
    ed1a_contribution = _einstein_ed1a_contribution()
    nd1_contribution = _nonlinear_nd1_contribution()
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
        "team_contributions": [
            {
                "path": str(CLASSICAL_SCALAR_CLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_SCALAR_CLOCK_CONTRIBUTION),
                "payload": scalar_clock_contribution,
            },
            {
                "path": str(CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION),
                "payload": neutral_clock_contribution,
            },
            {
                "path": str(CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION),
                "payload": neutral_clock_health_contribution,
            },
            {
                "path": str(CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION),
                "payload": homogeneous_stealth_contribution,
            },
            {
                "path": str(CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION),
                "payload": standard_stealth_no_go_contribution,
            },
            {
                "path": str(CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION),
                "payload": positive_berger_clock_contribution,
            },
            {
                "path": str(EINSTEIN_ED1A_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_ED1A_CONTRIBUTION),
                "payload": ed1a_contribution,
            },
            {
                "path": str(NONLINEAR_ND1_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(NONLINEAR_ND1_CONTRIBUTION),
                "payload": nd1_contribution,
            }
        ],
        "team_status": [
            {
                "team_id": "classical",
                "result_state": "PARTIAL_WITH_HEALTHY_BERGER_CLOCK_BACKGROUND",
                "verdict": "POSITIVE_CLOCK_BACKGROUND_EXISTS_CHARGE_OPEN",
                "established": "The standard one-field stealth route is ruled out, while an exact non-conformally-flat Berger-cylinder family carries a standard-sign rotating two-scalar phase clock with positive quartic and dominant-energy stress. The perturbative D charge remains open.",
                "next_gate": "full Berger-clock covariant charge and all-row BV audit",
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
                "established": "selected residual q2 D-derivation defect vanishes exactly; full support-local verdict remains blocked",
                "next_gate": "complete support-local q2 export and solve for iota_D^(2) or retain its obstruction",
            },
            {
                "team_id": "quantum",
                "result_state": "ALGEBRAIC_ENGINE_READY_ANALYTIC_FRAMEWORK_MISSING",
                "verdict": "ANALYTIC_FRAMEWORK_MISSING",
                "established": "the pre-scalar classical compact split is imported by content hash without quantum promotion; the new scalar no-go is not yet imported",
                "next_gate": "import the scalar-clock obstruction hash, then construct the renormalized observable algebra and classify the first D-Ward obstruction",
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
                "boundary_conditions": "closed unit S3; exact vacuum-cylinder one-real-scalar candidate",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED",
            },
            {
                "setting_id": "compact_neutral_clock_pair",
                "generator_id": "D_compact",
                "phase_space_id": "compact_neutral_clock_pair_homogeneous",
                "boundary_conditions": "closed unit S3; exact Bach-flat cylinder; H_D=0 and W nonzero; no surface flux",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_neutral_clock_pair_local_health",
                "generator_id": "D_compact",
                "phase_space_id": "compact_neutral_clock_pair_local_extension",
                "boundary_conditions": "local cylinder neighborhoods of the neutral winding orbit; all-row causal complex absent",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED",
            },
            {
                "setting_id": "compact_homogeneous_positive_stealth_clock",
                "generator_id": "D_compact",
                "phase_space_id": "compact_homogeneous_positive_stealth_scalar",
                "boundary_conditions": "closed unit S3; homogeneous positive-sign conformal scalar with quartic Weyl-invariant potential",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED",
            },
            {
                "setting_id": "compact_standard_conformal_stealth_clock",
                "generator_id": "D_compact",
                "phase_space_id": "standard_conformal_scalar_stealth_clock_sector",
                "boundary_conditions": "closed unit S3; complete standard positive-sign conformal scalar stealth family, including inhomogeneous configurations",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO",
            },
            {
                "setting_id": "compact_positive_berger_clock",
                "generator_id": "D_compact",
                "phase_space_id": "positive_rotating_scalar_berger_background",
                "boundary_conditions": "closed Berger S3; q in ((5-sqrt(21))/2,1/4); exact stationary Bach-sourced background; perturbative reduction open",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "PARTIAL",
                "verdict": "POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS",
            },
            {
                "setting_id": "compact_selected_residual_HT1_q2",
                "generator_id": "D_compact",
                "phase_space_id": "compact_selected_residual_HT1",
                "boundary_conditions": "closed cylinder; selected endpoint-projected HT1 BFV q2 domain",
                "lifecycle_layer": "INTERACTING",
                "status": "PARTIAL",
                "verdict": "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO",
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
                "promotion_gate": "certified scalar-clock scope theorem (the single-scalar no-go now qualifies) plus at least one complete boundary or interaction theorem",
            },
            "paper_X": {
                "status": "RESERVED_NOT_STARTED",
                "working_title": "Interaction and Quantum Stability of the Residual D-Quotient",
                "promotion_gate": "complete classical nonlinear export and applicable QME/Ward gate",
            },
        },
        "next_shared_gate": {
            "gate_id": "FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT",
            "owner_order": ["classical", "nonlinear", "quantum", "einstein_boundary"],
            "rule": "Treat the exact positive Berger family as a background candidate only. Derive the normalized covariant D charge on perturbations, construct the support-local all-row BV clock contraction and causal Green theory, and audit stability before assigning any D verdict.",
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
        "compact_scalar_clock": "SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED",
        "compact_neutral_clock_pair": "D_GAUGE",
        "compact_neutral_clock_pair_local_health": "OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED",
        "compact_homogeneous_positive_stealth_clock": "HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED",
        "compact_standard_conformal_stealth_clock": "STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO",
        "compact_positive_berger_clock": "POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS",
        "compact_selected_residual_HT1_q2": "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO",
        "asymptotic_real_cylinder_time": "PHASE_SPACE_NOT_CLOSED",
    }
    for setting, verdict in required.items():
        if ledger.get(setting, {}).get("verdict") != verdict:
            errors.append(f"{setting} verdict drifted")
    if ledger.get("compact_neutral_clock_pair", {}).get("phase_space_id") != (
        "compact_neutral_clock_pair_homogeneous"
    ):
        errors.append("neutral-clock verdict escaped its homogeneous phase space")
    if ledger.get("compact_quantum", {}).get("verdict") != "ANALYTIC_FRAMEWORK_MISSING":
        errors.append("quantum verdict promoted before QME")
    if ledger.get("compact_interacting", {}).get("verdict") != "INPUT_GATE_BLOCKED":
        errors.append("full interacting verdict promoted before local export")
    if ledger.get("compact_positive_berger_clock", {}).get("status") != "PARTIAL":
        errors.append("positive Berger background promoted before charge/BV audit")
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
    contribution_rows = "\n".join(
        "| {team} | `{setting}` | `{generator}` | `{phase_space}` | `{status}` | `{verdict}` |".format(
            team=record["payload"]["team_id"],
            setting=record["payload"]["setting_id"],
            generator=record["payload"]["generator_id"],
            phase_space=record["payload"]["phase_space_id"],
            status=record["payload"]["claim_status"],
            verdict=record["payload"]["verdict"],
        )
        for record in data["team_contributions"]
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
The one-real-scalar exact-cylinder and complete standard stealth-clock routes
are obstructed. A distinct neutral two-field reference sector supplies a
scoped homogeneous `D_GAUGE` theorem but fails its positive-health audit. The
first healthy background candidate is now exact: a non-conformally-flat Berger
cylinder supports two standard-sign rotating conformal scalars with positive
quartic potential, dominant-energy stress, timelike phase, and full raw clock
incidence. This is a background theorem only; its perturbative covariant
charge, all-row BV reduction, causal propagation, and stability remain open.

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

## Registered scoped contributions

| Team | Setting | Generator | Phase space | Status | Verdict |
|---|---|---|---|---|---|
{contribution_rows}

## Publication decision

This remains a cross-programme validation dossier.  Paper IX is reserved but
not started.  Its promotion gate is: {data['publication_plan']['paper_IX']['promotion_gate']}.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`{data['next_shared_gate']['gate_id']}`: {data['next_shared_gate']['rule']}

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
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_scalar_clock")["verdict"] = "D_GAUGE"
    reject("erase_single_scalar_clock_obstruction", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_neutral_clock_pair")["phase_space_id"] = "compact_scalar_clock"
    reject("erase_neutral_clock_scope", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_neutral_clock_pair_local_health")["verdict"] = "D_GAUGE"
    reject("erase_neutral_clock_health_obstruction", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_homogeneous_positive_stealth_clock")["verdict"] = "D_GAUGE"
    reject("erase_homogeneous_stealth_obstruction", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_standard_conformal_stealth_clock")["verdict"] = "D_GAUGE"
    reject("erase_standard_stealth_no_go", mutant)

    mutant = deepcopy(data)
    berger = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"] == "compact_positive_berger_clock"
    )
    berger["status"] = "CERTIFIED"
    berger["verdict"] = "D_GAUGE"
    reject("promote_Berger_background_before_charge", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_quantum")["verdict"] = "CARTAN_QUANTUM_EXACT"
    reject("promote_quantum_before_QME", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_selected_residual_HT1_q2")["verdict"] = "INTERACTING_CARTAN_EXISTS"
    reject("promote_selected_residual_to_full_cartan", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "asymptotic_real_cylinder_time")["verdict"] = "D_GAUGE"
    reject("promote_asymptotic_generator_before_phase_space", mutant)

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
        print("mutation guards: 12/12 PASS")
    print(CERTIFICATE, "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
