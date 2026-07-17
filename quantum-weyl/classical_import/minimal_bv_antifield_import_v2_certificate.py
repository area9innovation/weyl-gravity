"""Import and independently replay the classical minimal-BV antifield V2 export."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .verify_antifield_export_v2 import validate_export_v2


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPORT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
HISTORICAL_OBSTRUCTION = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION.json"
CONTRACT = HERE / "certificates/ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT.json"
EXPORT_SCHEMA = HERE / "schema/antifield_export_v2.schema.json"
SCHEMA = HERE / "schema/minimal_bv_antifield_import_v2_certificate.schema.json"
OUTPUT = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
SOURCE_PATHS = (
    "quantum-weyl/classical_import/minimal_bv_antifield_import_v2_certificate.py",
    "quantum-weyl/classical_import/verify_minimal_bv_antifield_import_v2.py",
    "quantum-weyl/classical_import/verify_antifield_export_v2.py",
    "quantum-weyl/classical_import/schema/antifield_export_v2.schema.json",
    "quantum-weyl/classical_import/schema/minimal_bv_antifield_import_v2_certificate.schema.json",
    "quantum-weyl/classical_import/tests/test_minimal_bv_antifield_import_v2_certificate.py",
    "quantum-weyl/classical_import/REPORT_V2.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}


def build() -> dict[str, Any]:
    payload = json.loads(EXPORT.read_text())
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(export_schema).validate(payload)
    replay = validate_export_v2(payload, repository_root=ROOT)
    dependencies = {
        "classical_export": _reference(EXPORT),
        "executable_receiving_contract": _reference(CONTRACT),
        "historical_receiver_obstruction": _reference(HISTORICAL_OBSTRUCTION),
    }
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    return {
        "schema": "quantum-weyl-minimal-bv-antifield-import-v2-certificate",
        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2",
        "result_state": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_IMPORTED_INDEPENDENTLY_REPLAYED",
        "classical_commit": payload["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "imported_export": {
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "generator_count": replay["generator_count"],
            "atom_count": replay["atom_count"],
            "component_shifts": replay["component_shifts"],
            "canonical_hashes": replay["canonical_hashes"],
        },
        "independent_replay": replay,
        "receiver_obstruction_resolution": {
            "historical_failure": "filtered adapter closure did not stabilize",
            "repair": "project exact generated monomials to the declared graded scope before finite block assembly",
            "scope_projection_status": replay["filtered_complex_adapter"]["scope_projection"]["status"],
            "projected_monomial_count": replay["filtered_complex_adapter"]["scope_projection"]["projected_monomial_count"],
            "untruncated_generator_identities_retained": True,
            "bounded_filtered_identities_replayed": True,
        },
        "claim_flags": {
            "ANTIFIELD_EXPORT_V2_RECEIVER_READY": True,
            "CLASSICAL_ANTIFIELD_EXPORT_IMPORTED": True,
            "CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT": True,
            "FILTERED_COMPLEX_ADAPTER_REPLAYED": True,
            "MINIMAL_BV_H04_H14_COMPUTED": False,
            "FULL_BV_G2_COMPLETE": False,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "MINIMAL_BV_H04_H14_WITH_KOSZUL_TATE_ROWS",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC receipt imports the classical covariant minimal-BV antifield "
            "export and independently replays its exact rational delta, gamma and Q rows. "
            "Generator-level Q decomposition, delta squared, the delta-gamma anticommutator and "
            "Q squared are checked before truncation; the declared ghost, antifield, form, "
            "engineering-dimension and derivative window is then enforced and the resulting "
            "finite sparse blocks pass the filtered-complex and AFN0 identities. All classical "
            "dependencies and producer proof artifacts are content-addressed and checked both in "
            "the working tree and at the frozen classical commit, while producer booleans are not "
            "used as authority. This resolves the historical receiver-only finite-closure "
            "obstruction. It does not compute the minimal-BV relative cohomology quotient, decide "
            "whether AFN0 representatives lift or become exact, calculate a repository Slavnov "
            "breaking or anomaly coefficient, restore the QME, transfer a quantum differential, "
            "or establish a Lorentzian or quantum theory."
        ),
        "resource_policy": {
            "arrival_and_replay": "completed with the scoped contract and classical integration tests",
            "minimal_BV_quotient_trigger": replay["canonical_hashes"],
            "full_repository_suite_required_when": [
                "the shared canonical algebra changes",
                "the relative-cohomology or filtered-complex engine changes",
                "the minimal-BV quotient is promoted to a theorem-level result",
            ],
        },
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "dependency_manifest_sha256": _canonical_hash(dependencies),
        },
    }


def validate(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("ANTIFIELD_EXPORT_V2_RECEIVER_READY") is not True
        or flags.get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED") is not True
        or flags.get("CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT") is not True
        or flags.get("FILTERED_COMPLEX_ADAPTER_REPLAYED") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "MINIMAL_BV_H04_H14_COMPUTED",
                "FULL_BV_G2_COMPLETE",
                "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
                "QME_RESTORED",
                "QUANTUM_CLAIM",
            )
        )
        or value.get("next_gate") != "MINIMAL_BV_H04_H14_WITH_KOSZUL_TATE_ROWS"
    ):
        raise ValueError("minimal-BV antifield import crossed its claim boundary")


def _text(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    content = _text(value)
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and OUTPUT.read_text() != content:
        raise SystemExit(f"stale minimal-BV antifield import: {OUTPUT}")
    print("CLASSICAL MINIMAL-BV ANTIFIELD V2 IMPORT: ACCEPTED; QUOTIENT OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
