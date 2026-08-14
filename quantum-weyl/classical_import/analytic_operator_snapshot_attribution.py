"""Attribute the physical analytic producer to the frozen classical BV snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ci.standalone_provenance import read_attached_blob
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_EXPORT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
LOCAL_IMPORT = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
TT_DICTIONARY = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json"
FULL_BV_LEDGER = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
EULER_COEFFICIENT = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json"
OUTPUT = HERE / "certificates/ANALYTIC_OPERATOR_CLASSICAL_SNAPSHOT_ATTESTATION.json"
SCHEMA = HERE / "schema/analytic-operator-snapshot-attribution-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/classical_import/analytic_operator_snapshot_attribution.py",
    "quantum-weyl/classical_import/verify_analytic_operator_snapshot_attribution.py",
    "quantum-weyl/classical_import/schema/analytic-operator-snapshot-attribution-v1.schema.json",
    "quantum-weyl/classical_import/tests/test_analytic_operator_snapshot_attribution.py",
    "quantum-weyl/reports/analytic-operator-classical-snapshot-attribution.md",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE
    ).stdout


def _tree_identity(commit: str) -> dict[str, str]:
    standalone_path = str(SOURCE_EXPORT.relative_to(ROOT))
    tree_path = "physics/symplectic-reconstruction/" + standalone_path
    expected_sha256 = _sha256(SOURCE_EXPORT)
    ref, committed = read_attached_blob(
        commit,
        tree_path,
        expected_sha256,
        root=ROOT,
    )
    blob_sha1 = _git("rev-parse", ref.object_spec).decode().strip()
    return {
        "path": tree_path,
        "blob_sha1": blob_sha1,
        "blob_sha256": _sha256_bytes(committed),
        "bytes_equal_to_worktree_export": committed == SOURCE_EXPORT.read_bytes(),
    }


def _artifact(path: Path, *, format_: str = "JSON_PROOF") -> dict[str, str]:
    return {
        "format": format_,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def validate_attribution(payload: object, *, repository_root: Path = ROOT) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):
        raise ValueError("analytic snapshot attribution is not an object")

    local_import = json.loads((repository_root / payload["proof_artifacts"][0]["path"]).read_text())
    source_export_path = repository_root / payload["proof_artifacts"][1]["path"]
    source_export = json.loads(source_export_path.read_text())
    for index, artifact in enumerate(payload["proof_artifacts"]):
        path = repository_root / artifact["path"]
        if not path.is_file() or _sha256(path) != artifact["sha256"]:
            raise ValueError(f"analytic attribution proof artifact {index} hash mismatch")

    hashes = local_import.get("independent_replay", {}).get("canonical_hashes")
    if (
        local_import.get("result_id") != "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2"
        or source_export.get("result_id") != "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2"
        or local_import.get("classical_commit") != payload["source_classical_commit"]
        or source_export.get("classical_commit") != payload["source_classical_commit"]
        or hashes != payload["canonical_hashes"]
        or source_export.get("canonical_hashes") != hashes
    ):
        raise ValueError("analytic attribution classical content drifted")

    tree = _tree_identity(payload["analytic_producer_commit"])
    if tree != payload["analytic_git_tree_export"]:
        raise ValueError("analytic attribution Git-tree identity drifted")
    if tree["blob_sha256"] != _sha256(source_export_path):
        raise ValueError("analytic attribution worktree export differs from producer tree")

    physical_ids = {
        "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1": TT_DICTIONARY,
        "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER": FULL_BV_LEDGER,
        "REPOSITORY_ROUND_S4_EULER_COEFFICIENT": EULER_COEFFICIENT,
    }
    if [row["result_id"] for row in payload["physical_analytic_artifacts"]] != list(physical_ids):
        raise ValueError("analytic attribution physical artifact order drifted")
    for row in payload["physical_analytic_artifacts"]:
        expected_path = physical_ids[row["result_id"]]
        if (
            row["artifact"] != _artifact(expected_path, format_="JSON_DATA")
            or json.loads(expected_path.read_text()).get("classical_commit")
            != payload["analytic_producer_commit"]
        ):
            raise ValueError("analytic attribution physical artifact binding drifted")

    proof_payload = {
        key: payload[key]
        for key in (
            "analytic_producer_commit",
            "source_classical_commit",
            "canonical_hashes",
            "analytic_git_tree_export",
            "physical_analytic_artifacts",
            "proof_artifacts",
        )
    }
    if payload["proof_sha256"] != _canonical_hash(proof_payload):
        raise ValueError("analytic attribution proof digest drifted")
    return {
        "result_id": payload["result_id"],
        "analytic_producer_commit": payload["analytic_producer_commit"],
        "source_classical_commit": payload["source_classical_commit"],
        "canonical_hashes": payload["canonical_hashes"],
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def build() -> dict[str, Any]:
    local_import = json.loads(LOCAL_IMPORT.read_text())
    source_export = json.loads(SOURCE_EXPORT.read_text())
    tt = json.loads(TT_DICTIONARY.read_text())
    analytic_commit = tt["classical_commit"]
    source_commit = local_import["classical_commit"]
    hashes = local_import["independent_replay"]["canonical_hashes"]
    if source_export.get("classical_commit") != source_commit or source_export.get("canonical_hashes") != hashes:
        raise ValueError("worktree classical export does not match frozen local import")
    tree = _tree_identity(analytic_commit)
    if tree["bytes_equal_to_worktree_export"] is not True:
        raise ValueError("analytic producer does not contain the frozen classical export blob")
    physical = [
        {
            "result_id": result_id,
            "artifact": _artifact(path, format_="JSON_DATA"),
        }
        for result_id, path in (
            ("REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1", TT_DICTIONARY),
            ("REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER", FULL_BV_LEDGER),
            ("REPOSITORY_ROUND_S4_EULER_COEFFICIENT", EULER_COEFFICIENT),
        )
    ]
    proofs = [_artifact(LOCAL_IMPORT), _artifact(SOURCE_EXPORT)]
    proof_payload = {
        "analytic_producer_commit": analytic_commit,
        "source_classical_commit": source_commit,
        "canonical_hashes": hashes,
        "analytic_git_tree_export": tree,
        "physical_analytic_artifacts": physical,
        "proof_artifacts": proofs,
    }
    value = {
        "schema": "quantum-weyl-analytic-operator-snapshot-attribution-v1",
        "result_id": "ANALYTIC_OPERATOR_CLASSICAL_SNAPSHOT_ATTESTATION",
        "result_state": "ANALYTIC_PRODUCER_GIT_TREE_CONTAINS_FROZEN_CLASSICAL_EXPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        **proof_payload,
        "claim_flags": {
            "ANALYTIC_PRODUCER_CLASSICAL_SNAPSHOT_ATTRIBUTED": True,
            "FIVE_CANONICAL_HASHES_MATCH": True,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL attestation proves "
            "that the Git tree of the accepted analytic producer commit contains "
            "byte-for-byte the frozen classical minimal-BV export, whose generator, "
            "atom, differential, dependency, and scope hashes equal the local-BV "
            "import. It attributes the TT dictionary, full-BV multiplicity ledger, "
            "and round-S4 Euler coefficient to that classical snapshot. It does not "
            "compute the C2 coefficient, a regulated Slavnov breaking, or a QME verdict."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_attribution(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale analytic snapshot attribution: {OUTPUT}")
    print("analytic operator classical snapshot attribution: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
