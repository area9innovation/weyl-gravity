"""Typed incoming-map ledger for the rank-fourteen equation SDR.

There are two isomorphic-looking, but differently typed, copies of the
Weyl--Cotton rank-fourteen operator.  The state constraint operator is

``K_state : U[26] -> C[14]``

whereas source compatibility is

``R_src : F[26] -> I[14]``.

Their coefficient tables agree in the canonical cylinder coordinates, but
their roles in the complex must not be conflated.  The exact curvature
equation complex is

``U --(L,K_state)--> F+C --(-R_src,S)--> I``.

The support-local auxiliary attachment supplies the three chain-map rows

``T : M_aux -> U``, ``A=(A_F,A_C) : Ebar_aux -> F+C`` and
``B : I_aux -> I``

with ``(L,K_state)T=A E_aux`` and ``(-R_src,S)A=B C_aux``.  Thus ``T`` is
not required to be a constrained state off shell: its secondary constraint
defect is exactly the constraint component ``A_C E_aux``.

This module inventories the authoritative bases, coefficient tables and
principal ranks needed by the rank-fourteen equation SDR.  It deliberately
does not construct that SDR or resume the curved PBW lower-order solve.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from .weyl_cotton_hyperbolic import (
    CONSTRAINT_DIMENSION,
    EVOLUTION_DIMENSION,
    ConstraintAdjustedWeylCottonEvolution,
)


STATE_BASIS = (
    "E_STF[5]",
    "B_STF[5]",
    "A_STF[5]",
    "C_STF[5]",
    "x[3]",
    "y[3]",
)
CONSTRAINT_BASIS = ("q[3]", "r[3]", "a[3]", "c[3]", "s[1]", "t[1]")
AUXILIARY_FIELD_BASIS = ("h[10]", "f[10]", "v[4]")
AUXILIARY_IDENTITY_BASIS = ("xi_minus_2_star[4]", "xi_0_star[4]", "sigma_star[1]")
BACH_BASIS = ("scalar[1]", "mixed[3]", "spatial_STF[5]")


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _tuple_digest(matrices: tuple[sp.Matrix, ...]) -> str:
    return hashlib.sha256(
        "\n".join(_digest(matrix) for matrix in matrices).encode("ascii")
    ).hexdigest()


def _nested(value: Mapping[str, object], key: str) -> Mapping[str, object]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return result


def _bach_to_curvature() -> sp.Matrix:
    """Constant rank-nine map into the adjusted forty equation rows."""

    result = sp.zeros(40, 9)
    # F order is E,B,A,C,x,y.  Only the five A_STF source rows occur.
    result[10:15, 4:9] = -sp.eye(5) / 2
    # C order is q,r,a,c,s,t.  The remaining Bach rows occur in a and s.
    result[26 + 6 : 26 + 9, 1:4] = -sp.eye(3) / 2
    result[26 + 12, 0] = -sp.Rational(3, 2)
    return result


def _auxiliary_identity_map() -> sp.Matrix:
    """The exact order-zero ``B:I_aux[9] -> I_curv[14]`` table."""

    result = sp.zeros(14, 9)
    # xi_0_star order is temporal, spatial 1/2/3 in columns 4..7.
    result[6:9, 5:8] = -sp.eye(3) / 4
    result[12, 4] = -sp.Rational(1, 4)
    return result


@dataclass(frozen=True)
class Rank14WeylCottonIncomingMapLedger:
    evolution: ConstraintAdjustedWeylCottonEvolution
    state_constraint_tables: tuple[sp.Matrix, ...]
    source_compatibility_tables: tuple[sp.Matrix, ...]
    equation_complex_tables: tuple[sp.Matrix, ...]
    identity_complex_tables: tuple[sp.Matrix, ...]
    bach_to_curvature: sp.Matrix
    auxiliary_identity_map: sp.Matrix

    @staticmethod
    def build() -> "Rank14WeylCottonIncomingMapLedger":
        evolution = ConstraintAdjustedWeylCottonEvolution.build()
        # Table order is temporal, space 1/2/3, zeroth.  K_state and R_src
        # have equal coefficients but retain distinct source/target types.
        k_state = (
            sp.zeros(CONSTRAINT_DIMENSION, EVOLUTION_DIMENSION),
            *evolution.source_compatibility_spatial_coefficients,
            evolution.source_compatibility_zeroth_coefficient,
        )
        r_src = tuple(matrix.copy() for matrix in k_state)
        e_curv = tuple(
            upper.col_join(lower)
            for upper, lower in zip(
                (
                    sp.eye(EVOLUTION_DIMENSION),
                    *evolution.evolution_spatial_coefficients,
                    evolution.evolution_zeroth_coefficient,
                ),
                k_state,
                strict=True,
            )
        )
        n_curv = tuple(
            (-source).row_join(subsidiary)
            for source, subsidiary in zip(
                r_src,
                (
                    sp.eye(CONSTRAINT_DIMENSION),
                    *evolution.constraint_spatial_coefficients,
                    evolution.constraint_zeroth_coefficient,
                ),
                strict=True,
            )
        )
        result = Rank14WeylCottonIncomingMapLedger(
            evolution=evolution,
            state_constraint_tables=k_state,
            source_compatibility_tables=r_src,
            equation_complex_tables=e_curv,
            identity_complex_tables=n_curv,
            bach_to_curvature=_bach_to_curvature(),
            auxiliary_identity_map=_auxiliary_identity_map(),
        )
        result.verify()
        return result

    def symbol(
        self,
        tables: tuple[sp.Matrix, ...],
        covector: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr],
    ) -> sp.Matrix:
        tau, *spatial = covector
        return (
            tau * tables[0]
            + sum(
                (spatial[axis] * tables[axis + 1] for axis in range(3)),
                sp.zeros(tables[0].rows, tables[0].cols),
            )
            + tables[4]
        ).applyfunc(sp.expand)

    def _sample(self, covector: tuple[int, int, int, int]) -> dict[str, int]:
        e_symbol = self.symbol(self.equation_complex_tables, covector)
        n_symbol = self.symbol(self.identity_complex_tables, covector)
        return {
            "Ecurv_rank": e_symbol.rank(),
            "Ncurv_rank": n_symbol.rank(),
            "Ecurv_kernel_rank": EVOLUTION_DIMENSION - e_symbol.rank(),
            "Ncurv_kernel_rank": 40 - n_symbol.rank(),
        }

    def verify(self) -> None:
        self.evolution.verify()
        if len(self.state_constraint_tables) != 5 or any(
            matrix.shape != (14, 26) for matrix in self.state_constraint_tables
        ):
            raise AssertionError("K_state coefficient ledger drifted")
        if self.state_constraint_tables is self.source_compatibility_tables:
            raise AssertionError("typed K_state/R_src copies were aliased")
        if any(
            left != right
            for left, right in zip(
                self.state_constraint_tables,
                self.source_compatibility_tables,
                strict=True,
            )
        ):
            raise AssertionError("canonical K_state/R_src tables differ")
        if any(matrix.shape != (40, 26) for matrix in self.equation_complex_tables):
            raise AssertionError("Ecurv=(L,K_state) table shape drifted")
        if any(matrix.shape != (14, 40) for matrix in self.identity_complex_tables):
            raise AssertionError("Ncurv=(-R_src,S) table shape drifted")

        # Ordinary commuting symbols miss exactly the parallel-curvature
        # correction already certified by the Weyl--Cotton package.
        tau, x1, x2, x3 = sp.symbols("ledger_tau ledger_x1 ledger_x2 ledger_x3")
        e_symbol = self.symbol(self.equation_complex_tables, (tau, x1, x2, x3))
        n_symbol = self.symbol(self.identity_complex_tables, (tau, x1, x2, x3))
        if (n_symbol * e_symbol).applyfunc(sp.expand) != (
            -self.evolution.sphere_curvature_correction
        ):
            raise AssertionError("curved SK-RL correction drifted")

        if self.bach_to_curvature.shape != (40, 9):
            raise AssertionError("wrong Bach equation map shape")
        if self.bach_to_curvature.rank() != 9:
            raise AssertionError("Bach equation map rank drifted")
        if self.bach_to_curvature[:26, :].rank() != 5:
            raise AssertionError("A_F Bach-row rank drifted")
        if self.bach_to_curvature[26:, :].rank() != 4:
            raise AssertionError("A_C Bach-row rank drifted")
        if self.auxiliary_identity_map.shape != (14, 9):
            raise AssertionError("wrong auxiliary identity map shape")
        if self.auxiliary_identity_map.rank() != 4:
            raise AssertionError("B identity rank drifted")
        if set(self.auxiliary_identity_map[:, :4]) != {0}:
            raise AssertionError("B unexpectedly uses xi_minus_2_star")
        if set(self.auxiliary_identity_map[:, 8:9]) != {0}:
            raise AssertionError("B unexpectedly uses the Weyl identity")

        expected_samples = {
            (2, 1, 0, 0): {"Ecurv_rank": 26, "Ncurv_rank": 14,
                            "Ecurv_kernel_rank": 0, "Ncurv_kernel_rank": 26},
            (0, 1, 0, 0): {"Ecurv_rank": 26, "Ncurv_rank": 14,
                            "Ecurv_kernel_rank": 0, "Ncurv_kernel_rank": 26},
            (1, 1, 0, 0): {"Ecurv_rank": 26, "Ncurv_rank": 14,
                            "Ecurv_kernel_rank": 0, "Ncurv_kernel_rank": 26},
            (1, 0, 0, 0): {"Ecurv_rank": 26, "Ncurv_rank": 14,
                            "Ecurv_kernel_rank": 0, "Ncurv_kernel_rank": 26},
        }
        for covector, expected in expected_samples.items():
            if self._sample(covector) != expected:
                raise AssertionError(f"complex symbol ranks drifted at {covector}")

    def certificate(
        self,
        *,
        symbol_certificate: Mapping[str, object],
        equation_certificate: Mapping[str, object],
        identity_certificate: Mapping[str, object],
        substitution_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if symbol_certificate.get("schema") != (
            "pure-weyl-rank14-weyl-cotton-symbol-audit-v1"
        ):
            raise AssertionError("wrong rank-14 symbol input")
        comparison = _nested(symbol_certificate, "image_kernel_comparison")
        dimensions = _nested(symbol_certificate, "dimension_ledger")
        if not (
            comparison.get("K_weighted_R_generic_defect_rank") == 3
            and comparison.get("generic_image_rank") == 5
            and comparison.get("generic_compatible_rank") == 12
            and comparison.get("generic_common_core_rank") == 2
            and dimensions.get("proposed_V7_equals_K12_mod_I5_is_defined") is False
        ):
            raise AssertionError("raw curvature/source compatibility audit drifted")
        if equation_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ) or not equation_certificate.get("first_chain_relation_exact"):
            raise AssertionError("first attachment chain square unavailable")
        if identity_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-identity-chain-map-v1"
        ) or not identity_certificate.get("second_chain_relation_exact"):
            raise AssertionError("second attachment chain square unavailable")
        if substitution_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ):
            raise AssertionError("mapping-cylinder coefficient package unavailable")

        return {
            "schema": "pure-weyl-rank14-weyl-cotton-incoming-map-ledger-v1",
            "purpose": (
                "typed exact inputs for the principal H7/equation-SDR decision; "
                "no lower-order PBW solve or Green promotion"
            ),
            "bases": {
                "U_state_26": list(STATE_BASIS),
                "F_source_26": list(STATE_BASIS),
                "C_constraint_14": list(CONSTRAINT_BASIS),
                "I_identity_14": list(CONSTRAINT_BASIS),
                "auxiliary_fields_and_paired_equations_24": list(
                    AUXILIARY_FIELD_BASIS
                ),
                "auxiliary_identities_9": list(AUXILIARY_IDENTITY_BASIS),
                "action_Bach_9": list(BACH_BASIS),
            },
            "typed_curvature_complex": {
                "first_arrow": "Ecurv=(L_26,K_state):U_26 -> F_26+C_14",
                "second_arrow": "Ncurv=(-R_src,S_14):F_26+C_14 -> I_14",
                "K_state_and_R_src_coefficients_equal": True,
                "K_state_and_R_src_types_equal": False,
                "K_state_table_sha256": _tuple_digest(
                    self.state_constraint_tables
                ),
                "R_src_table_sha256": _tuple_digest(
                    self.source_compatibility_tables
                ),
                "exact_operator_identity": "Ncurv Ecurv=0",
                "commuting_symbol_defect": "-unit-S3 curvature correction",
                "commuting_symbol_defect_rank": (
                    self.evolution.sphere_curvature_correction.rank()
                ),
                "sample_symbol_ranks": {
                    str(covector): self._sample(covector)
                    for covector in (
                        (2, 1, 0, 0),
                        (0, 1, 0, 0),
                        (1, 1, 0, 0),
                        (1, 0, 0, 0),
                    )
                },
            },
            "incoming_auxiliary_chain_map": {
                "T": "M_aux[24] -> U[26], order 3",
                "A": "Ebar_aux[24] -> F[26]+C[14], order 2",
                "B": "I_aux[9] -> I[14], order 0",
                "first_square": "(L,K_state) T=A E_aux",
                "first_square_split": [
                    "L T=A_F E_aux",
                    "K_state T=A_C E_aux",
                ],
                "second_square": "(-R_src,S) A=B C_aux",
                "cotangent_rows": ["Tsharp", "Asharp", "Bsharp"],
                "cotangent_rows_forced_by_same_BV_pairings": True,
            },
            "constant_equation_row_map": {
                "shape": [40, 9],
                "rank": self.bach_to_curvature.rank(),
                "F_component_rank": self.bach_to_curvature[:26, :].rank(),
                "F_component_support": "A_STF[5]",
                "C_component_rank": self.bach_to_curvature[26:, :].rank(),
                "C_component_support": "a[3]+s[1]",
                "sha256": _digest(self.bach_to_curvature),
            },
            "identity_row_map": {
                "shape": [14, 9],
                "rank": self.auxiliary_identity_map.rank(),
                "support": "I_a[3]+I_s[1] from xi_0_star[4]",
                "sha256": _digest(self.auxiliary_identity_map),
            },
            "raw_curvature_compatibility_diagnostic": {
                "raw_descended_map_rank": comparison["generic_image_rank"],
                "K_weighted_raw_map_defect_rank": comparison[
                    "K_weighted_R_generic_defect_rank"
                ],
                "compatible_kernel_rank": comparison[
                    "generic_compatible_rank"
                ],
                "raw_common_core_rank": comparison[
                    "generic_common_core_rank"
                ],
                "raw_map_may_instantiate_compatible_source_inclusion": False,
                "reason": "its other three directions source secondary constraints",
                "typed_warning": (
                    "do not replace K_state by R_src or discard A_C; a corrected "
                    "source inclusion may still define a V7 quotient"
                ),
            },
            "correct_principal_target": {
                "equation_cycles": "e in ker C_aux",
                "closed_image": "A(e) in ker Ncurv because N A=B C_aux",
                "quotient": "ker Ncurv / im Ecurv with the auxiliary equation rows",
                "candidate_corrected_equation_source_map": (
                    "e |-> [(A_F e,A_C e)] for e in ker C_aux"
                ),
                "candidate_F_component": "A_F restricted to ker C_aux",
                "A_F_is_independently_R_src_closed": False,
                "reason": (
                    "the exact closure relation is R_src A_F=S A_C on "
                    "ker C_aux; the constraint-source component cannot be dropped"
                ),
                "required_H7_task": (
                    "contract or lift A_C inside the derived equation quotient, "
                    "then identify the resulting compatible F-source class"
                ),
                "plain_state_kernel_quotient_is_the_target": False,
                "principal_H7_contraction_certified": False,
                "lower_order_PBW_work_may_resume": False,
            },
            "cross_certificates": {
                "raw_symbol_audit": "curved_rank14_weyl_cotton_symbol_audit.json",
                "equation_chain_map": "curved_curvature_auxiliary_chain_map.json",
                "identity_chain_map": "curved_curvature_identity_chain_map.json",
                "mapping_cylinder_tables": (
                    "curved_curvature_mapping_cylinder_substitution.json"
                ),
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "status_flags_promoted": [],
            "fail_closed": True,
        }
