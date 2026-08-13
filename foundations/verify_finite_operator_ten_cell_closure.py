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
from foundations.check_finite_operator_ten_cell_closure import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-finite-operator-ten-cell-closure-v1.schema.json"
REPORT = ROOT / "foundations/reports/finite-operator-ten-cell-closure.md"


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
    if len(promotions) != 10 or len(set(coordinates)) != 10:
        errors.append("exactly ten unique promotions")
    if sum(item.get("new_status") == "LOCAL_RESULT" for item in promotions) != 9:
        errors.append("nine local results")
    if sum(item.get("new_status") == "PIECES_ONLY" for item in promotions) != 1:
        errors.append("one pieces-only result")
    renorm = [item for item in promotions if item.get("coordinate", {}).get("obligation") == "RENORMALIZED_PRODUCTS"]
    if len(renorm) != 1 or renorm[0].get("new_status") != "PIECES_ONLY" or renorm[0].get("evidence_role") != "SUPPORTING":
        errors.append("renormalization fail-closed grade")
    flags = r.get("claim_flags", {})
    for key in ("exactly_ten_previously_unmapped_cells_classified", "nine_local_results", "one_pieces_only_result", "finite_hilbert_interaction_constructed", "finite_krein_interaction_constructed", "constructive_krein_state_probability_constructed", "fixed_model_counterterm_space_classified", "finite_regulated_products_constructed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("continuum_renormalized_products_constructed", "weyl_counterterms_classified", "general_carrier_equivalence_established", "choice_principle_required", "empirical_agreement_assessed", "lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for source in r.get("provenance", {}).get("inputs", []):
        path = ROOT / source.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            errors.append("source hash " + source.get("path", "missing"))
    for token in ("Nine are LOCAL_RESULT and one is PIECES_ONLY", "object-level realization", "All 256 basis products", "cutoff products do not become continuum renormalized", "LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
