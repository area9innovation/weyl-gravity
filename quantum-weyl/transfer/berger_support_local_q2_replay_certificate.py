#!/usr/bin/env python3
"""Emit the independent scientific replay of the landed Berger q2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_qsqrt10_replay import replay_scientific_q2
except ImportError:
    from berger_qsqrt10_replay import replay_scientific_q2


ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parents[1]
IMPORT_CERTIFICATE = ROOT / "certificates" / "BERGER_SUPPORT_LOCAL_Q2_IMPORT.json"
OUTPUT = (
    ROOT / "certificates" / "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json"
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _checked_import() -> dict[str, Any]:
    imported = json.loads(IMPORT_CERTIFICATE.read_text(encoding="utf-8"))
    if (
        imported.get("result_id") != "BERGER_SUPPORT_LOCAL_Q2_IMPORT"
        or imported.get("result_state")
        != "COMPLETE_SUPPORT_LOCAL_Q2_IMPORTED_SCIENTIFIC_REPLAY_PENDING"
        or imported.get("claim_flags", {}).get("CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED")
        is not True
        or imported.get("claim_flags", {}).get(
            "SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED"
        )
        is not False
    ):
        raise ValueError("support-local q2 import boundary drifted")
    return imported


def _source_manifest() -> dict[str, str]:
    paths = (
        "berger_qsqrt10_replay.py",
        "berger_support_local_q2_replay_certificate.py",
        "berger_support_local_q2_import.py",
        "berger_54_row_q2_arrival.py",
        "berger_54_row_q2_replay.py",
        "berger_54_row_local_d_import.py",
        "schema/berger-support-local-q2-scientific-replay-v1.schema.json",
        "tests/test_berger_support_local_q2_scientific_replay.py",
        "../reports/berger-support-local-q2-scientific-replay.md",
        "README.md",
    )
    return {path: _hash(ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    """Run the complete scientific replay and build its immutable receipt."""

    _checked_import()
    replay = dict(replay_scientific_q2())
    replay.pop("phase_seconds", None)
    if not replay["all_identities_pass"]:
        raise ValueError("scientific support-local q2 replay has a nonzero defect")
    manifest = _source_manifest()
    return {
        "schema": "quantum-weyl-berger-support-local-q2-scientific-replay-v1",
        "result_id": "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY",
        "result_state": "COMPLETE_SUPPORT_LOCAL_Q2_IMPORTED_IDENTITIES_INDEPENDENTLY_REPLAYED_TRANSFER_PENDING",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "import_certificate": {
            "path": str(IMPORT_CERTIFICATE.relative_to(REPOSITORY_ROOT)),
            "sha256": _hash(IMPORT_CERTIFICATE),
        },
        "replay": replay,
        "claim_flags": {
            "CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED": True,
            "SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED": True,
            "TRANSFERRED_ELL2_COMPUTED": False,
            "INTERACTING_CARTAN_VERDICT": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "TRANSFER_ELL2_AND_SOLVE_FULL_4D_UNARY_D_CARTAN_EXISTENCE",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC consumer independently replays q1/q2, D/q2, "
            "and BV cyclicity for the complete landed 54-row Berger tensor using "
            "exact Q(sqrt(10)) arithmetic, noncommutative PBW reduction, formal "
            "integration by parts, and the imported odd Darboux polarization. It "
            "does not yet transfer ell2, solve the prerequisite unary D-Cartan "
            "equation or the interacting arity-two D-Cartan equation, "
            "construct causal/Hadamard data, restore a QME, or make a quantum claim."
        ),
        "consumer_provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
    }


def validate_checked_receipt() -> dict[str, Any]:
    """Validate hashes and the stored exact-zero verdict without replaying q2."""

    _checked_import()
    if not OUTPUT.exists():
        raise ValueError(f"missing Berger support-local q2 replay receipt: {OUTPUT}")
    checked = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if (
        checked.get("schema")
        != "quantum-weyl-berger-support-local-q2-scientific-replay-v1"
        or checked.get("result_state")
        != "COMPLETE_SUPPORT_LOCAL_Q2_IMPORTED_IDENTITIES_INDEPENDENTLY_REPLAYED_TRANSFER_PENDING"
        or checked.get("import_certificate")
        != {
            "path": str(IMPORT_CERTIFICATE.relative_to(REPOSITORY_ROOT)),
            "sha256": _hash(IMPORT_CERTIFICATE),
        }
        or checked.get("consumer_provenance", {}).get("source_manifest")
        != _source_manifest()
        or checked.get("consumer_provenance", {}).get("source_manifest_sha256")
        != _canonical_hash(_source_manifest())
    ):
        raise ValueError("Berger support-local q2 replay receipt provenance drifted")
    replay = checked.get("replay", {})
    expected_zero_hash = _canonical_hash([])
    results = replay.get("results", {})
    if (
        replay.get("backend") != "two-rational-component-Q(sqrt(10))-v1"
        or replay.get("input", {}).get("q2_term_count") != 150305
        or replay.get("all_identities_pass") is not True
        or set(results)
        != {
            "q1_q2_arity_two_nilpotency",
            "D_q2_derivation",
            "BV_cyclicity_q2",
        }
        or any(
            result.get("status") != "PASS"
            or result.get("nonzero_coefficient_count") != 0
            or result.get("defect_sha256") != expected_zero_hash
            for result in results.values()
        )
    ):
        raise ValueError("Berger support-local q2 replay receipt is not exact zero")
    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--replay-check",
        action="store_true",
        help="rerun the full exact scientific replay and compare its receipt",
    )
    args = parser.parse_args()
    if args.emit:
        content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
        OUTPUT.write_text(content, encoding="utf-8")
    if args.replay_check:
        content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale Berger support-local q2 replay: {OUTPUT}")
    if args.check:
        try:
            validate_checked_receipt()
        except ValueError as error:
            raise SystemExit(str(error)) from error
    if not args.emit and not args.check and not args.replay_check:
        print(json.dumps(validate_checked_receipt(), indent=2, sort_keys=True))
    else:
        print("BERGER SUPPORT-LOCAL Q2: ALL SCIENTIFIC ARITY-TWO REPLAYS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
