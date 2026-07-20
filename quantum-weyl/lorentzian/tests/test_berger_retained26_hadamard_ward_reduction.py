from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_retained26_hadamard_ward_reduction import (
    support_class_audit,
    validate,
    ward_reduction_replay,
)
from lorentzian.berger_retained26_hadamard_ward_reduction_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_retained26_hadamard_ward_reduction import verify


class BergerRetained26HadamardWardReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/"
                "berger-retained26-hadamard-ward-reduction-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_ward_reduction(self) -> None:
        result = ward_reduction_replay()
        self.assertTrue(result["all_pass"])
        self.assertEqual(
            result["smooth_defect"],
            "C26=[H26_plus,q26] is a smooth kernel",
        )

    def test_kinetic_identity_is_load_bearing(self) -> None:
        self.assertFalse(
            ward_reduction_replay(kinetic_identity=False)["all_pass"]
        )

    def test_singular_intertwining_is_load_bearing(self) -> None:
        self.assertFalse(
            ward_reduction_replay(
                local_singular_intertwining=False
            )["all_pass"]
        )

    def test_compact_source_homotopy_is_not_silently_extended(self) -> None:
        result = support_class_audit()
        self.assertTrue(result["all_pass"])
        self.assertEqual(
            result["status"], "MISSING_SMOOTH_KERNEL_HOMOTOPY_CARRIER"
        )

    def test_support_overpromotion_negative_control(self) -> None:
        self.assertFalse(
            support_class_audit(
                global_smooth_kernel_homotopy_exported=True
            )["all_pass"]
        )

    def test_BRST_overpromotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
