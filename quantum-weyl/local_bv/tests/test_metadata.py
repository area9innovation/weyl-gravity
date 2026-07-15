from fractions import Fraction
import unittest

from local_bv import LocalJetAlgebra, minimal_registry


class MetadataTests(unittest.TestCase):
    def test_minimal_registry_carries_all_required_gradings(self) -> None:
        registry = minimal_registry()
        self.assertEqual(set(registry), {"g", "xi", "omega"})
        for spec in registry.values():
            payload = spec.canonical_payload()
            self.assertEqual(
                set(payload),
                {
                    "name",
                    "index_variance",
                    "symmetric_index_pairs",
                    "ghost_number",
                    "antifield_number",
                    "form_degree",
                    "mass_dimension",
                    "grassmann_parity",
                    "spacetime_parity",
                    "weyl_weight",
                    "provenance",
                },
            )
            self.assertNotIsInstance(spec.mass_dimension, float)
            self.assertNotIsInstance(spec.weyl_weight, float)

    def test_jet_metadata_is_exact_and_metric_indices_are_canonical(self) -> None:
        algebra = LocalJetAlgebra(4)
        left = algebra.jet("g", (3, 1), (1, 0, 2, 0))
        right = algebra.jet("g", (1, 3), (1, 0, 2, 0))
        self.assertEqual(left, right)
        self.assertEqual(left.mass_dimension, Fraction(3))
        self.assertEqual(left.weyl_weight, Fraction(2))

    def test_invalid_components_and_multi_indices_fail_closed(self) -> None:
        algebra = LocalJetAlgebra(4)
        with self.assertRaises(ValueError):
            algebra.jet("xi", ())
        with self.assertRaises(ValueError):
            algebra.jet("g", (0, 4))
        with self.assertRaises(ValueError):
            algebra.jet("omega", derivatives=(0, -1, 0, 0))


if __name__ == "__main__":
    unittest.main()
