from __future__ import annotations

import json
import unittest

from lorentzian.typed_biwave_volterra_theorem_import import OUTPUT, build, exact_fixture
from lorentzian.verify_typed_biwave_volterra_theorem_import import verify


class TypedBiwaveVolterraTheoremImportTests(unittest.TestCase):
    def test_independent_exact_replay_rejects_conflation(self) -> None:
        self.assertTrue(exact_fixture()["all_zero"])
        mutant = exact_fixture(conflate_resolvents=True)
        self.assertFalse(mutant["all_zero"])
        self.assertGreater(mutant["defect_counts"]["push_through"], 0)

    def test_claim_boundary_remains_conditional(self) -> None:
        flags = build()["claim_flags"]
        self.assertTrue(flags["TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED"])
        self.assertFalse(flags["HADAMARD_STATE"])
        self.assertFalse(flags["QUANTUM_THEORY"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
