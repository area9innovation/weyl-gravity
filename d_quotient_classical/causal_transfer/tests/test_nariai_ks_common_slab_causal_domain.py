from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.nariai_ks_common_slab_causal_domain import build, validate
from d_quotient_classical.causal_transfer.verify_nariai_ks_common_slab_causal_domain import verify


class NariaiKSCommonSlabCausalDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_quantifiers_and_common_cone(self) -> None:
        self.assertIn("for every T>0", self.value["theorem"]["quantifiers"])
        self.assertTrue(self.value["analytic_interface"]["common_reference_causal_cone"])
        self.assertEqual(self.value["proof"]["regularized_ode"]["einstein_equation_after_substitution"], "0")

    def test_downstream_gates_fail_closed(self) -> None:
        for flag in (
            "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
            "KS_METRIC_ENDPOINT_TYPED_BIWAVE",
            "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
            "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
            "HADAMARD_STATE",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
