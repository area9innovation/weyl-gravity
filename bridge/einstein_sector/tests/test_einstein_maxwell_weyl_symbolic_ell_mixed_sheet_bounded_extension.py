"""Tests for the symbolic mixed-sheet bounded extension join."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension import OUTPUT, build_certificate


class SymbolicEllMixedSheetBoundedExtensionTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build_certificate())

    def test_bounded_but_not_causal_or_all_orders(self) -> None:
        payload = build_certificate()
        self.assertEqual(payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "CERTIFIED")
        self.assertEqual(payload["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        self.assertFalse(payload["classification"]["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
