from __future__ import annotations

import json
import unittest

from local_bv.schema_validation import validate_instance
from transfer.berger_coupled_64_q2_import import _coefficient, build_payload, import_coupled_q2
from transfer.berger_coupled_64_q2_import_certificate import HERE, OUTPUT, build_certificate
from transfer.verify_berger_coupled_64_q2_import import verify


class BergerCoupled64Q2ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.imported = import_coupled_q2()
        cls.payload = build_payload()

    def test_complete_overlay_is_exact_and_pinned(self) -> None:
        self.assertEqual(self.imported.overlay_term_count, 1954)
        self.assertEqual(self.imported.overlay_nonzero_rows, 25)
        self.assertEqual(self.imported.maximum_total_jet_order, 3)
        self.assertEqual(len(self.imported.row_ids), 64)
        self.assertEqual(self.imported.K_derivation_terms_replayed, 1954)
        with self.assertRaisesRegex(ValueError, "exact rational"):
            _coefficient({"rational": 0.5, "sqrt10": 0})

    def test_gravity_seam_and_structural_replay_are_complete(self) -> None:
        self.assertEqual(self.payload["coverage"]["gravity_base_terms"], 150305)
        self.assertEqual(self.payload["coverage"]["combined_terms"], 152259)
        replay = self.payload["independent_replay"]
        self.assertTrue(
            all(
                value == "VERIFIED"
                for key, value in replay.items()
                if key != "K_derivation_overlay_terms_replayed"
            )
        )

    def test_generator_correction_is_fail_closed(self) -> None:
        semantics = self.payload["generator_semantics"]
        self.assertEqual(semantics["frozen_generator"], "K_Berger=D-omega R")
        self.assertEqual(
            semantics["raw_D_status"], "AFFINE_WITH_NONZERO_ZERO_ARITY_COMPONENT"
        )
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["K_BERGER_EQUIVARIANCE_INDEPENDENTLY_REPLAYED"])
        self.assertFalse(flags["RAW_D_EQUIVARIANCE_INDEPENDENTLY_REPLAYED"])
        self.assertFalse(flags["RAW_D_CARTAN_CERTIFIED"])

    def test_missing_carrier_theorem_is_minimal_and_fail_closed(self) -> None:
        theorem = self.payload["missing_carrier_theorem"]
        self.assertEqual(
            theorem["minimal_requested_exports"],
            [
                "BERGER_PORTABLE_64_ROW_UNARY_Q1",
                "BERGER_PORTABLE_64_ROW_CYCLIC_PAIRING",
                "BERGER_MAXWELL_UNARY_CONTRACTION",
            ],
        )
        flags = self.payload["claim_flags"]
        self.assertFalse(flags["Q1_Q2_IDENTITY_INDEPENDENTLY_REPLAYED"])
        self.assertFalse(flags["BV_CYCLICITY_INDEPENDENTLY_REPLAYED"])
        self.assertFalse(flags["MIXED_VERTEX_TRANSFERRED"])
        self.assertFalse(flags["QUANTUM_CLAIM"])

    def test_certificate_reproduces_and_has_strict_schema(self) -> None:
        certificate = build_certificate()
        schema = json.loads(
            (HERE / "schema/berger-coupled-64-q2-import-v1.schema.json").read_text()
        )
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        self.assertFalse(validate_instance(certificate, schema))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build_certificate())


if __name__ == "__main__":
    unittest.main()
