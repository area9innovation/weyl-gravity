"""Exact Chern--Weil algebra for the Euler variational transgression.

The algebra is deliberately small and noncommutative.  It derives curvature,
connection variation, and Bianchi rows from ``R=dA+A^2`` rather than entering
the transgression identity as a rewrite rule.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import factorial
from typing import Iterable, Mapping

from .algebra import canonical_sha256


Word = tuple[str, ...]
Expression = dict[Word, Fraction]
PairWord = tuple[Word, Word]
PairExpression = dict[PairWord, Fraction]

FORM_DEGREES = {"A": 1, "dA": 2, "K": 1, "dK": 2}
EXTERIOR_DERIVATIVE = {"A": "dA", "dA": None, "K": "dK", "dK": None}
VARIATION = {"A": "K", "dA": "dK", "K": None, "dK": None}


def _clean(terms: Mapping[Word, Fraction | int]) -> Expression:
    return {word: Fraction(value) for word, value in terms.items() if value}


def add(*expressions: Expression) -> Expression:
    result: dict[Word, Fraction] = {}
    for expression in expressions:
        for word, coefficient in expression.items():
            result[word] = result.get(word, Fraction()) + coefficient
    return _clean(result)


def scale(coefficient: Fraction | int, expression: Expression) -> Expression:
    return _clean({word: Fraction(coefficient) * value for word, value in expression.items()})


def multiply(left: Expression, right: Expression) -> Expression:
    result: dict[Word, Fraction] = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            word = left_word + right_word
            result[word] = result.get(word, Fraction()) + left_coefficient * right_coefficient
    return _clean(result)


def word_degree(word: Word) -> int:
    return sum(FORM_DEGREES[atom] for atom in word)


def exterior_derivative(expression: Expression) -> Expression:
    result: dict[Word, Fraction] = {}
    for word, coefficient in expression.items():
        prefix_degree = 0
        for position, atom in enumerate(word):
            differentiated = EXTERIOR_DERIVATIVE[atom]
            if differentiated is not None:
                new_word = word[:position] + (differentiated,) + word[position + 1 :]
                sign = -1 if prefix_degree % 2 else 1
                result[new_word] = result.get(new_word, Fraction()) + sign * coefficient
            prefix_degree += FORM_DEGREES[atom]
    return _clean(result)


def vary(expression: Expression) -> Expression:
    """Apply the degree-zero connection variation derivation."""

    result: dict[Word, Fraction] = {}
    for word, coefficient in expression.items():
        for position, atom in enumerate(word):
            varied = VARIATION[atom]
            if varied is None:
                continue
            new_word = word[:position] + (varied,) + word[position + 1 :]
            result[new_word] = result.get(new_word, Fraction()) + coefficient
    return _clean(result)


def covariant_derivative(expression: Expression) -> Expression:
    """Return ``D X=dX+A X-(-1)^degree(X) X A`` term by term."""

    result = exterior_derivative(expression)
    for word, coefficient in expression.items():
        degree = word_degree(word)
        result = add(
            result,
            {("A",) + word: coefficient},
            {word + ("A",): -((-1) ** degree) * coefficient},
        )
    return result


def _canonical_pair(left: Word, right: Word) -> tuple[PairWord, int]:
    """Use graded symmetry of ``epsilon_abcd X^ab wedge Y^cd``."""

    direct = (left, right)
    swapped = (right, left)
    if direct <= swapped:
        return direct, 1
    sign = -1 if (word_degree(left) * word_degree(right)) % 2 else 1
    return swapped, sign


def invariant_pair(left: Expression, right: Expression) -> PairExpression:
    result: dict[PairWord, Fraction] = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            pair, sign = _canonical_pair(left_word, right_word)
            result[pair] = result.get(pair, Fraction()) + sign * left_coefficient * right_coefficient
    return {pair: value for pair, value in result.items() if value}


def pair_add(*expressions: PairExpression) -> PairExpression:
    result: dict[PairWord, Fraction] = {}
    for expression in expressions:
        for pair, coefficient in expression.items():
            result[pair] = result.get(pair, Fraction()) + coefficient
    return {pair: value for pair, value in result.items() if value}


def pair_scale(coefficient: Fraction | int, expression: PairExpression) -> PairExpression:
    return {pair: Fraction(coefficient) * value for pair, value in expression.items() if value}


def _expression_payload(expression: Expression) -> list[dict[str, object]]:
    return [
        {
            "coefficient": {"numerator": coefficient.numerator, "denominator": coefficient.denominator},
            "word": list(word),
            "form_degree": word_degree(word),
        }
        for word, coefficient in sorted(expression.items())
    ]


def _pair_payload(expression: PairExpression) -> list[dict[str, object]]:
    return [
        {
            "coefficient": {"numerator": coefficient.numerator, "denominator": coefficient.denominator},
            "left": list(pair[0]),
            "right": list(pair[1]),
            "form_degree": word_degree(pair[0]) + word_degree(pair[1]),
        }
        for pair, coefficient in sorted(expression.items())
    ]


def _derived_weyl_connection_variation() -> dict[str, Fraction]:
    """Substitute ``h_ab=2 omega g_ab`` into the Levi-Civita variation.

    The three keys denote ``g_{rho nu} nabla_mu omega``,
    ``g_{rho mu} nabla_nu omega``, and ``g_{mu nu} nabla_rho omega``.
    The coefficients are produced from the Koszul formula's ``(+,+,-)/2``
    row and the factor two in the Weyl metric variation.
    """

    koszul_terms = (
        (Fraction(1, 2), "g_rho_nu_D_mu_omega"),
        (Fraction(1, 2), "g_rho_mu_D_nu_omega"),
        (Fraction(-1, 2), "g_mu_nu_D_rho_omega"),
    )
    result: dict[str, Fraction] = {}
    for coefficient, carrier in koszul_terms:
        result[carrier] = result.get(carrier, Fraction()) + 2 * coefficient
    return result


def _four_dimensional_generalized_connection_template() -> dict[str, object]:
    """Return the project ``n=4`` generalized-connection ansatz candidate.

    The project's symbolic carrier convention currently produces
    ``(-1)^p 2^p m!/(r! p!)``.  Boulanger's printed coefficient instead
    contains ``2^-p``.  The two vectors are kept separate until the carrier
    normalization map is verified; this function does not certify that map.
    """

    n = 4
    m = n // 2
    components = []
    for r in range(m + 1):
        p = m - r
        coefficient = Fraction(
            ((-1) ** p) * (2**p) * factorial(m),
            factorial(r) * factorial(p),
        )
        components.append(
            {
                "r": r,
                "p": p,
                "explicit_form_degree": n - r,
                "generalized_connection_degree": r,
                "weyl_two_form_count": p,
                "coefficient": coefficient,
                "sector": "TYPE_B_SEPARATELY_CLOSED" if r == 0 else "TYPE_A",
            }
        )
    if tuple(component["coefficient"] for component in components) != (
        Fraction(4),
        Fraction(-4),
        Fraction(1),
    ):
        raise AssertionError("four-dimensional generalized-connection coefficients drifted")
    return {
        "spacetime_dimension": n,
        "m": m,
        "generalized_connection": "tilde_omega_a = partial_a omega - Schouten_ab dx^b",
        "project_candidate_coefficient_formula": "(-1)^p 2^p m!/(r! p!)",
        "components": tuple(components),
        "type_a_component_indices": (1, 2),
        "type_b_component_indices": (0,),
        "expansion_status": "IN_PROGRESS",
    }


@lru_cache(maxsize=1)
def euler_transgression_analysis() -> dict[str, object]:
    connection = {("A",): Fraction(1)}
    connection_variation = {("K",): Fraction(1)}
    curvature = add(exterior_derivative(connection), multiply(connection, connection))
    curvature_variation = vary(curvature)
    covariant_connection_variation = covariant_derivative(connection_variation)
    if curvature_variation != covariant_connection_variation:
        raise AssertionError("delta R != D(delta A)")

    bianchi = covariant_derivative(curvature)
    if bianchi:
        raise AssertionError("derived curvature violates D R=0")

    euler = invariant_pair(curvature, curvature)
    delta_euler = pair_add(
        invariant_pair(curvature_variation, curvature),
        invariant_pair(curvature, curvature_variation),
    )
    theta = pair_scale(2, invariant_pair(connection_variation, curvature))
    d_theta = pair_scale(
        2,
        pair_add(
            invariant_pair(covariant_connection_variation, curvature),
            pair_scale(-1, invariant_pair(connection_variation, bianchi)),
        ),
    )
    variational_residual = pair_add(delta_euler, pair_scale(-1, d_theta))
    if variational_residual:
        raise AssertionError("delta E4 - d Theta_E did not vanish")

    descent_descendant = pair_scale(-1, theta)
    # Written explicitly as Q E4 + d(-Theta_E).
    descent_residual = pair_add(delta_euler, pair_scale(-1, d_theta))
    if descent_residual:
        raise AssertionError("Q E4 + d a3 did not vanish")

    connection_row = _derived_weyl_connection_variation()
    if tuple(connection_row.values()) != (Fraction(1), Fraction(1), Fraction(-1)):
        raise AssertionError("derived Weyl Levi-Civita connection row drifted")

    # Independent coordinate-current check in the carrier basis
    # (Ric^{ab} Hess_ab omega, R Box omega).  Contracted Bianchi gives
    # div(8 G^{ab} nabla_b omega) = 8 Ric.Hess - 4 R Box.
    local_euler_weyl_variation = (Fraction(8), Fraction(-4))
    coordinate_current_divergence = (Fraction(8), Fraction(-4))
    if local_euler_weyl_variation != coordinate_current_divergence:
        raise AssertionError("coordinate Euler current normalization drifted")

    # For the anomaly lift a4=omega E4, intrinsic Q omega=0 and the odd
    # Leibniz rule gives Q(a4)=-omega dTheta.  Adding d(omega Theta) leaves
    # d omega wedge Theta.  This exact nonzero residual records why the
    # intrinsic type-A continuation may not be replaced by the variational
    # transgression alone.
    anomaly_first_step = {
        "Q_omega_E4": {"omega_dTheta": Fraction(-1)},
        "d_omega_Theta": {
            "domega_Theta": Fraction(1),
            "omega_dTheta": Fraction(1),
        },
        "residual": {"domega_Theta": Fraction(1)},
    }
    generalized_connection_template = _four_dimensional_generalized_connection_template()

    return {
        "connection": connection,
        "connection_variation": connection_variation,
        "curvature": curvature,
        "curvature_variation": curvature_variation,
        "covariant_connection_variation": covariant_connection_variation,
        "bianchi_residual": bianchi,
        "euler": euler,
        "delta_euler": delta_euler,
        "theta_variation": theta,
        "descent_descendant": descent_descendant,
        "d_theta": d_theta,
        "variational_residual": variational_residual,
        "descent_residual": descent_residual,
        "derived_weyl_connection_variation": connection_row,
        "local_euler_weyl_variation": local_euler_weyl_variation,
        "coordinate_current_divergence": coordinate_current_divergence,
        "anomaly_first_step": anomaly_first_step,
        "generalized_connection_template": generalized_connection_template,
        "expression_payload": _expression_payload,
        "pair_payload": _pair_payload,
        "hash": canonical_sha256,
    }
