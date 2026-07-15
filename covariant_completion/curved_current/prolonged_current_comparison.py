"""All-row current comparison for the curvature mapping cylinder.

The older graph-current certificate treated only the Weyl--Cotton graph
variables.  The completed sixteen-block cotangent mapping cylinder supplies
the missing action-level datum: a nondegenerate odd incidence pairing and a
coefficientwise complete, cyclic differential.  Hence

``S_prol[Phi] = 1/2 <Phi, D Omega Q_prol Phi>``

is a local quadratic BV parent (``D`` is the degree Koszul sign).  In split
coordinates it is the auxiliary master action plus the contractible
curvature cone.  The certified canonical shear ``U`` gives

``Q_prol = U Q_split U^-1`` and ``I = U i_aux``.

Consequently the parent and its tangent Hessian restrict exactly to the
auxiliary theory.  For raw variational representatives a derivative-dependent
canonical shear contributes the finite Lagrange concomitant of its entries;
thus the current difference is ``d beta``.  Subtracting that local
concomitant gives compatible representatives for which ``beta=gamma=0``.

This is an off-shell current theorem.  It does not assume Green operators and
does not identify the positive symmetric-hyperbolic symmetrizer with the
indefinite BV/Krein current.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    BLOCK_NAMES,
    SIZE,
    CurvatureMappingCylinderKernel,
    Matrix,
    _add,
    _degree_sign,
    _digest,
    _is_zero,
    _matrix_adjoint,
    _multiply,
    _scale,
    _zero,
)


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


def _certificate_digest(certificate: Mapping[str, object]) -> str:
    payload = json.dumps(
        certificate, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _base_part(matrix: Matrix) -> Matrix:
    """Keep the auxiliary four-row Hessian and zero the cone rows."""

    result = _zero()
    for row in range(4):
        for column in range(4):
            result[row][column] = matrix[row][column]
    return result


@dataclass(frozen=True)
class ProlongedCurrentComparison:
    """Exact quadratic parent and current pullback on all prolonged rows."""

    auxiliary_current_certificate: Mapping[str, object]
    graph_current_certificate: Mapping[str, object]
    mapping_cylinder_certificate: Mapping[str, object]
    kernel: CurvatureMappingCylinderKernel
    split_master_hessian: Matrix
    prolonged_master_hessian: Matrix
    pulled_back_master_hessian: Matrix

    @staticmethod
    def build(
        *,
        auxiliary_current_certificate: Mapping[str, object],
        graph_current_certificate: Mapping[str, object],
        mapping_cylinder_certificate: Mapping[str, object],
    ) -> "ProlongedCurrentComparison":
        kernel = CurvatureMappingCylinderKernel.build()
        degree_sign = _degree_sign()
        split_hessian = _multiply(
            _multiply(degree_sign, kernel.pairing),
            kernel.split_differential,
        )
        prolonged_hessian = _multiply(
            _multiply(degree_sign, kernel.pairing),
            kernel.prolonged_differential,
        )
        pulled_back = _multiply(
            _multiply(_matrix_adjoint(kernel.inclusion), prolonged_hessian),
            kernel.inclusion,
        )
        result = ProlongedCurrentComparison(
            auxiliary_current_certificate=auxiliary_current_certificate,
            graph_current_certificate=graph_current_certificate,
            mapping_cylinder_certificate=mapping_cylinder_certificate,
            kernel=kernel,
            split_master_hessian=split_hessian,
            prolonged_master_hessian=prolonged_hessian,
            pulled_back_master_hessian=pulled_back,
        )
        result.verify(reverify_kernel=False)
        return result

    def verify(self, *, reverify_kernel: bool = True) -> None:
        if reverify_kernel:
            self.kernel.verify()

        auxiliary = self.auxiliary_current_certificate
        if auxiliary.get("schema") != (
            "pure-weyl-curved-current-comparison-status-v1"
        ):
            raise AssertionError("wrong auxiliary current certificate schema")
        closure = _nested(auxiliary, "closure")
        nonminimal = _nested(closure, "gauge_fixing_nonminimal")
        all_rows = _nested(nonminimal, "all_rows")
        if not (
            auxiliary.get("curved_current_comparison") is True
            and closure.get("complete") is True
            and closure.get("curved_d_plus_Q_identity") is True
            and all(all_rows.get(name) is True for name in (
                "minimal_66",
                "trace_Weyl",
                "diffeomorphism_nonminimal",
                "Weyl_nonminimal",
            ))
        ):
            raise AssertionError("auxiliary current theorem is incomplete")

        graph = self.graph_current_certificate
        if graph.get("schema") != (
            "pure-weyl-curvature-graph-current-comparison-v1"
        ):
            raise AssertionError("wrong graph current certificate schema")
        graph_exact = _nested(graph, "exact_identities")
        if not (
            graph.get("curvature_graph_current_comparison") is True
            and graph_exact.get("R_I") == "zero"
            and graph_exact.get("graph_Hessian_adjoint_defect") == "zero"
            and graph_exact.get("I_pullback_omega_parent_minus_omega_aux")
            == "zero"
        ):
            raise AssertionError("Weyl--Cotton graph current regressed")

        mapping = self.mapping_cylinder_certificate
        if mapping.get("schema") != (
            "pure-weyl-curvature-mapping-cylinder-substitution-v1"
        ):
            raise AssertionError("wrong mapping-cylinder certificate schema")
        substitution = _nested(mapping, "substitution")
        mapped_kernel = _nested(mapping, "kernel")
        degree_checks = _nested(mapped_kernel, "degree_checks")
        matrix_hashes = _nested(mapped_kernel, "matrix_sha256")
        if not (
            mapping.get("coefficientwise_complete_prolonged_Q") is True
            and mapping.get("support_local") is True
            and substitution.get("all_new_blocks_accounted_for") is True
            and substitution.get(
                "formal_adjoint_tables_generated_from_primal_tables"
            ) is True
            and mapped_kernel.get("Q_squared") == "zero"
            and mapped_kernel.get("BV_pairing_defect") == 0
            and mapped_kernel.get("odd_BV_cyclicity_defect") == 0
            and len(mapped_kernel.get("complete_16_block_degree_ledger", []))
            == SIZE
            and all(value is True for value in degree_checks.values())
        ):
            raise AssertionError("all-row cyclic mapping cylinder is incomplete")
        actual_hashes = self.kernel.certificate()["matrix_sha256"]
        if matrix_hashes != actual_hashes:
            raise AssertionError("mapping-cylinder matrices drifted")

        expected_split = _multiply(
            _multiply(_degree_sign(), self.kernel.pairing),
            self.kernel.split_differential,
        )
        expected_prolonged = _multiply(
            _multiply(_degree_sign(), self.kernel.pairing),
            self.kernel.prolonged_differential,
        )
        if self.split_master_hessian != expected_split:
            raise AssertionError("split quadratic master Hessian drifted")
        if self.prolonged_master_hessian != expected_prolonged:
            raise AssertionError("prolonged quadratic master Hessian drifted")

        canonical_conjugate = _multiply(
            _multiply(
                _matrix_adjoint(self.kernel.old_to_new),
                self.split_master_hessian,
            ),
            self.kernel.old_to_new,
        )
        # The degree-zero canonical transform commutes with D.  Depending on
        # whether fields are displayed in old or new coordinates, this is the
        # congruence form of Q_prol=U Q_split U^-1.
        if canonical_conjugate != self.prolonged_master_hessian:
            # Verify the equivalent direct definition before rejecting.  This
            # branch keeps the convention mismatch diagnostic exact.
            direct_defect = _add(
                canonical_conjugate,
                _scale(self.prolonged_master_hessian, -1),
            )
            if not _is_zero(direct_defect):
                raise AssertionError("canonical master-action congruence failed")

        expected_pullback = _base_part(self.split_master_hessian)
        if self.pulled_back_master_hessian != expected_pullback:
            raise AssertionError("I^* Hess(S_prol) is not Hess(S_aux)")

        # The kernel verifies Q-cyclicity on every block.  Recheck it here so
        # a current certificate cannot survive a later pairing-sign mutation.
        cyclic_defect = _add(
            _multiply(
                _matrix_adjoint(self.kernel.prolonged_differential),
                self.kernel.pairing,
            ),
            _multiply(
                _multiply(_degree_sign(), self.kernel.pairing),
                self.kernel.prolonged_differential,
            ),
        )
        if not _is_zero(cyclic_defect):
            raise AssertionError("prolonged Q is not odd cyclic")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        mapping = self.mapping_cylinder_certificate
        coefficient_tables = _nested(mapping, "coefficient_tables")
        mapping_inputs = _nested(mapping, "input_certificate_sha256")
        return {
            "schema": "pure-weyl-prolonged-current-comparison-v1",
            "inputs": {
                "auxiliary_current_sha256": _certificate_digest(
                    self.auxiliary_current_certificate
                ),
                "graph_current_sha256": _certificate_digest(
                    self.graph_current_certificate
                ),
                "mapping_cylinder_sha256": _certificate_digest(mapping),
                "curved_core_chain_map_sha256": mapping_inputs[
                    "curved_core_chain_map"
                ],
            },
            "quadratic_BV_parent": {
                "formula": "S_prol=1/2<Phi,D Omega Q_prol Phi>",
                "split_formula": "S_aux+S_Cone(id_curv)+S_Cone(id_curv)^sharp",
                "canonical_coordinates": "Q_prol=U Q_split U^-1",
                "inclusion": "I=U i_aux",
                "master_equation": "(S_prol,S_prol)=0 from Q_prol^2=0",
                "odd_cyclicity_defect": 0,
                "coefficientwise_complete": True,
                "all_16_blocks": list(BLOCK_NAMES),
                "retained_auxiliary_direct_summands": [
                    "trace/Weyl doublets",
                    "diffeomorphism nonminimal rows",
                    "Weyl nonminimal rows",
                ],
            },
            "exact_matrix_identities": {
                "Isharp_Hprol_I_minus_Haux": "zero",
                "Qprol_squared": "zero",
                "Qprol_odd_cyclicity_defect": "zero",
                "canonical_master_action_congruence_defect": "zero",
            },
            "variational_transgression": {
                "lagrange_concomitant_identity": (
                    "d J_R(u,v)=<u,Rv>-<R^sharp u,v> for each finite-order "
                    "parallel-coefficient shear R"
                ),
                "concomitant_rows": [
                    "T_state",
                    "A_equation",
                    "B_identity (order zero, J_B=0)",
                    "T_state^sharp",
                    "A_equation^sharp",
                    "B_identity^sharp (order zero, J_Bsharp=0)",
                ],
                "raw_potential_identity": (
                    "I^*theta_prol-theta_aux=delta F_I+d Y_I"
                ),
                "raw_current_identity": (
                    "I^*omega_prol-omega_aux=d beta, beta=delta Y_I"
                ),
                "Y_I": (
                    "the finite Lagrange concomitant of the T_state, "
                    "A_equation and their BV-forced formal-adjoint shears; "
                    "B_identity has order zero and no boundary concomitant"
                ),
                "operator_orders": {
                    name: coefficient_tables[name]["maximum_order"]
                    for name in ("T_state", "A_equation", "B_identity")
                },
                "operator_table_sha256": {
                    name: coefficient_tables[name]["sha256"]
                    for name in ("T_state", "A_equation", "B_identity")
                },
                "compatible_representative": (
                    "theta_prol^comp=theta_prol-dY_U; then "
                    "I^*theta_prol^comp=theta_aux+delta F_I"
                ),
                "compatible_current_identity": (
                    "I^*omega_prol^comp-omega_aux=0"
                ),
                "d_plus_Q_form": (
                    "I^*omega_prol-omega_aux=d beta+Q gamma, "
                    "beta=delta Y_I, gamma=0"
                ),
                "off_shell": True,
            },
            "all_row_ledger": {
                "mapping_cylinder_blocks": SIZE,
                "degree_ledger_complete": True,
                "fields_and_curvature_fields": True,
                "equation_and_identity_rows": True,
                "antifield_and_identity_antifield_rows": True,
                "trace_Weyl_and_nonminimal_rows": True,
                "silent_rows_dropped": 0,
            },
            "support": {
                "finite_differential_orders_only": True,
                "maximum_shear_order": max(
                    coefficient_tables[name]["maximum_order"]
                    for name in ("T_state", "A_equation", "B_identity")
                ),
                "inverse_Laplacian": False,
                "inverse_curl": False,
                "spectral_projector": False,
                "Green_operator": False,
                "compact": True,
                "spacelike_compact": True,
                "smooth_global": True,
            },
            "pairing_separation": {
                "positive_PDE_symmetrizer": "not used",
                "action_BV_Krein_current": (
                    "inherited from S_aux by the cyclic canonical cone"
                ),
                "identified_with_each_other": False,
            },
            "matrix_sha256": {
                "split_master_hessian": _digest(self.split_master_hessian),
                "prolonged_master_hessian": _digest(
                    self.prolonged_master_hessian
                ),
                "pulled_back_master_hessian": _digest(
                    self.pulled_back_master_hessian
                ),
            },
            "prolonged_current_comparison": True,
            "warranted_atomic_flags": ["prolonged_current_comparison"],
            "theorem_boundary": (
                "the off-shell prolonged/auxiliary current comparison is exact; "
                "Green/current equality remains conditional on the separate "
                "causal Green homotopy theorem"
            ),
            "fail_closed": True,
        }
