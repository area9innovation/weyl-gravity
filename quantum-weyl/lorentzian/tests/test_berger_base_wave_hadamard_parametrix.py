from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_base_wave_hadamard_parametrix import validate
from lorentzian.berger_base_wave_hadamard_parametrix_certificate import (
    HERE, OUTPUT, build_certificate,
)
from lorentzian.verify_berger_base_wave_hadamard_parametrix import (
    mutation_guards, verify_certificate,
)


class BergerBaseWaveHadamardParametrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.artifacts = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-base-wave-hadamard-parametrix-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_operator_inventory_is_complete(self) -> None:
        inventory = self.artifacts["operator_inventory"]
        self.assertEqual(
            [row["operator_id"] for row in inventory["operators"]],
            ["Box_2", "Box_1", "F_spatial K_spatial"],
        )
        self.assertEqual([row["rank"] for row in inventory["operators"]], [10, 3, 3])

    def test_parametrix_is_not_a_state(self) -> None:
        scope = self.certificate["scope_boundary"]
        self.assertTrue(scope["local_parametrix"])
        self.assertFalse(scope["global_exact_bisolution"])
        self.assertFalse(scope["quasifree_state"])
        self.assertFalse(scope["positivity_or_Krein_completion"])
        self.assertEqual(
            set(self.certificate["global_completion_obligations"].values()),
            {"OPEN"},
        )

    def test_smooth_commutator_remainder_is_not_called_a_bisolution(self) -> None:
        statement = self.certificate["parametrix_theorem"]["commutator"]
        self.assertIn("smooth local kernel", statement)
        self.assertNotIn("smooth local bisolution", statement)

    def test_adjoint_is_typed_against_p_sharp(self) -> None:
        micro = self.artifacts["microlocal_spectrum"]
        self.assertIn("P^sharp", micro["adjoint_reversal"])
        self.assertNotIn("P=P^sharp", micro["adjoint_reversal"])

    def test_flat_space_fixture_fixes_i0_C_plus_and_CCR_signs(self) -> None:
        flat = self.artifacts["flat_space_normalization"]
        self.assertEqual(flat["signature"], "(-,+,+,+)")
        self.assertIn("E=G_ret-G_adv", flat["green_convention"])
        self.assertIn("k=(-|p|,p)", flat["positive_frequency_covector"])
        self.assertTrue(all(flat["exact_sign_checks"].values()))
        self.assertTrue(
            self.certificate["verified_checks"][
                "flat_space_i0_C_plus_and_CCR_normalization"
            ]
        )

    def test_analytic_artifacts_are_ledgers_not_self_declared_proofs(self) -> None:
        records = self.certificate["theorem_instantiation_artifacts"]
        self.assertEqual(
            records["flat_space_normalization"]["artifact_type"],
            "JSON_FLAT_NORMALIZATION_WITNESS",
        )
        self.assertEqual(
            {
                record["artifact_type"]
                for name, record in records.items()
                if name != "flat_space_normalization"
            },
            {"JSON_THEOREM_INSTANTIATION_LEDGER"},
        )

    def test_independent_verifier_and_guards(self) -> None:
        self.assertEqual(verify_certificate(), self.certificate)
        mutation_guards(self.certificate)

    def test_global_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["scope_boundary"]["global_exact_bisolution"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
