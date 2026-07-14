"""Action/current theorem for the support-local Weyl--Cotton graph extension.

This module isolates the part of the prolonged-current comparison which is
already determined by the BV-canonical graph extension

``Psi_hat = Psi-C1 h`` and ``c_hat = c-div(Psi)``.

Let ``R(h,Psi,c)=(Psi-C1 h,c-div(Psi))``.  With any fixed nondegenerate
pointwise forms on the Weyl and Cotton bundles, the local quadratic parent

``L_parent=L_aux+1/2 <R phi,R phi>``

has graph Hessian ``R^sharp R``.  Its derivative-dependent boundary term is
the sum of the Green concomitants of ``C1`` and ``div``.  Both residuals and
their tangent variations vanish on the graph inclusion, so the added
presymplectic potential and current pull back to zero.  Thus the graph parent
agrees *exactly* with the auxiliary current (the compatible representatives
have ``beta=gamma=0``).

This result must not be confused with the current theorem for the complete
Bianchi--Bach resolution.  The latter still needs an all-row cyclic BV
operator or a local master action.  In particular, the positive symmetrizer
of the curvature evolution is an energy-estimate device, not the indefinite
action/BV current.
"""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from covariant_completion.curved_retract.curvature_prolongation_sdr import (
    CurvatureProlongationGraphSDR,
    Matrix,
    _add,
    _digest,
    _identity,
    _is_zero,
    _matrix_adjoint,
    _multiply,
    _scale,
    _zero,
)


@dataclass(frozen=True)
class CurvatureGraphCurrentComparison:
    """Exact quadratic parent and current pullback for the graph sector."""

    residual: Matrix
    graph_inclusion: Matrix
    graph_hessian: Matrix
    graph_sdr: CurvatureProlongationGraphSDR

    @staticmethod
    def build() -> "CurvatureGraphCurrentComparison":
        # Field order is (h,Psi,c); residual order is (Psi_hat,c_hat).
        residual = _zero(2, 3)
        residual[0][0] = OperatorPolynomial.atom("T", -1)
        residual[0][1] = OperatorPolynomial.identity()
        residual[1][1] = OperatorPolynomial.atom("D", -1)
        residual[1][2] = OperatorPolynomial.identity()

        # The graph is h |-> (h,C1 h,div C1 h).
        inclusion = _zero(3, 1)
        inclusion[0][0] = OperatorPolynomial.identity()
        inclusion[1][0] = OperatorPolynomial.atom("T")
        inclusion[2][0] = (
            OperatorPolynomial.atom("D") * OperatorPolynomial.atom("T")
        )

        hessian = _multiply(_matrix_adjoint(residual), residual)
        result = CurvatureGraphCurrentComparison(
            residual=residual,
            graph_inclusion=inclusion,
            graph_hessian=hessian,
            graph_sdr=CurvatureProlongationGraphSDR.build(),
        )
        result.verify(reverify_sdr=False)
        return result

    def verify(self, *, reverify_sdr: bool = True) -> None:
        if reverify_sdr:
            self.graph_sdr.verify()

        # R I=0 says both graph equations and their tangent variations vanish
        # on the inclusion.  It is the exact input to the potential pullback.
        if not _is_zero(_multiply(self.residual, self.graph_inclusion)):
            raise AssertionError("the Weyl/Cotton residual does not vanish on the graph")

        expected_hessian = _multiply(_matrix_adjoint(self.residual), self.residual)
        if self.graph_hessian != expected_hessian:
            raise AssertionError("the graph Hessian is not R^sharp R")
        adjoint_defect = _add(
            _matrix_adjoint(self.graph_hessian),
            _scale(self.graph_hessian, -1),
        )
        if not _is_zero(adjoint_defect):
            raise AssertionError("the graph parent Hessian is not formally self-adjoint")
        if not _is_zero(_multiply(self.graph_hessian, self.graph_inclusion)):
            raise AssertionError("the graph Hessian does not vanish on tangent graph data")

        # Tie the action calculation to the already-certified BV-canonical
        # cotangent lift rather than silently introducing a second shift.
        graph_certificate = self.graph_sdr.certificate(reverify=False)
        if graph_certificate["cotangent_lift"]["formal_BV_pairing_defect"] != 0:
            raise AssertionError("the graph variables are not the BV-canonical ones")
        if not graph_certificate["support_local_curvature_graph_retract"]:
            raise AssertionError("the graph inclusion is not support-local")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-curvature-graph-current-comparison-v1",
            "variables": {
                "fields": ["h", "Psi", "c"],
                "shifted_residuals": [
                    "Psi_hat=Psi-C1 h",
                    "c_hat=c-div Psi",
                ],
                "graph_inclusion": "h |-> (h,C1 h,div C1 h)",
                "cotangent_lift": "the exact type-II BV-canonical graph generator",
            },
            "local_quadratic_parent": {
                "formula": (
                    "L_parent=L_aux+1/2<Psi_hat,Psi_hat>_W+"
                    "1/2<c_hat,c_hat>_C"
                ),
                "bundle_forms": (
                    "fixed nondegenerate pointwise Weyl and Cotton forms; "
                    "identity in the formal normalization"
                ),
                "graph_Hessian": "R^sharp R",
                "graph_Hessian_formally_self_adjoint": True,
                "Euler_Lagrange_graph_block": (
                    "R^sharp R(h,Psi,c), equivalent after the triangular "
                    "graph shift to the two pointwise unit arrows"
                ),
            },
            "variational_boundary": {
                "green_concomitant_convention": (
                    "d J_A(u,v)=<u,A v>-<A^sharp u,v>"
                ),
                "theta_graph": (
                    "-J_C1(Psi_hat,delta h)-J_div(c_hat,delta Psi)"
                ),
                "delta_L_graph": (
                    "<Psi_hat,delta Psi-C1 delta h>+"
                    "<c_hat,delta c-div delta Psi>"
                ),
                "residual_pullback": "I^*(Psi_hat,c_hat)=(0,0)",
                "tangent_residual_pullback": (
                    "I^*(delta Psi_hat,delta c_hat)=(0,0)"
                ),
                "potential_pullback": "I^*theta_graph=0",
                "current_pullback": "I^*omega_graph=0",
            },
            "exact_identities": {
                "R_I": "zero",
                "Rsharp_R_I": "zero",
                "graph_Hessian_adjoint_defect": "zero",
                "I_pullback_theta_parent_minus_theta_aux": "zero",
                "I_pullback_omega_parent_minus_omega_aux": "zero",
                "improvement": "d beta+Q gamma with beta=0 and gamma=0",
            },
            "support": {
                "C1_order": 2,
                "div_order": 1,
                "finite_order_only": True,
                "pointwise_bundle_forms_only": True,
                "inverse_Laplacian": False,
                "inverse_curl": False,
                "spectral_projector": False,
                "Green_operator": False,
                "compact": True,
                "spacelike_compact": True,
                "smooth_global": True,
            },
            "matrix_sha256": {
                "residual_R": _digest(self.residual),
                "graph_inclusion": _digest(self.graph_inclusion),
                "graph_Hessian": _digest(self.graph_hessian),
            },
            "pairing_separation": {
                "positive_PDE_symmetrizer": (
                    "used only for symmetric-hyperbolic energy estimates and "
                    "finite propagation"
                ),
                "action_BV_Krein_current": (
                    "the indefinite cohomological pairing inherited from "
                    "L_aux and the local parent"
                ),
                "identified_with_each_other": False,
            },
            "curvature_graph_current_comparison": True,
            "prolonged_current_comparison": False,
            "flags_promoted_here": [],
            "action_level_blocker": {
                "missing": [
                    (
                        "a complete all-row Q_prol/master action containing the "
                        "derived Bianchi--Bach evolution, sourced constraints, "
                        "identity-antifields, and their antifield rows"
                    ),
                    (
                        "a cyclic BV pairing (or local quadratic parent) whose "
                        "Euler--Lagrange/Koszul--Tate rows are exactly that "
                        "curvature resolution"
                    ),
                    (
                        "formal-adjoint/cyclicity identities and the resulting "
                        "Green concomitant for every resolution row"
                    ),
                ],
                "why_the_PDE_symmetrizer_is_insufficient": (
                    "a positive symmetrizer proves well-posedness but neither "
                    "defines the BV presymplectic current nor supplies Q-cyclicity"
                ),
                "promotion_condition": (
                    "extend this exact graph parent to the complete all-row "
                    "curvature resolution and prove I^*omega_prol-omega_aux="
                    "d beta+Q gamma off shell"
                ),
            },
            "theorem_boundary": (
                "the local BV-canonical graph/generalized-auxiliary sector has "
                "an exact action and current pullback; the complete curvature "
                "resolution has no certified action-level cyclic realization yet"
            ),
            "fail_closed": True,
        }
