#!/usr/bin/env python3
"""Regression tests for the fail-closed quantum result contract."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_result", HERE / "validate_result.py")
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
SCHEMA = json.loads((HERE / "result.schema.json").read_text())


def base_record() -> dict[str, object]:
    return {
        "result_id": "schema-self-test",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 1,
        "form_degree": 4,
        "antifield_number": 0,
        "parity": "even",
        "representative": "schema fixture only",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": "schema/test_validate_result.py",
        "assumptions": ["This is a schema fixture, not a scientific result."],
        "notes": "",
    }


class ResultSchemaTests(unittest.TestCase):
    def test_minimal_record_passes(self) -> None:
        self.assertEqual(VALIDATOR.validate_record(base_record(), SCHEMA), [])

    def test_unknown_tag_fails(self) -> None:
        record = base_record()
        record["dependency_tags"] = ["FULL-QUANTUM"]
        errors = VALIDATOR.validate_record(record, SCHEMA)
        self.assertTrue(any("dependency_tags[0]" in error for error in errors))

    def test_split_descent_record_passes_without_legacy_collision(self) -> None:
        record = base_record()
        record.pop("descent_status")
        record["diff_descent_status"] = "NONZERO_COMPLETE"
        record["intrinsic_weyl_descent_status"] = "MIXED_BY_CANDIDATE"
        self.assertEqual(VALIDATOR.validate_record(record, SCHEMA), [])

    def test_legacy_and_split_descent_fields_cannot_mix(self) -> None:
        record = base_record()
        record["diff_descent_status"] = "NONZERO_COMPLETE"
        record["intrinsic_weyl_descent_status"] = "TRIVIAL"
        errors = VALIDATOR.validate_record(record, SCHEMA)
        self.assertTrue(any("mutually exclusive" in error for error in errors))

    def test_lorentzian_promotion_requires_causal_tag(self) -> None:
        record = base_record()
        record["lifecycle_status"] = "LORENTZIAN_CERTIFIED"
        errors = VALIDATOR.validate_record(record, SCHEMA)
        self.assertTrue(any("LORENTZIAN-CAUSAL" in error for error in errors))

    def test_residual_promotion_requires_projection(self) -> None:
        record = base_record()
        record["lifecycle_status"] = "RESIDUAL_TRANSFERRED"
        errors = VALIDATOR.validate_record(record, SCHEMA)
        self.assertTrue(any("residual transfer" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
