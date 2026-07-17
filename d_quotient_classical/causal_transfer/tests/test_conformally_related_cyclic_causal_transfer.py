from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.conformally_related_cyclic_causal_transfer import (
    build,
    validate,
)
from d_quotient_classical.causal_transfer.verify_conformally_related_cyclic_causal_transfer import (
    verify,
)


class ConformallyRelatedCyclicCausalTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_G3_open_class_and_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())
        self.assertTrue(self.value["flags"]["G3_OPEN_BACKGROUND_CLASS"])

    def test_affine_ghost_and_cotangent_shear(self) -> None:
        rows = self.value["finite_BV_canonical_map"]["minimal_rows"]
        self.assertEqual(rows["omega"], "omega_phi=omega-xi(phi)")
        self.assertEqual(rows["xi_star"], "xi_star_phi=xi_star+d(phi) omega_star")
        self.assertTrue(self.value["exact_checks"]["BV_pairing_preserved"])

    def test_nonconstant_global_consumer(self) -> None:
        consumer = self.value["nonconstant_consumer"]
        self.assertTrue(consumer["nonconstant"])
        self.assertTrue(consumer["all_derivatives_bounded"])
        self.assertTrue(consumer["same_causal_cones"])

    def test_scope_mutations_fail(self) -> None:
        for flag in (
            "ALL_LOCALLY_CONFORMALLY_FLAT_TOPOLOGIES",
            "FIXED_UNTRANSFORMED_GAUGE_FERMION",
            "TIMELIKE_BOUNDARY_VERSION",
            "HADAMARD_TRANSFER",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)

    def test_affine_term_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["exact_checks"]["affine_Weyl_ghost_term_included"] = False
        with self.assertRaisesRegex(ValueError, "check dropped"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
