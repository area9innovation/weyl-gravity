from __future__ import annotations

from copy import deepcopy
import json
import unittest

from transfer.relative_einstein_weyl_qme_defect_nondefinition import (
    evaluate,
    validate,
)
from transfer.relative_einstein_weyl_qme_defect_nondefinition_certificate import (
    OUTPUT,
    build,
)
from transfer.verify_relative_einstein_weyl_qme_defect_nondefinition import (
    verify,
)


class RelativeEinsteinWeylQMEDefectTests(unittest.TestCase):
    def test_exact_checks(self) -> None:
        self.assertTrue(all(evaluate()["exact_checks"].values()))

    def test_complete_linear_triangle_but_no_cyclic_pushforward(self) -> None:
        value = evaluate()
        self.assertTrue(
            value["claim_flags"]["COMPLETE_CLASSICAL_LINEAR_TRIANGLE_IMPORTED"]
        )
        self.assertFalse(
            value["claim_flags"][
                "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_IMPORTED"
            ]
        )

    def test_pure_weyl_vector_is_not_relative_vector(self) -> None:
        value = evaluate()
        self.assertEqual(value["coefficient_ledger"]["relative_vector"], "UNDEFINED")
        self.assertFalse(
            value["claim_flags"]["PURE_WEYL_VECTOR_IS_RELATIVE_VECTOR"]
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_relative_coefficient_overpromotion_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["RELATIVE_COEFFICIENT_COMPUTED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
