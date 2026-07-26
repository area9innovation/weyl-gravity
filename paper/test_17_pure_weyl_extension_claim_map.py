#!/usr/bin/env python3
"""Regression and adversarial tests for Paper 17."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "paper/generate_17_pure_weyl_extension_claim_map.py"
VERIFIER = ROOT / "paper/verify_17_pure_weyl_extension_claim_map.py"
PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
CLAIMS = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"


class Paper17ClaimMapTests(unittest.TestCase):
    def run_verifier(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VERIFIER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def mutated_claims(self, mutate) -> Path:
        data = json.loads(CLAIMS.read_text())
        mutate(data)
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        with handle:
            json.dump(data, handle)
        return Path(handle.name)

    def assert_promotion_rejected(self, phrase: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paper = Path(directory) / "paper.tex"
            paper.write_text(PAPER.read_text() + "\n" + phrase + "\n")
            claims = json.loads(CLAIMS.read_text())
            claims["paper_sha256"] = hashlib.sha256(paper.read_bytes()).hexdigest()
            claim_path = Path(directory) / "claims.json"
            claim_path.write_text(json.dumps(claims))
            result = self.run_verifier(
                "--paper", str(paper), "--claim-map", str(claim_path)
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden promotion", result.stdout + result.stderr)

    def test_generator_and_verifier(self) -> None:
        subprocess.run(["python3", str(GENERATOR), "--check"], cwd=ROOT, check=True)
        subprocess.run(["python3", str(VERIFIER)], cwd=ROOT, check=True)

    def test_cocycle_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["bach_cocycle_normal_form"].update(
                {"q": "-I*(15*r + 13 + 12/r + 8/r**2)/(120*omega)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cocycle normal-form identity failed", result.stdout + result.stderr)

    def test_period_matrix_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"].update(
                {
                    "period_matrix": [
                        ["y1*y2", "y2**2"],
                        ["y1**2", "-y1*y2"],
                    ]
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("period matrix drift", result.stdout + result.stderr)

    def test_root_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["generalized_root"].update(
                {"carrier_quotient": "a1/b0"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root carrier quotient", result.stdout + result.stderr)

    def test_resonant_chain_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["resonant_evaluation"].update(
                {"resonance_velocity": "kappa"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("resonant evaluation chain", result.stdout + result.stderr)

    def test_mass_parameter_relation_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["critical_mass_jet"].update(
                {"parameter_relation": "m = -I*omega*tau/2"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mass-jet declaration drift", result.stdout + result.stderr)

    def test_forced_gauge_slope_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["forced_gauge_asymptotic"].update(
                {"q_slope_at_infinity": "-I/(4*omega)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gauge slope identity failed", result.stdout + result.stderr)

    def test_boundary_gauge_factor_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["boundary_transgression"].update(
                {"field_redefinition_gauge": "Q_q=Q(q)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("boundary-transgression normalization", result.stdout + result.stderr)

    def test_causal_resolvent_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the causal spacetime resolvent has a second-order pole"
        )

    def test_ringdown_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a rigorous \\(t e^{i\\omega_nt}\\) ringdown term"
        )

    def test_mass_identification_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the intrinsic radial parameter \\(\\tau\\) is the physical squared mass"
        )

    def test_physical_mass_velocity_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["resonant_evaluation"].update(
                {"physical_mass_velocity": "-2*I*kappa/omega"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("resonant evaluation chain", result.stdout + result.stderr)

    def test_endpoint_transgression_vanishing_rejected(self) -> None:
        self.assert_promotion_rejected("the endpoint transgression vanishes")

    def test_miniversal_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the physical mass deformation is a miniversal unfolding"
        )

    def test_local_contour_global_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the local two-pole contour is the full retarded solution"
        )

    def test_filtered_metric_exponent_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["filtered_unfolding"].update(
                {"positive_metric_condition_scale": "1/abs(m)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("filtered unfolding declaration", result.stdout + result.stderr)

    def test_nilpotent_pole_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["root_polarization"].update(
                {"principal_coefficient_square": "1"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nilpotent principal coefficient", result.stdout + result.stderr)

    def test_parent_mass_derivative_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["parent_mass_derivative"].update(
                {"double_coefficient": "nu*P/(4*alpha_W)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("parent mass-derivative declaration", result.stdout + result.stderr)

    def test_projected_nilpotency_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "universal_critical_resonance"
            ].update({"projected_coefficient_intrinsically_nilpotent": True})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "universal critical-resonance declaration",
            result.stdout + result.stderr,
        )

    def test_simple_pole_frequency_derivative_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["canonical_simple_pole"].update(
                {
                    "simple_coefficient": (
                        "P*A0*H+H*A0*P=-Pdot"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical simple-pole declaration", result.stdout + result.stderr)

    def test_hellmann_feynman_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "augmented_hellmann_feynman"
            ].update({"velocity": "a_m/a_omega=beta/alpha"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Hellmann-Feynman declaration", result.stdout + result.stderr)

    def test_reflection_simple_pole_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["reflection_pair"].update(
                {"simple_coefficient": "conjugate(C_minus_1)"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reflection-pair declaration", result.stdout + result.stderr)

    def test_spectral_velocity_residue_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "spectral_velocity_generator"
            ].update({"simple_qnm_residue": "kappa=I*omega_n*nu_n/2"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("spectral-velocity declaration", result.stdout + result.stderr)

    def test_selector_weighted_sum_factor_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "spectral_velocity_generator"
            ].update(
                {
                    "weighted_velocity_sum": (
                        "sum(omega_n*nu_n)=-2*I*"
                        "integral_Gamma(S)/(2*pi*I)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("spectral-velocity declaration", result.stdout + result.stderr)

    def test_semisimple_smith_branch_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "simple_qnm_first_jet_dichotomy"
            ].update(
                {
                    "zero_velocity": (
                        "nu_n=0 iff b_B(omega_n)=0 iff Smith=(0,0,2)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "simple-QNM first-jet dichotomy",
            result.stdout + result.stderr,
        )

    def test_contact_order_bound_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "critical_contact_order"
            ].update({"pole_order_bound": "p+1"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("critical contact-order", result.stdout + result.stderr)

    def test_contact_order_factorial_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "critical_contact_order"
            ].update(
                {
                    "first_visible_double_coefficient": (
                        "(-1)**q*nu_n_q*P"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("critical contact-order", result.stdout + result.stderr)

    def test_validated_multi_qnm_contour_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a validated multi-QNM selector contour has been computed"
        )

    def test_overtone_tower_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "every Schwarzschild overtone is an EP2"
        )

    def test_second_spectral_form_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "spectral_flow_forms"
            ].update(
                {
                    "theta_2_principal": (
                        "(-nu_n**2/(omega-omega_n)**2"
                        "+xi_n/(omega-omega_n))*domega"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("spectral-flow form declaration", result.stdout + result.stderr)

    def test_evans_acceleration_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["evans_acceleration"].update(
                {
                    "acceleration": (
                        "(a_mm+2*nu*a_omega_m"
                        "+nu**2*a_omega_omega)/a_omega"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Evans acceleration declaration", result.stdout + result.stderr)

    def test_second_jet_double_coefficient_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["second_critical_jet"].update(
                {"double_coefficient": "nu*Pdot+xi*P"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("second critical-jet declaration", result.stdout + result.stderr)

    def test_damped_envelope_maximum_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["damped_jordan_envelope"].update(
                {"maximum_value": "1/gamma"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("damped Jordan envelope declaration", result.stdout + result.stderr)

    def test_krein_jordan_positive_form_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["krein_jordan_geometry"].update(
                {"positive_compatible_form_exists": True}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Krein-Jordan declaration", result.stdout + result.stderr)

    def test_krein_jordan_chain_shift_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["krein_jordan_geometry"].update(
                {"chain_shift": "V1->V1-d*V0/b"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Krein-Jordan declaration", result.stdout + result.stderr)

    def test_same_sign_limit_rank_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "opposite_signature_confluence"
            ].update({"same_sign_limit_rank": 2})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("opposite-sign confluence declaration", result.stdout + result.stderr)

    def test_acceleration_contour_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a validated multi-QNM acceleration contour has been computed"
        )

    def test_global_quantum_no_go_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the Krein--Jordan theorem proves a global quantum no-go"
        )

    def test_threshold_static_residue_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "threshold_static_exactness"
            ].update(
                {
                    "q_minus_one": (
                        "-I*(15*r + 13 + 12/r + 8/r**2)/120"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("threshold static-exact", result.stdout + result.stderr)

    def test_static_laurent_compatibility_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "static_mass_direction_nontriviality"
            ].update(
                {
                    "exceptional_zero_compatibility": (
                        "Lambda**2*(Lambda-2)*a_minus_2/9"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "static mass-direction nontriviality declaration",
            result.stdout + result.stderr,
        )

    def test_static_dipole_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "static_mass_direction_nontriviality"
            ].update({"dipole_preimage": "r**2/6+r**3/15+r**4/35"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "static mass-direction nontriviality declaration",
            result.stdout + result.stderr,
        )

    def test_static_cubic_obstruction_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "static_mass_direction_nontriviality"
            ].update({"cubic_obstruction": "Lambda**2+2*Lambda-12"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "static mass-direction nontriviality declaration",
            result.stdout + result.stderr,
        )

    def test_static_preimage_promotion_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "static_mass_direction_nontriviality"
            ].update({"rational_preimage_exists": True})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "static mass-direction nontriviality declaration",
            result.stdout + result.stderr,
        )

    def test_threshold_valuation_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "threshold_static_exactness"
            ].update({"exact_threshold_valuation": 2})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("threshold static-exactness", result.stdout + result.stderr)

    def test_qnm_curvature_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "second_order_qnm_curvature"
            ].update(
                {
                    "curvature": (
                        "(2*pair(tilde_u,B*H*B*u)"
                        "+nu**2*pair(tilde_u,L2*u)"
                        "-2*nu*pair(tilde_u,A1*u))/alpha"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("second-order QNM curvature", result.stdout + result.stderr)

    def test_refined_inverse_gap_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "refined_filtered_confluence"
            ].update({"inverse_gap": "1/(nu*m)+xi/(2*nu**2)+O(m)"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refined filtered-confluence", result.stdout + result.stderr)

    def test_numerical_curvature_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a numerical value of \\(\\xi_n\\) has been computed"
        )

    def test_threshold_uniform_shear_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "a threshold-uniform estimate for \\(b/a^2\\) is established"
        )

    def test_all_ell_bach_coefficient_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the general-\\(\\ell\\) Bach coefficient "
            "\\(c_\\ell(\\omega)\\) has been computed"
        )

    def test_two_parameter_discriminant_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["two_parameter_unfolding"].update(
                {"gap_squared": "nu**2*m**2+4*c*epsilon"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("two-parameter unfolding declaration", result.stdout + result.stderr)

    def test_invariant_reverse_coefficient_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["two_parameter_unfolding"].update(
                {"c_invariant": "-2*F_epsilon/F_omega_omega"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("two-parameter unfolding declaration", result.stdout + result.stderr)

    def test_lidskii_chain_denominator_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "lidskii_reverse_coupling"
            ].update({"chain_denominator": "pair(W0,L1*V1)"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Lidskii reverse-coupling declaration", result.stdout + result.stderr)

    def test_gap_nilpotent_factor_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "gap_controlled_confluence"
            ].update({"nilpotent_limit": "Delta*(P_plus-P_minus)=N"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gap-controlled confluence declaration", result.stdout + result.stderr)

    def test_filtration_error_scale_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "filtration_error_threshold"
            ].update({"required": "abs(c*epsilon_error)<<abs(nu*m)"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("filtration-error threshold declaration", result.stdout + result.stderr)

    def test_centered_resolvent_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["two_parameter_resolvent"].update(
                {"centered_frequency": "zeta=z"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("two-parameter resolvent declaration", result.stdout + result.stderr)

    def test_physical_mixing_coefficient_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the physical filtration-breaking coefficient \\(c_n\\) has been computed"
        )

    def test_all_ell_nonsplitting_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the Bach self-extension is nonsplit for every \\(\\ell\\ge2\\)"
        )

    def test_observable_simple_coefficient_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["observable_transfer"].update(
                {
                    "simple_coefficient": (
                        "O0*G_minus_1*S0+O1*G_minus_2*S0"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observable-transfer declaration", result.stdout + result.stderr)

    def test_observable_parent_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["observable_transfer"].update(
                {
                    "parent_principal": (
                        "nu*(O0*u) tensor (tilde_u*S0)"
                        "/(4*alpha_W*alpha)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observable-transfer declaration", result.stdout + result.stderr)

    def test_detector_oscillator_power_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "real_detector_normal_form"
            ].update({"critical_equation": "Q*h=0"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "real detector normal-form declaration",
            result.stdout + result.stderr,
        )

    def test_divided_difference_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "uniform_divided_difference_template"
            ].update(
                {
                    "phi_1": (
                        "exp(I*omega_0*t)"
                        "*(1-exp(I*delta*t))/delta"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "uniform detector-template declaration",
            result.stdout + result.stderr,
        )

    def test_detector_crossover_ratio_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "uniform_divided_difference_template"
            ].update({"crossover_ratio": "eta=abs(delta)*gamma"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "uniform detector-template declaration",
            result.stdout + result.stderr,
        )

    def test_jordan_derivative_norm_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "jordan_integrated_norms"
            ].update(
                {
                    "derivative_integral": (
                        "abs(C)**2*(gamma**2+Omega**2)/(2*gamma**3)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Jordan integrated-norm declaration",
            result.stdout + result.stderr,
        )

    def test_asymptotic_overlap_promotion_rejected(self) -> None:
        self.assert_promotion_rejected("the asymptotic strain overlap is nonzero")

    def test_physical_source_overlap_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "an astrophysical source excites the adjoint QNM"
        )

    def test_detector_detectability_promotion_rejected(self) -> None:
        self.assert_promotion_rejected("detector detectability is established")

    def test_coherent_kernel_factor_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["coherent_forcing"].update(
                {
                    "critical_response": (
                        "C*F0*exp(-I*Omega_d*t)"
                        "*(1-lambda*t*exp(-lambda*t))/lambda**2"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coherent-forcing declaration", result.stdout + result.stderr)

    def test_quadratic_buildup_factor_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["coherent_forcing"].update(
                {"critical_early_tuned": "C*F0*t**2"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coherent-forcing declaration", result.stdout + result.stderr)

    def test_critical_half_power_width_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"]["coherent_forcing"].update(
                {"critical_half_power_detuning": "gamma"}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coherent-forcing declaration", result.stdout + result.stderr)

    def test_pulse_sum_terminal_power_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "phase_matched_pulses"
            ].update(
                {
                    "critical_sum": (
                        "T*q*(1-(N+1)*q**N+N*q**N)/(1-q)**2"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "phase-matched pulse declaration",
            result.stdout + result.stderr,
        )

    def test_pulse_scaling_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "phase_matched_pulses"
            ].update({"coherent_critical_scaling": "N"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "phase-matched pulse declaration",
            result.stdout + result.stderr,
        )

    def test_mode_retention_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "certified_mode_timescales"
            ].update({"one_cycle_retention_approx": "0.500"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "certified mode-timescale declaration",
            result.stdout + result.stderr,
        )

    def test_matched_drive_gamma_power_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "matched_finite_window_drive"
            ].update(
                {
                    "long_window_limit": (
                        "abs(C)*sqrt(E)/(2*gamma**2)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "matched finite-window drive declaration",
            result.stdout + result.stderr,
        )

    def test_matched_drive_conjugation_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "matched_finite_window_drive"
            ].update({"optimizer": "g_W(T-s)"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "matched finite-window drive declaration",
            result.stdout + result.stderr,
        )

    def test_global_coherent_kernel_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the isolated critical kernel is the complete causal "
            "Schwarzschild Green function"
        )

    def test_log_partner_radial_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "quasinormal_logarithmic_partner"
            ].update(
                {
                    "bach_relative_tangent": (
                        "-I*kappa_n*u_sigma-sigma*r/4+O(1)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "logarithmic-partner declaration drift",
            result.stdout + result.stderr,
        )

    def test_log_partner_literal_log_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "quasinormal_logarithmic_partner"
            ].update({"literal_radial_logarithm": True})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "logarithmic-partner declaration drift",
            result.stdout + result.stderr,
        )

    def test_log_partner_jordan_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "qnm_jordan_time_law"
            ].update(
                {
                    "evolution": (
                        "exp(I*H*t)*V1=exp(I*omega_n*t)*(V1-I*t*V0)"
                    )
                }
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Jordan declaration drift",
            result.stdout + result.stderr,
        )

    def test_log_partner_metric_falloff_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the generalized Weyl metric has standard "
            "asymptotic-flatness falloff"
        )

    def test_log_partner_physical_source_overlap_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the plunging-particle source overlap is certified nonzero"
        )

    def test_null_infinity_bondi_shear_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "null_infinity_reconstruction"
            ].update({"Einstein_Bondi_shear": "2*I*X_AB/omega"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "null-infinity reconstruction declaration drift",
            result.stdout + result.stderr,
        )

    def test_conserved_source_sign_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "conserved_traceless_source"
            ].update({"P_r": "-mu*F/(2*I*omega*r*f)"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "conserved-source declaration drift",
            result.stdout + result.stderr,
        )

    def test_total_coulomb_derivative_mutation_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["exact_identities"][
                "quasinormal_logarithmic_partner"
            ].update({"total_coulomb_log_coefficient": "0"})
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "logarithmic-partner declaration drift",
            result.stdout + result.stderr,
        )

    def test_log_partner_absolute_priority_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "this is the first asymptotically flat black-hole "
            "logarithmic graviton"
        )

    def test_energy_budget_promotion_rejected(self) -> None:
        self.assert_promotion_rejected(
            "the coefficient-space budget is invariant gravitational energy"
        )

    def test_fail_closed_claim_flag_rejected(self) -> None:
        path = self.mutated_claims(
            lambda data: data["fail_closed_scope"].update(
                {"causal_exterior_spacetime_resolvent": True}
            )
        )
        try:
            result = self.run_verifier("--claim-map", str(path))
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fail-closed promotion", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
