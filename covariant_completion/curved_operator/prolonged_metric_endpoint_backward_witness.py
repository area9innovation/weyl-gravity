"""Coefficient-complete canonical backward witness on the 30-row endpoint.

The exact endpoint complex is

``G[5] --K--> M[10] --B--> E[10] --C--> I[5]``.

This module supplies the canonical algebraic backward witness

``W0(M->G,E->M,I->E)=(T_gf,2 I,T_gf^sharp)``.

The vector part of ``T_gf`` is the certified third-order cylinder companion
applied to the trace-free part of the metric.  Its scalar part is one quarter
of the trace.  Consequently ``T_gf K`` is triangular: the vector diagonal is
``Box(Box+2)``, the Weyl-scalar diagonal is the identity, and the only
off-diagonal entry is ``(1/2) div`` from vector ghosts to the Weyl row.

Every curved lower-order coefficient is reconstructed in symmetrized
covariant-derivative normal form.  The upper blocks are forced by the endpoint
pairings, not fitted independently.  The result is an algebraic witness
identity only; no Green property is asserted here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping

import sympy as sp

from covariant_completion.curved_operator.conventions import SYMMETRIC_COORDINATES
from covariant_completion.curved_operator.covariant_jets import CovariantJetBasis
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    CoefficientTable,
    ProlongedMetricEndpointComplex,
    ZERO,
    _certificate_digest,
    _sparse_table,
)
from covariant_completion.curved_retract.curvature_auxiliary_chain_map import (
    _digest_tables,
)
from covariant_completion.minimal_witness.cylinder_jets import Jet, _sum


Multiindex = tuple[int, int, int, int]


def _formal_pairing_adjoint(
    table: CoefficientTable,
    *,
    source_pairing: sp.Matrix,
    target_pairing: sp.Matrix,
) -> CoefficientTable:
    """Return ``source_pairing^-1 A^formal,T target_pairing``."""

    source_inverse = source_pairing.inv()
    return tuple(
        (
            multiindex,
            (
                source_inverse
                * ((-1) ** sum(multiindex) * coefficient.T)
                * target_pairing
            ).applyfunc(sp.expand),
        )
        for multiindex, coefficient in table
    )


def _trace(geometry, tensor) -> Jet:
    return _sum(
        geometry.inverse_metric[a][b] * tensor[a][b]
        for a in range(4)
        for b in range(4)
    )


def _apply_t_gf(geometry, tensor) -> list[Jet]:
    tracefree = geometry.tracefree_projection(tensor)
    return geometry.completed_companion(tracefree) + [
        sp.Rational(1, 4) * _trace(geometry, tensor)
    ]


def _apply_k(geometry, ghost: list[Jet]) -> list[list[Jet]]:
    vector = ghost[:4]
    scalar = ghost[4]
    derivative = geometry.covariant_derivative_covector(vector)
    return [
        [
            derivative[a][b]
            + derivative[b][a]
            + geometry.metric[a][b] * scalar
            for b in range(4)
        ]
        for a in range(4)
    ]


def _scalar_covariant_monomial(
    basis: CovariantJetBasis,
    multiindex: Multiindex,
    maximum_order: int,
) -> Jet:
    # Rank-zero specialization of the same triangular covariant-jet solver
    # used for tensor and covector inputs.
    tensor, _ = basis._covariant_monomial(  # noqa: SLF001 - exact shared kernel
        0, ((),), 0, multiindex, maximum_order
    )
    return tensor[()]


def _t_gf_table(basis: CovariantJetBasis) -> CoefficientTable:
    geometry = basis.geometry
    output: list[tuple[Multiindex, sp.Matrix]] = []
    for multiindex in geometry.exhaustive_multiindices(3):
        coefficient = sp.zeros(5, 10)
        for column in range(10):
            metric = basis.covariant_monomial_symmetric(column, multiindex, 3)
            image = _apply_t_gf(geometry, metric)
            coefficient[:, column] = sp.Matrix([value.value for value in image])
        output.append((multiindex, coefficient.applyfunc(sp.expand)))
    return tuple(sorted(output))


def _ghost_block_table(basis: CovariantJetBasis) -> CoefficientTable:
    """Apply ``T_gf K`` directly on every curved ghost four-jet."""

    geometry = basis.geometry
    output: list[tuple[Multiindex, sp.Matrix]] = []
    for multiindex in geometry.exhaustive_multiindices(4):
        coefficient = sp.zeros(5)
        for column in range(5):
            ghost = [Jet.constant(0) for _ in range(5)]
            if column < 4:
                covector = basis.covariant_monomial_covector(
                    column, multiindex, 4
                )
                ghost[:4] = covector
            else:
                ghost[4] = _scalar_covariant_monomial(
                    basis, multiindex, 4
                )
            image = _apply_t_gf(geometry, _apply_k(geometry, ghost))
            coefficient[:, column] = sp.Matrix([value.value for value in image])
            if column < 4:
                biwave = geometry.ghost_biwave(ghost[:4])
                if coefficient[:4, column] != sp.Matrix(
                    [value.value for value in biwave]
                ):
                    raise AssertionError(
                        "direct T_gf K does not equal Box(Box+2)"
                    )
                if coefficient[4, column] != sp.Rational(1, 2) * (
                    geometry.divergence_covector(ghost[:4]).value
                ):
                    raise AssertionError(
                        "direct T_gf K scalar/vector entry is not div/2"
                    )
            elif coefficient[:4, column] != sp.zeros(4, 1) or coefficient[
                4, column
            ] != sp.Integer(multiindex == ZERO):
                raise AssertionError("direct T_gf K Weyl block is not identity")
        output.append((multiindex, coefficient.applyfunc(sp.expand)))
    return tuple(sorted(output))


def _kt_table(basis: CovariantJetBasis) -> CoefficientTable:
    """Apply ``K T_gf`` directly on every curved metric four-jet."""

    geometry = basis.geometry
    output: list[tuple[Multiindex, sp.Matrix]] = []
    for multiindex in geometry.exhaustive_multiindices(4):
        coefficient = sp.zeros(10)
        for column in range(10):
            metric = basis.covariant_monomial_symmetric(column, multiindex, 4)
            image = _apply_k(geometry, _apply_t_gf(geometry, metric))
            coefficient[:, column] = sp.Matrix(
                [image[a][b].value for a, b in SYMMETRIC_COORDINATES]
            )
        output.append((multiindex, coefficient.applyfunc(sp.expand)))
    return tuple(sorted(output))


def _add_tables(
    left: CoefficientTable,
    right: CoefficientTable,
    *,
    left_scale: int = 1,
    right_scale: int = 1,
) -> CoefficientTable:
    left_dict = dict(left)
    right_dict = dict(right)
    if set(left_dict) != set(right_dict):
        raise AssertionError("coefficient-table multiindices do not agree")
    return tuple(
        (
            multiindex,
            (
                left_scale * left_dict[multiindex]
                + right_scale * right_dict[multiindex]
            ).applyfunc(sp.expand),
        )
        for multiindex in sorted(left_dict)
    )


def _identity_table(size: int, coefficient: int = 1) -> CoefficientTable:
    return ((ZERO, coefficient * sp.eye(size)),)


@dataclass(frozen=True)
class ProlongedMetricEndpointBackwardWitness:
    """Canonical W0 and its four degreewise anticommutator blocks."""

    endpoint: ProlongedMetricEndpointComplex
    t_gf_coefficients: CoefficientTable
    middle_coefficients: CoefficientTable
    t_gf_sharp_coefficients: CoefficientTable
    ghost_block_coefficients: CoefficientTable
    field_block_coefficients: CoefficientTable
    equation_block_coefficients: CoefficientTable
    identity_block_coefficients: CoefficientTable
    kt_coefficients: CoefficientTable

    @staticmethod
    def build(
        endpoint: ProlongedMetricEndpointComplex,
    ) -> "ProlongedMetricEndpointBackwardWitness":
        basis = CovariantJetBasis.build()
        t_gf = _t_gf_table(basis)
        t_gf_sharp = _formal_pairing_adjoint(
            t_gf,
            source_pairing=endpoint.field_pairing,
            target_pairing=endpoint.ghost_pairing,
        )
        ghost = _ghost_block_table(basis)
        kt = _kt_table(basis)
        field = _add_tables(
            endpoint.bach_coefficients,
            kt,
            left_scale=2,
        )
        equation = _formal_pairing_adjoint(
            field,
            source_pairing=endpoint.field_pairing,
            target_pairing=endpoint.field_pairing,
        )
        identity = _formal_pairing_adjoint(
            ghost,
            source_pairing=endpoint.ghost_pairing,
            target_pairing=endpoint.ghost_pairing,
        )
        result = ProlongedMetricEndpointBackwardWitness(
            endpoint=endpoint,
            t_gf_coefficients=t_gf,
            middle_coefficients=_identity_table(10, 2),
            t_gf_sharp_coefficients=t_gf_sharp,
            ghost_block_coefficients=ghost,
            field_block_coefficients=field,
            equation_block_coefficients=equation,
            identity_block_coefficients=identity,
            kt_coefficients=kt,
        )
        result.verify()
        return result

    @staticmethod
    def from_coefficient_payload(
        endpoint: ProlongedMetricEndpointComplex,
        payload: Mapping[str, object],
    ) -> "ProlongedMetricEndpointBackwardWitness":
        if payload.get("schema") != (
            "pure-weyl-prolonged-metric-endpoint-backward-witness-coefficients-v1"
        ):
            raise AssertionError("wrong endpoint W0 coefficient schema")

        def parse(section: Mapping[str, object], name: str) -> CoefficientTable:
            value = section.get(name)
            if not isinstance(value, Mapping):
                raise AssertionError(f"missing W0 coefficient table {name}")
            shape = value.get("shape")
            coefficients = value.get("coefficients")
            if not isinstance(shape, list) or not isinstance(coefficients, list):
                raise AssertionError(f"malformed W0 coefficient table {name}")
            output: list[tuple[Multiindex, sp.Matrix]] = []
            for item in coefficients:
                if not isinstance(item, Mapping):
                    raise AssertionError(f"malformed W0 coefficient item {name}")
                matrix = sp.zeros(shape[0], shape[1])
                entries = item.get("entries")
                if not isinstance(entries, list):
                    raise AssertionError(f"malformed W0 sparse table {name}")
                for row, column, coefficient in entries:
                    matrix[row, column] = sp.Rational(coefficient)
                output.append((tuple(item["multiindex"]), matrix))
            result = tuple(output)
            if _digest_tables(result) != value.get("sha256"):
                raise AssertionError(f"W0 coefficient digest mismatch {name}")
            return result

        witness = payload.get("W0")
        blocks = payload.get("D_end")
        auxiliaries = payload.get("composition_inputs")
        if not all(
            isinstance(value, Mapping)
            for value in (witness, blocks, auxiliaries)
        ):
            raise AssertionError("endpoint W0 payload is incomplete")
        assert isinstance(witness, Mapping)
        assert isinstance(blocks, Mapping)
        assert isinstance(auxiliaries, Mapping)
        result = ProlongedMetricEndpointBackwardWitness(
            endpoint=endpoint,
            t_gf_coefficients=parse(witness, "T_gf"),
            middle_coefficients=parse(witness, "middle_2I"),
            t_gf_sharp_coefficients=parse(witness, "T_gf_sharp"),
            ghost_block_coefficients=parse(blocks, "D_G"),
            field_block_coefficients=parse(blocks, "D_M"),
            equation_block_coefficients=parse(blocks, "D_E"),
            identity_block_coefficients=parse(blocks, "D_I"),
            kt_coefficients=parse(auxiliaries, "K_T_gf"),
        )
        result.verify()
        return result

    def verify(self) -> None:
        expected = {
            "T_gf": (self.t_gf_coefficients, (5, 10), 35, 3),
            "2I": (self.middle_coefficients, (10, 10), 1, 0),
            "T_gf_sharp": (self.t_gf_sharp_coefficients, (10, 5), 35, 3),
            "D_G": (self.ghost_block_coefficients, (5, 5), 70, 4),
            "D_M": (self.field_block_coefficients, (10, 10), 70, 4),
            "D_E": (self.equation_block_coefficients, (10, 10), 70, 4),
            "D_I": (self.identity_block_coefficients, (5, 5), 70, 4),
            "KT": (self.kt_coefficients, (10, 10), 70, 4),
        }
        for name, (table, shape, count, maximum_order) in expected.items():
            if len(table) != count or any(
                matrix.shape != shape for _, matrix in table
            ):
                raise AssertionError(f"{name} coefficient coverage drifted")
            if max(sum(multiindex) for multiindex, _ in table) != maximum_order:
                raise AssertionError(f"{name} order drifted")
        if self.middle_coefficients != _identity_table(10, 2):
            raise AssertionError("middle W0 block is not 2 fibre-identification")

        expected_sharp = _formal_pairing_adjoint(
            self.t_gf_coefficients,
            source_pairing=self.endpoint.field_pairing,
            target_pairing=self.endpoint.ghost_pairing,
        )
        if self.t_gf_sharp_coefficients != expected_sharp:
            raise AssertionError("upper W0 block is not T_gf sharp")
        if self.field_block_coefficients != _add_tables(
            self.endpoint.bach_coefficients,
            self.kt_coefficients,
            left_scale=2,
        ):
            raise AssertionError("D_M is not 2 Bach+K T_gf")
        if self.equation_block_coefficients != _formal_pairing_adjoint(
            self.field_block_coefficients,
            source_pairing=self.endpoint.field_pairing,
            target_pairing=self.endpoint.field_pairing,
        ):
            raise AssertionError("D_E is not the formal adjoint of D_M")
        if self.identity_block_coefficients != _formal_pairing_adjoint(
            self.ghost_block_coefficients,
            source_pairing=self.endpoint.ghost_pairing,
            target_pairing=self.endpoint.ghost_pairing,
        ):
            raise AssertionError("D_I is not the formal adjoint of D_G")

        # The exhaustive build checked the vector diagonal directly against
        # the independently evaluated cylinder ghost biwave.  The fast rail
        # reruns the remaining purely algebraic triangular structure.
        inverse_metric = sp.diag(-1, 1, 1, 1)
        for multiindex, coefficient in self.ghost_block_coefficients:
            expected_divergence = sp.zeros(1, 4)
            if sum(multiindex) == 1:
                axis = multiindex.index(1)
                expected_divergence[0, :] = (
                    sp.Rational(1, 2) * inverse_metric[axis, :]
                )
            if coefficient[:4, 4] != sp.zeros(4, 1):
                raise AssertionError("Weyl scalar leaked into vector ghost biwave")
            if coefficient[4:5, :4] != expected_divergence:
                raise AssertionError("scalar/vector triangular ghost entry drifted")
            target_scalar = sp.Integer(multiindex == ZERO)
            if coefficient[4, 4] != target_scalar:
                raise AssertionError("Weyl scalar ghost block is not identity")

    def coefficient_payload(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": (
                "pure-weyl-prolonged-metric-endpoint-backward-witness-coefficients-v1"
            ),
            "normal_form": (
                "parallel coefficients on fully symmetrized covariant derivatives; "
                "cylinder curvature commutators included by exact jet evaluation"
            ),
            "W0": {
                "T_gf": _sparse_table(
                    self.t_gf_coefficients, source="M[10]", target="G[5]"
                ),
                "middle_2I": _sparse_table(
                    self.middle_coefficients, source="E[10]", target="M[10]"
                ),
                "T_gf_sharp": _sparse_table(
                    self.t_gf_sharp_coefficients, source="I[5]", target="E[10]"
                ),
            },
            "D_end": {
                "D_G": _sparse_table(
                    self.ghost_block_coefficients, source="G[5]", target="G[5]"
                ),
                "D_M": _sparse_table(
                    self.field_block_coefficients, source="M[10]", target="M[10]"
                ),
                "D_E": _sparse_table(
                    self.equation_block_coefficients, source="E[10]", target="E[10]"
                ),
                "D_I": _sparse_table(
                    self.identity_block_coefficients, source="I[5]", target="I[5]"
                ),
            },
            "composition_inputs": {
                "K_T_gf": _sparse_table(
                    self.kt_coefficients, source="M[10]", target="M[10]"
                ),
            },
        }

    def certificate(
        self,
        *,
        dependencies: Mapping[str, Mapping[str, object]],
        coefficient_payload_sha256: str,
    ) -> dict[str, object]:
        self.verify()
        schemas = {
            "endpoint": "pure-weyl-prolonged-metric-endpoint-complex-v1",
            "ghost_biwave": "pure-weyl-cylinder-ghost-curvature-completion-v1",
            "field_biwave": "pure-weyl-cylinder-full-metric-biwave-v1",
            "minimal_witness": "pure-weyl-minimal-witness-block-matrix-v1",
        }
        for name, schema in schemas.items():
            value = dependencies.get(name)
            if not isinstance(value, Mapping) or value.get("schema") != schema:
                raise AssertionError(f"missing W0 dependency {name}")
        endpoint_certificate = dependencies["endpoint"]
        if endpoint_certificate.get("Q_end", {}).get("Q_end_squared") != "zero":
            raise AssertionError("exact endpoint differential is unavailable")
        ghost = dependencies["ghost_biwave"]
        factorization = ghost.get("factorization")
        if not isinstance(factorization, Mapping) or factorization.get("product") != (
            "R_minus R_plus=Box(Box+2) I_G"
        ):
            raise AssertionError("ghost biwave factorization drifted")
        field = dependencies["field_biwave"]
        if field.get("witness_field_block") != "2H=2B_lin+K T":
            raise AssertionError("field witness normalization drifted")
        minimal = dependencies["minimal_witness"]
        backward = minimal.get("backward_blocks")
        if not isinstance(backward, Mapping) or backward.get("E_to_M") != (
            "2 sharp^{-1}"
        ):
            raise AssertionError("minimal W0 middle normalization drifted")

        return {
            "schema": "pure-weyl-prolonged-metric-endpoint-backward-witness-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "dependency_sha256": {
                name: _certificate_digest(value)
                for name, value in dependencies.items()
            },
            "coefficient_payload_sha256": coefficient_payload_sha256,
            "endpoint_order": ["G[5]", "M[10]", "E[10]", "I[5]"],
            "W0": {
                "degree": -1,
                "nonzero_blocks": {
                    "M_to_G": "T_gf=(T_completed P_TF, trace/4)",
                    "E_to_M": "2 fibre-identification",
                    "I_to_E": "T_gf^sharp",
                },
                "maximum_order": 3,
                "graded_cyclic": True,
                "coefficient_sha256": {
                    "T_gf": _digest_tables(self.t_gf_coefficients),
                    "middle_2I": _digest_tables(self.middle_coefficients),
                    "T_gf_sharp": _digest_tables(self.t_gf_sharp_coefficients),
                },
            },
            "D_end": {
                "identity": "D_end=Q_end W0+W0 Q_end",
                "off_diagonal_blocks": "zero",
                "degreewise_blocks": {
                    "G": "T_gf K_met",
                    "M": "2 Bach_bar+K_met T_gf=2H",
                    "E": "2 Bach_bar+T_gf^sharp C_met=(D_M)^sharp",
                    "I": "C_met T_gf^sharp=(D_G)^sharp",
                },
                "maximum_order": 4,
                "coefficientwise_complete": True,
                "formal_adjoint_defects": 0,
                "coefficient_sha256": {
                    "D_G": _digest_tables(self.ghost_block_coefficients),
                    "D_M": _digest_tables(self.field_block_coefficients),
                    "D_E": _digest_tables(self.equation_block_coefficients),
                    "D_I": _digest_tables(self.identity_block_coefficients),
                },
            },
            "ghost_block": {
                "matrix_form": [
                    ["Box(Box+2) I_4", "0"],
                    ["(1/2) div", "I_1"],
                ],
                "vector_factorization": ["Box+Ric", "Box-Ric+2"],
                "curved_lower_order_coefficients_included": True,
                "Weyl_scalar_completion": "pointwise identity",
            },
            "endpoint_green_filtration_input": {
                "D_end_available_coefficientwise": True,
                "formula_for_relative_saddle": "S_end=D_end-C B",
                "required_exported_tables": [
                    "D_G",
                    "D_M",
                    "D_E",
                    "D_I",
                    "K_T_gf",
                ],
                "all_exported": True,
            },
            "support": {
                "finite_order": True,
                "maximum_order": 4,
                "inverse_Laplacian_or_curl": False,
                "spectral_or_helicity_projector": False,
                "Green_operator": False,
            },
            "proof_boundary": (
                "W0 and D_end are exact algebraic differential-operator data; "
                "this certificate does not prove that D_end or a relative saddle "
                "has advanced/retarded inverses"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [
                "endpoint_canonical_backward_witness_exact",
                "endpoint_D_end_coefficientwise_exact",
            ],
            "status_flags_promoted": [],
            "fail_closed": True,
        }


def write_payload(path: Path, payload: Mapping[str, object]) -> str:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
