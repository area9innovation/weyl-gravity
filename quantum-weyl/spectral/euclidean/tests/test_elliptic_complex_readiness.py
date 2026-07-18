from __future__ import annotations

import json
import unittest

from spectral.euclidean.elliptic_complex_readiness import OUTPUT, build, mutation_receipts
from spectral.euclidean.elliptic_complex_receiver import synthetic_payload
from spectral.euclidean.verify_elliptic_complex_readiness import verify


class EllipticComplexReadinessTests(unittest.TestCase):
    def test_exact_symbol_mutations_are_rejected(self) -> None:
        receipts = mutation_receipts(synthetic_payload())
        self.assertEqual(len(receipts), 5)
        self.assertTrue(all(row["rejected"] for row in receipts))

    def test_reduced_ledger_is_not_full_complex(self) -> None:
        value = build()
        by_id = {row["candidate_id"]: row for row in value["current_candidate_audit"]}
        ledger = by_id["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER"]
        self.assertTrue(ledger["Euclidean"])
        self.assertTrue(ledger["full_BV_rows"])
        self.assertFalse(ledger["principal_symbol_exactness"])
        self.assertFalse(
            value["claim_flags"]["REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED"]
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
