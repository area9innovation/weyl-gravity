"""Exact nonlocal E/L extraction from fourth-order TT solutions."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class TTBranchProjectors:
    def verify(self) -> None:
        time_square, absolute_curl = sp.symbols("T A", commutative=True)
        if not absolute_curl.is_commutative:
            raise AssertionError("spectral operators must commute in this certificate")
        energy_e = absolute_curl - 1
        energy_l = absolute_curl + 1
        gap = sp.expand(energy_l**2 - energy_e**2)
        if gap != 4 * absolute_curl:
            raise AssertionError("TT branch gap is not 4|C_2|")
        p_e = (time_square + energy_l**2) / gap
        p_l = -(time_square + energy_e**2) / gap
        bach = (time_square + energy_e**2) * (time_square + energy_l**2)
        if sp.simplify(p_e + p_l - 1) != 0:
            raise AssertionError("E/L projectors do not sum to one")
        if sp.simplify(p_e**2 - p_e - bach / gap**2) != 0:
            raise AssertionError("E projector is not idempotent modulo Bach")
        if sp.simplify(p_l**2 - p_l - bach / gap**2) != 0:
            raise AssertionError("L projector is not idempotent modulo Bach")
        if sp.simplify(p_e * p_l + bach / gap**2) != 0:
            raise AssertionError("E/L projectors are not orthogonal modulo Bach")
        if sp.simplify((time_square + energy_e**2) * p_e - bach / gap) != 0:
            raise AssertionError("E branch equation failed modulo Bach")
        if sp.simplify((time_square + energy_l**2) * p_l + bach / gap) != 0:
            raise AssertionError("L branch equation failed modulo Bach")

        harmonic = sp.symbols("r", integer=True, nonnegative=True)
        if sp.simplify(gap.subs(absolute_curl, harmonic + 3)) != 4 * (harmonic + 3):
            raise AssertionError("harmonic branch gap failed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-tt-branch-projectors-v1",
            "absolute_curl": "|C_2|=(C_2^2)^(1/2)",
            "helicity_projectors": "Pi_+/-=(1+/-C_2|C_2|^-1)/2",
            "energy_operators": {
                "A_E": "|C_2|-1",
                "A_L": "|C_2|+1",
            },
            "spectra": {"A_E": "2,3,4,...", "A_L": "4,5,6,..."},
            "gap": "A_L^2-A_E^2=4|C_2|>=12",
            "solution_extraction": {
                "h_E": "(4|C_2|)^-1(d_t^2+A_L^2)h",
                "h_L": "-(4|C_2|)^-1(d_t^2+A_E^2)h",
            },
            "sum": "h=h_E+h_L",
            "projector_identities": "exact modulo B_TT",
            "local": False,
            "causal_support_claim": False,
        }
