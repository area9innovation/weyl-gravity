from __future__ import annotations

from fractions import Fraction
import importlib.util
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = TRANSFER_ROOT / "local_expression_ast.py"
SPEC = importlib.util.spec_from_file_location("local_expression_ast", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
AST = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AST
SPEC.loader.exec_module(AST)


def _monomial(operator_id: str = "Bach") -> dict[str, object]:
    return {
        "operator_id": operator_id,
        "input_jets": [[1, 0, 0, 0], [0, 1, 0, 0]],
        "free_indices": ["mu", "nu"],
        "contractions": [["b", "a"], ["d", "c"]],
    }


class LocalExpressionAstTests(unittest.TestCase):
    def test_duplicate_terms_combine_and_contractions_canonicalize(self) -> None:
        expression = AST.LocalExpression.from_payload(
            {
                "terms": [
                    {"coefficient": {"numerator": 1, "denominator": 2}, "monomial": _monomial()},
                    {"coefficient": {"numerator": 1, "denominator": 3}, "monomial": _monomial()},
                ]
            },
            arity=2,
            spacetime_dimension=4,
        )
        self.assertEqual(len(expression.terms), 1)
        monomial, coefficient = expression.terms[0]
        self.assertEqual(coefficient, Fraction(5, 6))
        self.assertEqual(monomial.contractions, (("a", "b"), ("c", "d")))
        self.assertEqual(expression.to_payload()["terms"][0]["coefficient"], {"numerator": 5, "denominator": 6})

    def test_exact_cancellation_produces_canonical_zero(self) -> None:
        expression = AST.LocalExpression.from_payload(
            {
                "terms": [
                    {"coefficient": 1, "monomial": _monomial()},
                    {"coefficient": -1, "monomial": _monomial()},
                ]
            },
            arity=2,
            spacetime_dimension=4,
        )
        self.assertEqual(expression, AST.LocalExpression.zero())
        self.assertEqual(expression.to_payload(), {"terms": []})

    def test_addition_handles_zero_without_guessing_arity_or_dimension(self) -> None:
        expression = AST.LocalExpression.from_payload(
            {"terms": [{"coefficient": 1, "monomial": _monomial()}]},
            arity=2,
            spacetime_dimension=4,
        )
        self.assertEqual(AST.LocalExpression.zero().added(expression), expression)
        self.assertEqual(expression.added(expression.scaled(-1)), AST.LocalExpression.zero())

    def test_floating_point_and_bad_jet_multiindex_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact"):
            AST.LocalExpression.from_payload(
                {"terms": [{"coefficient": 0.5, "monomial": _monomial()}]},
                arity=2,
                spacetime_dimension=4,
            )
        malformed = _monomial()
        malformed["input_jets"] = [[1, 0], [0, 1]]
        with self.assertRaisesRegex(ValueError, "jet multi-index"):
            AST.LocalExpression.from_payload(
                {"terms": [{"coefficient": 1, "monomial": malformed}]},
                arity=2,
                spacetime_dimension=4,
            )


if __name__ == "__main__":
    unittest.main()
