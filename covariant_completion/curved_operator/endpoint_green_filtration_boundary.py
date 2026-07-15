"""Exact channel reduction of the canonical thirty-row endpoint operator.

The minimal relative ``A_F`` saddle has zero Schur correction, so the
remaining analytic operator is the coefficient-complete endpoint diagonal

``D_end=Q_end W0+W0 Q_end``.

This module resolves its easy channels without a Fourier or helicity
projector.  The ghost block is a pointwise triangular extension of the
certified vector biwave by the Weyl-scalar identity.  The metric block is a
pointwise triangular extension of its trace-free restriction by the trace
identity.  The equation and identity blocks are the corresponding formal
adjoints.  Hence the only unsolved analytic operator is the trace-free
nine-component block ``2H`` and its adjoint copy.

The reduction is coefficientwise on the exact curved tables.  It does not
claim a Green inverse for ``2H``.  The two remaining sufficient routes are a
same-bundle local factorization of ``2H`` or a causal metric-potential lift
from the certified Weyl--Cotton compatibility complex.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

import sympy as sp

from covariant_completion.curved_operator.conventions import (
    SYMMETRIC_COORDINATES,
    _ordinary_system,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_backward_witness import (
    ProlongedMetricEndpointBackwardWitness,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    CoefficientTable,
    ProlongedMetricEndpointComplex,
    ZERO,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _nonzero_count(table: CoefficientTable) -> int:
    return sum(int(value != 0) for _, matrix in table for value in matrix)


SmallMatrix = list[list[OperatorPolynomial]]


def _small_multiply(left: SmallMatrix, right: SmallMatrix) -> SmallMatrix:
    size = len(left)
    result = [
        [OperatorPolynomial.zero() for _ in range(size)] for _ in range(size)
    ]
    for row in range(size):
        for column in range(size):
            for middle in range(size):
                result[row][column] = (
                    result[row][column]
                    + left[row][middle] * right[middle][column]
                )
    return result


def _reduce_inverse_relations(entry: OperatorPolynomial) -> OperatorPolynomial:
    pending = list(entry.terms)
    output: dict[tuple[str, ...], object] = {}
    while pending:
        word, coefficient = pending.pop()
        replaced = False
        for index in range(max(0, len(word) - 1)):
            if word[index : index + 2] in {("R", "G"), ("G", "R")}:
                pending.append((word[:index] + word[index + 2 :], coefficient))
                replaced = True
                break
        if not replaced:
            output[word] = output.get(word, 0) + coefficient
    return OperatorPolynomial._from_dict(output)


def _is_reduced_identity(matrix: SmallMatrix) -> bool:
    for row, values in enumerate(matrix):
        for column, entry in enumerate(values):
            expected = (
                OperatorPolynomial.identity()
                if row == column
                else OperatorPolynomial.zero()
            )
            if _reduce_inverse_relations(entry) != expected:
                return False
    return True


@dataclass(frozen=True)
class EndpointGreenFiltrationBoundary:
    """The exact trace/Weyl triangular reductions of ``D_end``."""

    endpoint: ProlongedMetricEndpointComplex
    witness: ProlongedMetricEndpointBackwardWitness
    trace_inclusion: sp.Matrix
    trace_projection: sp.Matrix
    trace_projector: sp.Matrix
    tracefree_projector: sp.Matrix
    tracefree_field_coefficients: CoefficientTable
    trace_coupling_coefficients: CoefficientTable
    ghost_green_formula_left: bool
    ghost_green_formula_right: bool
    field_green_formula_left: bool
    field_green_formula_right: bool

    @staticmethod
    def build(
        endpoint: ProlongedMetricEndpointComplex,
        witness: ProlongedMetricEndpointBackwardWitness,
    ) -> "EndpointGreenFiltrationBoundary":
        source = _ordinary_system()
        metric = sp.Matrix(
            [source.metric[a, b] for a, b in SYMMETRIC_COORDINATES]
        )
        trace = source.trace / 4
        p_trace = metric * trace
        p_tracefree = sp.eye(10) - p_trace

        tracefree = tuple(
            (
                multiindex,
                (p_tracefree * coefficient * p_tracefree).applyfunc(sp.expand),
            )
            for multiindex, coefficient in witness.field_block_coefficients
        )
        coupling = tuple(
            (
                multiindex,
                (p_trace * coefficient * p_tracefree).applyfunc(sp.expand),
            )
            for multiindex, coefficient in witness.field_block_coefficients
        )

        one = OperatorPolynomial.identity()
        zero = OperatorPolynomial.zero()
        r = OperatorPolynomial.atom("R")
        g = OperatorPolynomial.atom("G")
        d = OperatorPolynomial.atom("d")
        triangular = [[r, zero], [d, one]]
        triangular_green = [[g, zero], [(d * g).scale(-1), one]]
        left = _is_reduced_identity(
            _small_multiply(triangular_green, triangular)
        )
        right = _is_reduced_identity(
            _small_multiply(triangular, triangular_green)
        )

        # The trace-field extension has exactly the same formal 2x2 shape;
        # R and G now denote D_TF and a hypothetical same-sided inverse.
        field_left = left
        field_right = right
        result = EndpointGreenFiltrationBoundary(
            endpoint=endpoint,
            witness=witness,
            trace_inclusion=metric,
            trace_projection=trace,
            trace_projector=p_trace,
            tracefree_projector=p_tracefree,
            tracefree_field_coefficients=tracefree,
            trace_coupling_coefficients=coupling,
            ghost_green_formula_left=left,
            ghost_green_formula_right=right,
            field_green_formula_left=field_left,
            field_green_formula_right=field_right,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.endpoint.verify()
        self.witness.verify()
        if self.witness.endpoint != self.endpoint:
            raise AssertionError("W0 is not built on the selected endpoint")
        if self.trace_projection * self.trace_inclusion != sp.eye(1):
            raise AssertionError("trace inclusion/projection is not normalized")
        if self.trace_projector**2 != self.trace_projector:
            raise AssertionError("trace projector is not idempotent")
        if self.tracefree_projector**2 != self.tracefree_projector:
            raise AssertionError("trace-free projector is not idempotent")
        if self.trace_projector * self.tracefree_projector != sp.zeros(10):
            raise AssertionError("trace and trace-free projectors overlap")

        for multiindex, coefficient in self.witness.field_block_coefficients:
            if (
                self.tracefree_projector * coefficient * self.trace_projector
                != sp.zeros(10)
            ):
                raise AssertionError("the trace field feeds the trace-free block")
            scalar = (
                self.trace_projection * coefficient * self.trace_inclusion
            )[0]
            if scalar != sp.Integer(multiindex == ZERO):
                raise AssertionError("the metric trace diagonal is not identity")

        pairing = self.endpoint.field_pairing
        if pairing.inv() * self.trace_projector.T * pairing != self.trace_projector:
            raise AssertionError("the trace split is not pairing self-adjoint")
        if not all(
            (
                self.ghost_green_formula_left,
                self.ghost_green_formula_right,
                self.field_green_formula_left,
                self.field_green_formula_right,
            )
        ):
            raise AssertionError("a triangular two-sided Green formula failed")

    def certificate(
        self,
        *,
        dependencies: Mapping[str, Mapping[str, object]],
    ) -> dict[str, object]:
        self.verify()
        schemas = {
            "endpoint": "pure-weyl-prolonged-metric-endpoint-complex-v1",
            "backward_witness": (
                "pure-weyl-prolonged-metric-endpoint-backward-witness-v1"
            ),
            "saddle_nilpotence": (
                "pure-weyl-endpoint-relative-saddle-nilpotence-v1"
            ),
            "ghost_biwave": "pure-weyl-cylinder-ghost-curvature-completion-v1",
            "field_intertwiner": "pure-weyl-cylinder-full-metric-biwave-v1",
            "field_symbol": "pure-weyl-minimal-witness-principal-symbol-v1",
            "curvature_chain": "pure-weyl-curved-core-curvature-chain-map-v1",
            "curvature_green": "pure-weyl-cotton-block-green-witness-v1",
            "curvature_pde": "pure-weyl-cotton-causal-pde-v1",
        }
        for name, schema in schemas.items():
            value = dependencies.get(name)
            if not isinstance(value, Mapping) or value.get("schema") != schema:
                raise AssertionError(f"missing endpoint Green dependency {name}")
        saddle = dependencies["saddle_nilpotence"]
        if saddle.get("schur_calculation", {}).get("endpoint_schur_operator") != (
            "S_end=D-CB=D"
        ):
            raise AssertionError("the endpoint Schur diagonal is not isolated")
        curvature_pde = dependencies["curvature_pde"]
        if curvature_pde.get("curvature_block_causal_solution_operators") is not True:
            raise AssertionError("the constrained curvature solution operator is absent")

        trace_coupling_nonzero = _nonzero_count(
            self.trace_coupling_coefficients
        )
        return {
            "schema": "pure-weyl-endpoint-green-filtration-boundary-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "dependency_sha256": {
                name: _certificate_digest(value)
                for name, value in dependencies.items()
            },
            "schur_endpoint": {
                "operator": "D_end",
                "reason": "the full hybrid minimal-A_F correction C B is zero",
                "degreewise_ranks": [5, 10, 10, 5],
            },
            "ghost_channel": {
                "block": "[[R,0],[d/2,1]]",
                "R": "Box(Box+2) I_4=R_minus R_plus",
                "R_factors_normally_hyperbolic": True,
                "same_sided_R_green": "G_R,+/-=G_plus,+/- G_minus,+/-",
                "same_sided_block_green": "[[G_R,0],[-(d/2)G_R,1]]",
                "left_inverse": self.ghost_green_formula_left,
                "right_inverse": self.ghost_green_formula_right,
                "metric_causal_support": True,
                "status": "GREEN",
            },
            "identity_channel": {
                "operator": "D_I=D_G^sharp",
                "green_relation": "G_I,+/-=(G_G,-/+)^sharp",
                "metric_causal_support": True,
                "status": "GREEN_BY_ADJOINT",
            },
            "metric_trace_filtration": {
                "decomposition": "M=S2_0 direct-sum trace",
                "projectors_pointwise_parallel": True,
                "D_M_matrix": "[[D_TF,0],[r_trace,1]]",
                "D_TF": "P_TF D_M P_TF=2H on S2_0",
                "trace_to_tracefree_defect": 0,
                "trace_diagonal_defect": 0,
                "trace_coupling_nonzero_coefficients": trace_coupling_nonzero,
                "conditional_green": "[[G_TF,0],[-r_trace G_TF,1]]",
                "conditional_left_inverse": self.field_green_formula_left,
                "conditional_right_inverse": self.field_green_formula_right,
            },
            "tracefree_channel": {
                "rank": 9,
                "operator": "D_TF=2H=2B_lin+K_TF T",
                "principal_symbol": "(zeta^2)^2 I_9",
                "gauge_intertwiner": "D_TF K_TF=K_TF Box(Box+2)",
                "reduced_physical_factors_known": True,
                "complete_lower_order_same_bundle_factorization": False,
                "support_local_curvature_to_metric_green_lift": False,
                "status": "OPEN",
            },
            "equation_channel": {
                "operator": "D_E=D_M^sharp",
                "remaining_open_part": "D_TF^sharp",
                "status": "OPEN_BY_ADJOINT",
            },
            "curvature_route": {
                "forward_chain_map": "(T_core,A_core,B_core)",
                "equation_cone_required": True,
                "raw_A_F_alone_declared_source_compatible": False,
                "Weyl_Cotton_L26_and_S14_causal": True,
                "remaining_map": (
                    "a retarded/advanced metric-potential lift from compatible "
                    "Weyl--Cotton curvature plus gauge data to S2_0"
                ),
                "inverse_Laplacian_or_curl_allowed": False,
            },
            "channel_ledger": {
                "total_endpoint_components": 30,
                "green_components": 12,
                "open_components_including_adjoint_copy": 18,
                "single_primal_open_operator_rank": 9,
                "open_operator": "2H on trace-free symmetric tensors",
            },
            "next_exact_tests": [
                "factor D_TF on the same trace-free bundle into causal second-order factors",
                "or construct a causal metric-potential lift for the full equation-cone curvature source",
                "then impose G_TF,+^sharp=G_TF,- and assemble the endpoint BV Green homotopy",
            ],
            "warranted_atomic_flags": [
                "endpoint_ghost_identity_green_channels_exact",
                "endpoint_trace_triangular_reduction_exact",
                "endpoint_tracefree_green_boundary_exact",
            ],
            "status_flags_promoted": [],
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "prolonged_green_witness": False,
            "fail_closed": True,
        }
