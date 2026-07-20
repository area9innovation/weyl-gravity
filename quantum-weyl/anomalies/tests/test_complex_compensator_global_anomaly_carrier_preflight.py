from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.complex_compensator_global_anomaly_carrier_preflight import validate
from anomalies.complex_compensator_global_anomaly_carrier_preflight_certificate import (
    OUTPUT,
    certificate,
)
from anomalies.verify_complex_compensator_global_anomaly_carrier_preflight import (
    verify,
    verify_payload,
)


class ComplexCompensatorGlobalAnomalyCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, certificate())

    def test_independent_topology_and_receiver_replay(self) -> None:
        self.assertEqual(
            verify()["result_id"],
            "COMPLEX_COMPENSATOR_GLOBAL_ANOMALY_CARRIER_NONDEFINITION",
        )

    def test_local_u1_mutation_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["imported_theory"]["internal_phase_symmetry"] = "LOCAL_U1"
        mutant["imported_theory"]["internal_U1_ghost_present"] = True
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)

    def test_nonzero_c1_sector_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["bundle_and_winding_ledger"]["H2"] = "Z"
        mutant["finite_index_ledger"]["principal_U1_Chern_class_rank"] = 1
        with self.assertRaisesRegex(ValueError, "schema|cellular|boundary"):
            verify_payload(mutant)

    def test_berger_magnetic_cross_background_substitution_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["bundle_and_winding_ledger"]["Berger_magnetic_bundle"] = "TRIVIAL"
        with self.assertRaisesRegex(ValueError, "schema|boundary"):
            verify_payload(mutant)

    def test_global_anomaly_freedom_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["GLOBAL_ANOMALY_FREE"] = True
        with self.assertRaisesRegex(ValueError, "boundary"):
            validate(mutant)

    def test_determinant_line_without_family_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["family_operator_requirements"]["Berezinian_determinant_line"] = True
        with self.assertRaisesRegex(ValueError, "schema"):
            verify_payload(mutant)

    def test_diff_mapping_class_guess_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["group_component_ledger"][2]["disconnected_components"] = "Z2"
        with self.assertRaisesRegex(ValueError, "boundary"):
            verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
