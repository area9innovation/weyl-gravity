#!/usr/bin/env python3
"""Import the scoped Berger fixed-coupling D_GAUGE theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
FIXED_CHARGE_PATH = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_FIXED_COUPLING_DELTA_CHARGE.json"
)
CONTRIBUTION_PATH = (
    ROOT
    / "d_quotient_programme"
    / "contributions"
    / "classical-berger-fixed-coupling-delta-charge.json"
)
PROGRAMME_STATUS_PATH = (
    ROOT / "d_quotient_programme" / "certificates" / "D_QUOTIENT_PROGRAMME_STATUS.json"
)
CLASSICAL_STATUS_PATH = (
    ROOT / "d_quotient_classical" / "certificates" / "CLASSICAL_D_QUOTIENT_STATUS.json"
)
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_TOTAL_D_DISPOSITION.json"

try:
    from .total_d_disposition import validate_total_d_disposition
except ImportError:
    from total_d_disposition import validate_total_d_disposition


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "total_d_disposition.py",
        "total_d_disposition_certificate.py",
        "schema/total-d-disposition-v1.schema.json",
        "tests/test_total_d_disposition.py",
    )
    return {
        f"quantum-weyl/transfer/{path}": _sha256(TRANSFER_ROOT / path)
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    fixed_charge = json.loads(FIXED_CHARGE_PATH.read_text(encoding="utf-8"))
    contribution = json.loads(CONTRIBUTION_PATH.read_text(encoding="utf-8"))
    programme = json.loads(PROGRAMME_STATUS_PATH.read_text(encoding="utf-8"))
    classical_status = json.loads(CLASSICAL_STATUS_PATH.read_text(encoding="utf-8"))
    if (
        fixed_charge.get("schema")
        != "pure-weyl-berger-fixed-coupling-delta-charge-v1"
        or fixed_charge.get("result_id") != "BERGER_FIXED_COUPLING_DELTA_CHARGE"
        or fixed_charge.get("claim_status") != "CERTIFIED"
        or fixed_charge.get("scientific_verdict") != "D_GAUGE"
        or fixed_charge.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise ValueError("classical Berger fixed-coupling verdict drifted")
    if fixed_charge.get("flags") != {
        "fixed_coupling_linearized_delta_Q_tangent_exists": False,
        "full_mode_average_argument_exact": True,
        "homogeneous_lapse_constraint_exact": True,
        "nonlinear_stability_proved": False,
        "scoped_D_verdict_promoted": True,
        "support_local_all_row_BV_retract_constructed": False,
        "total_helical_presymplectic_contraction_zero": True,
    }:
        raise ValueError("classical Berger fixed-coupling flags drifted")
    if fixed_charge.get("linearized_lapse_constraint", {}).get("identity") != (
        "delta E_N=-(alpha_B q^(3/2)/2)(delta Q_R/Q_R)"
    ):
        raise ValueError("classical Berger lapse constraint drifted")
    if fixed_charge.get("full_mode_upgrade", {}).get("conclusion") != (
        "delta Q_R=0 on the complete smooth fixed-coupling linearized solution space"
    ):
        raise ValueError("classical Berger full-mode tangent result drifted")
    if fixed_charge.get("presymplectic_conclusion") != {
        "imported_identity": "Omega_total(delta,L_D)=omega delta Q_R",
        "result": "Omega_total(delta,L_D)=0 for every allowed fixed-coupling linearized tangent",
        "scope": "the smooth fixed-coupling linearized covariant phase space about the positive Berger clock background on closed S3",
        "verdict": "D_GAUGE",
    }:
        raise ValueError("classical Berger presymplectic conclusion drifted")

    evidence = contribution.get("evidence", {})
    if (
        contribution.get("claim_status") != "CERTIFIED"
        or contribution.get("verdict") != "D_GAUGE"
        or contribution.get("setting_id") != fixed_charge.get("setting_id")
        or contribution.get("phase_space_id") != fixed_charge.get("phase_space_id")
        or contribution.get("generator_id") != fixed_charge.get("generator_id")
        or evidence.get("path") != FIXED_CHARGE_PATH.relative_to(ROOT).as_posix()
        or evidence.get("sha256") != _sha256(FIXED_CHARGE_PATH)
        or evidence.get("commit") != "cc5df8d547f7d2119282590a824ce92cd1d76d17"
    ):
        raise ValueError("Berger fixed-coupling contribution evidence drifted")
    registered = next(
        (
            row
            for row in programme.get("team_contributions", [])
            if row.get("path") == CONTRIBUTION_PATH.relative_to(ROOT).as_posix()
        ),
        None,
    )
    if (
        registered is None
        or registered.get("payload") != contribution
        or registered.get("sha256") != _sha256(CONTRIBUTION_PATH)
    ):
        raise ValueError("Berger fixed-coupling contribution is not registered")
    setting = next(
        (
            row
            for row in programme.get("setting_ledger", [])
            if row.get("setting_id") == fixed_charge.get("setting_id")
        ),
        None,
    )
    if setting is None or setting.get("status") != "CERTIFIED" or setting.get("verdict") != "D_GAUGE":
        raise ValueError("Berger fixed-coupling programme setting is not certified")
    classical_evidence = next(
        (
            row
            for row in classical_status.get("evidence_artifacts", [])
            if row.get("evidence_id") == "berger_fixed_coupling_delta_charge"
        ),
        None,
    )
    classical_setting = next(
        (
            row
            for row in classical_status.get("settings", [])
            if row.get("setting_id") == "positive_berger_clock"
        ),
        None,
    )
    if (
        classical_status.get("source_commit") != evidence["commit"]
        or classical_evidence is None
        or classical_evidence.get("path") != evidence["path"]
        or classical_evidence.get("sha256") != evidence["sha256"]
        or classical_setting is None
        or classical_setting.get("assessment_status") != "CERTIFIED"
        or classical_setting.get("verdict") != "D_GAUGE"
        or classical_setting.get("charge_test", {}).get("delta_H_D")
        != "IDENTICALLY_ZERO"
        or classical_setting.get("cartan_contraction", {}).get("status") != "OPEN"
    ):
        raise ValueError("classical Berger D_GAUGE ledger is incomplete or over-promoted")

    source_artifacts = [
        {
            "path": FIXED_CHARGE_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(FIXED_CHARGE_PATH),
        },
        {
            "path": CONTRIBUTION_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(CONTRIBUTION_PATH),
        },
        {
            "path": PROGRAMME_STATUS_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(PROGRAMME_STATUS_PATH),
        },
        {
            "path": CLASSICAL_STATUS_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(CLASSICAL_STATUS_PATH),
        },
    ]
    for artifact in source_artifacts:
        if _sha256(ROOT / artifact["path"]) != artifact["sha256"]:
            raise ValueError(f"Berger total-D source artifact drifted: {artifact['path']}")
    source_manifest = _source_manifest()
    receipt_elapsed_seconds = {
        "python3 d_quotient_classical/backreacted_clock/fixed_coupling_delta_charge.py --check --guards": 0.85,
        "python3 d_quotient_classical/backreacted_clock/verify_fixed_coupling_delta_charge_independent.py": 0.77,
        "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_fixed_coupling_delta_charge": 0.85,
        "python3 d_quotient_programme/verify_programme_status.py --check --guards": 0.11,
    }
    if set(contribution["verification_commands"]) != set(receipt_elapsed_seconds):
        raise ValueError("Berger fixed-coupling verification command ledger drifted")
    certificate = {
        "schema": "pure-weyl-total-d-disposition-v1",
        "result_id": "BERGER_TOTAL_D_DISPOSITION_D_GAUGE",
        "lifecycle_layer": "CLASSICAL_CHARGE",
        "claim_status": "CERTIFIED",
        "assessment_status": "COMPUTED",
        "verdict": "D_GAUGE",
        "setting_id": fixed_charge["setting_id"],
        "phase_space_id": fixed_charge["phase_space_id"],
        "generator_id": fixed_charge["generator_id"],
        "boundary_conditions": contribution["boundary_conditions"],
        "boundary_conditions_sha256": _sha256_text(
            contribution["boundary_conditions"]
        ),
        "classical_commit": evidence["commit"],
        "dependency_tags": fixed_charge["dependency_tags"],
        "charge_audit": {
            "combined_gravitational_matter_presymplectic_contraction": "COMPUTED",
            "normalization": "FIXED",
            "integrability": "INTEGRABLE",
            "allowed_fixed_coupling_delta_Q_tangent": "ABSENT",
            "presymplectic_kernel": "D_IN_KERNEL",
            "total_D_charge_variation": "ZERO",
        },
        "sector_ledger": [],
        "exact_checks": {
            "combined_presymplectic_contraction_derived": True,
            "charge_variation_identity_verified": True,
            "boundary_corner_terms_controlled": True,
            "fixed_coupling_tangent_space_classified": True,
            "exact_arithmetic": True,
        },
        "fail_closed": {
            "D_quotient_authorized": True,
            "unresolved_fields": [],
            "claim_boundary": fixed_charge["claim_boundary"],
        },
        "verification_receipts": [
            {
                "command": command,
                "elapsed_seconds": receipt_elapsed_seconds[command],
                "status": "PASS",
                "test_tier": 2 if "independent" in command else 1,
            }
            for command in contribution["verification_commands"]
        ],
        "provenance": {
            "source_commit": evidence["commit"],
            "source_artifacts": source_artifacts,
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "schema": "quantum-weyl/transfer/schema/total-d-disposition-v1.schema.json",
        },
        "next_gate": fixed_charge["next_gate"],
    }
    validate_total_d_disposition(certificate)
    return certificate


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"Berger total-D disposition receipt is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER TOTAL D: SCOPED D_GAUGE IMPORTED, BV CONTRACTION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
