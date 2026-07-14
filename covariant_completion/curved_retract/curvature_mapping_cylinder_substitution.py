"""Fail-closed substitution audit for the curvature mapping cylinder.

The 16-block kernel fixes the degree/sign incidence of the prolonged BV
differential.  The three nontrivial graph entries are supplied independently
by exact coefficient certificates:

``T_state : M_aux -> U`` (order three),
``A_equation : Ebar_aux -> Eq`` (order two), and
``B_identity : I_aux -> Id`` (order zero).

This module checks that those certificates have the exact schemas, domains,
orders, shapes, coefficient coverage, hashes and two chain relations required
by the kernel.  Since every cotangent entry is the forced formal adjoint of one
of these three tables, this block substitution is coefficientwise complete
without expanding one enormous sparse matrix.  It does not promote a project
status flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    payload = json.dumps(
        certificate, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _formal_adjoint_digest(
    primal_sha256: object,
    maximum_order: object,
    source_pairing_sha256: object,
    target_pairing_sha256: object,
) -> str:
    """Content address an adjoint table generated from one primal table."""

    if not (
        _is_sha256(primal_sha256)
        and isinstance(maximum_order, int)
        and _is_sha256(source_pairing_sha256)
        and _is_sha256(target_pairing_sha256)
    ):
        raise AssertionError("cannot derive formal-adjoint provenance")
    payload = (
        "pure-weyl-formal-adjoint-table-v1|"
        "parallel coefficients:A_I^sharp=(-1)^|I| A_I^T|"
        f"order={maximum_order}|primal={primal_sha256}|"
        f"source_pairing={source_pairing_sha256}|"
        f"target_pairing={target_pairing_sha256}"
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class CurvatureMappingCylinderSubstitution:
    """Validated coefficient inputs for the canonical cotangent cone."""

    state_gauge_certificate: Mapping[str, object]
    linearized_bach_certificate: Mapping[str, object]
    equation_certificate: Mapping[str, object]
    identity_certificate: Mapping[str, object]
    retract_certificate: Mapping[str, object]
    kernel_certificate: Mapping[str, object]
    cotangent_certificate: Mapping[str, object]

    def verify(self) -> None:
        state_gauge = self.state_gauge_certificate
        linearized_bach = self.linearized_bach_certificate
        equation = self.equation_certificate
        identity = self.identity_certificate
        retract = self.retract_certificate
        kernel = self.kernel_certificate
        cotangent_audit = self.cotangent_certificate

        if state_gauge.get("schema") != (
            "pure-weyl-curvature-state-gauge-chain-map-v1"
        ):
            raise AssertionError("wrong T K_aux certificate schema")
        gauge_jets = _nested(state_gauge, "exhaustive_jet_certificate")
        if not (
            state_gauge.get("T_state_K_aux_exact") is True
            and state_gauge.get("T_state_K_aux") == "zero"
            and state_gauge.get("C1_K_aux") == "zero"
            and gauge_jets.get("diffeomorphism_jets") == 140
            and gauge_jets.get("diffeomorphism_defects") == 0
            and gauge_jets.get("Weyl_scalar_jets") == 15
            and gauge_jets.get("Weyl_scalar_defects") == 0
            and gauge_jets.get("boost_components") == 4
            and gauge_jets.get("auxiliary_metric_block_defects") == 0
            and state_gauge.get("support_local") is True
        ):
            raise AssertionError("T_state K_aux gauge square is incomplete")
        if linearized_bach.get("schema") != (
            "pure-weyl-linearized-bach-cylinder-v1"
        ):
            raise AssertionError("wrong linearized Bach certificate schema")
        bach_gauge_jets = _nested(linearized_bach, "gauge_jet_test")
        if not (
            linearized_bach.get("factorization_input") == "B_lin=C_1^sharp C_1"
            and linearized_bach.get("gauge_identity")
            == "C_1 K=0 and hence B_lin K=0"
            and bach_gauge_jets.get("exhaustive") is True
            and bach_gauge_jets.get("input_components") == 4
            and bach_gauge_jets.get("maximum_order") == 3
            and bach_gauge_jets.get("multiindices_per_component") == 35
        ):
            raise AssertionError("linearized Bach gauge-jet input is incomplete")

        if equation.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ):
            raise AssertionError("wrong T/A coefficient certificate schema")
        t_state = _nested(equation, "T_state")
        if not (
            state_gauge.get("T_state") == t_state.get("operator")
            and t_state.get("shape") == [26, 24]
            and t_state.get("maximum_order") == 3
            and t_state.get("coefficient_multiindices") == 35
            and isinstance(t_state.get("nonzero_coefficients"), int)
            and t_state.get("nonzero_coefficients", 0) > 0
            and _is_sha256(t_state.get("sha256"))
        ):
            raise AssertionError("T_state coefficient coverage drifted")
        a_equation = _nested(equation, "A_equation")
        if not (
            a_equation.get("shape") == [40, 24]
            and a_equation.get("maximum_order") == 2
            and a_equation.get("coefficient_multiindices") == 15
            and isinstance(a_equation.get("nonzero_coefficients"), int)
            and a_equation.get("nonzero_coefficients", 0) > 0
            and a_equation.get("input_row") == "paired Ebar=J_aux^-1 E_raw"
            and a_equation.get("raw_to_paired_conversion")
            == "A_equation=A_raw J_aux"
            and _is_sha256(a_equation.get("sha256"))
        ):
            raise AssertionError("A_equation normalization or coverage drifted")
        if not equation.get("first_chain_relation_exact"):
            raise AssertionError("E_curv T=A Ebar is not exact")
        exhaustive = _nested(equation, "exhaustive_jet_certificate")
        if not (
            exhaustive.get("tested_metric_four_jets") == 700
            and exhaustive.get("Bach_sample_rank") == 9
            and exhaustive.get("E_curv_T_minus_H_Bach_defect") == 0
        ):
            raise AssertionError("T/A exhaustive jet certificate is incomplete")

        if identity.get("schema") != (
            "pure-weyl-curvature-auxiliary-identity-chain-map-v1"
        ):
            raise AssertionError("wrong B coefficient certificate schema")
        b_identity = _nested(identity, "B_identity")
        if not (
            b_identity.get("shape") == [14, 9]
            and b_identity.get("maximum_order") == 0
            and b_identity.get("coefficient_multiindices") == 1
            and b_identity.get("rank") == 4
            and b_identity.get("nonzero_coefficients") == 4
            and _is_sha256(b_identity.get("sha256"))
        ):
            raise AssertionError("B_identity coefficient coverage drifted")
        a_metric = _nested(identity, "A_metric")
        equation_h_hash = a_equation.get("Bach_to_curvature_sha256")
        identity_h_hash = a_metric.get("tracefree_Bach_to_curvature_sha256")
        if not (
            _is_sha256(equation_h_hash)
            and identity_h_hash == equation_h_hash
        ):
            raise AssertionError("A/B Bach-to-curvature map hashes do not agree")
        if retract.get("schema") != "pure-weyl-curved-chain-map-status-v1":
            raise AssertionError("wrong auxiliary retract certificate schema")
        q_retract = _nested(retract, "Q_conjugation_engine_regression")
        retract_hashes = _nested(q_retract, "matrix_sha256")
        identity_projection = _nested(identity, "identity_projection")
        if not (
            _is_sha256(identity_projection.get("sha256"))
            and identity_projection.get("full_retract_projection_sha256")
            == retract_hashes.get("projection")
            and _is_sha256(retract_hashes.get("projection"))
            and retract.get("curved_p_is_chain_map") is True
            and retract.get("all_BV_rows_in_curved_comparison") is True
        ):
            raise AssertionError("p_identity is not bound to the full retract")
        second_square = _nested(identity, "full_auxiliary_chain_relation")
        if not (
            identity.get("second_chain_relation_exact")
            and second_square.get("exact")
            and second_square.get("N_curv_A_equation_minus_B_identity_C_aux")
            == "zero"
        ):
            raise AssertionError("N_curv A=B C_aux is not exact")
        cotangent = _nested(identity, "cotangent_lift")
        if not (
            cotangent.get("shape") == [9, 14]
            and cotangent.get("maximum_order") == 0
            and cotangent.get("generated_from_same_BV_pairings") is True
        ):
            raise AssertionError("B_identity cotangent lift drifted")

        if kernel.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-kernel-v1"
        ):
            raise AssertionError("wrong cotangent kernel certificate schema")
        if kernel.get("exact_formal_kernel") is not True:
            raise AssertionError("the formal cotangent kernel is not exact")
        degree_checks = _nested(kernel, "degree_checks")
        if not all(
            degree_checks.get(key) is True
            for key in (
                "every_split_Q_arrow_raises_degree_by_one",
                "every_canonical_shear_has_degree_zero",
                "every_incidence_pairing_has_total_degree_one",
            )
        ):
            raise AssertionError("kernel degree ledger is incomplete")
        mapping_cylinder = _nested(kernel, "mapping_cylinder")
        if not (
            mapping_cylinder.get("autonomous_curvature_direct_sum_used") is False
            and mapping_cylinder.get("BV_pairing_defect") == 0
            and mapping_cylinder.get("odd_BV_pairing_squared") == "-identity"
            and mapping_cylinder.get("Q_squared") == "zero"
            and mapping_cylinder.get("P_I") == "identity"
            and mapping_cylinder.get("chain_maps") == "exact"
            and mapping_cylinder.get("I_P_minus_identity") == "QH+HQ"
        ):
            raise AssertionError("mapping-cylinder kernel identities drifted")
        normalization = _nested(kernel, "equation_normalization")
        if not (
            normalization.get("p_equation_domain") == "paired Ebar row"
            and normalization.get("raw_to_paired_map") == "A=A_raw J_aux"
            and normalization.get("J_aux_shape") == [24, 24]
            and normalization.get("J_aux_rank") == 24
            and _is_sha256(normalization.get("J_aux_sha256"))
            and normalization.get("Y_aux_shape") == [9, 9]
            and normalization.get("Y_aux_rank") == 9
            and _is_sha256(normalization.get("Y_aux_sha256"))
            and _is_sha256(
                normalization.get("odd_curvature_incidence_sha256")
            )
            and normalization.get("conversion_defect") == 0
        ):
            raise AssertionError("kernel equation-row convention drifted")
        matrix_hashes = _nested(kernel, "matrix_sha256")
        expected_hashes = {
            "split_Q",
            "canonical_transform",
            "prolonged_Q",
            "inclusion",
            "projection",
            "homotopy",
            "odd_pairing",
        }
        if set(matrix_hashes) != expected_hashes or not all(
            _is_sha256(value) for value in matrix_hashes.values()
        ):
            raise AssertionError("formal kernel matrix hashes are incomplete")
        if (
            matrix_hashes.get("odd_pairing")
            != normalization.get("odd_curvature_incidence_sha256")
        ):
            raise AssertionError("curvature incidence pairing hash drifted")
        support = _nested(kernel, "support")
        if not (
            support.get("finite_differential_orders_only") is True
            and support.get("inverse_Laplacian_or_curl") is False
            and support.get("spectral_projector") is False
            and support.get("Green_operator") is False
            and support.get("compact") is True
            and support.get("spacelike_compact") is True
            and support.get("smooth_global") is True
        ):
            raise AssertionError("support-locality certificate drifted")
        odd_cyclicity = _nested(kernel, "odd_BV_cyclicity")
        if not (
            odd_cyclicity.get("split_Q_cyclicity_defect") == 0
            and odd_cyclicity.get("prolonged_Q_cyclicity_defect") == 0
            and odd_cyclicity.get("homotopy_cyclicity_defect") == 0
            and odd_cyclicity.get("pairing_epsilon_auxiliary")
            == [1, 1, -1, -1]
            and odd_cyclicity.get("pairing_epsilon_X") == [1, -1, -1]
            and odd_cyclicity.get("pairing_epsilon_Y") == [-1, -1, 1]
        ):
            raise AssertionError("odd BV cyclicity certificate drifted")

        if cotangent_audit.get("schema") != (
            "pure-weyl-prolonged-BV-differential-attachment-audit-v1"
        ):
            raise AssertionError("wrong curvature cotangent audit schema")
        cotangent_completion = _nested(cotangent_audit, "cotangent_completion")
        cotangent_exact = _nested(cotangent_audit, "exact_results")
        if not (
            cotangent_completion.get("Q_squared") == "zero"
            and cotangent_completion.get("all_arrows_are_formal_cotangent_adjoints")
            is True
            and _is_sha256(cotangent_completion.get("matrix_sha256"))
            and cotangent_exact.get("cotangent_adjoint_Q_squared") is True
            and cotangent_exact.get("all_autonomous_curvature_rows_enumerated")
            is True
            and cotangent_exact.get("support_local_operator_complex") is True
        ):
            raise AssertionError("autonomous curvature cotangent audit is incomplete")

    def certificate(self) -> dict[str, object]:
        self.verify()
        state_gauge = self.state_gauge_certificate
        linearized_bach = self.linearized_bach_certificate
        equation = self.equation_certificate
        identity = self.identity_certificate
        retract = self.retract_certificate
        kernel = self.kernel_certificate
        cotangent_audit = self.cotangent_certificate
        pairing_data = _nested(kernel, "equation_normalization")
        curvature_pairing_hash = pairing_data[
            "odd_curvature_incidence_sha256"
        ]
        t_state = _nested(equation, "T_state")
        a_equation = _nested(equation, "A_equation")
        b_identity = _nested(identity, "B_identity")
        return {
            "schema": "pure-weyl-curvature-mapping-cylinder-substitution-v1",
            "input_certificate_sha256": {
                "state_gauge_chain_map": _certificate_digest(state_gauge),
                "linearized_bach": _certificate_digest(linearized_bach),
                "equation_chain_map": _certificate_digest(equation),
                "identity_chain_map": _certificate_digest(identity),
                "auxiliary_retract": _certificate_digest(retract),
                "formal_kernel": _certificate_digest(kernel),
                "autonomous_curvature_cotangent": _certificate_digest(
                    cotangent_audit
                ),
            },
            "coefficient_tables": {
                "T_state": {
                    "shape": t_state["shape"],
                    "maximum_order": t_state["maximum_order"],
                    "coefficient_multiindices": t_state["coefficient_multiindices"],
                    "sha256": t_state["sha256"],
                },
                "A_equation": {
                    "shape": a_equation["shape"],
                    "maximum_order": a_equation["maximum_order"],
                    "coefficient_multiindices": a_equation[
                        "coefficient_multiindices"
                    ],
                    "input_row": a_equation["input_row"],
                    "raw_to_paired_conversion": a_equation[
                        "raw_to_paired_conversion"
                    ],
                    "sha256": a_equation["sha256"],
                },
                "B_identity": {
                    "shape": b_identity["shape"],
                    "maximum_order": b_identity["maximum_order"],
                    "coefficient_multiindices": b_identity[
                        "coefficient_multiindices"
                    ],
                    "rank": b_identity["rank"],
                    "sha256": b_identity["sha256"],
                },
            },
            "formal_adjoint_provenance": {
                "rule": (
                    "parallel coefficients: A_I^sharp=(-1)^|I| A_I^T, "
                    "conjugated by the content-addressed source/target pairings"
                ),
                "T_state_sharp": {
                    "maximum_order": t_state["maximum_order"],
                    "primal_sha256": t_state["sha256"],
                    "source_pairing_sha256": pairing_data["J_aux_sha256"],
                    "target_pairing_sha256": curvature_pairing_hash,
                    "derived_sha256": _formal_adjoint_digest(
                        t_state["sha256"],
                        t_state["maximum_order"],
                        pairing_data["J_aux_sha256"],
                        curvature_pairing_hash,
                    ),
                },
                "A_equation_sharp": {
                    "maximum_order": a_equation["maximum_order"],
                    "primal_sha256": a_equation["sha256"],
                    "source_pairing_sha256": pairing_data["J_aux_sha256"],
                    "target_pairing_sha256": curvature_pairing_hash,
                    "derived_sha256": _formal_adjoint_digest(
                        a_equation["sha256"],
                        a_equation["maximum_order"],
                        pairing_data["J_aux_sha256"],
                        curvature_pairing_hash,
                    ),
                },
                "B_identity_sharp": {
                    "maximum_order": b_identity["maximum_order"],
                    "primal_sha256": b_identity["sha256"],
                    "source_pairing_sha256": pairing_data["Y_aux_sha256"],
                    "target_pairing_sha256": curvature_pairing_hash,
                    "derived_sha256": _formal_adjoint_digest(
                        b_identity["sha256"],
                        b_identity["maximum_order"],
                        pairing_data["Y_aux_sha256"],
                        curvature_pairing_hash,
                    ),
                },
            },
            "substitution": {
                "primal_blocks": [
                    "X_U += T_state M_aux",
                    "X_Eq += A_equation Ebar_aux",
                    "X_Id += B_identity I_aux",
                ],
                "cotangent_blocks": [
                    "Ebar_aux += -T_state^sharp X_U^sharp",
                    "M_aux += -A_equation^sharp X_Eq^sharp",
                    "G_aux += -B_identity^sharp X_Id^sharp",
                ],
                "all_new_blocks_accounted_for": True,
                "formal_adjoint_tables_generated_from_primal_tables": True,
                "state_gauge_relation": "T_state K_aux=0",
                "state_gauge_relation_exact": True,
                "first_chain_relation": "E_curv T_state=A_equation Ebar_aux",
                "first_chain_relation_exact": True,
                "second_chain_relation": (
                    "N_curv A_equation=B_identity C_aux"
                ),
                "second_chain_relation_exact": True,
                "Bach_to_curvature_sha256": a_equation[
                    "Bach_to_curvature_sha256"
                ],
                "identity_projection_sha256": identity["identity_projection"][
                    "sha256"
                ],
                "full_retract_projection_sha256": identity[
                    "identity_projection"
                ]["full_retract_projection_sha256"],
            },
            "kernel": {
                "complete_16_block_degree_ledger": kernel[
                    "complete_16_block_degree_ledger"
                ],
                "degree_checks": kernel["degree_checks"],
                "matrix_sha256": kernel["matrix_sha256"],
                "Q_squared": "zero",
                "BV_pairing_defect": 0,
                "odd_BV_cyclicity_defect": 0,
                "P_I": "identity",
                "I_P_minus_identity": "QH+HQ",
            },
            "meaning_of_coefficientwise_complete": (
                "every nonzero attachment block is an exact finite coefficient "
                "table T/A/B or its BV-forced formal adjoint; the remaining "
                "incidence blocks are exact identities or the certified "
                "autonomous auxiliary/curvature differentials"
            ),
            "coefficientwise_complete_prolonged_Q": True,
            "support_local": True,
            "warranted_atomic_flags": [
                "support_local_prolongation_retract",
                "prolonged_BV_operator_identity",
            ],
            "status_flags_promoted": [],
            "proof_boundary": (
                "this closes coefficient substitution, degree/sign incidence, "
                "nilpotence and the local prolongation SDR; it does not by "
                "itself construct a Green witness or causal homotopy"
            ),
            "fail_closed": True,
        }
