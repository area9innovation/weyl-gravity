import json
import unittest
from fractions import Fraction

from .runner import AGG, CERT, RAW
from .verify import main


class V6BChildRepairTest(unittest.TestCase):
    def test_independent_verifier(self) -> None:
        main()

    def test_only_requested_children_were_evaluated(self) -> None:
        raw = json.loads(RAW.read_text())
        self.assertEqual(
            [
                (entry["kind"], entry["panel"], entry["panel_count"])
                for entry in raw["observations"]
            ],
            [
                ("imported_parent_observation", 104, 512),
                ("repair_child", 208, 1024),
                ("repair_child", 209, 1024),
            ],
        )

    def test_claims_remain_fail_closed(self) -> None:
        certificate = json.loads(CERT.read_text())
        aggregate = json.loads(AGG.read_text())
        self.assertLessEqual(
            Fraction(aggregate["summary"]["coverage_stop"]),
            Fraction(105, 512),
        )
        self.assertFalse(certificate["claim_flags"]["root_count_certified"])
        self.assertFalse(certificate["claim_flags"]["QNM_location_certified"])
        self.assertFalse(certificate["claim_flags"]["Smith_selector_certified"])
        self.assertFalse(
            certificate["claim_flags"]["defective_fibre_or_EP2_certified"]
        )
