from __future__ import annotations

from copy import deepcopy
import json
import unittest

from cartan.renormalized_d_ward_insertion_nondefinition import (
    evaluate,
    validate,
)
from cartan.renormalized_d_ward_insertion_nondefinition_certificate import (
    OUTPUT,
    build,
)
from cartan.verify_renormalized_d_ward_insertion_nondefinition import verify


class RenormalizedDWardInsertionNondefinitionTests(unittest.TestCase):
    def test_exact_nondefinition_passes(self) -> None:
        value = evaluate()
        self.assertTrue(all(value["exact_checks"].values()))
        self.assertEqual(
            value["defect_target"]["classification"],
            "UNDEFINED_ANALYTICALLY",
        )

    def test_classical_contraction_is_now_imported(self) -> None:
        value = evaluate()
        self.assertEqual(value["classical_import"]["status"], "CERTIFIED")
        self.assertEqual(value["setting"]["generator_id"], "D_compact")

    def test_reference_scheme_is_explicitly_noncanonical(self) -> None:
        value = evaluate()
        self.assertEqual(
            value["finite_normalization"]["conditions"],
            ["z_C(mu_star)=0", "z_Rhat2(mu_star)=0"],
        )
        self.assertFalse(value["claim_flags"]["FINITE_NORMALIZATION_CANONICAL"])

    def test_first_distribution_extension_is_precise(self) -> None:
        branch = evaluate()["analytic_branches"]["same_background_lorentzian"]
        self.assertEqual(branch["first_missing_operator"], "T2_ren_tau_adic_BV")
        self.assertEqual(branch["off_diagonal_domain"], "M^2 minus Diag_2")
        self.assertIn(
            "EPSTEIN_GLASER_T2_EXTENSION_ACROSS_DIAG2",
            branch["missing_prerequisites"],
        )

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_next_producer_request_is_content_addressed(self) -> None:
        request = build()["producer_request"]
        self.assertEqual(request["to_stream"], "quantum-qme")
        self.assertEqual(len(request["event_sha256"]), 64)

    def test_canonical_normalization_promotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["FINITE_NORMALIZATION_CANONICAL"] = True
        with self.assertRaisesRegex(ValueError, "claim flags"):
            validate(mutant)

    def test_cartan_classification_promotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["defect_target"]["classification"] = "ZERO"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
