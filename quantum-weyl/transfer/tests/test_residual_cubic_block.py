from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


QUANTUM_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUANTUM_ROOT))

from transfer.residual_cubic_block import OUTPUT_PATH, build_certificate


class ResidualCubicBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate(4)

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.certificate)

    def test_selected_residual_cubic_bracket_is_nonzero_and_closed(self) -> None:
        certificate = self.certificate
        self.assertEqual(
            certificate["result_state"],
            "SELECTED_RESIDUAL_CUBIC_BRACKET_COMPUTED",
        )
        self.assertEqual(certificate["cubic_charge"]["component_count"], 15)
        self.assertEqual(certificate["checks"]["conformal_closure"], "VERIFIED_ON_EVERY_INTERIOR_SHELL")
        self.assertEqual(certificate["checks"]["chirality_off_diagonal_nonzero_entries"], 0)

    def test_matter_self_bracket_and_missing_local_lift_are_distinguished(self) -> None:
        computed = " ".join(self.certificate["computed_taylor_blocks"])
        self.assertIn("ell_2(physical_matter, physical_matter)", computed)
        missing = " ".join(self.certificate["uncomputed_taylor_blocks"])
        self.assertIn("support-local classical q2", missing)
        guards = " ".join(self.certificate["claim_guards"])
        self.assertIn("does not serialize the complete support-local", guards)
        self.assertIn("does not prove that the Pontryagin direction is central", guards)

    def test_centered_one_particle_statement_is_scoped(self) -> None:
        self.assertEqual(self.certificate["checks"]["one_particle_centered_h4"], 0)
        self.assertIn(
            "for this residual cubic charge block",
            self.certificate["scientific_consequences"][-1],
        )


if __name__ == "__main__":
    unittest.main()
