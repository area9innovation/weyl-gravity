from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_independent_weyl_connection_level4_no_go import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1.json"
)


class IndependentWeylConnectionLevel4NoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_charge_lattice_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_gauge_symbol_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["gauge_rank_and_reducibility"]["gauge_symbol"]["entries"][0][
            "coefficient"
        ] = "2"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_phase_weight_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_Ward_locus"]["constant_candidate_Weyl_weights"][
            "phase_kinetic"
        ] = "0"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_forced_zero_set_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_Ward_locus"]["complete_strata"]["Delta_nonzero"][
            "forced_zero_coefficients"
        ].remove("kappa_theta")
        with self.assertRaises(Exception):
            verify(mutated)

    def test_nonempty_intersection_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["terminal_verdict"][
            "independent_trace_gauge_and_nonzero_clock_charge_intersection"
        ] = "NONEMPTY"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_selected_action_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["SELECTED_LEVEL4_ACTION"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_green_parent_and_q2_promotions_rejected(self) -> None:
        for key in ("support_local_Green_parent", "nonlinear_q2"):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["gate_disposition"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)

    def test_complexified_and_quantum_promotions_rejected(self) -> None:
        for key in (
            "INTERNAL_U1_OR_COMPLEXIFIED_CONNECTION",
            "HADAMARD_ANOMALY_QME_OR_QUANTUM",
        ):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
