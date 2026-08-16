#!/usr/bin/env python3
"""Fail-closed provenance and Lean replay checker for the Physlib bridge."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "physlib-demo"
CERTIFICATE = DEMO / "certificates/PHYSLIB_STRICT_WEYL_SECOND_SOURCE_BRIDGE_V1.json"
ARITY_CERTIFICATE = DEMO / "certificates/PHYSLIB_MINIMAL_ARITY_THREE_FINITE_REPLAY_V1.json"
SOURCE = DEMO / "WeylPhyslibBridge/StrictWeylSecondSource.lean"
ARITY_SOURCE = DEMO / "WeylPhyslibBridge/MinimalArityThree.lean"
ARITY_GENERATOR = DEMO / "generate_minimal_arity_three.py"
FORGE_SOURCE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
ARITY_FORGE_SOURCE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
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
ARITY_EXPECTED_FLAGS = {
    "LEAN_KERNEL_PROOF_COMPILES": True,
    "CHANNEL_INVENTORY_FORMALIZED": True,
    "ALL_72_CHANNELS_REPLAYED": True,
    "ALL_212_PATHS_REPLAYED": True,
    "PATH_KIND_PARTITION_FORMALIZED": True,
    "EXACT_RECEIVER_ZERO_DEFECTS_FORMALIZED": True,
    "THREE_MUTATION_WITNESSES_FORMALIZED": True,
    "NATURAL_OPERATOR_EVALUATOR_FORMALIZED": False,
    "ARBITRARY_INPUT_NATURAL_IDENTITY_FORMALIZED": False,
    "CAUSAL_SUPPORT_FORMALIZED": False,
    "LORENTZIAN_QUANTUM_THEORY": False,
}


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
    if result.get("formalization_scope") != "CONCLUSION_ONLY":
        errors.append("formalization scope")
    if result.get("kernel_status") != "COMPILES" or result.get("web_passport", {}).get("evidence_effect") != "NONE":
        errors.append("proof-passport boundary")
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


def check_arity_three(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(ARITY_CERTIFICATE.read_text()) if data is None else data
    errors: list[str] = []
    if result.get("result_id") != "PHYSLIB_MINIMAL_ARITY_THREE_FINITE_REPLAY_V1":
        errors.append("arity result id")
    if result.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("arity dependency boundary")
    if result.get("formalization_scope") != "FINITE_SERIALIZED_RECEIVER":
        errors.append("arity formalization scope")
    if result.get("kernel_status") != "COMPILES" or result.get("web_passport", {}).get("evidence_effect") != "NONE":
        errors.append("arity proof-passport boundary")
    if result.get("foundational_portability") != "PROOF_METHOD_NOT_MINIMIZED":
        errors.append("arity portability boundary")
    if result.get("claim_flags") != ARITY_EXPECTED_FLAGS:
        errors.append("arity claim flags")
    if result.get("axiom_footprints") != {
        "census_and_zero_defects": ["propext", "Quot.sound"],
        "rational_mutation_witnesses": ["propext", "Classical.choice", "Quot.sound"],
    }:
        errors.append("arity axiom footprints")

    provenance = result.get("provenance", {})
    expected_paths = {
        "lean_source": ARITY_SOURCE,
        "generator": ARITY_GENERATOR,
        "forge_source_certificate": ARITY_FORGE_SOURCE,
    }
    for key, path in expected_paths.items():
        if provenance.get(key, {}).get("sha256") != sha256(path):
            errors.append(f"arity {key} hash")

    manifest = json.loads(MANIFEST.read_text())
    packages = {item["name"]: item for item in manifest["packages"]}
    pins = result.get("toolchain", {})
    if (DEMO / "lean-toolchain").read_text().strip() != pins.get("lean"):
        errors.append("arity Lean toolchain pin")
    if packages.get("Physlib", {}).get("rev") != pins.get("physlib_commit"):
        errors.append("arity Physlib manifest pin")
    if packages.get("mathlib", {}).get("rev") != pins.get("mathlib_commit"):
        errors.append("arity Mathlib manifest pin")

    sys.path.insert(0, str(DEMO))
    try:
        import generate_minimal_arity_three as generator
        if generator.render() != ARITY_SOURCE.read_text():
            errors.append("arity generated source drift")
    finally:
        sys.path.pop(0)
    source = ARITY_SOURCE.read_text()
    for theorem in (
        "channelCountCertified", "composablePathCountCertified",
        "q1q3PathCountCertified", "q2q2PathCountCertified", "q3q1PathCountCertified",
        "exactReceiverDefectsZero", "allThreeMutationsDetected",
    ):
        if not re.search(rf"\btheorem\s+{theorem}\b", source):
            errors.append(f"missing arity theorem {theorem}")
    if re.search(r"\b(sorry|admit|axiom)\b", source):
        errors.append("arity untrusted declaration token")
    digest = certificate_digest(result)
    if result.get("independent_checker", {}).get("certificate_digest_sha256") != digest:
        errors.append("arity certificate digest")
    return errors, {
        "arity_certificate_digest_sha256": digest,
        "arity_lean_source_sha256": sha256(ARITY_SOURCE),
        "arity_forge_source_sha256": sha256(ARITY_FORGE_SOURCE),
    }


def replay_lean() -> tuple[list[str], dict[str, Any]]:
    files = [
        "WeylPhyslibBridge/StrictWeylSecondSource.lean",
        "WeylPhyslibBridge/MinimalArityThree.lean",
    ]
    completed = [
        subprocess.run(["lake", "env", "lean", path], cwd=DEMO, text=True, capture_output=True, check=False)
        for path in files
    ]
    output = "".join(item.stdout + item.stderr for item in completed)
    errors: list[str] = []
    if any(item.returncode for item in completed):
        errors.append("Lean exited " + ",".join(str(item.returncode) for item in completed))
    for theorem in (
        "rationalCoefficientCancellation", "secondNonlinearSourceClosed",
        "channelCountCertified", "composablePathCountCertified",
        "exactReceiverDefectsZero", "allThreeMutationsDetected",
    ):
        if theorem not in output:
            errors.append(f"missing axiom report {theorem}")
    for axiom in EXPECTED_AXIOMS:
        if axiom not in output:
            errors.append(f"missing reported axiom {axiom}")
    return errors, {"lean_exit_codes": [item.returncode for item in completed], "axiom_report_seen": not errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-lean", action="store_true")
    args = parser.parse_args()
    errors, summary = check()
    arity_errors, arity_summary = check_arity_three()
    errors.extend(arity_errors)
    summary.update(arity_summary)
    if args.run_lean:
        replay_errors, replay_summary = replay_lean()
        errors.extend(replay_errors)
        summary.update(replay_summary)
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
