#!/usr/bin/env python3
"""Fail-closed provenance and Lean replay checker for the Physlib bridge."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "physlib-demo"
CERTIFICATE = DEMO / "certificates/PHYSLIB_STRICT_WEYL_SECOND_SOURCE_BRIDGE_V1.json"
SOURCE = DEMO / "WeylPhyslibBridge/StrictWeylSecondSource.lean"
FORGE_SOURCE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
MANIFEST = DEMO / "lake-manifest.json"

EXPECTED_FLAGS = {
    "LEAN_KERNEL_PROOF_COMPILES": True,
    "RATIONAL_COEFFICIENT_CANCELLATION_FORMALIZED": True,
    "SECOND_SOURCE_CLOSURE_IMPLICATION_FORMALIZED": True,
    "SOURCE_Q2_Q3_IDENTITIES_FORMALIZED": False,
    "GREEN_HOMOTOPY_FORMALIZED": False,
    "CAUSAL_SUPPORT_FORMALIZED": False,
    "HADAMARD_FORMALIZED": False,
    "PHYSICAL_POSITIVITY_FORMALIZED": False,
    "LORENTZIAN_QUANTUM_THEORY": False,
}
EXPECTED_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certificate_digest(data: dict[str, Any]) -> str:
    payload = copy.deepcopy(data)
    payload["independent_checker"]["certificate_digest_sha256"] = ""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(CERTIFICATE.read_text()) if data is None else data
    errors: list[str] = []
    if result.get("result_id") != "PHYSLIB_STRICT_WEYL_SECOND_SOURCE_BRIDGE_V1":
        errors.append("result id")
    if result.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency boundary")
    if result.get("claim_flags") != EXPECTED_FLAGS:
        errors.append("claim flags")
    if result.get("axiom_footprint") != EXPECTED_AXIOMS:
        errors.append("axiom footprint")

    provenance = result.get("provenance", {})
    if provenance.get("lean_source", {}).get("sha256") != sha256(SOURCE):
        errors.append("Lean source hash")
    if provenance.get("forge_source_certificate", {}).get("sha256") != sha256(FORGE_SOURCE):
        errors.append("Forge source hash")

    manifest = json.loads(MANIFEST.read_text())
    packages = {item["name"]: item for item in manifest["packages"]}
    pins = result.get("toolchain", {})
    if (DEMO / "lean-toolchain").read_text().strip() != pins.get("lean"):
        errors.append("Lean toolchain pin")
    if packages.get("Physlib", {}).get("rev") != pins.get("physlib_commit"):
        errors.append("Physlib manifest pin")
    if packages.get("mathlib", {}).get("rev") != pins.get("mathlib_commit"):
        errors.append("Mathlib manifest pin")

    source = SOURCE.read_text()
    for theorem in ("rationalCoefficientCancellation", "secondNonlinearSourceClosed"):
        if not re.search(rf"\btheorem\s+{theorem}\b", source):
            errors.append(f"missing theorem {theorem}")
    if re.search(r"\b(sorry|admit|axiom)\b", source):
        errors.append("untrusted declaration token")
    if "import Physlib.Meta.Informal.Basic" not in source:
        errors.append("Physlib import")

    digest = certificate_digest(result)
    if result.get("independent_checker", {}).get("certificate_digest_sha256") != digest:
        errors.append("certificate digest")
    return errors, {
        "certificate_digest_sha256": digest,
        "lean_source_sha256": sha256(SOURCE),
        "forge_source_sha256": sha256(FORGE_SOURCE),
    }


def replay_lean() -> tuple[list[str], dict[str, Any]]:
    command = ["lake", "env", "lean", "WeylPhyslibBridge/StrictWeylSecondSource.lean"]
    completed = subprocess.run(command, cwd=DEMO, text=True, capture_output=True, check=False)
    output = completed.stdout + completed.stderr
    errors: list[str] = []
    if completed.returncode:
        errors.append(f"Lean exited {completed.returncode}")
    for theorem in ("rationalCoefficientCancellation", "secondNonlinearSourceClosed"):
        if theorem not in output:
            errors.append(f"missing axiom report {theorem}")
    for axiom in EXPECTED_AXIOMS:
        if axiom not in output:
            errors.append(f"missing reported axiom {axiom}")
    return errors, {"lean_exit_code": completed.returncode, "axiom_report_seen": not errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-lean", action="store_true")
    args = parser.parse_args()
    errors, summary = check()
    if args.run_lean:
        replay_errors, replay_summary = replay_lean()
        errors.extend(replay_errors)
        summary.update(replay_summary)
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
