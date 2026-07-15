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
EVIDENCE_COMMIT = "0e919d434ce09c4dbab042c0c2aa708126409685"
EVIDENCE_PATH = (
    "physics/symplectic-reconstruction/quantum-weyl/cartan/"
    "certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json"
)
WORKING_EVIDENCE_PATH = (
    PACKAGE_ROOT / "certificates" / "CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json"
)


def _git_root() -> Path:
    output = subprocess.check_output(
        ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "--show-toplevel"],
        text=True,
    )
    return Path(output.strip())


def _evidence_bytes() -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(_git_root()), "show", f"{EVIDENCE_COMMIT}:{EVIDENCE_PATH}"]
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
    if evidence.get("result_id") != "CARTAN_DEFECT_COMPLEX_PRECERTIFICATE":
        raise ValueError("pinned evidence is not the Cartan defect precertificate")
    if evidence.get("result_state") != "ALGEBRAIC_ENGINE_READY_PHYSICAL_CANDIDATES_INPUT_BLOCKED":
        raise ValueError("pinned Cartan evidence has an unexpected result state")
    if evidence["lifecycle_gates"]["QME_RESTORED"] != "NOT_REACHED":
        raise ValueError("blocked contribution cannot cite a restored QME")
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
        ],
        "not_established": [
            "a complete bulk pure-Weyl Cartan-obstruction candidate basis",
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
            "PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check",
            "PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check",
            "PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/cartan/tests -v",
        ],
        "next_gate": "complete the AFN0 lower-form total complex, then instantiate the admissible bulk Cartan-obstruction basis; consume separately gated clock inputs only after their total-D and shared classical BV exports land",
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
        ["git", "-C", str(_git_root()), "show", f"{evidence['commit']}:{evidence['path']}"]
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
