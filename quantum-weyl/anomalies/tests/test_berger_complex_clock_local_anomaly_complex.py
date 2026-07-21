from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.berger_complex_clock_local_anomaly_complex import (
    OUTPUT,
    PAYLOAD,
    REPORT,
    _report,
    build,
)
from anomalies.verify_berger_complex_clock_local_anomaly_complex import verify, verify_values


class BergerComplexClockLocalAnomalyComplexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result, self.payload = build()

    def _reject_result_mutation(self, mutate) -> None:
        result = deepcopy(self.result)
        mutate(result)
        with self.assertRaises(Exception):
            verify_values(result, self.payload)

    def _reject_payload_mutation(self, mutate) -> None:
        payload = deepcopy(self.payload)
        mutate(payload)
        with self.assertRaises(Exception):
            verify_values(self.result, payload)

    def test_reproduction_and_independent_verification(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.result)
        self.assertEqual(json.loads(PAYLOAD.read_text()), self.payload)
        self.assertEqual(REPORT.read_text(), _report(self.result))
        self.assertEqual(verify(), self.result)

    def test_scientific_disposition(self) -> None:
        self.assertEqual(self.result["H14"]["even_quotient_dimension"], 0)
        self.assertEqual(self.result["H14"]["odd_quotient_dimension"], 0)
        self.assertEqual(
            self.result["strict_to_coupled_action_morphism"]["verdict"],
            "NONEXISTENT_IN_DECLARED_COMPLETE_MORPHISM_CLASS",
        )
        self.assertEqual(
            self.result["coefficient_and_qme_status"]["QME_status"],
            "NOT_RESTORED_FOR_GRAVITY_CLOCK_THEORY",
        )

    def test_nine_fail_closed_mutations(self) -> None:
        self._reject_result_mutation(
            lambda value: value["strict_to_coupled_action_morphism"]["separator"]["separation"].update(numerator=0)
        )
        self._reject_result_mutation(lambda value: value["H14"].update(even_quotient_dimension=1))
        self._reject_result_mutation(
            lambda value: value["coefficient_and_qme_status"].update(QME_status="QME_RESTORED")
        )
        self._reject_result_mutation(
            lambda value: value["symmetry_disposition"].update(K_Berger="LOCAL_GAUGE_GHOST")
        )
        self._reject_result_mutation(
            lambda value: value["dependencies"]["positive_berger_clock"].update(sha256="0" * 64)
        )
        self._reject_result_mutation(
            lambda value: value["candidate_completeness"]["ledger"][0].update(status="NONTRIVIAL")
        )
        self._reject_payload_mutation(lambda value: value.update(coefficient_status="COEFFICIENT_COMPUTED"))
        self._reject_result_mutation(
            lambda value: value["quartet_reduction"]["Q_W"][1][0].update(numerator=-1)
        )
        self._reject_result_mutation(
            lambda value: value["candidate_completeness"]["positive_antifield_characteristic_current"]["CE_control"].update(H2_dimension=1)
        )


if __name__ == "__main__":
    unittest.main()
