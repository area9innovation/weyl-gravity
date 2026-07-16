from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian import clock_reattached_principal_import as IMPORTER
from lorentzian.clock_reattached_principal_import_certificate import (
    OUTPUT,
    build_certificate,
)


ROOT = Path(__file__).resolve().parents[1]


class ClockReattachedPrincipalImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORTER._git_json(IMPORTER.CERTIFICATE)
        cls.schema = IMPORTER._git_json(IMPORTER.SCHEMA)
        cls.q1 = IMPORTER._git_json(IMPORTER.Q1_CERTIFICATE)
        cls.clock = IMPORTER._git_json(IMPORTER.CLOCK_CERTIFICATE)

    def test_checked_certificate_reproduces_and_validates(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "berger-clock-reattached-principal-import-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))
        self.assertFalse(certificate["quantum_execution_authorized"])

    def test_scalar_biwave_identities_are_independently_replayed(self) -> None:
        result = IMPORTER.validate_import(
            self.payload, self.schema, self.q1, self.clock
        )
        self.assertTrue(all(result["independent_exact_checks"].values()))
        self.assertEqual(
            result["preferred_realization"]["scalar_characteristic_set"],
            "zeta^2=0",
        )
        self.assertEqual(result["next_gate"], "BERGER_CURVED_CLOCK_REATTACHED_WITNESS")

    def test_mutated_companion_fails_exact_replay(self) -> None:
        forged = deepcopy(self.payload)
        forged["normalized_witness"]["companion_matrix"][0][0] = "0"
        with self.assertRaisesRegex(ValueError, "principal replay failed"):
            IMPORTER.validate_import(forged, self.schema, self.q1, self.clock)

    def test_nonlocal_clock_sdr_fails_closed(self) -> None:
        forged = deepcopy(self.clock)
        forged["flags"]["support_local_clock_SDR_exact"] = False
        with self.assertRaisesRegex(ValueError, "clock SDR dependency"):
            IMPORTER.validate_import(self.payload, self.schema, self.q1, forged)

    def test_curved_or_causal_promotion_fails_closed(self) -> None:
        for flag in (
            "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
        ):
            with self.subTest(flag=flag):
                forged = deepcopy(self.payload)
                forged["flags"][flag] = True
                with self.assertRaisesRegex(ValueError, "claim boundary"):
                    IMPORTER.validate_import(forged, self.schema, self.q1, self.clock)


if __name__ == "__main__":
    unittest.main()
