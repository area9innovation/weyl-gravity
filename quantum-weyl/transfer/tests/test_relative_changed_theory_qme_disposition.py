from __future__ import annotations

from copy import deepcopy
import json
import unittest

from transfer.relative_changed_theory_qme_disposition import build, validate
from transfer.relative_changed_theory_qme_disposition_certificate import (
    FINITE_OUTPUT,
    LOCAL_OUTPUT,
    OUTPUT,
    build as build_certificate,
)
from transfer.verify_relative_changed_theory_qme_disposition import (
    verify,
    verify_payload,
)


class RelativeChangedTheoryQMEDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_all_repair_orbits_remain_undefined(self) -> None:
        value = build()
        self.assertEqual(
            [row["relative_one_loop_defect"] for row in value["repair_orbit_dispositions"]],
            ["UNDEFINED", "UNDEFINED", "UNDEFINED"],
        )
        self.assertTrue(all(value["exact_checks"].values()))

    def test_two_independent_rails_are_emitted(self) -> None:
        self.assertEqual(
            json.loads(FINITE_OUTPUT.read_text()),
            self.value["finite_carrier_rail"],
        )
        self.assertEqual(
            json.loads(LOCAL_OUTPUT.read_text()),
            self.value["local_cohomology_rail"],
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build_certificate())

    def test_independent_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "RELATIVE_CHANGED_THEORY_QME_NONDEFINITION",
        )

    def test_inertia_mutation_rejected_separately(self) -> None:
        mutant = deepcopy(self.value)
        mutant["finite_carrier_rail"]["exact_compatibility"][
            "rank_one_is_minimal_pairing_or_action_form_change"
        ] = False
        with self.assertRaises(ValueError):
            verify_payload(mutant)

    def test_anomaly_coefficient_mutation_rejected_separately(self) -> None:
        mutant = deepcopy(self.value)
        mutant["coefficient_ledger"]["changed_pairing_relative_vector"] = {
            "ANOM_OMEGA_C2": {"numerator": 199, "denominator": 30}
        }
        with self.assertRaisesRegex(ValueError, "schema|coefficient"):
            verify_payload(mutant)

    def test_qme_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"][
            "RELATIVE_ONE_LOOP_QME_DEFINED_ON_ANY_REPAIR_ORBIT"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_strict_anomaly_cancellation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["STRICT_PURE_WEYL_ANOMALY_CANCELLED"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
