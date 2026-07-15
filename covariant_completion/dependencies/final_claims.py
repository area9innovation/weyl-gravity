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
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

COVARIANT_ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE_DIR = COVARIANT_ROOT / "certificates"
ANALYTIC_CERTIFICATE_DIR = COVARIANT_ROOT.parent / "analytic_completion" / "certificates"
BRIDGE_CERTIFICATE_DIR = COVARIANT_ROOT.parent / "bridge" / "certificates"

DIRECT_CAUSAL_PAIRING_INPUTS = {
    "curved_pbw": "adjoint_tractor_bgg_curved_pbw.json",
    "parent_transfer": "adjoint_tractor_green_transfer.json",
    "full_homotopy": "curved_full_prolonged_green_homotopy_assembly.json",
    "prolonged_current": "curved_prolonged_current_comparison.json",
    "auxiliary_metric_current": "curved_current_comparison.json",
    "green_current_theorem": "curved_green_current_pairing.json",
    "EAL_regression": "curved_EAL_pairing_regression.json",
}


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_certificate_digest(path: Path) -> str:
    value = json.loads(path.read_text(encoding="utf-8"))
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _authoritative_so42_input_sha256() -> dict[str, str]:
    paths = {
        "actual_causal_quasi_isomorphism": (
            CERTIFICATE_DIR / "curved_causal_transport_recognition.json"
        ),
        "auxiliary_retract": (
            CERTIFICATE_DIR / "curved_auxiliary_canonical_split.json"
        ),
        "curvature_mapping_cylinder": (
            CERTIFICATE_DIR
            / "curved_curvature_mapping_cylinder_substitution.json"
        ),
        "curvature_causal_pde": (
            CERTIFICATE_DIR / "curved_weyl_cotton_causal_pde.json"
        ),
        "raw_bv_transfer": BRIDGE_CERTIFICATE_DIR / "raw_bv_transfer.json",
        "cylinder_bgg_blocks": (
            BRIDGE_CERTIFICATE_DIR / "cylinder_bgg_blocks.json"
        ),
        "cylinder_metric_preimages": (
            BRIDGE_CERTIFICATE_DIR / "cylinder_metric_preimages.json"
        ),
        "curvature_EAL_spectrum": (
            CERTIFICATE_DIR / "curved_EAL_spectrum_all_level.json"
        ),
    }
    return {name: _json_certificate_digest(path) for name, path in paths.items()}


def so42_authoritative_certificate_passes(
    certificate: Mapping[str, Any],
) -> bool:
    if certificate.get("schema") != (
        "pure-weyl-so42-causal-transport-recognition-v1"
    ):
        return False
    if certificate.get("dependency_tag") != "LORENTZIAN-CAUSAL":
        return False
    sections = tuple(
        certificate.get(name)
        for name in (
            "conditional_theorem",
            "cutoff_homotopy",
            "local_naturality",
            "global_module_identification",
            "residual_action",
            "promotion_boundary",
            "input_certificate_sha256",
        )
    )
    if not all(isinstance(value, Mapping) for value in sections):
        return False
    theorem, cutoff, local, module, residual, boundary, hashes = sections
    if dict(hashes) != _authoritative_so42_input_sha256():
        return False
    return all(
        (
            theorem.get("recognition_exact") is True,
            theorem.get("requires_causal_quasi_isomorphism") is True,
            theorem.get("actual_causal_quasi_isomorphism_bound") is True,
            cutoff.get("formal_defect") == 0,
            cutoff.get("identity") == "[kappa,rho]=[Q,[chi,rho]]",
            cutoff.get("homotopy") == "[chi,rho]",
            cutoff.get("homotopy_support_compact") is True,
            cutoff.get("all_fifteen_generators") is True,
            local.get("auxiliary_shift_natural") is True,
            local.get("auxiliary_retract_support_local") is True,
            local.get("curvature_map_natural") is True,
            local.get("curvature_mapping_cylinder_support_local") is True,
            local.get("first_order_state_action_inherited_from_covariant_rows")
            is True,
            local.get("contractible_rows_add_no_action") is True,
            module.get("smooth_global_BGG_equivariant") is True,
            module.get("curvature_quotient_is_W_plus_W_minus") is True,
            module.get("all_level_EAL_exhaustion") is True,
            module.get("both_chiralities") is True,
            residual.get("raw_generators_are_chain_maps") is True,
            residual.get("raw_SDR_homotopy_equivariant") is True,
            residual.get("strict_so42_action_on_cohomology") is True,
            residual.get("proper_conformal_brackets_exact") is True,
            boundary.get("does_not_construct_causal_green_homotopy") is True,
            boundary.get("does_not_claim_strict_Cauchy_split") is True,
            boundary.get("does_not_claim_pairing_transport") is True,
            boundary.get("SO42_equivariant_transport_conditional") is True,
        )
    )


def direct_causal_pairing_certificate_passes(
    certificate: Mapping[str, Any],
) -> bool:
    """Recognize the SHA-bound implementation-neutral pairing theorem."""

    if certificate.get("schema") != (
        "pure-weyl-direct-causal-pairing-transport-v1"
    ):
        return False
    if certificate.get("dependency_tag") != "LORENTZIAN-CAUSAL":
        return False
    if certificate.get("fail_closed") is not True:
        return False
    recorded = certificate.get("input_certificate_sha256")
    guards = certificate.get("fail_closed_guards")
    causal = certificate.get("causal_difference")
    pairing = certificate.get("pairing_transport")
    normalization = certificate.get("normalization")
    if not all(
        isinstance(value, Mapping)
        for value in (recorded, guards, causal, pairing, normalization)
    ):
        return False
    if set(recorded) != set(DIRECT_CAUSAL_PAIRING_INPUTS):
        return False
    if any(
        recorded.get(role)
        != _file_sha256(CERTIFICATE_DIR / filename)
        for role, filename in DIRECT_CAUSAL_PAIRING_INPUTS.items()
    ):
        return False
    required_guards = {
        "EAL_regression:verified",
        "curved_pbw:theorem_boundary.cyclic_i_sharp_equals_p",
        "full_homotopy:causal_green_homotopy",
        "full_homotopy:full_hybrid_assembly.graded_adjoint_exact_conditionally",
        "green_current_theorem:Green_pairing_equals_current_pairing",
        "manual_final_H4_promotion_rejected",
        "prolonged_current:prolonged_current_comparison",
    }
    if not required_guards.issubset(guards):
        return False
    if any(value is not True for value in guards.values()):
        return False
    if causal.get("causal_support") is not True:
        return False
    if causal.get("graded_antisymmetry") != "Delta_Lambda^sharp=-Delta_Lambda":
        return False
    if pairing.get("implementation_neutral") is not True:
        return False
    if pairing.get("positive_PDE_symmetrizer_used") is not False:
        return False
    if pairing.get("canonical_D_TF_inverse_used") is not False:
        return False
    if pairing.get("global_W0_G_end_identity_used") is not False:
        return False
    if normalization.get("Krein_signs") != {"E": 1, "A": -1, "L": -1}:
        return False
    return all(
        (
            certificate.get("Green_pairing_equals_current_pairing") is True,
            certificate.get("pairing_compatibility") is True,
            certificate.get("status_flags_promoted")
            == [
                "Green_pairing_equals_current_pairing",
                "pairing_compatibility",
            ],
            certificate.get("final_covariant_H4") is False,
        )
    )


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
            "pure-weyl-curvature-prolongation-status-v3",
        )
        curvature_evolution_symbol = _load(
            "curved_curvature_evolution_principal_symbol.json",
            "pure-weyl-curvature-evolution-principal-symbol-v2",
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
        direct_causal_pairing = _load(
            "curved_direct_causal_pairing_transport.json",
            "pure-weyl-direct-causal-pairing-transport-v1",
        )
        so42_transport = _load(
            "curved_SO42_causal_transport_recognition.json",
            "pure-weyl-so42-causal-transport-recognition-v1",
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
            "implemented_structural_fact",
            (
                "curved_weyl_cotton_jet_comparison.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The complete curved Weyl/Cotton and Bach equations agree on all 150 independent Weyl two-jets and globalize by cylinder homogeneity.",
        )
        atomic(
            "curved_EB_first_order_closure",
            bool(curvature_prolongation.get("curved_EB_first_order_closure", False)),
            "implemented_structural_fact",
            (
                "curved_weyl_cotton_3plus1.json",
                "curved_weyl_cotton_bach_first_order.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The ten Weyl E/B components plus the sixteen-component Cotton divergence form an exact local 26-state first-order closure with 34 covariant rows and eight constraints.",
        )
        atomic(
            "curved_EB_symmetric_hyperbolicity",
            bool(curvature_prolongation["curved_EB_symmetric_hyperbolicity"]),
            "implemented_structural_fact",
            (
                "curved_weyl_cotton_hyperbolic.json",
                "curved_weyl_cotton_differential_ideal.json",
                "curved_weyl_cotton_formal_integrability.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The constraint-adjusted 26-state system is formally integrable-equivalent to the exact covariant rows and has a positive symmetrizer with causal characteristics.",
        )
        atomic(
            "curved_sourced_constraint_identity",
            bool(
                curvature_prolongation.get(
                    "curved_sourced_constraint_identity", False
                )
            ),
            "implemented_structural_fact",
            (
                "curved_weyl_cotton_formal_integrability.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The curvature-corrected sourced subsidiary identity and its six compatible-source rows are exact.",
        )
        atomic(
            "curved_constraint_propagation",
            bool(curvature_prolongation["curved_constraint_propagation"]),
            "implemented_structural_fact",
            (
                "curved_weyl_cotton_hyperbolic.json",
                "curved_weyl_cotton_formal_integrability.json",
                "curved_curvature_prolongation_status.json",
            ),
            "All fourteen primary and secondary constraints propagate in a causal symmetric-hyperbolic subsidiary system for compatible sources.",
        )
        atomic(
            "EAL_curvature_spectrum_match",
            bool(curvature_prolongation.get("EAL_curvature_spectrum_match", False)),
            "implemented_structural_fact",
            (
                "curved_EAL_spectrum_all_level.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The exact covariant Weyl--Cotton equations carry precisely the parity-complete E, A, and L towers at every energy; symbolic BGG rank and character identities prove exhaustion and the Cotton graph adds no modes.",
        )
        atomic(
            "support_local_prolongation_retract",
            bool(curvature_prolongation["support_local_prolongation_retract"]),
            "implemented_structural_fact",
            (
                "curved_curvature_mapping_cylinder_substitution.json",
                "curved_core_curvature_chain_map.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The corrected curved p_E/p_I attachments and their cotangent lifts give a finite-order support-local mapping-cylinder SDR on all sixteen BV blocks.",
        )
        atomic(
            "prolonged_BV_operator_identity",
            bool(
                curvature_prolongation.get(
                    "prolonged_BV_operator_identity", False
                )
            ),
            "implemented_structural_fact",
            (
                "curved_curvature_mapping_cylinder_substitution.json",
                "curved_core_curvature_chain_map.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The complete sixteen-block fibre-identified mapping cylinder is coefficientwise nilpotent, odd cyclic, and satisfies PI=1 and IP-1=QH+HQ; the old rank-four Rees defect used the wrong flat-Fourier cotangent projection.",
        )
        atomic(
            "prolonged_green_witness",
            bool(curvature_prolongation.get("prolonged_green_witness", False)),
            "scoped_legacy_implementation_flag",
            (
                "curved_curvature_mapping_cylinder_witness.json",
                "curved_auxiliary_prenormal_symbol.json",
                "curved_auxiliary_lower_order_factor_ansatz.json",
                "parallel_operator_composition.json",
                "symmetrized_pbw_composition.json",
                "curved_general_nonlinear_factor_system.json",
                "general_adjoint_factor.json",
                "curved_general_nonlinear_factor_sharp_order2.json",
                "curved_general_nonlinear_factor_sharp_order2_reduction.json",
                "curved_general_nonlinear_factor_sharp_macaulay_screen.json",
                "quadratic_obstruction_channel.json",
                "quadratic_obstruction_channel_fixed_branch.json",
                "curved_auxiliary_triangular_box_factor.json",
                "curved_mixed_order_green_promotion.json",
                "curved_relative_saddle_witness.json",
                "curved_relative_saddle_principal.json",
                "curved_expanded_relative_witness.json",
                "curved_expanded_relative_witness_commutant.json",
                "curved_expanded_relative_witness_scalar_completion.json",
                "curved_expanded_relative_witness_douglis.json",
                "curved_expanded_relative_witness_adjoint_sign.json",
                "curved_expanded_relative_witness_r6_family.json",
                "curved_expanded_relative_witness_r6_first_order_no_go.json",
                "curved_expanded_relative_witness_triangular_green_audit.json",
                "curved_expanded_relative_witness_jordan_homology.json",
                "curved_expanded_relative_witness_jordan_triangular.json",
                "curved_expanded_relative_witness_shifted_green_filtration.json",
                "curved_expanded_relative_witness_rank34_module.json",
                "curved_expanded_relative_witness_vector_contraction.json",
                "curved_expanded_relative_witness_all_row_assembly.json",
                "curved_rank14_weyl_cotton_input_manifest.json",
                "curved_expanded_relative_witness_rank14_curvature_presentation.json",
                "curved_rank14_weyl_cotton_symbol_audit.json",
                "curved_rank14_equation_cycle_gate.json",
                "curved_rank14_equation_sdr_boundary.json",
                "curved_rank14_full_cone_symbol_gate.json",
                "curved_rank14_weyl_cotton_incoming_map_ledger.json",
                "curved_expanded_relative_witness_incidence_screen.json",
                "curved_expanded_relative_witness_alternative_semisimplicity.json",
                "curved_expanded_relative_witness_alternative_family_no_go.json",
                "curved_curvature_prolongation_status.json",
            ),
            "Scoped legacy flag for a canonical prolonged witness with same-sided endpoint inverses. It remains false; the direct adjoint-tractor causal homotopy closes the required chain identity without asserting this stronger implementation.",
        )
        atomic(
            "curvature_causal_green_operators",
            bool(curvature_prolongation["curvature_causal_green_operators"]),
            "scoped_legacy_implementation_flag",
            ("curved_curvature_prolongation_status.json",),
            "The canonical endpoint witness has no certified same-sided inverse. This implementation-specific flag remains false and is not required by the direct tractor causal route.",
        )
        atomic(
            "direct_tractor_causal_homotopy",
            bool(
                curvature_prolongation.get(
                    "direct_tractor_causal_homotopy", False
                )
            ),
            "implemented_structural_fact",
            (
                "curved_full_prolonged_green_homotopy_assembly.json",
                "adjoint_tractor_bgg_curved_pbw.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The SHA-bound curved adjoint-tractor transfer, trace/Weyl shear, and 356+30 hybrid SDR give advanced and retarded all-row homotopies directly, without claiming a canonical endpoint inverse.",
        )
        atomic(
            "causal_green_homotopy",
            bool(curvature_prolongation.get("causal_green_homotopy", False)),
            "implemented_structural_fact",
            (
                "curved_full_prolonged_green_homotopy_assembly.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The complete 386-row prolonged complex has support-causal Lambda_+/- with Q Lambda_+/- + Lambda_+/- Q=1 and Lambda_+^sharp=Lambda_-.",
        )
        atomic(
            "causal_quasi_isomorphism",
            bool(curvature_prolongation.get("causal_quasi_isomorphism", False)),
            "implemented_structural_fact",
            (
                "curved_causal_transport_recognition.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The support-exact-sequence construction proves that Lambda_+-Lambda_- is a quasi-isomorphism Gamma_c(C_prol)[1] -> Gamma_sc(C_prol), and compactness of S3 identifies the target with all smooth cylinder solutions.",
        )
        atomic(
            "residual_endpoint_recovery",
            bool(curvature_prolongation.get("residual_endpoint_recovery", False)),
            "implemented_structural_fact",
            (
                "curved_causal_transport_recognition.json",
                "curved_curvature_prolongation_status.json",
                "residual_bfv_comparison.json",
            ),
            "All fifteen cutoff CKV classes and their dual endpoints are realized through the actual causal map, with no prolongation copy and suspension sign +1.",
        )
        atomic(
            "SO42_equivariant_transport",
            bool(curvature_prolongation.get("SO42_equivariant_transport", False))
            and so42_authoritative_certificate_passes(so42_transport),
            "implemented_structural_fact",
            (
                "curved_SO42_causal_transport_recognition.json",
                "curved_curvature_prolongation_status.json",
            ),
            "The causal/Cauchy identification transfers the full SO(4,2) action by the explicit compactly supported cutoff homotopy [kappa,rho]=[Q,[chi,rho]].",
        )
        atomic(
            "prolonged_current_comparison",
            bool(curvature_prolongation.get("prolonged_current_comparison", False)),
            "implemented_structural_fact",
            (
                "curved_curvature_prolongation_status.json",
                "curved_prolonged_current_comparison.json",
                "curved_current_comparison.json",
            ),
            "The all-row cyclic quadratic parent and off-shell d+Q current comparison are exact and content-addressed to the corrected curved core-chain and mapping-cylinder certificates.",
        )
        atomic(
            "direct_causal_pairing_transport",
            direct_causal_pairing_certificate_passes(direct_causal_pairing),
            "implemented_structural_fact",
            (
                "curved_direct_causal_pairing_transport.json",
                *DIRECT_CAUSAL_PAIRING_INPUTS.values(),
            ),
            "The SHA-bound direct cyclic causal homotopy identifies the Green pairing with the prolonged, auxiliary, metric, Cauchy and all-energy E/A/L current pairings; it does not use a canonical endpoint inverse.",
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
            "The legacy candidate electric/magnetic Weyl principal block has a positive symmetrizer and the two physical characteristic speeds in each direction. This certificate alone is principal-symbol evidence; the exact curved derivation is certified separately by the curved E/B, first-order, sourced-constraint, and propagation nodes.",
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
            "residual_H4_is_C2",
            bool(energy_h4["completed_centered_equals_algebraic_centered"])
            and list(energy_h4["centered"]["classes"]) == ["W_+^2", "W_-^2"]
            and int(energy_h4["centered"]["two_particle_H4"]) == 2,
            "implemented_structural_fact",
            ("analytic_completion/certificates/completed_H4.json",),
            "The completed energy-mode centered cohomology is the certified two-class space.",
        )
        atomic(
            "residual_gram_is_I2",
            list(energy_gram["completed_gram"]) == [[1, 0], [0, 1]],
            "implemented_structural_fact",
            ("analytic_completion/certificates/completed_gram.json",),
            "The completed energy-mode cohomological Gram matrix is I_2.",
        )
        derived(
            "energy_H4_is_C2",
            ("residual_H4_is_C2",),
            "compatibility_alias",
            "Compatibility alias for the independently certified residual/energy H4 theorem.",
        )
        derived(
            "energy_gram_is_I2",
            ("residual_gram_is_I2",),
            "compatibility_alias",
            "Compatibility alias for the independently certified residual/energy Gram theorem.",
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
                "curved_EB_first_order_closure",
                "curved_sourced_constraint_identity",
                "curved_constraint_propagation",
                "EAL_curvature_spectrum_match",
                "support_local_prolongation_retract",
                "prolonged_BV_operator_identity",
            ),
            "derived_analytic_claim",
            "The exact local curvature-prolonged complex includes its first-order equations, sourced subsidiary system, all-level spectrum, every BV row, and support-local equivalence.",
        )
        derived(
            "curvature_green_realization",
            (
                "curvature_prolonged_complex_exact",
                "curved_EB_symmetric_hyperbolicity",
                "direct_tractor_causal_homotopy",
                "causal_green_homotopy",
            ),
            "derived_analytic_claim",
            "The selected direct tractor realization supplies a causal homotopy on the complete prolonged BV complex; it does not assert the superseded canonical witness/inverse implementation.",
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
            (
                "complete_bv_green_hyperbolicity",
                "green_witness_recognition_theorem",
                "causal_green_homotopy",
            ),
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
            "formal_compact_to_global_consequence",
            ("compact_to_global_quasi_isomorphism", "causal_quasi_isomorphism"),
            "derived_analytic_claim",
            "The certified causal quasi-isomorphism realizes the formal compact-to-global theorem on R x S^3.",
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
                "direct_causal_pairing_transport",
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
                "scalar_wave_witness_no_go",
                "weyl_symbol_helicity_isomorphism",
                "curved_EB_equations",
                "curved_EB_first_order_closure",
                "curved_EB_symmetric_hyperbolicity",
                "curved_sourced_constraint_identity",
                "curved_constraint_propagation",
                "EAL_curvature_spectrum_match",
                "support_local_prolongation_retract",
                "prolonged_BV_operator_identity",
                "direct_tractor_causal_homotopy",
                "causal_green_homotopy",
                "causal_quasi_isomorphism",
                "residual_endpoint_recovery",
                "SO42_equivariant_transport",
                "prolonged_current_comparison",
                "direct_causal_pairing_transport",
                "pairing_compatibility",
                "residual_H4_is_C2",
                "residual_gram_is_I2",
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
                "residual_H4_is_C2": self.nodes["residual_H4_is_C2"].status,
                "residual_gram_is_I2": self.nodes["residual_gram_is_I2"].status,
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
                    "curved_EB_first_order_closure",
                    "curved_EB_symmetric_hyperbolicity",
                    "curved_sourced_constraint_identity",
                    "curved_constraint_propagation",
                    "EAL_curvature_spectrum_match",
                    "support_local_prolongation_retract",
                    "prolonged_BV_operator_identity",
                    "direct_tractor_causal_homotopy",
                    "causal_green_homotopy",
                ],
                "blocking_dependencies": list(
                    self._blocking_atomic_dependencies(
                        "curvature_green_realization"
                    )
                ),
            },
            "causal_transport_gate": {
                "status": self.nodes["final_covariant_H4"].status,
                "required_flags": list(self.nodes["final_covariant_H4"].requires),
                "blocking_atomic_dependencies": list(
                    self._blocking_atomic_dependencies("final_covariant_H4")
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
            "  E[exact curved first-order E/B system] --> F",
            "  S[sourced constraints and E/A/L audit] --> F",
            "  P[all-row support-local prolongation] --> F",
            "  G[direct tractor causal Green homotopy] --> F",
            "  T[endpoint, SO(4,2), and pairing transport] --> F",
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
            "residual_H4_is_C2",
            "residual_gram_is_I2",
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
                "Weyl-curvature realization. The reduced Weyl-symbol theorem, the",
                "exact curved equations, and the 26-state first-order closure are",
                "true, and the direct all-row causal homotopy is now exact. The",
                "remaining quasi-isomorphism, endpoint, equivariance, and",
                "pairing-transport flags below remain open.",
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
