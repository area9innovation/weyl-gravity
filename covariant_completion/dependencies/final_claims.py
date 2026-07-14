"""Assemble the final covariant theorem claims from atomic certificates.

This module is deliberately an *aggregator*, not another proof engine.  The
atomic verifier scripts establish the symbol, Fourier-complex, pairing, and
residual facts and emit machine-readable certificates.  Here those facts are
loaded, schema-checked, and combined in a directed acyclic graph.  A derived
claim is true if and only if every declared dependency is true.

The three theorem-boundary lemmas are kept visible as named nodes:

``curved_operator_identity``
    Exact curved ``Q^2=0`` and ``QW+WQ=P`` identities.
``curved_deformation_retract``
    Exact curved chain maps and deformation-retract identity.
``curved_current_comparison``
    Exact auxiliary Green current, Cauchy current, and metric pullback.

No downstream claim can become true while any required node remains false.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


COVARIANT_ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE_DIR = COVARIANT_ROOT / "certificates"
ANALYTIC_CERTIFICATE_DIR = COVARIANT_ROOT.parent / "analytic_completion" / "certificates"


@dataclass(frozen=True)
class ClaimNode:
    """One atomic or derived claim in the certification graph."""

    name: str
    status: bool
    classification: str
    requires: tuple[str, ...] = ()
    dependency_mode: str = "all"
    evidence: tuple[str, ...] = ()
    note: str = ""

    def certificate(self, blockers: tuple[str, ...]) -> dict[str, object]:
        return {
            "status": self.status,
            "classification": self.classification,
            "requires": list(self.requires),
            "dependency_mode": self.dependency_mode,
            "blocking_dependencies": list(blockers),
            "evidence": list(self.evidence),
            "note": self.note,
        }


def _load_from(directory: Path, name: str, schema: str) -> Mapping[str, Any]:
    path = directory / name
    if not path.is_file():
        raise AssertionError(f"missing dependency certificate: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != schema:
        raise AssertionError(
            f"certificate schema mismatch for {name}: "
            f"{payload.get('schema')!r} != {schema!r}"
        )
    return payload


def _load(name: str, schema: str) -> Mapping[str, Any]:
    return _load_from(CERTIFICATE_DIR, name, schema)


@dataclass(frozen=True)
class FinalClaimDependencyReport:
    """Validated claim DAG for the completed covariant theorem."""

    nodes: Mapping[str, ClaimNode]
    theorem_boundary_lemmas: tuple[str, ...]

    @staticmethod
    def build() -> "FinalClaimDependencyReport":
        curved_operator = _load(
            "curved_operator_identity_status.json",
            "pure-weyl-curved-operator-identity-status-v2",
        )
        curved_null_obstruction = _load(
            "curved_null_symbol_rank_obstruction.json",
            "pure-weyl-curved-null-symbol-rank-obstruction-v1",
        )
        curvature_prolongation = _load(
            "curved_curvature_prolongation_status.json",
            "pure-weyl-curvature-prolongation-status-v1",
        )
        curvature_evolution_symbol = _load(
            "curved_curvature_evolution_principal_symbol.json",
            "pure-weyl-curvature-evolution-principal-symbol-v1",
        )
        wave_symbols = _load(
            "degreewise_wave_symbols.json",
            "pure-weyl-degreewise-wave-symbols-v1",
        )
        curved_retract_status = _load(
            "curved_deformation_retract_status.json",
            "pure-weyl-curved-deformation-retract-status-v1",
        )
        curved_chain_maps = _load(
            "curved_chain_maps.json",
            "pure-weyl-curved-chain-map-status-v1",
        )
        curved_retract_identity = _load(
            "curved_retract_identity.json",
            "pure-weyl-curved-retract-identity-status-v1",
        )
        curved_support = _load(
            "curved_support_preservation.json",
            "pure-weyl-curved-retract-support-v1",
        )
        curved_current = _load(
            "curved_current_comparison.json",
            "pure-weyl-curved-current-comparison-status-v1",
        )
        curved_potentials = _load(
            "curved_presymplectic_potentials.json",
            "pure-weyl-curved-presymplectic-potential-status-v1",
        )
        curved_improvement = _load(
            "curved_current_improvement.json",
            "pure-weyl-curved-current-improvement-status-v1",
        )
        curved_cauchy = _load(
            "curved_cauchy_current.json",
            "pure-weyl-curved-cauchy-current-status-v1",
        )
        curved_green_current = _load(
            "curved_green_current_pairing.json",
            "pure-weyl-curved-green-current-pairing-status-v1",
        )
        curved_eal = _load(
            "curved_EAL_pairing_regression.json",
            "pure-weyl-curved-EAL-pairing-regression-v1",
        )
        recognition = _load(
            "green_operator_chain_compatibility.json",
            "pure-weyl-green-witness-recognition-v1",
        )
        residual = _load(
            "residual_bfv_comparison.json",
            "pure-weyl-covariant-residual-cutoff-recovery-v1",
        )
        energy_h4 = _load_from(
            ANALYTIC_CERTIFICATE_DIR,
            "completed_H4.json",
            "pure-weyl-completed-residual-cohomology-v1",
        )
        energy_gram = _load_from(
            ANALYTIC_CERTIFICATE_DIR,
            "completed_gram.json",
            "pure-weyl-completed-gram-v1",
        )

        nodes: dict[str, ClaimNode] = {}

        def atomic(
            name: str,
            status: bool,
            classification: str,
            evidence: tuple[str, ...],
            note: str,
        ) -> None:
            nodes[name] = ClaimNode(
                name=name,
                status=bool(status),
                classification=classification,
                evidence=evidence,
                note=note,
            )

        def derived(
            name: str,
            requires: tuple[str, ...],
            classification: str,
            note: str,
        ) -> None:
            missing = [dependency for dependency in requires if dependency not in nodes]
            if missing:
                raise AssertionError(f"{name} has undefined dependencies: {missing}")
            nodes[name] = ClaimNode(
                name=name,
                status=all(nodes[dependency].status for dependency in requires),
                classification=classification,
                requires=requires,
                note=note,
            )

        # Implemented structural facts.
        atomic(
            "degreewise_wave_symbols",
            bool(wave_symbols["verified"])
            and not bool(
                curved_operator["scalar_wave_realization"][
                    "curved_scalar_wave_no_go"
                ]
            ),
            "open_curved_obligation",
            (
                "degreewise_wave_symbols.json",
                "curved_null_symbol_rank_obstruction.json",
            ),
            "The flat symbols are scalar metric, but the current curved 24-field scalar-symbol completion is exactly obstructed.",
        )
        atomic(
            "curved_auxiliary_hessian_exact",
            bool(curved_operator["promotion_flags"]["curved_hessian_expanded"]),
            "implemented_structural_fact",
            (
                "curved_auxiliary_hessian.json",
                "curved_hessian_coefficient_table.json",
            ),
            "The complete action-derived curved Hessian table is exact, formally adjoint, and has 630/630 high-order jet coverage.",
        )
        atomic(
            "scalar_wave_witness_no_go",
            not bool(
                curved_null_obstruction[
                    "pointwise_pairing_companion_solution_exists"
                ]
            )
            and int(curved_null_obstruction["exact_hessian_rank"]) == 11
            and int(curved_null_obstruction["exact_gauge_rank"]) == 9,
            "implemented_negative_theorem",
            ("curved_null_symbol_rank_obstruction.json",),
            "At a null covector rank(E_2)=11>rank(K_1)=9, ruling out every pointwise-pairing/first-order-companion scalar witness for the present E and K.",
        )
        atomic(
            "physical_symbol_quotient_exact",
            int(
                curved_null_obstruction["fixed_action_field_operator_quotient"]
                ["image_N_mod_image_K_dimension"]
            )
            == 2,
            "implemented_structural_fact",
            ("curved_null_symbol_rank_obstruction.json",),
            "The normalized Hessian image modulo the gauge image is exactly two-dimensional.",
        )
        atomic(
            "physical_symbol_is_helicity_two",
            "helicity-2"
            in str(
                curved_null_obstruction["fixed_action_field_operator_quotient"][
                    "channel"
                ]
            ),
            "implemented_structural_fact",
            ("curved_null_symbol_rank_obstruction.json",),
            "The two quotient directions are the real helicity-two pair transverse to the null direction.",
        )
        atomic(
            "weyl_symbol_helicity_isomorphism",
            bool(curvature_prolongation["weyl_symbol_helicity_isomorphism"]),
            "implemented_structural_fact",
            ("curved_curvature_prolongation_status.json",),
            "On the exact Hessian-reduced physical quotient, the linearized Weyl symbol is an isomorphism onto the two helicity-two curvature directions.",
        )
        atomic(
            "curved_EB_equations",
            bool(curvature_prolongation["curved_EB_equations"]),
            "open_analytic_obligation",
            ("curved_curvature_prolongation_status.json",),
            "Derive the complete electric/magnetic Weyl equations from the curved linearized Bianchi/Cotton and Bach identities.",
        )
        atomic(
            "curved_EB_symmetric_hyperbolicity",
            bool(curvature_prolongation["curved_EB_symmetric_hyperbolicity"]),
            "open_analytic_obligation",
            ("curved_curvature_prolongation_status.json",),
            "Identify the actual curved E/B coefficient matrices and prove the positive STF form symmetrizes them.",
        )
        atomic(
            "curved_constraint_propagation",
            bool(curvature_prolongation["curved_constraint_propagation"]),
            "open_analytic_obligation",
            ("curved_curvature_prolongation_status.json",),
            "Derive the complete homogeneous curved evolution of every E/B constraint.",
        )
        atomic(
            "support_local_prolongation_retract",
            bool(curvature_prolongation["support_local_prolongation_retract"]),
            "open_analytic_obligation",
            ("curved_curvature_prolongation_status.json",),
            "Construct the local Psi-W(h) prolongation equivalence without inverse curl, Laplacian, or helicity projector.",
        )
        atomic(
            "curvature_causal_green_operators",
            bool(curvature_prolongation["curvature_causal_green_operators"]),
            "open_analytic_obligation",
            ("curved_curvature_prolongation_status.json",),
            "Construct retarded and advanced operators for the exact constrained curvature system and assemble the full BV blocks.",
        )
        atomic(
            "candidate_curvature_principal_symmetric_hyperbolicity",
            bool(
                curvature_evolution_symbol[
                    "candidate_curvature_principal_symmetric_hyperbolicity"
                ]
            ),
            "implemented_structural_fact",
            ("curved_curvature_evolution_principal_symbol.json",),
            "The candidate electric/magnetic Weyl principal block has a positive symmetrizer and the two physical characteristic speeds in each direction; derivation from the curved prolonged equations remains open.",
        )
        atomic(
            "candidate_curvature_principal_constraints_propagate",
            bool(
                curvature_evolution_symbol[
                    "candidate_curvature_principal_constraints_propagate"
                ]
            ),
            "implemented_structural_fact",
            ("curved_curvature_evolution_principal_symbol.json",),
            "The principal divergence constraints close through div(curl_2 h)=(1/2)curl_1(div h).",
        )
        atomic(
            "support_preservation",
            bool(curved_support["compact_support_preserved"])
            and bool(curved_support["spacelike_compact_support_preserved"])
            and bool(curved_support["smooth_global_support_preserved"]),
            "implemented_structural_fact",
            ("curved_support_preservation.json",),
            "The displayed finite differential and pointwise maps do not enlarge support.",
        )
        atomic(
            "green_witness_recognition_theorem",
            recognition["green_homotopies"]["identity"]
            == "Q Lambda_plus/minus+Lambda_plus/minus Q=1",
            "implemented_structural_fact",
            ("green_operator_chain_compatibility.json",),
            "Formal Green consequences hold once the curved witness hypotheses hold.",
        )
        atomic(
            "compact_cylinder_spacelike_support",
            bool(
                recognition["cylinder_specialization"][
                    "Gamma_sc_equals_Gamma_smooth"
                ]
            ),
            "implemented_structural_fact",
            ("compact_to_global_quasi_isomorphism.json",),
            "On R x S^3 every smooth section is spacelike compact.",
        )
        atomic(
            "EAL_pairing_regression",
            bool(curved_eal["verified"]),
            "implemented_structural_fact",
            ("curved_EAL_pairing_regression.json",),
            "The reduced physical current has the certified +E,-A,-L normalization.",
        )
        atomic(
            "ckv_cutoff_identity",
            residual["ghost_classes"]["causal_recovery"] == "[Lambda j_a]=[xi_a]"
            and int(residual["ghost_classes"]["rank"]) == 15,
            "implemented_structural_fact",
            ("residual_bfv_comparison.json",),
            "The cutoff-source identity recovers all fifteen modes once Lambda exists.",
        )
        atomic(
            "algebraic_residual_no_duplication",
            int(residual["bfv_replacement"]["one_residual_ghost_copy"]) == 15
            and int(residual["bfv_replacement"]["one_bfv_momentum_copy"]) == 15
            and bool(
                residual["bfv_replacement"][
                    "moment_map_is_a_function_not_an_extra_coordinate"
                ]
            ),
            "implemented_structural_fact",
            ("residual_no_duplication.json",),
            "The algebraic BFV replacement contains one ghost and one momentum copy.",
        )
        atomic(
            "energy_H4_is_C2",
            bool(energy_h4["completed_centered_equals_algebraic_centered"])
            and list(energy_h4["centered"]["classes"]) == ["W_+^2", "W_-^2"]
            and int(energy_h4["centered"]["two_particle_H4"]) == 2,
            "implemented_structural_fact",
            ("analytic_completion/certificates/completed_H4.json",),
            "The completed energy-mode centered cohomology is the certified two-class space.",
        )
        atomic(
            "energy_gram_is_I2",
            list(energy_gram["completed_gram"]) == [[1, 0], [0, 1]],
            "implemented_structural_fact",
            ("analytic_completion/certificates/completed_gram.json",),
            "The completed energy-mode cohomological Gram matrix is I_2.",
        )
        atomic(
            "curved_action_and_gauge_map",
            bool(curved_operator["exact_inputs_now"]["nonlinear_covariant_action"])
            and bool(curved_operator["exact_inputs_now"]["linearized_curved_gauge_map"])
            and bool(
                curved_operator["exact_inputs_now"][
                    "background_auxiliary_Lie_derivative_included"
                ]
            ),
            "implemented_structural_fact",
            (
                "curved_auxiliary_action_definition.json",
                "curved_operator_identity_status.json",
            ),
            "The exact covariant action and its curved 24-by-9 gauge map are instantiated.",
        )
        atomic(
            "parallel_curvature_derivative_normal_form",
            bool(
                curved_operator["exact_inputs_now"][
                    "parallel_curvature_derivative_normal_form"
                ]
            ),
            "implemented_structural_fact",
            ("curved_derivative_normal_form.json",),
            "Covariant derivative words reduce canonically using the parallel cylinder curvature.",
        )
        atomic(
            "curved_auxiliary_shift_is_BV_canonical",
            bool(
                curved_retract_status["promotion_criteria"][
                    "curved_shift_is_BV_canonical"
                ]
            ),
            "implemented_structural_fact",
            ("curved_auxiliary_canonical_split.json",),
            "The nonlinear completion-of-square shift has its exact local cotangent lift.",
        )
        atomic(
            "universal_post_shift_auxiliary_SDR",
            bool(
                curved_retract_status["proved"][
                    "universal_post_shift_36_dimensional_SDR"
                ]
            ),
            "implemented_structural_fact",
            ("curved_deformation_retract_status.json",),
            "The universal 36-dimensional shifted auxiliary cotangent summand contracts exactly.",
        )
        atomic(
            "exact_action_Fourier_current_improvement",
            bool(curved_current["exact_action_Fourier_current"])
            and bool(curved_current["exact_polynomial_improvement"]),
            "implemented_structural_fact",
            (
                "curved_action_current_comparison.json",
                "curved_current_improvement.json",
            ),
            "The action-level Fourier currents differ by an explicit antisymmetric improvement.",
        )

        # Atomic curved obligations. Each is read from its owning certificate;
        # no status is pinned false or promoted manually here.
        atomic(
            "curved_hessian_expanded",
            bool(curved_operator["promotion_criteria"]["curved_hessian_expanded"]),
            "open_curved_obligation",
            ("curved_operator_identity_status.json",),
            "Differentiate the exact covariant action to emit the complete curved auxiliary Hessian.",
        )
        atomic(
            "curved_companion_expanded",
            bool(curved_operator["promotion_criteria"]["curved_companion_expanded"]),
            "open_curved_obligation",
            ("curved_operator_identity_status.json",),
            "Emit the complete curved gauge companion from the exact gauge-fixing density.",
        )
        atomic(
            "curved_Q_nilpotency",
            curved_operator["promotion_criteria"]["curved_Q_squared"] == "zero",
            "open_curved_obligation",
            ("curved_operator_identity_status.json",),
            "Expand the curved four-row Q and exhaust its squared defect in canonical normal form.",
        )
        atomic(
            "curved_witness_identity",
            curved_operator["promotion_criteria"]["curved_QW_plus_WQ_minus_P"]
            == "zero",
            "open_curved_obligation",
            ("curved_operator_identity_status.json",),
            str(curved_operator["next_exact_step"]),
        )
        atomic(
            "curved_formal_adjointness",
            all(
                curved_operator["promotion_criteria"][name] == "zero"
                for name in (
                    "curved_field_adjoint_defect",
                    "curved_ghost_adjoint_defect",
                    "curved_witness_adjoint_defect",
                )
            ),
            "open_curved_obligation",
            ("curved_operator_identity_status.json",),
            "Evaluate every covariant integration-by-parts adjoint defect after the lower terms are emitted.",
        )
        atomic(
            "curved_globalization_coverage",
            curved_operator["promotion_criteria"]["globalization_coverage"]
            == "complete",
            "open_curved_obligation",
            ("curved_globalization.json", "curved_operator_identity_status.json"),
            "Exhaust every required curved jet fibre and isotropy component before globalizing the operator identity.",
        )
        atomic(
            "curved_metric_to_aux_chain_map",
            bool(curved_chain_maps["curved_i_is_chain_map"]),
            "open_curved_obligation",
            ("curved_chain_maps.json",),
            "Instantiate the metric-to-auxiliary chain map with all curved lower terms.",
        )
        atomic(
            "curved_aux_to_metric_chain_map",
            bool(curved_chain_maps["curved_p_is_chain_map"]),
            "open_curved_obligation",
            ("curved_chain_maps.json",),
            "Instantiate the auxiliary-to-metric chain map with all curved lower terms.",
        )
        atomic(
            "curved_retract_identity",
            bool(
                curved_retract_identity[
                    "actual_curved_i_p_minus_identity_equals_Qk_plus_kQ"
                ]
            ),
            "open_curved_obligation",
            ("curved_retract_identity.json",),
            "Verify pi=1 and ip-1=Qk+kQ for the actual covariant operators.",
        )
        atomic(
            "curved_Q_conjugation",
            bool(
                curved_retract_status["promotion_criteria"][
                    "actual_curved_Q_conjugation_verified"
                ]
            ),
            "open_curved_obligation",
            ("curved_deformation_retract_status.json",),
            "Conjugate the complete curved four-row Q by the local BV-canonical transformation.",
        )
        atomic(
            "curved_all_BV_rows",
            bool(
                curved_retract_status["promotion_criteria"][
                    "all_full_BV_rows_included"
                ]
            )
            and bool(curved_chain_maps["all_BV_rows_in_curved_comparison"]),
            "open_curved_obligation",
            (
                "curved_deformation_retract_status.json",
                "curved_chain_maps.json",
            ),
            "Reattach and verify every trace, antifield, ghost, and nonminimal curved row.",
        )
        atomic(
            "curved_auxiliary_presymplectic_potential",
            bool(curved_potentials["auxiliary_curved_potential_emitted"]),
            "open_curved_obligation",
            ("curved_presymplectic_potentials.json",),
            "Derive the complete curved auxiliary presymplectic potential from the exact action.",
        )
        atomic(
            "curved_metric_presymplectic_potential",
            bool(curved_potentials["metric_curved_potential_emitted"]),
            "open_curved_obligation",
            ("curved_presymplectic_potentials.json",),
            "Derive the complete curved fourth-order metric presymplectic potential.",
        )
        atomic(
            "curved_auxiliary_metric_current_identity",
            bool(curved_improvement["curved_d_plus_Q_identity"]),
            "open_curved_obligation",
            ("curved_current_improvement.json",),
            "Verify j_aux-j_metric=db+Qc with all cylinder lower terms.",
        )
        atomic(
            "curved_cauchy_boundary_current",
            bool(curved_cauchy["curved_slab_current_derived"]),
            "open_curved_obligation",
            ("curved_cauchy_current.json",),
            "Derive the exact slab current and prove equality on cohomology.",
        )
        atomic(
            "curved_green_current",
            bool(curved_green_current["Green_pairing_equals_current_pairing"]),
            "open_curved_obligation",
            ("curved_green_current_pairing.json",),
            "Prove equality of the causal Green pairing and the current pairing.",
        )

        # The three explicit theorem-boundary lemmas.
        derived(
            "curved_operator_identity",
            (
                "curved_hessian_expanded",
                "curved_companion_expanded",
                "curved_Q_nilpotency",
                "curved_witness_identity",
                "curved_formal_adjointness",
                "curved_globalization_coverage",
            ),
            "theorem_boundary_lemma",
            "Exact curved Q^2=0 and QW+WQ=P identities, including the covariant adjoint check; this no longer asserts an impossible scalar wave symbol.",
        )
        derived(
            "degreewise_normal_hyperbolicity",
            ("curved_operator_identity", "degreewise_wave_symbols"),
            "superseded_analytic_claim",
            "Retained as a negative legacy diagnostic: the exact null-symbol theorem rules out this route for the current bundle.",
        )
        derived(
            "support_preserving_retract",
            (
                "curved_auxiliary_shift_is_BV_canonical",
                "universal_post_shift_auxiliary_SDR",
                "curved_metric_to_aux_chain_map",
                "curved_aux_to_metric_chain_map",
                "curved_retract_identity",
                "curved_Q_conjugation",
                "curved_all_BV_rows",
                "support_preservation",
            ),
            "implemented_structural_fact",
            "The complete all-row curved SDR is local and support preserving, independently of the Green realization.",
        )
        derived(
            "curvature_prolonged_complex_exact",
            (
                "curved_EB_equations",
                "curved_constraint_propagation",
                "support_local_prolongation_retract",
            ),
            "open_analytic_obligation",
            "The exact local curvature-prolonged complex includes its equations, homogeneous constraints, and support-local equivalence.",
        )
        derived(
            "curvature_green_realization",
            (
                "curvature_prolonged_complex_exact",
                "curved_EB_symmetric_hyperbolicity",
                "curvature_causal_green_operators",
            ),
            "open_analytic_obligation",
            "The selected Green realization is the exact constrained symmetric-hyperbolic Weyl-curvature system.",
        )
        derived(
            "complete_bv_green_hyperbolicity",
            (
                "curved_auxiliary_hessian_exact",
                "support_preserving_retract",
                "curvature_green_realization",
                "curved_Q_nilpotency",
                "curved_witness_identity",
                "curved_formal_adjointness",
            ),
            "derived_analytic_claim",
            "The exact BV complex has causal Green operators through the selected Weyl-curvature prolongation.",
        )
        derived(
            "green_homotopies",
            ("complete_bv_green_hyperbolicity", "green_witness_recognition_theorem"),
            "derived_analytic_claim",
            "Retarded and advanced Green homotopies for the full auxiliary BV complex.",
        )
        derived(
            "curved_deformation_retract",
            ("support_preserving_retract",),
            "theorem_boundary_lemma",
            "Exact curved inclusion, projection, and homotopy identities in every support category.",
        )
        derived(
            "curved_current_comparison",
            (
                "curved_auxiliary_shift_is_BV_canonical",
                "exact_action_Fourier_current_improvement",
                "curved_auxiliary_presymplectic_potential",
                "curved_metric_presymplectic_potential",
                "curved_cauchy_boundary_current",
                "curved_auxiliary_metric_current_identity",
                "EAL_pairing_regression",
            ),
            "theorem_boundary_lemma",
            "Exact off-shell d+Q, Cauchy, and auxiliary-to-metric current comparison; Green pairing transport is gated separately.",
        )
        derived(
            "compact_to_global_quasi_isomorphism",
            ("green_homotopies", "compact_cylinder_spacelike_support"),
            "derived_analytic_claim",
            "Causal compact-to-spacelike-compact theorem specialized to global cylinder sections.",
        )
        derived(
            "causal_quasi_isomorphism",
            ("compact_to_global_quasi_isomorphism",),
            "derived_analytic_claim",
            "The causal Green map is the compact-to-global quasi-isomorphism on R x S^3.",
        )
        derived(
            "support_preserving_metric_equivalence",
            ("curved_deformation_retract", "support_preservation"),
            "derived_analytic_claim",
            "The original fourth-order and auxiliary BV complexes are locally equivalent in support categories.",
        )
        derived(
            "pairing_compatibility",
            (
                "curved_current_comparison",
                "green_homotopies",
                "curved_green_current",
                "EAL_pairing_regression",
            ),
            "derived_analytic_claim",
            "The covariant causal, Cauchy, and energy-mode pairings agree on cohomology.",
        )
        derived(
            "CKV_recovery",
            ("green_homotopies", "ckv_cutoff_identity"),
            "derived_analytic_claim",
            "The causal map realizes the fifteen cutoff sources as the global CKV classes.",
        )
        derived(
            "residual_no_duplication",
            (
                "support_preserving_metric_equivalence",
                "CKV_recovery",
                "algebraic_residual_no_duplication",
            ),
            "derived_analytic_claim",
            "Auxiliary enlargement, causal recovery, and BFV replacement preserve one residual copy.",
        )
        derived(
            "final_covariant_H4",
            (
                "curved_operator_identity",
                "curved_deformation_retract",
                "curved_current_comparison",
                "curved_EB_equations",
                "curved_EB_symmetric_hyperbolicity",
                "curved_constraint_propagation",
                "support_local_prolongation_retract",
                "curvature_causal_green_operators",
                "causal_quasi_isomorphism",
                "CKV_recovery",
                "residual_no_duplication",
                "energy_H4_is_C2",
                "energy_gram_is_I2",
            ),
            "terminal_theorem_claim",
            "Transport of the certified two-class H4 and Gram I2 through the covariant chain.",
        )

        result = FinalClaimDependencyReport(
            nodes=nodes,
            theorem_boundary_lemmas=(
                "curved_operator_identity",
                "curved_deformation_retract",
                "curved_current_comparison",
            ),
        )
        result.verify()
        return result

    def _blocking_atomic_dependencies(self, name: str) -> tuple[str, ...]:
        node = self.nodes[name]
        if node.status:
            return ()
        if not node.requires:
            return (name,)
        blockers: list[str] = []
        for dependency in node.requires:
            blockers.extend(self._blocking_atomic_dependencies(dependency))
        return tuple(dict.fromkeys(blockers))

    def verify(self) -> None:
        for name, node in self.nodes.items():
            if name != node.name:
                raise AssertionError(f"claim key/name mismatch: {name} != {node.name}")
            for dependency in node.requires:
                if dependency not in self.nodes:
                    raise AssertionError(f"{name} requires missing claim {dependency}")
            if node.requires:
                if node.dependency_mode == "all":
                    expected = all(
                        self.nodes[dependency].status for dependency in node.requires
                    )
                elif node.dependency_mode == "any":
                    expected = any(
                        self.nodes[dependency].status for dependency in node.requires
                    )
                else:
                    raise AssertionError(
                        f"unknown dependency mode for {name}: {node.dependency_mode}"
                    )
                if node.status != expected:
                    raise AssertionError(
                        f"derived claim {name}={node.status} but dependencies imply {expected}"
                    )

        # Depth-first cycle check.
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                raise AssertionError(f"claim dependency cycle at {name}")
            if name in visited:
                return
            visiting.add(name)
            for dependency in self.nodes[name].requires:
                visit(dependency)
            visiting.remove(name)
            visited.add(name)

        for name in self.nodes:
            visit(name)

        expected_boundary = {
            "curved_operator_identity",
            "curved_deformation_retract",
            "curved_current_comparison",
        }
        if set(self.theorem_boundary_lemmas) != expected_boundary:
            raise AssertionError("the declared curved theorem boundary changed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        claims = {
            name: node.certificate(self._blocking_atomic_dependencies(name))
            for name, node in self.nodes.items()
        }
        implemented = [name for name, node in self.nodes.items() if node.status]
        open_claims = [name for name, node in self.nodes.items() if not node.status]
        return {
            "schema": "pure-weyl-final-covariant-claim-dependencies-v1",
            "policy": (
                "derived claims use their declared all/any dependency mode; "
                "atomic statuses are read from owning certificates"
            ),
            "summary": {
                "implemented_or_derived_true": len(implemented),
                "open_or_blocked": len(open_claims),
                "complete_bv_green_hyperbolicity": self.nodes[
                    "complete_bv_green_hyperbolicity"
                ].status,
                "support_preserving_metric_equivalence": self.nodes[
                    "support_preserving_metric_equivalence"
                ].status,
                "pairing_compatibility": self.nodes["pairing_compatibility"].status,
                "energy_H4_is_C2": self.nodes["energy_H4_is_C2"].status,
                "energy_gram_is_I2": self.nodes["energy_gram_is_I2"].status,
                "final_covariant_H4": self.nodes["final_covariant_H4"].status,
            },
            "theorem_boundary_lemmas": {
                name: claims[name] for name in self.theorem_boundary_lemmas
            },
            "top_level_theorem_boundary_blockers": [
                name
                for name in self.theorem_boundary_lemmas
                if not self.nodes[name].status
            ],
            "claims": claims,
            "final_claim_atomic_blockers": list(
                self._blocking_atomic_dependencies("final_covariant_H4")
            ),
            "curvature_propagation_gate": {
                "status": self.nodes["curvature_green_realization"].status,
                "required_atomic_flags": [
                    "curved_EB_equations",
                    "curved_EB_symmetric_hyperbolicity",
                    "curved_constraint_propagation",
                    "support_local_prolongation_retract",
                    "curvature_causal_green_operators",
                ],
                "blocking_dependencies": list(
                    self._blocking_atomic_dependencies(
                        "curvature_green_realization"
                    )
                ),
            },
            "honest_status": (
                "The curved operator, deformation retract, current comparison, "
                "and final covariant H4 transport are certified."
                if self.nodes["final_covariant_H4"].status
                else "The algebraic/structural scaffold is certified. The final "
                "covariant H4 transport remains false exactly where the reported "
                "curved atomic dependencies remain open."
            ),
        }

    def markdown(self) -> str:
        certificate = self.certificate()
        lines = [
            "# Final covariant claim dependency report",
            "",
            "This report is generated from the atomic certificates. Each derived claim",
            "uses its displayed all/any dependency mode.",
            "",
            "## Dependency flow",
            "",
            "```mermaid",
            "flowchart TD",
            "  A[curved_operator_identity] --> F[final_covariant_H4]",
            "  E[curved_EB_equations] --> F",
            "  H[curved_EB_symmetric_hyperbolicity] --> F",
            "  Q[curved_constraint_propagation] --> F",
            "  P[support_local_prolongation_retract] --> F",
            "  G[curvature_causal_green_operators] --> F",
            "  R[curved_deformation_retract] --> F[final_covariant_H4]",
            "  C[curved_current_comparison] --> F",
            "```",
            "",
            "## Theorem boundary",
            "",
            "| Curved lemma | Status | Direct requirements |",
            "| --- | --- | --- |",
        ]
        for name in self.theorem_boundary_lemmas:
            node = self.nodes[name]
            requirements = ", ".join(f"`{item}`" for item in node.requires)
            lines.append(f"| `{name}` | **{str(node.status).lower()}** | {requirements} |")
        lines.extend(
            [
                "",
                "## Final claims",
                "",
                "| Claim | Status | Requires |",
                "| --- | --- | --- |",
            ]
        )
        final_names = (
            "complete_bv_green_hyperbolicity",
            "support_preserving_metric_equivalence",
            "pairing_compatibility",
            "causal_quasi_isomorphism",
            "CKV_recovery",
            "residual_no_duplication",
            "energy_H4_is_C2",
            "energy_gram_is_I2",
            "final_covariant_H4",
        )
        for name in final_names:
            node = self.nodes[name]
            requirements = ", ".join(f"`{item}`" for item in node.requires)
            lines.append(f"| `{name}` | **{str(node.status).lower()}** | {requirements} |")
        lines.extend(
            [
                "",
                "## Implemented scaffold",
                "",
            ]
        )
        for name, node in self.nodes.items():
            if node.status and node.classification == "implemented_structural_fact":
                lines.append(f"- `{name}` — {node.note}")
        lines.extend(
            [
                "",
                "## Remaining curvature-propagation theorem",
                "",
                "The selected final gate is the constrained symmetric-hyperbolic",
                "Weyl-curvature realization. The reduced Weyl-symbol theorem and the",
                "candidate principal matrix/constraint algebra are true; the five",
                "displayed curved realization flags remain open.",
                "",
            ]
        )
        for name in certificate["final_claim_atomic_blockers"]:
            lines.append(f"- `{name}` — {self.nodes[name].note}")
        transport_state = (
            "now-certified covariant transport"
            if self.nodes["final_covariant_H4"].status
            else "still-open covariant transport"
        )
        lines.extend(
            [
                "",
                "> The algebraic and energy-mode result is independently certified:",
                "> `H^4 = C^2` with Gram matrix `I_2`. This report tracks its",
                f"> {transport_state}.",
                "",
            ]
        )
        return "\n".join(lines)
