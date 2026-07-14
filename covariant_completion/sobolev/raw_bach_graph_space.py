"""Pullback graph space for raw fourth-order TT Cauchy data."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from covariant_completion.physical_operator.branch_projectors import TTBranchProjectors


@dataclass(frozen=True)
class RawBachGraphSpace:
    def verify(self) -> None:
        TTBranchProjectors().verify()
        absolute_curl = sp.symbols("A", positive=True)
        a_e = absolute_curl - 1
        a_l = absolute_curl + 1
        gap = 4 * absolute_curl
        h0, h1, h2, h3 = sp.symbols("h0 h1 h2 h3")
        q_e = (h2 + a_l**2 * h0) / gap
        p_e = (h3 + a_l**2 * h1) / gap
        q_l = -(h2 + a_e**2 * h0) / gap
        p_l = -(h3 + a_e**2 * h1) / gap
        if sp.simplify(q_e + q_l - h0) != 0:
            raise AssertionError("raw TT positions do not reconstruct h0")
        if sp.simplify(p_e + p_l - h1) != 0:
            raise AssertionError("raw TT velocities do not reconstruct h1")
        if sp.simplify(-a_e**2 * q_e - a_l**2 * q_l - h2) != 0:
            raise AssertionError("raw TT accelerations do not reconstruct h2")
        if sp.simplify(-a_e**2 * p_e - a_l**2 * p_l - h3) != 0:
            raise AssertionError("raw TT third derivatives do not reconstruct h3")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-raw-bach-graph-space-v1",
            "definition": "pullback of the E and L branch Sobolev norms",
            "branch_data": {
                "q_E": "(4|C_2|)^-1(h_2+A_L^2 h_0)",
                "p_E": "(4|C_2|)^-1(h_3+A_L^2 h_1)",
                "q_L": "-(4|C_2|)^-1(h_2+A_E^2 h_0)",
                "p_L": "-(4|C_2|)^-1(h_3+A_E^2 h_1)",
            },
            "inverse": {
                "h_0": "q_E+q_L",
                "h_1": "p_E+p_L",
                "h_2": "-A_E^2 q_E-A_L^2 q_L",
                "h_3": "-A_E^2 p_E-A_L^2 p_L",
            },
            "mixed_graph_regularity": True,
            "standard_product_sobolev_equivalence_proved": False,
        }
