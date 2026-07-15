import unittest
from fractions import Fraction

from local_bv.dimension_four_candidates import dimension_four_candidate_analysis


class DimensionFourCandidateTests(unittest.TestCase):
    def test_generated_ansatz_and_weyl_kernel(self) -> None:
        analysis = dimension_four_candidate_analysis()
        self.assertEqual(analysis["quadratic_ansatz_dimension"], 3)
        self.assertEqual(analysis["closed_kernel_dimension"], 2)
        self.assertEqual(
            analysis["integrated_weyl_variation"],
            ((Fraction(-4), Fraction(-4), Fraction(-12)),),
        )
        self.assertEqual(len(analysis["closed_kernel"]), 2)

    def test_conventional_pair_spans_computed_kernel(self) -> None:
        analysis = dimension_four_candidate_analysis()
        variation = analysis["integrated_weyl_variation"][0]
        for vector in analysis["conventional_closed_basis"]:
            self.assertEqual(
                sum(coefficient * value for coefficient, value in zip(variation, vector)),
                0,
            )
        self.assertEqual(
            analysis["conventional_closed_basis"],
            (
                (Fraction(1), Fraction(-2), Fraction(1, 3)),
                (Fraction(1), Fraction(-4), Fraction(1)),
            ),
        )

    def test_strict_and_modulo_divergence_closure_are_distinct(self) -> None:
        analysis = dimension_four_candidate_analysis()
        local = analysis["local_weyl_variation"]
        c2, e4 = analysis["conventional_closed_basis"]
        c2_variation = tuple(
            sum(coefficient * value for coefficient, value in zip(row, c2))
            for row in local
        )
        e4_variation = tuple(
            sum(coefficient * value for coefficient, value in zip(row, e4))
            for row in local
        )
        self.assertEqual(c2_variation, (Fraction(0), Fraction(0)))
        self.assertEqual(e4_variation, (Fraction(8), Fraction(-4)))
        self.assertEqual(e4_variation[1], -Fraction(1, 2) * e4_variation[0])

    def test_candidate_ledgers_are_complete_within_declared_scope(self) -> None:
        analysis = dimension_four_candidate_analysis()
        self.assertEqual(
            [record["class_id"] for record in analysis["counterterms"]],
            ["CT_C2", "CT_E4", "CT_C_DUAL_C", "CT_BOX_R"],
        )
        self.assertEqual(
            [record["class_id"] for record in analysis["anomalies"]],
            [
                "ANOM_OMEGA_C2",
                "ANOM_OMEGA_E4",
                "ANOM_OMEGA_C_DUAL_C",
                "ANOM_OMEGA_BOX_R",
            ],
        )
        records = analysis["counterterms"] + analysis["anomalies"]
        statuses = {record["class_id"]: record["class_status"] for record in records}
        self.assertEqual(statuses["CT_BOX_R"], "EXACT")
        self.assertEqual(statuses["ANOM_OMEGA_BOX_R"], "EXACT")
        self.assertTrue(
            all(
                status == "UNDECIDED"
                for class_id, status in statuses.items()
                if "BOX_R" not in class_id
            )
        )
        self.assertTrue(
            all(record["diff_descent_status"] == "NONZERO_DIFF_TOWER" for record in records)
        )
        intrinsic = {
            record["class_id"]: record["intrinsic_weyl_descent_status"]
            for record in records
        }
        self.assertEqual(intrinsic["CT_C2"], "STRICTLY_WEYL_INVARIANT")
        self.assertEqual(intrinsic["CT_C_DUAL_C"], "STRICTLY_WEYL_INVARIANT")
        self.assertEqual(intrinsic["ANOM_OMEGA_C2"], "TRIVIAL")
        self.assertEqual(intrinsic["ANOM_OMEGA_C_DUAL_C"], "TRIVIAL")

    def test_named_even_candidates_reach_the_native_weyl_carrier(self) -> None:
        analysis = dimension_four_candidate_analysis()
        self.assertEqual(
            analysis["c2_weyl_restriction"],
            analysis["e4_weyl_restriction"],
        )
        quotient = analysis["target_analysis"]["even"]["quotient"]
        self.assertTrue(
            any(quotient.free_coordinates(analysis["c2_weyl_restriction"]))
        )

    def test_box_r_has_explicit_boundary_and_anomaly_trivialization(self) -> None:
        analysis = dimension_four_candidate_analysis()
        self.assertTrue(analysis["box_r"])
        self.assertTrue(analysis["box_r_primitive"].index_multiplicities().get(0) == 1)
        self.assertEqual(
            analysis["box_anomaly_trivialization_coefficient"],
            Fraction(-1, 12),
        )
        box_anomaly = next(
            record
            for record in analysis["anomalies"]
            if record["class_id"] == "ANOM_OMEGA_BOX_R"
        )
        self.assertEqual(box_anomaly["integrated_triviality"], "COUNTERTERM_REMOVABLE")


if __name__ == "__main__":
    unittest.main()
