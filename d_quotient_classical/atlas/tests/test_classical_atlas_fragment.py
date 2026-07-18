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
        self.assertIn("NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1", ids)
        self.assertIn("NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1", ids)
        self.assertEqual(entry["descriptions"]["causal"], "OPEN")
        self.assertIn("factorized adjunction before PBW normal ordering", entry["claim_boundary"])
        self.assertIn("upper relative-saddle chain closes", entry["claim_boundary"])
        self.assertIn("unique 15-term algebraic cyclic completion", entry["claim_boundary"])
        self.assertIn("direct action-leading coefficients plus Noether uniqueness", entry["claim_boundary"])
        self.assertIn("all twenty-one differentiated ten-block SDR identities vanish", entry["claim_boundary"])
        self.assertIn("algebraic SDR is exact; transverse causal transfer remains open", entry["claim_boundary"])

    def test_berger_bridge_one_remains_fail_closed(self) -> None:
        entry = self.entries["classical.berger.crosswalk.retained36_to_einstein_extra"]
        self.assertEqual(set(entry["descriptions"].values()), {"NO_CERTIFIED_MAP"})
        self.assertIn("Bridge 1 is not activated", entry["claim_boundary"])
        self.assertIn("relative cofiber", entry["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
