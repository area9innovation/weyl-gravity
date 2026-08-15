from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from d_quotient_classical.nonminimal_identity.classical_nonlinear_weyl_boost_ghost_manifest_v1 import build, generated
from d_quotient_classical.nonminimal_identity.check_classical_nonlinear_weyl_boost_ghost_manifest_v1 import check


ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-nonlinear-weyl-boost-ghost-manifest-v1.md"


class NonlinearWeylBoostManifestTests(unittest.TestCase):
    def test_generated_current(self):
        certificate, report = generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_exact_manifest(self):
        value = build()
        self.assertEqual(check(value), [])
        self.assertTrue(value["gauge_algebra"]["off_shell_closure"])
        self.assertTrue(value["claim_flags"]["EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST"])
        self.assertFalse(value["claim_flags"]["FULL_386_SOURCE_Q2_ASSEMBLED"])

    def test_boost_covariance_mutation_rejected(self):
        value = json.loads(RESULT.read_text())
        value["shifted_auxiliary_covariance"]["boost"]["delta_G_b_coefficients"]["g_div_kappa"] = "2"
        self.assertTrue(check(value))

    def test_internal_bracket_mutation_rejected(self):
        value = json.loads(RESULT.read_text())
        row = next(item for item in value["gauge_algebra"]["brackets"] if item["pair"] == "Weyl,boost")
        row["coefficient_defect"] = {"sym_kappa_dsigma": "1"}
        self.assertTrue(check(value))

    def test_exhaustive_boundary_mutation_rejected(self):
        value = copy.deepcopy(build())
        value["claim_flags"]["FULL_386_SOURCE_Q2_ASSEMBLED"] = True
        self.assertTrue(check(value))


if __name__ == "__main__":
    unittest.main()
