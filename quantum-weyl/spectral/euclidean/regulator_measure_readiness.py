"""Readiness certificate for the repository regulator/zero-mode/measure ledger."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from .regulator_measure_receiver import SCHEMA as INPUT_SCHEMA
from .regulator_measure_receiver import synthetic_payload, validate_regulator_measure_ledger


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_READINESS.json"
SCHEMA = HERE / "schema/repository-regulator-zero-mode-measure-readiness-v1.schema.json"
DEPENDENCIES = {
    "standard_slice": HERE / "certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json",
    "physical_multiplicity": HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "elliptic_readiness": HERE / "certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_READINESS.json",
    "snapshot_compatibility": ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json",
    "negative_scalar_phase": HERE / "certificates/ROUND_S4_NEGATIVE_SCALAR_PHASE_LOCALITY.json",
    "conformal_zero_mode_volume": HERE / "certificates/ROUND_S4_CONFORMAL_ZERO_MODE_VOLUME_LOCALITY.json",
}
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/regulator_measure_receiver.py",
    "quantum-weyl/spectral/euclidean/regulator_measure_readiness.py",
    "quantum-weyl/spectral/euclidean/verify_regulator_measure_readiness.py",
    "quantum-weyl/spectral/euclidean/schema/repository-regulator-zero-mode-measure-input-v1.schema.json",
    "quantum-weyl/spectral/euclidean/schema/repository-regulator-zero-mode-measure-readiness-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_regulator_measure_readiness.py",
    "quantum-weyl/reports/repository-regulator-zero-mode-measure-readiness.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _rehash(payload: dict[str, Any]) -> None:
    payload["proof_sha256"] = _canonical_hash({key: payload[key] for key in ("classical_commit", "analytic_route", "background", "factor_ledger", "aggregate_checks", "measure_policy", "zero_mode_policy", "regulator_policy", "contour_and_phase_policy", "proof_artifacts")})


def mutation_receipts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None], bool], ...] = (
        ("weighted_rank", lambda row: row["aggregate_checks"]["weighted_logdet_rank"].update(numerator=1), True),
        ("zero_mode_total", lambda row: row["aggregate_checks"].update(total_zero_mode_dimension=2), True),
        ("priming", lambda row: row["factor_ledger"][1].update(primed=False), True),
        ("proof_digest", lambda row: row.update(proof_sha256="0" * 64), False),
    )
    receipts = []
    for name, mutate, rehash in mutations:
        mutant = deepcopy(payload)
        mutate(mutant)
        if rehash:
            _rehash(mutant)
        try:
            validate_regulator_measure_ledger(mutant, repository_root=ROOT, allow_synthetic_fixture=True)
        except Exception:
            rejected = True
        else:
            rejected = False
        receipts.append({"mutation": name, "rejected": rejected})
    return receipts


def build() -> dict[str, Any]:
    fixture = synthetic_payload(repository_root=ROOT)
    receipt = validate_regulator_measure_ledger(fixture, repository_root=ROOT, allow_synthetic_fixture=True)
    mutations = mutation_receipts(fixture)
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["standard_slice"].get("result_id") != "STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE":
        raise ValueError("standard integration slice drifted")
    if values["physical_multiplicity"].get("result_state") != "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED":
        raise ValueError("physical multiplicity ledger drifted")
    if values["elliptic_readiness"].get("claim_flags", {}).get("REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED") is not False:
        raise ValueError("elliptic readiness boundary drifted")
    phase_flags = values["negative_scalar_phase"].get("claim_flags", {})
    if (
        phase_flags.get(
            "PHASE_IRRELEVANT_TO_LOCAL_SLAVNOV_BREAKING_ON_FIXED_SIGN_CHAMBER"
        )
        is not True
        or phase_flags.get("GLOBAL_DETERMINANT_BRANCH_SELECTED") is not False
    ):
        raise ValueError("negative scalar phase locality drifted")
    volume_flags = values["conformal_zero_mode_volume"].get("claim_flags", {})
    if (
        volume_flags.get(
            "VOLUME_NORMALIZATION_IRRELEVANT_TO_LOCAL_SLAVNOV_FIXED_STRATUM"
        )
        is not True
        or volume_flags.get("GLOBAL_COLLECTIVE_COORDINATE_MEASURE_NORMALIZED")
        is not False
    ):
        raise ValueError("conformal zero-mode volume locality drifted")
    candidates = [
        {"candidate_id": values["standard_slice"]["result_id"], "repository_bound": False, "measure": True, "zero_modes": True, "local_regulator": True, "global_phase_policy": True, "complete": False, "disposition": "STANDARD_BACKGROUND_SLICE_PHASE_LOCALLY_IRRELEVANT_REPOSITORY_BINDING_OPEN"},
        {"candidate_id": values["physical_multiplicity"]["result_id"], "repository_bound": True, "measure": True, "zero_modes": True, "local_regulator": False, "global_phase_policy": False, "complete": False, "disposition": "REPOSITORY_MULTIPLICITY_LEDGER_NOT_REGULATOR_OR_GLOBAL_PHASE_LEDGER"},
        {"candidate_id": values["elliptic_readiness"]["result_id"], "repository_bound": False, "measure": False, "zero_modes": False, "local_regulator": False, "global_phase_policy": False, "complete": False, "disposition": "ELLIPTIC_RECEIVER_READY_PHYSICAL_COMPLEX_UNSUPPLIED"},
    ]
    proof_payload = {"dependency_hashes": {name: _sha256(path) for name, path in DEPENDENCIES.items()}, "receipt": receipt, "mutations": mutations, "candidates": candidates}
    return {
        "schema": "quantum-weyl-repository-regulator-zero-mode-measure-readiness-v1",
        "result_id": "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_READINESS",
        "result_state": "COMPOSITIONAL_RECEIVER_READY_PHYSICAL_LEDGER_NOT_SUPPLIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "dependency_hashes": proof_payload["dependency_hashes"],
        "accepted_contract": {"required_result_id": "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER", "input_schema_path": str(INPUT_SCHEMA.relative_to(ROOT)), "physical_input_status": "NOT_SUPPLIED"},
        "receiver_mechanics": {"synthetic_receipt": receipt, "mutation_receipts": mutations},
        "current_candidate_audit": candidates,
        "claim_flags": {"REGULATOR_ZERO_MODE_MEASURE_RECEIVER_READY": True, "NEGATIVE_SCALAR_PHASE_LOCALITY_BOUND": True, "CONFORMAL_ZERO_MODE_VOLUME_LOCALITY_BOUND": True, "CURRENT_CANDIDATES_AUDITED": True, "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED": False, "REGULATED_SLAVNOV_BREAKING_COMPUTED": False, "QME_DISPOSITION": False},
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER",
        "claim_boundary": "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL readiness certificate defines a compositional receiver for the repository full-BV determinant measure, zero-mode priming and symmetry-volume policy, covariant local regulator, indefinite-direction contours, and global phase disposition. The standard round-S4 slice supplies local factor evidence and the accepted multiplicity ledger supplies repository row binding, but neither artifact alone supplies the complete carrier. Receiver mechanics use a synthetic fixture only. No physical combined ledger, regulated Slavnov breaking, QME disposition, or Lorentzian quantum theory is claimed.",
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
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
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale regulator/measure readiness: {OUTPUT}")
    print("repository regulator/zero-mode/measure readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
