import unittest

from local_bv.schema_validation import validate_instance


class SchemaValidationTests(unittest.TestCase):
    def test_nested_required_const_and_additional_properties(self) -> None:
        schema = {
            "type": "object",
            "required": ["payload"],
            "additionalProperties": False,
            "properties": {
                "payload": {
                    "type": "object",
                    "required": ["count"],
                    "additionalProperties": False,
                    "properties": {"count": {"type": "integer", "const": 4}},
                }
            },
        }
        self.assertFalse(validate_instance({"payload": {"count": 4}}, schema))
        errors = validate_instance(
            {"payload": {"count": 3, "extra": True}}, schema
        )
        self.assertEqual(
            errors,
            [
                "$.payload.count: value differs from const",
                "$.payload.extra: additional property is forbidden",
            ],
        )

    def test_array_shape_pattern_and_uniqueness(self) -> None:
        schema = {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "uniqueItems": True,
            "items": {"type": "string", "pattern": "^[a-z]+$"},
        }
        self.assertFalse(validate_instance(["a", "b"], schema))
        self.assertTrue(validate_instance(["A", "A", "b"], schema))

    def test_union_and_null_types(self) -> None:
        schema = {"type": ["string", "null"]}
        self.assertFalse(validate_instance("proof.json", schema))
        self.assertFalse(validate_instance(None, schema))
        self.assertTrue(validate_instance(3, schema))


if __name__ == "__main__":
    unittest.main()
