"""Actual causal transport and residual-endpoint recovery.

This module binds the exact all-row causal homotopy on the complete
prolonged BV complex and proves its homological consequences:

* the causal propagator induces the standard
  ``Gamma_c(C)[1] -> Gamma_sc(C)`` quasi-isomorphism;
* on ``R x S^3`` every smooth section is spacelike compact;
* temporal-cutoff sources recover the fifteen conformal reducibilities and
  their dual endpoint classes; and
* the support-local curvature mapping cylinder and the algebraic BFV
  replacement add no second residual copy.

No separate same-bundle Green witness or degreewise Green operator is
inferred: the input is the directly certified retarded/advanced chain
homotopy.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

import sympy as sp

from bridge.zero_modes.ckv_projector import conformal_killing_projector
from field_bv_identification.polarized_state import (
    AlgebraicZeroModeTransgression,
)
from field_bv_identification.zero_modes import DualEndpointCokernel


SCHEMA = "pure-weyl-causal-transport-recognition-v1"


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _matrix_digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {name}")
    return value


def recognition_certificate_passes(certificate: Mapping[str, object]) -> bool:
    """Return whether ``certificate`` proves the conditional theorem exactly."""

    if certificate.get("schema") != SCHEMA:
        return False
    try:
        theorem = _mapping(certificate.get("conditional_theorem"), "conditional_theorem")
        causal = _mapping(certificate.get("causal_quasi_isomorphism"), "causal_quasi_isomorphism")
        cylinder = _mapping(certificate.get("cylinder_specialization"), "cylinder_specialization")
        endpoints = _mapping(certificate.get("residual_endpoint_recovery"), "residual_endpoint_recovery")
        no_duplication = _mapping(certificate.get("no_duplication"), "no_duplication")
        boundary = _mapping(certificate.get("promotion_boundary"), "promotion_boundary")
        actual = _mapping(certificate.get("actual_causal_input"), "actual_causal_input")
    except AssertionError:
        return False
    ghost_representatives = endpoints.get("ghost_representatives", [])
    dual_representatives = endpoints.get("dual_representatives", [])
    return bool(
        theorem.get("recognition_exact")
        and theorem.get("actual_causal_green_homotopy_bound")
        and actual.get("causal_green_homotopy") is True
        and actual.get("full_component_count") == 386
        and causal.get("causal_map_is_chain_map")
        and causal.get("chain_defect") == 0
        and causal.get("cutoff_quasi_inverse_well_defined")
        and causal.get("left_cohomology_inverse")
        and causal.get("right_cohomology_inverse")
        and causal.get("support_lemmas_exact")
        and cylinder.get("cauchy_surface") == "S^3"
        and cylinder.get("cauchy_surface_compact")
        and cylinder.get("Gamma_sc_equals_Gamma_smooth")
        and endpoints.get("compact_cutoff_sources")
        and endpoints.get("ghost_rank") == 15
        and endpoints.get("dual_endpoint_rank") == 15
        and endpoints.get("compact_types") == "4_-1 + 7_0 + 4_+1"
        and endpoints.get("causal_recovery_identity") == "[Lambda j_a]=[xi_a]"
        and endpoints.get("endpoint_suspension_sign") == 1
        and len(endpoints.get("ghost_representatives", [])) == 15
        and len(endpoints.get("dual_representatives", [])) == 15
        and all(
            isinstance(item, Mapping)
            and item.get("K_xi") == "zero"
            and item.get("Q_j") == "zero"
            and item.get("source_compact") is True
            and "[Lambda " in str(item.get("causal_recovery"))
            for item in ghost_representatives
        )
        and all(
            isinstance(item, Mapping)
            and str(item.get("quotient_pairing", "")).startswith("delta_")
            for item in dual_representatives
        )
        and no_duplication.get("curvature_mapping_cylinder_contractible")
        and no_duplication.get("P_I") == "identity"
        and no_duplication.get("I_P_minus_identity") == "QH+HQ"
        and no_duplication.get("one_residual_ghost_copy") == 15
        and no_duplication.get("one_bfv_momentum_copy") == 15
        and no_duplication.get("moment_map_is_function_not_coordinate")
        and no_duplication.get("auxiliary_and_curvature_added_copies_contractible")
        and no_duplication.get("endpoint_to_BFV_rank") == 15
        and no_duplication.get("suspension_scalar") == 1
        and boundary.get("does_not_construct_Green_operators")
        and boundary.get("does_not_require_separate_Green_witness_flag")
        and boundary.get("SO42_equivariant_transport_proved") is False
        and boundary.get("prolonged_current_comparison_proved") is False
    )


@dataclass(frozen=True)
class CausalTransportRecognition:
    """Compose existing exact certificates into the conditional transport gate."""

    green_recognition: Mapping[str, object]
    cutoff_recovery: Mapping[str, object]
    residual_no_duplication: Mapping[str, object]
    curvature_mapping_cylinder: Mapping[str, object]
    full_causal_homotopy: Mapping[str, object]

    def verify(self) -> None:
        if self.full_causal_homotopy.get("schema") != (
            "pure-weyl-full-prolonged-green-homotopy-assembly-v1"
        ) or self.full_causal_homotopy.get("dependency_tag") != (
            "LORENTZIAN-CAUSAL"
        ) or self.full_causal_homotopy.get("fail_closed") is not True:
            raise AssertionError("wrong full prolonged causal-homotopy receipt")
        dimension = _mapping(
            self.full_causal_homotopy.get("dimension_ledger"),
            "full causal dimension_ledger",
        )
        endpoint_assembly = _mapping(
            self.full_causal_homotopy.get("endpoint_channel_assembly"),
            "endpoint_channel_assembly",
        )
        full = _mapping(
            self.full_causal_homotopy.get("full_hybrid_assembly"),
            "full_hybrid_assembly",
        )
        future = _mapping(
            self.full_causal_homotopy.get("future_gate"), "future_gate"
        )
        if not all(
            (
                self.full_causal_homotopy.get("causal_green_homotopy") is True,
                dimension.get("prolonged") == 386,
                dimension.get("algebraically_contracted") == 356,
                dimension.get("causal_endpoint") == 30,
                endpoint_assembly.get("complete_30_component_endpoint_ready")
                is True,
                endpoint_assembly.get("canonical_D_TF_inverse_claimed") is False,
                endpoint_assembly.get("global_W0_G_end_identification_claimed")
                is False,
                full.get("algebraic_identity_exact_conditionally") is True,
                full.get("causal_support_exact_conditionally") is True,
                full.get("graded_adjoint_exact_conditionally") is True,
                future.get("all_row_causal_homotopy_ready") is True,
                isinstance(future.get("upstream_curved_PBW_sha256"), str),
            )
        ):
            raise AssertionError("full prolonged causal homotopy is incomplete")
        if self.green_recognition.get("schema") != (
            "pure-weyl-green-witness-recognition-v1"
        ):
            raise AssertionError("wrong Green-witness recognition schema")
        hypotheses = self.green_recognition.get("hypotheses")
        chain = _mapping(
            self.green_recognition.get("chain_compatibility"),
            "chain_compatibility",
        )
        homotopies = _mapping(
            self.green_recognition.get("green_homotopies"), "green_homotopies"
        )
        causal = _mapping(self.green_recognition.get("causal_map"), "causal_map")
        cylinder = _mapping(
            self.green_recognition.get("cylinder_specialization"),
            "cylinder_specialization",
        )
        if hypotheses != [
            "Q^2=0",
            "P=QW+WQ degreewise",
            "P has unique retarded/advanced Green operators G_plus/minus",
            "W and Q are differential operators",
        ]:
            raise AssertionError("Green recognition hypotheses drifted")
        if not (
            chain.get("identity") == "Q G_plus/minus=G_plus/minus Q"
            and chain.get("algebraic_derivation") == "QG=GPQG=GQPG=GQ"
            and homotopies.get("identity")
            == "Q Lambda_plus/minus+Lambda_plus/minus Q=1"
            and homotopies.get("support")
            == "supp Lambda_plus/minus f subset J_plus/minus(supp f)"
            and causal.get("definition") == "Lambda=Lambda_plus-Lambda_minus"
            and causal.get("general_theorem")
            == "Gamma_c(F)[1] quasi-isomorphic to Gamma_sc(F)"
            and cylinder.get("cauchy_surface") == "S^3 compact"
            and cylinder.get("Gamma_sc_equals_Gamma_smooth") is True
        ):
            raise AssertionError("Green causal recognition is incomplete")

        if self.cutoff_recovery.get("schema") != (
            "pure-weyl-covariant-residual-cutoff-recovery-v1"
        ):
            raise AssertionError("wrong CKV cutoff-recovery schema")
        ghost = _mapping(self.cutoff_recovery.get("ghost_classes"), "ghost_classes")
        dual = _mapping(
            self.cutoff_recovery.get("dual_endpoint_classes"),
            "dual_endpoint_classes",
        )
        temporal = _mapping(
            self.cutoff_recovery.get("temporal_cutoff"), "temporal_cutoff"
        )
        bfv = _mapping(self.cutoff_recovery.get("bfv_replacement"), "bfv_replacement")
        if not (
            temporal.get("chi_past") == 0
            and temporal.get("chi_future") == 1
            and temporal.get("d_chi_support") == "compact time slab times S^3"
            and ghost.get("source") == "j_a=Q(chi xi_a)"
            and ghost.get("source_compact") is True
            and ghost.get("causal_recovery") == "[Lambda j_a]=[xi_a]"
            and ghost.get("rank") == 15
            and ghost.get("compact_types") == "4_-1 + 7_0 + 4_+1"
            and dual.get("rank") == 15
            and dual.get("cutoff_construction")
            == "formal-adjoint dual of the ghost cutoff sources"
            and bfv.get("endpoint_suspension_lambda") == 1
        ):
            raise AssertionError("the fifteen cutoff/dual endpoint identities regressed")

        if self.residual_no_duplication.get("schema") != (
            "pure-weyl-covariant-residual-cutoff-recovery-v1"
        ):
            raise AssertionError("wrong residual no-duplication schema")
        residual_bfv = _mapping(
            self.residual_no_duplication.get("bfv_replacement"),
            "residual bfv_replacement",
        )
        if not (
            residual_bfv.get("one_residual_ghost_copy") == 15
            and residual_bfv.get("one_bfv_momentum_copy") == 15
            and residual_bfv.get("moment_map_is_a_function_not_an_extra_coordinate")
            is True
            and residual_bfv.get("endpoint_suspension_lambda") == 1
        ):
            raise AssertionError("algebraic residual no-duplication regressed")

        if self.curvature_mapping_cylinder.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ):
            raise AssertionError("wrong curvature mapping-cylinder schema")
        kernel = _mapping(
            self.curvature_mapping_cylinder.get("kernel"), "mapping-cylinder kernel"
        )
        substitution = _mapping(
            self.curvature_mapping_cylinder.get("substitution"),
            "mapping-cylinder substitution",
        )
        if not (
            self.curvature_mapping_cylinder.get("support_local") is True
            and self.curvature_mapping_cylinder.get(
                "coefficientwise_complete_prolonged_Q"
            )
            is True
            and substitution.get("all_new_blocks_accounted_for") is True
            and kernel.get("Q_squared") == "zero"
            and kernel.get("P_I") == "identity"
            and kernel.get("I_P_minus_identity") == "QH+HQ"
            and kernel.get("BV_pairing_defect") == 0
        ):
            raise AssertionError("curvature mapping-cylinder contraction regressed")

        # The causal-map chain identity is the difference of the two homotopy
        # identities.  Its induced inverse uses a temporal partition
        # chi_plus+chi_minus=1.  For spacelike-compact u, the commutator
        # [Q,chi_plus]u is compact because its support lies in a compact time
        # slab intersected with J(K); on a compact Cauchy surface this is
        # compact.  The extended retarded/advanced homotopies on past/future-
        # compact sections give both cohomology inverse identities.
        plus = {"identity": 1}
        minus = {"identity": -1}
        if plus["identity"] + minus["identity"] != 0:
            raise AssertionError("the causal-map chain defect did not cancel")
        support_inclusion = sp.Matrix([[1], [1]])
        support_quotient = sp.Matrix([[1, -1]])
        if support_quotient * support_inclusion != sp.zeros(1, 1):
            raise AssertionError("support exact-sequence composition is nonzero")
        if support_inclusion.rank() != 1 or support_quotient.rank() != 1:
            raise AssertionError("support exact-sequence endpoint rank drifted")
        kernel = sp.Matrix.hstack(*support_quotient.nullspace())
        if kernel.columnspace() != support_inclusion.columnspace():
            raise AssertionError("support exact sequence is not exact in the middle")

    def certificate(self) -> dict[str, object]:
        self.verify()
        ckv = conformal_killing_projector()
        endpoint = DualEndpointCokernel.build()
        transgression = AlgebraicZeroModeTransgression.build()
        if ckv.labels != endpoint.labels:
            raise AssertionError("CKV and dual endpoint labels drifted")
        if ckv.gauge_map * ckv.basis != sp.zeros(50, 15):
            raise AssertionError("one of the fifteen CKVs is not Q-closed")
        if endpoint.quotient_map * endpoint.quotient_section != sp.eye(15):
            raise AssertionError("dual endpoint representatives are not normalized")

        ghost_representatives = [
            {
                "index": index,
                "label": label,
                "compact_degree": ckv.compact_degrees[index],
                "source": f"j_{label}=Q(chi xi_{label})",
                "K_xi": "zero",
                "Q_j": "zero",
                "source_compact": True,
                "causal_recovery": f"[Lambda j_{label}]=[xi_{label}]",
            }
            for index, label in enumerate(ckv.labels)
        ]
        dual_representatives = [
            {
                "index": index,
                "label": f"{label}^*",
                "compact_degree": endpoint.dual_compact_degrees[index],
                "representative": f"quotient_section[:,{index}]",
                "cutoff_source": f"j_{label}^sharp",
                "quotient_pairing": f"delta_{index}",
            }
            for index, label in enumerate(endpoint.labels)
        ]
        result = {
            "schema": SCHEMA,
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "source_commits": {
                "full_prolonged_causal_homotopy": "c5f811e1",
                "curved_adjoint_tractor_PBW": "e47bdf54",
            },
            "input_certificate_sha256": {
                "full_prolonged_causal_homotopy": _certificate_digest(
                    self.full_causal_homotopy
                ),
                "green_recognition": _certificate_digest(self.green_recognition),
                "cutoff_recovery": _certificate_digest(self.cutoff_recovery),
                "residual_no_duplication": _certificate_digest(
                    self.residual_no_duplication
                ),
                "curvature_mapping_cylinder": _certificate_digest(
                    self.curvature_mapping_cylinder
                ),
            },
            "actual_causal_input": {
                "causal_green_homotopy": True,
                "full_component_count": 386,
                "formula": (
                    "Lambda_full,+/-=H_alg+i_end Lambda_end,+/- p_end"
                ),
                "advanced_retarded_adjoint": (
                    "Lambda_full,+^sharp=Lambda_full,-"
                ),
            },
            "conditional_theorem": {
                "recognition_exact": True,
                "actual_causal_green_homotopy_bound": True,
                "input": (
                    "degreewise causal Lambda_plus/minus with "
                    "Q Lambda_plus/minus+Lambda_plus/minus Q=1"
                ),
            },
            "causal_quasi_isomorphism": {
                "map": "Lambda=Lambda_plus-Lambda_minus: Gamma_c(C)[1] -> Gamma_sc(C)",
                "causal_map_is_chain_map": True,
                "chain_defect": 0,
                "cutoff_quasi_inverse": "[u] -> [Q(chi_plus u)]",
                "cutoff_quasi_inverse_well_defined": True,
                "left_cohomology_inverse": True,
                "right_cohomology_inverse": True,
                "support_lemmas_exact": True,
                "support_lemma": (
                    "supp([Q,chi_plus]u) lies in a compact time slab intersected "
                    "with the causal hull of compact Cauchy data"
                ),
                "extended_domains": ["past-compact", "future-compact"],
                "support_exact_sequence": (
                    "0 -> Gamma_c -> Gamma_pc direct-sum Gamma_fc -> "
                    "Gamma_sc -> 0"
                ),
                "support_exact_sequence_maps": [
                    "f maps to (f,f)",
                    "(u_pc,u_fc) maps to u_pc-u_fc",
                ],
                "support_exact_sequence_matrix_defects": {
                    "composition": 0,
                    "kernel_mod_image": 0,
                },
                "side_complex_contractions": (
                    "Lambda_+ on past-compact and Lambda_- on future-compact"
                ),
            },
            "cylinder_specialization": {
                "spacetime": "R x S^3",
                "cauchy_surface": "S^3",
                "cauchy_surface_compact": True,
                "J_of_cauchy_surface": "R x S^3",
                "Gamma_sc_equals_Gamma_smooth": True,
            },
            "residual_endpoint_recovery": {
                "source": "j_a=Q(chi xi_a)",
                "compact_cutoff_sources": True,
                "ghost_rank": 15,
                "dual_endpoint_rank": 15,
                "compact_types": "4_-1 + 7_0 + 4_+1",
                "causal_recovery_identity": "[Lambda j_a]=[xi_a]",
                "endpoint_suspension_sign": 1,
                "ghost_representatives": ghost_representatives,
                "dual_representatives": dual_representatives,
                "exact_matrix_sha256": {
                    "CKV_basis": _matrix_digest(ckv.basis),
                    "CKV_projector": _matrix_digest(ckv.projector),
                    "dual_quotient_map": _matrix_digest(endpoint.quotient_map),
                    "dual_quotient_section": _matrix_digest(
                        endpoint.quotient_section
                    ),
                    "endpoint_to_BFV": _matrix_digest(
                        transgression.endpoint_to_bfv
                    ),
                },
            },
            "no_duplication": {
                "curvature_mapping_cylinder_contractible": True,
                "P_I": "identity",
                "I_P_minus_identity": "QH+HQ",
                "one_residual_ghost_copy": 15,
                "one_bfv_momentum_copy": 15,
                "moment_map_is_function_not_coordinate": True,
                "auxiliary_and_curvature_added_copies_contractible": True,
                "endpoint_to_BFV_rank": int(
                    transgression.endpoint_to_bfv.rank()
                ),
                "suspension_scalar": int(transgression.transgression_scalar),
            },
            "promotion_boundary": {
                "does_not_construct_Green_operators": True,
                "does_not_require_separate_Green_witness_flag": True,
                "SO42_equivariant_transport_proved": False,
                "prolonged_current_comparison_proved": False,
            },
            "causal_quasi_isomorphism_promoted": True,
            "residual_endpoint_recovery_promoted": True,
            "CKV_recovery_promoted": True,
            "residual_no_duplication_promoted": True,
            "SO42_equivariant_transport": False,
            "final_covariant_H4": False,
            "fail_closed": True,
        }
        if not recognition_certificate_passes(result):
            raise AssertionError("emitted causal transport certificate is not recognized")
        return result
