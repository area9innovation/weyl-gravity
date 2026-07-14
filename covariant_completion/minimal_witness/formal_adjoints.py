"""Formal adjoints of the completed third-order companion.

All identities are on compactly supported spacetime sections, so boundary
terms vanish.  The convention is

``<h,K xi> = <-2 delta h,xi>``

for trace-free symmetric ``h``.  Hence ``delta^sharp=-K/2``.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


FormalTerms = dict[tuple[str, ...], Fraction]


def _formal_adjoint(terms: FormalTerms) -> FormalTerms:
    basic = {
        "delta": ("K", Fraction(-1, 2)),
        "div": ("d", Fraction(-1)),
        "d": ("div", Fraction(-1)),
        "BoxV": ("BoxV", Fraction(1)),
        "R": ("R", Fraction(1)),
        "Ric": ("Ric", Fraction(1)),
        "RicPair": ("RicTF", Fraction(1)),
    }
    output: FormalTerms = {}
    for word, coefficient in terms.items():
        adjoint_word: list[str] = []
        adjoint_coefficient = coefficient
        for operator in reversed(word):
            name, factor = basic[operator]
            adjoint_word.append(name)
            adjoint_coefficient *= factor
        key = tuple(adjoint_word)
        output[key] = output.get(key, Fraction(0)) + adjoint_coefficient
    return {word: value for word, value in output.items() if value}


@dataclass(frozen=True)
class CompanionFormalAdjoint:
    companion: str = (
        "Box delta-(1/3)d delta^2+(R/3)delta-Ric o delta"
        "+(1/3)d<Ric,h>"
    )
    adjoint: str = (
        "-(1/2)K Box+(1/6)K d div-(R/6)K"
        "+(1/2)K Ric-(1/3)Ric_TF div"
    )

    def verify(self) -> None:
        source: FormalTerms = {
            ("BoxV", "delta"): Fraction(1),
            ("d", "div", "delta"): Fraction(-1, 3),
            ("R", "delta"): Fraction(1, 3),
            ("Ric", "delta"): Fraction(-1),
            ("d", "RicPair"): Fraction(1, 3),
        }
        expected: FormalTerms = {
            ("K", "BoxV"): Fraction(-1, 2),
            ("K", "d", "div"): Fraction(1, 6),
            ("K", "R"): Fraction(-1, 6),
            ("K", "Ric"): Fraction(1, 2),
            ("RicTF", "div"): Fraction(-1, 3),
        }
        if _formal_adjoint(source) != expected:
            raise AssertionError("the companion formal adjoint was not derived exactly")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-companion-formal-adjoint-v1",
            "support_category": "compactly supported smooth cylinder sections",
            "pairing_convention": "<h,K xi>=<-2 delta h,xi>",
            "basic_adjoints": {
                "delta_sharp": "-K/2",
                "d_sharp": "-div",
                "Box_sharp": "Box",
                "Ric_sharp": "Ric",
                "Ric_parallel": True,
            },
            "T": self.companion,
            "Tsharp": self.adjoint,
            "machine_derivation": {
                "term_count": 5,
                "composition_order_reversed": True,
                "rational_coefficients_exact": True,
                "derived_terms_match_displayed_Tsharp": True,
            },
            "consequences": [
                "(TK)sharp=Ksharp Tsharp",
                "(B+(1/2)KT)sharp=B+(1/2)Tsharp Ksharp",
            ],
            "boundary_terms": "zero by compact spacetime support",
        }
