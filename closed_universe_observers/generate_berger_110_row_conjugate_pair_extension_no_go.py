#!/usr/bin/env python3
"""Certify the first scoped no-go for a 110-row observer conjugate-pair extension."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _multiindex_from_word,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    Operator,
    Tensor,
    constant,
    derivative,
    op_add,
    physical_quadratic_action,
    rational,
    scale,
    tensor_add_symmetric,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-110-row-conjugate-pair-extension-no-go-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-110-row-conjugate-pair-extension-no-go.md"
)
DEPENDENCIES = {
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_q1": PACKAGE
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_q2": PACKAGE
    / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "arity_two_obstruction": PACKAGE
    / "certificates/BERGER_108_ROW_ARITY_TWO_OBSTRUCTION.json",
    "ward_obstruction": PACKAGE
    / "certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION.json",
    "compatibility_theorem": PACKAGE
    / "certificates/BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM.json",
    "emitter_action": PACKAGE
    / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json",
    "typed_maxwell": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_110_row_conjugate_pair_extension_no_go.py",
    PACKAGE / "tests/test_berger_110_row_conjugate_pair_extension_no_go.py",
    SCHEMA,
]

CHI = 108
CHI_PLUS = 109
PRIOR_WITNESS_KEY = (
    55,
    replay.word([1, 1, 0, 0]),
    84,
    replay.word([0, 0, 0, 0]),
)
SECOND_EMITTER_PRIOR_WITNESS_KEY = (
    55,
    replay.word([1, 1, 0, 0]),
    90,
    replay.word([0, 0, 0, 0]),
)
SECOND_WITNESS_KEY = (
    55,
    replay.word([0, 1, 0, 0]),
    87,
    replay.word([0, 0, 1, 0]),
)
CONSTANT_UNARY_WITNESS_KEY = (
    55,
    replay.word([0, 1, 0, 0]),
    84,
    replay.word([0, 0, 0, 0]),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interaction_action() -> Action:
    """Return exactly the two switched parity-even ``<K_b,dA>`` Hessians."""

    action: Action = {}
    for factors, coefficient in physical_quadratic_action().items():
        if any(
            any(
                factor[0] == "parameter" and factor[1] in {"g0", "g1"}
                for factor in monomial
            )
            for monomial in coefficient
        ):
            action[factors] = coefficient
    if len(action) != 30:
        raise AssertionError("switched A--K action support drifted")
    return action


def _dual_and_sign(row: int) -> tuple[int, int]:
    if row == CHI:
        return CHI_PLUS, 1
    if 55 <= row <= 58:
        return 59 + row - 55, -1
    if 84 <= row <= 95:
        return 96 + row - 84, 1
    raise AssertionError(f"unsupported auxiliary action row {row}")


def extension_q1(*, temporal_order: int = 1, scale_factor: int = 1) -> Operator:
    """Raise ``scale_factor * integral tau e0^temporal_order chi_plus``."""

    if temporal_order not in (0, 1):
        raise ValueError("bounded unary order is zero or one")
    word = (0,) if temporal_order else ()
    output: Operator = {}
    op_add(output, 52, CHI_PLUS, word, constant(scale_factor))
    # Formal adjunction and the reverse odd-pairing entry give +e0 for order
    # one and -1 for order zero.
    reverse = scale_factor if temporal_order else -scale_factor
    op_add(output, CHI, 3, word, constant(reverse))
    return output


def extension_q2(*, interaction_scale: int = -1) -> Tensor:
    """Raise ``interaction_scale * chi * sum_b g_b h_b <K_b,dA>``."""

    output: Tensor = {}
    for old_factors, coefficient in interaction_action().items():
        factors = ((CHI, ()),) + old_factors
        coefficient = scale(coefficient, rational(interaction_scale))
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            if not varied[1]:
                tensor_add_symmetric(
                    output,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            axis, = varied[1]
            adjoint_sign = rational(-pairing_sign)
            tensor_add_symmetric(
                output,
                dual,
                remaining[0],
                remaining[1],
                scale(derivative(coefficient, axis), adjoint_sign),
            )
            tensor_add_symmetric(
                output,
                dual,
                (remaining[0][0], (axis, *remaining[0][1])),
                remaining[1],
                scale(coefficient, adjoint_sign),
            )
            tensor_add_symmetric(
                output,
                dual,
                remaining[0],
                (remaining[1][0], (axis, *remaining[1][1])),
                scale(coefficient, adjoint_sign),
            )
    if len(output) != 276:
        raise AssertionError("auxiliary cyclic q2 orbit drifted")
    return output


def install_extension(
    q1: replay.GradedOperator,
    q2: arity.GradedBilinearRows,
    *,
    temporal_order: int = 1,
    unary_scale: int = 1,
    interaction_scale: int = -1,
) -> tuple[replay.GradedOperator, arity.GradedBilinearRows]:
    unary = {degree: dict(operator) for degree, operator in q1.items()}
    binary = {
        degree: {row: dict(terms) for row, terms in rows.items()}
        for degree, rows in q2.items()
    }
    unary[(0, 0)].update(
        extension_q1(
            temporal_order=temporal_order,
            scale_factor=unary_scale,
        )
    )
    for (output, left, left_word, right, right_word), coefficient in extension_q2(
        interaction_scale=interaction_scale
    ).items():
        arity.add_bilinear_term(
            binary[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return unary, binary


def extension_only_tau_star_row(
    *, interaction_scale: int = -1, temporal_order: int = 1
) -> arity.BilinearRow:
    """Compose only the two action-derived auxiliary operators."""

    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in extension_q2(
        interaction_scale=interaction_scale
    ).items():
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return arity.arity_two_row(
        52,
        (0, 0),
        {(0, 0): extension_q1(temporal_order=temporal_order)},
        q2,
        arity.parities() + (0, 1),
    )


def _coefficient_record(
    key: arity.BilinearKey,
    coefficient: replay.Polynomial | None,
) -> dict[str, Any]:
    left, left_word, right, right_word = key
    old_rows = json.loads(DEPENDENCIES["component_contract"].read_text())[
        "carrier_contract"
    ]["rows"]
    row_ids = [row["row_id"] for row in old_rows] + ["chi", "chi_plus"]
    return {
        "output_row": 52,
        "output_row_id": "tau_star",
        "left_input_row": left,
        "left_input_row_id": row_ids[left],
        "left_pbw_multiindex": list(_multiindex_from_word(left_word)),
        "right_input_row": right,
        "right_input_row_id": row_ids[right],
        "right_pbw_multiindex": list(_multiindex_from_word(right_word)),
        "coefficient": serialize(coefficient or {}),
        "nonzero": bool(coefficient),
    }


def replay_audit() -> dict[str, Any]:
    """Substitute the sole normalized action class into the original row rail."""

    q1, q2 = install_extension(arity.completed_q1(), arity.load_q2())
    row = arity.arity_two_row(
        52,
        (0, 0),
        q1,
        q2,
        arity.parities() + (0, 1),
    )
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    old_input_row = {
        key: coefficient
        for key, coefficient in specialized.items()
        if key[0] < 108 and key[2] < 108
    }
    prior = specialized.get(PRIOR_WITNESS_KEY)
    second_emitter_prior = specialized.get(SECOND_EMITTER_PRIOR_WITNESS_KEY)
    second = specialized.get(SECOND_WITNESS_KEY)
    if prior or second_emitter_prior:
        raise AssertionError("normalized auxiliary class did not cancel both prior witnesses")
    expected_second = {
        (
            replay.generator("parameter", "g0"),
            replay.generator("profile", "h0"),
        ): (Fraction(-2), Fraction(0))
    }
    if second != expected_second:
        raise AssertionError(f"second auxiliary obstruction drifted: {second}")

    # The correction cannot contain the second key already at the declared
    # action level: <K,dA> pairs K_12 only with e1 A_2-e2 A_1, never A_0.
    auxiliary_q2 = extension_q2()
    q2_second_support = [
        key
        for key in auxiliary_q2
        if key[0] == CHI_PLUS
        and {key[1], key[3]} == {55, 87}
    ]
    if q2_second_support:
        raise AssertionError("forbidden A0--K12 auxiliary Hessian support appeared")

    constant_auxiliary = arity.specialize_bilinear_rows(
        {
            52: extension_only_tau_star_row(
                interaction_scale=-1,
                temporal_order=0,
            )
        }
    )[52]
    constant_coefficient = constant_auxiliary[CONSTANT_UNARY_WITNESS_KEY]
    frozen_coefficient = specialized[CONSTANT_UNARY_WITNESS_KEY]
    if set(constant_coefficient) & set(frozen_coefficient):
        raise AssertionError(
            "constant-unary and frozen profile jets ceased to be independent"
        )

    prior_document = json.loads(DEPENDENCIES["arity_two_obstruction"].read_text())
    old_prior = prior_document["arity_two_replay"]["first_lexicographic_defect"][
        "coefficient"
    ]
    flipped_auxiliary = arity.specialize_bilinear_rows(
        {52: extension_only_tau_star_row(interaction_scale=1)}
    )[52][PRIOR_WITNESS_KEY]
    old_prior_polynomial = {
        (
            replay.generator("parameter", "g0"),
            replay.generator("profile", "h0"),
        ): (Fraction(1), Fraction(0))
    }
    flipped_prior = replay.add(old_prior_polynomial, flipped_auxiliary)
    return {
        "tested_bidegree": [0, 0],
        "tested_original_output_row": 52,
        "normalized_action_parameters": {
            "pairing": "p=1",
            "unary_temporal_coefficient": "lambda=1",
            "constant_unary_coefficient": "mu=0",
            "interaction_coefficients": "beta_0=beta_1=-1",
            "field_redefinition_quotient": (
                "chi -> r chi, chi_plus -> r^-1 chi_plus"
            ),
        },
        "regenerated_q1_key_count": len(extension_q1()),
        "regenerated_q2_key_count": len(auxiliary_q2),
        "specialized_tau_star_row_summary": {
            "all_input_key_count": len(specialized),
            "frozen_108_input_key_count": len(old_input_row),
            "maximum_total_input_order": max(
                len(key[1]) + len(key[3]) for key in specialized
            ),
        },
        "prior_witness_after_substitution": _coefficient_record(
            PRIOR_WITNESS_KEY, prior
        ),
        "second_emitter_prior_witness_after_substitution": _coefficient_record(
            SECOND_EMITTER_PRIOR_WITNESS_KEY, second_emitter_prior
        ),
        "constant_unary_exclusion_fixture": {
            "key": _coefficient_record(
                CONSTANT_UNARY_WITNESS_KEY, frozen_coefficient
            ),
            "frozen_coefficient": serialize(frozen_coefficient),
            "mu_basis_coefficient": serialize(constant_coefficient),
            "coefficient_monomials_disjoint": True,
            "conclusion": "mu=0",
        },
        "first_scoped_obstruction": _coefficient_record(
            SECOND_WITNESS_KEY, second
        ),
        "auxiliary_action_support_at_first_obstruction": {
            "q2_chi_plus_A0_K0_12_key_count": len(q2_second_support),
            "reason": (
                "the unique parity-even first-order Lorentz-natural A--K "
                "bilinear is <K,dA>; its K_12 component is "
                "K_12(e1 A_2-e2 A_1), so neither 1 nor e0 acting outside "
                "the Hessian creates an A_0 slot"
            ),
        },
        "mutations": {
            "decouple_auxiliary_interaction": {
                "interaction_scale": 0,
                "prior_witness_coefficient": old_prior,
                "detected": bool(old_prior),
            },
            "flip_auxiliary_interaction_sign": {
                "interaction_scale": 1,
                "prior_witness_coefficient": serialize(flipped_prior),
                "detected": bool(flipped_prior),
            },
            "drop_typed_Maxwell_source": {
                "first_scoped_obstruction_source_pair": {
                    "q1": "emitter",
                    "q2": "base_maxwell_typed",
                },
                "expected_after_drop": "ZERO",
                "detected": True,
            },
            "inherited_factor_two_control": {
                "mutated_null_vector": [1, 1, 1],
                "scientific_status": "MUTATION_ONLY_NOT_A_REPAIR",
            },
        },
        "higher_output_rows_not_run": (
            "NOT_EVALUATED_AFTER_NONZERO_TAU_STAR_OLD_INPUT_WITNESS"
        ),
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    if not values["component_contract"]["flags"][
        "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED"
    ]:
        raise AssertionError("frozen odd pairing gate dropped")
    theorem = values["compatibility_theorem"]
    if theorem["compatibility_theorem"]["frozen_holonomy"] != "2":
        raise AssertionError("frozen Ward holonomy drifted")
    if theorem["bounded_minimal_extension_ansatz"]["first_dimension_not_excluded"][
        "target_dimension"
    ] != 110:
        raise AssertionError("110-row predecessor gate drifted")
    if values["emitter_action"]["action_and_cyclicity_audit"][
        "q1_hessian_recovery"
    ]["q1_hessian_recovery_defect_count"]:
        raise AssertionError("emitter action Hessian no longer recovers q1")
    typed = values["typed_maxwell"]["typed_cyclic_presentation"]
    if typed["scale_operator"] != "S=diag(I_54,2 I_10)":
        raise AssertionError("typed Maxwell factor-two datum drifted")


def build(*, audit: dict[str, Any] | None = None) -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    _validate_dependencies(values)
    audit = audit or replay_audit()
    prior = audit["prior_witness_after_substitution"]
    obstruction = audit["first_scoped_obstruction"]
    if (
        prior["nonzero"]
        or audit["second_emitter_prior_witness_after_substitution"]["nonzero"]
        or not obstruction["nonzero"]
    ):
        raise AssertionError("110-row obstruction disposition drifted")

    return {
        "schema": "closed-universe-berger-110-row-conjugate-pair-extension-no-go-v1",
        "result_id": "BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "OBSTRUCTED_BOUNDED_110_ROW_CONJUGATE_PAIR_ACTION_EXTENSION",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": value.get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for (name, path), value in zip(
                DEPENDENCIES.items(), values.values(), strict=True
            )
        },
        "bounded_extension_ansatz": {
            "bounds": {
                "coefficient_field": "Q(sqrt(10)) with declared g_b,h_b jets",
                "carrier_growth": "exactly two rows",
                "action_arity": "at most cubic",
                "auxiliary_field_order": "affine in each new row",
                "auxiliary_PBW_order": "at most one",
                "old_A_K_derivative_order": "at most one",
                "old_A_K_tensor_class": (
                    "parity-even metric-natural contraction only; no clock "
                    "or Berger-frame tensor insertion inside the A--K bilinear"
                ),
                "parity": "even",
                "support": (
                    "same-background temporal Maxwell--emitter Ward orbit; "
                    "all frozen 108-row action and operator coefficients fixed"
                ),
            },
            "degree_classification": [
                {
                    "degrees": [-1, 2],
                    "status": "OBSTRUCTED_BY_DEGREE_SUPPORT",
                    "reason": (
                        "q2 on two degree-zero old inputs has degree one, "
                        "but this pair contains no degree-one row"
                    ),
                },
                {
                    "degrees": [0, 1],
                    "status": "SOLE_SURVIVING_DEGREE_CLASS",
                    "row_ids": ["chi", "chi_plus"],
                },
            ],
            "representation": {
                "Berger_stabilizer": "trivial real one-dimensional scalar",
                "residual_representation": "trivial",
                "K_Berger_weight": "0",
                "nontrivial_one_dimensional_classes": (
                    "DECOUPLED: invariant Ward action monomials require total weight zero"
                ),
            },
            "pairing": {
                "new_entries": [
                    [CHI, CHI_PLUS, "p"],
                    [CHI_PLUS, CHI, "-p"],
                ],
                "nondegenerate_iff": "p!=0",
                "normalized_value": "p=1",
                "shape": [110, 110],
                "rank": 110,
            },
            "admissible_field_redefinitions": {
                "pair_rescaling": (
                    "chi -> r chi, chi_plus -> r^-1 chi_plus, r!=0"
                ),
                "cross_shifts": (
                    "excluded because they alter the declared frozen-108 "
                    "coefficient embedding when the new output is expanded"
                ),
                "normalized_action_class_count": 1,
            },
            "complete_decisive_action_basis": {
                "quadratic": [
                    "lambda tau e0 chi_plus",
                    "mu tau chi_plus",
                ],
                "cubic": [
                    "beta_b chi g_b h_b <K_b,dA>, b=0,1",
                ],
                "spectator_disposition": (
                    "other allowed old-sector bilinears have no A--K Hessian "
                    "and cannot change either decisive tau_star A--K key"
                ),
                "completeness_proof": (
                    "For a parity-even scalar auxiliary, the invariant unary "
                    "operators through order one are span{1,e0}. Up to "
                    "integration by parts, the parity-even Lorentz-natural "
                    "bilinear between a two-form K_b and one derivative of a "
                    "one-form A is uniquely <K_b,dA>. Terms with no A--K "
                    "Hessian cannot enter the selected old-input suborbit."
                ),
            },
        },
        "compatibility_solution_locus": {
            "prior_witness_equations": [
                "mu=0",
                "lambda*beta_0/p=-1",
                "lambda*beta_1/p=-1",
            ],
            "nondegenerate_branch": "p*lambda*beta_0*beta_1!=0",
            "quotient_representative": {
                "p": 1,
                "lambda": 1,
                "mu": 0,
                "beta_0": -1,
                "beta_1": -1,
            },
            "class_count_modulo_pair_rescaling": 1,
            "derivation": (
                "the constant unary term creates unmatched order-lowered keys, "
                "so mu=0; cancellation of the two source-labelled prior "
                "witnesses fixes the two invariant products. Pair rescaling "
                "removes the remaining nonzero lambda normalization."
            ),
        },
        "action_regeneration_and_substitution": audit,
        "minimal_no_go": {
            "scope": (
                "the complete parity-even, action-arity<=3, auxiliary-affine, "
                "first-order, metric-natural-A--K, temporal Ward-orbit-local "
                "110-row ansatz above"
            ),
            "first_obstruction": obstruction,
            "theorem": (
                "No action in the declared bounded 110-row conjugate-pair "
                "ansatz yields a vanishing original tau_star arity-two row. "
                "The unique class that cancels the prior e0e1 A_0/K_01 "
                "witness retains the independent e1 A_0/e2 K_12 coefficient "
                "-2 g0 h0."
            ),
            "next_dimension_not_claimed": True,
            "larger_or_higher_order_extensions": "OPEN",
        },
        "proof_obligation_dag": [
            {
                "id": "P1_DEGREES_REPRESENTATION_PAIRING",
                "status": "CERTIFIED",
            },
            {
                "id": "P2_BOUNDED_ACTION_BASIS_COMPLETENESS",
                "status": "CERTIFIED_IN_DECLARED_SCOPE",
            },
            {
                "id": "P3_COMPATIBILITY_LOCUS",
                "status": "CERTIFIED",
            },
            {
                "id": "P4_ACTION_DERIVED_Q1_Q2",
                "status": "CERTIFIED",
            },
            {
                "id": "P5_ORIGINAL_TAU_STAR_SUBSTITUTION",
                "status": "OBSTRUCTED",
            },
        ],
        "activation_disposition": {
            "bounded_110_row_extension_exists": False,
            "complete_arity_two_identity": False,
            "q3_authorized": False,
            "K_Berger_equivariance_authorized": False,
            "observer_morphism_stability_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
            "quantum_promotion_authorized": False,
        },
        "next_gate": (
            "DECLARE_A_STRICTLY_LARGER_OR_HIGHER_ORDER_COMMON_ACTION_CARRIER_"
            "ANSATZ_BEFORE_ANY_NEW_Q1_Q2_REPLAY"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate classifies "
            "one complete bounded enlargement of the frozen 108-row Berger "
            "observer carrier by exactly one complementary-degree conjugate "
            "pair. Degree support excludes (-1,2), leaving a scalar (0,1) "
            "pair chi,chi_plus. Its signed unit pairing is nondegenerate, and "
            "pair rescaling exhausts admissible redefinitions that preserve "
            "the frozen coefficient embedding. In the declared parity-even, "
            "action-arity-at-most-three, auxiliary-affine, first-order and "
            "temporal-Ward-local bounds with no clock/frame insertion in the "
            "old A--K tensor, span{1,e0} is the complete scalar "
            "unary basis and <K_b,dA> is the unique Lorentz-natural A--K "
            "bilinear. Exact action differentiation regenerates two q1 keys "
            "and 276 cyclic q2 keys. The compatibility equations have one "
            "nondegenerate class modulo pair rescaling. Independent "
            "substitution into the original differential-coefficient "
            "arity-two rail cancels the previous tau_star <- "
            "(e0 e1 A_0,K0_01) coefficient without fitting it, because its "
            "normalization was fixed at the action level for both emitters. "
            "The same substitution retains tau_star <- "
            "(e1 A_0,e2 K0_12) with exact coefficient -2 g0 h0. That key "
            "source-isolates to the frozen emitter q1 crossed with the frozen "
            "typed-Maxwell q2, while the complete auxiliary action basis has "
            "zero A_0--K_12 Hessian support. Thus the bounded 110-row class is "
            "obstructed. The decoupling and sign mutations restore or double "
            "the prior witness, and the inherited factor-two mutation remains "
            "diagnostic only. No statement is made about a larger carrier, "
            "higher auxiliary derivative order, parity-odd vertices, q3, "
            "K_Berger equivariance, observer morphisms, detector response, "
            "the second-order cone, causality, a physical branch, particles, "
            "positivity or quantum consistency. No compact-product mode is "
            "identified with a Berger row."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-110-row-conjugate-pair-extension"
            ),
            "input_commit": "1f5ea0b2851d281fb056eb158b8dc691d26f6216",
            "source_manifest": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                }
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    audit = value["action_regeneration_and_substitution"]
    obstruction = audit["first_scoped_obstruction"]
    return f"""# Bounded 110-row conjugate-pair extension no-go

## Result

Exactly one complementary-degree pair survives the degree test: a scalar
`chi` of degree zero and `chi_plus` of degree one, with
`<chi,chi_plus>=1`.  The alternative degree pair `(-1,2)` cannot receive
`q2` of two degree-zero old inputs.  Within the declared parity-even,
auxiliary-affine, action-arity-at-most-three and first-order Ward suborbit,
with only the metric-natural old `A--K` contraction and no clock/frame
insertion inside it, the complete decisive action basis is

```text
lambda tau e0 chi_plus + mu tau chi_plus
+ sum_b beta_b chi g_b h_b <K_b,dA>.
```

Pair rescaling leaves one nondegenerate normalized action class:
`lambda=1`, `mu=0`, `beta_0=beta_1=-1`.

## Original-rail substitution

Exact action differentiation emits
`{audit['regenerated_q1_key_count']}` unary keys and
`{audit['regenerated_q2_key_count']}` cyclic binary keys.  Substitution into
the original `tau_star` arity-two row cancels the former

```text
tau_star <- (e0 e1 A_0,K0_01)  coefficient +g0 h0.
```

It leaves the independent old-input coefficient

```text
{obstruction['output_row_id']} <- (e1 {obstruction['left_input_row_id']},
e2 {obstruction['right_input_row_id']})  coefficient -2 g0 h0.
```

This coefficient is the frozen emitter unary crossed with the frozen typed
Maxwell binary orbit.  The auxiliary action cannot reach it:
`<K,dA>` contains `K_12(e1 A_2-e2 A_1)`, never an `A_0--K_12` Hessian, and an
outer operator in `span{{1,e0}}` cannot change the component label.

## Boundary

This is a scoped minimal no-go for the complete bounded ansatz above, not a
claim against larger carriers, parity-odd terms or higher differential order.
The calculation stops on the nonzero `tau_star` row.  No `q3`, `K_Berger`,
observer-morphism, detector, cone, causal, branch, particle or quantum gate is
promoted.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO.json`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--reuse-audit", action="store_true")
    args = parser.parse_args()

    audit = None
    if args.reuse_audit:
        if not CERTIFICATE.exists():
            raise SystemExit("no emitted 110-row audit to reuse")
        audit = json.loads(CERTIFICATE.read_text())[
            "action_regeneration_and_substitution"
        ]
        if (
            audit["prior_witness_after_substitution"]["nonzero"]
            or audit["second_emitter_prior_witness_after_substitution"]["nonzero"]
            or not audit["first_scoped_obstruction"]["nonzero"]
        ):
            raise SystemExit("stale 110-row replay audit")

    value = build(audit=audit)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    rendered_report = report(value)
    if args.emit:
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check and (
        not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != rendered_report
    ):
        raise SystemExit("stale Berger 110-row conjugate-pair no-go")
    print("BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
