#!/usr/bin/env python3
"""Independent scientific checker for the strict pure-Weyl q3 witness."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import cylinder_cubic_bach_evaluator as cubic
import cylinder_polarized_bach_evaluator as point
from build_strict_386_quadratic_truncation_lambda2_source_obstruction import exact_fixture as q2_fixture
from local_q1_q2_receiver import apply_q1, field_fixture


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def without_hash(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "sha256"}


def recompute_cubic() -> dict[str, object]:
    background = point.flat_background(7)
    field = apply_q1("q1_h_c", field_fixture("c", 1, 7), background, 6)
    raw = {
        pair: {
            alpha: coefficient
            for a_degree, b_degree, alpha, coefficient in field[pair].terms
            if a_degree == b_degree == 0
        }
        for pair in point.PAIRS
    }
    return cubic.diagonal_cubic_bach_data(raw, background=background, output_coordinate_order=1)


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_PURE_WEYL_Q3_WITNESS_V1" or value.get("schema") != "strict-386-pure-weyl-q3-witness-v1":
        return ["result identity/schema drift"]

    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append("dependency hash drift: " + item.get("path", "<missing>"))
    implementation = value.get("provenance", {}).get("implementation", {})
    engine = ROOT / implementation.get("path", "")
    if not engine.is_file() or implementation.get("sha256") != sha(engine):
        errors.append("cubic engine hash drift")

    cubic_data = recompute_cubic()
    fixture = value.get("exact_cubic_fixture", {})
    if cubic_data.get("q1_q3_weyl_noether") != fixture.get("q1_q3_weyl_noether"):
        errors.append("q1 q3 Weyl image regeneration drift")
    if cubic_data.get("q1_q3_diff_noether") != fixture.get("q1_q3_diff_noether"):
        errors.append("q1 q3 Diff image regeneration drift")
    if cubic_data.get("nonlinear_weyl_identity_t3") != "0":
        errors.append("nonlinear Weyl identity is nonzero")
    regenerated_rows = cubic_data.get("q3_metric_euler_density", {})
    if sum(bool(row) for row in regenerated_rows.values()) != fixture.get("nonzero_metric_output_rows"):
        errors.append("q3 nonzero-row count drift")
    if sum(len(row) for row in regenerated_rows.values()) != fixture.get("metric_output_term_count"):
        errors.append("q3 term-count drift")

    q2 = q2_fixture()
    jacobiator = Fraction(q2["jacobiator_weyl_identity_value"])
    q1_q3 = Fraction(fixture.get("q1_q3_weyl_noether", "0"))
    cancellation = value.get("arity_three_cancellation", {})
    if jacobiator != Fraction(75760, 27):
        errors.append("independent q2 Jacobiator drift")
    if q1_q3 != Fraction(-75760, 9) or q1_q3 + 3 * jacobiator:
        errors.append("arity-three cancellation drift")
    if Fraction(cancellation.get("full_lambda2_source_q1_defect_on_witness", "1")):
        errors.append("lambda-squared witness source is not closed")
    if cancellation.get("general_full_source_closure") is not False:
        errors.append("general source closure over-promotion")

    sources = {item.get("source_id"): item for item in value.get("q3_source_compatibility", {}).get("sources", [])}
    berger = sources.get("BERGER_SUPPORT_LOCAL_Q3", {})
    receiver = sources.get("STRICT_PURE_WEYL_CUBIC_BACH_RECEIVER_V1", {})
    if berger.get("strict_386_direct_import") is not False or berger.get("disposition") != "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP":
        errors.append("Berger direct-import firewall drift")
    if berger.get("nonexistence_claimed") is not False:
        errors.append("Berger nonexistence overclaim")
    if receiver.get("disposition") != "RECEIVER_DERIVED_WITNESS_CANCELLATION_CERTIFIED" or receiver.get("strict_386_direct_import") is not False:
        errors.append("receiver-derived authority boundary drift")

    flags = value.get("claim_flags", {})
    true_flags = (
        "STRICT_PURE_WEYL_METRIC_Q3_DIAGONAL_WITNESS_DERIVED",
        "STRICT_PURE_WEYL_Q3_WITNESS_CANCELLATION_CERTIFIED",
        "STRICT_386_WITNESS_FULL_SOURCE_CLOSURE_CERTIFIED",
    )
    false_flags = (
        "BERGER_Q3_DIRECT_STRICT_IMPORT_COMPATIBLE",
        "STRICT_386_AUTHORITATIVE_Q3_IMPORTED",
        "STRICT_386_ARBITRARY_INPUT_Q3_CERTIFIED",
        "STRICT_386_FULL_BV_ARITY_THREE_IDENTITY_CERTIFIED",
        "STRICT_386_GENERAL_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    if any(flags.get(key) is not True for key in true_flags):
        errors.append("positive witness flag drift")
    if any(flags.get(key) is not False for key in false_flags):
        errors.append("authority/lifecycle firewall drift")

    sections = {
        "exact_cubic_fixture_sha256": "exact_cubic_fixture",
        "arity_three_cancellation_sha256": "arity_three_cancellation",
        "q3_source_compatibility_sha256": "q3_source_compatibility",
        "authoritative_q3_export_contract_sha256": "authoritative_q3_export_contract",
        "foundational_strength_sha256": "foundational_strength",
    }
    hashes = value.get("canonical_hashes", {})
    for hash_key, section_key in sections.items():
        section = value.get(section_key, {})
        expected = digest(without_hash(section))
        if section.get("sha256") != expected or hashes.get(hash_key) != expected:
            errors.append("canonical section hash drift: " + section_key)
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_PURE_WEYL_Q3_WITNESS_V1_SCIENTIFIC: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("- " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
