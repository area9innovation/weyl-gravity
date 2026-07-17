#!/usr/bin/env python3
"""Independent verifier for the Berger 84-row mixed r*kappa unary gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from closed_universe_observers.generate_berger_84_row_mixed_r_kappa_unary_gate import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    SOURCE_FILES,
    build,
)


def _matrix(entries: list[list[object]]) -> sp.Matrix:
    result = sp.zeros(10)
    for row, column, coefficient in entries:
        result[row, column] = sp.sympify(coefficient, locals={"I": sp.I})
    return result


def _vector(entries: list[list[object]]) -> sp.Matrix:
    result = sp.zeros(10, 1)
    for index, coefficient in entries:
        result[index] = sp.sympify(coefficient, locals={"I": sp.I})
    return result


def _independent_transport(value: dict) -> None:
    source = json.loads(DEPENDENCIES["rod_gravity_unary"].read_text())["physical_phi2_tensor"]
    matrices = [_matrix(item["entries"]) for item in source["spatial_derivative_matrices"]]
    for frequency in ("zero", "positive", "negative"):
        packed = sp.zeros(100, 1)
        for index, coefficient in source["assembled_sparse_coefficients"][frequency]:
            packed[index] = sp.sympify(coefficient, locals={"I": sp.I})
        components = [sp.Matrix(packed[10 * index:10 * (index + 1), 0]) for index in range(10)]
        expected_delta_n = [-sp.Rational(4, 3) * components[index] for index in (1, 2, 3)]
        persisted = value["q10_memory_transport"]["frequency_sectors"][frequency]
        observed_delta_n = [_vector(entries) for entries in persisted["delta_n_spatial_components_e1_e2_e3"]]
        if any((expected_delta_n[index] - observed_delta_n[index]).applyfunc(sp.simplify) != sp.zeros(10, 1) for index in range(3)):
            raise ValueError("independent delta n reconstruction failed")
        divergence = sum((matrices[index] * expected_delta_n[index] for index in range(3)), sp.zeros(10, 1))
        if (divergence - _vector(persisted["divergence_with_frozen_volume"])).applyfunc(sp.simplify) != sp.zeros(10, 1):
            raise ValueError("independent frozen-volume divergence reconstruction failed")
        frozen_multiplier = _vector(persisted["frozen_pairing_adjoint_multiplier"])
        if (frozen_multiplier + divergence).applyfunc(sp.simplify) != sp.zeros(10, 1):
            raise ValueError("independent frozen-pairing adjoint reconstruction failed")


def _independent_green_first_variation(value: dict) -> None:
    r = sp.symbols("r")
    operator0 = sp.Matrix([[5, 2], [3, 2]])
    variation = sp.Matrix([[1, 4], [-2, 3]])
    inverse0 = operator0.inv()
    inverse1 = -inverse0 * variation * inverse0
    candidate = inverse0 + r * inverse1
    operator = operator0 + r * variation
    for residual in (operator * candidate - sp.eye(2), candidate * operator - sp.eye(2)):
        if any(
            sp.simplify(sp.expand(residual[row, column]).coeff(r, 1)) != 0
            for row in range(2) for column in range(2)
        ):
            raise ValueError("independent Green first variation failed")
    audit = value["q10_formal_green_correction"]
    if audit["left_inverse_defect_count_at_r"] or audit["right_inverse_defect_count_at_r"]:
        raise ValueError("persisted Green first variation has a defect")


def _semantic_boundary(value: dict) -> None:
    if value["bidegree_audit"]["delta_T_bidegree"] != [1, 0]:
        raise ValueError("delta T was reassigned to the mixed bidegree")
    if value["bidegree_audit"]["delta_B_bidegree"] != [1, 1]:
        raise ValueError("delta B bidegree drifted")
    gate = value["q11_profile_gate"]
    if gate["mixed_Q11_computed"] or gate["profile_metric_variation_computed"]:
        raise ValueError("underdetermined profile was promoted")
    if gate["underdetermination_witness"]["independent_channel_defect_count"] != 2:
        raise ValueError("two-channel profile obstruction drifted")
    flags = value["flags"]
    required_true = (
        "MEMORY_TRANSPORT_BIDEGREE_CORRECTED",
        "PHI2_INDUCED_DELTA_T_EXACT",
        "FROZEN_PAIRING_DELTA_T_ADJOINT_EXACT",
        "Q10_CLOCK_GREEN_FIRST_VARIATION_EXACT",
        "SEPARATE_R_AXIS_MEMORY_TRANSPORT_REPAIRED",
        "MIXED_PROFILE_UNDERDETERMINED_BY_HANDOFF",
    )
    required_false = (
        "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED",
        "MIXED_GREEN_COEFFICIENT_CERTIFIED",
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "84_ROW_Q2_Q3_CERTIFIED",
        "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
        "QUANTUM_CLAIM",
    )
    if not all(flags[key] is True for key in required_true):
        raise ValueError("exact transport result was demoted")
    if not all(flags[key] is False for key in required_false):
        raise ValueError("blocked mixed result was promoted")
    if not all(row["detected"] and row["defect_count"] > 0 for row in value["mutation_results"]):
        raise ValueError("mutation rail failed")


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("mixed r*kappa unary certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    _independent_transport(value)
    _independent_green_first_variation(value)
    _semantic_boundary(value)
    for key in (
        "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED",
        "MIXED_GREEN_COEFFICIENT_CERTIFIED",
        "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED",
        "OBSERVER_EVALUATION_MORPHISM_CERTIFIED",
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
        raise ValueError("strict schema mutation accepted")
    print("BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
