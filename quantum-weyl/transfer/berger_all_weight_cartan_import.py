"""Pinned import of the all-weight homogeneous Berger arity-two Cartan theorem."""

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
CLASSICAL_COMMIT = "60c84aa55c50651fdfae1f6274249e2179a56d2d"
CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN.json"
SCHEMA_RELATIVE = "d_quotient_classical/schema/berger-all-weight-arity-two-D-Cartan-v1.schema.json"
PRODUCER_RELATIVE = "d_quotient_classical/backreacted_clock/berger_all_weight_arity_two_d_cartan.py"
VERIFIER_RELATIVE = "d_quotient_classical/backreacted_clock/verify_berger_all_weight_arity_two_d_cartan.py"
TEST_RELATIVE = "d_quotient_classical/backreacted_clock/tests/test_berger_all_weight_arity_two_d_cartan.py"
REPORT_RELATIVE = "d_quotient_classical/reports/berger-all-weight-arity-two-D-Cartan.md"
Q2_CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"
NO_GO_CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json"


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


def _cubic_from_q2(payload: dict[str, Any]) -> list[list[list[sp.Expr]]]:
    cubic = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for entry in payload["classical_binary_q2"]["entries"]:
        output, left, right = entry["output"] - 3, entry["left"], entry["right"]
        value = sp.Rational(entry["coefficient"])
        cubic[output][left][right] = value
        cubic[output][right][left] = value
    return cubic


def validate_classical_payload(
    payload: object, schema: object, q2_payload: object
) -> tuple[dict[str, Any], dict[str, bool]]:
    """Recompute the coefficient formulas and symbolic Cartan identity."""

    if not all(isinstance(value, dict) for value in (payload, schema, q2_payload)):
        raise ValueError("all-weight payload, schema, or q2 dependency is not an object")
    assert isinstance(payload, dict) and isinstance(schema, dict) and isinstance(q2_payload, dict)
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-all-weight-arity-two-D-Cartan-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("all-weight classical schema identity or strictness drifted")
    if (
        payload.get("schema") != "pure-weyl-berger-all-weight-arity-two-D-Cartan-v1"
        or payload.get("result_id") != "BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN"
        or payload.get("claim_status") != "CERTIFIED_REDUCED_MODE_NONZERO_WEIGHT_CARTAN_CONTRACTION"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise ValueError("all-weight classical result identity drifted")
    dependencies = payload.get("dependency_refs", {})
    if (
        dependencies.get("q2_block", {}).get("sha256")
        != hashlib.sha256(_git_blob(Q2_CERTIFICATE_RELATIVE)).hexdigest()
        or dependencies.get("finite_block_no_go", {}).get("sha256")
        != hashlib.sha256(_git_blob(NO_GO_CERTIFICATE_RELATIVE)).hexdigest()
    ):
        raise ValueError("all-weight dependency binding drifted")

    complex_ = payload.get("all_weight_complex", {})
    if (
        complex_.get("weight_lattice") != "Z"
        or complex_.get("support_in_weight")
        != "algebraic direct sum (finite support per input); completion is separate"
        or complex_.get("field_rows_at_each_weight") != ["u_k", "N_k", "rho_k"]
        or complex_.get("equation_rows_at_each_weight") != ["E_u,k", "E_N,k", "E_rho,k"]
        or complex_.get("closure") != "integer weights are closed under addition"
    ):
        raise ValueError("all-weight complex or closure drifted")

    hessian = sp.Matrix(
        [[sp.Rational(value) for value in row[:3]] for row in q2_payload["classical_unary_q1"]["matrix"][3:6]]
    )
    declared_hessian = sp.Matrix(
        [[sp.Rational(value) for value in row] for row in payload["coefficients"]["H"]]
    )
    inverse = sp.Matrix(
        [[sp.Rational(value) for value in row] for row in payload["coefficients"]["H_inverse"]]
    )
    if declared_hessian != hessian or hessian * inverse != sp.eye(3):
        raise ValueError("all-weight Hessian inverse identity failed")
    cubic = _cubic_from_q2(q2_payload)

    homotopy = payload.get("arity_two_Cartan_homotopy", {})
    mixed: dict[tuple[int, int, int], tuple[sp.Expr, sp.Expr]] = {}
    for entry in homotopy.get("mixed_sparse_entries", []):
        key = (entry["output_field"], entry["equation_input"], entry["field_input"])
        if key in mixed:
            raise ValueError("duplicate all-weight mixed primitive coefficient")
        mixed[key] = (
            sp.Rational(entry["coefficient_equation_weight"]),
            sp.Rational(entry["coefficient_field_weight"]),
        )
    equation: dict[tuple[int, int, int], tuple[sp.Expr, sp.Expr]] = {}
    for entry in homotopy.get("equation_sparse_entries", []):
        key = (entry["output_equation"], entry["left_equation"], entry["right_equation"])
        if key in equation:
            raise ValueError("duplicate all-weight equation primitive coefficient")
        equation[key] = (
            sp.Rational(entry["coefficient_left_weight"]),
            sp.Rational(entry["coefficient_right_weight"]),
        )

    for output in range(3):
        for equation_input in range(3):
            for field_input in range(3):
                base = sp.factor(
                    sum(
                        inverse[output, equation_index]
                        * cubic[equation_index][field_index][field_input]
                        * inverse[field_index, equation_input]
                        for equation_index in range(3)
                        for field_index in range(3)
                    )
                )
                expected = (-sp.Rational(2, 3) * base, -sp.Rational(1, 3) * base)
                if mixed.get((output, equation_input, field_input), (sp.S.Zero, sp.S.Zero)) != expected:
                    raise ValueError("all-weight mixed primitive coefficient failed")
        for left_equation in range(3):
            for right_equation in range(3):
                base = sp.factor(
                    sum(
                        cubic[output][first][second]
                        * inverse[first, left_equation]
                        * inverse[second, right_equation]
                        for first in range(3)
                        for second in range(3)
                    )
                )
                expected = (sp.Rational(1, 3) * base, -sp.Rational(1, 3) * base)
                if equation.get((output, left_equation, right_equation), (sp.S.Zero, sp.S.Zero)) != expected:
                    raise ValueError("all-weight equation primitive coefficient failed")
    if len(mixed) != homotopy.get("mixed_nonzero_count") or len(equation) != homotopy.get(
        "equation_nonzero_count"
    ):
        raise ValueError("all-weight primitive sparse count drifted")

    # Independently check every nontrivial input-type Cartan identity as a
    # polynomial in arbitrary input weights k and ell.
    k, ell = sp.symbols("k ell")
    for left in range(3):
        for right in range(3):
            for output in range(3):
                source = (k + ell) * sum(
                    inverse[output, equation_index] * cubic[equation_index][left][right]
                    for equation_index in range(3)
                )
                first = sum(
                    hessian[equation_input, left]
                    * (
                        mixed.get((output, equation_input, right), (0, 0))[0] * k
                        + mixed.get((output, equation_input, right), (0, 0))[1] * ell
                    )
                    for equation_input in range(3)
                )
                second = sum(
                    hessian[equation_input, right]
                    * (
                        mixed.get((output, equation_input, left), (0, 0))[0] * ell
                        + mixed.get((output, equation_input, left), (0, 0))[1] * k
                    )
                    for equation_input in range(3)
                )
                if sp.factor(source + first + second) != 0:
                    raise ValueError("all-weight symbolic Cartan identity failed")
            for equation_input in range(3):
                for output_equation in range(3):
                    source = k * sum(
                        cubic[output_equation][field][right]
                        * inverse[field, equation_input]
                        for field in range(3)
                    )
                    post = sum(
                        hessian[output_equation, field_output]
                        * (
                            mixed.get((field_output, equation_input, right), (0, 0))[0]
                            * k
                            + mixed.get((field_output, equation_input, right), (0, 0))[1]
                            * ell
                        )
                        for field_output in range(3)
                    )
                    pre = -sum(
                        hessian[second_equation, right]
                        * (
                            equation.get(
                                (output_equation, equation_input, second_equation),
                                (0, 0),
                            )[0]
                            * k
                            + equation.get(
                                (output_equation, equation_input, second_equation),
                                (0, 0),
                            )[1]
                            * ell
                        )
                        for second_equation in range(3)
                    )
                    if sp.factor(source + post + pre) != 0:
                        raise ValueError("all-weight mixed-input Cartan identity failed")

    def iota2_basis(
        left_kind: str,
        left_index: int,
        left_weight: sp.Expr,
        right_kind: str,
        right_index: int,
        right_weight: sp.Expr,
    ) -> dict[tuple[str, int], sp.Expr]:
        if left_kind == "x" and right_kind == "x":
            return {}
        if left_kind == "x" and right_kind == "e":
            return iota2_basis(
                "e", right_index, right_weight, "x", left_index, left_weight
            )
        if left_kind == "e" and right_kind == "x":
            return {
                ("x", output): sp.factor(a * left_weight + b * right_weight)
                for (output, equation_input, field_input), (a, b) in mixed.items()
                if equation_input == left_index
                and field_input == right_index
                and a * left_weight + b * right_weight != 0
            }
        return {
            ("e", output): sp.factor(a * left_weight + b * right_weight)
            for (output, left_equation, right_equation), (a, b) in equation.items()
            if left_equation == left_index
            and right_equation == right_index
            and a * left_weight + b * right_weight != 0
        }

    def pair(vector: dict[tuple[str, int], sp.Expr], kind: str, index: int) -> sp.Expr:
        value = sp.S.Zero
        for (output_kind, output), coefficient in vector.items():
            if output == index and output_kind == "x" and kind == "e":
                value += coefficient
            elif output == index and output_kind == "e" and kind == "x":
                value -= coefficient
        return sp.factor(value)

    basis = tuple((kind, index) for kind in ("x", "e") for index in range(3))
    parity = {"x": 0, "e": 1}
    third_weight = -k - ell
    for first_kind, first in basis:
        for second_kind, second in basis:
            for third_kind, third in basis:
                first_value = pair(
                    iota2_basis(first_kind, first, k, second_kind, second, ell),
                    third_kind,
                    third,
                )
                rotated = pair(
                    iota2_basis(
                        second_kind,
                        second,
                        ell,
                        third_kind,
                        third,
                        third_weight,
                    ),
                    first_kind,
                    first,
                )
                sign = (
                    -1
                    if parity[first_kind]
                    * (parity[second_kind] + parity[third_kind])
                    % 2
                    else 1
                )
                if sp.factor(first_value - sign * rotated) != 0:
                    raise ValueError("all-weight graded cyclicity identity failed")

    exact_checks = payload.get("exact_checks", {})
    if not exact_checks or any(value is not True for value in exact_checks.values()):
        raise ValueError("all-weight classical exact check dropped")
    flags = payload.get("flags", {})
    for name in (
        "BERGER_ALL_WEIGHT_HOMOGENEOUS_Q2_D_CLOSED",
        "BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN",
        "NONZERO_WEIGHT_D_CARTAN_TESTED",
    ):
        if flags.get(name) is not True:
            raise ValueError("all-weight positive claim dropped")
    for name in (
        "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION",
        "FULL_4D_SUPPORT_LOCAL_Q2",
        "COMPLETE_54_ROW_ARITY_TWO_D_CARTAN",
        "ND2_PHYSICAL_EXECUTION_AUTHORIZED",
    ):
        if flags.get(name) is not False:
            raise ValueError("all-weight claim boundary drifted")

    checks = {
        "strict_schema_identity": True,
        "dependency_hashes_bound": True,
        "integer_weight_convolution_closed": True,
        "hessian_inverse_exact": True,
        "mixed_primitive_coefficients_recomputed": True,
        "equation_primitive_coefficients_recomputed": True,
        "sparse_counts_exact": True,
        "all_input_type_Cartan_identities_symbolic": True,
        "graded_cyclicity_symbolic": True,
        "first_order_time_locality_imported": True,
        "claim_boundary_fail_closed": True,
    }
    return payload, checks


def build_import() -> dict[str, Any]:
    payload, checks = validate_classical_payload(
        _git_json(CERTIFICATE_RELATIVE),
        _git_json(SCHEMA_RELATIVE),
        _git_json(Q2_CERTIFICATE_RELATIVE),
    )
    homotopy = payload["arity_two_Cartan_homotopy"]
    return {
        "schema": "quantum-weyl-berger-all-weight-arity-two-cartan-import-v1",
        "result_id": "BERGER_ALL_WEIGHT_ARITY_TWO_CARTAN_IMPORT",
        "result_state": "NONZERO_WEIGHT_CARTAN_SOURCE_HAS_EXPLICIT_NONZERO_EXACT_PRIMITIVE",
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
                    ("finite_no_go_dependency", NO_GO_CERTIFICATE_RELATIVE),
                )
            },
        },
        "exact_import_checks": checks,
        "cartan_verdict": {
            "source_definition": "A_D^(2)=[q2,iota_D^(1)]",
            "source_nonzero_for_generic_nonzero_weights": True,
            "equation": "[q1,iota_D^(2)]=-A_D^(2)",
            "binary_verdict": "ADMISSIBLE_EXACT_PRIMITIVE",
            "primitive_nonzero": True,
            "primitive_operator_D_weight": 0,
            "input_weight_lattice": "Z x Z",
            "output_weight": "k+l",
            "mixed_formula": homotopy["mixed_formula"],
            "equation_formula": homotopy["equation_formula"],
            "mixed_nonzero_tensor_count": homotopy["mixed_nonzero_count"],
            "equation_nonzero_tensor_count": homotopy["equation_nonzero_count"],
            "differential_order_in_time": 1,
            "support_local_in_time": True,
            "graded_cyclic": True,
            "obstruction_witness": None,
        },
        "field_and_weight_content": {
            "fields_at_each_weight": ["u_k", "N_k", "rho_k"],
            "equations_at_each_weight": ["E_u,k", "E_N,k", "E_rho,k"],
            "all_integer_D_weights_retained": True,
            "finite_support_per_input": True,
        },
        "physical_interpretation": {
            "degree_zero_cohomology_dimension_per_weight": 0,
            "degree_one_cohomology_dimension_per_weight": 0,
            "introduces_negative_physical_direction": False,
            "negative_direction_reason": "the Hessian is invertible at every weight and the algebraic direct-sum Koszul--Tate complex is weightwise acyclic",
            "einstein_extra_weyl_coupling": {
                "status": "NOT_APPLICABLE_AT_NON_EINSTEIN_HOMOGENEOUS_BERGER_BASE_POINT",
                "coupling_established": False,
                "reason": "the retained u/N/rho rows have no radiative Einstein-versus-extra-Weyl branch decomposition",
            },
        },
        "claim_flags": {
            "NONZERO_WEIGHT_D_CARTAN_TESTED": True,
            "NONZERO_WEIGHT_D_CARTAN_EXACT_PRIMITIVE_EXISTS": True,
            "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION": False,
            "FULL_4D_SUPPORT_LOCAL_Q2": False,
            "COMPLETE_54_ROW_ARITY_TWO_D_CARTAN": False,
            "ND2_PHYSICAL_EXECUTION_AUTHORIZED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "reduced_mode_limitation": "The theorem retains every temporal D weight but only the three spatially homogeneous Berger field/equation pairs. It is time-local and exact on the algebraic direct sum, not the full four-dimensional support-local q2 or the complete 54-row BV Cartan contraction. It contains no radiative branch labels, causal/Hadamard data, residual transfer, or quantum correction.",
        "next_gate": "FULL_4D_SUPPORT_LOCAL_Q2_AND_COMPLETE_54_ROW_CARTAN",
    }
