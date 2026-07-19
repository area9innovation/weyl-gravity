"""Compute the ordered axial--polar L=4 cross-|n| source matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from functools import lru_cache
from math import factorial
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    axial_basis,
    branch_mass,
    certified_nonzero_interval,
    fraction_string,
    parse,
    rational_interval,
    target_mass,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import polar_basis
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe import canonical, scalar_l4, vector_l4


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_polar_L4_q2_slice.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
CALIBRATION = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json"
AXIAL_OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"

AXIAL_ROWS = {9, 12, 16, 17}
POLAR_ROWS = {6, 7, 10, 19}
OUTPUT_ORDERS = {23: (1, 3), 26: (1, 3), 30: (0, 2, 4), 31: (0, 2, 4)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def multinomial(total: int, first: int, second: int) -> int:
    third = total - first - second
    return factorial(total) // (factorial(first) * factorial(second) * factorial(third))


theta = sp.symbols("theta", real=True)
Y = sp.legendre(2, sp.cos(theta))
X = -sp.sin(theta) * sp.diff(Y, theta)


@lru_cache(maxsize=None)
def angular_derivative(row: int, order: int) -> sp.Expr:
    function = X if row in (9, 12, 19) else Y
    return sp.simplify(sp.diff(function, theta, order).subs(theta, sp.pi / 2))


@lru_cache(maxsize=1)
def generic_source() -> tuple[tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], sp.Matrix, dict[str, int]]:
    """Extract axial L=4 action rows for an axial first and polar second input."""

    k_1, omega_1, k_2, omega_2 = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    axial = sp.symbols("a_0:4", real=True)
    polar = sp.symbols("b_0:4", real=True)
    axial_index = {9: 0, 12: 1, 16: 2, 17: 3}
    polar_index = {6: 0, 7: 1, 10: 2, 19: 3}

    content = json.loads(Q2.read_text())["content"]
    profiles = []
    for profile in content["coefficient_profiles"]:
        values = {}
        for item in profile["coefficient_jets"]:
            if any(axis != 2 for axis in item["word"]):
                raise AssertionError(f"non-theta coefficient jet: {item['word']}")
            values[len(item["word"])] = sp.Rational(item["coefficient"])
        profiles.append(values)

    terms = []
    counts = {"axial_then_polar": 0, "polar_then_axial": 0}
    for term in content["terms"]:
        if term["output_row"] not in OUTPUT_ORDERS:
            continue
        left, right = term["inputs"][0]["row"], term["inputs"][1]["row"]
        if left in AXIAL_ROWS and right in POLAR_ROWS:
            counts["axial_then_polar"] += 1
            terms.append((term, "axial", "polar"))
        elif left in POLAR_ROWS and right in AXIAL_ROWS:
            counts["polar_then_axial"] += 1
            terms.append((term, "polar", "axial"))
    if counts != {"axial_then_polar": 832, "polar_then_axial": 832}:
        raise AssertionError(f"axial--polar q2 support changed: {counts}")

    def derivative(row: int, word: tuple[int, ...], kind: str) -> sp.Expr:
        if 3 in word:
            return sp.S.Zero
        if kind == "axial":
            amplitude, momentum, frequency = axial[axial_index[row]], k_1, omega_1
        else:
            amplitude, momentum, frequency = polar[polar_index[row]], k_2, omega_2
        return amplitude * (-sp.I * frequency) ** word.count(0) * (sp.I * momentum) ** word.count(1) * angular_derivative(row, word.count(2))

    output: dict[tuple[int, int], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for term, left_kind, right_kind in terms:
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
                    value += multinomial(output_order, coefficient_order, left_extra) * coefficient * derivative(left_row, left_word + (2,) * left_extra, left_kind) * derivative(right_row, right_word + (2,) * right_extra, right_kind)
            output[(row, output_order)] += value
    jets = {row: {order: sp.factor(sp.expand(output[(row, order)])) for order in orders} for row, orders in OUTPUT_ORDERS.items()}
    source = sp.Matrix([
        10 * vector_l4(jets[23]),
        10 * vector_l4(jets[26]),
        sp.Rational(1, 2) * scalar_l4(jets[30]),
        sp.Rational(1, 2) * scalar_l4(jets[31]),
    ]).applyfunc(sp.factor)
    return (k_1, omega_1, k_2, omega_2), axial, polar, source, counts


def build_slice() -> dict[str, object]:
    variables, axial, polar, source, counts = generic_source()
    return {
        "schema": "einstein-maxwell-weyl-ell2-axial-polar-L4-q2-slice-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_POLAR_L4_Q2_SLICE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "parent": {"q2_sha256": sha(Q2), "row_layout_sha256": sha(ROW_LAYOUT), "action_sha256": sha(ACTION)},
        "scope": {"background": "compact magnetically supported Plebanski-Hacyan product", "carrier": "ordered arbitrary axisymmetric axial then polar ell=2 gauge-slice representatives", "degree": 2, "parity": "axial times polar input; axial L=4 output", "ell": "2 times 2 -> 4", "m": "0+0 -> 0", "k": "arbitrary signed k_1,k_2", "omega": "arbitrary omega_1,omega_2 before shell specialization"},
        "pbw_support": {"axial_input_rows": sorted(AXIAL_ROWS), "polar_input_rows": sorted(POLAR_ROWS), "output_rows": list(OUTPUT_ORDERS), "ordered_term_counts": counts, "both_input_orders_included": True},
        "variables": [str(value) for value in variables],
        "axial_amplitudes_Ht_Hx_Qt_Qx": [str(value) for value in axial],
        "polar_amplitudes_At_B_Ct_U": [str(value) for value in polar],
        "source_action_row_order": ["20*metric_t/2", "-(-20*metric_x)/2", "maxwell_t/2", "maxwell_x/2"],
        "source_action_rows": [str(value) for value in source],
        "normalization": "diag(10,10,1/2,1/2) on raw projected PBW rows; fixed by the independent direct four-dimensional axial-plus-polar-minus fixture",
        "claim_boundary": "This exact slice is only the axial L=4 action source from an ordered axial/polar input pair. It does not impose branch shells or classify a correction."
    }


def target_adjoints(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    if branch == "p_extra":
        return [sp.Matrix([-momentum**2 - 20, momentum * frequency, 20, 0]), sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, 20])]
    mu = target_mass(branch)
    return [sp.Matrix([2 * momentum, -2 * frequency, momentum * (mu - 20), -frequency * (mu - 20)])]


def direct_calibration(source: sp.Matrix, variables: tuple[sp.Symbol, ...], axial_symbols: tuple[sp.Symbol, ...], polar_symbols: tuple[sp.Symbol, ...]) -> dict[str, object]:
    k = sp.sqrt(2 * sp.sqrt(3) - sp.Rational(7, 6))
    w = sp.sqrt(sp.Rational(29, 6))
    specialized = source.subs({variables[0]: k, variables[1]: w, variables[2]: -k, variables[3]: w, **dict(zip(axial_symbols, axial_basis("q_minus", k, w)[0], strict=True)), **dict(zip(polar_symbols, polar_basis("q_minus", -k, w)[0], strict=True))}, simultaneous=True).applyfunc(canonical)
    ledger = json.loads(CALIBRATION.read_text())["direct_source_ledger"]["axial_plus_polar_minus"]
    expected = sp.Matrix([parse(value) for value in ledger["source_rows"]])
    remainder = (specialized - expected).applyfunc(canonical)
    if remainder != sp.zeros(4, 1):
        raise AssertionError(f"axial--polar direct calibration failed: {remainder}")
    return {"certificate_path": str(CALIBRATION.relative_to(ROOT)), "certificate_sha256": sha(CALIBRATION), "specialized_source_rows": [str(value) for value in specialized], "generic_slice_minus_direct_source": [str(value) for value in remainder], "exact_match": True}


def compute() -> dict[str, object]:
    slice_value = build_slice()
    if json.loads(SLICE.read_text()) != slice_value:
        raise AssertionError("stale generic axial--polar L4 q2 slice")
    variables, axial_symbols, polar_symbols, source, _ = generic_source()
    calibration = direct_calibration(source, variables, axial_symbols, polar_symbols)
    rows = json.loads(PARITY.read_text())["source_workload"]["rows"]
    records = []
    coefficients = fixtures = zeros = obstructed = 0
    for row in rows:
        if row["output_ell"] != 4:
            continue
        rho = parse(row["rho"])
        signs = row["canonical_signed_momenta"]
        momenta = [signs[0] * sp.sqrt(rho), signs[1] * sp.sqrt(rho)]
        frequencies = [sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])), sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"]))]
        K, Omega = sum(momenta), sum(frequencies)
        shell_defect = canonical(Omega**2 - K**2 - target_mass(row["target_branch"]))
        if shell_defect != 0:
            raise AssertionError(f"candidate {row['candidate_index']} left target shell")
        first_basis = axial_basis(row["first_branch"], momenta[0], frequencies[0])
        second_basis = polar_basis(row["second_branch"], momenta[1], frequencies[1])
        adjoints = target_adjoints(row["target_branch"], K, Omega)
        basis_records = []
        for first_index, first_vector in enumerate(first_basis):
            for second_index, second_vector in enumerate(second_basis):
                specialized = source.subs({variables[0]: momenta[0], variables[1]: frequencies[0], variables[2]: momenta[1], variables[3]: frequencies[1], **dict(zip(axial_symbols, first_vector, strict=True)), **dict(zip(polar_symbols, second_vector, strict=True))}, simultaneous=True)
                pairings = [canonical((adjoint.T * specialized)[0]) for adjoint in adjoints]
                intervals = [certified_nonzero_interval(value) for value in pairings]
                nonzero = next((index for index, value in enumerate(intervals) if value is not None), None)
                status = "OBSTRUCTED" if nonzero is not None else "OPEN"
                coefficients += len(pairings); fixtures += 1; zeros += sum(value == 0 for value in pairings); obstructed += status == "OBSTRUCTED"
                basis_records.append({"first_basis_index": first_index, "second_basis_index": second_index, "pairings": [str(value) for value in pairings], "nonzero_component": nonzero, "pairing_intervals": [None if interval is None else {"lower": fraction_string(interval[0][0]), "upper": fraction_string(interval[0][1]), "decimal_digits": interval[1]} for interval in intervals], "bounded_status": status})
                print(f"candidate {row['candidate_index']} axial-polar basis ({first_index},{second_index}): {status}", flush=True)
        records.append({"candidate_index": row["candidate_index"], "first_branch": row["first_branch"], "second_branch": row["second_branch"], "target_branch": row["target_branch"], "rho": row["rho"], "signed_momenta": signs, "shell_defect": str(shell_defect), "target_cokernel_dimension": len(adjoints), "basis_fixtures": basis_records})
    if (coefficients, fixtures) != (27, 20):
        raise AssertionError(f"axial--polar L4 workload changed: {coefficients}/{fixtures}")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-axial-polar-L4-matrix-v1", "schema_path": str(SCHEMA.relative_to(ROOT)), "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_POLAR_L4_MATRIX", "lifecycle_state": "CLASSIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"], "generality_level": "G2_COMPLETE_ORDERED_AXIAL_POLAR_L4_BASIS_MATRIX",
        "scope": {"theory": "Weyl-Maxwell target", "background": "compact magnetically supported Plebanski-Hacyan product", "boundaries": "closed S1_L times S2 at twelve separately tuned algebraic circumference rows", "charge_sector": "fixed N=2 magnetic bundle", "carrier": "all ordered axisymmetric axial-first polar-second ell=2 branch-basis cross products between |n|=1 and |n|=2 resonating at L=4", "degree": 2, "parity": "axial then polar input; axial output", "ell": "2 times 2 -> 4", "m": "0+0 -> 0", "k": "row-specific signed compact momenta", "omega": "row-specific positive-frequency SUM channel"},
        "source_slice": {"path": str(SLICE.relative_to(ROOT)), "sha256": sha(SLICE), "result_id": slice_value["result_id"]}, "direct_calibration": calibration, "candidate_rows": records,
        "matrix_summary": {"candidate_rows": len(records), "ordered_input_basis_fixtures": fixtures, "target_adjoint_coefficients": coefficients, "zero_target_adjoint_coefficients": zeros, "nonzero_target_adjoint_coefficients": coefficients - zeros, "basis_fixtures_with_nonzero_cokernel_vector": obstructed, "basis_fixtures_without_this_resonant_witness": fixtures - obstructed},
        "second_order_verdict": {"basis_fixture_statuses": "OBSTRUCTED_OR_OPEN_AS_LISTED", "smooth_secular_status": "OPEN", "causal_retarded_status": "NO_CERTIFIED_MAP"},
        "workload_progress": {"resolved_axisymmetric_L4_coefficients": 81, "remaining_axisymmetric_L4_coefficients": 27, "remaining_nonaxisymmetric_L1_L3_coefficients": 56, "complete_two_fibre_tangent_cone_classified": False},
        "classification": {"complete_ordered_axial_polar_L4_basis_matrix_classified": True, "all_twenty_basis_fixtures_bounded_obstructed": obstructed == fixtures, "reverse_input_order_matrix_classified": False, "arbitrary_cross_parity_linear_combinations_classified": False, "all_axisymmetric_L4_coefficients_classified": False, "causal_or_quantum_claim": False},
        "claim_boundary": "This is the complete ordered axial-first/polar-second 27-coefficient L4 basis matrix at twelve separate circumference rows. A zero complete pairing vector leaves a fixture OPEN. Reverse input ordering, arbitrary linear combinations, 56 odd-L coefficients, smooth-secular and causal corrections, the complete tangent cone, residual observables and quantum states remain fail-closed.",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": sha(Path(__file__)), "inputs": {"parity_workload": {"path": str(PARITY.relative_to(ROOT)), "sha256": sha(PARITY)}, "axial_operator": {"path": str(AXIAL_OPERATOR.relative_to(ROOT)), "sha256": sha(AXIAL_OPERATOR)}, "q2": {"path": str(Q2.relative_to(ROOT)), "sha256": sha(Q2)}, "direct_calibration": {"path": str(CALIBRATION.relative_to(ROOT)), "sha256": sha(CALIBRATION)}}},
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix", "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix --recompute-exhaustive"]
    }


def fast_check() -> None:
    value = json.loads(OUTPUT.read_text())
    if json.loads(SLICE.read_text()) != build_slice(): raise AssertionError("stale axial--polar L4 slice")
    if value["provenance"]["generator_sha256"] != sha(Path(__file__)): raise AssertionError("axial--polar generator hash changed")
    for item in value["provenance"]["inputs"].values():
        if sha(ROOT / item["path"]) != item["sha256"]: raise AssertionError(f"stale input {item['path']}")
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        if row["shell_defect"] != "0": raise AssertionError("stored row left shell")
        for fixture in row["basis_fixtures"]:
            fixtures += 1; pairings = [parse(item) for item in fixture["pairings"]]; coefficients += len(pairings)
            for pairing, stored in zip(pairings, fixture["pairing_intervals"], strict=True):
                if pairing == 0: zeros += 1; assert stored is None
                else:
                    assert stored is not None; interval = rational_interval(pairing, int(stored["decimal_digits"])); assert [fraction_string(x) for x in interval] == [stored["lower"], stored["upper"]]; assert interval[0] > 0 or interval[1] < 0
            obstructed += fixture["bounded_status"] == "OBSTRUCTED"
    summary = value["matrix_summary"]
    if (fixtures, coefficients, zeros, obstructed) != (summary["ordered_input_basis_fixtures"], summary["target_adjoint_coefficients"], summary["zero_target_adjoint_coefficients"], summary["basis_fixtures_with_nonzero_cokernel_vector"]): raise AssertionError("stored summary changed")


def main() -> None:
    parser = argparse.ArgumentParser(); group = parser.add_mutually_exclusive_group(required=True); group.add_argument("--write", action="store_true"); group.add_argument("--check", action="store_true"); group.add_argument("--recompute-exhaustive", action="store_true"); args = parser.parse_args()
    if args.write: SLICE.write_text(json.dumps(build_slice(), indent=2, sort_keys=True) + "\n"); OUTPUT.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    elif args.check: fast_check()
    elif json.loads(OUTPUT.read_text()) != compute(): raise AssertionError("stale exhaustive axial--polar certificate")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_POLAR_L4_MATRIX: PASS")


if __name__ == "__main__": main()
