from __future__ import annotations

import importlib.util
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest


TRANSFER_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, TRANSFER_ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


REPLAY = _load("berger_qsqrt10_replay_test", "berger_qsqrt10_replay.py")
CERTIFICATE = _load(
    "berger_support_local_q2_replay_certificate_test",
    "berger_support_local_q2_replay_certificate.py",
)
SCHEMA = (
    TRANSFER_ROOT
    / "schema"
    / "berger-support-local-q2-scientific-replay-v1.schema.json"
)


class BergerSupportLocalQ2ScientificReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = CERTIFICATE.validate_checked_receipt()
        cls.replay = cls.certificate["replay"]

    def test_quadratic_field_and_noncommutative_pbw_are_exact(self) -> None:
        self.assertEqual(
            REPLAY.qmul((Fraction(1, 2), Fraction(1, 3)), (Fraction(2), Fraction(-1))),
            (Fraction(-7, 3), Fraction(1, 6)),
        )
        self.assertEqual(
            REPLAY.pbw_word((2, 1)),
            (((1, 2), REPLAY.ONE), ((3,), REPLAY.qneg((Fraction(0), Fraction(3, 20))))),
        )

    def test_all_landed_scientific_identities_replay_exactly(self) -> None:
        self.assertTrue(self.replay["all_identities_pass"])
        self.assertEqual(
            {
                name: result["nonzero_coefficient_count"]
                for name, result in self.replay["results"].items()
            },
            {
                "q1_q2_arity_two_nilpotency": 0,
                "D_q2_derivation": 0,
                "BV_cyclicity_q2": 0,
            },
        )
        self.assertEqual(self.replay["input"]["q2_term_count"], 150305)

    def test_odd_darboux_polarization_is_explicit(self) -> None:
        convention = self.replay["cyclicity_convention"]
        self.assertEqual(
            convention["identity"],
            "T(a,b,c)=(-1)^(dual(b)+parity(a)*parity(b))*T(c,a,b)",
        )

    def test_small_valid_degree_mutation_is_detected(self) -> None:
        imported = REPLAY.scientific_import.import_support_local_q2()
        q1_raw, _d_raw, pairing_raw = REPLAY.generic.load_committed_operators()
        q1 = REPLAY._parse_linear(q1_raw, name="q1")
        pairing = REPLAY._parse_pairing(pairing_raw)
        fixture = {(27, 5, 5, (), ()): REPLAY.ONE}
        mutation = {(28, 5, 5, (), ()): REPLAY.ONE}
        self.assertFalse(REPLAY.arity_two_defect(q1, fixture, imported.parsed.degrees))
        self.assertFalse(REPLAY.cyclicity_defect(fixture, pairing, imported.parsed.degrees))
        self.assertTrue(REPLAY.arity_two_defect(q1, mutation, imported.parsed.degrees))
        self.assertTrue(REPLAY.cyclicity_defect(mutation, pairing, imported.parsed.degrees))

    def test_certificate_and_strict_schema_reproduce(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(self.certificate))
        self.assertFalse(self.certificate["claim_flags"]["TRANSFERRED_ELL2_COMPUTED"])
        self.assertFalse(self.certificate["claim_flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
