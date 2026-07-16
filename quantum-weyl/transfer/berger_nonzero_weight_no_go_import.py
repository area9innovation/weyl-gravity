"""Pinned import of the exact Berger finite nonzero-weight closure no-go."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_COMMIT = "74125e016a1967c5745c4e6e04cd8fb5a7fa4007"
CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json"
SCHEMA_RELATIVE = "d_quotient_classical/schema/berger-nonzero-D-weight-finite-block-no-go-v1.schema.json"
PRODUCER_RELATIVE = "d_quotient_classical/backreacted_clock/berger_nonzero_weight_finite_block_no_go.py"
VERIFIER_RELATIVE = "d_quotient_classical/backreacted_clock/verify_berger_nonzero_weight_finite_block_no_go.py"
TEST_RELATIVE = "d_quotient_classical/backreacted_clock/tests/test_berger_nonzero_weight_finite_block_no_go.py"
REPORT_RELATIVE = "d_quotient_classical/reports/berger-nonzero-D-weight-finite-block-no-go.md"
Q2_CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned classical artifact {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _expression(raw: object, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    if not isinstance(raw, str):
        raise ValueError("exact polynomial is not a string")
    return sp.sympify(raw, locals={str(variable): variable for variable in variables})


def validate_classical_payload(
    payload: object, schema: object
) -> tuple[dict[str, Any], dict[str, bool]]:
    """Independently verify the proof-carrying pinned classical payload."""

    if not isinstance(payload, dict) or not isinstance(schema, dict):
        raise ValueError("classical no-go payload or schema is not an object")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-nonzero-D-weight-finite-block-no-go-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical no-go schema identity or strictness drifted")
    if (
        payload.get("schema") != "pure-weyl-berger-nonzero-D-weight-finite-block-no-go-v1"
        or payload.get("result_id") != "BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO"
        or payload.get("claim_status") != "CERTIFIED_REDUCED_MODE_CLOSURE_OBSTRUCTION"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise ValueError("classical no-go identity drifted")

    dependency = payload.get("dependency_ref", {})
    q2_sha256 = hashlib.sha256(_git_blob(Q2_CERTIFICATE_RELATIVE)).hexdigest()
    if (
        dependency.get("result_id") != "BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK"
        or dependency.get("path") != Q2_CERTIFICATE_RELATIVE
        or dependency.get("sha256") != q2_sha256
    ):
        raise ValueError("classical q2 dependency binding drifted")

    x = sp.symbols("x_u x_N x_rho", real=True)
    square = payload.get("square_map", {})
    if square.get("input_basis") != ["u", "N", "rho"] or square.get(
        "output_basis"
    ) != ["E_u", "E_N", "E_rho"]:
        raise ValueError("classical square-map basis drifted")
    components = [_expression(value, x) for value in square.get("components", [])]
    if len(components) != 3:
        raise ValueError("classical square-map arity drifted")

    real = payload.get("real_anisotropy_certificate", {})
    coefficients = [sp.Rational(value) for value in real.get("combination_coefficients", [])]
    gram_rows = real.get("gram_matrix", [])
    if len(coefficients) != 3 or len(gram_rows) != 3 or any(len(row) != 3 for row in gram_rows):
        raise ValueError("real anisotropy certificate shape drifted")
    gram = sp.Matrix([[sp.Rational(value) for value in row] for row in gram_rows])
    positive_form = sum(coefficient * component for coefficient, component in zip(coefficients, components))
    if sp.expand((sp.Matrix(x).T * gram * sp.Matrix(x))[0] - positive_form) != 0:
        raise ValueError("real anisotropy identity failed")
    minors = [sp.factor(gram[:size, :size].det()) for size in range(1, 4)]
    declared_minors = [sp.Rational(value) for value in real.get("leading_principal_minors", [])]
    if minors != declared_minors or any(value <= 0 for value in minors):
        raise ValueError("real anisotropy positivity failed")

    complex_ = payload.get("complex_anisotropy_certificate", {})
    targets = [_expression(value, x) for value in complex_.get("targets", [])]
    multiplier_rows = complex_.get("multipliers_by_target", [])
    if len(targets) != 3 or len(multiplier_rows) != 3:
        raise ValueError("complex anisotropy certificate shape drifted")
    for target, raw_row in zip(targets, multiplier_rows):
        multipliers = [_expression(value, x) for value in raw_row]
        if len(multipliers) != 3 or sp.expand(
            sum(multiplier * component for multiplier, component in zip(multipliers, components))
            - target
        ) != 0:
            raise ValueError("complex ideal-membership identity failed")
    if (
        sp.expand(targets[0] - x[2] ** 4) != 0
        or sp.expand(targets[1].subs(x[2], 0) - x[0] ** 2) != 0
        or sp.expand(targets[2].subs(x[2], 0) - x[1] ** 2) != 0
    ):
        raise ValueError("complex anisotropy triangular conclusion failed")

    failed = payload.get("first_failed_block", {})
    leakage = [sp.factor(component.subs({x[0]: 1, x[1]: 0, x[2]: 0})) for component in components]
    witness = [sp.Rational(value) for value in failed.get("normalized_dual_witness", [])]
    if (
        failed.get("declared_field_weights") != [-1, 0, 1]
        or failed.get("missing_output_weight") != 2
        or leakage != [sp.Rational(value) for value in failed.get("leakage_vector", [])]
        or len(witness) != 3
        or sum(left * right for left, right in zip(leakage, witness)) != 1
        or failed.get("witness_evaluation") != "1"
    ):
        raise ValueError("normalized finite-block leakage witness failed")

    no_go = payload.get("finite_block_no_go", {})
    weights = no_go.get("sample_forced_weights", [])
    if (
        no_go.get("conclusion") != "no such finite nonzero-weight cyclic q2-closed block exists"
        or len(weights) < 2
        or any(weights[index + 1] != -2 * weights[index] for index in range(len(weights) - 1))
    ):
        raise ValueError("finite-block closure no-go recurrence drifted")

    flags = payload.get("flags", {})
    required_true = (
        "BERGER_Q2_SQUARE_MAP_ANISOTROPIC",
        "BERGER_NONZERO_WEIGHT_FINITE_BLOCK_NO_GO",
        "NONZERO_WEIGHT_MODE_CLOSURE_OBSTRUCTION",
    )
    required_false = (
        "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION",
        "CLASSICAL_SUPPORT_LOCAL_Q2",
        "ND2_PHYSICAL_EXECUTION_AUTHORIZED",
    )
    if any(flags.get(name) is not True for name in required_true) or any(
        flags.get(name) is not False for name in required_false
    ):
        raise ValueError("classical no-go claim boundary drifted")
    exact_checks = payload.get("exact_checks", {})
    if not exact_checks or any(value is not True for value in exact_checks.values()):
        raise ValueError("classical no-go exact check dropped")

    checks = {
        "strict_schema_identity": True,
        "q2_dependency_hash_bound": True,
        "square_map_exact": True,
        "real_positive_form_identity": True,
        "real_sylvester_positivity": True,
        "complex_ideal_memberships": True,
        "complex_triangular_anisotropy": True,
        "first_leakage_recomputed": True,
        "dual_leakage_witness_normalized": True,
        "forced_weight_recurrence_unbounded": True,
        "claim_boundary_fail_closed": True,
    }
    return payload, checks


def build_import() -> dict[str, Any]:
    payload, checks = validate_classical_payload(
        _git_json(CERTIFICATE_RELATIVE), _git_json(SCHEMA_RELATIVE)
    )
    failed = payload["first_failed_block"]
    return {
        "schema": "quantum-weyl-berger-nonzero-weight-closure-no-go-import-v1",
        "result_id": "ND2_BERGER_NONZERO_WEIGHT_CLOSURE_NO_GO_IMPORT",
        "result_state": "FINITE_NONZERO_WEIGHT_CYCLIC_Q2_BLOCK_EXACTLY_OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "classical_source": {
            "commit": CLASSICAL_COMMIT,
            "artifacts": {
                name: _artifact(relative)
                for name, relative in (
                    ("certificate", CERTIFICATE_RELATIVE),
                    ("schema", SCHEMA_RELATIVE),
                    ("producer", PRODUCER_RELATIVE),
                    ("independent_verifier", VERIFIER_RELATIVE),
                    ("tests", TEST_RELATIVE),
                    ("report", REPORT_RELATIVE),
                    ("q2_dependency", Q2_CERTIFICATE_RELATIVE),
                )
            },
        },
        "imported_theorem": {
            "square_map_input": payload["square_map"]["input_basis"],
            "square_map_output": payload["square_map"]["output_basis"],
            "anisotropic_over": ["R", "C"],
            "first_failed_weights": failed["declared_field_weights"],
            "missing_output_weight": failed["missing_output_weight"],
            "leakage_vector": failed["leakage_vector"],
            "normalized_dual_leakage_witness": failed["normalized_dual_witness"],
            "forced_weight_recurrence": payload["finite_block_no_go"]["forced_weight_recurrence"],
            "conclusion": payload["finite_block_no_go"]["conclusion"],
        },
        "exact_import_checks": checks,
        "cartan_disposition": {
            "finite_nonzero_weight_cyclic_q2_closed_block_available": False,
            "cartan_equation_reached": False,
            "cartan_obstruction_witness": None,
            "closure_leakage_witness": failed["normalized_dual_witness"],
            "reason": "the proposed finite mode complex leaks under q2 before the Cartan complex is defined",
        },
        "claim_flags": {
            "FINITE_NONZERO_WEIGHT_ROUTE_DECIDED": True,
            "FINITE_NONZERO_WEIGHT_CLOSURE_OBSTRUCTED": True,
            "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION": False,
            "INFINITE_ALL_WEIGHT_COMPLETION_ESTABLISHED_BY_THIS_IMPORT": False,
            "BERGER_SUPPORT_LOCAL_Q2_EXISTS": False,
            "ND2_PHYSICAL_EXECUTION_AUTHORIZED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "INFINITE_ALL_WEIGHT_COMPLETION_OR_FULL_SUPPORT_LOCAL_Q2_D_ACTION",
        "claim_boundary": "This pinned import proves an exact REDUCED-MODE closure obstruction for every finite pairing-nondegenerate nonzero-D-weight block built from the rational Berger q2. It is not a Cartan-cohomology obstruction, does not address the infinite all-weight completion, and supplies no support-local, Lorentzian, or quantum result.",
    }
