from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_retained_36_branch_projector_obstruction_import import (
    LOCAL_SCHEMA,
    OUTPUT,
    SCHEMA_RELATIVE,
    CERTIFICATE_RELATIVE,
    _git_json,
    build,
    validate_classical_payload,
)
from transfer.verify_berger_retained_36_branch_projector_obstruction_import import verify


class BergerRetained36BranchProjectorObstructionImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.classical = _git_json(CERTIFICATE_RELATIVE)
        cls.classical_schema = _git_json(SCHEMA_RELATIVE)

    def test_certificate_reproduces_and_validates(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build())
        self.assertEqual(value, verify())
        schema = json.loads(LOCAL_SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)

    def test_scoped_obstruction_and_next_gate(self) -> None:
        value = build()
        self.assertFalse(
            value["obstruction_scope"]["same_bundle_support_local_projector_exists"]
        )
        self.assertEqual(value["carrier_enlargement"]["natural_candidate_retained_rank"], 46)
        self.assertFalse(value["carrier_enlargement"]["candidate_projector_certified"])
        self.assertEqual(
            value["next_gate"],
            "CONSTRUCT_BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1",
        )

    def test_normalized_witness_mutation_fails(self) -> None:
        forged = deepcopy(self.classical)
        forged["normalized_obstruction_witness"]["degree_two_defect"] = (
            "(71*p1**2 + 71*p2**2 + 9*p3**2)/80 + 1"
        )
        with self.assertRaisesRegex(ValueError, "polynomial remainder"):
            validate_classical_payload(forged, self.classical_schema)

    def test_claim_and_carrier_mutations_fail(self) -> None:
        forged = deepcopy(self.classical)
        forged["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] = True
        with self.assertRaises(Exception):
            validate_classical_payload(forged, self.classical_schema)

        forged = deepcopy(self.classical)
        forged["smallest_carrier_enlargement_required"][
            "smallest_natural_support_local_candidate"
        ]["candidate_retained_rank"] = 36
        with self.assertRaisesRegex(ValueError, "carrier-enlargement"):
            validate_classical_payload(forged, self.classical_schema)


if __name__ == "__main__":
    unittest.main()
