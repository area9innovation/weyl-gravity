from __future__ import annotations

import sys
import unittest

from d_quotient_classical.minimal_bv_antifield import classical_minimal_bv_antifield_export_v2 as producer


class ClassicalMinimalBVAntifieldV2Tests(unittest.TestCase):
    def test_complete_minimal_roles(self) -> None:
        self.assertEqual(
            {row["role"] for row in producer.generators()},
            {"metric", "diffeomorphism_ghost", "weyl_ghost", "metric_antifield", "diffeomorphism_ghost_antifield", "weyl_ghost_antifield"},
        )

    def test_actual_bach_and_noether_rows(self) -> None:
        foundations = producer.foundation_payloads()
        action = foundations[producer.DEPENDENCY_FILES["action_normalization"]]
        noether = foundations[producer.DEPENDENCY_FILES["noether_identity_rows"]]
        self.assertIn("B^{mu nu}", action["Euler_coordinate"])
        self.assertIn("nabla_nu g_star", noether["Koszul_Tate_rows"]["delta xi_star_mu"])

    def test_quantum_receiver_accepts_the_declared_graded_window(self) -> None:
        sys.path.insert(0, str(producer.ROOT / "quantum-weyl"))
        from classical_import.verify_antifield_export_v2 import validate_export_v2

        replay = validate_export_v2(producer.build_export("0" * 40))
        projection = replay["filtered_complex_adapter"]["scope_projection"]
        self.assertEqual(projection["status"], "DECLARED_GRADED_WINDOW_ENFORCED")
        self.assertGreater(projection["projected_monomial_count"], 0)

    def test_official_export_is_written(self) -> None:
        self.assertTrue(producer.OUTPUT.exists())


if __name__ == "__main__":
    unittest.main()
