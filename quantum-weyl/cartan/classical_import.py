"""Semantic adapter for the classical D-quotient status certificate."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATUS_PATH = (
    REPOSITORY_ROOT
    / "d_quotient_classical"
    / "certificates"
    / "CLASSICAL_D_QUOTIENT_STATUS.json"
)
EXPECTED_SETTINGS = (
    "vacuum_cylinder",
    "cylinder_scalar_clock",
    "cylinder_yang_mills",
    "weakly_deformed_background",
    "lorentzian_ds_ads",
    "asymptotically_flat",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_classical_d_status(record: object) -> dict[str, Any]:
    """Validate the semantic facts consumed by the quantum Cartan rail."""

    _require(isinstance(record, dict), "classical D status must be an object")
    data = copy.deepcopy(record)
    _require(
        data.get("result_id") == "CLASSICAL_D_QUOTIENT_STATUS",
        "unexpected classical D result_id",
    )
    _require(
        isinstance(data.get("source_commit"), str)
        and re.fullmatch(r"[0-9a-f]{40}", data["source_commit"]) is not None,
        "classical D source_commit is not a full commit hash",
    )
    _require(
        data.get("claim_state") in {"OPEN_FAIL_CLOSED", "PARTIAL", "COMPLETE"},
        "unknown classical D claim_state",
    )
    settings = data.get("settings")
    _require(isinstance(settings, list), "classical D settings must be an array")
    identifiers = [
        setting.get("setting_id") if isinstance(setting, dict) else None
        for setting in settings
    ]
    _require(
        all(isinstance(identifier, str) and identifier for identifier in identifiers),
        "classical D setting identifier is invalid",
    )
    _require(
        len(identifiers) == len(set(identifiers)),
        "classical D settings contain a duplicate identifier",
    )
    _require(
        set(EXPECTED_SETTINGS).issubset(identifiers),
        "classical D setting inventory is missing a required quantum setting",
    )
    by_id = {setting["setting_id"]: setting for setting in settings}
    vacuum = by_id["vacuum_cylinder"]
    _require(
        vacuum.get("assessment_status") == "CERTIFIED",
        "vacuum-cylinder classical D input is not certified",
    )
    _require(
        vacuum.get("verdict") == "SECTOR_DEPENDENT",
        "vacuum-cylinder classical D verdict is not sector-dependent",
    )
    sector_results = vacuum.get("sector_results")
    _require(isinstance(sector_results, list), "vacuum sector results are absent")
    sector_ids = [
        sector.get("sector_id") if isinstance(sector, dict) else None
        for sector in sector_results
    ]
    _require(
        len(sector_ids) == len(set(sector_ids)),
        "vacuum sector results contain a duplicate identifier",
    )
    sectors = {sector["sector_id"]: sector for sector in sector_results}
    _require(
        sectors.get("P_lin", {}).get("verdict") == "D_CHARGED",
        "P_lin is not certified as D_CHARGED",
    )
    _require(
        sectors.get("P_Taub0", {}).get("verdict") == "D_GAUGE",
        "P_Taub0 is not certified as D_GAUGE",
    )
    for setting_id in identifiers:
        setting = by_id[setting_id]
        _require(
            setting.get("assessment_status") in {"NOT_TESTED", "OPEN", "CERTIFIED"},
            f"unknown assessment status for {setting_id}",
        )
    return data


def load_classical_d_status(
    path: Path = DEFAULT_STATUS_PATH,
) -> dict[str, Any]:
    return validate_classical_d_status(json.loads(path.read_text(encoding="utf-8")))


def imported_setting_ledger(record: object) -> tuple[dict[str, str], ...]:
    """Derive the exact classical portion of the quantum setting ledger."""

    data = validate_classical_d_status(record)
    settings = {setting["setting_id"]: setting for setting in data["settings"]}
    output = []
    for setting_id in EXPECTED_SETTINGS:
        setting = settings[setting_id]
        if setting_id == "vacuum_cylinder":
            charge = "SECTOR_DEPENDENT_CLASSICALLY_P_LIN_CHARGED_P_TAUB0_GAUGE"
            status = "CERTIFIED_HASH_PINNED_NOT_A_QUANTUM_VERDICT"
        else:
            charge = setting["assessment_status"]
            status = setting["assessment_status"]
        output.append(
            {
                "setting_id": setting_id,
                "D_charge": charge,
                "classical_input_status": status,
            }
        )
    return tuple(output)


def import_receipt(path: Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    data = load_classical_d_status(path)
    vacuum = next(
        setting for setting in data["settings"] if setting["setting_id"] == "vacuum_cylinder"
    )
    return {
        "artifact": str(path.relative_to(REPOSITORY_ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_commit": data["source_commit"],
        "claim_state": data["claim_state"],
        "vacuum_assessment_status": vacuum["assessment_status"],
        "vacuum_verdict": vacuum["verdict"],
        "required_sector_verdicts": {
            sector["sector_id"]: sector["verdict"]
            for sector in vacuum["sector_results"]
            if sector["sector_id"] in {"P_lin", "P_Taub0"}
        },
        "additional_setting_ids": sorted(
            set(setting["setting_id"] for setting in data["settings"])
            - set(EXPECTED_SETTINGS)
        ),
        "semantic_validation": "VERIFIED",
    }
