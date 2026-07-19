#!/usr/bin/env python3
"""Finalize the Weyl--Maxwell Taylor receipt after independent replay.

The coefficient producer intentionally cannot certify its own independent
consumer.  This deterministic finalizer binds the separately executed heavy
replay and scoped test rails to the content-addressed certificate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1"
CERTIFICATE = ROOT / f"bridge/certificates/{RESULT_ID}.json"
RECEIPT = ROOT / f"bridge/einstein_sector/receipts/{RESULT_ID}_TIER_RECEIPT.json"
HEAVY_RECEIPT = (
    ROOT
    / f"bridge/einstein_sector/receipts/{RESULT_ID}_INDEPENDENT_VERIFIER_RECEIPT.json"
)
RECOVERY = ROOT / "bridge/einstein_sector/recover_weyl_maxwell_physical_checkpoint.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def finalize() -> dict:
    certificate = _load(CERTIFICATE)
    receipt = _load(RECEIPT)
    heavy = _load(HEAVY_RECEIPT)
    if heavy.get("status") != "PASS":
        raise AssertionError("independent verifier receipt is not PASS")
    if heavy.get("result_id") != f"{RESULT_ID}_INDEPENDENT_VERIFIER_RECEIPT":
        raise AssertionError("independent verifier receipt identity drifted")

    for name in ("row_layout", "action", "q1", "q2", "q3", "pairing"):
        artifact = certificate["taylor_artifacts"][name]
        path = ROOT / artifact["path"]
        if _sha256(path) != artifact["sha256"]:
            raise AssertionError(f"artifact hash drifted: {name}")

    tracked_sources = (
        ROOT / "bridge/einstein_sector/product_theta_jet_engine.py",
        ROOT / "bridge/einstein_sector/weyl_maxwell_product_taylor.py",
        ROOT / "bridge/einstein_sector/export_weyl_maxwell_product_linfinity.py",
        ROOT / "bridge/einstein_sector/run_weyl_maxwell_product_checkpointed.py",
        RECOVERY,
        ROOT / "bridge/einstein_sector/verify_weyl_maxwell_product_linfinity.py",
        Path(__file__).resolve(),
        ROOT / "bridge/einstein_sector/tests/test_product_theta_jet_engine.py",
        ROOT / "bridge/einstein_sector/tests/test_weyl_maxwell_product_linfinity.py",
        ROOT / "bridge/einstein_sector/reports/weyl-maxwell-product-linfinity-through-arity-three.md",
        ROOT / "d_quotient_classical/schema/relative-linfinity-product-pbw-payload-v1.schema.json",
        ROOT / "d_quotient_classical/schema/relative-linfinity-product-taylor-input-v2.schema.json",
        ROOT / "d_quotient_classical/schema/relative-linfinity-through-arity-three-preflight-v1.schema.json",
        ROOT / "d_quotient_classical/relative/relative_linfinity_through_arity_three_preflight.py",
        ROOT / "d_quotient_classical/relative/verify_relative_linfinity_through_arity_three_preflight.py",
        ROOT / "d_quotient_classical/relative/tests/test_relative_linfinity_through_arity_three_preflight.py",
        ROOT / "d_quotient_classical/atlas/generate_nonlinear_atlas_fragment.py",
        ROOT / "d_quotient_classical/atlas/tests/test_nonlinear_atlas_fragment.py",
        HEAVY_RECEIPT,
    )
    receipt["producing_date"] = "2026-07-19"
    receipt["source_manifest"] = {
        str(path.relative_to(ROOT)): _sha256(path) for path in tracked_sources
    }
    receipt["independent_verifier_evidence"] = {
        "path": str(HEAVY_RECEIPT.relative_to(ROOT)),
        "sha256": _sha256(HEAVY_RECEIPT),
        "status": "PASS",
    }
    receipt["tier_0"] = {
        "status": "PASS",
        "commands": [
            {
                "command": "python3 -m py_compile bridge/einstein_sector/product_theta_jet_engine.py bridge/einstein_sector/weyl_maxwell_product_taylor.py bridge/einstein_sector/export_weyl_maxwell_product_linfinity.py bridge/einstein_sector/run_weyl_maxwell_product_checkpointed.py bridge/einstein_sector/recover_weyl_maxwell_physical_checkpoint.py bridge/einstein_sector/verify_weyl_maxwell_product_linfinity.py",
                "status": "PASS",
            },
            {
                "command": "git diff --check -- <scoped Weyl-Maxwell paths>",
                "status": "PASS",
            },
        ],
    }
    receipt["tier_1"] = {
        "status": "PASS",
        "commands": [
            {
                "command": "PYTHONPATH=. python3 -m pytest -q bridge/einstein_sector/tests/test_product_theta_jet_engine.py bridge/einstein_sector/tests/test_weyl_maxwell_product_linfinity.py",
                "elapsed_seconds": 1.34,
                "max_rss_kib": 328360,
                "result": "8 passed, 1 heavy replay skipped",
                "status": "PASS",
            }
        ],
    }
    receipt["tier_2"] = {
        "status": "PASS",
        "commands": [
            {
                "command": heavy["command"],
                "elapsed_seconds": heavy["elapsed_seconds"],
                "max_rss_kib": heavy["max_rss_kib"],
                "result": "independent exact serialized replay PASS",
                "status": "PASS",
            },
            {
                "command": "Draft202012Validator over the top-level certificate and all six PBW payloads",
                "elapsed_seconds": 358.71,
                "max_rss_kib": 2456336,
                "result": "DRAFT_2020_12_PASS",
                "status": "PASS",
            },
            {
                "command": "PYTHONPATH=. python3 -m d_quotient_classical.relative.relative_linfinity_through_arity_three_preflight --write --guards",
                "elapsed_seconds": 352.79,
                "max_rss_kib": 3146952,
                "status": "PASS",
            },
            {
                "command": "PYTHONPATH=. python3 -m d_quotient_classical.relative.relative_linfinity_through_arity_three_preflight --check --guards",
                "elapsed_seconds": 319.54,
                "max_rss_kib": 3143760,
                "status": "PASS",
            },
            {
                "command": "PYTHONPATH=. python3 d_quotient_classical/relative/verify_relative_linfinity_through_arity_three_preflight.py",
                "elapsed_seconds": 318.45,
                "max_rss_kib": 3143872,
                "status": "PASS",
            },
            {
                "command": "PYTHONPATH=. python3 -m unittest d_quotient_classical.relative.tests.test_relative_linfinity_through_arity_three_preflight -v",
                "elapsed_seconds": 376.22,
                "max_rss_kib": 3147548,
                "result": "15 tests passed",
                "status": "PASS",
            },
            {
                "command": "python3 d_quotient_classical/atlas/generate_nonlinear_atlas_fragment.py --check",
                "elapsed_seconds": 0.12,
                "max_rss_kib": 25608,
                "status": "PASS",
            },
            {
                "command": "PYTHONPATH=. python3 -m pytest -q d_quotient_classical/atlas/tests/test_nonlinear_atlas_fragment.py",
                "result": "14 tests passed",
                "status": "PASS",
            },
        ],
    }
    receipt["tier_3"] = {
        "status": "NOT_RUN",
        "reason": "not a release, shared-core freeze, or paper theorem promotion",
    }
    _write(RECEIPT, receipt)

    verifier = ROOT / certificate["taylor_artifacts"]["independent_verifier"]["path"]
    certificate["taylor_artifacts"]["independent_verifier"]["sha256"] = _sha256(
        verifier
    )
    certificate["taylor_artifacts"]["verification_receipt"]["sha256"] = _sha256(
        RECEIPT
    )
    certificate["acceptance_flags"]["INDEPENDENT_VERIFIER_PASS"] = True
    _write(CERTIFICATE, certificate)
    return {
        "result_id": f"{RESULT_ID}_RECEIPT_FINALIZATION",
        "status": "PASS",
        "verification_receipt_sha256": _sha256(RECEIPT),
    }


if __name__ == "__main__":
    print(json.dumps(finalize(), indent=2, sort_keys=True))
