from __future__ import annotations

import copy
import json
import unittest
from unittest import mock

from d_quotient_classical.compensator import two_phase_counterflow_trace_charge_preflight as producer
from d_quotient_classical.compensator import verify_two_phase_counterflow_trace_charge_preflight as verifier
from d_quotient_classical.atlas import generate_two_phase_counterflow_trace_charge_atlas_fragment as atlas


class TwoPhaseCounterflowTraceChargePreflightTest(unittest.TestCase):
    def test_producer_is_deterministic(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_exact_replay(self) -> None:
        verifier.verify()

    def test_atlas_is_deterministic_and_fail_closed(self) -> None:
        first = atlas.build()
        self.assertEqual(first, atlas.build())
        self.assertEqual(len(first["entries"]), 3)
        for row in first["entries"]:
            self.assertEqual(row["descriptions"]["causal"], "NO_CERTIFIED_MAP")
            self.assertEqual(row["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_import_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(producer.IMPORTS)
        mutated["gauss_structure"]["sha256"] = "0" * 64
        with mock.patch.object(producer, "IMPORTS", mutated):
            with self.assertRaisesRegex(AssertionError, "import drifted"):
                producer.build()

    def test_payload_mutation_rejected(self) -> None:
        _, payload = producer.build()
        payload["selected_fixture"]["parameters"]["alpha_R"] = "1"
        with self.assertRaisesRegex(AssertionError, "content hash"):
            producer.validate_payload(payload)

    def test_split_inertia_mutation_rejected(self) -> None:
        _, payload = producer.build()
        payload["quadratic_hessian_and_constraints"]["reduced_velocity_determinant"] = "9"
        payload["content_sha256"] = producer._digest({k: v for k, v in payload.items() if k != "content_sha256"})
        with self.assertRaisesRegex(AssertionError, "split inertia"):
            producer.validate_payload(payload)

    def test_cylinder_promotion_rejected(self) -> None:
        certificate, payload = producer.build()
        certificate["terminal_verdict"]["cylinder"] = "PASSED"
        with self.assertRaisesRegex(AssertionError, "cylinder obstruction"):
            producer.validate_certificate(certificate, payload)

    def test_unrestricted_D_promotion_rejected(self) -> None:
        certificate, payload = producer.build()
        certificate["terminal_verdict"]["unrestricted_D_is_gauge"] = True
        with self.assertRaisesRegex(AssertionError, "unrestricted D"):
            producer.validate_certificate(certificate, payload)

    def test_causal_and_Maxwell_promotion_rejected(self) -> None:
        for key in ("FULL_BV_CAUSAL_PARENT", "GREEN_HYPERBOLICITY", "HADAMARD_OR_QUANTUM", "MAXWELL_TERM"):
            certificate, payload = producer.build()
            certificate["claim_flags"][key] = True
            with self.assertRaisesRegex(AssertionError, "claim boundary"):
                producer.validate_certificate(certificate, payload)

    def test_exact_selected_fixture(self) -> None:
        certificate, _ = producer.build()
        selected = certificate["selected_fixture"]
        self.assertEqual(selected["parameters"]["alpha_B"], "5")
        self.assertEqual(selected["parameters"]["alpha_R"], "0")
        self.assertEqual(selected["reduced_L2"], "dot_u^2/8-659*u^2/1920")
        self.assertTrue(selected["Hamiltonian_positive"])


if __name__ == "__main__":
    unittest.main()
