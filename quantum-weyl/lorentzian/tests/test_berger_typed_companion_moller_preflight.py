from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_typed_companion_moller_preflight import (
    triangular_replay,
    validate,
)
from lorentzian.berger_typed_companion_moller_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_typed_companion_moller_preflight import verify


class BergerTypedCompanionMollerPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-typed-companion-moller-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_noncommutative_triangular_replay(self) -> None:
        replay = triangular_replay()
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(replay["intertwiners"], ["C M_sol^pm=B", "M_src^pm C=B"])

    def test_source_and_solution_maps_remain_distinct(self) -> None:
        typed = self.certificate["typed_transport"]
        self.assertIn("X_B,s(I)->X_C,s(I)", typed["full_solution_map"])
        self.assertIn("Y_C,s(I)->Y_B,s(I)", typed["full_source_map"])
        self.assertNotEqual(typed["full_solution_map"], typed["full_source_map"])

    def test_adjoint_reverses_retarded_to_advanced(self) -> None:
        identity = self.certificate["typed_transport"]["adjoint_reversal"]
        self.assertIn("retarded", identity)
        self.assertIn("advanced", identity)
        self.assertIn("Csharp", identity)

    def test_kernel_transport_remains_formal(self) -> None:
        candidate = self.certificate["formal_kernel_candidate"]
        self.assertEqual(
            candidate["status"],
            "FORMAL_UNTIL_DISTRIBUTIONAL_COMPOSITION_IS_CERTIFIED",
        )
        self.assertEqual(set(self.certificate["microlocal_obligations"].values()), {"OPEN"})

    def test_order_two_transport_does_not_inherit_smooth_potential_theorem(self) -> None:
        diagnosis = self.certificate["microlocal_diagnosis"]
        self.assertEqual(diagnosis["maximum_order_V2"], 2)
        self.assertFalse(
            diagnosis["all_Sobolev_Volterra_convergence_is_wavefront_control"]
        )
        self.assertFalse(diagnosis["smooth_potential_Moller_theorem_applies_directly"])

    def test_distributional_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
