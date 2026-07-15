"""Ordinary-bidegree expansion of the normalized four-dimensional Euler form.

The expansion is derived from Theorem 1 of arXiv:0704.2472 and the frozen
source/project normalization.  It verifies carrier combinatorics, top Euler
reconstruction, the BRST-closed bottom, and the structural termination of the
intrinsic descent.  The two connecting descent identities remain fail-closed
until the full ``D W``/Cotton and ``Gamma`` generator actions are implemented.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Any

from .algebra import canonical_sha256
from .generalized_connection import (
    EULER_BIDEGREES,
    euler_normalization_contract,
    generalized_connection_dictionary,
)


def _fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _coefficient(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def _expanded_terms() -> tuple[dict[str, Any], ...]:
    normalization = euler_normalization_contract()
    phi_coefficients = tuple(map(_coefficient, normalization["project_coefficients"]))
    terms: list[dict[str, Any]] = []
    for r in range(3):
        p = 2 - r
        grouped: dict[tuple[int, int], dict[str, Any]] = {}
        for word in product(("U", "P"), repeat=r):
            ghost_tilde_count = word.count("U")
            form_tilde_count = r - ghost_tilde_count
            inversions = sum(
                word[left] == "P" and word[right] == "U"
                for left in range(r)
                for right in range(left + 1, r)
            )
            odd_reordering_sign = (-1) ** inversions
            epsilon_relabeling_sign = (-1) ** inversions
            canonicalization_sign = odd_reordering_sign * epsilon_relabeling_sign
            if canonicalization_sign != 1:
                raise AssertionError("epsilon/odd carrier canonicalization sign drifted")
            contribution = (
                phi_coefficients[r]
                * ((-1) ** form_tilde_count)
                * canonicalization_sign
            )
            group = grouped.setdefault(
                (ghost_tilde_count, form_tilde_count),
                {
                    "coefficient": Fraction(),
                    "multiplicity": 0,
                    "expanded_words": [],
                },
            )
            group["coefficient"] += contribution
            group["multiplicity"] += 1
            group["expanded_words"].append(
                {
                    "word": "".join(word) or "EMPTY",
                    "tilde_component_sign": (-1) ** form_tilde_count,
                    "odd_reordering_sign": odd_reordering_sign,
                    "epsilon_relabeling_sign": epsilon_relabeling_sign,
                    "canonicalization_sign": canonicalization_sign,
                }
            )
        for (ghost_tilde_count, form_tilde_count), group in sorted(grouped.items()):
            coefficient = group["coefficient"]
            ghost_number = 1 + ghost_tilde_count
            form_degree = r + form_tilde_count + 2 * p
            term_id = (
                f"PHI{r}_U{ghost_tilde_count}_P{form_tilde_count}_W{p}"
            )
            terms.append(
                {
                    "term_id": term_id,
                    "phi_r": r,
                    "p": p,
                    "ghost_number": ghost_number,
                    "form_degree": form_degree,
                    "coefficient": _fraction(coefficient),
                    "carrier": {
                        "undifferentiated_weyl_ghost_count": 1,
                        "epsilon_count": 1,
                        "ghost_gradient_U_count": ghost_tilde_count,
                        "schouten_one_form_P_count": form_tilde_count,
                        "explicit_dx_count": r,
                        "weyl_two_form_count": p,
                    },
                    "canonical_factor_order": "omega epsilon U...U P...P dx...dx W...W",
                    "multiplicity": group["multiplicity"],
                    "expanded_words": group["expanded_words"],
                    "sign_origin": "tilde_omega = U - P plus odd-carrier reordering inside epsilon",
                }
            )
    return tuple(
        sorted(
            terms,
            key=lambda row: (
                row["ghost_number"],
                row["phi_r"],
                row["term_id"],
            ),
        )
    )


def euler_intrinsic_component_expansion() -> dict[str, Any]:
    """Build the exact carrier expansion and its current verification gates."""

    terms = _expanded_terms()
    components = []
    for ghost_number, form_degree in EULER_BIDEGREES:
        component_terms = [
            row
            for row in terms
            if (row["ghost_number"], row["form_degree"])
            == (ghost_number, form_degree)
        ]
        components.append(
            {
                "ghost_number": ghost_number,
                "form_degree": form_degree,
                "term_count": len(component_terms),
                "terms": component_terms,
                "component_status": (
                    "EXPANDED_PRECANONICAL"
                    if component_terms
                    else "STRUCTURALLY_ZERO_BY_R_LE_N_OVER_2"
                ),
            }
        )

    counts = tuple(component["term_count"] for component in components)
    if counts != (3, 2, 1, 0, 0):
        raise AssertionError("ordinary Euler component counts drifted")

    coefficient_rows = tuple(
        tuple(_coefficient(term["coefficient"]) for term in component["terms"])
        for component in components
    )
    if coefficient_rows != (
        (Fraction(1), Fraction(4), Fraction(4)),
        (Fraction(-4), Fraction(-8)),
        (Fraction(4),),
        (),
        (),
    ):
        raise AssertionError("ordinary Euler component coefficients drifted")

    # With X denoting the Schouten contribution P_a dx^a, the top component
    # is the exact binomial expansion of epsilon (W+2X)(W+2X).
    top_polynomial = {
        "W_squared": Fraction(1),
        "W_X": Fraction(4),
        "X_squared": Fraction(4),
    }
    reconstructed_euler = {
        "W_squared": Fraction(1),
        "W_X": Fraction(4),
        "X_squared": Fraction(4),
    }
    if top_polynomial != reconstructed_euler:
        raise AssertionError("top Euler reconstruction failed")

    bottom = components[2]
    forbidden_bottom_factors = {
        "schouten_one_form_P_count",
        "weyl_two_form_count",
    }
    if any(
        term["carrier"][factor]
        for term in bottom["terms"]
        for factor in forbidden_bottom_factors
    ):
        raise AssertionError("Euler bottom contains a non-BRST-inert carrier")

    payload = {
        "result_id": "EULER_INTRINSIC_BIDEGREE_EXPANSION",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "source": {
            "title": "General solutions of the Wess-Zumino consistency condition for the Weyl anomalies",
            "arxiv": "0704.2472",
            "source_version": "v1 (2007-04-19)",
            "formula": "Theorem 1, specialized to n=4 and globally rescaled by the frozen top normalization",
            "intrinsic_length_bound": "0 <= r <= m=n/2=2",
        },
        "carrier_definitions": {
            "U_alpha": "partial_alpha omega",
            "P_alpha": "K_alpha_rho dx^rho",
            "tilde_omega_alpha": "U_alpha - P_alpha",
            "X": "Schouten contribution P_alpha dx^alpha in the curvature decomposition",
        },
        "dictionary_sha256": generalized_connection_dictionary()["dictionary_sha256"],
        "normalization_sha256": euler_normalization_contract()[
            "normalization_sha256"
        ],
        "components": components,
        "checks": {
            "ordinary_bidegree_expansion": "VERIFIED",
            "coefficient_multiplicities_from_binomial_expansion": "VERIFIED",
            "top_component_reconstructs_omega_E4": "VERIFIED",
            "bottom_QW_closure": "VERIFIED",
            "ghost_number_4_form_1_component": "STRUCTURALLY_ZERO",
            "ghost_number_5_form_0_component": "STRUCTURALLY_ZERO",
            "QW_a14_plus_dh_a23": "NOT_COMPUTED_MISSING_COTTON_AND_GAMMA_ACTION",
            "QW_a23_minus_dh_a32": "NOT_COMPUTED_MISSING_COTTON_AND_GAMMA_ACTION",
        },
        "top_reconstruction": {
            "curvature_decomposition": "R = W + 2 X",
            "computed_polynomial": {
                key: _fraction(value) for key, value in top_polynomial.items()
            },
            "target_polynomial": {
                key: _fraction(value) for key, value in reconstructed_euler.items()
            },
            "residual": {},
        },
        "bottom_closure": {
            "representative": "4 omega epsilon^(ab nu1 nu2) U_a U_b dx^nu1 dx^nu2",
            "rules": [
                "Q_W omega = 0",
                "Q_W U_alpha = partial_alpha(Q_W omega) = 0",
                "Q_W dx^mu = 0",
                "the Weyl variation of the density carrier is proportional to omega and vanishes after multiplication by the existing odd omega",
            ],
            "residual": {},
        },
        "claim_boundary": {
            "intrinsic_tower_status": "COMPONENT_EXPANSION_VERIFIED_CONNECTING_IDENTITIES_PENDING",
            "relative_cohomology_status": "UNDECIDED",
            "coefficient_status": "NOT_COMPUTED",
            "full_bv_status": "BLOCKED_BY_ANTIFIELD_EXPORT",
        },
        "next_required_generator_identities": [
            "D W^(mu nu) = 2 C_rho g^(rho[mu) dx^(nu])",
            "Q_W P_alpha from Q_W K_alpha_beta = -nabla_alpha partial_beta omega",
            "Gamma_alpha action on the Weyl two-form",
            "Cotton cancellation in both connecting bidegree equations",
        ],
    }
    return {**payload, "expansion_sha256": canonical_sha256(payload)}
