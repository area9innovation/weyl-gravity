from __future__ import annotations

import copy
import unittest

from foundations.check_krein_state_selection import check
from foundations.verify_krein_state_selection_zf import (
    CSTAR_SOURCE,
    CUBE,
    FOCK_SOURCE,
    KREIN_SOURCE,
    REPORT,
    RESULT,
    load,
    verify,
)


class KreinStateSelectionZFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()
        cls.krein = load(KREIN_SOURCE)
        cls.cstar = load(CSTAR_SOURCE)
        cls.fock = load(FOCK_SOURCE)
        cls.cube = load(CUBE)

    def run_verify(self, *, result=None, report=None, krein=None, cstar=None, fock=None, cube=None):
        return verify(
            result=copy.deepcopy(self.result) if result is None else result,
            report=self.report if report is None else report,
            krein_source=copy.deepcopy(self.krein) if krein is None else krein,
            cstar_source=copy.deepcopy(self.cstar) if cstar is None else cstar,
            fock_source=copy.deepcopy(self.fock) if fock is None else fock,
            cube=copy.deepcopy(self.cube) if cube is None else cube,
        )[0]

    def test_repository_result_passes(self):
        self.assertEqual(self.run_verify(), [])

    def test_sign_normalization_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["finite_exact_witness"]["state_formulas"]["omega_n"] = "omega_n(A)=[n,An]"
        self.assertTrue(self.run_verify(result=result))

    def test_positivity_digest_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_finite_digest"] = "0" * 64
        self.assertTrue(check(result)[0])

    def test_permutation_control_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["finite_exact_witness"]["permutation_controls"][3]["uniform_coordinate_weight"]["denominator"] = 7
        self.assertTrue(check(result)[0])

    def test_krein_source_hash_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["provenance"]["inputs"][0]["sha256"] = "f" * 64
        self.assertTrue(self.run_verify(result=result))

    def test_cstar_source_claim_mutation_fails(self):
        source = copy.deepcopy(self.cstar)
        source["claim_flags"]["explicit_zf_states_constructed"] = False
        self.assertTrue(self.run_verify(cstar=source))

    def test_choice_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["state_construction"]["choice_status"] = "COUNTABLE_CHOICE_USED"
        self.assertTrue(self.run_verify(result=result))

    def test_singular_state_overclaim_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["singular_state_nonexistence_proved"] = True
        self.assertTrue(self.run_verify(result=result))

    def test_physical_state_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["physical_weyl_state_selected"] = True
        self.assertTrue(self.run_verify(result=result))

    def test_lorentzian_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.assertTrue(self.run_verify(result=result))

    def test_cube_promotion_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["cube_promotions"][0]["new_status"] = "COMPLETE"
        self.assertTrue(check(result)[0])

    def test_unapplied_cube_promotion_fails(self):
        cube = copy.deepcopy(self.cube)
        cell = next(
            item for item in cube["cells"]
            if item["foundation"] == "WEAK_CHOICE_ZF"
            and item["carrier"] == "KREIN_INDEFINITE"
            and item["obligation"] == "STATES_PROBABILITY"
        )
        cell["status"] = "PRIORITY_GAP"
        self.assertTrue(self.run_verify(cube=cube))

    def test_report_boundary_mutation_fails(self):
        self.assertTrue(self.run_verify(report=self.report.replace("singular invariant states", "all states")))


if __name__ == "__main__":
    unittest.main()
