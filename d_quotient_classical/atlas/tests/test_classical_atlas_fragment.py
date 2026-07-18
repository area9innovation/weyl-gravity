from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ATLAS = ROOT / "d_quotient_classical/atlas/classical-causal-atlas-fragment.json"


class ClassicalAtlasFragmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(ATLAS.read_text())
        cls.entries = {entry["id"]: entry for entry in cls.value["entries"]}

    def test_required_backgrounds(self) -> None:
        ids = set(self.entries)
        self.assertTrue(any("vacuum_cylinder" in value for value in ids))
        self.assertTrue(any("berger" in value for value in ids))
        self.assertTrue(any("nariai" in value for value in ids))
        self.assertIn("classical.bach_flat.open_parent_detour", ids)

    def test_W_squares_are_not_particles(self) -> None:
        for name in ("plus", "minus"):
            carrier = self.entries[f"classical.vacuum_cylinder.deformation.w_{name}_squared"]["scope"]["carrier"]
            self.assertIn("not a one-particle mode", carrier)

    def test_correction_classes_are_separate(self) -> None:
        for entry in self.entries.values():
            second = entry["mode_data"]["second_order"]
            self.assertIn("bounded_or_finite_quasiperiodic", second)
            self.assertIn("smooth_secular", second)
            self.assertIn("causal_retarded", second)

    def test_transverse_nariai_parent_is_scoped(self) -> None:
        entry = self.entries["classical.nariai.transverse_kantowski_sachs_tangent"]
        ids = {item["result_id"] for item in entry["evidence"]}
        self.assertIn("NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1", ids)
        self.assertEqual(entry["descriptions"]["causal"], "OPEN")
        self.assertIn("207-coefficient", entry["claim_boundary"])
        self.assertIn("unique 59-coefficient endpoint gauge repair", entry["claim_boundary"])
        self.assertIn("Phi-only repair is obstructed", entry["claim_boundary"])
        self.assertIn("first-square map is invertible", entry["claim_boundary"])
        self.assertIn("normalized-L0 response map has rank 44 but augmented rank 45", entry["claim_boundary"])
        self.assertIn("five-term witness", entry["claim_boundary"])
        self.assertIn("action-derived transverse first-BGG variation has zero coefficients", entry["claim_boundary"])

    def test_berger_bridge_one_remains_fail_closed(self) -> None:
        entry = self.entries["classical.berger.crosswalk.retained36_to_einstein_extra"]
        self.assertEqual(set(entry["descriptions"].values()), {"NO_CERTIFIED_MAP"})
        self.assertIn("Bridge 1 is not activated", entry["claim_boundary"])
        self.assertIn("relative cofiber", entry["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
