from __future__ import annotations

import json
from pathlib import Path
import unittest

import jsonschema
import sympy as sp

from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    PAIRS,
    _volume_density_ratio,
)


ROOT = Path(__file__).resolve().parents[3]


class BergerSupportLocalQ2Test(unittest.TestCase):
    def test_volume_density_first_and_second_variations(self) -> None:
        volume = _volume_density_ratio()
        variables = sp.symbols("x0:10")
        metric = sp.diag(-1, 1, 1, 1)
        for pair, variable in zip(PAIRS, variables, strict=True):
            first, second = pair
            metric[first, second] += variable
            if first != second:
                metric[second, first] += variable
        exact = sp.sqrt(-metric.det())
        zero = {variable: 0 for variable in variables}
        linear = {
            component: coefficient
            for component, word, coefficient in volume.linear.terms
            if not word
        }
        bilinear = {
            (left, right): coefficient
            for left, left_word, right, right_word, coefficient in volume.bilinear.terms
            if not left_word and not right_word
        }
        for left, variable in enumerate(variables):
            self.assertEqual(
                sp.simplify(linear.get(left, 0) - sp.diff(exact, variable).subs(zero)),
                0,
            )
            for right, other in enumerate(variables):
                self.assertEqual(
                    sp.simplify(
                        bilinear.get((left, right), 0)
                        - sp.diff(exact, variable, other).subs(zero)
                    ),
                    0,
                )

    def test_draft_2020_12_schemas_validate_frozen_artifacts(self) -> None:
        pairs = (
            (
                "d_quotient_classical/schema/berger-support-local-q2-v1.schema.json",
                "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
            ),
            (
                "d_quotient_classical/schema/berger-support-local-q2-payload-v1.schema.json",
                "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json",
            ),
        )
        for schema_path, artifact_path in pairs:
            schema = json.loads((ROOT / schema_path).read_text())
            artifact = json.loads((ROOT / artifact_path).read_text())
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(artifact)


if __name__ == "__main__":
    unittest.main()
