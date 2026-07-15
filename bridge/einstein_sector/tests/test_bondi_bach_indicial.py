from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import bondi_bach_indicial


class BondiBachIndicialTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        bondi_bach_indicial.verify_certificate()

    def test_roots_and_boundary_roles(self) -> None:
        result = bondi_bach_indicial.build_certificate()
        self.assertEqual(result["radiative_indicial_roots"], ["0", "1"])
        self.assertFalse(result["p1_einstein_falloff"]["boundary_metric_changed"])
        self.assertTrue(result["p0_extra_bach_falloff"]["boundary_metric_changed"])
        self.assertEqual(
            result["kinematic_boundary_selection"]["status"], "KINEMATIC_ONLY"
        )
        self.assertFalse(
            result["claim_flags"]["boundary_condition_preserved_by_causal_green_operators"]
        )
        self.assertEqual(
            result["series_recursions"]["leading_radiative_equation"],
            "4p(p-1) d_u^2 f_0=0",
        )

    def test_exact_single_term_coefficients(self) -> None:
        p, angular = bondi_bach_indicial.sp.symbols("p L")
        self.assertEqual(
            bondi_bach_indicial.biwave_coefficients(p, angular)[0],
            4 * p * (p - 1),
        )
        self.assertEqual(
            bondi_bach_indicial.biwave_coefficients(0, angular),
            (0, 0, angular * (angular - 2)),
        )

    def test_false_causal_promotion_is_rejected(self) -> None:
        payload = bondi_bach_indicial.build_certificate()
        payload["claim_flags"]["boundary_condition_preserved_by_causal_green_operators"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(bondi_bach_indicial.BondiBachIndicialError):
                bondi_bach_indicial.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
