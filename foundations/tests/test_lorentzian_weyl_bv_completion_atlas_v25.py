from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("atlas_v25_check_test", ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v25.py")
VERIFY = module("atlas_v25_verify_test", ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v25.py")


class AtlasV25Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value), [])

    def test_generated(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v25.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_channel_count(self):
        self.mutation_fails(lambda value: value["strict_386_stabilized_q3_preflight"].__setitem__("expanded_ternary_block_channels", 15))

    def test_authority_firewall(self):
        self.mutation_fails(lambda value: value["strict_386_stabilized_q3_preflight"].__setitem__("authoritative_full_q3_imported", True))

    def test_causal_firewall(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("strict_386_candidate_causal_lambda2_source_closure_certified", True))

    def test_route_order(self):
        self.mutation_fails(lambda value: value["route_selection"].reverse())


if __name__ == "__main__":
    unittest.main()
