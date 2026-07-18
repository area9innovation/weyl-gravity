from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from atlas.generate_quantum_atlas_fragment import OUTPUT, build, validate_fragment
from atlas.verify_quantum_atlas_fragment import verify
from residual_atlas.validate_fragment import validate as validate_common_fragment


class QuantumAtlasFragmentTests(unittest.TestCase):
    def test_generated_entry_kinds_and_nonparticle_ledgers(self) -> None:
        value = build()
        kinds = [entry["quantum_data"]["entry_kind"] for entry in value["entries"]]
        self.assertEqual(kinds.count("MODE_FAMILY"), 6)
        self.assertEqual(kinds.count("NONPARTICLE_RESIDUAL_CLASS"), 2)
        self.assertEqual(kinds.count("CARRIER_IMPORT_GAP"), 1)
        self.assertEqual(kinds.count("CLASSICAL_TO_QUANTUM_CROSSWALK"), 1)
        self.assertEqual(kinds.count("NON_MODE_PARTICLE_GUARD"), 3)
        residual = [
            entry for entry in value["entries"]
            if entry["quantum_data"]["entry_kind"] == "NONPARTICLE_RESIDUAL_CLASS"
        ]
        self.assertTrue(all(
            entry["quantum_data"]["particle_interpretation"]["statement"] == "NOT_A_PARTICLE"
            for entry in residual
        ))

    def test_tangent_cone_inference_is_fail_closed(self) -> None:
        entry = next(
            row for row in build()["entries"]
            if row["quantum_data"]["entry_kind"] == "CLASSICAL_TO_QUANTUM_CROSSWALK"
        )
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["quantum_data"]["carrier_crosswalk"]["status"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["quantum_data"]["anomaly_QME_dependency"]["status"], "OBSTRUCTED")
        self.assertIn(
            "full extended BV QME",
            entry["quantum_data"]["anomaly_QME_dependency"]["statement"],
        )

    def test_strict_field_content_quantum_lifecycle_is_obstructed(self) -> None:
        value = build()
        physical = [
            entry for entry in value["entries"]
            if entry["quantum_data"]["entry_kind"]
            in {"MODE_FAMILY", "NONPARTICLE_RESIDUAL_CLASS", "CARRIER_IMPORT_GAP"}
        ]
        self.assertTrue(all(
            entry["quantum_data"]["anomaly_QME_dependency"]["status"] == "OBSTRUCTED"
            for entry in physical
        ))
        local_guard = next(
            entry for entry in value["entries"]
            if entry["id"] == "quantum.crosswalk.local_anomaly_class_to_particle"
        )
        self.assertEqual(
            local_guard["quantum_data"]["anomaly_QME_dependency"]["status"],
            "OBSTRUCTED",
        )
        self.assertEqual(
            local_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )

    def test_non_mode_carriers_are_not_particles(self) -> None:
        guards = [
            entry for entry in build()["entries"]
            if entry["quantum_data"]["entry_kind"] == "NON_MODE_PARTICLE_GUARD"
        ]
        self.assertEqual(len(guards), 3)
        self.assertTrue(all(
            entry["quantum_data"]["particle_interpretation"]["status"] == "NO_CERTIFIED_MAP"
            for entry in guards
        ))

    def test_semantic_and_schema_mutations_are_rejected(self) -> None:
        value = build()
        mutant = deepcopy(value)
        residual = next(
            entry for entry in mutant["entries"]
            if entry["quantum_data"]["entry_kind"] == "NONPARTICLE_RESIDUAL_CLASS"
        )
        residual["quantum_data"]["particle_interpretation"]["statement"] = "PARTICLE"
        with self.assertRaises(ValueError):
            validate_fragment(mutant)
        mutant = deepcopy(value)
        mutant["entries"][0]["descriptions"]["quantum"] = "READY"
        with self.assertRaises(ValidationError):
            validate_fragment(mutant)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())
        validate_common_fragment(OUTPUT)


if __name__ == "__main__":
    unittest.main()
