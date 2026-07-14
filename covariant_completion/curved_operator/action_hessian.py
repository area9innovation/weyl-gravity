"""Action-derived factorization and gauge kernel of the curved Hessian.

Completing the nonlinear auxiliary square gives the exact local field change

``f_hat = f-S(h,v)``,  ``S=D[A_g^{-1}G^b]_(gbar,0)``.

The quadratic action is therefore the pullback of the action-normalized Bach
Hessian plus the pointwise auxiliary mass Hessian.  This module verifies the
decisive curved identity behind that pullback: ``f_hat`` is invariant under
the complete nine-component linearized gauge map.  The check is exhaustive
on every local third jet, not a Fourier or harmonic sample.

The module intentionally does not call this an expanded coefficient table;
the formal-adjoint pullback still has to be reduced to the canonical
covariant-derivative normal form before the four-row Q/W/P flag can close.
"""

from __future__ import annotations

from dataclasses import dataclass
import sympy as sp

from covariant_completion.curved_retract.tangent_shift import (
    CurvedAuxiliaryTangentShift,
)
from .conventions import CurvedBVConventions, _ordinary_system
from .eliminated_density import EliminatedVectorDensityIdentity


@dataclass(frozen=True)
class ActionDerivedAuxiliaryHessian:
    conventions: CurvedBVConventions
    shift: CurvedAuxiliaryTangentShift
    eliminated_density: EliminatedVectorDensityIdentity
    gauge_jet_vectors_tested: int

    @staticmethod
    def build(
        shift: CurvedAuxiliaryTangentShift | None = None,
    ) -> "ActionDerivedAuxiliaryHessian":
        # The retract/current aggregates already own this expensive exact jet
        # object.  Accepting it here keeps one source of coefficients while
        # avoiding a duplicate exhaustive gauge-jet expansion.
        if shift is None:
            shift = CurvedAuxiliaryTangentShift.build()
        result = ActionDerivedAuxiliaryHessian(
            conventions=CurvedBVConventions.build(),
            shift=shift,
            eliminated_density=EliminatedVectorDensityIdentity.build(),
            gauge_jet_vectors_tested=9
            * len(shift.geometry.exhaustive_multiindices(3)),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.conventions.verify()
        self.eliminated_density.verify()
        if self.shift.diffeomorphism_gauge_defect != sp.zeros(10, 4):
            raise AssertionError("diffeomorphism tangent-shift defect")
        if self.shift.conformal_boost_gauge_defect != sp.zeros(10, 4):
            raise AssertionError("conformal-boost tangent-shift defect")
        if self.shift.weyl_gauge_defect != sp.zeros(10, 1):
            raise AssertionError("Weyl tangent-shift defect")

        # The remaining diagonal blocks are independently exact: the mass
        # map is nondegenerate and B_lin K=0 was exhaustively proved by the
        # action-normalized linearized-Weyl construction.
        source_mass = _ordinary_system().auxiliary_mass_hessian
        if source_mass.rank() != 10:
            raise AssertionError("auxiliary mass Hessian normalization drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        jets_per_component = len(self.shift.geometry.exhaustive_multiindices(3))
        return {
            "schema": "pure-weyl-action-derived-curved-auxiliary-hessian-v1",
            "construction": (
                "E_aux,cyl=U_shift^sharp diag(B_lin,A_g,0) U_shift, "
                "U_shift(h,f,v)=(h,f-S(h,v),v)"
            ),
            "sources": {
                "nonlinear_square": "phi_hat=phi-A_g^{-1}G^b(g,b)",
                "tangent": "S=D[A_g^{-1}G^b]_(gbar,0)",
                "metric_block": "action-normalized LinearizedBach",
                "auxiliary_block": "A_g(phi)=-1/2(phi-g tr_g phi)",
                "vector_block": (
                    "zero modulo the certified eliminated-density boundary current"
                ),
            },
            "curved_gauge_invariance": {
                "identity": "S(K_h ghost,K_v ghost)=K_f ghost",
                "maximum_jet_order": 3,
                "ghost_components": 9,
                "jet_vectors_per_component": jets_per_component,
                "complete_jet_vectors_tested": self.gauge_jet_vectors_tested,
                "all_tensor_outputs_tested": 10,
                "defect": 0,
                "jet_basis_encoding": (
                    "generic exponential jet; coefficients of the covector "
                    "polynomial exhaust all symmetric partial jets"
                ),
                "includes_background_auxiliary_Lie_derivative": True,
                "not_a_harmonic_cutoff": True,
            },
            "consequence": "E_aux,cyl K_aux,cyl=0",
            "formal_self_adjoint_by_construction": True,
            "eliminated_vector_density_boundary_identity": True,
            "support_local": True,
            "expanded_canonical_derivative_table": (
                "certified separately by curved_auxiliary_hessian.json"
            ),
            "theorem_boundary": (
                "the exact action factorization, gauge kernel, and Hessian table are "
                "proved; the gauge-fixed wave completion has an exact null-rank "
                "obstruction and the exhaustive Q/W/P lower-jet ledger remains open"
            ),
        }
