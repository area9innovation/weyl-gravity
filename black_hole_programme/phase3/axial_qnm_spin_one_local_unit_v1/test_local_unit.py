#!/usr/bin/env python3
"""Adversarial tests for the spin-one local-unit certificate."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import sympy as sp

from .verify import CERTIFICATE, CROSSCHECK, RUN, verify_paths


def dump(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SpinOneLocalUnitTests(unittest.TestCase):
    def test_spin_one_reduced_operator_coefficients(self) -> None:
        z, omega, rho = sp.symbols("z omega rho")
        lapse = 1 - 2 * z
        # After y=exp(-i omega x)v, r->z=1/r and division by z^2.
        aa = sp.expand(lapse**2 * z**2)
        bb = sp.expand(
            2 * lapse**2 * z
            - 2 * lapse * z**2
            + 2 * sp.I * omega * lapse
        )
        cc = sp.expand(-6 * (1 - 2 * z))
        self.assertEqual(aa, z**2 - 4 * z**3 + 4 * z**4)
        self.assertEqual(
            sp.simplify(
                bb
                - (
                    2 * sp.I * omega
                    + (2 - 4 * sp.I * omega) * z
                    - 10 * z**2
                    + 12 * z**3
                )
            ),
            0,
        )
        self.assertEqual(cc, -6 + 12 * z)
        # At the horizon the common multiplier r^4/(r-2) sends V_1
        # to 6r=12+6rho.
        self.assertEqual(-6 * (2 + rho), -12 - 6 * rho)

    def test_certificate_verifies(self) -> None:
        verify_paths()

    def test_zero_containing_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = json.loads(RUN.read_text())
            run["local_unit_gate"]["delta"]["real_radius"] = "1"
            run["local_unit_gate"]["delta"]["imag_radius"] = "1"
            run["local_unit_gate"][
                "certified_rational_modulus_lower"
            ] = "1/2500"
            changed_run = root / "run.json"
            dump(changed_run, run)
            certificate = json.loads(CERTIFICATE.read_text())
            certificate["run"]["sha256"] = sha(changed_run)
            changed_certificate = root / "certificate.json"
            dump(changed_certificate, certificate)
            with self.assertRaises(AssertionError):
                verify_paths(changed_certificate, changed_run, CROSSCHECK)

    def test_wrong_smith_promotion_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            certificate = json.loads(CERTIFICATE.read_text())
            certificate["result"]["full_connection_smith_valuations"] = [
                0, 1, 1
            ]
            changed = root / "certificate.json"
            dump(changed, certificate)
            with self.assertRaises(AssertionError):
                verify_paths(changed, RUN, CROSSCHECK)

    def test_green_resolvent_overclaim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            certificate = json.loads(CERTIFICATE.read_text())
            certificate["claim_flags"][
                "green_resolvent_second_order_pole_established"
            ] = True
            changed = root / "certificate.json"
            dump(changed, certificate)
            with self.assertRaises(AssertionError):
                verify_paths(changed, RUN, CROSSCHECK)


if __name__ == "__main__":
    unittest.main()
