from __future__ import annotations

import json
import unittest
from pathlib import Path

import sympy as sp

from ..produce import (CERTIFICATE, axial_l2_vphi_row, carrier_horizon_gate,
                       polynomial_mode_residual)


class EndpointBasisTests(unittest.TestCase):
    def test_exact_omitted_row_residual(self):
        row, symbols = axial_l2_vphi_row()
        residual, _ = polynomial_mode_residual(row, symbols)
        self.assertEqual(sp.simplify(
            residual - 3*sp.I*(symbols["omega"]-2*sp.I)/symbols["r"]**2), 0)

    def test_mutation_wrong_polynomial_sign_is_caught(self):
        row, s = axial_l2_vphi_row()
        mutated = row.subs({s["H0"]: -sp.I*s["omega"]*s["r"]+2-2/s["r"],
                            s["H1"]: 1}).doit()
        target = 3*sp.I*(s["omega"]-2*sp.I)/s["r"]**2
        self.assertNotEqual(sp.simplify(mutated-target), 0)

    def test_integer_spaced_carrier_resonance_is_compatible(self):
        gate = carrier_horizon_gate()
        self.assertTrue(gate["integer_spaced_resonance"]["compatible"])
        self.assertFalse(gate["integer_spaced_resonance"]["logarithm_forced"])

    def test_mutation_metric_promotion_is_refused(self):
        cert = json.loads(CERTIFICATE.read_text())
        self.assertFalse(cert["claim_flags"]["complete_metric_endpoint_basis_certified"])
        self.assertEqual(cert["disposition"]["reconstructed_metric_endpoint_basis"],
                         "NOT_DEFINED")

    def test_pilot_interval_has_no_exception(self):
        cert = json.loads(CERTIFICATE.read_text())
        self.assertEqual(cert["exceptional_set"]["real_pilot_interval"], [])
        self.assertEqual(cert["declaration"]["frequency"],
                         "real dimensionless omega=M*omega in [1/2,3/4]")


if __name__ == "__main__":
    unittest.main()
