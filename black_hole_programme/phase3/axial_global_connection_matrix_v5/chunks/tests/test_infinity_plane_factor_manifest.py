from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ..infinity_plane_factor_manifest import verify_manifest
from ..verify_handoff import HandoffError


HERE = Path(__file__).resolve()
ROOT = HERE.parents[5]
ARTIFACTS = HERE.parents[1] / "artifacts"
MANIFEST = ARTIFACTS / "infinity_plane_manifests" / "q00.json"


class InfinityPlaneFactorManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(MANIFEST.read_text())

    def test_q0_manifest_replays(self) -> None:
        self.assertTrue(
            verify_manifest(self.payload, 0, ARTIFACTS, ROOT)
        )
        self.assertEqual(self.payload["proof"]["total_step_count"], 279)

    def test_missing_radial_factor_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        del payload["steps"][10]
        with self.assertRaisesRegex(HandoffError, "incomplete or unordered"):
            verify_manifest(
                payload, 0, ARTIFACTS, ROOT, rebuild=False
            )

    def test_missing_crosswalk_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["steps"][212]["kind"] = "restricted-prefix-factor"
        with self.assertRaisesRegex(HandoffError, "crosswalk missing"):
            verify_manifest(
                payload, 0, ARTIFACTS, ROOT, rebuild=False
            )

    def test_full_matrix_promotion_mutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["proof"][
            "full_matrix_join_not_used_for_plane_classification"
        ] = False
        with self.assertRaisesRegex(HandoffError, "proof drift"):
            verify_manifest(
                payload, 0, ARTIFACTS, ROOT, rebuild=False
            )


if __name__ == "__main__":
    unittest.main()
