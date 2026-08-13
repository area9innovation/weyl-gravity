"""Falsification tests for the localized affine hidden-parity orbit theorem."""
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
    "REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_localized_affine_hidden_parity_orbit.py")
VERIFIER = os.path.join(ROOT, "reverse_physics/verify_bt_localized_affine_hidden_parity_orbit.py")


class LocalizedAffineHiddenParityOrbitTests(unittest.TestCase):
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

    def test_producer_check(self):
        self.assertEqual(self.command([sys.executable, PRODUCER, "--check"]).returncode, 0)

    def test_independent_verifier(self):
        self.assertEqual(self.command([sys.executable, VERIFIER]).returncode, 0)

    def test_localized_identity_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["exact_localized_identity"].update(identity="F(h(phi))=F(phi) off shell")).returncode, 0)

    def test_second_iterate_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["exact_localized_identity"].update(second_iterate="h^2(phi)=phi off shell")).returncode, 0)

    def test_affine_field_strength_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["affine_background_orbit"].update(field_strength="0")).returncode, 0)

    def test_affine_orbit_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["affine_background_orbit"].update(orbit=["(v,c)"])).returncode, 0)

    def test_one_sheet_promotion_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["affine_background_orbit"].update(conclusion="ONE_SHEET_PARITY_FIXED")).returncode, 0)

    def test_linearized_equation_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["linearized_on_shell_intertwiner"].update(linearized_equation="E=0")).returncode, 0)

    def test_parity_tangent_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["linearized_on_shell_intertwiner"].update(parity_tangent="T_v=-1")).returncode, 0)

    def test_fourier_fixture_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["zero_background_limit"]["exact_fourier_fixtures"][2].update(offshell_modulus_squared={"numerator": 0, "denominator": 1})).returncode, 0)

    def test_packet_limit_promotion_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["zero_background_limit"].update(packet_conclusion="STRONG_LIMIT_EXISTS")).returncode, 0)

    def test_Jordan_fixture_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["zero_background_limit"]["Jordan_fixture"]["rows"][3].update(frobenius_norm_squared={"numerator": 2, "denominator": 1})).returncode, 0)

    def test_Jordan_limit_promotion_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["zero_background_limit"]["Jordan_fixture"].update(conclusion="LIMIT_EXISTS")).returncode, 0)

    def test_new_field_mutation_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["Eq19_and_physical_disposition"].update(second_sheet_status="NEW_PHYSICAL_FIELD")).returncode, 0)

    def test_offshell_projector_promotion_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["Eq19_and_physical_disposition"].update(off_shell_projector_identity="PROVED")).returncode, 0)

    def test_q10_transfer_promotion_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["Eq19_and_physical_disposition"].update(standard_projector_q10_comparison="PROVED_EQUAL")).returncode, 0)

    def test_full_Eq19_promotion_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value["Eq19_and_physical_disposition"].update(full_public_Eq19="PROVED")).returncode, 0)

    def test_boundary_removal_rejected(self):
        self.assertNotEqual(self.mutate(lambda value: value.update(does_not_establish=[])).returncode, 0)

    def test_hash_mutation_rejected(self):
        def mutation(value):
            path = next(iter(value["provenance"]["input_hashes"]))
            value["provenance"]["input_hashes"][path] = "0" * 64

        self.assertNotEqual(self.mutate(mutation).returncode, 0)


if __name__ == "__main__":
    unittest.main()
