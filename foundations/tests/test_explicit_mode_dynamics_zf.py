from __future__ import annotations

import copy
import unittest

from foundations.check_explicit_mode_dynamics import check
from foundations.verify_explicit_mode_dynamics_zf import CUBE, ENERGY, KREIN, REPORT, RESULT, load, verify


class ExplicitModeDynamicsZFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()
        cls.energy = load(ENERGY)
        cls.krein = load(KREIN)
        cls.cube = load(CUBE)

    def run_verify(self, *, result=None, report=None, energy=None, krein=None, cube=None):
        return verify(
            result=copy.deepcopy(self.result) if result is None else result,
            report=self.report if report is None else report,
            energy=copy.deepcopy(self.energy) if energy is None else energy,
            krein=copy.deepcopy(self.krein) if krein is None else krein,
            cube=copy.deepcopy(self.cube) if cube is None else cube,
        )[0]

    def test_repository_result_passes(self):
        self.assertEqual(self.run_verify(), [])

    def test_degree_digest_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_digest"] = "0" * 64
        self.assertTrue(check(result)[0])

    def test_matrix_unit_count_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["finite_exact_witness"]["matrix_units"] = 323
        self.assertTrue(check(result)[0])

    def test_promotion_set_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["cube_promotions"][0]["old_status"] = "PRIORITY_GAP"
        self.assertTrue(check(result)[0])

    def test_choice_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["continuity_and_foundations"]["choice_principle_added"] = "COUNTABLE_CHOICE"
        self.assertTrue(self.run_verify(result=result))

    def test_interacting_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["interacting_dynamics_constructed"] = True
        self.assertTrue(self.run_verify(result=result))

    def test_lorentzian_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.assertTrue(self.run_verify(result=result))

    def test_energy_source_mutation_fails(self):
        energy = copy.deepcopy(self.energy)
        energy["claim_flags"]["explicit_energy_self_adjointness_route_classified"] = False
        self.assertTrue(self.run_verify(energy=energy))

    def test_krein_source_mutation_fails(self):
        krein = copy.deepcopy(self.krein)
        krein["claim_flags"]["zf_one_particle_completion_sufficient"] = False
        self.assertTrue(self.run_verify(krein=krein))

    def test_unapplied_cube_promotion_fails(self):
        cube = copy.deepcopy(self.cube)
        coordinate = ("WEAK_CHOICE_ZF", "ALGEBRAIC_CSTAR", "DYNAMICS_PROPAGATION")
        cell = next(item for item in cube["cells"] if tuple(item[key] for key in ("foundation", "carrier", "obligation")) == coordinate)
        cell["status"] = "PRIORITY_GAP"
        self.assertTrue(self.run_verify(cube=cube))

    def test_report_continuity_boundary_fails(self):
        self.assertTrue(self.run_verify(report=self.report.replace("Stone's theorem is not being invoked", "Stone proves existence")))


if __name__ == "__main__":
    unittest.main()
