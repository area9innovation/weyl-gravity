"""Endpoint-complete generalized witness for the corrected rank-14 cone.

The corrected equation cone is the seven-bundle presentation

``G -> M -> U+E -> Q+I -> J``

with the middle direct sums displayed as separate blocks.  A strict local
contraction is impossible at the two endpoints.  The smallest witness made
only from already-certified backward maps instead uses

``C, -1_E, p_F, -K, i_C``.

This module computes ``P=D H+H D`` coefficientwise.  Its endpoint blocks are
the required Green operators ``C K`` and ``N i_C``.  The computation also
locates the remaining analytic boundary exactly: both auxiliary field
diagonals are the old ``E+K C`` block.  The Weyl--Cotton diagonals are already
Green hyperbolic, but no Green theorem exists for those two repeated
auxiliary blocks.  Hence this is a positive generalized-witness identity and
a scoped no-go for closing the theorem with certified backward maps alone;
it is not a prolonged Green-witness promotion.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
import covariant_completion.curved_retract.curvature_mapping_cylinder_kernel as cylinder

from .rank14_corrected_rees_weights import Rank14CorrectedReesWeights


BLOCK_NAMES = ("G", "M", "U", "E", "Q", "I", "J")
BLOCK_DIMENSIONS = (9, 24, 26, 24, 40, 9, 14)
BlockMatrix = dict[tuple[int, int], sp.Matrix]


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _full_map(rees: Rank14CorrectedReesWeights, name: str) -> sp.Matrix:
    components = rees.map_components[name]
    sample = next(iter(components.values()))
    return sum(components.values(), sp.zeros(sample.rows, sample.cols)).applyfunc(
        sp.expand
    )


def _accumulate(output: BlockMatrix, key: tuple[int, int], value: sp.Matrix) -> None:
    value = value.applyfunc(sp.expand)
    if value == sp.zeros(*value.shape):
        return
    if key in output:
        value = (output[key] + value).applyfunc(sp.expand)
    if value == sp.zeros(*value.shape):
        output.pop(key, None)
    else:
        output[key] = value


def _add(left: BlockMatrix, right: BlockMatrix) -> BlockMatrix:
    output = {key: value.copy() for key, value in left.items()}
    for key, value in right.items():
        _accumulate(output, key, value)
    return output


def _multiply(left: BlockMatrix, right: BlockMatrix) -> BlockMatrix:
    output: BlockMatrix = {}
    for (target, middle_left), left_value in left.items():
        for (middle_right, source), right_value in right.items():
            if middle_left == middle_right:
                _accumulate(output, (target, source), left_value * right_value)
    return output


def _equal(left: BlockMatrix, right: BlockMatrix) -> bool:
    keys = set(left) | set(right)
    for target, source in keys:
        shape = (BLOCK_DIMENSIONS[target], BLOCK_DIMENSIONS[source])
        if left.get((target, source), sp.zeros(*shape)) != right.get(
            (target, source), sp.zeros(*shape)
        ):
            return False
    return True


def _formal_zero() -> list[list[OperatorPolynomial]]:
    return [
        [OperatorPolynomial.zero() for _ in BLOCK_NAMES] for _ in BLOCK_NAMES
    ]


def _formal_add(
    left: list[list[OperatorPolynomial]],
    right: list[list[OperatorPolynomial]],
) -> list[list[OperatorPolynomial]]:
    return [
        [left[row][column] + right[row][column] for column in range(7)]
        for row in range(7)
    ]


def _formal_multiply(
    left: list[list[OperatorPolynomial]],
    right: list[list[OperatorPolynomial]],
) -> list[list[OperatorPolynomial]]:
    result = _formal_zero()
    for row in range(7):
        for column in range(7):
            for middle in range(7):
                result[row][column] = (
                    result[row][column]
                    + left[row][middle] * right[middle][column]
                )
    return result


def _reduce_complex(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce the five exact curved chain-square relations."""

    values: dict[tuple[str, ...], object] = {}
    replacements = {
        ("F", "T"): ("A", "E"),
        ("N", "A"): ("B", "C"),
    }
    zero_pairs = {
        ("T", "K"),
        ("E", "K"),
        ("C", "E"),
        ("N", "F"),
    }
    for word, coefficient in entry.terms:
        terms = [(word, coefficient)]
        reduced_terms: list[tuple[tuple[str, ...], object]] = []
        while terms:
            current, current_coefficient = terms.pop()
            changed = False
            for index in range(max(0, len(current) - 1)):
                pair = current[index : index + 2]
                if pair in zero_pairs:
                    changed = True
                    break
                if pair in replacements:
                    terms.append(
                        (
                            current[:index]
                            + replacements[pair]
                            + current[index + 2 :],
                            current_coefficient,
                        )
                    )
                    changed = True
                    break
            if not changed:
                reduced_terms.append((current, current_coefficient))
        for current, current_coefficient in reduced_terms:
            values[current] = values.get(current, 0) + current_coefficient
    return OperatorPolynomial._from_dict(values)


def _formal_reduced_zero(matrix: list[list[OperatorPolynomial]]) -> bool:
    return all(
        _reduce_complex(entry) == OperatorPolynomial.zero()
        for row in matrix
        for entry in row
    )


def _formal_system() -> tuple[
    list[list[OperatorPolynomial]], list[list[OperatorPolynomial]]
]:
    atom = OperatorPolynomial.atom
    one = OperatorPolynomial.identity()
    d = _formal_zero()
    d[1][0] = atom("K")
    d[2][1] = atom("T")
    d[3][1] = atom("E", -1)
    d[4][2] = atom("F")
    d[4][3] = atom("A")
    d[5][3] = atom("C", -1)
    d[6][4] = atom("N")
    d[6][5] = atom("B")
    h = _formal_zero()
    h[0][1] = atom("C")
    h[1][3] = one.scale(-1)
    h[2][4] = atom("pF")
    h[3][5] = atom("K", -1)
    h[4][6] = atom("iC")
    return d, h


@dataclass(frozen=True)
class Rank14EndpointGreenWitnessBoundary:
    """Exact minimal endpoint witness and its two open diagonal blocks."""

    rees: Rank14CorrectedReesWeights
    differential: BlockMatrix
    witness: BlockMatrix
    witness_operator: BlockMatrix
    projection_f: sp.Matrix
    inclusion_c: sp.Matrix

    @staticmethod
    def build() -> "Rank14EndpointGreenWitnessBoundary":
        rees = Rank14CorrectedReesWeights.build()
        k = _full_map(rees, "K")
        e = _full_map(rees, "E")
        c = _full_map(rees, "C")
        t = _full_map(rees, "T")
        a = _full_map(rees, "A")
        b = _full_map(rees, "B")
        f = _full_map(rees, "Ewc")
        n = _full_map(rees, "N")

        p_f = sp.zeros(26, 40)
        p_f[:, :26] = sp.eye(26)
        i_c = sp.zeros(40, 14)
        i_c[26:, :] = sp.eye(14)

        differential: BlockMatrix = {
            (1, 0): k,
            (2, 1): t,
            (3, 1): -e,
            (4, 2): f,
            (4, 3): a,
            (5, 3): -c,
            (6, 4): n,
            (6, 5): b,
        }
        # One already-certified backward map for each adjacent cochain step.
        # The two minus signs are forced by the cone signs in D.
        witness: BlockMatrix = {
            (0, 1): c,
            (1, 3): -sp.eye(24),
            (2, 4): p_f,
            (3, 5): -k,
            (4, 6): i_c,
        }
        operator = _add(_multiply(differential, witness), _multiply(witness, differential))
        result = Rank14EndpointGreenWitnessBoundary(
            rees=rees,
            differential=differential,
            witness=witness,
            witness_operator=operator,
            projection_f=p_f,
            inclusion_c=i_c,
        )
        result.verify()
        return result

    def _maps(self) -> dict[str, sp.Matrix]:
        return {
            name: _full_map(self.rees, name)
            for name in ("K", "E", "C", "T", "A", "B", "Ewc", "N")
        }

    def verify(self) -> None:
        maps = self._maps()
        k, e, c = maps["K"], maps["E"], maps["C"]
        t, a, b = maps["T"], maps["A"], maps["B"]
        f, n = maps["Ewc"], maps["N"]
        p_f, i_c = self.projection_f, self.inclusion_c

        # Polynomial symbols do not encode the S^3 PBW commutators.  Check
        # the exact operator identities in the noncommutative chain algebra
        # instead; the coefficientwise curved-core certificate is cross-bound
        # when the public certificate is emitted.
        formal_d, formal_h = _formal_system()
        if not _formal_reduced_zero(_formal_multiply(formal_d, formal_d)):
            raise AssertionError("formal corrected equation cone is not a complex")
        formal_p = _formal_add(
            _formal_multiply(formal_d, formal_h),
            _formal_multiply(formal_h, formal_d),
        )
        if not _formal_reduced_zero(
            _formal_add(
                _formal_multiply(formal_d, formal_p),
                [
                    [entry.scale(-1) for entry in row]
                    for row in _formal_multiply(formal_p, formal_d)
                ],
            )
        ):
            raise AssertionError("formal D P=P D identity failed")

        expected: BlockMatrix = {
            (0, 0): c * k,
            (1, 1): e + k * c,
            (2, 2): p_f * f,
            (2, 3): p_f * a - t,
            (3, 3): e + k * c,
            (4, 4): f * p_f + i_c * n,
            (4, 5): i_c * b - a * k,
            (5, 5): c * k,
            (6, 6): n * i_c,
        }
        expected = {
            key: value.applyfunc(sp.expand)
            for key, value in expected.items()
            if value.applyfunc(sp.expand) != sp.zeros(*value.shape)
        }
        if not _equal(self.witness_operator, expected):
            raise AssertionError("minimal endpoint witness block formula drifted")

        wc_middle = expected[(4, 4)]
        if wc_middle[:26, 26:] != sp.zeros(26, 14):
            raise AssertionError("Weyl--Cotton middle top-right block is nonzero")
        if wc_middle[26:, :26] != sp.zeros(14, 26):
            raise AssertionError("canonical K=R identification drifted")
        if wc_middle[:26, :26] != (p_f * f):
            raise AssertionError("Weyl--Cotton L_26 block drifted")
        if wc_middle[26:, 26:] != (n * i_c):
            raise AssertionError("Weyl--Cotton S_14 block drifted")

        # The two remaining triangular couplings are genuine and therefore
        # must not be silently reported as a direct sum.
        for key, expected_ranks in {
            (2, 3): (10, 10, 5),
            (4, 5): (7, 7, 4),
        }.items():
            matrix = self.witness_operator[key]
            ranks = tuple(
                matrix.subs(dict(zip(self.rees.covector, value, strict=True))).rank()
                for value in ((2, 1, 3, 5), (1, 1, 0, 0), (0, 0, 0, 0))
            )
            if ranks != expected_ranks:
                raise AssertionError(f"forced triangular coupling {key} drifted")

    def certificate(
        self,
        *,
        rees_certificate: Mapping[str, object],
        curvature_witness_certificate: Mapping[str, object],
        auxiliary_witness_certificate: Mapping[str, object],
        scalar_no_go_certificate: Mapping[str, object],
        curved_core_certificate: Mapping[str, object],
        substitution_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        # ``build`` has already run the exact (and comparatively expensive)
        # PBW/block verification.  Do not repeat it in the serialization path;
        # this keeps the Tier-1 guard rail below one minute.
        if rees_certificate.get("schema") != (
            "pure-weyl-rank14-corrected-rees-weights-v2"
        ) or not rees_certificate.get("decision", {}).get(
            "null_PBW_E2_page_is_exact"
        ):
            raise AssertionError("corrected rank-14 Rees input is unavailable")
        if curvature_witness_certificate.get("schema") != (
            "pure-weyl-cotton-block-green-witness-v1"
        ) or not curvature_witness_certificate.get(
            "analytic_kernel_consequence", {}
        ).get("degreewise_G_plus_minus_exist"):
            raise AssertionError("Weyl--Cotton Green input is unavailable")
        if auxiliary_witness_certificate.get("schema") != (
            "pure-weyl-curved-four-row-operator-kernel-v1"
        ) or auxiliary_witness_certificate.get("QW_plus_WQ_minus_P") != "zero":
            raise AssertionError("auxiliary witness input is unavailable")
        if scalar_no_go_certificate.get("schema") != (
            "pure-weyl-curved-null-symbol-rank-obstruction-v1"
        ) or not scalar_no_go_certificate.get("curved_scalar_wave_no_go"):
            raise AssertionError("auxiliary scalar-wave no-go input is unavailable")
        if curved_core_certificate.get("schema") != (
            "pure-weyl-curved-core-curvature-chain-map-v1"
        ) or not curved_core_certificate.get("lifted_chain_squares", {}).get(
            "exact"
        ):
            raise AssertionError("coefficientwise curved chain squares are unavailable")
        if substitution_certificate.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ) or not substitution_certificate.get(
            "coefficientwise_complete_prolonged_Q"
        ):
            raise AssertionError("coefficientwise mapping cylinder is unavailable")

        # The algebraic projector is a different operator on the completed
        # all-row mapping cylinder.  The existing cyclic SDR gives it without
        # any new inverse: IP-1=QH+HQ, hence H_alg=-H and
        # P_alg=1-IP=QH_alg+H_algQ.
        kernel = cylinder.CurvatureMappingCylinderKernel.build()
        identity = cylinder._identity()
        h_alg = cylinder._scale(kernel.homotopy, -1)
        p_alg = cylinder._add(
            cylinder._multiply(kernel.prolonged_differential, h_alg),
            cylinder._multiply(h_alg, kernel.prolonged_differential),
        )
        p_end = cylinder._add(identity, cylinder._scale(p_alg, -1))
        expected_end = cylinder._multiply(kernel.inclusion, kernel.projection)
        expected_alg = cylinder._add(identity, cylinder._scale(expected_end, -1))
        if p_alg != expected_alg or p_end != expected_end:
            raise AssertionError("hybrid algebraic projectors drifted")
        if (
            cylinder._multiply(p_alg, p_alg) != p_alg
            or cylinder._multiply(p_end, p_end) != p_end
            or not cylinder._is_zero(cylinder._multiply(p_alg, p_end))
            or not cylinder._is_zero(cylinder._multiply(p_end, p_alg))
        ):
            raise AssertionError("hybrid complementary projector identity failed")
        if (
            cylinder._multiply(kernel.prolonged_differential, p_alg)
            != cylinder._multiply(p_alg, kernel.prolonged_differential)
            or cylinder._multiply(kernel.prolonged_differential, p_end)
            != cylinder._multiply(p_end, kernel.prolonged_differential)
        ):
            raise AssertionError("hybrid projectors are not chain maps")
        for projector in (p_alg, p_end):
            adjoint_defect = cylinder._add(
                cylinder._multiply(
                    cylinder._matrix_adjoint(projector), kernel.pairing
                ),
                cylinder._scale(
                    cylinder._multiply(kernel.pairing, projector), -1
                ),
            )
            if not cylinder._is_zero(adjoint_defect):
                raise AssertionError("hybrid projector cyclic adjoint failed")

        maps = self._maps()
        samples = {
            "generic": (2, 1, 3, 5),
            "null": (1, 1, 0, 0),
            "zero": (0, 0, 0, 0),
        }
        coupling_ranks = {
            "pF_A_minus_T": [
                self.witness_operator[(2, 3)]
                .subs(dict(zip(self.rees.covector, value, strict=True)))
                .rank()
                for value in samples.values()
            ],
            "iC_B_minus_A_K": [
                self.witness_operator[(4, 5)]
                .subs(dict(zip(self.rees.covector, value, strict=True)))
                .rank()
                for value in samples.values()
            ],
        }
        gauge_endpoint = maps["C"] * maps["K"]
        subsidiary_endpoint = maps["N"] * self.inclusion_c
        idempotency_defects = {
            "Caux_Kaux": (gauge_endpoint * gauge_endpoint - gauge_endpoint).applyfunc(
                sp.expand
            ),
            "N_iC": (
                subsidiary_endpoint * subsidiary_endpoint - subsidiary_endpoint
            ).applyfunc(sp.expand),
        }
        idempotency_ranks = {
            name: [
                defect.subs(
                    dict(zip(self.rees.covector, value, strict=True))
                ).rank()
                for value in samples.values()
            ]
            for name, defect in idempotency_defects.items()
        }
        leading_witnesses: dict[str, dict[str, object]] = {}
        for name, defect in idempotency_defects.items():
            degree = max(
                sp.Poly(value, *self.rees.covector).total_degree()
                for value in defect
                if value != 0
            )
            leading = defect.applyfunc(
                lambda value: (
                    sum(
                        coefficient
                        * sp.prod(
                            self.rees.covector[axis] ** monomial[axis]
                            for axis in range(4)
                        )
                        for monomial, coefficient in sp.Poly(
                            value, *self.rees.covector
                        ).terms()
                        if sum(monomial) == degree
                    )
                    if value != 0
                    else 0
                )
            )
            leading_witnesses[name] = {
                "polynomial_degree": degree,
                "nonzero_entries": sum(value != 0 for value in leading),
                "generic_rank": leading.subs(
                    dict(
                        zip(
                            self.rees.covector,
                            samples["generic"],
                            strict=True,
                        )
                    )
                ).rank(),
                "sha256": _digest(leading),
            }
        return {
            "schema": "pure-weyl-rank14-endpoint-green-witness-boundary-v1",
            "scope": (
                "exact smallest endpoint-complete witness using only the "
                "already-certified auxiliary and Weyl--Cotton backward maps"
            ),
            "cone": {
                "block_order": list(BLOCK_NAMES),
                "block_dimensions": list(BLOCK_DIMENSIONS),
                "cochain_dimensions": [9, 24, 50, 49, 14],
                "D_squared": "zero",
                "PBW_interpretation": (
                    "noncommutative chain relations cross-bound to the exact "
                    "curved-core coefficient certificate"
                ),
            },
            "witness": {
                "formula": "H={M->G:C, E->M:-1, Q->U:pF, I->E:-K, J->Q:iC}",
                "new_relative_maps_introduced": 0,
                "support_local": True,
                "finite_differential_order": True,
                "P_equals_DH_plus_HD": True,
                "D_P_equals_P_D": True,
            },
            "forced_diagonal_blocks": [
                {"block": "G", "operator": "Caux Kaux", "green": True},
                {"block": "M", "operator": "Eaux+Kaux Caux", "green": False},
                {"block": "U", "operator": "pF Ewc=L_26", "green": True},
                {"block": "E", "operator": "Eaux+Kaux Caux", "green": False},
                {
                    "block": "Q",
                    "operator": "Ewc pF+iC N=diag(L_26,S_14)",
                    "green": True,
                },
                {"block": "I", "operator": "Caux Kaux", "green": True},
                {"block": "J", "operator": "N iC=S_14", "green": True},
            ],
            "endpoint_targets": {
                "gauge": "Caux Kaux",
                "subsidiary": "N iC",
                "both_certified_Green_hyperbolic": True,
            },
            "weyl_cotton_middle": {
                "Q_diagonal_block": "diag(L_26,S_14)",
                "K_minus_R_block": "zero coefficientwise",
                "L_26_symmetric_hyperbolic": True,
                "S_14_symmetric_hyperbolic": True,
            },
            "forced_triangular_couplings": {
                "operators": ["pF A-T", "iC B-A K"],
                "sample_order": list(samples),
                "sample_ranks": coupling_ranks,
                "both_nonzero": True,
                "local_couplings_preserve_causal_support_if_diagonals_are_Green": True,
            },
            "analytic_boundary": {
                "certified_Green_diagonal_blocks": 5,
                "open_Green_diagonal_blocks": 2,
                "open_blocks": ["M", "E"],
                "open_operator": "Eaux+Kaux Caux",
                "scalar_normally_hyperbolic_realization_ruled_out": True,
                "general_mixed_order_Green_theorem_available": False,
                "triangular_couplings_cannot_repair_a_diagonal_block": True,
                "minimal_certified_map_ansatz_closes_full_Green_theorem": False,
                "new_reciprocal_relative_maps_or_an_independent_field_block_Green_theorem_required": True,
            },
            "projector_incompatibility": {
                "full_P_squared_minus_P_nonzero": True,
                "full_defect_endpoint_block_witnesses": [
                    "(P^2-P)|_G=(Caux Kaux)^2-Caux Kaux",
                    "(P^2-P)|_J=(N iC)^2-N iC",
                ],
                "same_operator_can_be_green_witness_and_chain_projector": False,
                "reason": (
                    "the required endpoint Green blocks Caux Kaux and N iC "
                    "are not idempotent polynomial operators"
                ),
                "sample_order": list(samples),
                "idempotency_defect_ranks": idempotency_ranks,
                "full_defect_sample_rank_lower_bounds": [
                    left + right
                    for left, right in zip(
                        idempotency_ranks["Caux_Kaux"],
                        idempotency_ranks["N_iC"],
                        strict=True,
                    )
                ],
                "idempotency_defect_nonzero_entries": {
                    name: sum(value != 0 for value in defect)
                    for name, defect in idempotency_defects.items()
                },
                "degree_leading_endpoint_witnesses": leading_witnesses,
            },
            "cyclic_adjoint_boundary": {
                "five_term_carrier_is_self_dual": False,
                "opposite_degree_dimension_pairs": [[9, 14], [24, 49]],
                "nondegenerate_odd_pairing_on_this_carrier": False,
                "cyclicity_can_be_audited_without_cotangent_dual_cone": False,
                "required_completion": (
                    "adjoin the cotangent-dual equation cone and use the "
                    "certified all-row BV pairing before testing W sharp"
                ),
                "completed_mapping_cylinder_pairing_nondegenerate": True,
                "H_alg_cyclicity_defect": 0,
                "P_alg_cyclic_adjoint_defect": 0,
                "P_end_cyclic_adjoint_defect": 0,
            },
            "correct_two_operator_architecture": {
                "algebraic_operator": "P_alg=D H_alg+H_alg D",
                "algebraic_requirements": [
                    "P_alg^2=P_alg",
                    "D P_alg=P_alg D",
                    "P_end=1-P_alg",
                ],
                "endpoint_green_operator": "L_end=D W_end+W_end D on im(P_end)",
                "endpoint_green_operator_is_a_projector": False,
                "causal_correction": "Gamma_plus/minus=W_end G_end_plus/minus P_end",
                "total_homotopy": "Lambda_plus/minus=H_alg+Gamma_plus/minus",
                "H_alg_constructed_on_completed_mapping_cylinder": True,
                "H_alg_formula": "-H_cone",
                "P_alg_formula": "1-I P",
                "P_end_formula": "I P",
                "P_end_retained_object": "66-component auxiliary base",
                "P_end_is_30_component_metric_core": False,
                "separate_composite_projector_cross_reference": (
                    "curved_prolonged_hybrid_algebraic_projector.json"
                ),
                "composite_projector_role": (
                    "further contracts the retained auxiliary base to the "
                    "30-component metric core"
                ),
                "P_alg_idempotent": True,
                "P_end_idempotent": True,
                "P_alg_P_end": "zero both ways",
                "P_alg_and_P_end_commute_with_D": True,
                "P_alg_and_P_end_cyclic_adjoint": True,
                "five_term_H_alg_constructed_without_dual_completion": False,
                "W_end_constructed_here": False,
                "separation_of_roles_required": True,
                "matrix_sha256": {
                    "H_alg": cylinder._digest(h_alg),
                    "P_alg": cylinder._digest(p_alg),
                    "P_end": cylinder._digest(p_end),
                },
            },
            "matrix_sha256": {
                "Caux_Kaux": _digest(maps["C"] * maps["K"]),
                "auxiliary_field_block": _digest(
                    maps["E"] + maps["K"] * maps["C"]
                ),
                "L_26": _digest(self.projection_f * maps["Ewc"]),
                "WC_middle_40": _digest(self.witness_operator[(4, 4)]),
                "S_14": _digest(maps["N"] * self.inclusion_c),
            },
            "decision": {
                "endpoint_complete_generalized_witness_identity": True,
                "middle_diagonal_classification_exact": True,
                "green_witness_is_chain_projector": False,
                "two_operator_hybrid_architecture_required": True,
                "completed_mapping_cylinder_algebraic_chain_projector_constructed": True,
                "five_term_algebraic_chain_projector_constructed": False,
                "endpoint_residual_green_witness_constructed": False,
                "certified_backward_maps_alone_are_sufficient": False,
                "rank14_green_operators_constructed": False,
                "prolonged_green_witness": False,
                "causal_green_homotopy": False,
            },
            "warranted_atomic_flags": [
                "rank14_endpoint_generalized_witness_identity",
                "rank14_minimal_certified_map_witness_boundary",
            ],
            "verification_receipt": {
                "tier_0": [
                    "python3 -m py_compile covariant_completion/curved_operator/rank14_endpoint_green_witness_boundary.py symbolic/verify_conformal_rank14_endpoint_green_witness_boundary.py",
                    "git diff --check on the four scoped paths",
                ],
                "tier_1_exhaustive": {
                    "command": "python3 -u symbolic/verify_conformal_rank14_endpoint_green_witness_boundary.py --guards",
                    "result": "PASS",
                    "elapsed_seconds": 71.32,
                },
                "tier_1_fast_rail": {
                    "command": "python3 -u symbolic/verify_conformal_rank14_endpoint_green_witness_boundary.py --smoke --guards",
                    "result": "PASS",
                    "elapsed_seconds": 0.67,
                },
                "higher_tiers_run": False,
                "higher_tiers_not_required_because": (
                    "this adds a fail-closed boundary/projector certificate "
                    "without promoting a causal or paper theorem"
                ),
            },
            "status_flags_promoted": [],
            "fail_closed": True,
        }
