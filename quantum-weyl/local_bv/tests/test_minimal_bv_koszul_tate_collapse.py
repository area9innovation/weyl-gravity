from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from local_bv.minimal_bv_koszul_tate_collapse import analysis
from local_bv.minimal_bv_koszul_tate_collapse_certificate import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from local_bv.verify_minimal_bv_koszul_tate_collapse import verify


class MinimalBVKoszulTateCollapseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analysis = analysis()
        cls.certificate = build()

    def test_all_positive_antifield_atoms_are_contracted(self) -> None:
        self.assertEqual(self.analysis["pair_atom_count"], 12)
        self.assertEqual(self.analysis["positive_antifield_atom_count"], 10)
        self.assertEqual(len(self.analysis["contractible_pairs"]), 6)
        self.assertGreater(self.analysis["regression_monomial_count"], 1000)

    def test_afn0_classes_lift_without_claiming_diff_completion(self) -> None:
        ledger = self.analysis["lift_ledger"]
        self.assertEqual(
            {row["representative_id"] for row in ledger["H04_covariant_candidate_classes"]},
            {"CT_C2", "CT_E4", "CT_C_DUAL_C"},
        )
        self.assertEqual(
            {row["representative_id"] for row in ledger["H14_Weyl_ghost_candidate_classes"]},
            {"ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C"},
        )
        self.assertTrue(
            all(
                row["minimal_KT_lift_status"]
                == "LIFTS_UNCHANGED_ON_REGULAR_BACH_LOCUS"
                for key in ("H04_covariant_candidate_classes", "H14_Weyl_ghost_candidate_classes")
                for row in ledger[key]
            )
        )
        self.assertEqual(
            {
                (row["representative_id"], row["minimal_KT_lift_status"])
                for row in ledger["exact_rows"]
            },
            {
                ("CT_BOX_R", "REMAINS_D_H_EXACT"),
                ("ANOM_OMEGA_BOX_R", "REMAINS_Q_EXACT_MOD_D_H"),
            },
        )
        self.assertEqual(self.analysis["open_sectors"]["full_minimal_BV_H14"], "NOT_COMPUTED")

    def test_certificate_reproduces_and_is_strict(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, self.certificate)
        self.assertEqual(value, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        validate(value)


if __name__ == "__main__":
    unittest.main()
