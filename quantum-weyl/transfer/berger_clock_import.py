"""Content-addressed nonlinear import of the classical Berger clock candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_ROOT = ROOT / "d_quotient_classical"
PROGRAMME_ROOT = ROOT / "d_quotient_programme"

BACKGROUND_PATH = CLASSICAL_ROOT / "certificates" / "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
CHARGE_PATH = CLASSICAL_ROOT / "certificates" / "BERGER_CLOCK_REDUCED_CHARGE_SEED.json"
CLASSICAL_STATUS_PATH = CLASSICAL_ROOT / "certificates" / "CLASSICAL_D_QUOTIENT_STATUS.json"
PROGRAMME_STATUS_PATH = PROGRAMME_ROOT / "certificates" / "D_QUOTIENT_PROGRAMME_STATUS.json"
BACKGROUND_CONTRIBUTION_PATH = PROGRAMME_ROOT / "contributions" / "classical-positive-berger-clock-background.json"
CHARGE_CONTRIBUTION_PATH = PROGRAMME_ROOT / "contributions" / "classical-berger-clock-charge-seed.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Berger import object is not a mapping: {path}")
    return value


def _require_commit(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"{label} commit is invalid")
    return value


def _require_exact_evidence(
    contribution: dict[str, Any],
    *,
    expected_path: Path,
    expected_verdict: str,
) -> dict[str, str]:
    evidence = contribution.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"path", "commit", "sha256"}:
        raise ValueError("Berger contribution evidence ledger is invalid")
    relative = expected_path.relative_to(ROOT).as_posix()
    if evidence["path"] != relative or evidence["sha256"] != _sha256(expected_path):
        raise ValueError("Berger contribution evidence does not match the imported bytes")
    commit = _require_commit(evidence["commit"], "Berger contribution source")
    if contribution.get("claim_status") != "CERTIFIED" or contribution.get("verdict") != expected_verdict:
        raise ValueError("Berger contribution claim status or verdict drifted")
    return {"path": relative, "commit": commit, "sha256": evidence["sha256"]}


def build_import() -> dict[str, Any]:
    background = _load(BACKGROUND_PATH)
    charge = _load(CHARGE_PATH)
    classical_status = _load(CLASSICAL_STATUS_PATH)
    programme_status = _load(PROGRAMME_STATUS_PATH)
    background_contribution = _load(BACKGROUND_CONTRIBUTION_PATH)
    charge_contribution = _load(CHARGE_CONTRIBUTION_PATH)

    if background.get("result_id") != "POSITIVE_BERGER_CLOCK_BACKGROUND":
        raise ValueError("Berger background result id drifted")
    if charge.get("result_id") != "BERGER_CLOCK_REDUCED_CHARGE_SEED":
        raise ValueError("Berger reduced-charge result id drifted")
    for payload in (background, charge):
        if payload.get("setting_id") != "compact_positive_berger_clock":
            raise ValueError("Berger setting id drifted")
        if payload.get("phase_space_id") != "positive_rotating_scalar_berger_background":
            raise ValueError("Berger phase-space id drifted")
        if payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
            raise ValueError("Berger dependency tags drifted")

    required_background_true = {
        "bounded_below_quartic",
        "everywhere_timelike_phase_clock",
        "exact_backreacted_background_exists",
        "full_diff_weyl_incidence",
        "positive_standard_scalar_kinetic",
    }
    required_background_false = {
        "covariant_phase_space_D_charge_computed",
        "linear_and_nonlinear_stability_proved",
        "quantum_admissibility_proved",
        "support_local_all_row_bv_retract_constructed",
    }
    flags = background.get("flags", {})
    if any(flags.get(key) is not True for key in required_background_true):
        raise ValueError("a certified healthy Berger background flag was lost")
    if any(flags.get(key) is not False for key in required_background_false):
        raise ValueError("an open Berger background gate was prematurely promoted")
    if background.get("gate_result") != {
        "gate": "POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK",
        "next_gate": "FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT",
        "next_gate_status": "OPEN",
        "status": "PASSED_BY_EXACT_BERGER_BACKGROUND",
    }:
        raise ValueError("Berger background gate ledger drifted")
    if (
        background.get("exact_solution_family", {}).get("parameter_interval")
        != "(5-sqrt(21))/2 < q < 1/4"
        or background.get("energy_health", {}).get("dominant_energy_condition") is not True
    ):
        raise ValueError("Berger exact interval or energy-health result drifted")

    charge_flags = charge.get("flags", {})
    if charge_flags.get("global_internal_charge_computed") is not True:
        raise ValueError("Berger internal charge was erased")
    if charge_flags.get("helical_D_internal_relation_computed") is not True:
        raise ValueError("Berger helical D relation was erased")
    for key in (
        "gravitational_and_matter_presymplectic_currents_combined",
        "support_local_all_row_bv_retract_constructed",
        "total_covariant_D_charge_computed",
    ):
        if charge_flags.get(key) is not False:
            raise ValueError("an open Berger charge gate was prematurely promoted")
    if charge.get("clock_interpretation", {}).get("charge_nonzero_on_open_interval") is not True:
        raise ValueError("Berger charge seed no longer proves nonzero clock momentum")
    if charge.get("exact_identities", {}).get("integrated_charge") != (
        "Q_R=16 pi^2 alpha_B q sqrt(1-4q)"
    ):
        raise ValueError("Berger integrated charge normalization drifted")
    if charge.get("exact_identities", {}).get("helical_action") != (
        "L_D(T_1,T_2)=omega R(T_1,T_2)"
    ):
        raise ValueError("Berger helical action drifted")
    if charge.get("clock_interpretation", {}).get("canonical_phase_momentum") != "p_theta=Q_R":
        raise ValueError("Berger canonical phase momentum drifted")
    if charge.get("next_gate") != "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT":
        raise ValueError("Berger reduced-charge next gate drifted")

    background_evidence = _require_exact_evidence(
        background_contribution,
        expected_path=BACKGROUND_PATH,
        expected_verdict="POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS",
    )
    charge_evidence = _require_exact_evidence(
        charge_contribution,
        expected_path=CHARGE_PATH,
        expected_verdict="NONZERO_INTERNAL_CLOCK_MOMENTUM_TOTAL_D_OPEN",
    )

    classical_evidence = {
        row["evidence_id"]: row
        for row in classical_status.get("evidence_artifacts", [])
        if isinstance(row, dict) and "evidence_id" in row
    }
    for evidence_id, expected in (
        ("positive_berger_clock_background", background_evidence),
        ("berger_clock_reduced_charge_seed", charge_evidence),
    ):
        row = classical_evidence.get(evidence_id)
        if row is None or row.get("path") != expected["path"] or row.get("sha256") != expected["sha256"]:
            raise ValueError(f"classical Berger evidence row drifted: {evidence_id}")

    programme_rows = {
        row.get("setting_id"): row
        for row in programme_status.get("setting_ledger", [])
        if isinstance(row, dict)
    }
    if programme_rows.get("compact_positive_berger_clock", {}).get("status") != "PARTIAL":
        raise ValueError("programme Berger background scope was promoted or removed")
    if programme_rows.get("compact_positive_berger_clock_reduced_charge", {}).get("status") != "PARTIAL":
        raise ValueError("programme Berger charge scope was promoted or removed")
    programme_contributions = {
        row.get("path"): row
        for row in programme_status.get("team_contributions", [])
        if isinstance(row, dict)
    }
    for path, payload in (
        (BACKGROUND_CONTRIBUTION_PATH, background_contribution),
        (CHARGE_CONTRIBUTION_PATH, charge_contribution),
    ):
        relative = path.relative_to(ROOT).as_posix()
        row = programme_contributions.get(relative)
        if (
            row is None
            or row.get("sha256") != _sha256(path)
            or row.get("payload") != payload
        ):
            raise ValueError(f"programme Berger contribution registration drifted: {relative}")

    classical_status_commit = _require_commit(
        classical_status.get("source_commit"),
        "classical status source",
    )
    programme_base_commit = _require_commit(
        programme_status.get("programme_base_commit"),
        "programme base",
    )

    return {
        "schema": "quantum-weyl-berger-clock-nonlinear-import-v1",
        "result_id": "BERGER_CLOCK_NONLINEAR_IMPORT",
        "result_state": "BACKGROUND_AND_REDUCED_CHARGE_IMPORTED_TOTAL_D_OPEN",
        "setting_id": "compact_positive_berger_clock",
        "phase_space_id": "positive_rotating_scalar_berger_background",
        "generator_id": "D_compact",
        "lifecycle_layer": "CLASSICAL_CHARGE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "setting_verdict": "INPUT_GATE_BLOCKED",
        "imported_background": {
            "parameter_interval": background["exact_solution_family"]["parameter_interval"],
            "positive_standard_scalar_kinetic": flags["positive_standard_scalar_kinetic"],
            "bounded_below_quartic": flags["bounded_below_quartic"],
            "dominant_energy_condition": background["energy_health"]["dominant_energy_condition"],
            "everywhere_timelike_phase_clock": flags["everywhere_timelike_phase_clock"],
            "full_diff_weyl_incidence": flags["full_diff_weyl_incidence"],
        },
        "imported_reduced_charge": {
            "integrated_charge": charge["exact_identities"]["integrated_charge"],
            "helical_action": charge["exact_identities"]["helical_action"],
            "charge_nonzero_on_open_interval": True,
            "canonical_phase_momentum": charge["clock_interpretation"]["canonical_phase_momentum"],
        },
        "D_disposition": {
            "status": "OPEN",
            "allowed_terminal_dispositions": [
                "D_GAUGE",
                "D_CHARGED_NO_QUOTIENT",
                "SECTOR_DEPENDENT",
                "NOT_HAMILTONIAN",
            ],
            "reason": "the reduced O(2) clock momentum is nonzero, but the combined gravitational-plus-matter covariant D charge has not been computed",
            "next_gate": "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT",
        },
        "physical_run_gate": {
            "total_D_disposition_certificate": "NOT_AVAILABLE",
            "support_local_q1_q2_D": "NOT_AVAILABLE",
            "classical_contraction": "NOT_AVAILABLE",
            "admissibility_policy": "NOT_AVAILABLE",
            "support_local_q3": "NOT_AVAILABLE",
            "route": "BLOCKED_BEFORE_CARTAN_CLASSIFICATION",
        },
        "established": [
            "a healthy exact positive-energy Berger clock background exists on an open parameter interval",
            "the clock phase carries nonzero conserved standard-sign matter momentum",
            "D acts helically with the internal O(2) rotation on the exact background",
        ],
        "not_established": [
            "the total gravitational-plus-matter covariant D charge",
            "a D_GAUGE, D_CHARGED_NO_QUOTIENT, SECTOR_DEPENDENT, or NOT_HAMILTONIAN disposition",
            "a support-local all-row matter-coupled BV contraction",
            "a physical nonlinear Cartan correction or obstruction on the Berger background",
            "causal propagation, stability, quantum admissibility, or a Lorentzian quantum theorem",
        ],
        "provenance": {
            "background": background_evidence,
            "reduced_charge": charge_evidence,
            "classical_status": {
                "path": CLASSICAL_STATUS_PATH.relative_to(ROOT).as_posix(),
                "sha256": _sha256(CLASSICAL_STATUS_PATH),
                "source_commit": classical_status_commit,
            },
            "programme_status": {
                "path": PROGRAMME_STATUS_PATH.relative_to(ROOT).as_posix(),
                "sha256": _sha256(PROGRAMME_STATUS_PATH),
                "programme_base_commit": programme_base_commit,
            },
        },
    }
