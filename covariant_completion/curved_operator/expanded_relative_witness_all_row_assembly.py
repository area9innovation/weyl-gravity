"""Fail-closed all-row assembly theorem for the shifted relative witness.

This module does not invent the missing rank-fourteen curvature-field
cokernel.  It records how every currently certified Green block fits into
the complete shifted/mapping-cylinder ledger and proves the remaining block
algebra conditionally on one explicit ``R14`` package.

There are two ledgers and they must not be confused.  The 116-component
analytic symbol has the disjoint decomposition

``F34 + v[4] + U[26] + Fsharp[26] + Usharp[26]``.

The rank-34 term has the exact filtration ``F12 -> F34 -> F8+F14``.  The
restricted TT biwave plus ``f_hat`` theorem is evidence inside ``F14``; it is
not a support-local direct summand and is therefore not counted a second
time.  Likewise the rank-four field singleton closes to a rank-sixteen BV
contractible summand once its primal and cotangent partners are included.

The sixteen-block curvature mapping cylinder is the all-BV-row incidence
ledger.  Its differential, canonical shear, cotangent signs and local SDR
are already coefficientwise exact.  In split coordinates a replacement
witness is the direct sum of the sector witnesses below; conjugation by the
certified shear transports both ``W`` and ``P=QW+WQ`` to the attached
mapping cylinder.

The formal calculation here checks, noncommutatively and block by block,

``Q^2=0``, ``P=QW+WQ``, two-sided same-sided Green inversion, ``QG=GQ`` and
``Q(WG)+(WG)Q=1``.

The Green and homotopy checks use the rank-fourteen relations as hypotheses.
The emitted certificate marks those hypotheses unsupplied.  Consequently no
global Green or causal flag is promoted.  The exact missing package includes
the projector-free quotient operator, its compatible-source Green maps and
the local source-lift/extension identities listed in the certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from typing import Mapping

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


SECTORS = (
    ("physical_biwave_restricted", "known_overlap", 4),
    ("shifted_fhat_contractible", "known_overlap", 4),
    ("rank12_gauge_subsidiary", "known_disjoint", 12),
    ("rank8_constraint_quotient", "known_disjoint", 8),
    ("rank14_field_cokernel", "missing_disjoint", 14),
    ("shifted_vector_BV_contraction", "known_BV_closure", 16),
    ("curvature_U_tail", "known_disjoint", 26),
    ("curvature_Fsharp_tail", "known_disjoint", 26),
    ("curvature_Usharp_tail", "known_disjoint", 26),
    ("mapping_cone_contractible_rows", "known_all_row", 12),
)


Matrix = list[list[OperatorPolynomial]]


def _zero(size: int) -> Matrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)]
        for _ in range(size)
    ]


def _identity(size: int) -> Matrix:
    result = _zero(size)
    for index in range(size):
        result[index][index] = OperatorPolynomial.identity()
    return result


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            left[row][column] + right[row][column]
            for column in range(len(left))
        ]
        for row in range(len(left))
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    result = _zero(size)
    for row in range(size):
        for column in range(size):
            entry = OperatorPolynomial.zero()
            for middle in range(size):
                entry = entry + left[row][middle] * right[middle][column]
            result[row][column] = entry
    return result


def _scale(matrix: Matrix, coefficient: int) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in matrix]


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


def _sector_complex() -> tuple[Matrix, Matrix, Matrix, Matrix, Matrix]:
    """Return the universal split Q,W,P,G,Lambda sector assembly.

    Every sector is represented by its source/equation pair.  ``D_i`` is the
    corresponding differential row and ``V_i`` the certified (or, for R14,
    conditional) backward witness.  Source and equation Green maps are kept
    separate because this is what makes the chain-commutation/source-lift
    relation visible.
    """

    count = len(SECTORS)
    size = 2 * count
    q = _zero(size)
    witness = _zero(size)
    green = _zero(size)
    for index in range(count):
        source = 2 * index
        equation = source + 1
        q[equation][source] = OperatorPolynomial.atom(f"D{index}")
        witness[source][equation] = OperatorPolynomial.atom(f"V{index}")
        green[source][source] = OperatorPolynomial.atom(f"GS{index}")
        green[equation][equation] = OperatorPolynomial.atom(f"GE{index}")
    operator = _add(_multiply(q, witness), _multiply(witness, q))
    homotopy = _multiply(witness, green)
    return q, witness, operator, green, homotopy


def _reduce_sector(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Apply exactly the sector Green and chain-commutation hypotheses."""

    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced = tuple(word)
        changed = True
        while changed:
            changed = False
            for index in range(max(0, len(reduced) - 1)):
                # D GS = GE D is the compatible-source/source-lift identity.
                for sector in range(len(SECTORS)):
                    if reduced[index : index + 2] == (
                        f"D{sector}",
                        f"GS{sector}",
                    ):
                        reduced = (
                            reduced[:index]
                            + (f"GE{sector}", f"D{sector}")
                            + reduced[index + 2 :]
                        )
                        changed = True
                        break
                if changed:
                    break

                for sector in range(len(SECTORS)):
                    cancellations = (
                        (f"V{sector}", f"D{sector}", f"GS{sector}"),
                        (f"GS{sector}", f"V{sector}", f"D{sector}"),
                        (f"D{sector}", f"V{sector}", f"GE{sector}"),
                        (f"GE{sector}", f"D{sector}", f"V{sector}"),
                        # Derived from GE D=D GS and V D GS=1.
                        (f"V{sector}", f"GE{sector}", f"D{sector}"),
                    )
                    for pattern in cancellations:
                        stop = index + len(pattern)
                        if reduced[index:stop] == pattern:
                            reduced = reduced[:index] + reduced[stop:]
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _is_zero(matrix: Matrix) -> bool:
    return all(
        _reduce_sector(entry) == OperatorPolynomial.zero()
        for row in matrix
        for entry in row
    )


def _is_identity(matrix: Matrix) -> bool:
    identity = _identity(len(matrix))
    return _is_zero(_add(matrix, _scale(identity, -1)))


@dataclass(frozen=True)
class ExpandedRelativeAllRowAssembly:
    """Exact conditional sector algebra and certificate dependency audit."""

    q: Matrix
    witness: Matrix
    operator: Matrix
    green: Matrix
    homotopy: Matrix

    @staticmethod
    def build() -> "ExpandedRelativeAllRowAssembly":
        q, witness, operator, green, homotopy = _sector_complex()
        result = ExpandedRelativeAllRowAssembly(
            q=q,
            witness=witness,
            operator=operator,
            green=green,
            homotopy=homotopy,
        )
        result.verify()
        return result

    def verify(self) -> None:
        size = 2 * len(SECTORS)
        if len(self.q) != size:
            raise AssertionError("all-row sector count drifted")
        if not _is_zero(_multiply(self.q, self.q)):
            raise AssertionError("split sector Q is not nilpotent")
        direct = _add(
            _multiply(self.q, self.witness),
            _multiply(self.witness, self.q),
        )
        if direct != self.operator:
            raise AssertionError("sector P=QW+WQ identity failed")
        if not _is_identity(_multiply(self.operator, self.green)):
            raise AssertionError("conditional sector Green right inverse failed")
        if not _is_identity(_multiply(self.green, self.operator)):
            raise AssertionError("conditional sector Green left inverse failed")
        if not _is_zero(
            _add(
                _multiply(self.q, self.green),
                _scale(_multiply(self.green, self.q), -1),
            )
        ):
            raise AssertionError("conditional QG=GQ identity failed")
        if not _is_identity(
            _add(
                _multiply(self.q, self.homotopy),
                _multiply(self.homotopy, self.q),
            )
        ):
            raise AssertionError("conditional sector Green homotopy failed")

    def certificate(
        self,
        *,
        shifted_certificate: Mapping[str, object],
        rank34_certificate: Mapping[str, object],
        vector_certificate: Mapping[str, object],
        mapping_substitution_certificate: Mapping[str, object],
        mapping_witness_certificate: Mapping[str, object],
        curvature_witness_certificate: Mapping[str, object],
        curvature_causal_certificate: Mapping[str, object],
        bridge_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()

        if shifted_certificate.get("schema") != (
            "pure-weyl-expanded-relative-shifted-green-filtration-v1"
        ):
            raise AssertionError("wrong shifted physical input")
        physical = _nested(
            shifted_certificate, "actual_local_physical_replacement_witness"
        )
        if not (
            physical.get("Q_squared_defect") == 0
            and physical.get("P_identity_defect") == 0
            and physical.get("left_Green_defect") == 0
            and physical.get("right_Green_defect") == 0
            and physical.get("Q_Lambda_plus_Lambda_Q_defect") == 0
        ):
            raise AssertionError("restricted physical/f_hat block regressed")

        if rank34_certificate.get("schema") != (
            "pure-weyl-expanded-relative-rank34-module-v1"
        ):
            raise AssertionError("wrong rank-34 filtration input")
        submodule = _nested(rank34_certificate, "local_differential_submodule")
        subgreen = _nested(
            rank34_certificate, "presented_submodule_recursive_inverse"
        )
        quotient = _nested(rank34_certificate, "quotient_presentation")
        if not (
            submodule.get("presentation_rank") == 12
            and submodule.get("intertwining_defect") == 0
            and subgreen.get("left_inverse_defect") == 0
            and subgreen.get("right_inverse_defect") == 0
        ):
            raise AssertionError("rank-12 presented Green module regressed")
        if not (
            quotient.get("constraint_quotient_rank") == 8
            and quotient.get("constraint_quotient_symmetric_hyperbolic")
            and quotient.get("field_cokernel_rank") == 14
            and quotient.get("C1_descends_to_field_cokernel")
        ):
            raise AssertionError("rank-8/rank-14 quotient ledger regressed")
        if quotient.get("C1_induced_biwave_intertwiner_constructed"):
            raise AssertionError("rank-14 input unexpectedly claims completion")

        if vector_certificate.get("schema") != (
            "pure-weyl-expanded-relative-vector-contraction-v1"
        ):
            raise AssertionError("wrong shifted vector input")
        vector_atomic = _nested(vector_certificate, "warranted_atomic_flags")
        if not all(vector_atomic.values()):
            raise AssertionError("shifted vector Green contraction regressed")

        if mapping_substitution_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ) or not mapping_substitution_certificate.get(
            "coefficientwise_complete_prolonged_Q"
        ):
            raise AssertionError("coefficientwise mapping-cylinder Q unavailable")
        kernel = _nested(mapping_substitution_certificate, "kernel")
        if not (
            kernel.get("Q_squared") == "zero"
            and kernel.get("BV_pairing_defect") == 0
            and kernel.get("I_P_minus_identity") == "QH+HQ"
            and len(kernel.get("complete_16_block_degree_ledger", [])) == 16
        ):
            raise AssertionError("all-row mapping-cylinder kernel regressed")

        if mapping_witness_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-witness-v1"
        ):
            raise AssertionError("wrong coefficientwise mapping witness input")
        mapping_identities = _nested(mapping_witness_certificate, "exact_identities")
        if not (
            mapping_identities.get("P_prol_equals_QW_plus_WQ")
            and mapping_identities.get("P_prol_equals_S_Psplit_Sinverse")
            and mapping_identities.get("support_local_diagonalization_inverse_exact")
        ):
            raise AssertionError("mapping-cylinder witness algebra regressed")

        if curvature_witness_certificate.get("schema") != (
            "pure-weyl-cotton-block-green-witness-v1"
        ):
            raise AssertionError("wrong curvature tail witness input")
        curvature_identities = _nested(
            curvature_witness_certificate, "exact_block_identities"
        )
        if not (
            curvature_identities.get("P_equals_QW_plus_WQ")
            and curvature_identities.get("Q_P_equals_P_Q")
        ):
            raise AssertionError("curvature tail witness identity regressed")

        if curvature_causal_certificate.get("schema") != (
            "pure-weyl-cotton-causal-pde-v1"
        ) or not curvature_causal_certificate.get(
            "curvature_block_causal_solution_operators"
        ):
            raise AssertionError("curvature tail Green operators unavailable")
        compatible = _nested(
            curvature_causal_certificate, "compatible_source_restriction"
        )
        if not (
            compatible.get("unique")
            and compatible.get("restriction_does_not_use_a_projector_onto_ker_K_src")
        ):
            raise AssertionError("compatible curvature source theorem regressed")

        if bridge_certificate.get("schema") != "pure-weyl-prolonged-green-bridge-v1":
            raise AssertionError("wrong finite triangular theorem input")
        triangular = _nested(
            bridge_certificate, "finite_triangular_green_theorem"
        )
        if not (
            triangular.get("left_inverse_defect") == 0
            and triangular.get("right_inverse_defect") == 0
            and triangular.get("finite_no_Neumann_convergence_assumption")
        ):
            raise AssertionError("finite triangular Green recursion regressed")

        blockwise = []
        for index, (name, coverage, rank) in enumerate(SECTORS):
            blockwise.append(
                {
                    "sector": name,
                    "coverage": coverage,
                    "rank": rank,
                    "Q": f"D{index}: source_{index}->equation_{index}",
                    "W": f"V{index}: equation_{index}->source_{index}",
                    "P_source": f"V{index} D{index}",
                    "P_equation": f"D{index} V{index}",
                    "QW_plus_WQ_defect": 0,
                    "Green_input_supplied": name != "rank14_field_cokernel",
                }
            )

        return {
            "schema": "pure-weyl-expanded-relative-all-row-assembly-v1",
            "scope": (
                "conditional exact all-row assembly in the certified shifted "
                "and curvature-mapping-cylinder filtrations"
            ),
            "analytic_116_coverage": {
                "disjoint_ledger": [
                    {"sector": "rank34_SCC", "rank": 34},
                    {"sector": "vector_singleton", "rank": 4},
                    {"sector": "curvature_U", "rank": 26},
                    {"sector": "curvature_Fsharp", "rank": 26},
                    {"sector": "curvature_Usharp", "rank": 26},
                ],
                "rank_sum": 116,
                "rank34_filtration": "12 presented + 8 constraint quotient + 14 field cokernel",
                "rank34_filtration_sum": 34,
                "restricted_TT_biwave_plus_fhat_is_inside_rank14": True,
                "restricted_TT_block_counted_as_disjoint_sector": False,
                "reason": (
                    "its aligned/covariant restricted theorem has no support-local "
                    "projector from arbitrary rank-14 sources"
                ),
            },
            "all_BV_row_coverage": {
                "mapping_cylinder_blocks": 16,
                "coefficientwise_Q": True,
                "Q_squared_defect": 0,
                "BV_pairing_defect": 0,
                "support_local_SDR": True,
                "rank4_field_closes_to_vector_BV_rank": 16,
                "vector_primal_and_cotangent_rows": True,
                "curvature_cone_primal_and_cotangent_rows": True,
                "formal_adjoint_tails_present": True,
            },
            "blockwise_witness_ledger": blockwise,
            "conditional_formal_assembly": {
                "sector_pairs": len(SECTORS),
                "formal_matrix_rank": 2 * len(SECTORS),
                "Q_squared_defect": 0,
                "P_equals_QW_plus_WQ_defect": 0,
                "conditional_G_left_defect": 0,
                "conditional_G_right_defect": 0,
                "conditional_QG_minus_GQ_defect": 0,
                "conditional_QWG_plus_WGQ_minus_identity_defect": 0,
                "split_Q_sha256": _digest(self.q),
                "split_W_sha256": _digest(self.witness),
                "split_P_sha256": _digest(self.operator),
                "conditional_G_sha256": _digest(self.green),
                "conjugation": (
                    "Q_prol=S Q_split S^-1, W_prol=S W_split S^-1, "
                    "P_prol=S P_split S^-1"
                ),
                "conjugation_identity_already_coefficientwise": True,
                "interpretation": (
                    "this is the associated-graded recognition algebra after "
                    "the displayed filtration/source-lift package is supplied; "
                    "the coefficientwise unsplit 16-block identity is supplied "
                    "independently by the mapping-cylinder witness certificate"
                ),
            },
            "known_green_blocks": {
                "restricted_physical_biwave_and_fhat": True,
                "rank12_presented_gauge_subsidiary": True,
                "rank8_constraint_quotient": True,
                "rank16_shifted_vector_contraction": True,
                "rank26_curvature_tails_and_adjoints": True,
                "mapping_cylinder_contractible_rows": True,
                "finite_triangular_extension_theorem": True,
            },
            "rank14_required_package": {
                "supplied": False,
                "field_cokernel_rank": 14,
                "must_be_projector_free": True,
                "required_operator_data": [
                    "a local differential presentation pi14 of the field cokernel",
                    "the complete curved induced operator L14, including lower-order coefficients",
                    "a degree-minus-one V14 on the corresponding BV rows with P14=Q14 V14+V14 Q14",
                    "a local intertwiner pi14 L22=L14 pi14 modulo the certified constraint row",
                    "the cotangent/formal-adjoint presentation with project fibre pairings",
                ],
                "required_green_data": [
                    "same-sided G14_plus/minus on every compatible compact source",
                    "L14 G14_plus/minus=1 and G14_plus/minus L14=1",
                    "retarded/advanced causal support",
                    "D14 G14_source=G14_equation D14 (the sector chain-commutation identity)",
                ],
                "required_source_lift_equations": [
                    "K14_src f14=0",
                    "K14 L14=L_K14 K14 and K14_src L14=L_K14 K14",
                    "K14 G14_plus/minus f14=0 for K14_src f14=0",
                    "L34 J12=J12 L12",
                    "pi22 L34=L22 pi22",
                    "L22 J8=J8 L8",
                    "pi14 L22=L14 pi14",
                    "for lifted u14, f22-L22 u14 lies in im(J8)",
                    "for lifted u22, f34-L34 u22 lies in im(J12)",
                    "the two residual-source lifts are local differential maps and preserve support",
                ],
                "acceptable_realizations": [
                    "a support-local filtration chart with triangular L12,L8,L14 diagonal",
                    "a mapping-cone presentation with explicit residual-source lifts",
                    "a constrained curvature extension whose compatible Green map lands directly in F34",
                ],
                "forbidden_shortcuts": [
                    "covector-dependent helicity projector",
                    "inverse Laplacian or inverse curl",
                    "claiming the restricted TT inverse acts on arbitrary rank-14 sources",
                ],
            },
            "conditional_closure_theorem": {
                "hypothesis": "rank14_required_package.supplied=true with every displayed identity exact",
                "then_all_row_W_exists": True,
                "then_P_equals_QW_plus_WQ": True,
                "then_same_sided_Green_operators_exist_by_finite_recursion": True,
                "then_QG_equals_GQ": True,
                "then_Lambda_equals_WG": True,
                "then_Q_Lambda_plus_Lambda_Q_equals_identity": True,
                "no_additional_analytic_block_after_rank14": True,
            },
            "current_boundary": {
                "rank14_required_package_supplied": False,
                "coefficientwise_all_row_replacement_W_realized": False,
                "coefficientwise_existing_mapping_W_QW_identity": True,
                "rank12_and_rank8_are_filtration_subquotients_not_split_W_blocks": True,
                "complete_all_row_Green_operator_realized": False,
                "complete_all_row_Green_homotopy_realized": False,
                "only_remaining_analytic_assembly_input": (
                    "projector-free rank-14 field-cokernel operator/Green/source-lift package"
                ),
            },
            "warranted_atomic_flags": {
                "all_row_green_block_ledger_complete": True,
                "all_row_conditional_QW_identity_exact": True,
                "all_row_conditional_green_recursion_exact": True,
                "all_row_green_assembly_reduced_to_rank14": True,
            },
            "status_flags_promoted": [],
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "fail_closed": True,
        }
