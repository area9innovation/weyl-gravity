from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.local_anomaly_antifield_completion_audit import evaluate, validate
from local_bv.local_anomaly_antifield_completion_audit_certificate import (
    OUTPUT,
    build,
)
from local_bv.verify_local_anomaly_antifield_completion_audit import verify


class LocalAnomalyAntifieldCompletionAuditTests(unittest.TestCase):
    def test_exact_audit_passes(self) -> None:
        value = evaluate()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            value["science_forge"]["stop_condition_status"], "DONE"
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_two_method_coordinates(self) -> None:
        value = build()["two_method_coefficients"]
        self.assertEqual(
            set(value["type_A"].values()), {"87/20"}
        )
        self.assertEqual(
            set(value["type_B"].values()), {"199/30"}
        )

    def test_lifecycles_are_not_conflated(self) -> None:
        value = build()["QME_lifecycles"]
        self.assertEqual(
            value["strict_fixed_field_content"],
            "OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN",
        )
        self.assertEqual(
            value["tau_adic_compensator_extended"],
            "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN",
        )
        self.assertEqual(value["Lorentzian"], "OPEN")

    def test_overpromotion_fails_closed(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["STRICT_THEORY_ANOMALY_FREE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
