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
        self.assertEqual(kinds.count("NON_MODE_PARTICLE_GUARD"), 13)
        cubic_guard = next(
            entry for entry in value["entries"]
            if entry["id"] == "quantum.crosswalk.algebraic_cubic_weyl_carrier_to_particle"
        )
        self.assertEqual(
            cubic_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
        third_curvature_guard = next(
            entry for entry in value["entries"]
            if entry["id"] == "quantum.crosswalk.third_curvature_weyl_carrier_manifest_to_particle"
        )
        self.assertEqual(
            third_curvature_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
        cpt_guard = next(
            entry for entry in value["entries"]
            if entry["id"] == "quantum.crosswalk.cpt_universal_third_curvature_kernel_to_particle"
        )
        self.assertEqual(
            cpt_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
        self.assertIn(
            "generic-background full-BV trace substitution open",
            cpt_guard["scope"]["carrier"],
        )
        ghost_guard = next(
            entry for entry in value["entries"]
            if entry["id"] == "quantum.crosswalk.generic_background_diff_weyl_ghost_cpt_obstruction_to_particle"
        )
        self.assertEqual(
            ghost_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
        self.assertIn("minimal-CPT substitution obstructed", ghost_guard["scope"]["carrier"])
        physical_guard = next(
            entry for entry in value["entries"]
            if entry["id"]
            == "quantum.crosswalk.generic_background_physical_hessian_n3_fixture_to_particle"
        )
        self.assertIn("formal-adjoint completion", physical_guard["scope"]["carrier"])
        self.assertEqual(
            physical_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
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
        self.assertEqual(entry["quantum_data"]["anomaly_QME_dependency"]["status"], "CERTIFIED")
        self.assertIn(
            "tau-adic compensator-extended",
            entry["quantum_data"]["anomaly_QME_dependency"]["statement"],
        )
        self.assertIn(
            "raw BoxR coefficient",
            entry["quantum_data"]["anomaly_QME_dependency"]["statement"],
        )
        self.assertIn("structural dependence of the Ricci-scalar sector", entry["claim_boundary"])
        self.assertEqual(entry["quantum_data"]["lifecycle_state"]["status"], "NO_CERTIFIED_MAP")

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
        self.assertEqual(local_guard["quantum_data"]["anomaly_QME_dependency"]["status"], "CERTIFIED")
        self.assertEqual(
            local_guard["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )

    def test_reduced_vacuum_cylinder_bridge4_is_certified_without_full_bv_promotion(self) -> None:
        modes = [
            entry
            for entry in build()["entries"]
            if entry["quantum_data"]["entry_kind"] == "MODE_FAMILY"
        ]
        self.assertEqual(len(modes), 6)
        self.assertTrue(all(
            entry["quantum_data"]["compatible_complex_structure"]["status"]
            == "CERTIFIED"
            and entry["quantum_data"]["Hadamard_two_point_function"]["status"]
            == "CERTIFIED"
            and "not a full-BV kernel"
            in entry["quantum_data"]["Hadamard_two_point_function"]["statement"]
            and entry["quantum_data"]["lifecycle_state"]["status"] == "CERTIFIED"
            for entry in modes
        ))

    def test_berger_hadamard_gap_names_regular_morphism_boundary(self) -> None:
        berger = next(
            entry for entry in build()["entries"]
            if entry["id"] == "quantum.berger.carrier_gap.retained_26_stationary_modes"
        )
        hadamard = berger["quantum_data"]["Hadamard_two_point_function"]
        self.assertEqual(hadamard["status"], "OPEN")
        self.assertIn("temporal-cutoff Green family", hadamard["statement"])
        self.assertIn("regular response morphism", hadamard["statement"])
        self.assertIn(
            "BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY",
            {evidence["result_id"] for evidence in berger["evidence"]},
        )

    def test_non_mode_carriers_are_not_particles(self) -> None:
        guards = [
            entry for entry in build()["entries"]
            if entry["quantum_data"]["entry_kind"] == "NON_MODE_PARTICLE_GUARD"
        ]
        self.assertEqual(len(guards), 13)
        round_s4 = next(
            entry for entry in guards
            if entry["id"]
            == "quantum.crosswalk.round_s4_schur_zeta_factorization_to_particle"
        )
        self.assertIn("factorization defect 5/3", round_s4["scope"]["carrier"])
        self.assertEqual(
            round_s4["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
        fv = next(
            entry for entry in guards
            if entry["id"] == "quantum.crosswalk.fv_conformized_c2_log_form_factor_to_particle"
        )
        self.assertEqual(
            fv["quantum_data"]["particle_interpretation"]["status"],
            "NO_CERTIFIED_MAP",
        )
        ghost = next(
            entry for entry in guards
            if entry["id"]
            == "quantum.crosswalk.generic_background_diff_weyl_ghost_cpt_obstruction_to_particle"
        )
        self.assertIn(
            "resummed into one normalized Schur kernel",
            ghost["scope"]["carrier"],
        )
        self.assertIn("matched zero-pole correction 3^-6", ghost["scope"]["carrier"])
        self.assertEqual(
            {
                evidence["result_id"]
                for evidence in ghost["evidence"]
            },
            {
                "GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION",
                "GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION",
                "GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION",
                "GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION",
                "GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS",
                "GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS",
                "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION",
                "GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT",
                "GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE",
                "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE",
                "ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES",
                "PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER",
                "PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE",
                "PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS",
                "PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE",
                "PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY",
                "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION",
                "GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER",
                "GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL",
                "GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION",
                "GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION",
                "GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION",
                "SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK",
            },
        )
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
