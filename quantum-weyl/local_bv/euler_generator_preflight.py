"""Indexed generator and convention preflight for the Euler connecting rows.

The purpose of this module is to make a failed connecting cancellation
diagnostic.  It binds the source Cotton convention to the project's existing
Weyl--Schouten--Cotton algebra, supplies a small indexed total-form word
algebra, applies the Weyl differential to the bottom representative, and
audits the finite two-Riemann decomposition used by the Euler head.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable

from .algebra import canonical_sha256
from .curvature import RIEMANN
from .specialization import WEYL
from .tensors import TensorExpression, TensorFactor, TensorMonomial
from .weyl_decomposition import (
    COTTON,
    SCHOUTEN,
    cotton_definition_relation,
    expand_riemann_factors,
)


@dataclass(frozen=True)
class GeneratorSpec:
    name: str
    tensor_rank: int
    ghost_number: int
    form_degree: int
    coefficient_parity: int
    weyl_weight: int | str

    @property
    def total_parity(self) -> int:
        return (self.coefficient_parity + self.form_degree) % 2

    def canonical_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "tensor_rank": self.tensor_rank,
            "ghost_number": self.ghost_number,
            "form_degree": self.form_degree,
            "coefficient_parity": self.coefficient_parity,
            "total_parity": self.total_parity,
            "weyl_weight": self.weyl_weight,
        }


GENERATOR_SPECS = {
    row.name: row
    for row in (
        GeneratorSpec("omega", 0, 1, 0, 1, 0),
        GeneratorSpec("density_epsilon", 4, 0, 0, 0, -4),
        GeneratorSpec("U", 1, 1, 0, 1, 0),
        GeneratorSpec("P", 1, 0, 1, 0, "INHOMOGENEOUS_CONNECTION"),
        GeneratorSpec("H", 1, 1, 1, 1, 0),
        GeneratorSpec("dx", 1, 0, 1, 0, 0),
        GeneratorSpec("W_two_form", 2, 0, 2, 0, -2),
        GeneratorSpec("Cotton_two_form", 1, 0, 2, 0, -2),
    )
}
Q_ROW_STATUS = {
    "omega": "AVAILABLE_ZERO",
    "density_epsilon": "AVAILABLE_NONZERO",
    "U": "AVAILABLE_ZERO",
    "P": "AVAILABLE_NONZERO",
    "H": "AVAILABLE_ZERO",
    "dx": "AVAILABLE_ZERO",
    "W_two_form": "NOT_COMPUTED_GAMMA_AND_WEIGHT_ACTION",
    "Cotton_two_form": "NOT_COMPUTED_DERIVED_CURVATURE_ACTION",
}


@dataclass(frozen=True)
class IndexedFactor:
    generator: str
    indices: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.generator not in GENERATOR_SPECS:
            raise ValueError(f"unknown Euler generator: {self.generator}")
        if len(self.indices) != GENERATOR_SPECS[self.generator].tensor_rank:
            raise ValueError(
                f"{self.generator} expects {GENERATOR_SPECS[self.generator].tensor_rank} indices"
            )

    @property
    def spec(self) -> GeneratorSpec:
        return GENERATOR_SPECS[self.generator]

    def sort_key(self) -> tuple[object, ...]:
        return self.generator, self.indices

    def canonical_payload(self) -> dict[str, object]:
        return {"generator": self.generator, "indices": list(self.indices)}


Word = tuple[IndexedFactor, ...]
WordExpression = dict[Word, Fraction]


def _canonical_word(factors: Iterable[IndexedFactor]) -> tuple[int, Word | None]:
    original = tuple(factors)
    order = tuple(sorted(range(len(original)), key=lambda index: original[index].sort_key()))
    inversions = 0
    for left_position, left_original in enumerate(order):
        if not original[left_original].spec.total_parity:
            continue
        for right_original in order[left_position + 1 :]:
            if (
                original[right_original].spec.total_parity
                and left_original > right_original
            ):
                inversions += 1
    canonical = tuple(original[index] for index in order)
    if any(
        left == right and left.spec.total_parity
        for left, right in zip(canonical, canonical[1:])
    ):
        return 0, None
    return (-1 if inversions % 2 else 1), canonical


def _expression(terms: Iterable[tuple[Fraction | int, Iterable[IndexedFactor]]]) -> WordExpression:
    output: WordExpression = {}
    for coefficient, factors in terms:
        sign, word = _canonical_word(factors)
        if not sign or word is None:
            continue
        value = output.get(word, Fraction()) + sign * Fraction(coefficient)
        if value:
            output[word] = value
        else:
            output.pop(word, None)
    return output


def _q_factor(factor: IndexedFactor) -> tuple[tuple[Fraction, Word], ...]:
    if Q_ROW_STATUS[factor.generator].startswith("NOT_COMPUTED"):
        raise ValueError(f"Q_W row is not computed for {factor.generator}")
    if factor.generator == "density_epsilon":
        return (
            (
                Fraction(-4),
                (
                    IndexedFactor("omega"),
                    factor,
                ),
            ),
        )
    if factor.generator == "P":
        return ((Fraction(-1), (IndexedFactor("H", factor.indices),)),)
    return ()


def q_weyl(expression: WordExpression) -> WordExpression:
    """Apply the odd Weyl differential with coefficient-parity signs."""

    terms: list[tuple[Fraction, Word]] = []
    for word, coefficient in expression.items():
        prefix_parity = 0
        for position, factor in enumerate(word):
            for image_coefficient, replacement in _q_factor(factor):
                sign = -1 if prefix_parity % 2 else 1
                terms.append(
                    (
                        coefficient * image_coefficient * sign,
                        word[:position] + replacement + word[position + 1 :],
                    )
                )
            prefix_parity += factor.spec.coefficient_parity
    return _expression(terms)


def _word_payload(expression: WordExpression) -> list[dict[str, object]]:
    return [
        {
            "coefficient": {
                "numerator": coefficient.numerator,
                "denominator": coefficient.denominator,
            },
            "factors": [factor.canonical_payload() for factor in word],
        }
        for word, coefficient in sorted(
            expression.items(), key=lambda item: tuple(factor.sort_key() for factor in item[0])
        )
    ]


def _source_project_cotton_bridge() -> dict[str, object]:
    a, b, c = 0, 1, 2
    source_cotton = TensorExpression(
        {
            TensorMonomial((TensorFactor(SCHOUTEN, (b, a), (c,)),)): 1,
            TensorMonomial((TensorFactor(SCHOUTEN, (c, a), (b,)),)): -1,
        }
    )
    project_cotton = TensorExpression.monomial(
        TensorMonomial((TensorFactor(COTTON, (a, b, c)),))
    )
    definition = cotton_definition_relation((a, b, c))
    if source_cotton + project_cotton != definition:
        raise AssertionError("source/project Cotton convention bridge drifted")
    payload = {
        "source_definition": "C_source[a,b,c] = nabla_c P_ba - nabla_b P_ca",
        "project_definition": "A_project[a,b,c] = nabla_b P_ca - nabla_c P_ba",
        "bridge": "C_source[a,b,c] = -A_project[a,b,c]",
        "source_expression_sha256": source_cotton.canonical_hash(),
        "project_expression_sha256": project_cotton.canonical_hash(),
        "definition_relation_sha256": definition.canonical_hash(),
        "verification_status": "VERIFIED_EXACT_TENSOR_RELATION",
    }
    return {**payload, "bridge_sha256": canonical_sha256(payload)}


def _two_riemann_preflight() -> dict[str, object]:
    source = TensorExpression.monomial(
        TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 2, 3)),
                TensorFactor(RIEMANN, (4, 5, 6, 7)),
            )
        )
    )
    expanded = expand_riemann_factors(source, max_factors=2)
    sectors: dict[str, TensorExpression] = {}
    for weyl_count, schouten_count, name in (
        (2, 0, "WEYL_WEYL"),
        (1, 1, "WEYL_SCHOUTEN"),
        (0, 2, "SCHOUTEN_SCHOUTEN"),
    ):
        sectors[name] = TensorExpression(
            {
                monomial: coefficient
                for monomial, coefficient in expanded.terms.items()
                if sum(factor.spec == WEYL for factor in monomial.factors)
                == weyl_count
                and sum(factor.spec == SCHOUTEN for factor in monomial.factors)
                == schouten_count
            }
        )
    if len(expanded.terms) != 25 or any(not sector for sector in sectors.values()):
        raise AssertionError("two-Riemann sector expansion drifted")
    payload = {
        "source_term_count": len(source.terms),
        "expanded_term_count": len(expanded.terms),
        "source_sha256": source.canonical_hash(),
        "expanded_sha256": expanded.canonical_hash(),
        "sector_term_counts": {
            name: len(sector.terms) for name, sector in sectors.items()
        },
        "sector_sha256": {
            name: sector.canonical_hash() for name, sector in sectors.items()
        },
        "epsilon_contraction_status": "NOT_COMPUTED",
        "verification_status": "RICCI_PRODUCT_EXPANSION_VERIFIED",
    }
    return {**payload, "preflight_sha256": canonical_sha256(payload)}


def euler_generator_preflight() -> dict[str, Any]:
    bottom = _expression(
        (
            (
                4,
                (
                    IndexedFactor("omega"),
                    IndexedFactor("density_epsilon", (0, 1, 2, 3)),
                    IndexedFactor("U", (0,)),
                    IndexedFactor("U", (1,)),
                    IndexedFactor("dx", (2,)),
                    IndexedFactor("dx", (3,)),
                ),
            ),
        )
    )
    bottom_q = q_weyl(bottom)
    if bottom_q:
        raise AssertionError("indexed Weyl differential did not close the Euler bottom")

    q_squared = {}
    for name, spec in GENERATOR_SPECS.items():
        if Q_ROW_STATUS[name].startswith("NOT_COMPUTED"):
            q_squared[name] = Q_ROW_STATUS[name]
            continue
        indices = tuple(range(spec.tensor_rank))
        generator = _expression(((1, (IndexedFactor(name, indices),)),))
        q_squared[name] = "VERIFIED" if not q_weyl(q_weyl(generator)) else "FAILED"
    if any(
        status != "VERIFIED"
        for name, status in q_squared.items()
        if not Q_ROW_STATUS[name].startswith("NOT_COMPUTED")
    ):
        raise AssertionError("Q_W squared failed on an Euler preflight generator")

    cotton_bridge = _source_project_cotton_bridge()
    riemann_preflight = _two_riemann_preflight()
    generator_payload = [
        spec.canonical_payload() for spec in GENERATOR_SPECS.values()
    ]
    payload = {
        "result_id": "EULER_CONNECTING_IDENTITY_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generator_dictionary": generator_payload,
        "generator_dictionary_sha256": canonical_sha256(generator_payload),
        "cotton_convention_bridge": cotton_bridge,
        "two_riemann_top_preflight": riemann_preflight,
        "bottom_representative": _word_payload(bottom),
        "bottom_QW_residual": _word_payload(bottom_q),
        "QW_squared_on_generators": q_squared,
        "QW_generator_row_status": Q_ROW_STATUS,
        "checks": {
            "indexed_total_form_words": "VERIFIED",
            "coefficient_and_total_parities_separated": "VERIFIED",
            "source_project_cotton_sign": "VERIFIED",
            "bounded_two_riemann_expansion": "VERIFIED",
            "bottom_closure_by_applied_QW": "VERIFIED",
            "QW_squared_on_available_generator_rows": "VERIFIED",
            "epsilon_contracted_top_reconstruction": "NOT_COMPUTED",
            "horizontal_generator_rows": "NOT_COMPUTED",
            "QW_dh_anticommutator_on_connecting_generators": "NOT_COMPUTED",
            "Gamma_action_on_W_two_form": "NOT_COMPUTED",
        },
        "source_to_project_identity_map": {
            "source_DW": "D W^(mu nu) = 2 C_source_rho g^(rho[mu) dx^(nu])",
            "project_DW": "D W^(mu nu) = -2 A_project_rho g^(rho[mu) dx^(nu])",
            "status": "SIGN_TRANSLATED_HORIZONTAL_ROW_NOT_YET_IMPLEMENTED",
        },
        "claim_boundary": {
            "preflight_status": "INDEXED_QW_AND_CONVENTION_ROWS_VERIFIED_HORIZONTAL_ROWS_PENDING",
            "intrinsic_tower_status": "CONNECTING_IDENTITIES_NOT_COMPUTED",
            "relative_cohomology_status": "UNDECIDED",
        },
    }
    return {**payload, "preflight_sha256": canonical_sha256(payload)}
