import unittest

from local_bv.curvature import (
    RIEMANN,
    contraction_from_pairing,
    pair_partitions,
    riemann_product_contraction_from_pairing,
)
from local_bv.pairing_orbits import (
    identical_factor_group,
    signed_pairing_orbits,
)
from local_bv.tensors import CANONICALIZATION_CACHE_MAXSIZE, TensorMonomial


class PairingOrbitTests(unittest.TestCase):
    def test_canonicalization_cache_is_bounded(self) -> None:
        self.assertEqual(CANONICALIZATION_CACHE_MAXSIZE, 65_536)
        self.assertEqual(
            TensorMonomial.canonicalize.cache_parameters()["maxsize"],
            CANONICALIZATION_CACHE_MAXSIZE,
        )

    def test_quadratic_orbits_reproduce_monomial_canonicalization(self) -> None:
        pairings = tuple(pair_partitions(tuple(range(8))))
        actions = identical_factor_group(RIEMANN, 2)
        orbits = signed_pairing_orbits(pairings, actions)
        self.assertEqual(len(actions), 128)
        self.assertEqual(sum(orbit.size for orbit in orbits), 105)
        self.assertEqual(sum(not orbit.vanishes for orbit in orbits), 4)

        for orbit in orbits:
            expected_sign, expected = contraction_from_pairing(
                orbit.canonical_pairing
            ).canonicalize()
            with self.subTest(pairing=orbit.canonical_pairing):
                self.assertEqual(bool(expected_sign), not orbit.vanishes)
                if not orbit.vanishes:
                    self.assertIsNotNone(expected)
                    for pairing, sign in zip(
                        orbit.members, orbit.signs_to_canonical
                    ):
                        actual_sign, actual = contraction_from_pairing(
                            pairing
                        ).canonicalize()
                        self.assertEqual(actual, expected)
                        self.assertEqual(actual_sign, sign * expected_sign)

    def test_cubic_orbits_cover_all_pairings_without_raw_canonicalization(self) -> None:
        pairings = tuple(pair_partitions(tuple(range(12))))
        actions = identical_factor_group(RIEMANN, 3)
        orbits = signed_pairing_orbits(pairings, actions)
        self.assertEqual(len(pairings), 10395)
        self.assertEqual(len(actions), 3072)
        self.assertEqual(sum(orbit.size for orbit in orbits), len(pairings))
        self.assertEqual(
            len({pairing for orbit in orbits for pairing in orbit.members}),
            len(pairings),
        )
        self.assertTrue(any(orbit.vanishes for orbit in orbits))
        self.assertTrue(any(not orbit.vanishes for orbit in orbits))
        for orbit in orbits:
            sign, canonical = riemann_product_contraction_from_pairing(
                orbit.canonical_pairing, 3
            ).canonicalize()
            with self.subTest(pairing=orbit.canonical_pairing):
                self.assertEqual(bool(sign), not orbit.vanishes)
                self.assertEqual(canonical is not None, not orbit.vanishes)


if __name__ == "__main__":
    unittest.main()
