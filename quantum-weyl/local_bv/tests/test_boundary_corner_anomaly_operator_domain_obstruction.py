from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.boundary_corner_anomaly_operator_domain_obstruction import (
    evaluate,
    validate,
)
from local_bv.boundary_corner_anomaly_operator_domain_obstruction_certificate import (
    OUTPUT,
    build,
)
from local_bv.verify_boundary_corner_anomaly_operator_domain_obstruction import (
    verify,
)


class BoundaryCornerAnomalyObstructionTests(unittest.TestCase):
    def test_exact_checks(self) -> None:
        self.assertTrue(all(evaluate()["exact_checks"].values()))

    def test_geometry_has_faces_and_corners(self) -> None:
        carrier = evaluate()["declared_carrier"]
        self.assertEqual(len(carrier["boundary_faces"]), 3)
        self.assertEqual(len(carrier["codimension_two_corners"]), 2)

    def test_two_boundary_gauge_branches_remain_distinct(self) -> None:
        branches = evaluate()["boundary_gauge_branching"]
        self.assertIn("face_preserving_branch", branches)
        self.assertIn("moving_boundary_branch", branches)
        self.assertEqual(branches["decision"].split(":", 1)[0], "UNDEFINED")

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_boundary_cohomology_overpromotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["BOUNDARY_CORNER_COHOMOLOGY_COMPUTED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
