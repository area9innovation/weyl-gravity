from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.repository_round_s4_euler_coefficient import (
    OUTPUT,
    SCHEMA,
    analysis,
    build,
    validate_claim_boundary,
)
from spectral.euclidean.verify_repository_round_s4_euler_coefficient import verify


class RepositoryRoundS4EulerCoefficientTests(unittest.TestCase):
    def test_exact_factor_sum(self) -> None:
        replay = analysis()
        self.assertEqual(Fraction(replay["a"]), Fraction(87, 20))
        self.assertEqual([row["status"] for row in replay["rows"]], ["MATCHED"] * 4)

    def test_certificate_reproduces_validates_and_independently_replays(self) -> None:
        payload = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), payload)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        self.assertEqual(verify()["status"], "INDEPENDENT_REPLAY_ACCEPTED")

    def test_round_s4_cannot_promote_c2_or_qme(self) -> None:
        for flag in ("REPOSITORY_C2_COEFFICIENT_COMPUTED", "QME_DISPOSITION"):
            mutant = deepcopy(build())
            mutant["claim_flags"][flag] = True
            with self.assertRaises(ValueError):
                validate_claim_boundary(mutant)


if __name__ == "__main__":
    unittest.main()
