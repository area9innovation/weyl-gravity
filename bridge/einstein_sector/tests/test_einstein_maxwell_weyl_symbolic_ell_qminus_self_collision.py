from __future__ import annotations

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_qminus_self_collision import build
from bridge.einstein_sector.verify_einstein_maxwell_weyl_symbolic_ell_qminus_self_collision import verify


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json"


class SymbolicEllQminusSelfCollisionTests(unittest.TestCase):
    def test_certificate_is_reproducible(self) -> None:
        self.assertEqual(build(), json.loads(CERTIFICATE.read_text(encoding="utf-8")))

    def test_unique_collision_and_fail_closed_boundary(self) -> None:
        value = build()
        collision = value["symbolic_collision_proof"]["unique_collision"]
        self.assertEqual((collision["L"], collision["K"], collision["Omega"]), ("2*ell", "0", "2*omega_minus"))
        self.assertFalse(value["classification"]["symbolic_dynamical_adjoint_coefficient_computed"])
        self.assertFalse(value["classification"]["all_primary_symbolic_collision_census_complete"])
        self.assertEqual(value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")

    def test_independent_verifier(self) -> None:
        verify()


if __name__ == "__main__":
    unittest.main()
