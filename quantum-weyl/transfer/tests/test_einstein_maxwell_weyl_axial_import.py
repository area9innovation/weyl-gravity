from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "einstein_maxwell_weyl_axial_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("einstein_maxwell_weyl_axial_import_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORTER = sys.modules[CERT.build_import.__module__]


class EinsteinMaxwellWeylAxialImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.operator = IMPORTER._git_json(IMPORTER.OPERATOR_CERTIFICATE)
        cls.green = IMPORTER._git_json(IMPORTER.GREEN_CERTIFICATE)
        cls.pairing = IMPORTER._git_json(IMPORTER.PAIRING_CERTIFICATE)
        cls.Lee_Wald = IMPORTER._git_json(IMPORTER.LEE_WALD_CERTIFICATE)
        cls.Lee_Wald_fixture = IMPORTER._git_json(IMPORTER.LEE_WALD_FIXTURE)
        cls.schemas = {
            "operator": IMPORTER._git_json(IMPORTER.OPERATOR_SCHEMA),
            "green": IMPORTER._git_json(IMPORTER.GREEN_SCHEMA),
            "pairing": IMPORTER._git_json(IMPORTER.PAIRING_SCHEMA),
            "Lee_Wald": IMPORTER._git_json(IMPORTER.LEE_WALD_SCHEMA),
            "Lee_Wald_fixture": IMPORTER._git_json(IMPORTER.LEE_WALD_FIXTURE_SCHEMA),
        }
        cls.registration = IMPORTER._git_json(IMPORTER.REGISTRATION)

    def validate(self, *, operator=None, green=None, pairing=None, Lee_Wald=None, registration=None):
        return IMPORTER.validate_bridge_payloads(
            operator or self.operator,
            green or self.green,
            pairing or self.pairing,
            Lee_Wald or self.Lee_Wald,
            self.Lee_Wald_fixture,
            self.schemas,
            registration or self.registration,
        )

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), CERT.build_certificate())

    def test_linearized_light_gravity_boundary(self) -> None:
        result = CERT.build_certificate()
        self.assertTrue(result["physical_interpretation"]["linearized_coupled_metric_Maxwell_branch_available"])
        self.assertFalse(result["physical_interpretation"]["interacting_light_model_available"])
        self.assertEqual(result["reduced_pairing_verdict"]["signature"], [2, 0])
        self.assertTrue(result["reduced_pairing_verdict"]["nonradical"])
        self.assertTrue(result["physical_interpretation"]["direct_compact_Lee_Wald_pairing_available"])
        self.assertEqual(result["direct_Lee_Wald_verdict"]["complete_generic_axial_target_signature"], [3, 1])
        self.assertFalse(result["claim_flags"]["PHYSICAL_PARTICLE_OR_GHOST_CLASSIFICATION"])

    def test_green_current_mutation_is_rejected(self) -> None:
        forged = deepcopy(self.green)
        forged["reduced_current"]["time_current_terms"][0]["coefficient"] += "+1"
        with self.assertRaisesRegex(ValueError, "Green identity replay"):
            self.validate(green=forged)

    def test_pairing_and_scope_mutations_are_rejected(self) -> None:
        forged = deepcopy(self.pairing)
        forged["pairing"]["determinant"] = "0"
        with self.assertRaisesRegex(ValueError, "pairing determinant"):
            self.validate(pairing=forged)

        forged = deepcopy(self.pairing)
        forged["classification"]["physical_norm_or_ghost_claim"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            self.validate(pairing=forged)

    def test_registration_mutation_is_rejected(self) -> None:
        forged = deepcopy(self.registration)
        forged["evidence"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "registration"):
            self.validate(registration=forged)

    def test_Lee_Wald_promotion_and_scope_mutations_are_rejected(self) -> None:
        forged = deepcopy(self.Lee_Wald)
        forged["full_solution_pairing"]["complete_generic_axial_target_signature"] = [4, 0]
        with self.assertRaisesRegex(ValueError, "Lee--Wald claim boundary"):
            self.validate(Lee_Wald=forged)

        forged = deepcopy(self.Lee_Wald)
        forged["classification"]["quantum_ghost_or_unitarity_claim"] = True
        with self.assertRaisesRegex(ValueError, "Lee--Wald claim boundary"):
            self.validate(Lee_Wald=forged)


if __name__ == "__main__":
    unittest.main()
