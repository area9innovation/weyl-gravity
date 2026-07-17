from __future__ import annotations

import json
import unittest

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    _action_operator,
    _equation_map,
    _generic_operator,
)
from bridge.einstein_sector.einstein_maxwell_polar_master_complex import _matrix as _source_matrix
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_full_tensor import verify_certificate as verify_independently


class PolarFullTensorTests(unittest.TestCase):
    def test_action_operator_and_chain_square(self) -> None:
        tensor, (eigenvalue, momentum, frequency) = _generic_operator()
        action, field_map, equation_map, _ = _equation_map()
        source, _ = _source_matrix()
        self.assertEqual(
            (action - sp.diag(-1, 2, -1, 2 * eigenvalue) * tensor[[0, 1, 2, 7], :]).applyfunc(sp.factor),
            sp.zeros(4),
        )
        self.assertEqual(
            (action - action.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T).applyfunc(sp.factor),
            sp.zeros(4),
        )
        self.assertEqual((action * field_map - equation_map * source).applyfunc(sp.factor), sp.zeros(4, 5))
        self.assertTrue(all(sp.denom(value).is_number for value in equation_map))

    def test_characteristic(self) -> None:
        action, (eigenvalue, momentum, frequency) = _action_operator()
        extra = frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3)
        einstein = (frequency**2 - momentum**2) ** 2 - 2 * eigenvalue * (frequency**2 - momentum**2) + eigenvalue * (eigenvalue - 2)
        expected = sp.Rational(9, 16) * eigenvalue**3 * (eigenvalue - 2) * extra**2 * einstein
        self.assertEqual(sp.factor(action.det()), sp.factor(expected))

    def test_schema_and_independent_verifier(self) -> None:
        payload = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(payload)
        verify_independently()


if __name__ == "__main__":
    unittest.main()
