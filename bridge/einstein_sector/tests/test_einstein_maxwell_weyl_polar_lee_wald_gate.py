from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    _direct_sample_audit,
    _shell_audit,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_lee_wald_gate import (
    verify_certificate as verify_independently,
)


class PolarLeeWaldGateTests(unittest.TestCase):
    def test_direct_samples_and_interpolation(self) -> None:
        audit = _direct_sample_audit()
        self.assertTrue(audit["spectral_interpolation"]["all_physical_ell_at_least_2_match"])
        self.assertEqual([sample["lambda"] for sample in audit["samples"]], [6, 12, 20])
        for sample in audit["samples"]:
            self.assertEqual(sample["direct_minus_action_Green_remainder"], [["0"] * 4 for _ in range(4)])

    def test_shell_pairing(self) -> None:
        audit = _shell_audit()
        self.assertEqual(audit["Einstein_extra_mixed_remainder_mod_p_q"], ["0", "0"])
        self.assertEqual(audit["extra_positive_frequency_inertia"], [2, 0])
        self.assertEqual(audit["complete_polar_target_inertia_before_residual_quotient"], [3, 1])

    def test_certificate_schema_and_independent_verifier(self) -> None:
        payload = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
