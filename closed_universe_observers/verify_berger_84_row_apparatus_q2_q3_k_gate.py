#!/usr/bin/env python3
"""Independent verifier for the Berger apparatus q2/q3 and affine-K gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from closed_universe_observers.generate_berger_84_row_apparatus_q2_q3_k_gate import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    SOURCE_FILES,
    build,
)


def _independent_jacobian_two_jet() -> None:
    s, t = sp.symbols("s t")
    G = sp.Matrix([[4, 1, 0], [1, 3, 1], [0, 1, 2]])
    X = sp.Matrix([[2, -1, 3], [-1, 5, 0], [3, 0, -2]])
    Y = sp.Matrix([[1, 2, -1], [2, -3, 4], [-1, 4, 6]])
    J = sp.sqrt(sp.det(G + s * X + t * Y))
    inverse = G.inv()
    J0 = sp.sqrt(G.det())
    first = J0 * sp.trace(inverse * X) / 2
    second = J0 * (
        sp.trace(inverse * X) * sp.trace(inverse * Y) / 4
        - sp.trace(inverse * X * inverse * Y) / 2
    )
    if sp.simplify(sp.diff(J, s).subs({s: 0, t: 0}) - first) != 0:
        raise ValueError("independent first Gram-Jacobian variation failed")
    if sp.simplify(sp.diff(J, s, t).subs({s: 0, t: 0}) - second) != 0:
        raise ValueError("independent second Gram-Jacobian variation failed")


def _independent_product_two_jet() -> None:
    s, t = sp.symbols("s t")
    factors = [
        2 + 3 * s + 5 * t + 7 * s * t,
        11 + 13 * s + 17 * t + 19 * s * t,
        23 + 29 * s + 31 * t + 37 * s * t,
        41 + 43 * s + 47 * t + 53 * s * t,
    ]
    product = sp.prod(factors)
    exact = sp.diff(product, s, t).subs({s: 0, t: 0})
    direct = sum(
        sp.diff(factor, s, t).subs({s: 0, t: 0})
        * sp.prod(factors[j].subs({s: 0, t: 0}) for j in range(4) if j != i)
        for i, factor in enumerate(factors)
    )
    pairs = sum(
        (
            sp.diff(factors[i], s).subs({s: 0, t: 0}) * sp.diff(factors[j], t).subs({s: 0, t: 0})
            + sp.diff(factors[i], t).subs({s: 0, t: 0}) * sp.diff(factors[j], s).subs({s: 0, t: 0})
        )
        * sp.prod(factors[k].subs({s: 0, t: 0}) for k in range(4) if k not in (i, j))
        for i in range(4)
        for j in range(i + 1, 4)
    )
    if sp.simplify(exact - direct - pairs) != 0:
        raise ValueError("independent readout product two-jet failed")
    if sp.simplify(exact - direct) == 0:
        raise ValueError("independent pair-partition mutation was not detected")


def _independent_affine_k_audit(value: dict) -> None:
    rods = json.loads(DEPENDENCIES["global_rods"].read_text())
    nu = sp.sqrt(58) / 6
    delta = sp.Rational(1, 96)
    for rod, recorded in zip(rods["global_rods"], value["K_Berger_gate"]["background_components"]["rod_witnesses"]):
        phase = sp.sympify(rod["hopf_phase"])
        expected = sp.simplify(-nu * 3 * sp.sqrt(10) * sp.cos(phase) * sp.sin(nu * delta) / 10)
        if expected == 0 or sp.simplify(sp.sympify(recorded["K0_value"]) - expected) != 0:
            raise ValueError("independent affine rod witness failed")
    phi2 = json.loads(DEPENDENCIES["rod_gravity_unary"].read_text())["physical_phi2_tensor"]
    expected_count = phi2["assembled_nonzero_counts"]["positive"] + phi2["assembled_nonzero_counts"]["negative"]
    if value["K_Berger_gate"]["background_components"]["time_dependent_Phi2_nonzero_coefficient_count"] != expected_count:
        raise ValueError("affine metric K0 count drifted")

    coordinates = sp.symbols("x0:4")
    rows = []
    derivative_rows = []
    for detector in rods["global_rods"]:
        center = sp.Rational(detector["physical_event_time"])
        for profile_text in detector["spatial_profiles"]:
            profile = sp.sympify(profile_text, locals={str(x): x for x in coordinates})
            spatial = [sp.expand(profile).coeff(x) for x in coordinates]
            rows.append([sp.cos(nu * center) * entry for entry in spatial] + [sp.sin(nu * center) * entry for entry in spatial])
            derivative_rows.append([nu * sp.sin(nu * center) * entry for entry in spatial] + [-nu * sp.cos(nu * center) * entry for entry in spatial])
    current_rank = sp.Matrix(rows).rank()
    closure_rank = sp.Matrix(rows + derivative_rows).rank()
    completion = value["K_Berger_gate"]["existing_rod_linear_symmetry_completion"]
    if (current_rank, closure_rank) != (6, 8):
        raise ValueError("independent rod closure rank failed")
    if completion["current_real_rod_span_rank"] != current_rank or completion["time_translation_closure_rank"] != closure_rank:
        raise ValueError("rod closure rank payload drifted")
    if completion["constant_internal_6_by_6_completion_exists"] or completion["minimal_additional_real_rod_directions"] != 2:
        raise ValueError("invalid six-rod internal-symmetry disposition")

    x = sp.symbols("x")
    K = 7 + 11 * x
    Q3 = 2 * x + 3 * x**2 / 2 + 5 * x**3 / 6
    Q4 = Q3 + 13 * x**4 / 24
    difference = sp.expand(K * sp.diff(Q4, x) - Q4 * sp.diff(K, x) - K * sp.diff(Q3, x) + Q3 * sp.diff(K, x)).coeff(x, 3)
    if sp.simplify(difference - sp.Rational(91, 6)) != 0:
        raise ValueError("independent q4 affine-K obstruction failed")


def _semantic_boundary(value: dict) -> None:
    flags = value["flags"]
    required_true = (
        "APPARATUS_NORMALIZED_PROFILE_TWO_JET_EXACT",
        "APPARATUS_Q2_ACTION_JET_EXPORTED",
        "APPARATUS_Q3_ACTION_JET_EXPORTED",
        "APPARATUS_Q2_Q3_CYCLIC_AT_R0",
        "APPARATUS_ARITY_TWO_IDENTITY_THROUGH_R_FIRST_JET",
        "APPARATUS_ARITY_THREE_IDENTITY_AT_R0",
        "AFFINE_K_BERGER_THROUGH_ARITY_TWO_CERTIFIED",
        "Q4_INPUT_REQUIRED",
        "FORMAL_BACKREACTED_UNARY_RANK_TWO_CERTIFIED",
    )
    required_false = (
        "APPARATUS_ARITY_THREE_IDENTITY_THROUGH_R_FIRST_JET",
        "FULL_BACKREACTED_APPARATUS_Q3_CERTIFIED",
        "K_BERGER_BACKGROUND_PRESERVING_ON_APPARATUS",
        "AFFINE_K_BERGER_THROUGH_ARITY_THREE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "EMITTER_RECOIL_CERTIFIED",
        "QUANTUM_CLAIM",
    )
    if not all(flags[key] is True for key in required_true):
        raise ValueError("certified apparatus jet was demoted")
    if not all(flags[key] is False for key in required_false):
        raise ValueError("apparatus/K result was over-promoted")
    disposition = value["observer_morphism_disposition"]
    if disposition["failure_category"] != "K_BERGER_AFFINE_ARITY_THREE_INPUT_OBSTRUCTION_NOT_SIGNAL_OR_RANK_FAILURE":
        raise ValueError("observer defect category drifted")
    if value["observer_response"]["formal_rank"] != 2:
        raise ValueError("formal response rank drifted")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("apparatus q2/q3 K certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {entry["path"]: entry["sha256"] for entry in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    _independent_jacobian_two_jet()
    _independent_product_two_jet()
    _independent_affine_k_audit(value)
    _semantic_boundary(value)
    for key in (
        "APPARATUS_ARITY_THREE_IDENTITY_THROUGH_R_FIRST_JET",
        "FULL_BACKREACTED_APPARATUS_Q3_CERTIFIED",
        "K_BERGER_BACKGROUND_PRESERVING_ON_APPARATUS",
        "AFFINE_K_BERGER_THROUGH_ARITY_THREE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "EMITTER_RECOIL_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][key] = True
        try:
            _semantic_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")
    schema_mutant = deepcopy(value)
    schema_mutant["unexpected"] = True
    try:
        Draft202012Validator(schema).validate(schema_mutant)
    except ValidationError:
        pass
    else:
        raise ValueError("strict-schema mutation accepted")
    return value


def main() -> int:
    verify()
    print("BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
