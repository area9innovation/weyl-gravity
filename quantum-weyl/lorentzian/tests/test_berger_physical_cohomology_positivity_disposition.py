from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_physical_cohomology_positivity_disposition import (
    carrier_classification,
    representative_change_replay,
    validate,
)
from lorentzian.berger_physical_cohomology_positivity_disposition_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_physical_cohomology_positivity_disposition import (
    verify,
)


class BergerPhysicalCohomologyPositivityDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/"
                "berger-physical-cohomology-positivity-disposition-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_representative_change_formula(self) -> None:
        result = representative_change_replay()
        self.assertTrue(result["all_pass"])
        self.assertFalse(result["pairing_descends"])

    def test_pairing_null_Ward_mutation_invalidates_current_boundary(self) -> None:
        self.assertFalse(
            representative_change_replay(
                ward_defect_certified_pairing_null=True
            )["all_pass"]
        )

    def test_both_closed_arguments_are_load_bearing(self) -> None:
        self.assertFalse(
            representative_change_replay(
                closed_first_argument=False
            )["all_pass"]
        )
        self.assertFalse(
            representative_change_replay(
                closed_second_argument=False
            )["all_pass"]
        )

    def test_every_declared_available_carrier_is_classified(self) -> None:
        rows = carrier_classification()
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            {row["physical_form"] for row in rows},
            {"UNDEFINED", "NO_CERTIFIED_MAP", "NO_HADAMARD_TWO_POINT_FUNCTION"},
        )

    def test_auxiliary_and_reduced_signs_are_not_physical(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["BERGER_AUXILIARY_SIGNATURE_NOT_PHYSICAL_NORM"])
        self.assertTrue(
            flags["BERGER_REDUCED_EAL_SIGN_NOT_BERGER_PHYSICAL_NORM"]
        )
        self.assertFalse(flags["BERGER_PHYSICAL_KREIN_SECTOR_UNAVOIDABLE"])

    def test_positivity_overpromotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_PHYSICAL_OBSERVABLE_POSITIVITY"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
