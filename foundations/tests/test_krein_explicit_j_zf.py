from __future__ import annotations

import copy
import unittest

from foundations.check_krein_explicit_j import check
from foundations.verify_krein_explicit_j_zf import (
    FOCK_PATH,
    LITERATURE_PATH,
    ONE_PARTICLE_PATH,
    REPORT_PATH,
    RESULT_PATH,
    load_json,
    verify,
)


class KreinExplicitJZFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = load_json(RESULT_PATH)
        cls.one_particle = load_json(ONE_PARTICLE_PATH)
        cls.fock = load_json(FOCK_PATH)
        cls.literature = load_json(LITERATURE_PATH)
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def verify_mutation(self, *, result=None, one_particle=None, fock=None, literature=None, report=None):
        errors, _ = verify(
            result=copy.deepcopy(self.result) if result is None else result,
            one_particle=copy.deepcopy(self.one_particle) if one_particle is None else one_particle,
            fock=copy.deepcopy(self.fock) if fock is None else fock,
            literature=copy.deepcopy(self.literature) if literature is None else literature,
            report_text=self.report if report is None else report,
        )
        return errors

    def test_repository_certificate_passes(self) -> None:
        self.assertEqual(self.verify_mutation(), [])

    def test_integer_checker_rejects_sign_mutation(self) -> None:
        result = copy.deepcopy(self.result)
        result["mode_witness"]["form_sign"]["A"] = 1
        errors, _ = check(result)
        self.assertTrue(errors)

    def test_integer_checker_rejects_branch_mutation(self) -> None:
        result = copy.deepcopy(self.result)
        result["mode_witness"]["branch_minimum"]["L"] = 3
        errors, _ = check(result)
        self.assertTrue(errors)

    def test_cutoff_digest_drift_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_cutoff_digest"] = "f" * 64
        self.assertTrue(self.verify_mutation(result=result))

    def test_choice_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["first_new_commitments"]["choice_principle_added"] = "COUNTABLE_CHOICE"
        self.assertTrue(self.verify_mutation(result=result))

    def test_weakest_base_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["first_new_commitments"]["weakest_subsystem_status"] = "PROVED"
        self.assertTrue(self.verify_mutation(result=result))

    def test_source_regression_drift_is_rejected(self) -> None:
        source = copy.deepcopy(self.one_particle)
        source["regression"]["level_dimensions"]["12"] = 851
        self.assertTrue(self.verify_mutation(one_particle=source))

    def test_fock_control_drift_is_rejected(self) -> None:
        fock = copy.deepcopy(self.fock)
        fock["sample"]["dimension_Sym2_H2"] = 54
        self.assertTrue(self.verify_mutation(fock=fock))

    def test_source_hash_drift_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(self.verify_mutation(result=result))

    def test_literature_identity_drift_is_rejected(self) -> None:
        literature = copy.deepcopy(self.literature)
        entry = next(item for item in literature["entries"] if item["id"] == "blackadar-farah-karagila-2026")
        entry["artifact"]["sha256"] = "0" * 64
        self.assertTrue(self.verify_mutation(literature=literature))

    def test_dag_cycle_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["proof_dependency_dag"]["edges"].append({"from": "B0", "to": "D0"})
        self.assertTrue(self.verify_mutation(result=result))

    def test_lorentzian_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["dependency_tags"] = ["LORENTZIAN-CAUSAL"]
        self.assertTrue(self.verify_mutation(result=result))

    def test_report_boundary_drift_is_rejected(self) -> None:
        report = self.report.replace("not the weakest", "minimal")
        self.assertTrue(self.verify_mutation(report=report))


if __name__ == "__main__":
    unittest.main()
