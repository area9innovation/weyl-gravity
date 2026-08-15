#!/usr/bin/env python3
"""Independently check polarized formal Yang--Feldman coefficients."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def recorded_digest(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("sha256", None)
    return digest(payload)


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def shapes(leaves: int, memo: dict[int, tuple[Any, ...]]) -> tuple[Any, ...]:
    """Enumerate nested pairs, independently of the producer's string recursion."""
    if leaves not in memo:
        values = []
        for left_count in range(1, leaves):
            for left in shapes(left_count, memo):
                for right in shapes(leaves - left_count, memo):
                    values.append((left, right))
        memo[leaves] = tuple(values)
    return memo[leaves]


def render_shape(value: Any) -> str:
    return "x" if value == "x" else f"B({render_shape(value[0])},{render_shape(value[1])})"


def add_poly(target: dict[str, Fraction], source: dict[str, Fraction], scale: Fraction = Fraction(1)) -> None:
    for tree, coefficient in source.items():
        target[tree] = target.get(tree, Fraction(0)) + scale * coefficient
        if target[tree] == 0:
            del target[tree]


def binary(left: dict[str, Fraction], right: dict[str, Fraction]) -> dict[str, Fraction]:
    return {
        f"B({l},{r})": lc * rc
        for l, lc in left.items()
        for r, rc in right.items()
    }


def exact_coefficients(max_power: int) -> list[dict[str, Fraction]]:
    coefficients = [{"x": Fraction(1)}]
    for power in range(1, max_power + 1):
        value: dict[str, Fraction] = {}
        for left_power in range(power):
            add_poly(value, binary(coefficients[left_power], coefficients[power - 1 - left_power]), -Fraction(1, 2))
        coefficients.append(value)
    return coefficients


def fixed_point_residual(coefficients: list[dict[str, Fraction]], power: int) -> dict[str, Fraction]:
    residual = dict(coefficients[power]) if power else dict(coefficients[0])
    if power == 0:
        add_poly(residual, {"x": Fraction(1)}, -1)
    else:
        for left_power in range(power):
            add_poly(residual, binary(coefficients[left_power], coefficients[power - 1 - left_power]), Fraction(1, 2))
    return residual


def picard(previous: list[dict[str, Fraction]], max_power: int) -> list[dict[str, Fraction]]:
    result: list[dict[str, Fraction]] = [{"x": Fraction(1)}] + [{} for _ in range(max_power)]
    for power in range(1, max_power + 1):
        for left_power in range(power):
            add_poly(result[power], binary(previous[left_power], previous[power - 1 - left_power]), -Fraction(1, 2))
    return result


def check(value: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if value is None:
        value = json.loads(RESULT.read_text())
    if value.get("result_id") != "STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1":
        errors.append("result identity drift")
        return errors

    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append(f"dependency hash drift: {item['path']}")

    literature = value.get("literature_template", {})
    if literature.get("artifact", {}).get("sha256") != "8175a1e403cf4843c171a5df040f35decb591280cd19d1a099323c29f642957e":
        errors.append("Hawkins-Rejzner content pin drift")
    if "Lemma 3.12" not in literature.get("imported_statement", "") or "nonperturbative" not in literature.get("imported_statement", ""):
        errors.append("formal-template boundary incomplete")

    convention = value.get("formal_convention", {})
    if "lambda/2" not in convention.get("fixed_point", "") or convention.get("direction", "").startswith("R is the formal inverse") is not True:
        errors.append("formal direction or factorial convention drift")
    recurrence = value.get("coefficient_recurrence", {})
    if recurrence.get("analytic_norm_or_radius") != "NOT_SUPPLIED" or "lambda-adic only" not in recurrence.get("formal_topology", ""):
        errors.append("formal/analytic boundary drift")

    rows = value.get("catalan_tree_formula", {}).get("checked_rows", [])
    coefficients = exact_coefficients(len(rows) - 1)
    memo: dict[int, tuple[Any, ...]] = {1: ("x",)}
    for index, row in enumerate(rows):
        leaves = index + 1
        rendered = tuple(render_shape(shape) for shape in shapes(leaves, memo))
        expected_count = comb(2 * index, index) // (index + 1)
        expected_weight = (-Fraction(1, 2)) ** index
        if row.get("coupling_power") != index or row.get("leaves") != leaves:
            errors.append(f"coefficient row index drift at {leaves} leaves")
        if row.get("plane_tree_count") != expected_count or row.get("catalan_closed_form") != expected_count:
            errors.append(f"Catalan count drift at {leaves} leaves")
        if row.get("canonical_tree_list_sha256") != digest(list(rendered)):
            errors.append(f"tree enumeration digest drift at {leaves} leaves")
        polynomial = coefficients[index]
        if set(polynomial) != set(rendered) or any(coefficient != expected_weight for coefficient in polynomial.values()):
            errors.append(f"tree polynomial drift at coupling power {index}")
        if parse_fraction(row.get("coefficient_per_plane_tree", "0")) != expected_weight:
            errors.append(f"per-tree rational drift at coupling power {index}")
        if parse_fraction(row.get("commutative_scalar_collapse", "0")) != expected_count * expected_weight:
            errors.append(f"scalar collapse drift at coupling power {index}")
        if fixed_point_residual(coefficients, index):
            errors.append(f"fixed-point coefficient residual at power {index}")

    max_power = len(rows) - 1
    iterate = [{"x": Fraction(1)}] + [{} for _ in range(max_power)]
    for iteration in range(max_power + 1):
        for power in range(iteration + 1):
            if iterate[power] != coefficients[power]:
                errors.append(f"Picard coefficient failed to stabilize: iteration={iteration}, power={power}")
                break
        iterate = picard(iterate, max_power)

    orientations = value.get("polarized_support_and_continuity", {})
    for sign, support in (("plus", "past compact"), ("minus", "future compact")):
        item = orientations.get(sign, {})
        if item.get("every_finite_coefficient_defined") is not True or item.get("coefficient_support_for_m_ge_1") != support:
            errors.append(f"{sign} support inheritance drift")
        if "fixed compact leaf-support Frechet step" not in item.get("fixed_step_continuity", ""):
            errors.append(f"{sign} continuity scope drift")

    diagnostic = value.get("bv_equation_diagnostic", {})
    if diagnostic.get("order_lambda_residual") != "q1(r_1)+(1/2)q2(x,x)=0":
        errors.append("first BV residual drift")
    expected_second = "(1/4)(B_sigma(x,q2(x,x))+B_sigma(q2(x,x),x))"
    if diagnostic.get("order_lambda_squared_residual") != expected_second:
        errors.append("lambda-squared BV residual drift")
    if diagnostic.get("order_lambda_squared_zero_certified") is not False or diagnostic.get("nonzero_claimed") is not False:
        errors.append("BV residual disposition over-promoted")

    foundations = value.get("foundational_strength", {})
    if foundations.get("choice_operation_added") is not False or foundations.get("infinite_analytic_sum_added") is not False:
        errors.append("foundation boundary drift")
    if foundations.get("weakest_complete_foundational_base") != "NOT_ESTABLISHED":
        errors.append("weakest-base over-promotion")

    flags = value.get("claim_flags", {})
    required_true = (
        "STRICT_386_CANDIDATE_POLARIZED_FORMAL_COEFFICIENTS_CERTIFIED",
        "STRICT_386_CANDIDATE_COEFFICIENTWISE_FIXED_POINT_VERIFIED",
        "STRICT_386_CANDIDATE_CATALAN_TREE_FORMULA_VERIFIED",
        "STRICT_386_CANDIDATE_FORMAL_INVERSE_VERIFIED",
        "STRICT_386_CANDIDATE_LAMBDA_ADIC_STABILIZATION_VERIFIED",
    )
    required_false = (
        "STRICT_386_CANDIDATE_ANALYTIC_SERIES_CONVERGENCE_CERTIFIED",
        "STRICT_386_CANDIDATE_NONPERTURBATIVE_MOLLER_MAP_CONSTRUCTED",
        "STRICT_386_WEYL_BV_MAURER_CARTAN_SERIES_CERTIFIED",
        "STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED",
        "STRICT_386_Q3_OR_HIGHER_CAUSAL_TREES_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS",
        "QME_RESTORED",
        "RESIDUAL_TRANSFERRED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    for key in required_true:
        if flags.get(key) is not True:
            errors.append(f"required true flag missing: {key}")
    for key in required_false:
        if flags.get(key) is not False:
            errors.append(f"required false firewall missing: {key}")

    for key, expected in value.get("canonical_hashes", {}).items():
        field = {
            "literature_template_sha256": "literature_template",
            "formal_convention_sha256": "formal_convention",
            "coefficient_recurrence_sha256": "coefficient_recurrence",
            "catalan_tree_formula_sha256": "catalan_tree_formula",
            "polarized_support_sha256": "polarized_support_and_continuity",
            "bv_equation_diagnostic_sha256": "bv_equation_diagnostic",
            "foundational_strength_sha256": "foundational_strength",
            "authority_boundary_sha256": "authority_boundary",
            "formal_coefficient_snapshot_sha256": "formal_coefficient_snapshot",
        }.get(key)
        if field and recorded_digest(value[field]) != expected:
            errors.append(f"canonical hash drift: {key}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1: PASS")
    print("  - unique retarded and advanced formal coefficients close lambda-adically")
    print("  - exact Catalan tree weights and coefficient residuals independently replay")
    print("  - the lambda-squared BV/Moller promotion gate remains explicitly open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
