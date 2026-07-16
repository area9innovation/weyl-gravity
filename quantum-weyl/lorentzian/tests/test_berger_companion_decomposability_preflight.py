from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_companion_decomposability_preflight import (
    null_symbol_replay,
    validate,
)
from lorentzian.berger_companion_decomposability_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_companion_decomposability_preflight import verify


class BergerCompanionDecomposabilityPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-companion-decomposability-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_null_symbol_is_nonzero_square_zero(self) -> None:
        replay = null_symbol_replay(7)
        self.assertEqual(replay["canonical_representative_rank"], 7)
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(replay["minimal_polynomial_on_null_fixture"], "lambda^2")

    def test_characteristic_set_does_not_promote_wavefront_set(self) -> None:
        self.assertEqual(
            self.certificate["principal_symbol_analysis"]["characteristic_set"],
            "Char(C20)={q=0}=metric null cone",
        )
        self.assertEqual(
            self.certificate["pauli_jordan_input"]["kernel_wavefront_set"],
            "NOT_COMPUTED",
        )

    def test_fewster_target_is_exact(self) -> None:
        target = self.certificate["decomposability_target"]
        self.assertEqual(
            target["required_kernel_inclusion"],
            "WF(E_C) subset (N_plus x N_minus) union (N_minus x N_plus)",
        )
        self.assertIn("does not change", target["causal_sign_convention_note"])

    def test_minimal_missing_carrier_is_named(self) -> None:
        missing = self.certificate["minimal_missing_carrier"]
        self.assertEqual(
            missing["result_id"],
            "BERGER_COMPANION_PAULI_JORDAN_WAVEFRONT_THEOREM",
        )
        self.assertIn("WF(E_C)", missing["statement"])

    def test_decomposability_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
