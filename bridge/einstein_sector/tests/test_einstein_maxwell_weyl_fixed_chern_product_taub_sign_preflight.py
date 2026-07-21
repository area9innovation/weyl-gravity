from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight import (
    ATLAS_OUTPUT,
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_atlas,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight import (
    IndependentPreflightVerificationError,
    verify_certificate,
)


class FixedChernProductTaubSignPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_and_exact_import_count(self) -> None:
        jsonschema.Draft202012Validator(self.schema).validate(self.payload)
        self.assertEqual(len(self.payload["provenance"]["imported_artifacts"]), 6)

    def test_subcritical_critical_supercritical_chambers(self) -> None:
        chambers = self.payload["fixed_chern_background_theorem"]["chambers"]
        self.assertEqual([row["background_count"] for row in chambers], [0, 1, 2])
        self.assertEqual(chambers[1]["multiplicity"], 2)
        self.assertEqual(chambers[1]["k_1"], "0")

    def test_open_chamber_contains_ds_and_ads_branches(self) -> None:
        branches = self.payload["fixed_chern_background_theorem"]["chambers"][2]["branches"]
        self.assertEqual([branch["sign_k_1"] for branch in branches], ["POSITIVE", "NEGATIVE"])

    def test_rational_fixture(self) -> None:
        fixture = self.payload["fixed_chern_background_theorem"]["exact_fixture"]
        self.assertEqual(fixture["alpha_critical"], "3")
        self.assertEqual(
            fixture["open_chamber_example"]["branches"],
            [{"k_2": "1/2", "k_1": "1/4"}, {"k_2": "3/2", "k_1": "-3/4"}],
        )

    def test_off_wall_sign_promotions_are_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["flat_fixture_is_double_root_wall"])
        self.assertFalse(classification["off_wall_extra_energy_definiteness_certified"])
        self.assertFalse(classification["off_wall_einstein_opposite_sign_certified"])
        self.assertFalse(classification["sign_change_across_wall_certified"])

    def test_atlas_is_fail_closed(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("certificate has not been generated")
        atlas = build_atlas(self.payload, DEFAULT_OUTPUT)
        self.assertEqual(
            atlas["entries"][0]["descriptions"],
            {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "NO_CERTIFIED_MAP",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
        )

    def test_schema_rejects_false_sign_promotion(self) -> None:
        mutation = copy.deepcopy(self.payload)
        mutation["classification"]["off_wall_extra_energy_definiteness_certified"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutation)

    def test_committed_payload_matches_and_independent_verifier_passes(self) -> None:
        if not DEFAULT_OUTPUT.exists() or not ATLAS_OUTPUT.exists():
            self.skipTest("generated artifacts have not been written")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_independent_verifier_rejects_certificate_hash_mutation(self) -> None:
        if not DEFAULT_OUTPUT.exists() or not ATLAS_OUTPUT.exists():
            self.skipTest("generated artifacts have not been written")
        mutation = copy.deepcopy(json.loads(ATLAS_OUTPUT.read_text(encoding="utf-8")))
        mutation["entries"][0]["evidence"][0]["sha256"] = "0" * 64
        temp = ATLAS_OUTPUT.with_suffix(".mutation-test.json")
        try:
            temp.write_text(json.dumps(mutation), encoding="utf-8")
            with self.assertRaises(IndependentPreflightVerificationError):
                verify_certificate(DEFAULT_OUTPUT, temp)
        finally:
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
