#!/usr/bin/env python3
"""Mutation tests for the bounded partial-jet preflight."""
from __future__ import annotations

import copy
import json
import unittest

from .produce import CERTIFICATE
from .verify import verify_document


class PartialJetPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(CERTIFICATE.read_text())

    def test_certificate_verifies(self) -> None:
        self.assertEqual(verify_document(copy.deepcopy(self.document)), [])

    def test_status_promotion_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["status"] = "CERTIFIED_ONE_MICROFACTOR_PARTIAL_JET_PASS"
        self.assertTrue(verify_document(changed))

    def test_tail_refusal_mutation_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["attempt"]["parsed_result"]["tail"] = "0"
        self.assertTrue(verify_document(changed))

    def test_T_plus_promotion_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["T_plus_recovered"] = True
        self.assertTrue(verify_document(changed))

    def test_reference_comparison_promotion_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"][
            "expanded_six_state_reference_compared"
        ] = True
        self.assertTrue(verify_document(changed))

    def test_import_hash_drift_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["imports"]["partial_jet_crosswalk"]["sha256"] = "0" * 64
        self.assertTrue(verify_document(changed))


if __name__ == "__main__":
    unittest.main()
