from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector.verify_einstein_weyl_alpha_b3_ostrogradsky_canonical_crosswalk import (
    CERT,
    verify,
)


class AlphaB3CanonicalCrosswalkTests(unittest.TestCase):
    def _reject(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify(path)

    def test_independent_verifier(self) -> None:
        verify()

    def test_mutation_controls_are_declared(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        self.assertEqual(payload["normalization"]["exact_action_scale_selected_over_reference"], "-3/2")
        self.assertEqual(payload["normalization"]["selected_one_slot_cubic"], "-s**2/48")
        self.assertEqual(payload["channel_coverage"]["actual_signed_channel_rows"], 27)
        self.assertTrue(payload["symplectic_and_equation_checks"]["symplecticity"])

    def test_rescaled_background_is_detectable(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        mutated = copy.deepcopy(payload)
        mutated["background"]["P0_coordinate_density"][0][0] = "2*sin(theta)"
        self._reject(mutated)

    def test_omitted_signed_channel_is_detectable(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        payload["signed_channel_crosswalk"] = payload["signed_channel_crosswalk"][:-1]
        self._reject(payload)

    def test_zeroed_pi_is_detectable(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        payload["linear_polar_crosswalk"]["2"]["delta_pi_over_phase"] = [["0"] * 3 for _ in range(3)]
        self._reject(payload)

    def test_boundary_shift_is_detectable(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        payload["normalization"]["boundary_convention"] = "add an unspecified time boundary term"
        self._reject(payload)

    def test_competing_action_is_detectable(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        payload["normalization"]["exact_action_scale_selected_over_reference"] = "1"
        self._reject(payload)

    def test_nonzero_omitted_shift_is_detectable(self) -> None:
        payload = json.loads(CERT.read_text(encoding="utf-8"))
        row = next(row for row in payload["signed_channel_crosswalk"] if row["ell"] == 2)
        row["covariant_coefficients"][1] = "1"
        self._reject(payload)


if __name__ == "__main__":
    unittest.main()
