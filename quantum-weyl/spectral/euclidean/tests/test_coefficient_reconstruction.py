from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(REPOSITORY_ROOT / "quantum-weyl") not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT / "quantum-weyl"))

from local_bv.schema_validation import validate_instance

CERT_PATH = ROOT / "coefficient_certificate.py"
SPEC = importlib.util.spec_from_file_location("euclidean_coefficient_certificate_test", CERT_PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
CALC = sys.modules[CERT.exact_payload.__module__]


class WeylGravitonCoefficientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(CERT.SCHEMA.read_text())

    def test_spin_two_coefficients_from_two_backgrounds(self) -> None:
        anomaly = CALC.spin_two_anomaly()
        self.assertEqual(anomaly.a, Fraction(87, 20))
        self.assertEqual(anomaly.beta1, Fraction(137, 60))
        self.assertEqual(anomaly.c, Fraction(199, 30))
        self.assertEqual(anomaly.beta2, Fraction(199, 15))
        self.assertEqual(anomaly.c - anomaly.a, anomaly.beta1)
        self.assertEqual(CALC.chs_c_conical_sphere(2), anomaly.c)

    def test_factorized_constant_curvature_sum(self) -> None:
        ledger = CALC.spin_two_factor_ledger()
        signed = sum(Fraction(row["signed_a_contribution"]) for row in ledger)
        self.assertEqual(signed, Fraction(87, 20))
        self.assertEqual(CALC.chs_a_factorized(2), CALC.chs_a_closed_form(2))

    def test_ricci_flat_determinant_combination(self) -> None:
        expected = (
            2 * CALC.ricci_flat_operator_beta1(2)
            - 3 * CALC.ricci_flat_operator_beta1(1)
        )
        self.assertEqual(expected, Fraction(137, 60))

    def test_exact_D_reducibilities(self) -> None:
        cylinder = CALC.cylinder_d_reducibility()
        minkowski = CALC.minkowski_d_reducibility()
        cylinder.verify()
        minkowski.verify()
        self.assertEqual(cylinder.sigma, 0)
        self.assertEqual(cylinder.divergence, 0)
        self.assertEqual(minkowski.sigma, -1)
        self.assertEqual(minkowski.divergence, 4)

    def test_D_pullbacks_and_lower_towers(self) -> None:
        cylinder = CALC.d_pullback(CALC.cylinder_d_reducibility())
        minkowski = CALC.d_pullback(CALC.minkowski_d_reducibility())
        self.assertEqual(cylinder["top_anomaly_status"], "ZERO")
        self.assertEqual(cylinder["top_anomaly_coordinates"], {"C2": "0", "E4": "0"})
        self.assertEqual(
            minkowski["top_anomaly_coordinates"],
            {"C2": "-199/30", "E4": "87/20"},
        )
        for frame in (cylinder, minkowski):
            self.assertEqual(frame["intrinsic_type_A_lower_descent"], "ZERO_FOR_CONSTANT_SIGMA_D")
            self.assertTrue(
                all(row["D_restricted_status"] == "ZERO_BY_cD_SQUARED" for row in frame["universal_diff_lower_descent"])
            )

    def test_certificate_reproduces_and_validates(self) -> None:
        built = CERT.build_certificate()
        self.assertEqual(validate_instance(built, self.schema), [])
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), built)

    def test_claim_boundary_is_fail_closed(self) -> None:
        flags = CERT.build_certificate()["claim_flags"]
        self.assertTrue(flags["STANDARD_BACKGROUND_A_AND_C_COMPUTED"])
        self.assertTrue(flags["FULL_GAUGE_FIXED_BV_ANOMALY_BASIS_AVAILABLE"])
        self.assertTrue(flags["CYLINDER_D_LOCAL_ANOMALY_PULLBACK_ZERO"])
        for key in (
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
            "D_CARTAN_ANOMALY_CLASSIFIED",
            "QME_RESTORED",
            "RESIDUAL_TRANSFERRED",
            "LORENTZIAN_CERTIFIED",
        ):
            self.assertFalse(flags[key])

    def test_schema_rejects_illegal_promotions(self) -> None:
        forged = deepcopy(CERT.build_certificate())
        forged["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(validate_instance(forged, self.schema))

        forged = deepcopy(CERT.build_certificate())
        forged["D_descent"]["cartan_defect_status"] = "ZERO"
        self.assertTrue(validate_instance(forged, self.schema))


if __name__ == "__main__":
    unittest.main()
