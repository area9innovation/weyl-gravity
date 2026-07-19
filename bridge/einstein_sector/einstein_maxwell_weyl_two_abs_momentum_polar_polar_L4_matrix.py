"""Compute the complete polar--polar L=4 cross-|n| source matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from functools import lru_cache
from math import factorial
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    branch_mass,
    certified_nonzero_interval,
    fraction_string,
    parse,
    target_adjoints,
    target_mass,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe import (
    OUTPUT_ORDERS,
    canonical,
    scalar_l4,
    vector_l4,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_polar_polar_L4_q2_slice.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
POLAR = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json"
CALIBRATION = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json"
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"
SUPPORTED_INPUTS = {6, 7, 10, 19}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def multinomial(total: int, first: int, second: int) -> int:
    third = total - first - second
    return factorial(total) // (
        factorial(first) * factorial(second) * factorial(third)
    )


theta = sp.symbols("theta", real=True)
Y = sp.legendre(2, sp.cos(theta))
X = -sp.sin(theta) * sp.diff(Y, theta)


@lru_cache(maxsize=None)
def angular_derivative(row: int, order: int) -> sp.Expr:
    function = X if row == 19 else Y
    return sp.simplify(sp.diff(function, theta, order).subs(theta, sp.pi / 2))


@lru_cache(maxsize=1)
def generic_source() -> tuple[tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], sp.Matrix, int]:
    """Extract the four polar L=4 action rows for arbitrary polar inputs."""

    k_1, omega_1, k_2, omega_2 = sp.symbols(
        "k_1 omega_1 k_2 omega_2", real=True
    )
    first = sp.symbols("a_0:4", real=True)
    second = sp.symbols("b_0:4", real=True)
    row_index = {6: 0, 7: 1, 10: 2, 19: 3}
    content = json.loads(Q2.read_text())["content"]
    profiles: list[dict[int, sp.Expr]] = []
    for profile in content["coefficient_profiles"]:
        values: dict[int, sp.Expr] = {}
        for item in profile["coefficient_jets"]:
            word = item["word"]
            if any(axis != 2 for axis in word):
                raise AssertionError(f"non-theta coefficient jet: {word}")
            values[len(word)] = sp.Rational(item["coefficient"])
        profiles.append(values)
    terms = [
        term
        for term in content["terms"]
        if term["output_row"] in OUTPUT_ORDERS
        and term["inputs"][0]["row"] in SUPPORTED_INPUTS
        and term["inputs"][1]["row"] in SUPPORTED_INPUTS
    ]
    if len(terms) != 1576:
        raise AssertionError(f"polar--polar q2 support changed: {len(terms)}")

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
                        multinomial(output_order, coefficient_order, left_extra)
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
    source = sp.Matrix(
        [
            2 * scalar_l4(jets[20]),
            2 * scalar_l4(jets[21]),
            2 * scalar_l4(jets[24]),
            40 * vector_l4(jets[33]),
        ]
    ).applyfunc(sp.factor)
    return (k_1, omega_1, k_2, omega_2), first, second, source, len(terms)


def build_slice() -> dict[str, object]:
    variables, first, second, source, term_count = generic_source()
    return {
        "schema": "einstein-maxwell-weyl-ell2-polar-polar-L4-q2-slice-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_POLAR_POLAR_L4_Q2_SLICE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "parent": {
            "q2_sha256": sha(Q2),
            "row_layout_sha256": sha(ROW_LAYOUT),
            "action_sha256": sha(ACTION),
        },
        "scope": {
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "carrier": "two arbitrary axisymmetric polar ell=2 gauge-slice representatives",
            "degree": 2,
            "parity": "polar times polar input; polar L=4 output",
            "ell": "2 times 2 -> 4",
            "m": "0+0 -> 0",
            "k": "arbitrary signed k_1,k_2",
            "omega": "arbitrary omega_1,omega_2 before shell specialization",
        },
        "variables": [str(value) for value in variables],
        "first_amplitudes_At_B_Ct_U": [str(value) for value in first],
        "second_amplitudes_At_B_Ct_U": [str(value) for value in second],
        "source_action_row_order": [
            "-metric_00",
            "2*metric_01",
            "-metric_11",
            "2*20*maxwell_axial",
        ],
        "source_action_rows": [str(value) for value in source],
        "relevant_q2_terms": term_count,
        "claim_boundary": "This exact slice is only the polar L=4 action source from two polar ell=2 inputs. It does not impose a branch shell or classify a correction.",
    }


def polar_basis(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    if branch == "p_extra":
        return [
            sp.Matrix(
                [
                    1,
                    -(3 * momentum**2 + 8) / (3 * momentum * frequency),
                    1,
                    0,
                ]
            ),
            sp.Matrix(
                [
                    sp.Rational(4, 3),
                    -2 * (momentum**2 + 6) / (3 * momentum * frequency),
                    0,
                    1,
                ]
            ),
        ]
    mass = branch_mass(branch)
    maxwell = sp.Integer(6)
    sphere_trace = -12 * maxwell / (mass - 6)
    reconstruction = sphere_trace - 2 * maxwell
    common = -(frequency**2 + momentum**2) * reconstruction / mass
    mixed = 2 * momentum * frequency * reconstruction / mass
    return [
        sp.Matrix(
            [
                common + sphere_trace,
                mixed,
                common - sphere_trace,
                maxwell,
            ]
        ).applyfunc(sp.factor)
    ]


def validate_input_basis(
    branch: str,
    momentum: sp.Expr,
    frequency: sp.Expr,
    basis: list[sp.Matrix],
) -> None:
    action, (eigenvalue, target_momentum, target_frequency) = _action_operator()
    block = action.subs(
        {
            eigenvalue: 6,
            target_momentum: momentum,
            target_frequency: frequency,
        }
    )
    for vector in basis:
        defect = (block * vector).applyfunc(canonical)
        if defect != sp.zeros(4, 1):
            raise AssertionError(f"polar {branch} representative left its shell: {defect}")


def calibration() -> dict[str, object]:
    variables, first, second, source, _ = generic_source()
    momentum = sp.sqrt(2 * sp.sqrt(3) - sp.Rational(7, 6))
    frequency = sp.sqrt(sp.Rational(29, 6))
    first_vector = polar_basis("q_minus", momentum, frequency)[0]
    second_vector = polar_basis("q_minus", -momentum, frequency)[0]
    specialized = source.subs(
        {
            variables[0]: momentum,
            variables[1]: frequency,
            variables[2]: -momentum,
            variables[3]: frequency,
            **dict(zip(first, first_vector, strict=True)),
            **dict(zip(second, second_vector, strict=True)),
        },
        simultaneous=True,
    ).applyfunc(canonical)
    expected = sp.Matrix(
        [
            parse(value)
            for value in json.loads(CALIBRATION.read_text())["direct_source_ledger"]
            ["polar_polar"]["source_rows"]
        ]
    )
    if (specialized - expected).applyfunc(canonical) != sp.zeros(4, 1):
        raise AssertionError("generic polar--polar q2 slice lost its direct calibration")
    return {
        "certificate_path": str(CALIBRATION.relative_to(ROOT)),
        "certificate_sha256": sha(CALIBRATION),
        "specialized_source_rows": [str(value) for value in specialized],
        "matches_direct_four_dimensional_source": True,
    }


def compute() -> dict[str, object]:
    slice_value = build_slice()
    if json.loads(SLICE.read_text()) != slice_value:
        raise AssertionError("stale generic polar--polar L4 q2 slice")
    calibration_value = calibration()
    variables, first_symbols, second_symbols, source, _ = generic_source()
    rows = json.loads(PARITY.read_text())["source_workload"]["rows"]
    records: list[dict[str, object]] = []
    coefficient_count = fixture_count = zero_coefficients = 0
    obstructed_fixtures = 0
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
        first_basis = polar_basis(
            row["first_branch"], momenta[0], frequencies[0]
        )
        second_basis = polar_basis(
            row["second_branch"], momenta[1], frequencies[1]
        )
        validate_input_basis(
            row["first_branch"], momenta[0], frequencies[0], first_basis
        )
        validate_input_basis(
            row["second_branch"], momenta[1], frequencies[1], second_basis
        )
        adjoints = target_adjoints(
            row["target_branch"], output_momentum, output_frequency
        )
        basis_records = []
        for first_index, first_vector in enumerate(first_basis):
            for second_index, second_vector in enumerate(second_basis):
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
                pairings = [
                    canonical((adjoint.T * specialized)[0]) for adjoint in adjoints
                ]
                intervals = [certified_nonzero_interval(value) for value in pairings]
                nonzero_index = next(
                    (index for index, value in enumerate(intervals) if value is not None),
                    None,
                )
                status = "OBSTRUCTED" if nonzero_index is not None else "OPEN"
                coefficient_count += len(pairings)
                fixture_count += 1
                zero_coefficients += sum(value == 0 for value in pairings)
                obstructed_fixtures += status == "OBSTRUCTED"
                basis_records.append(
                    {
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
                        "bounded_status": status,
                    }
                )
                print(
                    f"candidate {row['candidate_index']} polar basis "
                    f"({first_index},{second_index}): {status}",
                    flush=True,
                )
        records.append(
            {
                "candidate_index": row["candidate_index"],
                "first_branch": row["first_branch"],
                "second_branch": row["second_branch"],
                "target_branch": row["target_branch"],
                "rho": row["rho"],
                "signed_momenta": signs,
                "shell_defect": str(shell_defect),
                "target_cokernel_dimension": len(adjoints),
                "basis_fixtures": basis_records,
            }
        )
    if (coefficient_count, fixture_count) != (27, 20):
        raise AssertionError(
            f"polar--polar L4 workload changed: {coefficient_count}/{fixture_count}"
        )
    completion = json.loads(POLAR.read_text())
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-polar-polar-L4-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_POLAR_POLAR_L4_MATRIX",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_COMPLETE_POLAR_POLAR_L4_BASIS_MATRIX",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 at twelve separately tuned algebraic circumference rows",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all axisymmetric polar ell=2 branch-basis cross products between |n|=1 and |n|=2 that resonate at L=4",
            "degree": 2,
            "parity": "polar times polar input; polar output",
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
        "direct_calibration": calibration_value,
        "polar_primary_completeness": {
            "primary_decomposition": completion["Einstein_primary_image"]
            ["target_physical_fiber_primary_decomposition"],
            "resultant_p_q": completion["Einstein_primary_image"]["p_q_resultant"],
        },
        "candidate_rows": records,
        "matrix_summary": {
            "candidate_rows": len(records),
            "polar_input_basis_fixtures": fixture_count,
            "target_adjoint_coefficients": coefficient_count,
            "zero_target_adjoint_coefficients": zero_coefficients,
            "nonzero_target_adjoint_coefficients": coefficient_count
            - zero_coefficients,
            "basis_fixtures_with_nonzero_cokernel_vector": obstructed_fixtures,
            "basis_fixtures_without_this_resonant_witness": fixture_count
            - obstructed_fixtures,
        },
        "second_order_verdict": {
            "basis_fixture_statuses": "OBSTRUCTED_OR_OPEN_AS_LISTED",
            "smooth_secular_status": "OPEN",
            "causal_retarded_status": "NO_CERTIFIED_MAP",
        },
        "workload_progress": {
            "resolved_axisymmetric_L4_coefficients": 54,
            "remaining_axisymmetric_L4_coefficients": 54,
            "remaining_nonaxisymmetric_L1_L3_coefficients": 56,
            "complete_two_fibre_tangent_cone_classified": False,
        },
        "classification": {
            "complete_polar_polar_L4_basis_matrix_classified": True,
            "all_twenty_basis_fixtures_bounded_obstructed": obstructed_fixtures
            == fixture_count,
            "arbitrary_polar_linear_combinations_classified": False,
            "all_axisymmetric_L4_coefficients_classified": False,
            "causal_or_quantum_claim": False,
        },
        "claim_boundary": "This is the complete 27-coefficient polar--polar L4 basis matrix at twelve separate circumference rows. A zero complete pairing vector leaves that fixture OPEN rather than proving extension. Arbitrary linear combinations, both ordered cross-parity matrices, 56 odd-L coefficients, smooth-secular or causal corrections, the complete tangent cone, residual observables and quantum states remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                "parity_workload": {
                    "path": str(PARITY.relative_to(ROOT)),
                    "sha256": sha(PARITY),
                },
                "polar_completion": {
                    "path": str(POLAR.relative_to(ROOT)),
                    "sha256": sha(POLAR),
                },
                "calibration": {
                    "path": str(CALIBRATION.relative_to(ROOT)),
                    "sha256": sha(CALIBRATION),
                },
                "q2": {"path": str(Q2.relative_to(ROOT)), "sha256": sha(Q2)},
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix --recompute-exhaustive",
        ],
    }


def fast_check() -> None:
    value = json.loads(OUTPUT.read_text())
    if json.loads(SLICE.read_text()) != build_slice():
        raise AssertionError("stale generic polar--polar L4 q2 slice")
    if value["provenance"]["generator_sha256"] != sha(Path(__file__)):
        raise AssertionError("polar--polar L4 generator hash changed")
    for item in value["provenance"]["inputs"].values():
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise AssertionError(f"stale polar--polar L4 input: {item['path']}")
    summary = value["matrix_summary"]
    if (
        summary["candidate_rows"],
        summary["polar_input_basis_fixtures"],
        summary["target_adjoint_coefficients"],
    ) != (12, 20, 27):
        raise AssertionError(f"polar--polar L4 summary changed: {summary}")
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        if row["shell_defect"] != "0":
            raise AssertionError("stored polar--polar L4 row left its target shell")
        for fixture in row["basis_fixtures"]:
            fixtures += 1
            pairings = [parse(item) for item in fixture["pairings"]]
            intervals = fixture["pairing_intervals"]
            coefficients += len(pairings)
            zeros += sum(pairing == 0 for pairing in pairings)
            has_witness = False
            for pairing, stored in zip(pairings, intervals, strict=True):
                if pairing == 0:
                    if stored is not None:
                        raise AssertionError("zero coefficient acquired an interval")
                    continue
                if stored is None:
                    raise AssertionError("nonzero coefficient lost its interval")
                actual = certified_nonzero_interval(pairing)
                if actual is None:
                    raise AssertionError("stored nonzero coefficient vanished")
                if [fraction_string(item) for item in actual[0]] != [
                    stored["lower"],
                    stored["upper"],
                ]:
                    raise AssertionError("stored polar interval changed")
                has_witness = True
            expected_status = "OBSTRUCTED" if has_witness else "OPEN"
            if fixture["bounded_status"] != expected_status:
                raise AssertionError("polar basis-fixture verdict changed")
            obstructed += has_witness
    if (fixtures, coefficients, zeros, obstructed) != (
        20,
        27,
        summary["zero_target_adjoint_coefficients"],
        summary["basis_fixtures_with_nonzero_cokernel_vector"],
    ):
        raise AssertionError("stored polar--polar L4 counts changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--recompute-exhaustive", action="store_true")
    args = parser.parse_args()
    if args.write:
        SLICE.write_text(json.dumps(build_slice(), indent=2, sort_keys=True) + "\n")
        OUTPUT.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    elif args.check:
        fast_check()
    elif json.loads(OUTPUT.read_text()) != compute():
        raise AssertionError("stale polar--polar L4 exhaustive certificate")
    print(
        "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_POLAR_POLAR_L4_MATRIX: PASS"
    )


if __name__ == "__main__":
    main()
