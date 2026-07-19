from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ATLAS = ROOT / "bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json"


class EinsteinAtlasFragmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(ATLAS.read_text(encoding="utf-8"))
        cls.entries = {entry["id"]: entry for entry in cls.value["entries"]}

    def test_stable_identifiers_are_unique(self) -> None:
        self.assertEqual(len(self.entries), len(self.value["entries"]))

    def test_twist_exceptional_is_independence_witness(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.twist_exceptional_independence"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")

    def test_exceptional_difference_frequency_census_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.exceptional_ell1_k0_difference_frequency_census"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("Twenty-seven exact resultant", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_causal_compact_product_claims_remain_fail_closed(self) -> None:
        for entry in self.value["entries"]:
            if "crosswalk" not in entry["id"]:
                self.assertIn(entry["mode_data"]["second_order"]["causal_retarded"]["status"], {"OPEN", "NO_CERTIFIED_MAP"})

    def test_bridge_one_is_linear_and_fail_closed_downstream(self) -> None:
        entry = self.entries["einstein.ph.bridge.relative_branch_dictionary_v1"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("NONCYCLIC_THREE_FORM_LINEAR_TRIANGLE_CERTIFIED", entry["claim_boundary"])
        self.assertIn("without harmonic selection", entry["claim_boundary"])
        self.assertIn("causal Green data and q2/q3 relative compatibility remain open", entry["claim_boundary"])
        self.assertEqual(entry["descriptions"]["observational"], "NO_CERTIFIED_MAP")
        self.assertEqual(entry["descriptions"]["quantum"], "NO_CERTIFIED_MAP")

    def test_candidate13_derived_source_crosswalk_preserves_full_f2_obstruction(self) -> None:
        entry = self.entries["einstein.ph.bridge.relative_candidate13_derived_source_crosswalk"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("circle-pressure", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("separate 18-dimensional", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("exactly {0}", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("full-domain support-local f2 remains obstructed", entry["claim_boundary"])
        self.assertIn("arity three is not authorized", entry["claim_boundary"])

    def test_nonzero_k_exceptional_cofiber_is_registered_without_bridge_promotion(self) -> None:
        entry = self.entries["einstein.ph.wm.extra.exceptional_ell1_nonzero_k"]
        self.assertEqual(entry["mode_data"]["dispersion"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["lee_wald"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "OPEN")

    def test_nonzero_k_constant_twist_same_shell_is_sharp_but_not_sufficient(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.nonzero_k_constant_twist_same_shell"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("exactly m_A=0", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("Opposite-momentum wave-wave terms", entry["claim_boundary"])
        self.assertEqual(entry["mode_data"]["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_finite_multimomentum_divisor_is_arithmetic_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.finite_multimomentum_resonance_divisor"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("squared shell divisor is linear", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Identity-resonant", entry["claim_boundary"])

    def test_first_two_abs_momentum_carrier_has_no_identity_resonance(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_identity_audit"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("exceptional set is finite", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Isolated candidates", entry["claim_boundary"])

    def test_first_two_abs_momentum_candidates_are_exact_but_sources_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_isolated_candidates"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("21 distinct positive algebraic rho", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Later rows close bounded origin", entry["claim_boundary"])
        self.assertIn("nonzero bounded points for 16-21", entry["claim_boundary"])

    def test_collision_scalar_classifier_keeps_fifteen_six_split(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_collision_scalar_separation_classification"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("universal midpoint factorization", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("indices 1-15", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("indices 16-21", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not a mode identification across backgrounds", entry["claim_boundary"])

    def test_same_sign_same_fibre_census_closes_only_its_rows(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_collision_same_fibre_census"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("864 exact same-fibre", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("cross-fibre resonance remains", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("full cone geometry", entry["claim_boundary"])

    def test_same_sign_witnesses_prove_nonempty_not_full_cones(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_collision_bounded_witnesses"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("candidate 21", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("six distinct", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not a classification", entry["claim_boundary"])

    def test_same_sign_scalar_cone_has_four_extreme_rays(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_scalar_extreme_rays"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("exactly four", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("scalar nonnegative occupation cone", entry["claim_boundary"])

    def test_all_24_scalar_extreme_rays_lift_but_sums_remain_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_extreme_ray_lifts"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("Ten lifts omit", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("24 scalar extreme rays", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not a classification of arbitrary nonnegative sums", entry["claim_boundary"])

    def test_same_sign_scalar_cones_have_bounded_sections(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_scalar_cone_sections"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("arbitrary scalar-cone occupations", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("projects surjectively", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not a statement that every amplitude", entry["claim_boundary"])

    def test_same_sign_phase_parity_fibre_product_is_exact_but_not_decomposed_over_reals(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_phase_parity_fibre_product"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("complex resonance varieties are decomposed", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("necessary and sufficient", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not an irreducible real Hermitian", entry["claim_boundary"])

    def test_same_sign_resonance_face_fibres_are_complex_not_real_complete(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_resonance_face_fibres"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("component counts are 1,1,1,4,1,2", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("DIFFERENCE channel on 17,20", entry["scope"]["omega"])
        self.assertIn("not a real connected-component", entry["claim_boundary"])

    def test_same_sign_automatic_face_rotation_links_are_connected_only_in_scope(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_automatic_face_rotation_links"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("nonempty connected zero fibre", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("full bilinear factor", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("nonempty and connected", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("only on automatic faces", entry["claim_boundary"])

    def test_same_sign_axisymmetric_section_is_rotation_critical(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_same_sign_axisymmetric_rotation_critical_locus"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("rank zero at the origin and exactly two", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("critical", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not a quadratic-normal-form", entry["claim_boundary"])

    def test_first_two_abs_momentum_parity_workload_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_parity_workload"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("164 reduced scalar adjoint coefficient", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("56 odd-L", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_candidate4_axial_source_is_obstructed_only_in_bounded_class(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate4_axial_bounded_obstruction"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertIn("norm witness 3622", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("other 162 workload coefficients", entry["claim_boundary"])

    def test_axial_qminus_l4_triplet_is_obstructed_without_merging_fibres(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_qminus_l4_triplet_obstruction"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertIn("nonzero constant term excludes zero", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("three fibres are not identified", entry["mode_data"]["dispersion"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("other 160 workload coefficients", entry["claim_boundary"])

    def test_complete_axial_axial_l4_basis_matrix_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_axial_l4_matrix"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertIn("26 have exact rational intervals excluding zero", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("distinct rows are not identified", entry["mode_data"]["dispersion"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not its arbitrary-amplitude zero variety", entry["claim_boundary"])

    def test_complete_polar_polar_l4_basis_matrix_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_polar_polar_l4_matrix"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertIn("26 have exact rational intervals excluding zero", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("distinct rows are not identified", entry["mode_data"]["dispersion"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("two ordered cross-parity matrices", entry["claim_boundary"])

    def test_forward_cross_parity_l4_matrix_is_ordered_and_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_polar_l4_matrix"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("All 27 scalar adjoint coefficients", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("reverse input order is not identified", entry["mode_data"]["dispersion"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not the reverse order", entry["claim_boundary"])

    def test_reverse_cross_parity_closes_basis_workload_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_polar_axial_l4_matrix"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("explicit role substitution, not name matching", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("All 27 scalar adjoint coefficients", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("108 of 108 axisymmetric L4 basis coefficients", entry["claim_boundary"])

    def test_complete_cross_fibre_basis_matrix_stays_amplitude_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_nonaxisymmetric_l1_matrix"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("All twelve exceptional L1 adjoint coefficients are nonzero", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("164 of 164 branch-basis scalar coefficients", entry["claim_boundary"])
        self.assertIn("not the arbitrary-amplitude zero variety", entry["claim_boundary"])

    def test_cross_fibre_amplitude_system_stays_factorized_and_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_cross_fibre_amplitude_system"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("twenty-one pairwise distinct physical circumference", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("54 target-parity/adjoint equations", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("128 ordered branch-basis fixtures", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("418 complex scalar magnetic", entry["mode_data"]["lee_wald"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not an irreducible zero-variety decomposition", entry["claim_boundary"])

    def test_scalar_l4_zero_varieties_have_four_components_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l4_zero_varieties"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("fibres 3,5,9,15,21", entry["mode_data"]["dispersion"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("exactly four ten-dimensional linear components", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("two mixed proportionality sheets", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("other sixteen fibres", entry["claim_boundary"])
        self.assertIn("complete two-fibre tangent cone", entry["claim_boundary"])

    def test_odd_l_highest_weight_subspaces_are_witnesses_not_cones(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_odd_l_highest_weight_zero_subspaces"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("three L1 difference carriers and six L3 sum carriers", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("all 130 scalar equations", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not their complete irreducible ideals", entry["claim_boundary"])

    def test_scalar_l3_candidate_two_is_a_full_ideal_not_an_extension(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l3_zero_variety"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("Candidate 2 remains one declared physical circumference", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("irreducible complex dimension-12", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("twenty minors", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("other fifteen fibrewise ideals", entry["claim_boundary"])

    def test_scalar_l1_varieties_are_full_ideals_not_extensions(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l1_zero_varieties"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("Candidates 14,17,20", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("lambda squared equal to 128/5", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("irreducible complex dimension-14", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all 20 fibrewise cross-fibre resonance ideals are now classified", entry["claim_boundary"])

    def test_candidate4_target_doublet_has_four_components_not_an_extension(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate4_l4_zero_variety"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("two target-adjoint components", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("exactly four ten-dimensional linear components", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("plus or minus sqrt(3)", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all 20 fibrewise cross-fibre resonance ideals are now classified", entry["claim_boundary"])

    def test_target_doublet_l3_varieties_are_determinantal_not_extensions(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_target_doublet_l3_zero_varieties"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("Candidates 1 and 16 remain two separately tuned", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("four target-adjoint rows reduce exactly to two first-transvectant equations", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("irreducible complex dimension-12", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all 20 fibrewise cross-fibre resonance ideals are now classified", entry["claim_boundary"])

    def test_multiplicity_two_l3_varieties_keep_spectators_and_open_extension(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_multiplicity_two_l3_zero_varieties"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("Candidates 6, 10 and 18 remain three separately tuned", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("parity-pencil square of 384", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("one spectator quartic per parity", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("irreducible complex dimension-22", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all 20 fibrewise cross-fibre resonance ideals are now classified", entry["claim_boundary"])

    def test_multiplicity_two_l4_varieties_have_four_spectator_extended_components(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_rank_one_branch_l4_zero_varieties"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("Candidates 8 and 12 remain two separately tuned", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("squared row ratios 3/40 and 120", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("four complex dimension-20 components", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("ten-dimensional spectator space", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all 20 cross-fibre ideals are now classified", entry["claim_boundary"])

    def test_regular_pencil_l4_varieties_are_non_equidimensional_and_not_extensions(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_regular_pencil_l4_zero_varieties"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("three separately tuned circumference fibres", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("positive trace, determinant and discriminant", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("exactly six real-supported linear components", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("one dimension-20", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all 20 cross-fibre ideals are now classified", entry["claim_boundary"])

    def test_candidate13_prime_ideal_has_pure_extra_taub_no_go(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_l4_incidence_reduction"]
        second = entry["mode_data"]["second_order"]
        self.assertIn("separately tuned circumference fibre", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("four distinct nonzero real generalized roots", entry["mode_data"]["lee_wald"]["statement"])
        self.assertIn("three-root cancellation witness", entry["mode_data"]["lee_wald"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("prime complex dimension-22 cone", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("splitting-jump strata are at most 20", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("only at the origin", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OBSTRUCTED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("pure-extra Taub no-go", entry["claim_boundary"])
        self.assertIn("larger mixed Einstein-extra", entry["claim_boundary"])

    def test_candidate13_mixed_null_witness_activates_same_fibre_gate(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["scope"]["m"], 0)
        self.assertIn("Einstein-minus", entry["scope"]["carrier"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("J_1,J_2,J_3", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("second-fibre-zero sheet", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("independence and activation witness", entry["claim_boundary"])

    def test_candidate13_same_fibre_census_leaves_only_zero_frequency_gate(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_same_fibre_resonance_census"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("144 exact", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("homogeneous nonzero-frequency quotient", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OPEN")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("complete nonzero-frequency same-fibre shell census", entry["claim_boundary"])
        self.assertIn("K!=0 and K=0", entry["claim_boundary"])

    def test_candidate13_mixed_witness_has_pressure_obstruction(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_mixed_bounded_extension"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("R_c is strictly negative", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("not the full candidate-13 mixed cone", entry["claim_boundary"])

    def test_candidate13_complete_mixed_cone_separates_correction_classes(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_complete_mixed_cone"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("exactly the five stabilizers plus circle pressure", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("18-coefficient prime", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("exactly {0}", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("complete real bounded-origin", entry["claim_boundary"])

    def test_candidate13_scalar_separator_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.candidate13_scalar_separation_no_go"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("strictly positive occupation coefficient", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("{0}", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_finite_generic_zero_block_is_complete_but_scoped(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.finite_generic_bounded_zero_block"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("circle pressure", entry["mode_data"]["taub_maps"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("R_c=0", second["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("nonzero-frequency resonances are excluded", entry["claim_boundary"])

    def test_nonaxisymmetric_l3_matrix_closes_basis_not_cone(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ell2_two_abs_momentum_nonaxisymmetric_l3_matrix"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("All 44 target-adjoint coefficients", entry["mode_data"]["resonance"]["statement"])
        self.assertIn("multiplicity-one V3 carrier", entry["scope"]["m"])
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("twelve nonaxisymmetric L1 coefficients", entry["claim_boundary"])

    def test_twist_aligned_phase_divisor_requires_an_independent_functional(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_resonance_gate"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("does not import the later dynamical matrix", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_twist_aligned_ell2_fixture_is_bounded_obstructed_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_bounded_obstruction"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("one tuned ell=2", entry["claim_boundary"])

    def test_symbolic_ell_qminus_self_collision_is_arithmetic_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.symbolic_ell_qminus_self_collision"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("unique q-minus self-product collision", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("dynamical two-parity matrix is certified", entry["claim_boundary"])
        self.assertIn("full bounded inversion", entry["claim_boundary"])

    def test_symbolic_ell_axial_qminus_is_obstructed_but_not_causal(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.symbolic_ell_axial_qminus_obstruction"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Polar and mixed input coefficients", entry["claim_boundary"])

    def test_two_parity_l4_null_face_does_not_claim_extension(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.opposite_momentum_ell2_parity_resonance_matrix"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_symbolic_ell_two_parity_matrix_keeps_null_sheets_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.symbolic_ell_qminus_parity_resonance_matrix"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("two coordinate planes plus two nonzero mixed-parity sheets", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_tuned_mixed_parity_face_has_one_bounded_extension(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.opposite_momentum_ell2_mixed_parity_bounded_extension"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("one tuned", entry["claim_boundary"])

    def test_symbolic_standard_branch_census_closes_only_dispersion(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.symbolic_ell_standard_branch_collision_census"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("Every q-plus-involving", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_symbolic_mixed_sheets_have_bounded_jets_not_all_orders(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.symbolic_ell_mixed_sheet_bounded_extension"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("all-orders integration", entry["claim_boundary"])

    def test_symbolic_tuned_axisymmetric_cone_is_complete_only_in_scope(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.symbolic_ell_tuned_axisymmetric_bounded_cone"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("sharp", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("multiple |k|", entry["claim_boundary"])

    def test_tuned_axisymmetric_bounded_cone_is_complete_only_in_scope(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.opposite_momentum_ell2_tuned_axisymmetric_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Extra p-primary inputs", entry["claim_boundary"])

    def test_tuned_all_primary_bounded_cone_widens_the_balance_fibre(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.opposite_momentum_ell2_tuned_all_primary_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("multiple |k|", entry["claim_boundary"])

    def test_abd_matrix_is_input_not_full_nonlinear_theorem(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.abd_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertIn("superseded", entry["claim_boundary"])

    def test_complete_homogeneous_twist_matrix_remains_precone(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")

    def test_aligned_face_has_correction_class_split(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face"]
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["second_order"]["smooth_secular"]["status"], "CERTIFIED")
        self.assertIn("all 20 C4 extra/extra bilinear generators", entry["mode_data"]["second_order"]["smooth_secular"]["statement"])
        self.assertIn("no additional off-axis branch", entry["mode_data"]["resonance"]["statement"])

    def test_finite_generic_multi_momentum_cone_is_fail_closed_by_category(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.finite_generic_all_momenta_smooth_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "OPEN")
        self.assertIn("multiple |k| fibres", second_order["smooth_secular"]["statement"])
        self.assertIn("Exceptional/global input modes", entry["claim_boundary"])

    def test_complete_finite_harmonic_cone_includes_exceptional_global_inputs(self) -> None:
        entry = self.entries["einstein.ph.wm.complete_finite_harmonic_smooth_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("complete certified linear inventory", second_order["smooth_secular"]["statement"])
        self.assertIn("P_(j,r)", entry["mode_data"]["resonance"]["statement"])

    def test_standard_global_bounded_cone_is_complete_but_scoped(self) -> None:
        entry = self.entries["einstein.ph.wm.standard.global_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("{(c,d,W_x,A)}", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("complete a/d polynomial maps", entry["claim_boundary"])
        self.assertIn("Q_e*a=0", entry["claim_boundary"])

    def test_complete_electric_wilson_transport_is_bounded_but_not_causal(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.electric_wilson_complete_oscillator_transport"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Q_e*a=0", entry["claim_boundary"])
        self.assertIn("a/d polynomial maps", entry["claim_boundary"])

    def test_circumference_column_separates_resonance_from_polynomial_growth(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.circumference_complete_oscillator_column"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("R_(j,a), not P_(j,r)", entry["mode_data"]["resonance"]["statement"])

    def test_d_column_exposes_full_time_polynomial_repair(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.d_times_ell2_extra"]
        self.assertIn("d*z2=0", entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("not a complete bounded d-column theorem", entry["claim_boundary"])
        abd = self.entries["einstein.ph.wm.interaction.abd_times_ell2_extra"]
        self.assertEqual(abd["mode_data"]["resonance"]["status"], "OPEN")
        self.assertIn("superseded", abd["claim_boundary"])

    def test_multi_ell_minus_pivots_remain_fixture_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.abd_times_generic_k0_einstein_minus_pivot_fixtures"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("symbolic functional-form or degree bound", entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"])

    def test_repaired_ad_polynomial_zero_locus_is_exact_but_pre_resonance(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.ad_ell2_extra_polynomial_zero_locus"]
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("<a*z_ax1,a*z_ax2,a*z_pol1,a*z_pol2,d*z_pol2>", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OPEN")

    def test_complete_global_ell2_extra_cone_collapses_to_standard_global(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.complete_global_ell2_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("{(c,d,W_x,A)}", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_aligned_global_minus_extra_bounded_cone_survives(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.aligned_global_axial_ell2_minus_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("x_minus=", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_global_axial_all_m_historical_cone_is_superseded(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("complete_global_twist", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("SUPERSEDED BY", entry["claim_boundary"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_global_both_parity_ell2_historical_cone_is_superseded(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_ell2_all_m_both_parity_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("historical aggregate", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("SUPERSEDED BY", entry["claim_boundary"])

    def test_complete_global_twist_ell2_cone_is_regenerated_after_projector_repair(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("c,W_x,A arbitrary", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("REGENERATED", entry["claim_boundary"])

    def test_global_fixed_ell_k0_bounded_cone_is_registered(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_fixed_ell_k0_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("c,W_x,A", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("historical A=0 restriction is superseded", entry["claim_boundary"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_fixed_ell_constant_twist_factorization_is_registered(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.fixed_ell_constant_twist_factorization"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("Q_(ell,+)=Q_(ell,-)=0", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("bounded product cone", entry["claim_boundary"])
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")

    def test_global_finite_harmonic_k0_bounded_cone_is_registered(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.global_finite_harmonic_k0_bounded_cone"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
        self.assertIn("c,W_x,A", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("Infinite completion", entry["claim_boundary"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_ad_pivots_keep_the_live_collision_open(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.exceptional_ell1_ad_resonance_pivots"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("a*t pivot", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("exceptional-times-ell2-extra", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_difference_matrix_is_sparse_and_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.exceptional_ell1_ell2_extra_difference_matrix"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertIn("six adjoint projections vanish", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertIn("all-m tensor", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_resonance_ellipse_requires_einstein_balance(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_axisymmetric_resonance_ellipse"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "OBSTRUCTED")
        self.assertIn("strictly negative", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("16*r_x^2+3*r_p^2=115*d^2", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OPEN")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_exceptional_ellipse_einstein_minus_frequency_gate_is_fail_closed(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_einstein_minus_frequency_gate"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("Forty exact algebraic comparisons", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("complete zero-frequency source cancels", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertIn("same-shell adjoint pairing", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_no_single_minus_mode_rescues_the_exceptional_ellipse(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_single_minus_dressing_no_go"]
        second_order = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertIn("every ell>=2", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second_order["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertIn("forces d=0", second_order["bounded_or_finite_quasiperiodic"]["statement"])
        self.assertEqual(second_order["smooth_secular"]["status"], "CERTIFIED")
        self.assertEqual(second_order["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_no_finite_minus_sum_rescues_the_exceptional_ellipse(self) -> None:
        entry=self.entries["einstein.ph.wm.mixed.exceptional_ellipse_finite_minus_dressing_no_go"]
        second=entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"],"OBSTRUCTED")
        self.assertIn("three-minus",entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"],"OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"],"CERTIFIED")
        self.assertEqual(second["causal_retarded"]["status"],"NO_CERTIFIED_MAP")

    def test_no_smooth_wiener_minus_sum_rescues_the_exceptional_ellipse(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_wiener_minus_dressing_no_go"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("Bohr-frequency", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_no_standard_global_data_rescue_the_exceptional_ellipse(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_standard_global_minus_no_go"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("b=B=0", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("triangular a then d pivots", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_no_ell1_oscillators_rescue_the_exceptional_ellipse(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_ell1_oscillator_minus_no_go"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("strictly negative", entry["mode_data"]["taub_maps"]["statement"])
        self.assertIn("fourteen exact", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_complete_k0_pair_to_minus_census_remains_arithmetic_only(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.complete_k0_pair_to_minus_nonresonance"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "NOT_APPLICABLE")
        self.assertEqual(
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"],
            "OPEN",
        )
        self.assertIn("k=0", entry["claim_boundary"])

    def test_complete_declared_k0_exceptional_carrier_is_obstructed(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_complete_k0_no_go"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(entry["mode_data"]["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Maximal finite-energy/Sobolev", entry["claim_boundary"])

    def test_complete_k0_no_go_extends_to_sobolev_bohr_domain(self) -> None:
        entry = self.entries["einstein.ph.wm.mixed.exceptional_ellipse_sobolev_bohr_complete_k0_no_go"]
        second = entry["mode_data"]["second_order"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertIn("s>=6", entry["mode_data"]["dispersion"]["statement"])
        self.assertIn("Bochner-Fejer", entry["mode_data"]["resonance"]["statement"])
        self.assertEqual(second["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(second["smooth_secular"]["status"], "OPEN")
        self.assertEqual(second["causal_retarded"]["status"], "NO_CERTIFIED_MAP")
        self.assertIn("Sharp energy/low-regularity", entry["claim_boundary"])

    def test_constant_twist_projector_repair_is_authoritative(self) -> None:
        entry = self.entries["einstein.ph.wm.interaction.constant_twist_ell2_projector_repair"]
        self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
        self.assertIn("*dY_21", entry["mode_data"]["resonance"]["statement"])
        bounded = entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]
        self.assertEqual(bounded["status"], "CERTIFIED")
        self.assertIn("R_A^3", bounded["statement"])
        self.assertEqual(entry["descriptions"]["causal"], "NO_CERTIFIED_MAP")

    def test_mistyped_constant_twist_rows_are_superseded(self) -> None:
        identifiers = {
            "einstein.ph.wm.interaction.constant_twist_wave_counterexample",
            "einstein.ph.wm.interaction.constant_twist_ell2_extra_position_zero_locus",
            "einstein.ph.wm.interaction.constant_twist_ell2_einstein_position_zero_locus",
            "einstein.ph.wm.interaction.constant_twist_ell2_moment_resonance_cone",
            "einstein.ph.wm.mixed.constant_twist_ell2_complete_bounded_cone",
        }
        for identifier in identifiers:
            with self.subTest(identifier=identifier):
                entry = self.entries[identifier]
                self.assertEqual(entry["descriptions"]["nonlinear"], "OBSTRUCTED")
                self.assertEqual(entry["mode_data"]["resonance"]["status"], "OBSTRUCTED")
                self.assertIn("SUPERSEDED BY", entry["claim_boundary"])

    def test_projector_dependent_successors_are_regenerated(self) -> None:
        identifiers = {
            "einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone",
            "einstein.ph.wm.mixed.twist_circumference_wilson_ell2_complete_bounded_cone",
            "einstein.ph.wm.mixed.d_twist_ell2_complete_bounded_cone",
            "einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone",
        }
        for identifier in identifiers:
            with self.subTest(identifier=identifier):
                entry = self.entries[identifier]
                self.assertEqual(entry["descriptions"]["nonlinear"], "CERTIFIED")
                self.assertEqual(entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "CERTIFIED")
                self.assertIn("REGENERATED", entry["claim_boundary"])

if __name__ == "__main__":
    unittest.main()
