import unittest

from bridge.anomaly_restriction.generate_strict_anomaly_restriction_atlas_fragment import (
    build,
)


class StrictAnomalyRestrictionAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment = build()
        cls.entries = {entry["id"]: entry for entry in cls.fragment["entries"]}

    def test_two_backgrounds_are_not_crosswalked(self):
        self.assertEqual(len(self.entries), 2)
        scopes = [entry["scope"]["background"] for entry in self.entries.values()]
        self.assertEqual(len(scopes), len(set(scopes)))

    def test_cylinder_and_berger_have_distinct_fail_closed_statuses(self):
        cylinder = self.entries[
            "bridge.anomaly.cylinder_taub_zero_restriction_carrier_gap"
        ]
        berger = self.entries[
            "bridge.anomaly.berger_strict_pure_weyl_full_bv_map_obstruction"
        ]
        self.assertEqual(cylinder["descriptions"]["quantum"], "NO_CERTIFIED_MAP")
        self.assertEqual(berger["descriptions"]["quantum"], "OBSTRUCTED")
        self.assertEqual(
            cylinder["quantum_data"]["carrier_crosswalk"]["status"],
            "NO_CERTIFIED_MAP",
        )
        self.assertEqual(
            berger["quantum_data"]["carrier_crosswalk"]["status"], "OBSTRUCTED"
        )

    def test_no_particle_or_qme_promotion(self):
        for entry in self.entries.values():
            self.assertEqual(
                entry["quantum_data"]["particle_interpretation"]["status"],
                "NOT_APPLICABLE",
            )
            self.assertNotEqual(entry["descriptions"]["causal"], "CERTIFIED")


if __name__ == "__main__":
    unittest.main()
