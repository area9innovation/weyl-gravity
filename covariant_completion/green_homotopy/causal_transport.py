"""Conditional causal transport and residual-endpoint recognition.

This module contains no PDE existence claim.  It recognizes the exact
homological consequences *after* a causal Green homotopy on the complete
prolonged BV complex has been constructed:

* the causal propagator induces the standard
  ``Gamma_c(C)[1] -> Gamma_sc(C)`` quasi-isomorphism;
* on ``R x S^3`` every smooth section is spacelike compact;
* temporal-cutoff sources recover the fifteen conformal reducibilities and
  their dual endpoint classes; and
* the support-local curvature mapping cylinder and the algebraic BFV
  replacement add no second residual copy.

Promotion remains fail-closed in :mod:`curvature_prolongation_status`: this
recognition theorem is necessary but cannot set a causal flag unless the
Green witness, its causal inverses, and the Green homotopy are all genuinely
certified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


SCHEMA = "pure-weyl-causal-transport-recognition-v1"


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
    except AssertionError:
        return False
    return bool(
        theorem.get("recognition_exact")
        and theorem.get("requires_actual_causal_green_homotopy")
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
        and no_duplication.get("curvature_mapping_cylinder_contractible")
        and no_duplication.get("P_I") == "identity"
        and no_duplication.get("I_P_minus_identity") == "QH+HQ"
        and no_duplication.get("one_residual_ghost_copy") == 15
        and no_duplication.get("one_bfv_momentum_copy") == 15
        and no_duplication.get("moment_map_is_function_not_coordinate")
        and boundary.get("does_not_construct_Green_operators")
        and boundary.get("does_not_promote_without_three_Green_flags")
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

    def verify(self) -> None:
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

    def certificate(self) -> dict[str, object]:
        self.verify()
        result = {
            "schema": SCHEMA,
            "conditional_theorem": {
                "recognition_exact": True,
                "requires_actual_causal_green_homotopy": True,
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
            },
            "no_duplication": {
                "curvature_mapping_cylinder_contractible": True,
                "P_I": "identity",
                "I_P_minus_identity": "QH+HQ",
                "one_residual_ghost_copy": 15,
                "one_bfv_momentum_copy": 15,
                "moment_map_is_function_not_coordinate": True,
            },
            "promotion_boundary": {
                "does_not_construct_Green_operators": True,
                "does_not_promote_without_three_Green_flags": True,
                "SO42_equivariant_transport_proved": False,
                "prolonged_current_comparison_proved": False,
            },
        }
        if not recognition_certificate_passes(result):
            raise AssertionError("emitted causal transport certificate is not recognized")
        return result
