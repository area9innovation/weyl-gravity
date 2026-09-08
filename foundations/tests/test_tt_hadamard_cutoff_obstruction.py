"""Mutation controls for the reduced TT obstruction's finite evidence."""
from copy import deepcopy
import json
import unittest

from foundations.verify_tt_hadamard_cutoff_obstruction import OUTPUT, verify


class CutoffObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(OUTPUT.read_text())

    def test_independent_replay(self):
        verify(self.value)

    def test_mutations_are_rejected(self):
        mutations = (
            ("negative sign", lambda v: v["exact_examples"][0].update(filtered_reference_expectation="1/96")),
            ("CCR", lambda v: v["exact_examples"][0].update(finite_repair_coefficients=["0", "1/96", "0"])),
            ("positivity", lambda v: v["exact_examples"][0].update(repaired_coefficients=["1/48", "-1/96", "0"])),
            ("spectral gap", lambda v: v["exact_examples"][0].update(E_frequency=3)),
            ("smooth bound", lambda v: v["exact_examples"][0].update(necessary_B_squared_M_for_nonnegative_test="0")),
            ("all-energy", lambda v: v["positive_polynomial_witnesses_n_equals_m_plus_4"].update(gap=["12", "3"])),
            ("filter", lambda v: v["formulas"].update(filter_at_E_plus_minus=["1", "0"])),
            ("hash", lambda v: v["inputs"][0].update(sha256="0"*64)),
            ("lost input", lambda v: v["inputs"].pop()),
            ("causal promotion", lambda v: v["dependency_tags"].append("LORENTZIAN-CAUSAL")),
            ("strict promotion", lambda v: v["claim_flags"].update(FULL_STRICT_386_PHYSICAL_POSITIVITY_DECIDED=True)),
            ("machine promotion", lambda v: v["claim_flags"].update(INFINITE_ANALYSIS_MACHINE_VERIFIED=True)),
            ("novelty", lambda v: v["claim_flags"].update(NEW_GHOST_DISCOVERY_CLAIMED=True)),
            ("hide drift", lambda v: v["import_audit"].update(drift=[])),
            ("import promotion", lambda v: v["import_audit"].update(reference_gate="PASS")),
            ("programme promotion", lambda v: v["claim_flags"].update(CURRENT_PROGRAMME_PHYSICAL_RESULT_ACTIVATED=True)),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                v = deepcopy(self.value)
                mutate(v)
                with self.assertRaises(ValueError):
                    verify(v)


if __name__ == "__main__":
    unittest.main()
