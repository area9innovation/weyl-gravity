#!/usr/bin/env python3
"""Validate the fail-closed classical D-quotient challenge handoff."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERTIFICATE = ROOT / "d_quotient_classical" / "certificates" / "CLASSICAL_D_QUOTIENT_STATUS.json"
SCHEMA_PATH = ROOT / "d_quotient_classical" / "schema" / "classical-status-v1.schema.json"

DEPENDENCY_TAGS = {
    "LOCAL-ALGEBRAIC",
    "EUCLIDEAN-SPECTRAL",
    "REDUCED-MODE",
    "LORENTZIAN-CAUSAL",
}
VERDICTS = {"D_GAUGE", "D_CHARGED", "SECTOR_DEPENDENT", "NOT_HAMILTONIAN"}
SETTING_IDS = [
    "vacuum_cylinder",
    "cylinder_scalar_clock",
    "cylinder_neutral_clock_pair",
    "positive_berger_clock",
    "cylinder_yang_mills",
    "weakly_deformed_background",
    "lorentzian_ds_ads",
    "asymptotically_flat",
]
COMPLEX_IDS = [
    "absolute_so42",
    "D_global_symmetry",
    "zero_charge_transformations",
    "local_gauge_only",
]
CERTIFIED = {"CERTIFIED", "CERTIFIED_BASELINE"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_keys(value: object, keys: set[str], path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return
    missing = sorted(keys - set(value))
    extra = sorted(set(value) - keys)
    for key in missing:
        errors.append(f"{path}.{key}: missing required property")
    for key in extra:
        errors.append(f"{path}.{key}: additional property is forbidden")


def _check_tags(tags: object, path: str, errors: list[str], *, allow_empty: bool) -> None:
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        errors.append(f"{path}: expected a string array")
        return
    if not allow_empty and not tags:
        errors.append(f"{path}: at least one dependency tag is required")
    if len(tags) != len(set(tags)):
        errors.append(f"{path}: duplicate dependency tag")
    for tag in tags:
        if tag not in DEPENDENCY_TAGS:
            errors.append(f"{path}: unknown dependency tag {tag!r}")


def _check_evidence_refs(
    refs: object,
    path: str,
    errors: list[str],
    evidence_ids: set[str],
    *,
    required: bool,
) -> None:
    if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
        errors.append(f"{path}: expected an evidence-id array")
        return
    if required and not refs:
        errors.append(f"{path}: certified result requires evidence")
    if len(refs) != len(set(refs)):
        errors.append(f"{path}: duplicate evidence reference")
    for ref in refs:
        if ref not in evidence_ids:
            errors.append(f"{path}: unknown evidence reference {ref!r}")


def _validate_evidence(record: dict[str, Any], errors: list[str]) -> set[str]:
    artifacts = record.get("evidence_artifacts")
    if not isinstance(artifacts, list):
        errors.append("$.evidence_artifacts: expected array")
        return set()
    ids: set[str] = set()
    for index, artifact in enumerate(artifacts):
        path = f"$.evidence_artifacts[{index}]"
        keys = {"evidence_id", "path", "sha256", "dependency_tags", "claim_scope"}
        _require_keys(artifact, keys, path, errors)
        if not isinstance(artifact, dict):
            continue
        evidence_id = artifact.get("evidence_id")
        if not isinstance(evidence_id, str) or re.fullmatch(r"[a-z0-9_]+", evidence_id) is None:
            errors.append(f"{path}.evidence_id: invalid identifier")
        elif evidence_id in ids:
            errors.append(f"{path}.evidence_id: duplicate identifier")
        else:
            ids.add(evidence_id)
        _check_tags(artifact.get("dependency_tags"), f"{path}.dependency_tags", errors, allow_empty=False)
        relative = artifact.get("path")
        expected_hash = artifact.get("sha256")
        if not isinstance(relative, str) or not relative:
            errors.append(f"{path}.path: expected nonempty repository-relative path")
            continue
        target = (ROOT / relative).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{path}.path: path escapes repository root")
            continue
        if not target.is_file():
            errors.append(f"{path}.path: evidence file does not exist")
        elif not isinstance(expected_hash, str) or _sha256(target) != expected_hash:
            errors.append(f"{path}.sha256: content hash mismatch")
    return ids


def _validate_matrix_cell(
    cell: object,
    path: str,
    errors: list[str],
    evidence_ids: set[str],
) -> None:
    keys = {"status", "result", "dependency_tags", "evidence_refs"}
    _require_keys(cell, keys, path, errors)
    if not isinstance(cell, dict):
        return
    status = cell.get("status")
    if status not in {"NOT_TESTED", "OPEN", "NOT_APPLICABLE", "CERTIFIED_BASELINE", "CERTIFIED"}:
        errors.append(f"{path}.status: invalid matrix status")
    certified = status in CERTIFIED
    if certified and not isinstance(cell.get("result"), str):
        errors.append(f"{path}.result: certified cell requires a result")
    if not certified and cell.get("result") is not None:
        errors.append(f"{path}.result: open/untested cell must remain null")
    _check_tags(cell.get("dependency_tags"), f"{path}.dependency_tags", errors, allow_empty=not certified)
    _check_evidence_refs(cell.get("evidence_refs"), f"{path}.evidence_refs", errors, evidence_ids, required=certified)


def _validate_charge(setting: dict[str, Any], path: str, errors: list[str], evidence_ids: set[str]) -> None:
    charge = setting.get("charge_test")
    keys = {
        "status", "delta_H_D", "integrability", "flux", "conservation",
        "reference_normalization", "phase_space_preserved", "surface_corner_terms",
        "strongest_counterexample", "evidence_refs",
    }
    _require_keys(charge, keys, f"{path}.charge_test", errors)
    if not isinstance(charge, dict):
        return
    status = charge.get("status")
    if status not in {"NOT_TESTED", "OPEN", "CERTIFIED"}:
        errors.append(f"{path}.charge_test.status: invalid status")
    required_evidence = status == "CERTIFIED"
    _check_evidence_refs(
        charge.get("evidence_refs"),
        f"{path}.charge_test.evidence_refs",
        errors,
        evidence_ids,
        required=required_evidence,
    )
    verdict = setting.get("verdict")
    assessment = setting.get("assessment_status")
    tags = setting.get("verdict_dependency_tags")
    if assessment == "CERTIFIED":
        if verdict not in VERDICTS:
            errors.append(f"{path}.verdict: certified setting requires one scientific verdict")
        if status != "CERTIFIED":
            errors.append(f"{path}.charge_test.status: certified verdict requires certified charge test")
        if not tags:
            errors.append(f"{path}.verdict_dependency_tags: certified verdict requires dependency tags")
        if setting.get("claim_scope") in {"COVARIANT_SMOOTH", "LORENTZIAN_BOUNDARY"} and (
            not isinstance(tags, list) or "LORENTZIAN-CAUSAL" not in tags
        ):
            errors.append(f"{path}.verdict_dependency_tags: covariant/Lorentzian verdict requires LORENTZIAN-CAUSAL")
    else:
        if verdict is not None:
            errors.append(f"{path}.verdict: open/untested setting must use null")
        if tags:
            errors.append(f"{path}.verdict_dependency_tags: open/untested setting must be empty")

    if verdict == "D_GAUGE":
        requirements = {
            "delta_H_D": "IDENTICALLY_ZERO",
            "integrability": "INTEGRABLE",
            "flux": "ZERO",
            "conservation": "CONSERVED",
            "reference_normalization": "DECLARED",
            "phase_space_preserved": "YES",
            "surface_corner_terms": "COMPLETE",
        }
        for key, expected in requirements.items():
            if charge.get(key) != expected:
                errors.append(f"{path}.charge_test.{key}: D_GAUGE requires {expected}")
    elif verdict == "D_CHARGED":
        if charge.get("delta_H_D") != "NONZERO_EXAMPLE" and charge.get("flux") != "NONZERO":
            errors.append(f"{path}.charge_test: D_CHARGED requires a nonzero variation example or flux")
        if charge.get("phase_space_preserved") != "YES":
            errors.append(f"{path}.charge_test.phase_space_preserved: D_CHARGED requires YES")
    elif verdict == "SECTOR_DEPENDENT":
        restrictions = setting.get("sector_restrictions")
        if not isinstance(restrictions, list) or len(restrictions) < 2:
            errors.append(f"{path}.sector_restrictions: SECTOR_DEPENDENT requires at least two declared sectors")
        sector_results = setting.get("sector_results")
        if not isinstance(sector_results, list) or len(sector_results) < 2:
            errors.append(f"{path}.sector_results: SECTOR_DEPENDENT requires at least two certified sector results")
        elif {row.get("verdict") for row in sector_results if isinstance(row, dict)} != {"D_GAUGE", "D_CHARGED"}:
            errors.append(f"{path}.sector_results: compact split must exhibit both D_GAUGE and D_CHARGED")
        if charge.get("strongest_counterexample") in {None, ""}:
            errors.append(f"{path}.charge_test.strongest_counterexample: sector verdict requires the charged sector witness")
    elif verdict == "NOT_HAMILTONIAN":
        if charge.get("integrability") != "NONINTEGRABLE" and charge.get("phase_space_preserved") != "NO":
            errors.append(f"{path}.charge_test: NOT_HAMILTONIAN requires nonintegrability or phase-space failure")


def validate_record(record: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["$: expected object"]
    top_keys = {
        "schema", "result_id", "source_commit", "claim_state", "dependency_tags",
        "scientific_verdicts", "settings", "residual_complexes", "work_packages",
        "evidence_artifacts", "verification_receipts", "open_fields", "claim_boundary",
    }
    _require_keys(record, top_keys, "$", errors)
    if record.get("schema") != "pure-weyl-classical-d-quotient-status-v1":
        errors.append("$.schema: unsupported schema")
    if record.get("result_id") != "CLASSICAL_D_QUOTIENT_STATUS":
        errors.append("$.result_id: unexpected result identifier")
    if not isinstance(record.get("source_commit"), str) or re.fullmatch(r"[0-9a-f]{40}", record["source_commit"]) is None:
        errors.append("$.source_commit: expected a full Git commit hash")
    if record.get("scientific_verdicts") != ["D_GAUGE", "D_CHARGED", "SECTOR_DEPENDENT", "NOT_HAMILTONIAN"]:
        errors.append("$.scientific_verdicts: exact ordered verdict vocabulary required")
    _check_tags(record.get("dependency_tags"), "$.dependency_tags", errors, allow_empty=False)
    evidence_ids = _validate_evidence(record, errors)

    settings = record.get("settings")
    if not isinstance(settings, list):
        errors.append("$.settings: expected array")
    else:
        ids = [entry.get("setting_id") if isinstance(entry, dict) else None for entry in settings]
        if ids != SETTING_IDS:
            errors.append("$.settings: exact ordered six-setting matrix required")
        setting_keys = {
            "setting_id", "claim_scope", "phase_space_status", "phase_space", "boundary_conditions",
            "assessment_status", "verdict", "verdict_dependency_tags", "sector_restrictions", "sector_results",
            "charge_test", "cartan_contraction", "causal_homotopy", "one_particle_sector",
            "pairing", "einstein_sector", "assumptions",
        }
        for index, setting in enumerate(settings):
            path = f"$.settings[{index}]"
            _require_keys(setting, setting_keys, path, errors)
            if not isinstance(setting, dict):
                continue
            _check_tags(setting.get("verdict_dependency_tags"), f"{path}.verdict_dependency_tags", errors, allow_empty=True)
            _validate_charge(setting, path, errors, evidence_ids)
            sector_results = setting.get("sector_results")
            if not isinstance(sector_results, list):
                errors.append(f"{path}.sector_results: expected array")
            else:
                seen_sector_ids: set[str] = set()
                for sector_index, sector in enumerate(sector_results):
                    sector_path = f"{path}.sector_results[{sector_index}]"
                    sector_keys = {"sector_id", "phase_space", "verdict", "charge_result", "linearizability", "dependency_tags", "evidence_refs"}
                    _require_keys(sector, sector_keys, sector_path, errors)
                    if not isinstance(sector, dict):
                        continue
                    sector_id = sector.get("sector_id")
                    if not isinstance(sector_id, str) or re.fullmatch(r"[A-Za-z0-9_]+", sector_id) is None:
                        errors.append(f"{sector_path}.sector_id: invalid identifier")
                    elif sector_id in seen_sector_ids:
                        errors.append(f"{sector_path}.sector_id: duplicate identifier")
                    else:
                        seen_sector_ids.add(sector_id)
                    if sector.get("verdict") not in {"D_GAUGE", "D_CHARGED", "NOT_HAMILTONIAN"}:
                        errors.append(f"{sector_path}.verdict: invalid sector verdict")
                    _check_tags(sector.get("dependency_tags"), f"{sector_path}.dependency_tags", errors, allow_empty=False)
                    _check_evidence_refs(sector.get("evidence_refs"), f"{sector_path}.evidence_refs", errors, evidence_ids, required=True)
            for name in ("cartan_contraction", "causal_homotopy", "one_particle_sector", "pairing", "einstein_sector"):
                _validate_matrix_cell(setting.get(name), f"{path}.{name}", errors, evidence_ids)

    complexes = record.get("residual_complexes")
    if not isinstance(complexes, list):
        errors.append("$.residual_complexes: expected array")
    else:
        ids = [entry.get("complex_id") if isinstance(entry, dict) else None for entry in complexes]
        if ids != COMPLEX_IDS:
            errors.append("$.residual_complexes: exact ordered four-complex comparison required")
        for index, item in enumerate(complexes):
            path = f"$.residual_complexes[{index}]"
            keys = {"complex_id", "definition_status", "computation_status", "definition", "dependency_tags", "cohomology_dimensions", "one_particle_result", "gram_matrix", "representatives", "trivializations", "evidence_refs", "open_fields"}
            _require_keys(item, keys, path, errors)
            if not isinstance(item, dict):
                continue
            certified = item.get("computation_status") in CERTIFIED
            partial = item.get("computation_status") == "PARTIAL"
            _check_tags(item.get("dependency_tags"), f"{path}.dependency_tags", errors, allow_empty=not (certified or partial))
            _check_evidence_refs(item.get("evidence_refs"), f"{path}.evidence_refs", errors, evidence_ids, required=certified or partial)
            if certified and item.get("cohomology_dimensions") is None:
                errors.append(f"{path}.cohomology_dimensions: certified computation requires dimensions")
            if not certified and not partial:
                for field in ("cohomology_dimensions", "one_particle_result", "gram_matrix"):
                    if item.get(field) is not None:
                        errors.append(f"{path}.{field}: open computation must remain null")
            definition = item.get("definition")
            if item.get("complex_id") == "D_global_symmetry" and isinstance(definition, str):
                lowered = definition.lower().replace(" ", "")
                if "setsubtraction" in lowered or "so(4,2)\\<d>" in lowered:
                    errors.append(f"{path}.definition: set subtraction is not a Lie algebra construction")

    packages = record.get("work_packages")
    package_ids = ["charge", "alternative_complexes", "relational_clock", "background_deformation"]
    if not isinstance(packages, dict) or set(packages) != set(package_ids):
        errors.append("$.work_packages: exact four work packages required")
    elif isinstance(packages, dict):
        for name in package_ids:
            package = packages[name]
            path = f"$.work_packages.{name}"
            keys = {"status", "dependency_tags", "result", "evidence_refs", "next_gate"}
            _require_keys(package, keys, path, errors)
            if not isinstance(package, dict):
                continue
            certified = package.get("status") == "CERTIFIED"
            partial = package.get("status") == "PARTIAL"
            obstructed = package.get("status") == "OBSTRUCTED"
            evidenced = certified or partial or obstructed
            _check_tags(package.get("dependency_tags"), f"{path}.dependency_tags", errors, allow_empty=not evidenced)
            _check_evidence_refs(package.get("evidence_refs"), f"{path}.evidence_refs", errors, evidence_ids, required=evidenced)
            if evidenced and not isinstance(package.get("result"), str):
                errors.append(f"{path}.result: certified/partial/obstructed package requires a result")
            if not evidenced and package.get("result") is not None:
                errors.append(f"{path}.result: noncertified package must remain null")

        clock = packages.get("relational_clock")
        scalar_setting = next(
            (
                setting
                for setting in settings
                if isinstance(setting, dict)
                and setting.get("setting_id") == "cylinder_scalar_clock"
            ),
            None,
        )
        neutral_setting = next(
            (
                setting
                for setting in settings
                if isinstance(setting, dict)
                and setting.get("setting_id") == "cylinder_neutral_clock_pair"
            ),
            None,
        )
        berger_setting = next(
            (
                setting
                for setting in settings
                if isinstance(setting, dict)
                and setting.get("setting_id") == "positive_berger_clock"
            ),
            None,
        )
        if isinstance(clock, dict) and clock.get("status") == "PARTIAL":
            if clock.get("evidence_refs") != [
                "scalar_clock_vertical_slice",
                "neutral_conformal_clock_pair",
                "neutral_clock_bv_health_audit",
                "homogeneous_positive_conformal_stealth_clock",
                "inhomogeneous_conformal_stealth_clock_no_go",
                "positive_berger_clock_background",
                "berger_clock_reduced_charge_seed",
                "berger_fixed_coupling_delta_charge",
            ]:
                errors.append("$.work_packages.relational_clock: partial replacement requires the one-scalar, neutral-pair, health, stealth, and positive Berger-background certificates")
            if not isinstance(scalar_setting, dict):
                errors.append("$.settings: missing scalar-clock setting")
            elif scalar_setting.get("verdict") is not None or scalar_setting.get("assessment_status") != "OPEN":
                errors.append("$.settings.cylinder_scalar_clock: obstructed candidate must remain open without a D verdict")
            if not isinstance(neutral_setting, dict):
                errors.append("$.settings: missing neutral-clock setting")
            elif (
                neutral_setting.get("verdict") != "D_GAUGE"
                or neutral_setting.get("assessment_status") != "CERTIFIED"
                or neutral_setting.get("claim_scope") != "REDUCED_MODE"
            ):
                errors.append("$.settings.cylinder_neutral_clock_pair: replacement requires the scoped homogeneous D_GAUGE theorem")
            if not isinstance(berger_setting, dict):
                errors.append("$.settings: missing positive-Berger-clock setting")
            elif (
                berger_setting.get("verdict") != "D_GAUGE"
                or berger_setting.get("assessment_status") != "CERTIFIED"
                or berger_setting.get("claim_scope") != "REDUCED_MODE"
                or berger_setting.get("charge_test", {}).get("status")
                != "CERTIFIED"
                or berger_setting.get("phase_space_status") != "SPECIFIED"
            ):
                errors.append("$.settings.positive_berger_clock: fixed-coupling linearized D_GAUGE theorem is required")

    receipts = record.get("verification_receipts")
    if not isinstance(receipts, list) or not receipts:
        errors.append("$.verification_receipts: at least one receipt is required")
    elif isinstance(receipts, list):
        receipt_keys = {"command", "elapsed_seconds", "status", "test_tier", "higher_tiers_not_run", "escalation_criterion"}
        for index, receipt in enumerate(receipts):
            path = f"$.verification_receipts[{index}]"
            _require_keys(receipt, receipt_keys, path, errors)
            if not isinstance(receipt, dict):
                continue
            if receipt.get("status") == "PASS" and not isinstance(receipt.get("elapsed_seconds"), (int, float)):
                errors.append(f"{path}.elapsed_seconds: PASS requires elapsed time")
            if receipt.get("status") == "NOT_RUN" and receipt.get("elapsed_seconds") is not None:
                errors.append(f"{path}.elapsed_seconds: NOT_RUN requires null")

    if record.get("claim_state") == "COMPLETE":
        if not isinstance(settings, list) or any(entry.get("assessment_status") != "CERTIFIED" for entry in settings if isinstance(entry, dict)):
            errors.append("$.claim_state: COMPLETE requires all six setting verdicts")
        if not isinstance(packages, dict) or any(packages[name].get("status") != "CERTIFIED" for name in package_ids):
            errors.append("$.claim_state: COMPLETE requires all four work packages")
    return sorted(set(errors))


def _mutation_guards(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def rejected(name: str, mutant: dict[str, Any]) -> None:
        if not validate_record(mutant):
            failures.append(name)

    mutant = deepcopy(record)
    for setting in mutant["settings"]:
        if setting["assessment_status"] != "CERTIFIED":
            setting["verdict"] = "D_GAUGE"
            break
    rejected("open_verdict_promoted", mutant)

    mutant = deepcopy(record)
    mutant["settings"][0]["assessment_status"] = "CERTIFIED"
    mutant["settings"][0]["verdict"] = None
    rejected("certified_without_verdict", mutant)

    mutant = deepcopy(record)
    setting = mutant["settings"][0]
    setting["assessment_status"] = "CERTIFIED"
    setting["verdict"] = "D_GAUGE"
    setting["verdict_dependency_tags"] = ["LORENTZIAN-CAUSAL"]
    setting["charge_test"]["status"] = "CERTIFIED"
    setting["charge_test"]["evidence_refs"] = setting["causal_homotopy"]["evidence_refs"]
    rejected("gauge_without_zero_charge_receipt", mutant)

    mutant = deepcopy(record)
    mutant["evidence_artifacts"][0]["sha256"] = "0" * 64
    rejected("tampered_evidence_hash", mutant)

    mutant = deepcopy(record)
    mutant["scientific_verdicts"] = ["D_GAUGE", "D_CHARGED", "SECTOR_DEPENDENT", "OPEN"]
    rejected("verdict_vocabulary_drift", mutant)

    mutant = deepcopy(record)
    mutant["residual_complexes"][1]["definition"] = "so(4,2)\\<D> set subtraction"
    rejected("illegal_set_subtraction", mutant)

    mutant = deepcopy(record)
    neutral = next(
        setting
        for setting in mutant["settings"]
        if setting["setting_id"] == "cylinder_neutral_clock_pair"
    )
    neutral["claim_scope"] = "COVARIANT_SMOOTH"
    rejected("neutral_clock_scope_escape", mutant)

    mutant = deepcopy(record)
    mutant["work_packages"]["relational_clock"]["evidence_refs"] = [
        "neutral_conformal_clock_pair"
    ]
    rejected("single_scalar_obstruction_erased", mutant)

    mutant = deepcopy(record)
    mutant["work_packages"]["relational_clock"]["evidence_refs"] = [
        "scalar_clock_vertical_slice",
        "neutral_conformal_clock_pair",
        "neutral_clock_bv_health_audit",
    ]
    rejected("homogeneous_stealth_obstruction_erased", mutant)

    mutant = deepcopy(record)
    mutant["work_packages"]["relational_clock"]["evidence_refs"] = [
        "scalar_clock_vertical_slice",
        "neutral_conformal_clock_pair",
        "neutral_clock_bv_health_audit",
        "homogeneous_positive_conformal_stealth_clock",
    ]
    rejected("complete_stealth_obstruction_erased", mutant)

    mutant = deepcopy(record)
    berger = next(
        setting
        for setting in mutant["settings"]
        if setting["setting_id"] == "positive_berger_clock"
    )
    berger["verdict"] = "D_CHARGED"
    rejected("berger_fixed_coupling_D_GAUGE_erased", mutant)

    mutant = deepcopy(record)
    mutant["work_packages"]["relational_clock"]["evidence_refs"] = [
        ref
        for ref in mutant["work_packages"]["relational_clock"]["evidence_refs"]
        if ref != "berger_clock_reduced_charge_seed"
    ]
    rejected("berger_clock_momentum_erased", mutant)

    mutant = deepcopy(record)
    mutant["work_packages"]["relational_clock"]["evidence_refs"] = [
        ref
        for ref in mutant["work_packages"]["relational_clock"]["evidence_refs"]
        if ref != "berger_fixed_coupling_delta_charge"
    ]
    rejected("berger_fixed_coupling_verdict_erased", mutant)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    # Parsing the declared JSON Schema is a Tier-0 guard even though this
    # dependency-free checker enforces the scientific cross-field rules.
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if schema.get("$id") != "https://area9.dk/schemas/pure-weyl-classical-d-quotient-status-v1.schema.json":
        print("schema: unexpected $id", file=sys.stderr)
        return 1
    record = json.loads(args.certificate.read_text(encoding="utf-8"))
    errors = validate_record(record)
    if errors:
        for error in errors:
            print(f"{args.certificate}: {error}", file=sys.stderr)
        return 1
    if args.guards:
        failures = _mutation_guards(record)
        if failures:
            for failure in failures:
                print(f"mutation guard failed: {failure}", file=sys.stderr)
            return 1
        print("mutation guards: 13/13 PASS")
    print(f"{args.certificate}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
