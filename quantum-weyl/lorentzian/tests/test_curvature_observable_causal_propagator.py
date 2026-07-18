from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.curvature_observable_causal_propagator import validate
from lorentzian.curvature_observable_causal_propagator_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_curvature_observable_causal_propagator import verify


class CurvatureObservableCausalPropagatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/curvature-observable-causal-propagator-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_transport_formula_and_support(self) -> None:
        propagator = self.certificate["transported_propagator"]
        self.assertEqual(
            propagator["definition"], "Delta_C^obs=R_C Delta_Lambda J_C"
        )
        self.assertIn("J(supp f)", propagator["causal_support"])
        self.assertEqual(
            propagator["status"], "CONSTRUCTED_AS_EXACT_SUPPORT_LOCAL_TRANSPORT"
        )

    def test_gauge_invariance_and_ccr_match(self) -> None:
        self.assertEqual(
            self.certificate["curvature_map"]["gauge_identity"],
            "T_state K_aux=0",
        )
        self.assertEqual(self.certificate["CCR_comparison"]["status"], "EXACT")
        self.assertTrue(
            all(self.certificate["transport_identity_replay"]["checks"].values())
        )
        replay = self.certificate["transport_identity_replay"]
        self.assertEqual(replay["formal_adjoint_word"], replay["propagator_word"])
        self.assertEqual(replay["formal_adjoint_sign"], -1)
        self.assertEqual(replay["graded_skew_defect"], 0)

    def test_autonomous_green_and_state_remain_open(self) -> None:
        boundary = self.certificate["analytic_boundary"]
        self.assertEqual(
            boundary["transported_curvature_observable_causal_propagator"],
            "CONSTRUCTED",
        )
        self.assertEqual(
            boundary["autonomous_curvature_advanced_retarded_Green_operators"],
            "NOT_CONSTRUCTED",
        )
        self.assertEqual(boundary["Hadamard_two_point_function"], "NOT_CONSTRUCTED")

    def test_overclaims_fail_closed(self) -> None:
        for flag in (
            "AUTONOMOUS_CURVATURE_GREEN_OPERATORS_CONSTRUCTED",
            "CURVATURE_PROPAGATOR_WAVEFRONT_SET_CERTIFIED",
            "CURVATURE_HADAMARD_STATE_CONSTRUCTED",
            "LORENTZIAN_QME_RESTORED",
        ):
            mutant = deepcopy(self.certificate)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "over-promoted"):
                validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
