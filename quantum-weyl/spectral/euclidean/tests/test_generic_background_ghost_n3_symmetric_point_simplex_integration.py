from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_n3_symmetric_point_simplex_integration import (
    OUTPUT,
    SCHEMA,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n3_symmetric_point_simplex_integration import (
    verify,
)


def _rehash(value: dict) -> None:
    payload = {
        "masters": value["master_moments"],
        "channels": value["channel_rows"],
    }
    value["formula_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class GenericGhostN3SymmetricPointSimplexIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_strict_schema_and_exact_headline_values(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        validate(self.value)
        rows = {row["channel_id"]: row for row in self.value["channel_rows"]}
        self.assertEqual(
            rows["I10_123"]["integrated_value"]["rational"],
            {"numerator": -440, "denominator": 2187},
        )
        self.assertEqual(
            rows["I10_123"]["integrated_value"][
                "scalar_triangle_master_coefficient"
            ],
            {"numerator": -4736, "denominator": 2187},
        )
        self.assertTrue(
            all(
                rows[channel]["integrated_value"]["rational"]["numerator"] == 0
                and rows[channel]["integrated_value"][
                    "scalar_triangle_master_coefficient"
                ]["numerator"]
                == 0
                for channel in ("I28_123", "I28_132", "I28_231")
            )
        )

    def test_independent_divergence_and_quadrature_replay(self) -> None:
        self.assertEqual(verify(), self.value)

    def test_channel_mutation_is_rejected_after_rehash(self) -> None:
        mutant = deepcopy(self.value)
        mutant["channel_rows"][0]["integrated_value"]["rational"]["numerator"] += 1
        _rehash(mutant)
        with self.assertRaisesRegex(ValueError, "exact reconstruction"):
            verify(mutant)

    def test_divergence_mutation_is_rejected_after_rehash(self) -> None:
        mutant = deepcopy(self.value)
        mutant["master_moments"][0]["divergence_certificate"]["P_terms"][0][
            "coefficient"
        ]["numerator"] += 1
        _rehash(mutant)
        with self.assertRaisesRegex(ValueError, "divergence identity"):
            verify(mutant)

    def test_fail_closed_lifecycle_mutation(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"] = True
        with self.assertRaises(Exception):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
