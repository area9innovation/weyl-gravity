from __future__ import annotations

import copy
import unittest
from unittest import mock

from d_quotient_classical.compensator import (
    general_closed_cauchy_relative_phase_hodge_theorem as producer,
)
from d_quotient_classical.compensator import (
    verify_general_closed_cauchy_relative_phase_hodge_theorem as verifier,
)
from d_quotient_classical.atlas import (
    generate_general_closed_cauchy_relative_phase_hodge_atlas_fragment as atlas,
)


class GeneralClosedCauchyRelativePhaseHodgeTheoremTest(unittest.TestCase):
    def test_producer_is_deterministic(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_exact_replay(self) -> None:
        verifier.verify()

    def test_atlas_is_deterministic_and_fail_closed(self) -> None:
        first = atlas.build()
        self.assertEqual(first, atlas.build())
        self.assertEqual(len(first["entries"]), 5)
        for entry in first["entries"]:
            self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")
            self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_import_hash_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(producer.IMPORT)
        mutated["sha256"] = "0" * 64
        with mock.patch.object(producer, "IMPORT", mutated):
            with self.assertRaisesRegex(AssertionError, "import drifted"):
                producer.build()

    def test_payload_mutation_rejected(self) -> None:
        _, payload = producer.build()
        payload["fixtures"][0]["relative_metric_Grel"] = [["-6/5"]]
        with self.assertRaisesRegex(AssertionError, "content hash"):
            producer.validate_payload(payload)

    def test_claim_promotion_rejected(self) -> None:
        certificate, payload = producer.build()
        certificate["claim_flags"]["GLOBAL_GREEN_HYPERBOLICITY"] = True
        with self.assertRaisesRegex(AssertionError, "claim boundary"):
            producer.validate_certificate(certificate, payload)

    def test_b1_positive_wilson_counts(self) -> None:
        _, payload = producer.build()
        row = next(item for item in payload["fixtures"] if item["fixture_id"].startswith("T3"))
        self.assertEqual(row["topology"]["betti_1"], 3)
        self.assertEqual(row["harmonic_connection_tangent_dimension"], 6)
        self.assertEqual(row["massive_harmonic_family_count"], 3)
        self.assertEqual(row["kernel_Wilson_family_count"], 3)
        self.assertEqual(row["relative_winding_free_rank"], 6)

    def test_nonprimitive_charge_and_torsion_are_retained(self) -> None:
        _, payload = producer.build()
        row = next(item for item in payload["fixtures"] if item["fixture_id"].startswith("L5"))
        self.assertEqual(row["smith_invariants"], [2])
        self.assertEqual(row["constant_gauge_stabilizer"]["component_count"], 2)
        self.assertEqual(row["topology"]["torsion_H2_invariant_factors"], [5])
        self.assertEqual(row["admissible_torsion_bundle_kernel_order"], 1)

    def test_support_strata_recompute_charge_rank(self) -> None:
        _, payload = producer.build()
        row = next(item for item in payload["fixtures"] if item["fixture_id"].startswith("T3"))
        neutral_only = next(
            item for item in row["active_support_strata"] if item["active_phase_rows"] == [2]
        )
        self.assertEqual(neutral_only["rank_Q_support"], 0)
        self.assertEqual(neutral_only["relative_phase_dimension_on_stratum"], 1)

    def test_global_quotient_and_obstruction_are_explicit(self) -> None:
        certificate, _ = producer.build()
        quotient = certificate["integral_lattice_quotient"]
        self.assertIn("Z^n times R^r", quotient["quotient_derivation"])
        self.assertIn("integral complement", quotient["topological_obstruction"])
        self.assertEqual(
            certificate["topological_obstruction"]["status"],
            "STRUCTURAL_TOPOLOGICAL_OBSTRUCTION",
        )

    def test_s3_and_constant_mode_reproduction_flags(self) -> None:
        certificate, _ = producer.build()
        terminal = certificate["terminal_verdict"]
        self.assertTrue(terminal["S3_reproduced"])
        self.assertTrue(terminal["homogeneous_constant_mode_reproduced"])
        self.assertFalse(terminal["full_causal_parent_activated"])


if __name__ == "__main__":
    unittest.main()
