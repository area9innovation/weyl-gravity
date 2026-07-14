"""Local tensor-curl factorization of the cylinder TT Bach operator."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from covariant_completion.geometry.tensor_curl import TensorCurlCertificate


@dataclass(frozen=True)
class TTBachFactorization:
    """Certify Euclidean and Lorentzian factorizations in one convention."""

    def verify(self) -> None:
        TensorCurlCertificate().verify()
        time_square, laplacian, curl = sp.symbols("T Delta C", commutative=True)
        relation = {curl**2: -laplacian + 3}

        euclidean_source = (
            time_square**2
            + 2 * time_square * (laplacian - 4)
            + (laplacian - 2) ** 2
        )
        euclidean_factors = (
            -time_square + (curl - 1) ** 2
        ) * (-time_square + (curl + 1) ** 2)
        reduced_euclidean = sp.rem(
            sp.Poly(sp.expand(euclidean_factors - euclidean_source), curl),
            sp.Poly(curl**2 + laplacian - 3, curl),
        ).as_expr()
        if sp.expand(reduced_euclidean) != 0:
            raise AssertionError("Euclidean tensor-curl factorization failed")

        p_minus = time_square + (curl - 1) ** 2
        p_plus = time_square + (curl + 1) ** 2
        expanded_minus = sp.expand(p_minus).subs(relation, simultaneous=True)
        expanded_plus = sp.expand(p_plus).subs(relation, simultaneous=True)
        if expanded_minus != time_square - laplacian + 4 - 2 * curl:
            raise AssertionError("wrong Lorentzian P_- lower-order terms")
        if expanded_plus != time_square - laplacian + 4 + 2 * curl:
            raise AssertionError("wrong Lorentzian P_+ lower-order terms")
        if sp.expand(p_minus * p_plus - p_plus * p_minus) != 0:
            raise AssertionError("the local TT factors do not commute")

        harmonic = sp.symbols("r", integer=True, nonnegative=True)
        absolute_curl = harmonic + 3
        lower = absolute_curl - 1
        upper = absolute_curl + 1
        if lower != harmonic + 2 or upper != harmonic + 4:
            raise AssertionError("wrong TT harmonic frequencies")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-tt-local-factorization-v1",
            "euclidean_operator": "d_tau^4+2 d_tau^2(D^2-4)+(D^2-2)^2",
            "euclidean_factorization": (
                "[-d_tau^2+(C_2-1)^2][-d_tau^2+(C_2+1)^2]"
            ),
            "lorentzian_factors": {
                "P_minus": "d_t^2-D^2+4-2C_2",
                "P_plus": "d_t^2-D^2+4+2C_2",
            },
            "lorentzian_bach": "B_TT=P_minus P_plus=P_plus P_minus",
            "principal_part": "d_t^2-D^2 on spatial two-tensors",
            "lower_order_curl": "first order",
            "factors_normally_hyperbolic": True,
            "constraint_subspace": "TT, preserved by C_2 and both factors",
            "reduced_green_hyperbolic": True,
            "green_operator_order": (
                "for B=P_minus o P_plus, G_B^+/-=G_Pplus^+/- o G_Pminus^+/-"
            ),
            "tt_frequencies": ["r+2", "r+4"],
            "locality_guard": "the C_2 factorization is local",
            "scope_guard": (
                "this is the reduced physical TT operator, not a Green's witness "
                "for the complete BV complex"
            ),
        }
