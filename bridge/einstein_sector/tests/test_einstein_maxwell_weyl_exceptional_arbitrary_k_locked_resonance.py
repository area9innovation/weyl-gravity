from __future__ import annotations

import copy
import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance import (
    ATLAS,
    OUTPUT,
    build_certificate,
    verify_output,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance import (
    verify_certificate,
    verify_payload,
)


class ExceptionalArbitraryKLockedResonanceTests(unittest.TestCase):
    def test_generated_certificate_current(self) -> None:
        verify_output()

    def test_independent_verifier(self) -> None:
        verify_certificate()

    def test_authoritative_join_hash(self) -> None:
        value = build_certificate()
        self.assertEqual(
            value["provenance"]["inputs"]["join"]["sha256"],
            "63b605c2441e9cf9d38e8b542641f060cc1a240de0af377cee57ebb0c0b848fd",
        )

    def test_atlas_is_fail_closed(self) -> None:
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        entry = atlas["entries"][0]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"],
            "OPEN",
        )
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_decisive_coefficient_mutation_rejected(self) -> None:
        value = json.loads(OUTPUT.read_text(encoding="utf-8"))
        mutated = copy.deepcopy(value)
        mutated["locked_difference_matrix"]["nonzero_columns"]["axial_L1_output"] = (
            "R_ax(k)=0"
        )
        with self.assertRaises(AssertionError):
            verify_payload(mutated)


if __name__ == "__main__":
    unittest.main()
