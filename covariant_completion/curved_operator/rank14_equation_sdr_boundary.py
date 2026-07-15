"""Exact boundary for the proposed rank-14/Weyl--Cotton equation SDR.

The tempting state-level quotient

``ker(K_src) / im(C1, div C1)``

does not exist off shell: the curvature state has three generic components
in the secondary constraint rows.  The correct object is the *equation*
complex

``U26 --(L,K)--> F26 + C14 --(-K_src,S)--> I14``.

Its curved identity is exact because the unit-sphere commutator correction
cancels the commuting-symbol defect.  This module records that distinction,
the resulting minimal mapping-cone ledger, the full lower-order coefficient
tables and their formal adjoints.  It deliberately does not manufacture a
seven-dimensional retraction from a quotient which is not defined.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from .rank14_weyl_cotton_symbol_audit import Rank14WeylCottonSymbolAudit
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _digest_tables(tables: tuple[sp.Matrix, ...]) -> str:
    payload = "\n".join(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)) for matrix in tables
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _adjoint_tables(
    derivative: tuple[sp.Matrix, ...], zeroth: sp.Matrix
) -> tuple[sp.Matrix, ...]:
    """Constant-coefficient formal adjoint table in derivative/zero order."""

    return tuple(-matrix.T for matrix in derivative) + (zeroth.T,)


@dataclass(frozen=True)
class Rank14EquationSDRBoundary:
    symbol: Rank14WeylCottonSymbolAudit
    evolution: ConstraintAdjustedWeylCottonEvolution
    field_kernel_rank: int
    equation_derivative_tables: tuple[sp.Matrix, ...]
    equation_zeroth_table: sp.Matrix
    identity_derivative_tables: tuple[sp.Matrix, ...]
    identity_zeroth_table: sp.Matrix
    equation_adjoint_tables: tuple[sp.Matrix, ...]
    identity_adjoint_tables: tuple[sp.Matrix, ...]

    @staticmethod
    def build() -> "Rank14EquationSDRBoundary":
        symbol = Rank14WeylCottonSymbolAudit.build()
        evolution = ConstraintAdjustedWeylCottonEvolution.build()

        # E=(L,K).  Table order is time, three spatial derivatives, zeroth.
        equation_derivative: list[sp.Matrix] = [
            sp.eye(26).col_join(sp.zeros(14, 26))
        ]
        equation_derivative.extend(
            evolution.evolution_spatial_coefficients[axis].col_join(
                evolution.source_compatibility_spatial_coefficients[axis]
            )
            for axis in range(3)
        )
        equation_zero = evolution.evolution_zeroth_coefficient.col_join(
            evolution.source_compatibility_zeroth_coefficient
        )

        # N=(-K_src,S).  Its exact composition with E is the sourced
        # subsidiary identity, including the noncommuting S3 correction.
        identity_derivative: list[sp.Matrix] = [
            sp.zeros(14, 26).row_join(sp.eye(14))
        ]
        identity_derivative.extend(
            (-evolution.source_compatibility_spatial_coefficients[axis]).row_join(
                evolution.constraint_spatial_coefficients[axis]
            )
            for axis in range(3)
        )
        identity_zero = (-evolution.source_compatibility_zeroth_coefficient).row_join(
            evolution.constraint_zeroth_coefficient
        )

        equation_adjoint = _adjoint_tables(
            tuple(equation_derivative), equation_zero
        )
        identity_adjoint = _adjoint_tables(
            tuple(identity_derivative), identity_zero
        )

        result = Rank14EquationSDRBoundary(
            symbol=symbol,
            evolution=evolution,
            field_kernel_rank=14 - symbol.local_prolonged_map.rank(),
            equation_derivative_tables=tuple(equation_derivative),
            equation_zeroth_table=equation_zero,
            identity_derivative_tables=tuple(identity_derivative),
            identity_zeroth_table=identity_zero,
            equation_adjoint_tables=equation_adjoint,
            identity_adjoint_tables=identity_adjoint,
        )
        result.verify()
        return result

    def verify(self) -> None:
        local = self.symbol.local_prolonged_map
        compatibility = self.symbol.compatibility_symbol
        if local.shape != (26, 14) or local.rank() != 5:
            raise AssertionError("rank-14 descended curvature map drifted")
        if self.field_kernel_rank != 9:
            raise AssertionError("U9=ker(R) drifted")
        if compatibility.shape != (14, 26) or compatibility.rank() != 14:
            raise AssertionError("compatible-source presentation drifted")
        if 26 - compatibility.rank() != 12:
            raise AssertionError("K12 compatible-source kernel drifted")
        defect_rank = (compatibility * self.symbol.state_symbol_fields).rank()
        if defect_rank != 3:
            raise AssertionError("off-shell curvature constraint defect is not rank three")
        if self.symbol.state_symbol_fields.rank() - defect_rank != 2:
            raise AssertionError("generic common core is not rank two")

        if len(self.equation_derivative_tables) != 4 or any(
            table.shape != (40, 26) for table in self.equation_derivative_tables
        ):
            raise AssertionError("E=(L,K) derivative table coverage drifted")
        if self.equation_zeroth_table.shape != (40, 26):
            raise AssertionError("wrong E=(L,K) zeroth table")
        if len(self.identity_derivative_tables) != 4 or any(
            table.shape != (14, 40) for table in self.identity_derivative_tables
        ):
            raise AssertionError("N=(-K_src,S) derivative table coverage drifted")
        if self.identity_zeroth_table.shape != (14, 40):
            raise AssertionError("wrong N=(-K_src,S) zeroth table")
        if self.evolution.commuting_symbol_defect == sp.zeros(14, 26):
            raise AssertionError("sphere commutator correction was silently dropped")
        if (
            self.evolution.commuting_symbol_defect
            + self.evolution.sphere_curvature_correction
            != sp.zeros(14, 26)
        ):
            raise AssertionError("curved sourced subsidiary identity regressed")

        expected_eq_adjoint = _adjoint_tables(
            self.equation_derivative_tables, self.equation_zeroth_table
        )
        expected_id_adjoint = _adjoint_tables(
            self.identity_derivative_tables, self.identity_zeroth_table
        )
        if self.equation_adjoint_tables != expected_eq_adjoint:
            raise AssertionError("equation formal-adjoint table drifted")
        if self.identity_adjoint_tables != expected_id_adjoint:
            raise AssertionError("identity formal-adjoint table drifted")

    def certificate(
        self,
        *,
        helicity_certificate: Mapping[str, object],
        equation_chain_certificate: Mapping[str, object],
        identity_chain_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        weyl = helicity_certificate.get("linearized_Weyl_symbol")
        if helicity_certificate.get("schema") != (
            "pure-weyl-curved-helicity-two-channel-v1"
        ) or not isinstance(weyl, Mapping):
            raise AssertionError("wrong helicity-two input")
        if weyl.get("induced_quotient_matrix") != [["1/4", "0"], ["0", "1/4"]]:
            raise AssertionError("R restricted to H2 is not one quarter I2")
        if equation_chain_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ) or not equation_chain_certificate.get("first_chain_relation_exact"):
            raise AssertionError("full auxiliary equation square unavailable")
        if identity_chain_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-identity-chain-map-v1"
        ) or not identity_chain_certificate.get("second_chain_relation_exact"):
            raise AssertionError("full auxiliary identity square unavailable")

        defect = self.symbol.compatibility_symbol * self.symbol.state_symbol_fields
        defect_rows = sorted(
            {
                row
                for row in range(defect.rows)
                if any(defect[row, column] != 0 for column in range(defect.cols))
            }
        )
        return {
            "schema": "pure-weyl-rank14-equation-sdr-boundary-v1",
            "scope": (
                "exact rank/Douglis boundary plus the complete curved Weyl--Cotton "
                "equation/identity complex; no rank-14 Green homotopy is claimed"
            ),
            "proposed_state_SDR_audit": {
                "F14_rank": 14,
                "R_rank": self.symbol.local_prolonged_map.rank(),
                "U9_equals_kernel_R_rank": self.field_kernel_rank,
                "K_source_row_rank": self.symbol.compatibility_symbol.rank(),
                "K12_compatible_kernel_rank": 26 - self.symbol.compatibility_symbol.rank(),
                "K_R_generic_defect_rank": defect.rank(),
                "K_R_nonzero_row_indices": defect_rows,
                "im_R_intersection_K12_rank": (
                    self.symbol.state_symbol_fields.rank() - defect.rank()
                ),
                "K12_mod_common_core_rank": 10,
                "claimed_V7_equals_K12_mod_imR_is_defined": False,
                "reason": "im(R) is not contained in ker(K) off shell",
                "strict_SR_state_retraction_rejected": True,
            },
            "correct_equation_complex": {
                "objects": ["U_WC[26]", "F_WC[26]+C_WC[14]", "I_WC[14]"],
                "first_arrow": "E_curv=(L_26,K_state)",
                "second_arrow": "N_curv=(-K_src,S_14)",
                "identity": "N_curv E_curv=0",
                "commuting_symbol_defect_nonzero": True,
                "unit_S3_PBW_correction_exact": True,
                "equation_table_sha256": _digest_tables(
                    self.equation_derivative_tables + (self.equation_zeroth_table,)
                ),
                "identity_table_sha256": _digest_tables(
                    self.identity_derivative_tables + (self.identity_zeroth_table,)
                ),
                "equation_adjoint_sha256": _digest_tables(
                    self.equation_adjoint_tables
                ),
                "identity_adjoint_sha256": _digest_tables(
                    self.identity_adjoint_tables
                ),
                "all_curvature_lower_order_terms_included": True,
                "source_compatibility_operator_included": True,
                "formal_adjoints_included": True,
            },
            "auxiliary_derived_closure": {
                "first_square": "E_curv T_state=A_equation E_aux",
                "second_square": "N_curv A_equation=B_identity C_aux",
                "first_square_exact": True,
                "second_square_exact": True,
                "interpretation": (
                    "the three transverse-to-compatibility curvature directions "
                    "are closed only after retaining the auxiliary equation image"
                ),
            },
            "canonical_relative_cone": {
                "carrier": "U_WC[26] plus Ebar_aux[24]",
                "constraint": "Khat(s,e)=K_state(s)-A_C(e)",
                "graph_map": "That(phi)=(T(phi),E_aux(phi))",
                "closure_identity": "Khat That=K_state T-A_C E_aux=0",
                "closure_exact": True,
                "derivation": "constraint component of E_curv T=A E_aux",
                "support_local": True,
                "maximum_orders": {
                    "T": 3,
                    "E_aux": 2,
                    "K_state": 1,
                    "A_C": 2,
                },
                "requires_projector": False,
                "retained_when_strict_source_correction_fails": True,
            },
            "requested_AF_candidate_type_audit": {
                "requested_formula": "K_state A_F=A_C on ker C_aux",
                "literally_typed": False,
                "reason": (
                    "A_F lands in F_source, so its outgoing operator is R_src, "
                    "not K_state; A_C lands in C_constraint and is followed by S"
                ),
                "correct_formula_on_equation_cycles": (
                    "R_src A_F=S A_C on ker C_aux"
                ),
                "derivation": "(-R_src,S)A=B C_aux",
                "corrected_pair_is_N_closed": True,
                "A_F_alone_is_R_src_closed": False,
                "candidate_T_rel_defined": False,
                "reason_T_rel_not_formed": (
                    "T lands in U_state while A_F E_aux lands in F_source; a "
                    "coordinate identification would not be a typed chain map"
                ),
            },
            "null_physical_regression": {
                "Weyl_image_mod_gauge_preimages_split": "B3 plus H2",
                "H2_rank": 2,
                "R_restricted_to_H2": "(1/4) I2",
                "R_restricted_to_H2_invertible": True,
                "is_not_identified_with_ker_K_quotient": True,
            },
            "minimum_mapping_cone_ledger": {
                "off_shell_constraint_directions_that_must_be_retained": 3,
                "generic_compatible_complement_after_true_common_core": 10,
                "field_kernel_requiring_equation_homotopy_rank": self.field_kernel_rank,
                "minimum_new_primal_rows_if_auxiliary_equation_rows_are_not_reused": 3,
                "minimum_cyclic_dual_rows_in_that_case": 3,
                "existing_auxiliary_equation_rows_must_be_tested_before_adding_pairs": True,
                "seven_direction_search_on_K12_mod_imR_should_stop": True,
            },
            "support_and_pairing": {
                "E_and_N_maximum_order": 1,
                "finite_order": True,
                "support_local": True,
                "inverse_Laplacian_or_curl": False,
                "spectral_projector": False,
                "formal_adjoint_rule": "A_I^sharp=(-1)^|I| A_I^T",
                "cyclic_completion_requires_displayed_adjoint_tables": True,
            },
            "decision": {
                "rank14_equation_SDR_constructed": False,
                "rank14_green_operators_constructed": False,
                "next_exact_target": (
                    "retain the canonical relative cone and compute the derived "
                    "equation quotient ker(N_curv)/im(E_curv) together with the "
                    "auxiliary A/B maps, rather than the invalid state quotient"
                ),
            },
            "warranted_atomic_flags": {
                "rank14_fake_state_SDR_rejected": True,
                "rank14_full_equation_cone_required": True,
            },
            "status_flags_promoted": [],
            "fail_closed": True,
        }


def certificate_from_verified_inputs(
    *,
    symbol_certificate: Mapping[str, object],
    helicity_certificate: Mapping[str, object],
    equation_chain_certificate: Mapping[str, object],
    identity_chain_certificate: Mapping[str, object],
    cycle_gate_certificate: Mapping[str, object],
) -> dict[str, object]:
    """Compose the boundary without rebuilding the expensive Weyl symbol.

    The upstream symbol certificate is content-checked below and has its own
    exact verifier.  All full lower-order Weyl--Cotton and adjoint tables are
    rebuilt here; this keeps the compositional verifier fast.
    """

    if symbol_certificate.get("schema") != (
        "pure-weyl-rank14-weyl-cotton-symbol-audit-v1"
    ):
        raise AssertionError("wrong rank-14 symbol certificate")
    dimensions = symbol_certificate.get("dimension_ledger")
    comparison = symbol_certificate.get("image_kernel_comparison")
    cone = symbol_certificate.get("exact_chain_square_replacement")
    if not all(isinstance(value, Mapping) for value in (dimensions, comparison, cone)):
        raise AssertionError("incomplete rank-14 symbol boundary")
    assert isinstance(dimensions, Mapping)
    assert isinstance(comparison, Mapping)
    assert isinstance(cone, Mapping)
    if (
        dimensions.get("U14_domain"),
        dimensions.get("U9_kernel_of_raw_curvature_map"),
        dimensions.get("I5_raw_curvature_image"),
        dimensions.get("K12_compatible_kernel"),
        dimensions.get("H2_generic_common_core"),
        dimensions.get("V10_compatible_mod_common_core"),
        dimensions.get("proposed_V7_equals_K12_mod_I5_is_defined"),
    ) != (14, 9, 5, 12, 2, 10, False):
        raise AssertionError("rank-14 dimension ledger drifted")
    if comparison.get("K_weighted_R_generic_defect_rank") != 3:
        raise AssertionError("off-shell constraint defect drifted")

    weyl = helicity_certificate.get("linearized_Weyl_symbol")
    if helicity_certificate.get("schema") != (
        "pure-weyl-curved-helicity-two-channel-v1"
    ) or not isinstance(weyl, Mapping) or weyl.get(
        "induced_quotient_matrix"
    ) != [["1/4", "0"], ["0", "1/4"]]:
        raise AssertionError("helicity-two input drifted")
    if equation_chain_certificate.get("schema") != (
        "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
    ) or not equation_chain_certificate.get("first_chain_relation_exact"):
        raise AssertionError("first auxiliary chain square unavailable")
    if identity_chain_certificate.get("schema") != (
        "pure-weyl-curvature-auxiliary-identity-chain-map-v1"
    ) or not identity_chain_certificate.get("second_chain_relation_exact"):
        raise AssertionError("second auxiliary chain square unavailable")
    if cycle_gate_certificate.get("schema") != (
        "pure-weyl-rank14-equation-cycle-gate-v1"
    ):
        raise AssertionError("wrong equation-cycle gate")
    cycle_translation = cycle_gate_certificate.get("typed_translation")
    cycle_cone = cycle_gate_certificate.get("canonical_equation_cone")
    literal = cycle_gate_certificate.get("literal_shorthand_audit")
    if not all(
        isinstance(value, Mapping)
        for value in (cycle_translation, cycle_cone, literal)
    ):
        raise AssertionError("incomplete equation-cycle gate")
    assert isinstance(cycle_translation, Mapping)
    assert isinstance(cycle_cone, Mapping)
    assert isinstance(literal, Mapping)
    if (
        cycle_translation.get("cycle_relation_defect") != 0
        or cycle_cone.get("Ncurv_cycle_defect") != 0
        or cycle_cone.get("generic_rank") != 5
        or literal.get("literally_well_typed") is not False
        or literal.get("degree_three_term_generic_rank") != 3
    ):
        raise AssertionError("typed equation-cycle result drifted")

    evolution = ConstraintAdjustedWeylCottonEvolution.build()
    equation_derivative = (
        sp.eye(26).col_join(sp.zeros(14, 26)),
        *tuple(
            evolution.evolution_spatial_coefficients[axis].col_join(
                evolution.source_compatibility_spatial_coefficients[axis]
            )
            for axis in range(3)
        ),
    )
    equation_zero = evolution.evolution_zeroth_coefficient.col_join(
        evolution.source_compatibility_zeroth_coefficient
    )
    identity_derivative = (
        sp.zeros(14, 26).row_join(sp.eye(14)),
        *tuple(
            (-evolution.source_compatibility_spatial_coefficients[axis]).row_join(
                evolution.constraint_spatial_coefficients[axis]
            )
            for axis in range(3)
        ),
    )
    identity_zero = (-evolution.source_compatibility_zeroth_coefficient).row_join(
        evolution.constraint_zeroth_coefficient
    )
    equation_adjoint = _adjoint_tables(equation_derivative, equation_zero)
    identity_adjoint = _adjoint_tables(identity_derivative, identity_zero)
    if evolution.commuting_symbol_defect + evolution.sphere_curvature_correction != sp.zeros(14, 26):
        raise AssertionError("curved sourced subsidiary identity regressed")

    return {
        "schema": "pure-weyl-rank14-equation-sdr-boundary-v1",
        "scope": "compositional exact equation-cone boundary; no Green promotion",
        "proposed_state_SDR_audit": {
            "F14_rank": 14,
            "R_rank": 5,
            "U9_equals_kernel_R_rank": 9,
            "K_source_row_rank": 14,
            "K12_compatible_kernel_rank": 12,
            "K_R_generic_defect_rank": 3,
            "im_R_intersection_K12_rank": 2,
            "K12_mod_common_core_rank": 10,
            "claimed_V7_equals_K12_mod_imR_is_defined": False,
            "strict_SR_state_retraction_rejected": True,
        },
        "correct_equation_complex": {
            "objects": ["U_WC[26]", "F_WC[26]+C_WC[14]", "I_WC[14]"],
            "identity": "N_curv E_curv=0",
            "commuting_symbol_defect_nonzero": True,
            "unit_S3_PBW_correction_exact": True,
            "all_curvature_lower_order_terms_included": True,
            "formal_adjoints_included": True,
            "equation_table_sha256": _digest_tables(equation_derivative + (equation_zero,)),
            "identity_table_sha256": _digest_tables(identity_derivative + (identity_zero,)),
            "equation_adjoint_sha256": _digest_tables(equation_adjoint),
            "identity_adjoint_sha256": _digest_tables(identity_adjoint),
        },
        "auxiliary_derived_closure": {
            "first_square_exact": True,
            "second_square_exact": True,
        },
        "canonical_relative_cone": {
            "carrier": "U_WC[26] plus Ebar_aux[24]",
            "constraint": "Khat(s,e)=K_state(s)-A_C(e)",
            "graph_map": "That(phi)=(T(phi),E_aux(phi))",
            "closure_exact": True,
            "support_local": True,
            "requires_projector": False,
        },
        "requested_AF_candidate_type_audit": {
            "requested_formula": "K_state A_F=A_C on ker C_aux",
            "literally_typed": False,
            "correct_formula_on_equation_cycles": "R_src A_F=S A_C on ker C_aux",
            "corrected_pair_is_N_closed": True,
            "A_F_alone_is_R_src_closed": False,
            "candidate_T_rel_defined": False,
            "cycle_gate_cross_certificate": "curved_rank14_equation_cycle_gate.json",
        },
        "null_physical_regression": {
            "H2_rank": 2,
            "R_restricted_to_H2": "(1/4) I2",
            "R_restricted_to_H2_invertible": True,
            "is_not_identified_with_ker_K_quotient": True,
        },
        "minimum_mapping_cone_ledger": {
            "off_shell_constraint_directions_that_must_be_retained": 3,
            "generic_compatible_complement_after_true_common_core": 10,
            "field_kernel_requiring_equation_homotopy_rank": 9,
            "minimum_new_primal_rows_if_auxiliary_equation_rows_are_not_reused": 3,
            "minimum_cyclic_dual_rows_in_that_case": 3,
        },
        "decision": {
            "rank14_equation_SDR_constructed": False,
            "rank14_green_operators_constructed": False,
        },
        "warranted_atomic_flags": {
            "rank14_fake_state_SDR_rejected": True,
            "rank14_full_equation_cone_required": True,
        },
        "status_flags_promoted": [],
        "fail_closed": True,
    }
