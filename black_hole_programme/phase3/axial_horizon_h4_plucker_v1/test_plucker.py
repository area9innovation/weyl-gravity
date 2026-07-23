from __future__ import annotations

import copy
import hashlib
import json
import unittest

import sympy as sp

from . import produce
from . import verify


class PluckerPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = json.loads(verify.METADATA.read_text())
        cls.schema = json.loads(verify.SCHEMA.read_text())
        cls.source = verify.SOURCE.read_text()
        cls.log = verify.LOG.read_text()

    def test_induced_action_matches_wedge_derivative(self):
        matrix = sp.Matrix([
            [1, 2, 0, -1, 0, 3],
            [0, -2, 1, 0, 1, 0],
            [3, 0, 1, 2, 0, -1],
            [0, 1, 0, 1, 2, 0],
            [-1, 0, 2, 0, 3, 1],
            [2, 1, 0, -2, 0, 1],
        ])
        plane = sp.Matrix([
            [1, 0, 2],
            [0, 1, -1],
            [2, 1, 0],
            [-1, 2, 1],
            [1, 1, 1],
            [0, -1, 2],
        ])
        epsilon = sp.symbols("epsilon")
        direct = produce.plucker_coordinates(
            plane + epsilon * matrix * plane
        ).diff(epsilon).subs(epsilon, 0)
        induced = (
            produce.induced_matrix(matrix)
            * produce.plucker_coordinates(plane)
        )
        self.assertEqual(direct, induced)

    def test_scalar_identity_acts_by_three(self):
        value = sp.symbols("value")
        self.assertEqual(
            produce.induced_matrix(value * sp.eye(6)),
            3 * value * sp.eye(20),
        )

    def test_all_relations_vanish_on_exact_wedge(self):
        plane = sp.Matrix([
            [1, 0, 2],
            [0, 1, -1],
            [2, 1, 0],
            [-1, 2, 1],
            [1, 1, 1],
            [0, -1, 2],
        ])
        coordinates = produce.plucker_coordinates(plane)
        for relation in produce.plucker_relations():
            value = sum(
                coefficient * coordinates[left] * coordinates[right]
                for (left, right), coefficient in relation
            )
            self.assertEqual(sp.expand(value), 0)
        self.assertEqual(produce.relation_span_rank(), 35)

    def test_nontrivial_dyadic_scale(self):
        self.assertEqual(produce.projective_scale_exponent(8.0), 3)
        self.assertEqual(produce.projective_scale_exponent(0.125), -2)

    def test_source_and_log_verify(self):
        verify.verify_source(self.source, self.metadata, self.schema)
        result = verify.verify_log(
            self.log, self.metadata["source_sha256"]
        )
        self.assertEqual(result["segment_count"], 13)
        self.assertEqual(result["final_pivot"], 5)

    def test_induced_table_mutation_is_rejected(self):
        mutated = self.source.replace(
            "0=>PlTerm(0,0,0,0,1)",
            "0=>PlTerm(0,0,0,0,-1)",
            1,
        )
        metadata = copy.deepcopy(self.metadata)
        metadata["source_sha256"] = hashlib.sha256(
            mutated.encode()
        ).hexdigest()
        with self.assertRaisesRegex(
            verify.VerificationError, "signed-term table"
        ):
            verify.verify_source(mutated, metadata, self.schema)

    def test_relation_mutation_is_rejected(self):
        mutated = self.source.replace(
            "PLUCKER_RELATION_DEFECT relation=44",
            "PLUCKER_RELATION_DEFECT relation=43",
            1,
        )
        metadata = copy.deepcopy(self.metadata)
        metadata["source_sha256"] = hashlib.sha256(
            mutated.encode()
        ).hexdigest()
        with self.assertRaisesRegex(
            verify.VerificationError, "runtime relation inventory"
        ):
            verify.verify_source(mutated, metadata, self.schema)

    def test_missing_rank_witness_is_rejected(self):
        mutated = self.log.replace(
            "margin=0.00021578230196176156",
            "margin=0.0",
            1,
        )
        with self.assertRaisesRegex(
            verify.VerificationError, "pivot witness"
        ):
            verify.verify_log(mutated, self.metadata["source_sha256"])

    def test_relation_defect_log_is_rejected(self):
        mutated = self.log + "\nPLUCKER_RELATION_DEFECT relation=0\n"
        with self.assertRaisesRegex(
            verify.VerificationError, "relation defect"
        ):
            verify.verify_log(mutated, self.metadata["source_sha256"])


if __name__ == "__main__":
    unittest.main()
