"""Tests for the BT torus phase-pullback obstruction."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_torus_phase_pullback_obstruction as producer


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_euclidean_torus_phase_pullback_obstruction.py"
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class TorusPhasePullbackObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = producer.build()

    def verify(self, certificate: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(certificate, handle)
            path = handle.name
        try:
            return subprocess.run(
                ["python3", VERIFIER, "--certificate", path],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            os.unlink(path)

    def test_certificate_self_check(self) -> None:
        checks = self.certificate["checks"]
        self.assertTrue(checks["ok"])
        self.assertEqual(checks["passed"], 10)
        self.assertEqual(checks["total"], 10)

    def test_exact_phase_factors(self) -> None:
        cycle = decode(self.certificate["exact_direct_torus_fixture"]["cycle_quotient"])
        for row in self.certificate["exact_direct_torus_fixture"]["torus_rows"]:
            active = row["active_coordinates"]
            self.assertEqual(decode(row["torus_quotient"]), active**2 * cycle)
            self.assertEqual(decode(row["quotient_over_cycle"]), active**2)

    def test_hierarchy_peak_symmetry_and_scaling(self) -> None:
        for row in self.certificate["exact_hierarchy_fixtures"]:
            m = row["member"]
            self.assertEqual(row["length"], 4 * m**4 + 2)
            self.assertEqual(decode(row["maximum_edge_ratio"]), m)
            self.assertEqual(decode(row["opposite_current"]), -decode(row["peak_current"]))
            self.assertEqual(
                decode(row["cycle_quotient_scaled_by_m6"]),
                decode(row["cycle_quotient"]) * m**6,
            )

    def test_unmodified_certificate_passes_independent_verifier(self) -> None:
        result = self.verify(self.certificate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mutated_predecessor_hash_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_direct_torus_norm_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_direct_torus_fixture"]["torus_rows"][1][
            "torus_gradient_norm_squared"
        ]["numerator"] += 1
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_phase_factor_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["phase_pullback_theorem"]["quotient_identity"] = "Q_T=k*Q_C"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_mutated_lower_bound_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["hierarchy_lower_bound"]["cycle_lower"] = "Q_C>=1/(14m^6) for m>=4"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_false_all_field_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["research_disposition"]["all_field_torus_scaled_PL"] = "PROVED"
        self.assertNotEqual(self.verify(mutated).returncode, 0)

    def test_lorentzian_tag_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.assertNotEqual(self.verify(mutated).returncode, 0)


if __name__ == "__main__":
    unittest.main()
