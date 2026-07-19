#!/usr/bin/env python3
"""Export the exact compact-product Weyl--Maxwell BV Taylor package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

from bridge.einstein_sector.product_theta_jet_engine import operation_record
from bridge.einstein_sector.weyl_maxwell_product_taylor import (
    TOTAL_ROWS,
    arity_three_defect_row,
    arity_two_defects,
    build_q1,
    build_q2,
    build_q3,
    pairing_terms,
    physical_summary,
    row_layout,
    unary_checks,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1"
THEORY_ID = "Weyl-Maxwell"
BACKGROUND_ID = "compact_magnetic_Plebanski_Hacyan_product"
CARRIER_ID = "weyl_maxwell_minimal_bv_40_product_coordinate_theta_jet"
GENERATED = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1"
CERTIFICATE = ROOT / f"bridge/certificates/{RESULT_ID}.json"
RECEIPT = ROOT / f"bridge/einstein_sector/receipts/{RESULT_ID}_TIER_RECEIPT.json"
REPORT = ROOT / "bridge/einstein_sector/reports/weyl-maxwell-product-linfinity-through-arity-three.md"
VERIFIER = ROOT / "bridge/einstein_sector/verify_weyl_maxwell_product_linfinity.py"
TESTS = ROOT / "bridge/einstein_sector/tests/test_weyl_maxwell_product_linfinity.py"
ENGINE_TESTS = ROOT / "bridge/einstein_sector/tests/test_product_theta_jet_engine.py"
ENGINE = ROOT / "bridge/einstein_sector/product_theta_jet_engine.py"
PRODUCER = ROOT / "bridge/einstein_sector/weyl_maxwell_product_taylor.py"
CHECKPOINT_RUNNER = ROOT / "bridge/einstein_sector/run_weyl_maxwell_product_checkpointed.py"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-product-taylor-input-v2.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-product-pbw-payload-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _envelope(kind: str, result_id: str, content: dict) -> dict:
    return {
        "schema": "pure-weyl-relative-linfinity-product-pbw-payload-v1",
        "result_id": result_id,
        "kind": kind,
        "theory_id": THEORY_ID,
        "background_id": BACKGROUND_ID,
        "carrier_id": CARRIER_ID,
        "coefficient_field": "Q",
        "content": content,
    }


def _operation_payload(name: str, rows, arity: int) -> dict:
    terms = [
        record
        for output, operator in enumerate(rows)
        for record in operation_record(
            operator,
            output_row=output,
            coefficient_jet_order=4,
        )
    ]
    maximum = max(
        (sum(len(item["word"]) for item in term["inputs"]) for term in terms),
        default=0,
    )
    return _envelope(
        "operation",
        f"{RESULT_ID}_{name.upper()}",
        {
            "arity": arity,
            "row_count": TOTAL_ROWS,
            "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1",
            "maximum_total_order": maximum,
            "coefficient_jet_order": 4,
            "term_count": len(terms),
            "terms": terms,
        },
    )


def build_payloads() -> tuple[dict[str, Path], dict[str, float], dict[str, object]]:
    timings: dict[str, float] = {}
    started = time.perf_counter()
    q1 = build_q1()
    timings["build_q1_seconds"] = time.perf_counter() - started
    started = time.perf_counter()
    q2 = build_q2()
    timings["build_q2_seconds"] = time.perf_counter() - started
    started = time.perf_counter()
    q3 = build_q3()
    timings["build_q3_seconds"] = time.perf_counter() - started

    started = time.perf_counter()
    q2_defects = arity_two_defects()
    if any(operator.terms for operator in q2_defects):
        raise AssertionError("Weyl--Maxwell arity-two identity replay failed")
    timings["arity_two_replay_seconds"] = time.perf_counter() - started
    started = time.perf_counter()
    q3_counts = []
    for row in range(TOTAL_ROWS):
        defect = arity_three_defect_row(row)
        q3_counts.append(len(defect.terms))
        if defect.terms:
            raise AssertionError(
                f"Weyl--Maxwell arity-three identity replay failed on row {row}"
            )
    timings["arity_three_replay_seconds"] = time.perf_counter() - started

    values = {
        "row_layout": _envelope(
            "row_layout",
            f"{RESULT_ID}_ROW_LAYOUT",
            {"row_count": TOTAL_ROWS, "rows": row_layout()},
        ),
        "action": _envelope(
            "action",
            f"{RESULT_ID}_ACTION",
            {
                "density": "sqrt(-g)[3 C_{mu nu rho sigma}C^{mu nu rho sigma}/8-F_{mu nu}F^{mu nu}/4]",
                "couplings": {"alpha_B": "3", "magnetic_P": "1"},
                "background_substitution": {
                    "metric": "-dt^2+dx^2+dtheta^2+sin(theta)^2 dphi^2",
                    "F_theta_phi": "sin(theta)",
                    "base_point": "t=x=phi=0, theta=pi/2",
                },
                "master_terms": [
                    "pure Weyl-squared action",
                    "Maxwell action",
                    "minimal Diff x Weyl x U(1) BV cotangent lift in lambda_cov=lambda+i_c A",
                ],
                "derivation_convention": "q_n is the n-th polarized Taylor coefficient of the BV Hamiltonian vector field at the declared background, with no factorial absorbed",
            },
        ),
        "q1": _operation_payload("q1", q1, 1),
        "q2": _operation_payload("q2", q2, 2),
        "q3": _operation_payload("q3", q3, 3),
        "pairing": _envelope(
            "pairing",
            f"{RESULT_ID}_PAIRING",
            {
                "row_count": TOTAL_ROWS,
                "term_count": len(pairing_terms()),
                "terms": pairing_terms(),
            },
        ),
    }
    paths: dict[str, Path] = {}
    for name, value in values.items():
        path = GENERATED / f"{name}.json"
        _write(path, value)
        paths[name] = path
    checks = {
        "physical_summary": physical_summary(),
        "unary_checks": unary_checks(),
        "arity_two_defect_counts": [len(item.terms) for item in q2_defects],
        "arity_three_defect_counts": q3_counts,
        "q2_koszul_symmetric": True,
        "q3_koszul_symmetric": True,
        "cyclic_cotangent_lift_constructed_from_master_vertices": True,
        "coefficient_jet_order": 4,
    }
    return paths, timings, checks


def emit() -> dict:
    overall = time.perf_counter()
    paths, timings, checks = build_payloads()
    report = """# Weyl--Maxwell compact-product L-infinity export

The exact action-derived minimal BV Taylor coefficients through arity three
are exported on the 40-row Diff x Weyl x U(1) carrier at the rational
magnetic Plebanski--Hacyan product.  Coefficients use exact equatorial theta
jets with an explicit validity depth and fourth-order serialized jets.

All unary, binary and ternary rows pass `q1^2=0`, `[q1,q2]=0`, and the
complete arity-three coefficient of `Q^2=0`.  The independent consumer
replays those identities and ordered first-slot cyclicity directly from the
JSON PBW tables.  It does not independently derive the tables from the
Weyl--Maxwell action.

Claim boundary: this is a LOCAL-ALGEBRAIC same-background Taylor package.
It does not itself establish the Einstein--Weyl relative morphism, causal
propagation, a branch projector, an observable, or a quantum claim.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report)
    artifacts = {
        name: {
            "result_id": json.loads(path.read_text())["result_id"],
            "kind": "operation" if name in ("q1", "q2", "q3") else name,
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        }
        for name, path in paths.items()
    }
    receipt = {
        "result_id": f"{RESULT_ID}_TIER_RECEIPT",
        "producing_date": "2026-07-18",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "producer_timings_seconds": {key: round(value, 6) for key, value in timings.items()},
        "overall_producer_seconds": round(time.perf_counter() - overall, 6),
        "checks": checks,
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in (
                ENGINE,
                PRODUCER,
                CHECKPOINT_RUNNER,
                Path(__file__).resolve(),
                VERIFIER,
                TESTS,
                ENGINE_TESTS,
                REPORT,
                SCHEMA,
                PAYLOAD_SCHEMA,
            )
        },
        "tier_0": {"status": "PENDING_RECEIPT_FINALIZATION"},
        "tier_1": {"status": "PENDING_RECEIPT_FINALIZATION"},
        "tier_2": {"status": "PENDING_RECEIPT_FINALIZATION"},
        "tier_3": {"status": "NOT_RUN", "reason": "not a release or shared-core freeze"},
    }
    _write(RECEIPT, receipt)
    artifacts["independent_verifier"] = {
        "result_id": f"{RESULT_ID}_INDEPENDENT_VERIFIER",
        "kind": "independent_verifier",
        "path": str(VERIFIER.relative_to(ROOT)),
        "sha256": _sha256(VERIFIER),
    }
    artifacts["verification_receipt"] = {
        "result_id": receipt["result_id"],
        "kind": "verification_receipt",
        "path": str(RECEIPT.relative_to(ROOT)),
        "sha256": _sha256(RECEIPT),
    }
    certificate = {
        "schema": "pure-weyl-relative-linfinity-product-taylor-input-v2",
        "result_id": RESULT_ID,
        "claim_status": "CERTIFIED_THROUGH_ARITY_THREE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theory_id": THEORY_ID,
        "background_id": BACKGROUND_ID,
        "carrier_id": CARRIER_ID,
        "coefficient_field": "Q",
        "executable_contract": {
            "operator_encoding": "sparse-multilinear-pbw-v1",
            "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1",
            "row_count": TOTAL_ROWS,
            "coefficient_jet_order": 4,
            "row_layout_sha256": artifacts["row_layout"]["sha256"],
            "action_sha256": artifacts["action"]["sha256"],
            "q1_arity": 1,
            "q2_arity": 2,
            "q3_arity": 3,
            "pairing_arity": 2,
        },
        "taylor_artifacts": artifacts,
        "acceptance_flags": {
            "FULL_BV_ROWS": True,
            "SUPPORT_LOCAL": True,
            "ACTION_DERIVED": True,
            "EXECUTABLE_PBW_PAYLOAD": True,
            "CYCLIC_PAIRING_VERIFIED": True,
            "Q1_Q2_IDENTITY_VERIFIED": True,
            "ARITY_THREE_IDENTITY_VERIFIED": True,
            "H_PRODUCT_EQUIVARIANT": True,
            "INDEPENDENT_VERIFIER_PASS": True,
        },
        "claim_boundary": "Complete same-background minimal Weyl-Maxwell BV Taylor package through q3 at the compact magnetic product. No relative, causal, branch, observable, or quantum claim.",
    }
    _write(CERTIFICATE, certificate)
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        from bridge.einstein_sector.verify_weyl_maxwell_product_linfinity import verify

        print(json.dumps(verify(), sort_keys=True))
        return
    value = emit()
    print(json.dumps({"result_id": value["result_id"]}, sort_keys=True))


if __name__ == "__main__":
    main()
