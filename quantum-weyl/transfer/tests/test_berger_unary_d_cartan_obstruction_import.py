from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from transfer import berger_unary_d_cartan_obstruction_import as IMPORT
from transfer.berger_unary_d_cartan_obstruction_import_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class BergerUnaryDCartanObstructionImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_checked_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (ROOT / "schema/berger-unary-d-cartan-obstruction-import-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_symbol_class_and_normalized_dual_are_replayed(self) -> None:
        replay = self.certificate["exact_symbol_replay"]
        witness = self.certificate["normalized_obstruction_witness"]
        self.assertEqual(replay["symbol_ranks"], {"K1": 3, "H4": 1, "L1": 3})
        self.assertEqual(replay["cohomology_dimensions"], [0, 6, 6, 0])
        self.assertEqual(witness["dual_on_representative"], "1")
        self.assertEqual(self.certificate["source_dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(self.certificate["source_method_tags"], ["MICROLOCAL-SYMBOL"])
        self.assertTrue(all(self.certificate["independent_exact_checks"].values()))

    def test_bare_no_go_does_not_promote_an_extension_or_quantum_claim(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"])
        self.assertFalse(flags["BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION"])
        self.assertFalse(flags["QUANTUM_CLAIM"])
        self.assertEqual(
            self.certificate["descent_to_54_rows"]["status"],
            "VERIFIED_FROM_IMPORTED_D_EQUIVARIANT_SDR",
        )

    def test_mutated_normalized_witness_fails_closed(self) -> None:
        payload = deepcopy(IMPORT._git_json(IMPORT.CLASSICAL_CERTIFICATE))
        payload["normalized_field_class"]["dual_witness"][5] = "0"
        with self.assertRaisesRegex(ValueError, "normalized witness drifted"):
            IMPORT.validate_import(
                payload,
                IMPORT._git_json(IMPORT.CLASSICAL_SCHEMA),
                IMPORT._git_json(IMPORT.CLASSICAL_Q1),
                IMPORT._git_json(IMPORT.CLASSICAL_D),
                json.loads(IMPORT.GAUGE_IMPORT.read_text()),
                json.loads(IMPORT.D_IMPORT.read_text()),
            )

    def test_mutated_source_method_and_symbol_hash_fail_closed(self) -> None:
        for mutate, message in (
            (
                lambda payload: payload.__setitem__("method_tags", []),
                "method_tags|schema validation failed",
            ),
            (
                lambda payload: payload["douglis_symbol_fixture"][
                    "specialized_symbol_sha256"
                ].__setitem__("H4", "0" * 64),
                "specialized symbol hashes drifted",
            ),
        ):
            payload = deepcopy(IMPORT._git_json(IMPORT.CLASSICAL_CERTIFICATE))
            mutate(payload)
            with self.assertRaisesRegex(ValueError, message):
                IMPORT.validate_import(
                    payload,
                    IMPORT._git_json(IMPORT.CLASSICAL_SCHEMA),
                    IMPORT._git_json(IMPORT.CLASSICAL_Q1),
                    IMPORT._git_json(IMPORT.CLASSICAL_D),
                    json.loads(IMPORT.GAUGE_IMPORT.read_text()),
                    json.loads(IMPORT.D_IMPORT.read_text()),
                )


if __name__ == "__main__":
    unittest.main()
