#!/usr/bin/env python3
"""Scoped tests for the projective interaction microfactor."""

from __future__ import annotations

import json
import unittest

from black_hole_programme.phase4.axial_explicit_tplus_band_v1 import (
    produce_projective_micro as producer,
)
from black_hole_programme.phase4.axial_explicit_tplus_band_v1 import (
    verify_projective_micro as verifier,
)


class ProjectiveMicroTests(unittest.TestCase):
    def test_certificate_is_fail_closed(self) -> None:
        certificate = json.loads(producer.CERTIFICATE.read_text())
        self.assertEqual(
            certificate["status"],
            "PROJECTIVE_INTERACTION_MICRO_PASS_R4_OPEN",
        )
        self.assertTrue(
            certificate["claim_flags"][
                "local_interaction_variables_interval_enclosed"
            ]
        )
        self.assertFalse(
            certificate["claim_flags"]["complete_outgoing_frame_at_r4"]
        )
        self.assertFalse(
            certificate["claim_flags"]["explicit_Tplus_certified"]
        )

    def test_independent_audit(self) -> None:
        self.assertEqual(verifier.main(), 0)


if __name__ == "__main__":
    unittest.main()
