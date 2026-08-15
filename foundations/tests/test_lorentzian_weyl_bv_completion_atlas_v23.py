#!/usr/bin/env python3
"""Mutation tests for completion Atlas V23."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


CHECK = module("atlas_v23_check_test", ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v23.py")
VERIFY = module("atlas_v23_verify_test", ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v23.py")


class AtlasV23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def mutation_fails(self, change):
        value = deepcopy(self.value)
        change(value)
        self.assertTrue(CHECK.check(value) or VERIFY.verify(value))

    def test_current(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value), [])

    def test_cell_removed(self):
        self.mutation_fails(lambda value: value["branches"][0]["stages"].pop())

    def test_q3_value(self):
        self.mutation_fails(lambda value: value["strict_pure_weyl_q3_witness"].__setitem__("computed_q1_q3_weyl_identity_value", "0"))

    def test_general_closure_overclaim(self):
        self.mutation_fails(lambda value: value["strict_pure_weyl_q3_witness"].__setitem__("general_full_weyl_lambda2_source_closed", True))

    def test_berger_import_overclaim(self):
        self.mutation_fails(lambda value: value["strict_pure_weyl_q3_witness"].__setitem__("Berger_q3_direct_import_compatible", True))

    def test_authoritative_q3_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("strict_386_authoritative_q3_imported", True))

    def test_route_order(self):
        self.mutation_fails(lambda value: value["route_selection"].reverse())


if __name__ == "__main__":
    unittest.main()
