"""Emit the quantum-team contribution to the cross-programme D dossier."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
REPOSITORY_ROOT = QUANTUM_ROOT.parent
PROGRAMME_ROOT = REPOSITORY_ROOT / "d_quotient_programme"
OUTPUT_PATH = PACKAGE_ROOT / "contributions" / "QUANTUM_CARTAN_BLOCKED.json"
SCHEMA_PATH = PROGRAMME_ROOT / "schema" / "team-contribution-v1.schema.json"
GENERATOR_REGISTRY_PATH = PROGRAMME_ROOT / "registry" / "generators.json"
PHASE_SPACE_REGISTRY_PATH = PROGRAMME_ROOT / "registry" / "phase_spaces.json"
EVIDENCE_COMMIT = "db533d49e7644fc2482f472a8ed2f41e06469314"
EVIDENCE_PATH = (
    "quantum-weyl/cartan/certificates/"
    "LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json"
)
WORKING_EVIDENCE_PATH = (
    PACKAGE_ROOT / "certificates" / "LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json"
)


def _evidence_bytes() -> bytes:
    return subprocess.check_output(
        [
            "git",
            "-C",
            str(REPOSITORY_ROOT),
            "show",
            f"{EVIDENCE_COMMIT}:./{EVIDENCE_PATH}",
        ]
    )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _registry_entry(path: Path, key: str, value: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    collection = "generators" if key == "generator_id" else "phase_spaces"
    matches = [item for item in payload[collection] if item[key] == value]
    if len(matches) != 1:
        raise ValueError(f"registry does not contain exactly one {key}={value}")
    return matches[0]


def build_contribution() -> dict[str, Any]:
    evidence_bytes = _evidence_bytes()
    evidence = json.loads(evidence_bytes)
    if evidence.get("result_id") != "LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON":
        raise ValueError("pinned evidence is not the local/D-Cartan comparison")
    if evidence.get("result_state") != "LOCAL_D_PULLBACK_COMPUTED_TARGET_CHAIN_MAP_UNDEFINED":
        raise ValueError("pinned comparison evidence has an unexpected result state")
    comparison = evidence.get("cartan_defect_comparison", {})
    if comparison.get("classification_status") != "NO_VERDICT":
        raise ValueError("blocked contribution cannot cite a Cartan verdict")
    if comparison.get("zero_local_pullback_implies_zero_cartan_defect") is not False:
        raise ValueError("local zero was incorrectly promoted to a Cartan result")
    if WORKING_EVIDENCE_PATH.read_bytes() != evidence_bytes:
        raise ValueError("working Cartan certificate differs from the pinned evidence commit")
    _registry_entry(GENERATOR_REGISTRY_PATH, "generator_id", "D_compact")
    phase_space = _registry_entry(
        PHASE_SPACE_REGISTRY_PATH, "phase_space_id", "compact_quantum"
    )
    return {
        "schema": "pure-weyl-d-quotient-team-contribution-v1",
        "team_id": "quantum",
        "setting_id": "vacuum_cylinder",
        "generator_id": "D_compact",
        "phase_space_id": "compact_quantum",
        "boundary_conditions": phase_space["boundary_conditions"],
        "lifecycle_layer": "QUANTUM",
        "claim_status": "BLOCKED",
        "verdict": None,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "established": [
            "exact first-order sourced Cartan-defect identity",
            "admissible-operator quotient mechanics with primitive and dual witnesses",
            "first-order scheme covariance with illegal scheme shifts rejected",
            "semantic import of the classical compact-cylinder sector split without quantum promotion",
            "complete intrinsic Euler descent included in the truncated AFN0 even-anomaly closure slice",
            "hash-bound AFN0 closure witnesses with semantic agreement checks against the descent database",
            "complete even Weyl-ghost AFN0 candidate quotient with normalized dual witnesses for omega C2 and omega E4",
            "complete odd Weyl-ghost AFN0 candidate quotient with a normalized dual witness for omega C dual C",
            "zero direct local bulk D_compact anomaly pullback on the closed vacuum cylinder because sigma_D=0",
            "source/target degree audit and minimal missing-carrier theorem for the renormalized local Ward-insertion map",
        ],
        "not_established": [
            "a complete Diff and antifield-dependent pure-Weyl anomaly basis",
            "a local-anomaly to admissible D-Cartan chain map",
            "a renormalized observable algebra or actual Q_1",
            "a restored local quantum master equation",
            "a residual quantum transfer, coefficient, or pairing correction",
            "a scalar-clock, boundary, corner, or Lorentzian causal quantum theorem",
        ],
        "evidence": {
            "path": EVIDENCE_PATH,
            "commit": EVIDENCE_COMMIT,
            "sha256": _sha256(evidence_bytes),
        },
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 -m cartan.local_anomaly_comparison_certificate --check",
            "PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check",
            "PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/cartan/tests -v",
        ],
        "next_gate": "import the full classical antifield/Koszul-Tate and D-action export, compute the regulated Slavnov breaking, and construct the renormalized local Ward-insertion map into the admissible D-Cartan complex; consume separately gated clock inputs only after their total-D and shared classical BV exports land",
    }


def validate_contribution(record: object) -> None:
    if not isinstance(record, dict):
        raise ValueError("team contribution must be an object")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = set(schema["required"])
    properties = schema["properties"]
    if set(record) != required:
        raise ValueError("team contribution fields differ from the exact schema")
    for field in ("schema",):
        if record[field] != properties[field]["const"]:
            raise ValueError(f"team contribution has invalid {field}")
    for field in ("team_id", "lifecycle_layer", "claim_status"):
        if record[field] not in properties[field]["enum"]:
            raise ValueError(f"team contribution has invalid {field}")
    if record["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
        raise ValueError("quantum contribution dependency tags are not fail-closed")
    if record["verdict"] is not None:
        raise ValueError("blocked quantum contribution must not emit a verdict")
    _registry_entry(GENERATOR_REGISTRY_PATH, "generator_id", record["generator_id"])
    _registry_entry(
        PHASE_SPACE_REGISTRY_PATH, "phase_space_id", record["phase_space_id"]
    )
    evidence = record["evidence"]
    if not isinstance(evidence, dict) or set(evidence) != {"path", "commit", "sha256"}:
        raise ValueError("team contribution evidence fields are invalid")
    if re.fullmatch(r"[0-9a-f]{40}", evidence["commit"]) is None:
        raise ValueError("team contribution evidence commit is not a full hash")
    if re.fullmatch(r"[0-9a-f]{64}", evidence["sha256"]) is None:
        raise ValueError("team contribution evidence digest is invalid")
    pinned = subprocess.check_output(
        [
            "git",
            "-C",
            str(REPOSITORY_ROOT),
            "show",
            f"{evidence['commit']}:./{evidence['path']}",
        ]
    )
    if _sha256(pinned) != evidence["sha256"]:
        raise ValueError("team contribution evidence hash does not match its commit")


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contribution = build_contribution()
    validate_contribution(contribution)
    content = _render(contribution)
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"quantum D contribution is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("D-QUOTIENT QUANTUM CONTRIBUTION: BLOCKED, NO VERDICT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
