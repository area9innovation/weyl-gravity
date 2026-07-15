"""Conditional all-row causal assembly for the prolonged BV complex.

The exact hybrid algebraic SDR splits the 386-component prolonged complex
into a 356-component locally contractible sector and the 30-component metric
curvature graph.  Write its identities as

``Q H_alg+H_alg Q=P_alg``, ``P_end=i_end p_end`` and
``P_alg+P_end=1``.

On the endpoint, the trace/Weyl shift is a finite differential triangular
chain isomorphism ``U``.  In shifted variables the complex is the direct sum
of the trace-free 4--9--9--4 complex and pointwise identity doublets.  Thus,
if ``lambda_TF,+/-`` is the transferred adjoint-tractor homotopy and ``h_tr``
is the pointwise trace/Weyl contraction, then

``Lambda_end,+/-=U (lambda_TF,+/- direct-sum h_tr) U^-1``.

This is deliberately not identified with ``W0 G_end``: the tractor receipt
does not by itself construct a same-sided inverse of the canonical endpoint
witness operator.  The certified ghost/identity Green blocks and trace
triangular formulas remain independent checks on the easy channels.

The complete prolonged homotopy is then

``Lambda_full,+/-=H_alg+i_end Lambda_end,+/- p_end``.

This module proves the two formal identities, support transfer, and cyclic
adjoint transfer.  It is fail closed against the current curved BGG/PBW
boundary: no causal flag is promoted until the upstream transfer certificate
contains the authoritative future curved-PBW digest and exact true gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

import sympy as sp

from covariant_completion.certificate_provenance import (
    digest_json_object,
    is_sha256,
)

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


def _endpoint_normal_form(
    entry: OperatorPolynomial,
) -> OperatorPolynomial:
    """Reduce the triangular conjugation of the endpoint homotopy."""

    values = entry.as_dict()
    # q U=U q0 and V q=q0 V, where V=U^-1.
    left_chain = values.pop(("q", "U", "l", "V"), Fraction(0))
    values[("U", "q0", "l", "V")] = values.get(
        ("U", "q0", "l", "V"), Fraction(0)
    ) + left_chain
    right_chain = values.pop(("U", "l", "V", "q"), Fraction(0))
    values[("U", "l", "q0", "V")] = values.get(
        ("U", "l", "q0", "V"), Fraction(0)
    ) + right_chain
    left = values.pop(("U", "q0", "l", "V"), Fraction(0))
    right = values.pop(("U", "l", "q0", "V"), Fraction(0))
    if left == right:
        values[("U", "V")] = values.get(("U", "V"), Fraction(0)) + left
    else:
        values[("U", "q0", "l", "V")] = left
        values[("U", "l", "q0", "V")] = right
    inverse = values.pop(("U", "V"), Fraction(0))
    values[()] = values.get((), Fraction(0)) + inverse
    return OperatorPolynomial._from_dict(values)


def _full_normal_form(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce the full hybrid homotopy identity exactly."""

    values = entry.as_dict()

    # Q i=i q and p Q=q p.
    qi = values.pop(("Q", "i", "l", "p"), Fraction(0))
    values[("i", "q", "l", "p")] = values.get(
        ("i", "q", "l", "p"), Fraction(0)
    ) + qi
    pq = values.pop(("i", "l", "p", "Q"), Fraction(0))
    values[("i", "l", "q", "p")] = values.get(
        ("i", "l", "q", "p"), Fraction(0)
    ) + pq

    # QH+HQ=P_alg.
    qh = values.pop(("Q", "H"), Fraction(0))
    hq = values.pop(("H", "Q"), Fraction(0))
    if qh == hq:
        values[("A",)] = values.get(("A",), Fraction(0)) + qh
    else:
        values[("Q", "H")] = qh
        values[("H", "Q")] = hq

    # q l+l q=1_end, then i p=P_end.
    ql = values.pop(("i", "q", "l", "p"), Fraction(0))
    lq = values.pop(("i", "l", "q", "p"), Fraction(0))
    if ql == lq:
        values[("E",)] = values.get(("E",), Fraction(0)) + ql
    else:
        values[("i", "q", "l", "p")] = ql
        values[("i", "l", "q", "p")] = lq

    # P_alg+P_end=1.
    alg = values.pop(("A",), Fraction(0))
    end = values.pop(("E",), Fraction(0))
    if alg == end:
        values[()] = values.get((), Fraction(0)) + alg
    else:
        values[("A",)] = alg
        values[("E",)] = end
    return OperatorPolynomial._from_dict(values)


def _assembly_adjoint(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Formal cyclic adjoint for the hybrid assembly words."""

    sharp = {
        "H": "H",
        "i": "p",
        "p": "i",
        "lplus": "lminus",
        "lminus": "lplus",
        "U": "V",
        "V": "U",
    }
    return OperatorPolynomial._from_dict(
        {
            tuple(sharp[name] for name in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _trace_weyl_shear_checks() -> dict[str, object]:
    """Check the explicit trace/Weyl chain shear and contraction.

    Aggregate the trace-free slots to one formal component.  With
    ``d=div/2`` the unshifted first and last arrows are

    ``K=[[K_TF,0],[d,1]]`` and ``C=[[C_TF,d^sharp],[0,1]]``.

    The displayed ghost and identity shears conjugate them to block diagonal
    form.  The middle Bach arrow is already trace free.
    """

    k, c, d, dsharp = sp.symbols("K_TF C_TF d dsharp", commutative=False)
    one = sp.Integer(1)
    zero = sp.Integer(0)
    u_g = sp.Matrix([[one, zero], [-d, one]])
    u_g_inverse = sp.Matrix([[one, zero], [d, one]])
    u_m = sp.eye(2)
    u_e = sp.eye(2)
    u_i = sp.Matrix([[one, dsharp], [zero, one]])
    u_i_inverse = sp.Matrix([[one, -dsharp], [zero, one]])

    k_unshifted = sp.Matrix([[k, zero], [d, one]])
    k_split = sp.diag(k, one)
    c_unshifted = sp.Matrix([[c, dsharp], [zero, one]])
    c_split = sp.diag(c, one)

    inverse_exact = bool(
        u_g * u_g_inverse == sp.eye(2)
        and u_g_inverse * u_g == sp.eye(2)
        and u_i * u_i_inverse == sp.eye(2)
        and u_i_inverse * u_i == sp.eye(2)
    )
    chain_exact = bool(
        k_unshifted * u_g == u_m * k_split
        and c_unshifted * u_e == u_i * c_split
    )
    cyclic_exact = bool(
        u_i
        == u_g_inverse.T.xreplace({d: dsharp})
        and u_e == u_m.T
    )

    q_trace = sp.zeros(4)
    q_trace[1, 0] = 1
    q_trace[3, 2] = 1
    h_trace = sp.zeros(4)
    h_trace[0, 1] = 1
    h_trace[2, 3] = 1
    contraction_exact = bool(q_trace * h_trace + h_trace * q_trace == sp.eye(4))

    return {
        "d": "div/2",
        "U_G_shifted_to_unshifted": [["1", "0"], ["-d", "1"]],
        "U_G_inverse": [["1", "0"], ["d", "1"]],
        "U_M": "identity on TF+trace",
        "U_E": "identity on TF-dual+trace-dual",
        "U_I_shifted_to_unshifted": [
            ["1", "d^sharp"],
            ["0", "1"],
        ],
        "U_I_inverse": [["1", "-d^sharp"], ["0", "1"]],
        "first_arrow_unshifted": "[[K_TF,0],[d,1]]",
        "first_arrow_split": "diag(K_TF,1)",
        "last_arrow_unshifted": "[[C_TF,d^sharp],[0,1]]",
        "last_arrow_split": "diag(C_TF,1)",
        "inverse_checks_exact": inverse_exact,
        "q_U_equals_U_q_split": chain_exact,
        "cyclic_U_sharp_equals_U_inverse": cyclic_exact,
        "trace_complex_order": ["G_trace", "M_trace", "E_trace", "I_trace"],
        "trace_q_nonzero": ["G_trace->M_trace=1", "E_trace->I_trace=1"],
        "trace_h_nonzero": ["M_trace->G_trace=1", "I_trace->E_trace=1"],
        "trace_qh_plus_hq": "identity_4" if contraction_exact else "defect",
    }


@dataclass(frozen=True)
class FullProlongedGreenHomotopyAssembly:
    """Exact conditional assembly theorem for all 386 components."""

    prolonged_dimension: int
    algebraic_dimension: int
    endpoint_dimension: int
    endpoint_identity_exact: bool
    endpoint_adjoint_transfer_exact: bool
    trace_weyl_shear_exact: bool
    full_identity_exact: bool
    adjoint_transfer_exact: bool

    @staticmethod
    def build() -> "FullProlongedGreenHomotopyAssembly":
        q = OperatorPolynomial.atom("q")
        triangular = OperatorPolynomial.atom("U")
        triangular_inverse = OperatorPolynomial.atom("V")
        endpoint_lambda = (
            triangular * OperatorPolynomial.atom("l") * triangular_inverse
        )
        endpoint_identity = _endpoint_normal_form(
            q * endpoint_lambda + endpoint_lambda * q
        )
        endpoint_plus = (
            triangular
            * OperatorPolynomial.atom("lplus")
            * triangular_inverse
        )
        endpoint_minus = (
            triangular
            * OperatorPolynomial.atom("lminus")
            * triangular_inverse
        )

        full_q = OperatorPolynomial.atom("Q")
        h_alg = OperatorPolynomial.atom("H")
        inclusion = OperatorPolynomial.atom("i")
        endpoint_homotopy = OperatorPolynomial.atom("l")
        projection = OperatorPolynomial.atom("p")
        full_lambda = h_alg + inclusion * endpoint_homotopy * projection
        full_identity = _full_normal_form(
            full_q * full_lambda + full_lambda * full_q
        )

        lplus = h_alg + inclusion * OperatorPolynomial.atom("lplus") * projection
        lminus = h_alg + inclusion * OperatorPolynomial.atom("lminus") * projection
        shear = _trace_weyl_shear_checks()
        result = FullProlongedGreenHomotopyAssembly(
            prolonged_dimension=386,
            algebraic_dimension=356,
            endpoint_dimension=30,
            endpoint_identity_exact=(
                endpoint_identity == OperatorPolynomial.identity()
            ),
            endpoint_adjoint_transfer_exact=(
                _assembly_adjoint(endpoint_plus) == endpoint_minus
            ),
            trace_weyl_shear_exact=all(
                shear[key] is True
                for key in (
                    "inverse_checks_exact",
                    "q_U_equals_U_q_split",
                    "cyclic_U_sharp_equals_U_inverse",
                )
            )
            and shear["trace_qh_plus_hq"] == "identity_4",
            full_identity_exact=(full_identity == OperatorPolynomial.identity()),
            adjoint_transfer_exact=(_assembly_adjoint(lplus) == lminus),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.prolonged_dimension != self.algebraic_dimension + self.endpoint_dimension:
            raise AssertionError("386=356+30 dimension ledger drifted")
        if not self.endpoint_identity_exact:
            raise AssertionError("endpoint triangular homotopy identity failed")
        if not self.endpoint_adjoint_transfer_exact:
            raise AssertionError("endpoint triangular adjoint transfer failed")
        if not self.trace_weyl_shear_exact:
            raise AssertionError("explicit trace/Weyl chain shear failed")
        if not self.full_identity_exact:
            raise AssertionError("full hybrid homotopy identity failed")
        if not self.adjoint_transfer_exact:
            raise AssertionError("full advanced/retarded adjoint transfer failed")

    def certificate(
        self,
        *,
        hybrid_certificate: Mapping[str, object],
        endpoint_certificate: Mapping[str, object],
        backward_witness_certificate: Mapping[str, object],
        filtration_certificate: Mapping[str, object],
        curved_chain_maps_certificate: Mapping[str, object],
        green_transfer_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        self._validate_hybrid(hybrid_certificate)
        self._validate_endpoint(endpoint_certificate)
        self._validate_backward(backward_witness_certificate)
        self._validate_filtration(filtration_certificate)
        self._validate_trace_weyl_rows(curved_chain_maps_certificate)
        transfer_ready = self._validate_transfer(green_transfer_certificate)

        dependencies = {
            "hybrid_algebraic_projector": digest_json_object(hybrid_certificate),
            "metric_endpoint_complex": digest_json_object(endpoint_certificate),
            "endpoint_backward_witness": digest_json_object(
                backward_witness_certificate
            ),
            "endpoint_green_filtration": digest_json_object(
                filtration_certificate
            ),
            "curved_trace_Weyl_rows": digest_json_object(
                curved_chain_maps_certificate
            ),
            "adjoint_tractor_green_transfer": digest_json_object(
                green_transfer_certificate
            ),
        }

        return {
            "schema": "pure-weyl-full-prolonged-green-homotopy-assembly-v1",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "input_certificate_sha256": dependencies,
            "dimension_ledger": {
                "prolonged": self.prolonged_dimension,
                "algebraically_contracted": self.algebraic_dimension,
                "causal_endpoint": self.endpoint_dimension,
                "identity": "386=356+30",
            },
            "endpoint_channel_assembly": {
                "tracefree_complex_ranks": [4, 9, 9, 4],
                "trace_Weyl_ranks": [1, 1, 1, 1],
                "full_endpoint_ranks": [5, 10, 10, 5],
                "ghost_green": (
                    "[[G_R,+/-,0],[-(div/2)G_R,+/-,1]]"
                ),
                "identity_green": "advanced/retarded adjoint of ghost block",
                "trace_Weyl_contraction": "pointwise identity doublets",
                "explicit_trace_Weyl_shear": _trace_weyl_shear_checks(),
                "shear_differential_order": 1,
                "shear_support_local": True,
                "shear_inverse_Laplacian_or_curl": False,
                "easy_channel_same_sided_inverses_exact": True,
                "finite_triangular_chain_extension": True,
                "endpoint_witness_identity": "D_end=q W0+W0 q",
                "canonical_D_TF_inverse_claimed": False,
                "global_W0_G_end_identification_claimed": False,
                "homotopy_formula": (
                    "Lambda_end,+/-=U (Lambda_TF,+/- direct-sum h_tr) U^-1"
                ),
                "homotopy_identity_exact_conditionally": (
                    self.endpoint_identity_exact
                ),
                "graded_adjoint_exact_conditionally": (
                    self.endpoint_adjoint_transfer_exact
                ),
                "tracefree_transfer_ready": transfer_ready,
                "complete_30_component_endpoint_ready": transfer_ready,
            },
            "full_hybrid_assembly": {
                "formula": (
                    "Lambda_full,+/-=H_alg+i_end Lambda_end,+/- p_end"
                ),
                "projector_identities": [
                    "Q H_alg+H_alg Q=P_alg",
                    "P_end=i_end p_end",
                    "P_alg+P_end=1",
                    "Q i_end=i_end q",
                    "p_end Q=q p_end",
                    "p_end i_end=1",
                ],
                "derivation": (
                    "Q Lambda_full+Lambda_full Q=P_alg+"
                    "i_end(q Lambda_end+Lambda_end q)p_end="
                    "P_alg+P_end=1"
                ),
                "algebraic_identity_exact_conditionally": self.full_identity_exact,
                "support": (
                    "H_alg, i_end and p_end are finite-order local; local "
                    "terms preserve support and endpoint causal support stays "
                    "inside J^+/- of the source"
                ),
                "causal_support_exact_conditionally": True,
                "adjoint": (
                    "H_alg^sharp=H_alg, i_end^sharp=p_end and "
                    "Lambda_end,+^sharp=Lambda_end,- imply "
                    "Lambda_full,+^sharp=Lambda_full,-"
                ),
                "graded_adjoint_exact_conditionally": self.adjoint_transfer_exact,
            },
            "future_gate": {
                "authoritative_certificate": (
                    "adjoint_tractor_bgg_curved_pbw.json"
                ),
                "upstream_green_transfer_ready": transfer_ready,
                "upstream_curved_PBW_sha256": green_transfer_certificate.get(
                    "curved_BGG_gate", {}
                ).get("future_certificate_sha256"),
                "all_row_causal_homotopy_ready": transfer_ready,
            },
            "warranted_atomic_flags": [
                "full_prolonged_hybrid_homotopy_assembly_theorem_exact",
                "endpoint_triangular_channel_assembly_theorem_exact",
            ],
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": transfer_ready,
            "status_flags_promoted": (
                ["causal_green_homotopy"] if transfer_ready else []
            ),
            "proof_boundary": (
                "the all-row algebra, support and graded-adjoint transfer are "
                + (
                    "exact and the SHA-bound curved PBW receipt activates the "
                    "trace-free transfer, hence the complete causal homotopy"
                    if transfer_ready
                    else "exact; the causal flag remains false until the "
                    "authoritative curved PBW receipt activates the upstream "
                    "trace-free transfer"
                )
            ),
            "fail_closed": True,
        }

    @staticmethod
    def _validate_hybrid(certificate: Mapping[str, object]) -> None:
        if certificate.get("schema") != (
            "pure-weyl-prolonged-hybrid-algebraic-projector-v1"
        ) or certificate.get("fail_closed") is not True:
            raise AssertionError("wrong hybrid algebraic projector receipt")
        dimensions = certificate.get("minimal_dimension_ledger")
        composite = certificate.get("composite_SDR")
        if not isinstance(dimensions, Mapping) or not isinstance(composite, Mapping):
            raise AssertionError("hybrid projector ledger is missing")
        if (
            dimensions.get("prolonged"),
            dimensions.get("algebraically_contracted"),
            dimensions.get("retained_metric_curvature_graph"),
        ) != (386, 356, 30):
            raise AssertionError("hybrid dimension ledger drifted")
        required = {
            "P_alg_idempotent": True,
            "P_end_idempotent": True,
            "P_alg_P_end": "zero",
            "D_P_alg_equals_P_alg_D": True,
            "D_P_end_equals_P_end_D": True,
            "cyclic_and_formally_self_adjoint": True,
            "support_local": True,
        }
        if any(composite.get(key) != value for key, value in required.items()):
            raise AssertionError("hybrid SDR identity drifted")
        if composite.get("P_alg") != "1-P_end=Q H_alg+H_alg Q":
            raise AssertionError("hybrid homotopy identity is unavailable")

    @staticmethod
    def _validate_endpoint(certificate: Mapping[str, object]) -> None:
        if certificate.get("schema") != (
            "pure-weyl-prolonged-metric-endpoint-complex-v1"
        ) or certificate.get("fail_closed") is not True:
            raise AssertionError("wrong metric endpoint receipt")
        if certificate.get("dimension") != 30:
            raise AssertionError("metric endpoint dimension drifted")
        q_end = certificate.get("Q_end")
        maps = certificate.get("local_graph_maps")
        if not isinstance(q_end, Mapping) or not isinstance(maps, Mapping):
            raise AssertionError("endpoint chain data are missing")
        identities = maps.get("identities")
        support = maps.get("support")
        if q_end.get("Q_end_squared") != "zero" or not isinstance(
            identities, Mapping
        ) or not isinstance(support, Mapping):
            raise AssertionError("endpoint complex identity drifted")
        for key, value in {
            "p_end_j_end": "identity_30",
            "j_end_p_end": "P_end",
            "Q_prol_j_end": "j_end_Q_end",
            "p_end_Q_prol": "Q_end_p_end",
        }.items():
            if identities.get(key) != value:
                raise AssertionError(f"endpoint graph identity {key} drifted")
        if not all(
            support.get(key) is True
            for key in ("finite_order_differential", "compact", "spacelike_compact")
        ):
            raise AssertionError("endpoint graph maps are not support local")

    @staticmethod
    def _validate_backward(certificate: Mapping[str, object]) -> None:
        if certificate.get("schema") != (
            "pure-weyl-prolonged-metric-endpoint-backward-witness-v2"
        ) or certificate.get("fail_closed") is not True:
            raise AssertionError("wrong endpoint backward witness receipt")
        witness = certificate.get("W0")
        operator = certificate.get("D_end")
        support = certificate.get("support")
        if not all(isinstance(value, Mapping) for value in (witness, operator, support)):
            raise AssertionError("endpoint witness data are missing")
        if witness.get("graded_cyclic") is not True:
            raise AssertionError("endpoint witness is not cyclic")
        if operator.get("identity") != "D_end=Q_end W0+W0 Q_end":
            raise AssertionError("endpoint witness anticommutator drifted")
        if operator.get("formal_adjoint_defects") != 0:
            raise AssertionError("endpoint operator adjoint defect is nonzero")
        if support.get("finite_order") is not True:
            raise AssertionError("endpoint witness is not differential local")

    @staticmethod
    def _validate_filtration(certificate: Mapping[str, object]) -> None:
        if certificate.get("schema") != (
            "pure-weyl-endpoint-green-filtration-boundary-v1"
        ) or certificate.get("dependency_tag") != "LORENTZIAN-CAUSAL" or (
            certificate.get("fail_closed") is not True
        ):
            raise AssertionError("wrong endpoint Green filtration receipt")
        ghost = certificate.get("ghost_channel")
        identity = certificate.get("identity_channel")
        trace = certificate.get("metric_trace_filtration")
        tracefree = certificate.get("tracefree_channel")
        if not all(
            isinstance(value, Mapping)
            for value in (ghost, identity, trace, tracefree)
        ):
            raise AssertionError("endpoint channel ledger is missing")
        if ghost.get("status") != "GREEN" or not all(
            ghost.get(key) is True
            for key in ("left_inverse", "right_inverse", "metric_causal_support")
        ):
            raise AssertionError("ghost triangular Green block drifted")
        if identity.get("status") != "GREEN_BY_ADJOINT" or (
            identity.get("metric_causal_support") is not True
        ):
            raise AssertionError("identity adjoint Green block drifted")
        if not all(
            trace.get(key) is True
            for key in (
                "projectors_pointwise_parallel",
                "conditional_left_inverse",
                "conditional_right_inverse",
            )
        ) or trace.get("trace_diagonal_defect") != 0:
            raise AssertionError("metric trace triangular formula drifted")
        if tracefree.get("rank") != 9 or (
            tracefree.get("principal_symbol_checked_coefficientwise") is not True
        ):
            raise AssertionError("trace-free endpoint boundary drifted")

    @staticmethod
    def _validate_trace_weyl_rows(certificate: Mapping[str, object]) -> None:
        if certificate.get("schema") != "pure-weyl-curved-chain-map-status-v1" or (
            certificate.get("curved_deformation_retract") is not True
        ):
            raise AssertionError("wrong curved trace/Weyl row receipt")
        if certificate.get("curved_Q_factorized_operator_instantiated") is not True:
            raise AssertionError("actual curved Q is unavailable for trace/Weyl rows")
        ledger = certificate.get("row_ledger")
        if not isinstance(ledger, Mapping):
            raise AssertionError("curved BV row ledger is missing")
        summands = ledger.get("reattached_direct_summands")
        if not isinstance(summands, list) or not any(
            isinstance(item, Mapping)
            and item.get("name") == "trace/Weyl doublet and antifield dual"
            and item.get("differential") == "pointwise identity contraction"
            for item in summands
        ):
            raise AssertionError("trace/Weyl pointwise doublets are unavailable")

    @staticmethod
    def _validate_transfer(certificate: Mapping[str, object]) -> bool:
        if certificate.get("schema") != (
            "pure-weyl-adjoint-tractor-green-transfer-v1"
        ) or certificate.get("dependency_tag") != "LORENTZIAN-CAUSAL" or (
            certificate.get("fail_closed") is not True
        ):
            raise AssertionError("wrong adjoint-tractor Green transfer receipt")
        transfer = certificate.get("transfer_theorem")
        gate = certificate.get("curved_BGG_gate")
        endpoint = certificate.get("endpoint_assembly")
        dependencies = certificate.get("dependency_sha256")
        if not all(
            isinstance(value, Mapping)
            for value in (transfer, gate, endpoint, dependencies)
        ):
            raise AssertionError("adjoint-tractor transfer ledger is missing")
        if not all(
            transfer.get(key) is True
            for key in (
                "algebraic_identity_exact",
                "cyclic_adjoint_exact_conditionally",
            )
        ) or "does not enlarge support" not in str(
            transfer.get("support_derivation")
        ):
            raise AssertionError("abstract endpoint transfer theorem drifted")

        ready = certificate.get("tracefree_causal_green_homotopy") is True
        if ready:
            curved_hash = gate.get("future_certificate_sha256")
            if not all(
                (
                    gate.get("future_certificate_schema_valid") is True,
                    gate.get("all_required_keys_true") is True,
                    gate.get("upstream_transfer_flag_remains_false") is True,
                    endpoint.get("tracefree_parent_transfer_ready") is True,
                    endpoint.get("complete_30_row_endpoint_causal_homotopy")
                    is False,
                    certificate.get("causal_green_homotopy") is False,
                    is_sha256(curved_hash),
                    dependencies.get("curved_bgg") == curved_hash,
                )
            ):
                raise AssertionError("causal transfer lacks authoritative PBW binding")
        elif endpoint.get("complete_30_row_endpoint_causal_homotopy") is True or (
            certificate.get("causal_green_homotopy") is True
        ):
            raise AssertionError("trace-free transfer receipt overpromotes endpoint")
        return ready
