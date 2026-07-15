"""Homological location of the fixed-temporal intrinsic Jordan chain.

The pair-(1,6), cyclic ``-2 Pi`` witness has the polynomial chain

``a0=2 f_23,  a1=h_23``

at the aligned null root.  The letter ``Q`` used in the polynomial-chain
certificate denotes the *weighted witness pencil*, not the BV differential.
This module keeps those two operators separate and locates both amplitudes in
the exact four-row auxiliary BV complex.

The result is useful for choosing the next analytic architecture.  The
eigenvector ``a0`` is the shifted generalized auxiliary tensor and belongs to
the already certified pointwise contractible ``f_hat -> A_g f_hat^*`` pair.
The generalized amplitude ``a1`` is the retained metric helicity-two
direction.  Its linearized Weyl symbol is nonzero and it is not a gauge
symbol.  Thus the Jordan block is an off-shell triangular extension from a
contractible auxiliary block to the physical metric block.  It is neither a
curvature-cone doublet nor a second physical class.

The extension splits as an ``SO(2)`` bundle representation and, after the
existing support-local BV-canonical auxiliary shift, as a ``Q_BV`` complex.
It does not split as a module for the fixed witness pencil: that is precisely
the parameter-uniform Jordan no-go.  No extra acyclic enlargement is needed
for the *homological* split.  This does not construct a triangular Green
inverse, so no Green or causal flag is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import sympy as sp

from .conventions import SYMMETRIC_COORDINATES, _ordinary_system
from .expanded_hessian import load_coefficient_cache
from .invariant_pairings import _rotation_generators, _tensor_representation
from .null_symbol_rank_obstruction import DEFAULT_CACHE


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
R6_NO_GO_CERTIFICATE = (
    CERTIFICATE_DIR / "curved_expanded_relative_witness_r6_first_order_no_go.json"
)
RETRACT_CERTIFICATE = CERTIFICATE_DIR / "curved_deformation_retract_status.json"
HELICITY_CERTIFICATE = CERTIFICATE_DIR / "curved_helicity_two_channel.json"

FIELD_RANK = 24
GHOST_RANK = 9
H23 = 8
F23 = 18
ALIGNED_COVECTOR = (-1, 1, 0, 0)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nonzero(vector: sp.MatrixBase) -> list[list[object]]:
    return [
        [index, str(vector[index])]
        for index in range(vector.rows)
        if vector[index] != 0
    ]


def _load_required(path: Path, schema: str) -> dict[str, object]:
    payload = json.loads(path.read_text())
    if payload.get("schema") != schema:
        raise AssertionError(f"required certificate schema drifted: {path.name}")
    return payload


@dataclass(frozen=True)
class ExpandedRelativeJordanHomology:
    """Exact BV/symbol classification of ``2 f23 <- h23``."""

    full_bv_field_differential: sp.Matrix
    principal_bv_field_symbol: sp.Matrix
    gauge_symbol: sp.Matrix
    companion_symbol: sp.Matrix
    field_shift_new_to_old: sp.Matrix
    field_shift_old_to_new: sp.Matrix
    a0: sp.Matrix
    a1: sp.Matrix
    q_a0: sp.Matrix
    q_a1: sp.Matrix
    principal_q_a0: sp.Matrix
    principal_q_a1: sp.Matrix
    q_pair: sp.Matrix
    pair_homotopy: sp.Matrix
    pair_projector: sp.Matrix
    little_group_on_hf: sp.Matrix
    source_hashes: tuple[tuple[str, str], ...]

    @staticmethod
    def build() -> "ExpandedRelativeJordanHomology":
        r6 = _load_required(
            R6_NO_GO_CERTIFICATE,
            "pure-weyl-expanded-relative-r6-first-order-no-go-v1",
        )
        retract = _load_required(
            RETRACT_CERTIFICATE,
            "pure-weyl-curved-deformation-retract-status-v1",
        )
        helicity = _load_required(
            HELICITY_CERTIFICATE,
            "pure-weyl-curved-helicity-two-channel-v1",
        )
        intrinsic = r6["intrinsic_polynomial_Jordan_chain"]
        if not intrinsic["all_46_parameter_directions_preserve_both_identities"]:
            raise AssertionError("the required parameter-uniform chain is absent")
        constraint_scope = r6["constraint_scope"]
        if constraint_scope["Jordan_chain_lies_in_constraint_subspace"]:
            raise AssertionError("the 212-state Jordan lift constraint scope drifted")
        if not constraint_scope[
            "intrinsic_116_polynomial_chain_independently_certified"
        ]:
            raise AssertionError("the intrinsic pencil chain is not independently bound")
        if not retract["curved_deformation_retract"]:
            raise AssertionError("the required all-row curved retract is not certified")
        transformed_q = retract["factorized_actual_curved_Q"]["transformed_Q"]
        if "f_hat -> A_g f_hat^*" not in transformed_q["generalized_auxiliary"]:
            raise AssertionError("the required shifted auxiliary arrow is absent")
        if transformed_q["off_diagonal_blocks"] != "zero":
            raise AssertionError("the certified curved Q split is no longer direct")
        if not helicity["linearized_Weyl_symbol"]["is_isomorphism"]:
            raise AssertionError("the required helicity-two Weyl map is not certified")
        if helicity["linearized_Weyl_symbol"][
            "electric_TT_matrix_on_h22-h33_h23"
        ] != [["-1/2", "0"], ["0", "-1/2"]]:
            raise AssertionError("the physical h23 Weyl image drifted")

        system = _ordinary_system()
        substitution = dict(
            zip(system.covector, ALIGNED_COVECTOR, strict=True)
        )
        full_q = (
            system.field_fibre_pairing.inv()
            * system.gauge_invariant_flat_hessian
        ).subs(substitution)
        gauge = system.gauge_map.subs(substitution)
        companion = system.gauge_condition.subs(substitution)

        # The homogeneous order-two BV field symbol is kept separate from
        # the full Fourier differential.  Lower-order auxiliary mass terms
        # are homologically decisive and must not be discarded.
        zeta, hessian, _ = load_coefficient_cache(DEFAULT_CACHE)
        scale = sp.Symbol("jordan_homology_scale")
        principal_hessian = hessian.applyfunc(
            lambda value: sp.expand(
                value.subs({entry: scale * entry for entry in zeta})
            ).coeff(scale, 2)
        )
        principal_q = (
            system.field_fibre_pairing.inv()
            * principal_hessian.subs(
                dict(zip(zeta, ALIGNED_COVECTOR, strict=True))
            )
        )

        mass = system.gauge_invariant_flat_hessian[10:20, 10:20]
        shift = sp.eye(FIELD_RANK)
        shift[10:20, 0:10] = (
            -mass.inv() * system.gauge_invariant_flat_hessian[10:20, 0:10]
        )
        shift[10:20, 20:24] = (
            -mass.inv() * system.gauge_invariant_flat_hessian[10:20, 20:24]
        )
        shift = shift.subs(substitution)

        a0 = sp.zeros(FIELD_RANK, 1)
        a0[F23] = 2
        a1 = sp.zeros(FIELD_RANK, 1)
        a1[H23] = 1

        # A 48-coordinate M_aux direct-sum Ebar_aux subcomplex is sufficient
        # to display the existing contractible helicity component.  The
        # paired equation coordinate is Ebar_h23 (index 8), not Ebar_f23:
        # the action fibre form exchanges the tensor rows.
        q_pair = sp.zeros(2 * FIELD_RANK)
        q_pair[FIELD_RANK:, :FIELD_RANK] = full_q
        homotopy = sp.zeros(2 * FIELD_RANK)
        homotopy[F23, FIELD_RANK + H23] = 1
        projector = sp.zeros(2 * FIELD_RANK)
        projector[F23, F23] = 1
        projector[FIELD_RANK + H23, FIELD_RANK + H23] = 1

        tensor_rotation = _tensor_representation(_rotation_generators()[1])
        h_a = sp.zeros(10, 1)
        h_a[7], h_a[9] = 1, -1
        h_b = sp.zeros(10, 1)
        h_b[8] = 1
        # The same tensor representation acts on h and f.  In the real
        # bases (22-33,23) this is two copies of helicity two.
        if tensor_rotation * h_a != -2 * h_b:
            raise AssertionError("transverse tensor rotation drifted")
        if tensor_rotation * h_b != 2 * h_a:
            raise AssertionError("transverse tensor rotation drifted")
        little = sp.diag(
            sp.Matrix([[0, 2], [-2, 0]]),
            sp.Matrix([[0, 2], [-2, 0]]),
        )

        result = ExpandedRelativeJordanHomology(
            full_bv_field_differential=full_q,
            principal_bv_field_symbol=principal_q,
            gauge_symbol=gauge,
            companion_symbol=companion,
            field_shift_new_to_old=shift,
            field_shift_old_to_new=shift.inv(),
            a0=a0,
            a1=a1,
            q_a0=full_q * a0,
            q_a1=full_q * a1,
            principal_q_a0=principal_q * a0,
            principal_q_a1=principal_q * a1,
            q_pair=q_pair,
            pair_homotopy=homotopy,
            pair_projector=projector,
            little_group_on_hf=little,
            source_hashes=tuple(
                (path.name, _file_digest(path))
                for path in (
                    R6_NO_GO_CERTIFICATE,
                    RETRACT_CERTIFICATE,
                    HELICITY_CERTIFICATE,
                )
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        e_hstar = sp.zeros(FIELD_RANK, 1)
        e_hstar[H23] = -2
        e_fstar = sp.zeros(FIELD_RANK, 1)
        e_fstar[F23] = 4
        if self.q_a0 != e_hstar:
            raise AssertionError("full BV image of 2 f23 drifted")
        if self.q_a1 != sp.zeros(FIELD_RANK, 1):
            raise AssertionError("aligned full BV image of h23 drifted")
        if self.principal_q_a0 != sp.zeros(FIELD_RANK, 1):
            raise AssertionError("principal BV image of 2 f23 drifted")
        if self.principal_q_a1 != e_fstar:
            raise AssertionError("principal BV image of h23 drifted")

        # Neither amplitude is a gauge-symbol image.  Only a1 is a full
        # aligned BV cocycle; a0 is killed by the lower-order mass arrow.
        gauge_rank = self.gauge_symbol.rank()
        if self.gauge_symbol.row_join(self.a0).rank() != gauge_rank + 1:
            raise AssertionError("f23 unexpectedly became a gauge direction")
        if self.gauge_symbol.row_join(self.a1).rank() != gauge_rank + 1:
            raise AssertionError("h23 unexpectedly became a gauge direction")
        if self.companion_symbol[:, H23] != sp.zeros(GHOST_RANK, 1):
            raise AssertionError("the contractible equation partner is not Q-closed")

        # At the aligned characteristic root the differential shift fixes
        # both sparse amplitudes: h23 stays in the retained metric block and
        # f23 is exactly f_hat23 in the generalized-auxiliary block.
        if self.field_shift_old_to_new * self.a0 != self.a0:
            raise AssertionError("2 f23 is not the shifted auxiliary amplitude")
        if self.field_shift_old_to_new * self.a1 != self.a1:
            raise AssertionError("h23 did not remain in the metric block")

        if (
            self.q_pair * self.pair_homotopy
            + self.pair_homotopy * self.q_pair
            != -self.pair_projector
        ):
            raise AssertionError("the f23/Ebar_h23 pair did not contract")
        if self.q_pair * self.q_pair != sp.zeros(2 * FIELD_RANK):
            raise AssertionError("the displayed two-row BV restriction is not nilpotent")
        if self.little_group_on_hf != sp.diag(
            sp.Matrix([[0, 2], [-2, 0]]),
            sp.Matrix([[0, 2], [-2, 0]]),
        ):
            raise AssertionError("helicity-two representation split drifted")
        if self.little_group_on_hf**2 != -4 * sp.eye(4):
            raise AssertionError("little-group weights are not two helicity-two copies")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-jordan-homology-v1",
            "scope": {
                "relative_branch": "fixed-temporal pair-(1,6)",
                "scalar_branch": "BV-cyclic D_alt=-2 Pi_(h00,f00,v0)",
                "aligned_covector": list(ALIGNED_COVECTOR),
                "classification_level": (
                    "exact flat Fourier anchor plus the certified global "
                    "support-local curved BV split"
                ),
                "polynomial_Q_is_not_BV_Q": True,
            },
            "component_ledger": {
                "M_aux_order": ["h[10]", "f[10]", "v[4]"],
                "symmetric_tensor_order": [
                    list(component) for component in SYMMETRIC_COORDINATES
                ],
                "a0": {
                    "formula": "2 f_23",
                    "M_aux_index": F23,
                    "BV_degree": 0,
                    "shifted_block": "f_hat[10] generalized auxiliary",
                },
                "a1": {
                    "formula": "h_23",
                    "M_aux_index": H23,
                    "BV_degree": 0,
                    "shifted_block": "h[10] retained metric",
                },
                "equation_partner_of_a0": {
                    "formula": "Ebar_h23",
                    "Ebar_aux_index": H23,
                    "BV_degree": 1,
                    "reason": "the action fibre pairing exchanges the tensor rows",
                },
            },
            "BV_differential_at_aligned_anchor": {
                "full_QBV_a0": _nonzero(self.q_a0),
                "full_QBV_a1": _nonzero(self.q_a1),
                "principal_QBV_a0": _nonzero(self.principal_q_a0),
                "principal_QBV_a1": _nonzero(self.principal_q_a1),
                "identities": [
                    "Q_BV(2 f23)=-2 Ebar_h23",
                    "Q_BV(h23)=0",
                    "sigma_2(Q_BV)(2 f23)=0",
                    "sigma_2(Q_BV)(h23)=4 Ebar_f23",
                    "Q_BV(Ebar_h23)=0",
                ],
                "a0_is_BV_cocycle": False,
                "a1_is_aligned_BV_cocycle": True,
                "a0_is_gauge_symbol": False,
                "a1_is_gauge_symbol": False,
                "full_field_differential_sha256": _digest(
                    self.full_bv_field_differential
                ),
                "principal_field_symbol_sha256": _digest(
                    self.principal_bv_field_symbol
                ),
            },
            "existing_contractible_pair": {
                "arrow": "f_hat23 -> -Ebar_h23",
                "homotopy": "k(Ebar_h23)=f_hat23",
                "identity": "Qk+kQ=-Pi_(f_hat23,Ebar_h23)",
                "identity_defect": 0,
                "a0_projection_to_metric_core": 0,
                "a1_projection_to_metric_core": "h23",
                "a0_is_in_Q_contractible_summand": True,
                "a1_is_in_Q_contractible_summand": False,
                "additional_acyclic_pair_required_for_homological_split": False,
            },
            "curvature_and_constraints": {
                "a0_is_curvature_mapping_cone_coordinate": False,
                "a1_is_curvature_mapping_cone_coordinate": False,
                "curvature_graph_lift_of_a0": "zero (T_state depends on retained h)",
                "curvature_graph_lift_of_a1": "Psi=sigma(C1)h23, nonzero",
                "linearized_Weyl_target": "physical helicity (+2) plus (-2)",
                "Weyl_symbol_on_a1_nonzero": True,
                "Weyl_symbol_on_a0": 0,
                "standard_212_Jordan_lift_satisfies_gradient_constraints": False,
                "intrinsic_116_polynomial_chain_independent_of_that_lift": True,
            },
            "representation_and_extension": {
                "real_helicity_basis": [
                    "h22-h33",
                    "h23",
                    "f22-f33",
                    "f23",
                ],
                "little_group_generator": [
                    [int(value) for value in row]
                    for row in self.little_group_on_hf.tolist()
                ],
                "generator_square": "-4 I4",
                "bundle_representation": "H_(+-2) direct-sum H_(+-2)",
                "splits_as_SO2_bundle_representation": True,
                "splits_as_fixed_witness_pencil_module": False,
                "splits_as_QBV_complex_after_existing_local_shift": True,
                "Jordan_extension_survives_Q_cohomology": False,
                "cohomology_contribution": (
                    "a0 contributes zero; the retained a1 channel maps to the "
                    "physical Weyl helicity-two quotient"
                ),
                "extension_type": (
                    "off-shell triangular coupling between an existing "
                    "contractible auxiliary pair and the retained physical metric block"
                ),
            },
            "architectural_consequence": {
                "Jordan_block_entirely_contractible": False,
                "Jordan_block_touches_physical_curvature_through_a1": True,
                "Jordan_eigenvector_is_contractible": True,
                "candidate_next_route": (
                    "a block-triangular Green construction may contract the f_hat "
                    "pair and propagate the retained curvature block separately"
                ),
                "triangular_Green_inverse_constructed_here": False,
                "changing_temporal_incidence_still_available": True,
            },
            "source_certificate_sha256": dict(self.source_hashes),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "causal_quasi_isomorphism": False,
            "status_flags_promoted": [],
            "warranted_atomic_flags": [],
            "fail_closed": True,
        }
