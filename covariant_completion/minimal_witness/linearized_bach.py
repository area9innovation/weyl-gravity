"""Action-normalized linearized Bach operator from the Weyl tensor.

The background Weyl tensor vanishes, so connection variations do not enter
the two divergences in

``B_std(h)_ab = nabla^c nabla^d C_1(h)_{acbd}``
``              +(1/2) Ric^{cd} C_1(h)_{acbd}``.

The remaining overall sign/scale is fixed against the independently derived
flat action symbol rather than against a selected physical mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from .cylinder_jets import CylinderJetGeometry, Jet, _sum, _zero


def _rank(shape: tuple[int, ...]):
    if len(shape) == 1:
        return [_zero() for _ in range(shape[0])]
    return [_rank(shape[1:]) for _ in range(shape[0])]


@dataclass(frozen=True)
class LinearizedBach:
    geometry: CylinderJetGeometry
    riemann_mixed: tuple
    schouten: tuple

    @staticmethod
    def build() -> "LinearizedBach":
        geometry = CylinderJetGeometry.build()
        gamma = geometry.christoffel
        riemann = _rank((4, 4, 4, 4))
        for rho in range(4):
            for sigma in range(4):
                for mu in range(4):
                    for nu in range(4):
                        riemann[rho][sigma][mu][nu] = (
                            gamma[rho][nu][sigma].derivative(mu)
                            - gamma[rho][mu][sigma].derivative(nu)
                            + _sum(
                                gamma[rho][mu][middle]
                                * gamma[middle][nu][sigma]
                                - gamma[rho][nu][middle]
                                * gamma[middle][mu][sigma]
                                for middle in range(4)
                            )
                        )
        schouten = tuple(
            tuple(
                Fraction(1, 2)
                * (geometry.ricci[mu][nu] - geometry.metric[mu][nu])
                for nu in range(4)
            )
            for mu in range(4)
        )
        return LinearizedBach(
            geometry=geometry,
            riemann_mixed=tuple(
                tuple(tuple(tuple(row) for row in plane) for plane in block)
                for block in riemann
            ),
            schouten=schouten,
        )

    def connection_variation(self, tensor):
        derivative = self.geometry.covariant_derivative_symmetric(tensor)
        output = _rank((4, 4, 4))
        for rho in range(4):
            for mu in range(4):
                for nu in range(4):
                    output[rho][mu][nu] = Fraction(1, 2) * _sum(
                        self.geometry.inverse_metric[rho][contracted]
                        * (
                            derivative[mu][nu][contracted]
                            + derivative[nu][mu][contracted]
                            - derivative[contracted][mu][nu]
                        )
                        for contracted in range(4)
                    )
        return output

    def covariant_derivative_connection_variation(self, variation):
        gamma = self.geometry.christoffel
        output = _rank((4, 4, 4, 4))
        for axis in range(4):
            for rho in range(4):
                for mu in range(4):
                    for nu in range(4):
                        output[axis][rho][mu][nu] = (
                            variation[rho][mu][nu].derivative(axis)
                            + _sum(
                                gamma[rho][axis][contracted]
                                * variation[contracted][mu][nu]
                                - gamma[contracted][axis][mu]
                                * variation[rho][contracted][nu]
                                - gamma[contracted][axis][nu]
                                * variation[rho][mu][contracted]
                                for contracted in range(4)
                            )
                        )
        return output

    def linearized_weyl(self, tensor):
        geometry = self.geometry
        connection_variation = self.connection_variation(tensor)
        derivative = self.covariant_derivative_connection_variation(
            connection_variation
        )

        riemann_mixed_one = _rank((4, 4, 4, 4))
        for rho in range(4):
            for sigma in range(4):
                for mu in range(4):
                    for nu in range(4):
                        riemann_mixed_one[rho][sigma][mu][nu] = (
                            derivative[mu][rho][nu][sigma]
                            - derivative[nu][rho][mu][sigma]
                        )

        riemann_lower_one = _rank((4, 4, 4, 4))
        for alpha in range(4):
            for sigma in range(4):
                for mu in range(4):
                    for nu in range(4):
                        riemann_lower_one[alpha][sigma][mu][nu] = _sum(
                            tensor[alpha][rho]
                            * self.riemann_mixed[rho][sigma][mu][nu]
                            + geometry.metric[alpha][rho]
                            * riemann_mixed_one[rho][sigma][mu][nu]
                            for rho in range(4)
                        )

        ricci_one = _rank((4, 4))
        for sigma in range(4):
            for nu in range(4):
                ricci_one[sigma][nu] = _sum(
                    riemann_mixed_one[rho][sigma][rho][nu]
                    for rho in range(4)
                )

        raised_tensor_ricci = _sum(
            geometry.inverse_metric[mu][left]
            * geometry.inverse_metric[nu][right]
            * tensor[left][right]
            * geometry.ricci[mu][nu]
            for mu in range(4)
            for nu in range(4)
            for left in range(4)
            for right in range(4)
        )
        scalar_one = (
            -raised_tensor_ricci
            + _sum(
                geometry.inverse_metric[mu][nu] * ricci_one[mu][nu]
                for mu in range(4)
                for nu in range(4)
            )
        )
        schouten_one = _rank((4, 4))
        for mu in range(4):
            for nu in range(4):
                schouten_one[mu][nu] = Fraction(1, 2) * (
                    ricci_one[mu][nu]
                    - Fraction(1, 6)
                    * (
                        scalar_one * geometry.metric[mu][nu]
                        + 6 * tensor[mu][nu]
                    )
                )

        weyl = _rank((4, 4, 4, 4))
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        variation_g_schouten = (
                            tensor[a][c] * self.schouten[d][b]
                            + geometry.metric[a][c] * schouten_one[d][b]
                            - tensor[a][d] * self.schouten[c][b]
                            - geometry.metric[a][d] * schouten_one[c][b]
                            - tensor[b][c] * self.schouten[d][a]
                            - geometry.metric[b][c] * schouten_one[d][a]
                            + tensor[b][d] * self.schouten[c][a]
                            + geometry.metric[b][d] * schouten_one[c][a]
                        )
                        weyl[a][b][c][d] = (
                            riemann_lower_one[a][b][c][d]
                            - variation_g_schouten
                        )
        return weyl

    def covariant_derivative_rank4(self, tensor):
        gamma = self.geometry.christoffel
        output = _rank((4, 4, 4, 4, 4))
        for axis in range(4):
            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        for d in range(4):
                            output[axis][a][b][c][d] = (
                                tensor[a][b][c][d].derivative(axis)
                                - _sum(
                                    gamma[contracted][axis][a]
                                    * tensor[contracted][b][c][d]
                                    + gamma[contracted][axis][b]
                                    * tensor[a][contracted][c][d]
                                    + gamma[contracted][axis][c]
                                    * tensor[a][b][contracted][d]
                                    + gamma[contracted][axis][d]
                                    * tensor[a][b][c][contracted]
                                    for contracted in range(4)
                                )
                            )
        return output

    def covariant_derivative_rank3(self, tensor):
        gamma = self.geometry.christoffel
        output = _rank((4, 4, 4, 4))
        for axis in range(4):
            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        output[axis][a][b][c] = (
                            tensor[a][b][c].derivative(axis)
                            - _sum(
                                gamma[contracted][axis][a]
                                * tensor[contracted][b][c]
                                + gamma[contracted][axis][b]
                                * tensor[a][contracted][c]
                                + gamma[contracted][axis][c]
                                * tensor[a][b][contracted]
                                for contracted in range(4)
                            )
                        )
        return output

    def standard_bach_from_weyl(self, weyl):
        """Apply the standard curvature-to-Bach operator to an algebraic Weyl field.

        This is the reusable ``D(U)`` map

        ``nabla^c nabla^d U_acbd + (1/2) Ric^cd U_acbd``.

        ``standard_bach`` below supplies ``U=C_1 h``.  Keeping the curvature
        input entry point explicit lets the curvature-prolongation work derive
        its electric/magnetic equations without reconstructing a metric
        potential or using a nonlocal inverse of ``C_1``.
        """

        geometry = self.geometry
        derivative = self.covariant_derivative_rank4(weyl)
        first_divergence = _rank((4, 4, 4))
        for a in range(4):
            for c in range(4):
                for b in range(4):
                    first_divergence[a][c][b] = _sum(
                        geometry.inverse_metric[d][axis]
                        * derivative[axis][a][c][b][d]
                        for d in range(4)
                        for axis in range(4)
                    )
        second_derivative = self.covariant_derivative_rank3(first_divergence)
        output = _rank((4, 4))
        for a in range(4):
            for b in range(4):
                double_divergence = _sum(
                    geometry.inverse_metric[c][axis]
                    * second_derivative[axis][a][c][b]
                    for c in range(4)
                    for axis in range(4)
                )
                ricci_term = Fraction(1, 2) * _sum(
                    geometry.ricci_up[c][d] * weyl[a][c][b][d]
                    for c in range(4)
                    for d in range(4)
                )
                output[a][b] = double_divergence + ricci_term
        return geometry.tracefree_projection(output)

    def standard_bach(self, tensor):
        return self.standard_bach_from_weyl(self.linearized_weyl(tensor))

    def action_normalized_bach(self, tensor):
        # Fixed by ``verify_normalization`` below.
        return [
            [-2 * value for value in row]
            for row in self.standard_bach(tensor)
        ]

    def verify_background_curvature(self) -> None:
        for sigma in range(4):
            for nu in range(4):
                computed = _sum(
                    self.riemann_mixed[rho][sigma][rho][nu]
                    for rho in range(4)
                ).value
                expected = self.geometry.ricci[sigma][nu].value
                if sp.simplify(computed - expected) != 0:
                    raise AssertionError(
                        f"background Ricci mismatch at {sigma,nu}: {computed-expected}"
                    )

    def verify_normalization(self) -> None:
        """Compare the fourth-derivative part with the action symbol."""

        from .field_biwave import GaugeFixedMetricBiwave

        fields = GaugeFixedMetricBiwave(self.geometry)
        # Degree-four monomials kill every lower-order curvature contribution
        # at the base point.  Testing the complete fibre and all degree-four
        # multiindices therefore compares the full principal symbol.
        nonzero = 0
        for component in range(9):
            for multiindex in self.geometry.exhaustive_multiindices(4):
                if sum(multiindex) != 4:
                    continue
                tensor = fields.tracefree_section(component, multiindex)
                standard = self.standard_bach(tensor)
                wave = self.geometry.rough_wave_symmetric(tensor)
                wave_squared = self.geometry.rough_wave_symmetric(wave)
                principal_companion = self.geometry.companion_terms(tensor)[0]
                k_companion = self.geometry.conformal_killing(principal_companion)
                for mu in range(4):
                    for nu in range(4):
                        expected = Fraction(1, 2) * (
                            wave_squared[mu][nu].value
                            - k_companion[mu][nu].value
                        )
                        actual = -2 * standard[mu][nu].value
                        if sp.simplify(actual - expected) != 0:
                            raise AssertionError(
                                "standard Bach normalization mismatch on principal "
                                f"jet {component,multiindex,mu,nu}: {actual-expected}"
                            )
                        if sp.simplify(actual) != 0:
                            nonzero += 1
        if nonzero == 0:
            raise AssertionError("linearized Bach principal symbol vanished identically")

    def verify_weyl_gauge_invariance(self) -> None:
        """Certify ``C_1 K=0`` on every local third jet.

        The composition has differential order three.  Exhausting all such
        jets at one point therefore proves the natural operator identity on
        the homogeneous cylinder and implies ``B K=0`` without an expensive
        fifth-jet recomputation of the two Weyl divergences.
        """

        geometry = self.geometry
        for component in range(4):
            for multiindex in geometry.exhaustive_multiindices(3):
                covector = geometry.zero_covector()
                covector[component] = Jet.monomial(multiindex)
                weyl = self.linearized_weyl(
                    geometry.conformal_killing(covector)
                )
                for a in range(4):
                    for b in range(4):
                        for c in range(4):
                            for d in range(4):
                                if sp.simplify(weyl[a][b][c][d].value) != 0:
                                    raise AssertionError(
                                        "C_1 K !=0 on exhaustive local third jets: "
                                        f"input={component,multiindex}, "
                                        f"output={a,b,c,d}"
                                    )

    def verify(self) -> None:
        self.verify_background_curvature()
        self.verify_normalization()
        self.verify_weyl_gauge_invariance()

    def certificate(self, *, verify: bool = True) -> dict[str, object]:
        if verify:
            self.verify()
        return {
            "schema": "pure-weyl-linearized-bach-cylinder-v1",
            "category": "natural local operators on the conformal cylinder",
            "construction": (
                "B_lin=-2[nabla^c nabla^d C_1(acbd)"
                "+(1/2)Ric^{cd}C_1(acbd)]"
            ),
            "normalization": (
                "-2 times the displayed standard Bach convention, fixed on "
                "every trace-free fourth principal jet against the repository "
                "action Hessian"
            ),
            "factorization_input": "B_lin=C_1^sharp C_1",
            "gauge_identity": "C_1 K=0 and hence B_lin K=0",
            "gauge_jet_test": {
                "maximum_order": 3,
                "input_components": 4,
                "multiindices_per_component": len(
                    self.geometry.exhaustive_multiindices(3)
                ),
                "exhaustive": True,
            },
            "principal_jet_test": {
                "maximum_order": 4,
                "tracefree_input_components": 9,
                "homogeneous_multiindices": 35,
                "exhaustive": True,
            },
            "formal_self_adjointness": (
                "follows from the C_1^sharp C_1 action construction"
            ),
            "globalization": {
                "equivariance": "R x SO(4)",
                "parallel_background_curvature": True,
                "jet_basis_spans_every_component": True,
                "isotropy_covariance_exhausted": True,
                "homogeneous_operator_coefficients": True,
                "argument": (
                    "the natural operator differences have the certified finite "
                    "differential orders; vanishing on every fibre component and "
                    "every jet through those orders at one homogeneous base point "
                    "therefore gives the global cylinder identities"
                ),
            },
        }
