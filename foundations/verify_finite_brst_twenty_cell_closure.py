#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.check_finite_brst_twenty_cell_closure import check, expected_coordinates

RESULT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-finite-brst-twenty-cell-closure-v1.schema.json"
REPORT = ROOT / "foundations/reports/finite-brst-twenty-cell-closure.md"


def load(path: Path):
    return json.loads(path.read_text())


def canonical_digest(value: dict) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def verify(*, result=None, report=None):
    r = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    errors.extend("schema " + e.message for e in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(r))
    checker_errors, summary = check()
    errors.extend("checker " + e for e in checker_errors)
    if summary["digest"] != r.get("independent_checker", {}).get("expected_digest"):
        errors.append("checker digest")
    if canonical_digest(r) != r.get("canonical_digest"):
        errors.append("canonical digest")
    promotions = r.get("promotions", [])
    coordinates = [tuple(item.get("coordinate", {}).values()) for item in promotions]
    if coordinates != expected_coordinates() or len(set(coordinates)) != 20:
        errors.append("exact twenty target coordinates")
    if sum(item.get("new_status") == "LOCAL_RESULT" and item.get("evidence_role") == "DIRECT_LOCAL" for item in promotions) != 17:
        errors.append("seventeen direct local results")
    products = [item for item in promotions if item.get("coordinate", {}).get("obligation") == "RENORMALIZED_PRODUCTS"]
    if len(products) != 3 or any(item.get("new_status") != "PIECES_ONLY" or item.get("evidence_role") != "SUPPORTING" for item in products):
        errors.append("three fail-closed product grades")
    flags = r.get("claim_flags", {})
    for key in ("exactly_twenty_previously_unmapped_cells_classified", "seventeen_local_results", "three_pieces_only_results", "counterterms_classified_before_qme", "anomalies_classified_before_qme", "finite_one_loop_qme_restored", "residual_transfer_after_restoration"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("continuum_renormalized_products_constructed", "weyl_qme_restored", "weyl_residual_quantum_transfer", "general_carrier_equivalence_established", "empirical_agreement_assessed", "lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for source in r.get("provenance", {}).get("inputs", []):
        path = ROOT / source.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            errors.append("source hash " + source.get("path", "missing"))
    for token in ("Seventeen cells become LOCAL_RESULT", "H^0(Q)=Q[k]", "H^1(Q)=Q[r]", "classified before any QME", "Only the restored correction", "all 1296 products", "PIECES_ONLY", "LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
