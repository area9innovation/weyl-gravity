"""Content-addressed nonlinear import of the classical Berger clock candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
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
TOTAL_D_PATH = TRANSFER_ROOT / "certificates" / "BERGER_TOTAL_D_DISPOSITION.json"
PARTIAL_SDR_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_CLOCK_PARTIAL_SDR_IMPORT.json"
)
BACKGROUND_THEOREM_COMMIT = "bb5738d6e3e30a68adcc9a70c35dac089079e3db"
CHARGE_THEOREM_COMMIT = "bb5738d6e3e30a68adcc9a70c35dac089079e3db"
CLASSICAL_LEDGER_COMMIT = "09844b4299a263ff99792397ce8c06c74e3921a6"
PROGRAMME_LEDGER_COMMIT = "c4a1d28bab4d716a281db1c5428a83e515f6a822"

try:
    from .total_d_disposition import validate_total_d_disposition
except ImportError:
    from total_d_disposition import validate_total_d_disposition


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Berger import object is not a mapping: {path}")
    return value


def _git_blob(path: Path, *, commit: str) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    prefix = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return subprocess.run(
        ["git", "show", f"{commit}:{prefix}{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _load_git(path: Path, *, commit: str) -> dict[str, Any]:
    value = json.loads(_git_blob(path, commit=commit))
    if not isinstance(value, dict):
        raise ValueError(f"pinned Berger object is not a mapping: {path}")
    return value


def _git_sha256(path: Path, *, commit: str) -> str:
    return hashlib.sha256(_git_blob(path, commit=commit)).hexdigest()


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
    commit = _require_commit(evidence["commit"], "Berger contribution source")
    if evidence["path"] != relative or evidence["sha256"] != _git_sha256(
        expected_path,
        commit=commit,
    ):
        raise ValueError("Berger contribution evidence does not match the imported bytes")
    if contribution.get("claim_status") != "CERTIFIED" or contribution.get("verdict") != expected_verdict:
        raise ValueError("Berger contribution claim status or verdict drifted")
    return {"path": relative, "commit": commit, "sha256": evidence["sha256"]}


def build_import() -> dict[str, Any]:
    background = _load_git(BACKGROUND_PATH, commit=BACKGROUND_THEOREM_COMMIT)
    charge = _load_git(CHARGE_PATH, commit=CHARGE_THEOREM_COMMIT)
    classical_status = _load_git(
        CLASSICAL_STATUS_PATH,
        commit=CLASSICAL_LEDGER_COMMIT,
    )
    programme_status = _load_git(
        PROGRAMME_STATUS_PATH,
        commit=PROGRAMME_LEDGER_COMMIT,
    )
    background_contribution = _load_git(
        BACKGROUND_CONTRIBUTION_PATH,
        commit=PROGRAMME_LEDGER_COMMIT,
    )
    charge_contribution = _load_git(
        CHARGE_CONTRIBUTION_PATH,
        commit=PROGRAMME_LEDGER_COMMIT,
    )
    total_D_payload = _load(TOTAL_D_PATH)
    total_D = validate_total_d_disposition(total_D_payload)
    partial_sdr = _load(PARTIAL_SDR_PATH)

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
    if total_D.status != "D_GAUGE" or not total_D.D_quotient_authorized:
        raise ValueError("Berger fixed-coupling D_GAUGE disposition was lost")
    if (
        partial_sdr.get("schema")
        != "quantum-weyl-berger-clock-partial-sdr-import-v1"
        or partial_sdr.get("result_state")
        != "PARTIAL_CLOCK_SECTOR_SDR_AVAILABLE_PORTABLE_MAPS_BLOCKED"
        or partial_sdr.get("setting_id") != total_D.setting_id
        or partial_sdr.get("phase_space_id") != total_D.phase_space_id
        or partial_sdr.get("boundary_conditions_sha256")
        != total_D.boundary_conditions_sha256
        or partial_sdr.get("coverage", {}).get("contracted_clock_dimension") != 8
        or partial_sdr.get("coverage", {}).get("full_minimal_dimension") != 34
        or partial_sdr.get("nd2_gate", {}).get(
            "classical_contraction_artifact_satisfied"
        )
        is not False
        or partial_sdr.get("nd2_gate", {}).get("physical_execution_authorized")
        is not False
    ):
        raise ValueError("Berger partial clock SDR import crossed its evidence boundary")
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
            or row.get("sha256")
            != _git_sha256(path, commit=PROGRAMME_LEDGER_COMMIT)
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
        "result_state": "BACKGROUND_CHARGE_SCOPED_D_GAUGE_AND_PARTIAL_CLOCK_SDR_IMPORTED_FULL_BV_OPEN",
        "setting_id": "compact_positive_berger_clock",
        "phase_space_id": "positive_rotating_scalar_berger_background",
        "generator_id": "D_compact",
        "lifecycle_layer": "CLASSICAL_BV",
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
            "status": "D_GAUGE",
            "setting_id": total_D.setting_id,
            "phase_space_id": total_D.phase_space_id,
            "boundary_conditions_sha256": total_D.boundary_conditions_sha256,
            "classical_commit": total_D.classical_commit,
            "reason": "the exact fixed-coupling lapse constraint and compact averaging force delta Q_R=0, hence Omega_total(delta,L_D)=0 on the declared linearized phase space",
            "next_gate": "FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT",
        },
        "partial_clock_sdr": {
            "status": "AVAILABLE_EVIDENCE_ONLY",
            "contracted_rows": 8,
            "full_minimal_rows": 34,
            "retained_rows": 26,
            "portable_map_payload": "NOT_AVAILABLE",
            "D_equivariance": "NOT_COMPUTED",
            "complete_classical_contraction": False,
        },
        "physical_run_gate": {
            "total_D_disposition_certificate": "AVAILABLE_SCOPED_D_GAUGE",
            "partial_clock_sector_sdr": "AVAILABLE_EVIDENCE_ONLY",
            "support_local_q1_q2_D": "NOT_AVAILABLE",
            "classical_contraction": "NOT_AVAILABLE",
            "admissibility_policy": "NOT_AVAILABLE",
            "support_local_q3": "NOT_AVAILABLE",
            "route": "D_GAUGE_CERTIFIED_BV_INPUT_BLOCKED",
        },
        "established": [
            "a healthy exact positive-energy Berger clock background exists on an open parameter interval",
            "the clock phase carries nonzero conserved standard-sign matter momentum",
            "D acts helically with the internal O(2) rotation on the exact background",
            "D is presymplectically null on the smooth fixed-coupling linearized Berger phase space",
            "the eight minimal temporal-diffeomorphism/Weyl clock rows form an exact support-local cyclic SDR",
        ],
        "not_established": [
            "portable coefficient-level clock maps consumable by the ND2 assembler",
            "D-equivariance of the partial clock-sector SDR",
            "a support-local all-row matter-coupled BV contraction",
            "a physical nonlinear Cartan correction or obstruction on the Berger background",
            "causal propagation, stability, quantum admissibility, or a Lorentzian quantum theorem",
        ],
        "provenance": {
            "background": background_evidence,
            "reduced_charge": charge_evidence,
            "classical_status": {
                "path": CLASSICAL_STATUS_PATH.relative_to(ROOT).as_posix(),
                "sha256": _git_sha256(
                    CLASSICAL_STATUS_PATH,
                    commit=CLASSICAL_LEDGER_COMMIT,
                ),
                "source_commit": classical_status_commit,
                "ledger_commit": CLASSICAL_LEDGER_COMMIT,
            },
            "programme_status": {
                "path": PROGRAMME_STATUS_PATH.relative_to(ROOT).as_posix(),
                "sha256": _git_sha256(
                    PROGRAMME_STATUS_PATH,
                    commit=PROGRAMME_LEDGER_COMMIT,
                ),
                "programme_base_commit": programme_base_commit,
                "ledger_commit": PROGRAMME_LEDGER_COMMIT,
            },
            "total_D_disposition": {
                "path": TOTAL_D_PATH.relative_to(ROOT).as_posix(),
                "sha256": _sha256(TOTAL_D_PATH),
                "classical_commit": total_D.classical_commit,
            },
            "partial_clock_sdr": {
                "path": PARTIAL_SDR_PATH.relative_to(ROOT).as_posix(),
                "sha256": _sha256(PARTIAL_SDR_PATH),
                "classical_theorem_commit": partial_sdr["classical_theorem_commit"],
            },
        },
    }
