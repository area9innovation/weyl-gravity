from __future__ import annotations

import copy
import unittest

from anomalies import dressed_canonical_berezinian_locality_preflight as module


class DressedCanonicalBerezinianTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = module.build()

    def _rejects(self, mutator) -> None:
        changed = copy.deepcopy(self.value)
        mutator(changed)
        with self.assertRaises(ValueError):
            module.validate(changed)

    def test_baseline(self) -> None:
        module.validate(self.value)
        self.assertEqual(
            self.value["finite_cutoff_berezinian"]["full_BV_log_J_per_cell"],
            "-40 tau",
        )

    def test_missing_antifield_factor_rejected(self) -> None:
        self._rejects(
            lambda value: value["finite_cutoff_berezinian"].__setitem__(
                "cotangent_factor_count", 1
            )
        )

    def test_wrong_berezinian_exponent_rejected(self) -> None:
        self._rejects(
            lambda value: value["finite_cutoff_berezinian"].__setitem__(
                "full_BV_log_J_per_cell", "-20 tau"
            )
        )

    def test_tau_hat_star_sign_mutation_rejected(self) -> None:
        self._rejects(
            lambda value: value["canonical_cotangent_map"].__setitem__(
                "one_form_defect", "4 g.g_star delta tau"
            )
        )

    def test_unit_jacobian_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["finite_cutoff_berezinian"].__setitem__(
                "is_identically_one", True
            )
        )

    def test_action_independent_locality_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["continuum_disposition"].__setitem__(
                "verdict", "ACTION_INDEPENDENT_CONTINUUM_LOCALITY_CERTIFIED"
            )
        )

    def test_qap_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["claim_flags"].__setitem__(
                "QAP_ESTABLISHED", True
            )
        )


if __name__ == "__main__":
    unittest.main()
