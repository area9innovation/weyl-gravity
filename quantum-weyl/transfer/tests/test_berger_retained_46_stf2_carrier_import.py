from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_retained_46_stf2_carrier_import import (
    EXPECTED_CHECKS,
    OUTPUT,
    SCHEMA,
    SparseOperator,
    _load_inputs,
    _replay,
    build,
    validate,
)
from transfer import berger_qsqrt10_replay as q10
from transfer.verify_berger_retained_46_stf2_carrier_import import verify


class BergerRetained46STF2CarrierImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_receipt_reproduces_and_schema_is_strict(self) -> None:
        committed = json.loads(OUTPUT.read_text())
        self.assertEqual(committed, self.value)
        self.assertEqual(committed, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(committed)

    def test_all_graph_sdr_identities_are_independently_replayed(self) -> None:
        replay = self.value["independent_replay"]
        self.assertFalse(replay["producer_executed"])
        self.assertEqual(set(replay["checks"]), EXPECTED_CHECKS)
        self.assertTrue(all(replay["checks"].values()))

    def test_carrier_and_projector_are_not_conflated(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED"])
        self.assertTrue(flags["RANK_46_GRAPH_SDR_INDEPENDENTLY_REPLAYED"])
        self.assertFalse(flags["RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED"])
        self.assertFalse(flags["ELL3_BRANCH_MIXING_AUTHORIZED"])
        self.assertFalse(flags["RANK_46_IS_QUANTUM_PREREQUISITE"])

    def test_operator_mutation_breaks_exact_replay(self) -> None:
        _classical, _schema, matrices = _load_inputs()
        iota = matrices["iota_36_to_46"]
        terms = dict(iota.terms)
        key = min(terms)
        terms[key] = q10.qadd(terms[key], q10.ONE)
        mutant = dict(matrices)
        mutant["iota_36_to_46"] = SparseOperator(iota.shape, terms)
        with self.assertRaisesRegex(ValueError, "independent rank-46 replay failed"):
            _replay(mutant)

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
            "Q2_Q3_LIFT_MATERIALIZED_ON_RANK_46",
            "LORENTZIAN_CAUSAL",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
