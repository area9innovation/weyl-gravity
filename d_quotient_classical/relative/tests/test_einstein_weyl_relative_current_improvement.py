"""Fast fail-closed tests for the frozen current improvement."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from bridge.einstein_sector.product_taylor_engine import COORDINATES
from d_quotient_classical.relative import einstein_weyl_relative_current_improvement as producer
from d_quotient_classical.relative.einstein_weyl_relative_lee_wald_pbw import (
    _basis_decomposition,
    _basis_derivative,
)


class RelativeCurrentImprovementTests(unittest.TestCase):
    def test_stored_artifacts_are_strict_and_complete(self) -> None:
        certificate = json.loads(producer.OUTPUT.read_text())
        payload = json.loads(producer.GENERATED.read_text())
        producer.validate(certificate)
        self.assertEqual(payload["term_count"], 2478)
        self.assertEqual(len(payload["terms"]), 2478)

    def test_laurent_basis_is_exactly_differentiated(self) -> None:
        self.assertEqual(_basis_derivative((0, -3)), {(1, -4): -3})
        self.assertEqual(_basis_derivative((1, -2)), {(0, -3): -2, (0, -1): 1})
        self.assertEqual(
            _basis_decomposition(sp.Rational(3, 8) / sp.sin(COORDINATES[2])),
            {(0, -1): sp.Rational(3, 8)},
        )

    def test_downstream_promotions_are_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "cyclic_dual_bv_rows_certified",
            "slice_integral_matches_complete_five_charge_q2",
            "direct_f2_repaired",
            "arity_three_authorized",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
