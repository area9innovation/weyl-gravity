"""Falsification tests for BT eight-point Krein charge localization."""
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_eight_point_krein_charge_localization.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_eight_point_krein_charge_localization.py"
)


class EightPointKreinChargeLocalizationTests(unittest.TestCase):
    def command(self, argv):
        return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)

    def mutate(self, mutation):
        with open(CERT, encoding="utf-8") as handle:
            value = json.load(handle)
        mutation(value)
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle)
            handle.flush()
            return self.command([sys.executable, VERIFIER, "--verify", handle.name])

    def test_producer_fast_check(self):
        self.assertEqual(
            self.command([sys.executable, PRODUCER, "--fast-check"]).returncode, 0
        )

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_rho_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["charge_fibre"]["rho"].update(numerator=820)
            ).returncode,
            0,
        )

    def test_gram_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["charge_fibre"]["gram"][1].__setitem__(1, "-3")
            ).returncode,
            0,
        )

    def test_null_basis_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["charge_fibre"]["null_charge_basis_S"][1]
                .__setitem__(1, "-1")
            ).returncode,
            0,
        )

    def test_charge_generator_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["charge_fibre"]["transported_charge_generator"][0]
                .__setitem__(1, "1")
            ).returncode,
            0,
        )

    def test_positive_projector_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["charge_fibre"]["positive_projector"][0]
                .__setitem__(1, "0")
            ).returncode,
            0,
        )

    def test_positive_component_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_negative_line"]["positive_component"][0]
                .__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_negative_component_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_negative_line"]["negative_component"][0]
                .__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_one_sided_pairing_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_negative_line"][
                    "negative_self_pairing"
                ].update(numerator=-1)
            ).returncode,
            0,
        )

    def test_cross_pairing_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_negative_line"][
                    "positive_negative_pairing"
                ].update(numerator=-2)
            ).returncode,
            0,
        )

    def test_full_pairing_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["canonical_negative_line"]["full_pairing"].update(
                    numerator=-1
                )
            ).returncode,
            0,
        )

    def test_positive_block_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_charge_decomposition"][
                    "positive_charge_block"
                ][0].__setitem__(0, "0")
            ).returncode,
            0,
        )

    def test_negative_pullback_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_charge_decomposition"][
                    "negative_self_pullback"
                ][0].__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_cross_pullback_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["profile_charge_decomposition"][
                    "positive_negative_pullback"
                ][0].__setitem__(0, "-1")
            ).returncode,
            0,
        )

    def test_Q_identification_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["Eq19_boundary"].update(
                    Q_remainder_identification="IDENTIFIED"
                )
            ).returncode,
            0,
        )

    def test_neutral_operator_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(
                    neutral_higher_composite_operator="CONSTRUCTED"
                )
            ).returncode,
            0,
        )

    def test_eq19_promotion_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["disposition"].update(Eq19_all_orders="PROVED")
            ).returncode,
            0,
        )

    def test_scope_boundary_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(lambda value: value.update(does_not_establish=[])).returncode,
            0,
        )

    def test_input_hash_mutation_rejected(self):
        self.assertNotEqual(
            self.mutate(
                lambda value: value["provenance"]["inputs"][0].update(
                    sha256="0" * 64
                )
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
