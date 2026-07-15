from __future__ import annotations

from copy import deepcopy
import json
import unittest

from d_quotient_classical.backreacted_clock.verify_berger_retained_minimal_operator import (
    CERTIFICATE,
    SCHEMA,
    validate_portable_schema_contract,
)


class BergerRetainedMinimalOperatorSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text())
        cls.schema = json.loads(SCHEMA.read_text())

    def test_strict_pbw_records_validate(self) -> None:
        validate_portable_schema_contract(self.schema, self.payload)

    def test_required_but_undefined_q1_properties_are_rejected(self) -> None:
        mutant = deepcopy(self.schema)
        mutant["properties"]["q1_blocks"].pop("properties")
        with self.assertRaisesRegex(AssertionError, "undeclared properties"):
            validate_portable_schema_contract(mutant, self.payload)

    def test_bad_pbw_exponent_vector_is_rejected(self) -> None:
        mutant = deepcopy(self.payload)
        mutant["q1_blocks"]["K_spatial"]["entries"][0][2][0][0].append(0)
        with self.assertRaisesRegex(AssertionError, "exponent vector"):
            validate_portable_schema_contract(self.schema, mutant)


if __name__ == "__main__":
    unittest.main()
