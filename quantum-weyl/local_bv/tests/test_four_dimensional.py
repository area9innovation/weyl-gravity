import unittest

from local_bv.curvature import (
    curvature_product_bianchi_analysis,
    one_derivative_contraction_from_pairing,
    pair_partitions,
    riemann_product_contraction_from_pairing,
    two_derivative_contraction_from_pairing,
)
from local_bv.four_dimensional import (
    four_dimensional_schouten_analysis,
    pairing_coordinate_ledger,
    pairing_schouten_relation,
    schouten_endpoint_selections,
)
from local_bv.specialization import (
    TensorOccurrence,
    schouten_antisymmetrization,
)


class FourDimensionalSchoutenTests(unittest.TestCase):
    @staticmethod
    def _occurrence(sector: str, position: int) -> TensorOccurrence:
        if sector == "R3":
            return TensorOccurrence(position // 4, "slots", position % 4)
        if sector == "nablaR_nablaR":
            if position in (0, 5):
                return TensorOccurrence(position // 5, "derivatives", 0)
            factor = 0 if position < 5 else 1
            return TensorOccurrence(factor, "slots", position - 1 - 5 * factor)
        if sector == "R_nabla2R":
            if position < 2:
                return TensorOccurrence(0, "derivatives", position)
            if position < 6:
                return TensorOccurrence(0, "slots", position - 2)
            return TensorOccurrence(1, "slots", position - 6)
        raise ValueError("unknown sector")

    def test_endpoint_selections_are_exhaustive(self) -> None:
        cubic_pairing = tuple((2 * index, 2 * index + 1) for index in range(6))
        derivative_pairing = tuple((2 * index, 2 * index + 1) for index in range(5))
        self.assertEqual(len(schouten_endpoint_selections(cubic_pairing)), 192)
        self.assertEqual(len(schouten_endpoint_selections(derivative_pairing)), 32)

    def test_pairing_antisymmetrizer_matches_signed_coordinates(self) -> None:
        ten_slot_pairings = tuple(pair_partitions(tuple(range(10))))
        cases = (
            (
                "R3",
                tuple(pair_partitions(tuple(range(12)))),
                curvature_product_bianchi_analysis(3)[
                    "pairing_monomial_coordinates"
                ],
                lambda pairing: riemann_product_contraction_from_pairing(
                    pairing, 3
                ),
            ),
            (
                "nablaR_nablaR",
                ten_slot_pairings,
                pairing_coordinate_ledger(
                    ten_slot_pairings, one_derivative_contraction_from_pairing
                ),
                one_derivative_contraction_from_pairing,
            ),
            (
                "R_nabla2R",
                ten_slot_pairings,
                pairing_coordinate_ledger(
                    ten_slot_pairings, two_derivative_contraction_from_pairing
                ),
                two_derivative_contraction_from_pairing,
            ),
        )
        for sector, pairings, coordinates, constructor in cases:
            for pairing in pairings:
                for selection in schouten_endpoint_selections(pairing):
                    fast = pairing_schouten_relation(
                        pairing, selection, coordinates
                    )
                    if not fast:
                        continue
                    direct = schouten_antisymmetrization(
                        constructor(pairing),
                        tuple(self._occurrence(sector, position) for position in selection),
                        dimension=4,
                    )
                    self.assertEqual(fast, direct, sector)
                    self.assertTrue(
                        all(term.is_complete_contraction() for term in fast.terms)
                    )
                    break
                else:
                    continue
                break
            else:
                self.fail(f"no nonzero {sector} Schouten relation was generated")

    def test_cubic_coordinate_ledger_covers_every_rewiring(self) -> None:
        analysis = curvature_product_bianchi_analysis(3)
        coordinates = analysis["pairing_monomial_coordinates"]
        self.assertEqual(len(coordinates), 10_395)
        pairing = min(coordinates)
        for selection in schouten_endpoint_selections(pairing):
            pairing_schouten_relation(pairing, selection, coordinates)

    def test_exact_four_dimensional_specialization_ledger(self) -> None:
        analysis = four_dimensional_schouten_analysis()
        self.assertEqual(analysis["dimension"], 4)
        self.assertEqual(analysis["total_candidate_count"], 3_328)
        self.assertEqual(analysis["total_nonzero_candidate_count"], 2_992)
        self.assertEqual(analysis["unique_nonzero_relation_count"], 72)
        self.assertEqual(analysis["schouten_relation_rank_in_ambient_basis"], 11)
        self.assertEqual(analysis["universal_quotient_dimension"], 10)
        self.assertEqual(analysis["four_dimensional_quotient_dimension"], 8)
        self.assertEqual(analysis["schouten_rank_on_universal_quotient"], 2)
        self.assertEqual(
            analysis["schouten_rank_on_universal_quotient"],
            10 - analysis["four_dimensional_quotient_dimension"],
        )
        self.assertEqual(
            len(analysis["kernel_expressions"]),
            analysis["schouten_rank_on_universal_quotient"],
        )
        self.assertGreater(analysis["unique_nonzero_relation_count"], 0)
        self.assertEqual(
            analysis["tower"].current.parity_block_dimensions["odd"], 0
        )
        self.assertEqual(
            analysis["sector_ranks_after_specialization"],
            {"R3": 6, "nablaR_nablaR": 4, "R_nabla2R": 4},
        )
        expected_sectors = {
            "R3": (13, 2_496, 2_160, 36, 5, 8, 6),
            "nablaR_nablaR": (12, 384, 384, 18, 3, 4, 4),
            "R_nabla2R": (14, 448, 448, 18, 3, 6, 6),
        }
        for name, expected in expected_sectors.items():
            sector = analysis["sector_generation"][name]
            self.assertEqual(
                (
                    sector["basis_dimension"],
                    sector["candidate_count"],
                    sector["nonzero_candidate_count"],
                    sector["unique_nonzero_relation_count"],
                    sector["schouten_relation_rank_in_ambient_sector"],
                    sector["intrinsic_quotient_dimension_before_schouten"],
                    sector["intrinsic_quotient_dimension_after_schouten"],
                ),
                expected,
            )


if __name__ == "__main__":
    unittest.main()
