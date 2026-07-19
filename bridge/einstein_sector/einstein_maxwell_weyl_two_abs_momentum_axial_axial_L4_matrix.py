"""Compute the complete axial-axial L=4 cross-|n| source matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from math import factorial, isqrt
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe import (
    OUTPUT_ORDERS,
    angular_derivative,
    canonical,
    load_relevant,
    scalar_l4,
    vector_l4,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_axial_L4_q2_slice.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
POLAR = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


Interval = tuple[Fraction, Fraction]


def _interval_add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def _interval_multiply(left: Interval, right: Interval) -> Interval:
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def _integer_power(value: Interval, exponent: int) -> Interval:
    if exponent < 0:
        powered = _integer_power(value, -exponent)
        if powered[0] <= 0 <= powered[1]:
            raise ZeroDivisionError("interval reciprocal crosses zero")
        return min(1 / powered[0], 1 / powered[1]), max(
            1 / powered[0], 1 / powered[1]
        )
    if exponent == 0:
        return Fraction(1), Fraction(1)
    if exponent % 2 == 0 and value[0] <= 0 <= value[1]:
        return Fraction(0), max(abs(value[0]), abs(value[1])) ** exponent
    endpoints = value[0] ** exponent, value[1] ** exponent
    return min(endpoints), max(endpoints)


def _sqrt_bound(value: Fraction, scale: int) -> tuple[Fraction, Fraction]:
    if value < 0:
        raise ValueError(f"negative radicand bound: {value}")
    scaled_floor = value.numerator * scale * scale // value.denominator
    root_floor = isqrt(scaled_floor)
    lower = Fraction(root_floor, scale)
    if lower * lower == value:
        return lower, lower
    return lower, Fraction(root_floor + 1, scale)


def _sqrt_interval(value: Interval, scale: int) -> Interval:
    if value[0] < 0:
        raise ValueError(f"interval radicand crosses the negative axis: {value}")
    return _sqrt_bound(value[0], scale)[0], _sqrt_bound(value[1], scale)[1]


def rational_interval(expression: sp.Expr, decimal_digits: int = 50) -> Interval:
    """Evaluate a real nested-radical expression with exact rational bounds."""

    scale = 10**decimal_digits

    def evaluate(value: sp.Expr) -> Interval:
        if value.is_Rational:
            exact = Fraction(int(sp.numer(value)), int(sp.denom(value)))
            return exact, exact
        if value.is_Add:
            result = (Fraction(0), Fraction(0))
            for term in value.args:
                result = _interval_add(result, evaluate(term))
            return result
        if value.is_Mul:
            result = (Fraction(1), Fraction(1))
            for factor in value.args:
                result = _interval_multiply(result, evaluate(factor))
            return result
        if value.is_Pow and value.exp.is_Rational:
            exponent = sp.Rational(value.exp)
            if exponent.q == 1:
                return _integer_power(evaluate(value.base), int(exponent.p))
            if exponent.q == 2:
                numerator = int(exponent.p)
                if numerator < 0:
                    positive = _sqrt_interval(
                        _integer_power(evaluate(value.base), -numerator), scale
                    )
                    return _integer_power(positive, -1)
                return _sqrt_interval(
                    _integer_power(evaluate(value.base), numerator), scale
                )
        raise TypeError(f"unsupported exact-interval node: {value}")

    if expression.has(sp.I):
        raise ValueError("non-real pairing entered rational interval proof")
    return evaluate(expression)


def certified_nonzero_interval(expression: sp.Expr) -> tuple[Interval, int] | None:
    if expression == 0:
        return None
    for digits in (30, 50, 80, 120):
        interval = rational_interval(expression, digits)
        if interval[0] > 0 or interval[1] < 0:
            return interval, digits
    raise AssertionError(f"failed to isolate pairing away from zero: {expression}")


def fraction_string(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def multinomial(total: int, first: int, second: int) -> int:
    third = total - first - second
    return factorial(total) // (
        factorial(first) * factorial(second) * factorial(third)
    )


@lru_cache(maxsize=1)
def generic_source() -> tuple[tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], sp.Matrix]:
    """Extract the four polar L=4 action rows for arbitrary axial inputs."""

    k_1, omega_1, k_2, omega_2 = sp.symbols(
        "k_1 omega_1 k_2 omega_2", real=True
    )
    first = sp.symbols("a_0:4", real=True)
    second = sp.symbols("b_0:4", real=True)
    row_index = {9: 0, 12: 1, 16: 2, 17: 3}

    def derivative(
        row: int,
        word: tuple[int, ...],
        momentum: sp.Expr,
        frequency: sp.Expr,
        amplitudes: tuple[sp.Symbol, ...],
    ) -> sp.Expr:
        if 3 in word:
            return sp.S.Zero
        return (
            amplitudes[row_index[row]]
            * (-sp.I * frequency) ** word.count(0)
            * (sp.I * momentum) ** word.count(1)
            * angular_derivative(row, word.count(2))
        )

    terms, profiles = load_relevant()
    output: dict[tuple[int, int], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for term in terms:
        row = int(term["output_row"])
        left, right = term["inputs"]
        left_row, right_row = int(left["row"]), int(right["row"])
        left_word, right_word = tuple(left["word"]), tuple(right["word"])
        profile = profiles[int(term["coefficient_profile"])]
        for output_order in OUTPUT_ORDERS[row]:
            value = sp.S.Zero
            for coefficient_order in range(output_order + 1):
                coefficient = profile.get(coefficient_order, sp.S.Zero)
                if coefficient == 0:
                    continue
                for left_extra in range(output_order - coefficient_order + 1):
                    right_extra = output_order - coefficient_order - left_extra
                    value += (
                        multinomial(
                            output_order, coefficient_order, left_extra
                        )
                        * coefficient
                        * derivative(
                            left_row,
                            left_word + (2,) * left_extra,
                            k_1,
                            omega_1,
                            first,
                        )
                        * derivative(
                            right_row,
                            right_word + (2,) * right_extra,
                            k_2,
                            omega_2,
                            second,
                        )
                    )
            output[(row, output_order)] += value
    jets = {
        row: {
            order: sp.factor(sp.expand(output[(row, order)]))
            for order in orders
        }
        for row, orders in OUTPUT_ORDERS.items()
    }
    source = sp.Matrix([
        2 * scalar_l4(jets[20]),
        2 * scalar_l4(jets[21]),
        2 * scalar_l4(jets[24]),
        40 * vector_l4(jets[33]),
    ]).applyfunc(sp.factor)
    return (k_1, omega_1, k_2, omega_2), first, second, source


def build_slice() -> dict[str, object]:
    variables, first, second, source = generic_source()
    value = {
        "schema": "einstein-maxwell-weyl-ell2-axial-axial-L4-q2-slice-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_AXIAL_L4_Q2_SLICE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "parent": {
            "q2_sha256": sha(Q2),
            "row_layout_sha256": sha(ROW_LAYOUT),
            "action_sha256": sha(ACTION),
        },
        "scope": {
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "carrier": "two arbitrary axisymmetric axial ell=2 gauge-slice representatives",
            "degree": 2,
            "parity": "axial times axial input; polar L=4 output",
            "ell": "2 times 2 -> 4",
            "m": "0+0 -> 0",
            "k": "arbitrary signed k_1,k_2",
            "omega": "arbitrary omega_1,omega_2 before shell specialization",
        },
        "variables": [str(value) for value in variables],
        "first_amplitudes_Ht_Hx_Qt_Qx": [str(value) for value in first],
        "second_amplitudes_Ht_Hx_Qt_Qx": [str(value) for value in second],
        "source_action_row_order": [
            "-metric_00",
            "2*metric_01",
            "-metric_11",
            "2*20*maxwell_axial",
        ],
        "source_action_rows": [str(value) for value in source],
        "relevant_q2_terms": 842,
        "claim_boundary": "This exact slice is only the polar L=4 action source from two axial ell=2 inputs. It does not impose a branch shell or classify a correction.",
    }
    return value


def branch_mass(branch: str) -> sp.Expr:
    return {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }[branch]


def axial_basis(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    mass = branch_mass(branch)
    if branch != "p_extra":
        return [sp.Matrix([
            2 * momentum,
            -2 * frequency,
            momentum * (mass - 6),
            -frequency * (mass - 6),
        ])]
    return [
        sp.Matrix([-momentum**2 - 6, momentum * frequency, 6, 0]),
        sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, 6]),
    ]


def target_adjoints(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    if branch == "p_extra":
        return [
            sp.Matrix([
                1,
                -(3 * momentum**2 + 29) / (3 * momentum * frequency),
                1,
                0,
            ]),
            sp.Matrix([
                sp.Rational(4, 3),
                -2 * (momentum**2 + 20) / (3 * momentum * frequency),
                0,
                1,
            ]),
        ]
    mass = 20 + (-1 if branch == "q_minus" else 1) * 2 * sp.sqrt(10)
    return [sp.Matrix([
        -2 * (20 * momentum**2 - mass * momentum**2 - 20),
        2 * momentum * frequency * (20 - mass),
        -2 * (
            20 * momentum**2
            - mass * momentum**2
            + 400
            - 20 * mass
            - 20
        ),
        20,
    ])]


def target_mass(branch: str) -> sp.Expr:
    return {
        "q_minus": 20 - 2 * sp.sqrt(10),
        "p_extra": sp.Rational(58, 3),
        "q_plus": 20 + 2 * sp.sqrt(10),
    }[branch]


def compute() -> dict[str, object]:
    slice_value = build_slice()
    if json.loads(SLICE.read_text()) != slice_value:
        raise AssertionError("stale generic axial-axial L4 q2 slice")
    variables, first_symbols, second_symbols, source = generic_source()
    rows = json.loads(PARITY.read_text())["source_workload"]["rows"]
    records: list[dict[str, object]] = []
    coefficient_count = 0
    basis_fixture_count = 0
    zero_coefficients = 0
    for row in rows:
        if row["output_ell"] != 4:
            continue
        rho = parse(row["rho"])
        signs = row["canonical_signed_momenta"]
        momenta = [signs[0] * sp.sqrt(rho), signs[1] * sp.sqrt(rho)]
        frequencies = [
            sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])),
            sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"])),
        ]
        output_momentum = momenta[0] + momenta[1]
        output_frequency = frequencies[0] + frequencies[1]
        shell_defect = canonical(
            output_frequency**2
            - output_momentum**2
            - target_mass(row["target_branch"])
        )
        if shell_defect != 0:
            raise AssertionError(f"candidate {row['candidate_index']} left target shell")
        first_basis = axial_basis(
            row["first_branch"], momenta[0], frequencies[0]
        )
        second_basis = axial_basis(
            row["second_branch"], momenta[1], frequencies[1]
        )
        adjoints = target_adjoints(
            row["target_branch"], output_momentum, output_frequency
        )
        basis_records = []
        for first_index, first_vector in enumerate(first_basis):
            for second_index, second_vector in enumerate(second_basis):
                # The variable order is k1,w1,k2,w2, not (k1,k2,w1,w2).
                specialized = source.subs(
                    {
                        variables[0]: momenta[0],
                        variables[1]: frequencies[0],
                        variables[2]: momenta[1],
                        variables[3]: frequencies[1],
                        **dict(zip(first_symbols, first_vector, strict=True)),
                        **dict(zip(second_symbols, second_vector, strict=True)),
                    },
                    simultaneous=True,
                )
                pairings = [canonical((adjoint.T * specialized)[0]) for adjoint in adjoints]
                coefficient_count += len(pairings)
                basis_fixture_count += 1
                zero_coefficients += sum(value == 0 for value in pairings)
                intervals = [certified_nonzero_interval(value) for value in pairings]
                nonzero_index = next(
                    (index for index, value in enumerate(intervals) if value is not None),
                    None,
                )
                if nonzero_index is None:
                    raise AssertionError(
                        f"candidate {row['candidate_index']} axial basis fixture lost obstruction"
                    )
                witness_interval, witness_digits = intervals[nonzero_index]
                basis_records.append({
                    "first_basis_index": first_index,
                    "second_basis_index": second_index,
                    "pairings": [str(value) for value in pairings],
                    "nonzero_component": nonzero_index,
                    "pairing_intervals": [
                        None
                        if interval is None
                        else {
                            "lower": fraction_string(interval[0][0]),
                            "upper": fraction_string(interval[0][1]),
                            "decimal_digits": interval[1],
                        }
                        for interval in intervals
                    ],
                    "witness_interval": {
                        "lower": fraction_string(witness_interval[0]),
                        "upper": fraction_string(witness_interval[1]),
                        "decimal_digits": witness_digits,
                        "excludes_zero": True,
                    },
                    "bounded_status": "OBSTRUCTED",
                })
                print(
                    f"candidate {row['candidate_index']} axial basis "
                    f"({first_index},{second_index}): PASS",
                    flush=True,
                )
        records.append({
            "candidate_index": row["candidate_index"],
            "first_branch": row["first_branch"],
            "second_branch": row["second_branch"],
            "target_branch": row["target_branch"],
            "rho": row["rho"],
            "signed_momenta": signs,
            "shell_defect": str(shell_defect),
            "target_cokernel_dimension": len(adjoints),
            "basis_fixtures": basis_records,
        })
    if coefficient_count != 27 or basis_fixture_count != 20:
        raise AssertionError(
            f"axial-axial L4 workload changed: {coefficient_count}/{basis_fixture_count}"
        )
    polar = json.loads(POLAR.read_text())["characteristic_and_module"]
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-axial-axial-L4-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_AXIAL_L4_MATRIX",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_COMPLETE_AXIAL_AXIAL_L4_BASIS_MATRIX",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 at twelve separately tuned algebraic circumference rows",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all axisymmetric axial ell=2 branch-basis cross products between |n|=1 and |n|=2 that resonate at L=4",
            "degree": 2,
            "parity": "axial times axial input; polar output",
            "ell": "2 times 2 -> 4",
            "m": "0+0 -> 0",
            "k": "row-specific signed compact momenta on |n|=1 and |n|=2",
            "omega": "row-specific positive-frequency SUM channel",
        },
        "source_slice": {
            "path": str(SLICE.relative_to(ROOT)),
            "sha256": sha(SLICE),
            "result_id": slice_value["result_id"],
        },
        "polar_primary_completeness": {
            "primary_decomposition": polar["primary_decomposition"],
            "resultant_p_q": polar["resultant_p_q"],
        },
        "candidate_rows": records,
        "matrix_summary": {
            "candidate_rows": len(records),
            "axial_input_basis_fixtures": basis_fixture_count,
            "target_adjoint_coefficients": coefficient_count,
            "zero_target_adjoint_coefficients": zero_coefficients,
            "nonzero_target_adjoint_coefficients": coefficient_count - zero_coefficients,
            "basis_fixtures_with_nonzero_cokernel_vector": basis_fixture_count,
        },
        "second_order_verdict": {
            "bounded_or_finite_quasiperiodic_basis_fixtures": "OBSTRUCTED",
            "smooth_secular_status": "OPEN",
            "causal_retarded_status": "NO_CERTIFIED_MAP",
        },
        "workload_progress": {
            "resolved_axisymmetric_L4_coefficients": 27,
            "remaining_axisymmetric_L4_coefficients": 81,
            "remaining_nonaxisymmetric_L1_L3_coefficients": 56,
            "complete_two_fibre_tangent_cone_classified": False,
        },
        "classification": {
            "complete_axial_axial_L4_basis_matrix_classified": True,
            "all_twenty_basis_fixtures_bounded_obstructed": True,
            "arbitrary_axial_linear_combinations_classified": False,
            "all_axisymmetric_L4_coefficients_classified": False,
            "causal_or_quantum_claim": False,
        },
        "claim_boundary": "This is the complete 27-coefficient axial-axial L4 basis matrix at twelve separate circumference rows. It does not classify cancellations in arbitrary linear combinations, the other 81 axisymmetric coefficients, 56 odd-L coefficients, smooth-secular or causal corrections, the complete tangent cone, residual observables or quantum states.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                "parity_workload": {"path": str(PARITY.relative_to(ROOT)), "sha256": sha(PARITY)},
                "polar_operator": {"path": str(POLAR.relative_to(ROOT)), "sha256": sha(POLAR)},
                "q2": {"path": str(Q2.relative_to(ROOT)), "sha256": sha(Q2)},
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix --recompute-exhaustive",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.py --exhaustive",
        ],
    }


def fast_check() -> None:
    value = json.loads(OUTPUT.read_text())
    if json.loads(SLICE.read_text()) != build_slice():
        raise AssertionError("stale generic axial-axial L4 q2 slice")
    provenance = value["provenance"]
    if provenance["generator_sha256"] != sha(Path(__file__)):
        raise AssertionError("axial-axial L4 generator hash changed")
    for item in provenance["inputs"].values():
        path = ROOT / item["path"]
        if sha(path) != item["sha256"]:
            raise AssertionError(f"stale axial-axial L4 input: {path}")
    summary = value["matrix_summary"]
    if summary != {
        "axial_input_basis_fixtures": 20,
        "basis_fixtures_with_nonzero_cokernel_vector": 20,
        "candidate_rows": 12,
        "nonzero_target_adjoint_coefficients": 26,
        "target_adjoint_coefficients": 27,
        "zero_target_adjoint_coefficients": 1,
    }:
        raise AssertionError(f"axial-axial L4 summary changed: {summary}")
    fixtures = 0
    coefficients = 0
    zeros = 0
    for row in value["candidate_rows"]:
        if row["shell_defect"] != "0":
            raise AssertionError("stored axial-axial L4 row left its target shell")
        for fixture in row["basis_fixtures"]:
            fixtures += 1
            pairings = [parse(item) for item in fixture["pairings"]]
            intervals = fixture["pairing_intervals"]
            coefficients += len(pairings)
            zeros += sum(pairing == 0 for pairing in pairings)
            for pairing, stored in zip(pairings, intervals, strict=True):
                if pairing == 0:
                    if stored is not None:
                        raise AssertionError("zero coefficient acquired a nonzero interval")
                    continue
                if stored is None:
                    raise AssertionError("nonzero coefficient lost its interval")
                actual = rational_interval(pairing, int(stored["decimal_digits"]))
                if [fraction_string(item) for item in actual] != [
                    stored["lower"], stored["upper"]
                ]:
                    raise AssertionError("stored exact rational interval changed")
                if not (actual[0] > 0 or actual[1] < 0):
                    raise AssertionError("stored interval no longer excludes zero")
            witness = intervals[int(fixture["nonzero_component"])]
            if witness is None or not fixture["witness_interval"]["excludes_zero"]:
                raise AssertionError("basis fixture lost its nonzero cokernel witness")
    if (fixtures, coefficients, zeros) != (20, 27, 1):
        raise AssertionError(
            f"stored axial-axial L4 workload changed: {fixtures}/{coefficients}/{zeros}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--recompute-exhaustive", action="store_true")
    args = parser.parse_args()
    if args.write:
        SLICE.write_text(json.dumps(build_slice(), indent=2, sort_keys=True) + "\n")
        value = compute()
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif args.check:
        fast_check()
    elif json.loads(OUTPUT.read_text()) != compute():
        raise AssertionError("stale axial-axial L4 exhaustive certificate")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_AXIAL_L4_MATRIX: PASS")


if __name__ == "__main__":
    main()
