from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_cutoff_volterra_normal_topology_convergence import (
    majorant_ratio,
    majorant_replay,
    proof_replay,
    seminorm_majorant,
    validate,
)
from lorentzian.berger_cutoff_volterra_normal_topology_convergence_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_cutoff_volterra_normal_topology_convergence import (
    verify,
)


class BergerCutoffVolterraNormalTopologyConvergenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/berger-cutoff-volterra-normal-topology-convergence-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_majorant_ratio(self) -> None:
        for r in range(8):
            for n in range(16):
                self.assertEqual(
                    seminorm_majorant(n + 1, derivative_order=r),
                    seminorm_majorant(n, derivative_order=r)
                    * majorant_ratio(n, derivative_order=r),
                )

    def test_simplex_factor_is_load_bearing(self) -> None:
        self.assertTrue(majorant_replay()["absolute_summability"])
        self.assertFalse(
            majorant_replay(include_simplex_factor=False)["absolute_summability"]
        )

    def test_completeness_is_load_bearing(self) -> None:
        self.assertTrue(proof_replay()["all_pass"])
        self.assertFalse(proof_replay(normal_space_complete=False)["all_pass"])

    def test_transpose_reversal_is_load_bearing(self) -> None:
        self.assertFalse(
            proof_replay(transpose_reversal_available=False)["all_pass"]
        )

    def test_order_two_infinite_incidence_is_rejected(self) -> None:
        self.assertFalse(
            proof_replay(order_zero_infinite_incidence=False)["all_pass"]
        )

    def test_transport_overpromotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"][
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
