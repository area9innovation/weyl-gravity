"""Compute the complete nonaxisymmetric L=1,3 cross-|n| source workload."""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    axial_basis,
    branch_mass,
    certified_nonzero_interval,
    fraction_string,
    parse,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import polar_basis
from bridge.einstein_sector.nonaxisymmetric_pbw_projector import canonical, reduced_source


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_nonaxisymmetric_L1_L3_q2_slices.json"
PROJECTOR = ROOT / "bridge/einstein_sector/nonaxisymmetric_pbw_projector.py"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"
EXCEPTIONAL = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json"
L3_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.json"
L3_SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_nonaxisymmetric_L3_q2_slice.json"
PARITY_PAIRS = (
    ("axial", "axial"),
    ("polar", "polar"),
    ("axial", "polar"),
    ("polar", "axial"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def generic_slices() -> tuple[
    tuple[sp.Symbol, ...],
    tuple[sp.Symbol, ...],
    tuple[sp.Symbol, ...],
    dict[tuple[str, str, int], sp.Matrix],
]:
    k_1, omega_1, k_2, omega_2 = sp.symbols(
        "k_1 omega_1 k_2 omega_2", real=True
    )
    first = sp.symbols("a_0:4", real=True)
    second = sp.symbols("b_0:4", real=True)
    sources: dict[tuple[str, str, int], sp.Matrix] = {}
    for output_ell in (1, 3):
        for first_parity, second_parity in PARITY_PAIRS:
            sources[(first_parity, second_parity, output_ell)] = reduced_source(
                first_parity,
                second_parity,
                first,
                second,
                k_1,
                omega_1,
                k_2,
                omega_2,
                output_ell,
            ).applyfunc(sp.factor)
    return (k_1, omega_1, k_2, omega_2), first, second, sources


def build_slice() -> dict[str, object]:
    variables, first, second, sources = generic_slices()
    return {
        "schema": "einstein-maxwell-weyl-ell2-nonaxisymmetric-L1-L3-q2-slices-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_NONAXISYMMETRIC_L1_L3_Q2_SLICES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "parent": {
            "q2_sha256": sha(Q2),
            "row_layout_sha256": sha(ROW_LAYOUT),
            "action_sha256": sha(ACTION),
        },
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "Clebsch-Gordan-reduced ordered ell=2 times ell=2 PBW q2 slices",
            "degree": 2,
            "parity": "all four ordered axial/polar input pairs",
            "ell": "2 times 2 -> 1 or 3",
            "m": "normalized all-m coupled tensor, highest-weight output M=L",
            "k": "arbitrary signed k_1,k_2",
            "omega": "arbitrary signed omega_1,omega_2 before shell specialization",
        },
        "variables": [str(value) for value in variables],
        "first_amplitudes": [str(value) for value in first],
        "second_amplitudes": [str(value) for value in second],
        "angular_normalization": "standard normalized complex Y_lm and Clebsch-Gordan coefficients; every stored matrix coefficient carries the common 1/sqrt(pi) normalization",
        "source_action_row_orders": {
            "axial": ["lambda*metric_t/2", "lambda*metric_x/2", "maxwell_t/2", "maxwell_x/2"],
            "polar": ["-2*metric_00", "2*metric_01", "-2*metric_11", "2*lambda*maxwell_axial"],
        },
        "sources": {
            f"{first_parity}_{second_parity}_L{output_ell}": [
                str(value)
                for value in sources[(first_parity, second_parity, output_ell)]
            ]
            for output_ell in (1, 3)
            for first_parity, second_parity in PARITY_PAIRS
        },
        "claim_boundary": "These are reduced action-source tensors before branch, circumference and target-adjoint specialization. They do not classify a correction or an arbitrary-amplitude zero variety.",
    }


def load_slice() -> tuple[
    tuple[sp.Symbol, ...],
    tuple[sp.Symbol, ...],
    tuple[sp.Symbol, ...],
    dict[tuple[str, str, int], sp.Matrix],
]:
    value = json.loads(SLICE.read_text())
    k_1, omega_1, k_2, omega_2 = sp.symbols(
        "k_1 omega_1 k_2 omega_2", real=True
    )
    first = sp.symbols("a_0:4", real=True)
    second = sp.symbols("b_0:4", real=True)
    local = {str(item): item for item in (k_1, omega_1, k_2, omega_2, *first, *second)}
    sources = {
        (first_parity, second_parity, output_ell): sp.Matrix(
            [
                sp.sympify(item, locals={"sqrt": sp.sqrt, "pi": sp.pi, **local})
                for item in value["sources"][f"{first_parity}_{second_parity}_L{output_ell}"]
            ]
        )
        for output_ell in (1, 3)
        for first_parity, second_parity in PARITY_PAIRS
    }
    return (k_1, omega_1, k_2, omega_2), first, second, sources


def input_basis(
    parity: str,
    branch: str,
    momentum: sp.Expr,
    frequency: sp.Expr,
) -> list[sp.Matrix]:
    return (
        axial_basis(branch, momentum, frequency)
        if parity == "axial"
        else polar_basis(branch, momentum, frequency)
    )


def target_mass(output_ell: int, branch: str) -> sp.Expr:
    eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    if output_ell == 1:
        if branch != "extra":
            raise ValueError((output_ell, branch))
        return sp.Rational(4, 3)
    if branch == "p_extra":
        return eigenvalue - sp.Rational(2, 3)
    sign = -1 if branch == "q_minus" else 1
    return eigenvalue + sign * sp.sqrt(2 * eigenvalue)


def axial_target_adjoints(
    output_ell: int,
    branch: str,
    momentum: sp.Expr,
    frequency: sp.Expr,
) -> list[sp.Matrix]:
    if output_ell == 1:
        return [
            sp.Matrix(
                [
                    0,
                    1,
                    sp.Rational(3, 2) * momentum * frequency,
                    -sp.Rational(3, 2) * (momentum**2 + 2),
                ]
            )
        ]
    eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    mass = target_mass(output_ell, branch)
    if branch == "p_extra":
        return [
            sp.Matrix([-momentum**2 - eigenvalue, momentum * frequency, eigenvalue, 0]),
            sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, eigenvalue]),
        ]
    return [
        sp.Matrix(
            [
                2 * momentum,
                -2 * frequency,
                momentum * (mass - eigenvalue),
                -frequency * (mass - eigenvalue),
            ]
        )
    ]


def polar_target_adjoints(
    output_ell: int,
    branch: str,
    momentum: sp.Expr,
    frequency: sp.Expr,
) -> list[sp.Matrix]:
    if output_ell == 1:
        return [
            sp.Matrix(
                [
                    -momentum * (3 * momentum**2 + 4),
                    frequency * (3 * momentum**2 + 2),
                    -momentum * (3 * momentum**2 + 4),
                    0,
                ]
            )
        ]
    eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    mass = target_mass(output_ell, branch)
    if branch == "p_extra":
        return [
            sp.Matrix(
                [
                    1,
                    -(3 * momentum**2 + sp.Rational(3, 2) * eigenvalue - 1)
                    / (3 * momentum * frequency),
                    1,
                    0,
                ]
            ),
            sp.Matrix(
                [
                    sp.Rational(4, 3),
                    -2 * (momentum**2 + eigenvalue) / (3 * momentum * frequency),
                    0,
                    1,
                ]
            ),
        ]
    return [
        sp.Matrix(
            [
                -2 * (eigenvalue * momentum**2 - mass * momentum**2 - eigenvalue),
                2 * momentum * frequency * (eigenvalue - mass),
                -2
                * (
                    eigenvalue * momentum**2
                    - mass * momentum**2
                    + eigenvalue**2
                    - eigenvalue * mass
                    - eigenvalue
                ),
                eigenvalue,
            ]
        )
    ]


def target_adjoints(
    parity: str,
    output_ell: int,
    branch: str,
    momentum: sp.Expr,
    frequency: sp.Expr,
) -> list[sp.Matrix]:
    return (
        axial_target_adjoints(output_ell, branch, momentum, frequency)
        if parity == "axial"
        else polar_target_adjoints(output_ell, branch, momentum, frequency)
    )


def real_scaled_pairing(value: sp.Expr) -> tuple[sp.Expr, str]:
    scaled = canonical(sp.sqrt(sp.pi) * value)
    if scaled.has(sp.I):
        scaled = canonical(-sp.I * scaled)
        phase = "-i*sqrt(pi)"
    else:
        phase = "sqrt(pi)"
    if scaled.has(sp.I) or scaled.has(sp.pi):
        raise AssertionError(f"pairing did not reduce to a real algebraic number: {scaled}")
    return scaled, phase


def verify_certified_l3_submatrix(
    sources: dict[tuple[str, str, int], sp.Matrix],
) -> None:
    certified = json.loads(L3_SLICE.read_text())["source_action_rows"]
    variables, first, second, _ = load_slice()
    local = {str(item): item for item in (*variables, *first, *second)}
    for first_parity, second_parity in PARITY_PAIRS:
        expected = sp.Matrix(
            [
                sp.sympify(item, locals={"sqrt": sp.sqrt, **local})
                for item in certified[f"{first_parity}_{second_parity}"]
            ]
        )
        remainder = (
            sp.sqrt(sp.pi) * sources[(first_parity, second_parity, 3)] - expected
        ).applyfunc(canonical)
        if remainder != sp.zeros(4, 1):
            raise AssertionError(
                f"{first_parity}-{second_parity} L3 slice disagrees with certified submatrix"
            )


def compute() -> dict[str, object]:
    variables, first_symbols, second_symbols, sources = load_slice()
    workload = json.loads(PARITY.read_text())["source_workload"]["rows"]
    exceptional = json.loads(EXCEPTIONAL.read_text())
    if not exceptional["classification"]["nonzero_k_exceptional_solution_cofiber_certified"]:
        raise AssertionError("exceptional nonzero-k target input changed")
    l3_certificate = json.loads(L3_CERTIFICATE.read_text())
    if not l3_certificate["classification"]["all_44_L3_adjoint_coefficients_classified"]:
        raise AssertionError("certified L3 submatrix changed")
    verify_certified_l3_submatrix(sources)
    records: list[dict[str, object]] = []
    coefficients = fixtures = zeros = obstructed = 0
    for row in workload:
        output_ell = int(row["output_ell"])
        if output_ell not in (1, 3):
            continue
        rho = parse(row["rho"])
        signs = row["canonical_signed_momenta"]
        momenta = [sp.Integer(signs[0]) * sp.sqrt(rho), sp.Integer(signs[1]) * sp.sqrt(rho)]
        positive_frequencies = [
            sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])),
            sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"])),
        ]
        temporal_signs = [1, 1 if row["temporal_channel"] == "SUM" else -1]
        frequencies = [
            temporal_signs[index] * positive_frequencies[index]
            for index in range(2)
        ]
        target_momentum = sum(momenta)
        target_frequency = sum(frequencies)
        shell_defect = canonical(
            target_frequency**2
            - target_momentum**2
            - target_mass(output_ell, row["target_branch"])
        )
        if shell_defect != 0:
            raise AssertionError(f"candidate {row['candidate_index']} left its target shell")
        channel_records: list[dict[str, object]] = []
        for channel in row["parity_channels"]:
            first_parity = channel["first_parity"]
            second_parity = channel["second_parity"]
            target_parity = channel["target_parity"]
            first_basis = input_basis(
                first_parity,
                row["first_branch"],
                momenta[0],
                frequencies[0],
            )
            second_basis = input_basis(
                second_parity,
                row["second_branch"],
                momenta[1],
                frequencies[1],
            )
            adjoints = target_adjoints(
                target_parity,
                output_ell,
                row["target_branch"],
                target_momentum,
                target_frequency,
            )
            source = sources[(first_parity, second_parity, output_ell)]
            basis_records: list[dict[str, object]] = []
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
                    pairings: list[sp.Expr] = []
                    phases: list[str] = []
                    intervals: list[tuple[tuple[object, object], int] | None] = []
                    for adjoint in adjoints:
                        pairing, phase = real_scaled_pairing((adjoint.T * specialized)[0])
                        pairings.append(pairing)
                        phases.append(phase)
                        intervals.append(certified_nonzero_interval(pairing))
                    nonzero_component = next(
                        (index for index, value in enumerate(intervals) if value is not None),
                        None,
                    )
                    status = "OBSTRUCTED" if nonzero_component is not None else "OPEN"
                    fixtures += 1
                    coefficients += len(pairings)
                    zeros += sum(value == 0 for value in pairings)
                    obstructed += status == "OBSTRUCTED"
                    basis_records.append(
                        {
                            "first_basis_index": first_index,
                            "second_basis_index": second_index,
                            "scaled_pairings": [str(value) for value in pairings],
                            "phase_normalizations": phases,
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
                            "nonzero_component": nonzero_component,
                            "bounded_status": status,
                        }
                    )
            expected_coefficients = int(channel["reduced_scalar_source_coefficients"])
            actual_coefficients = len(first_basis) * len(second_basis) * len(adjoints)
            if actual_coefficients != expected_coefficients:
                raise AssertionError(
                    f"candidate {row['candidate_index']} {first_parity}-{second_parity} multiplicity changed"
                )
            channel_records.append(
                {
                    "first_parity": first_parity,
                    "second_parity": second_parity,
                    "target_parity": target_parity,
                    "angular_carrier": "normalized all-m Clebsch-Gordan reduced tensor; M=L",
                    "target_cokernel_dimension": len(adjoints),
                    "basis_fixtures": basis_records,
                }
            )
        records.append(
            {
                "candidate_index": row["candidate_index"],
                "first_branch": row["first_branch"],
                "second_branch": row["second_branch"],
                "target_branch": row["target_branch"],
                "output_ell": output_ell,
                "rho": row["rho"],
                "signed_momenta": signs,
                "temporal_channel": row["temporal_channel"],
                "temporal_signs": temporal_signs,
                "shell_defect": str(shell_defect),
                "parity_channels": channel_records,
            }
        )
    if coefficients != 56:
        raise AssertionError(f"nonaxisymmetric workload changed: {coefficients}")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-nonaxisymmetric-L1-L3-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_NONAXISYMMETRIC_L1_L3_MATRIX",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_COMPLETE_NONAXISYMMETRIC_L1_L3_BRANCH_BASIS_MATRIX",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 at the isolated algebraic circumference rows",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all ordered nonaxisymmetric ell=2 branch-basis cross products between |n|=1 and |n|=2",
            "degree": 2,
            "parity": "all four ordered axial/polar input pairs kept separate",
            "ell": "2 times 2 -> 1 or 3",
            "m": "complete reduced SO(3) tensor coefficient, extracted at M=L",
            "k": "row-specific signed compact momenta",
            "omega": "row-specific signed SUM or DIFFERENCE channel",
        },
        "source_slices": {
            "path": str(SLICE.relative_to(ROOT)),
            "sha256": sha(SLICE),
            "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_NONAXISYMMETRIC_L1_L3_Q2_SLICES",
        },
        "candidate_rows": records,
        "matrix_summary": {
            "candidate_rows": len(records),
            "ordered_parity_channels": sum(len(row["parity_channels"]) for row in records),
            "ordered_input_basis_fixtures": fixtures,
            "target_adjoint_coefficients": coefficients,
            "zero_target_adjoint_coefficients": zeros,
            "nonzero_target_adjoint_coefficients": coefficients - zeros,
            "basis_fixtures_with_nonzero_cokernel_vector": obstructed,
            "basis_fixtures_without_this_resonant_witness": fixtures - obstructed,
        },
        "normalization": {
            "stored_pairings": "the physical adjoint pairing multiplied by sqrt(pi), or by -i*sqrt(pi) when the complex harmonic convention makes it imaginary",
            "zero_locus_preserved": True,
            "reason": "the removed phase is fixed and nonzero on each displayed coefficient",
        },
        "classification": {
            "complete_nonaxisymmetric_L1_L3_branch_basis_matrix_classified": True,
            "all_56_odd_L_reduced_coefficients_classified": True,
            "certified_L3_submatrix_replayed": True,
            "all_164_branch_basis_coefficients_classified": True,
            "arbitrary_amplitude_zero_variety_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "claim_boundary": "This closes the 56 reduced odd-L branch-basis coefficients, not cancellations among arbitrary amplitudes or the complete two-fibre tangent cone. Smooth-secular, causal, residual, observational and quantum lifecycles remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                "parity_workload": {"path": str(PARITY.relative_to(ROOT)), "sha256": sha(PARITY)},
                "q2": {"path": str(Q2.relative_to(ROOT)), "sha256": sha(Q2)},
                "row_layout": {"path": str(ROW_LAYOUT.relative_to(ROOT)), "sha256": sha(ROW_LAYOUT)},
                "action": {"path": str(ACTION.relative_to(ROOT)), "sha256": sha(ACTION)},
                "exceptional_nonzero_k": {"path": str(EXCEPTIONAL.relative_to(ROOT)), "sha256": sha(EXCEPTIONAL)},
                "nonaxisymmetric_projector": {"path": str(PROJECTOR.relative_to(ROOT)), "sha256": sha(PROJECTOR)},
                "certified_L3_matrix": {"path": str(L3_CERTIFICATE.relative_to(ROOT)), "sha256": sha(L3_CERTIFICATE)},
                "certified_L3_slice": {"path": str(L3_SLICE.relative_to(ROOT)), "sha256": sha(L3_SLICE)},
            },
        },
    }


def fast_check() -> None:
    value = json.loads(OUTPUT.read_text())
    if value["provenance"]["generator_sha256"] != sha(Path(__file__)):
        raise AssertionError("nonaxisymmetric generator hash changed")
    if value["source_slices"]["sha256"] != sha(SLICE):
        raise AssertionError("nonaxisymmetric source slice changed")
    for item in value["provenance"]["inputs"].values():
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise AssertionError(f"stale input {item['path']}")
    summary = value["matrix_summary"]
    if summary["target_adjoint_coefficients"] != 56:
        raise AssertionError("nonaxisymmetric workload count changed")
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        if row["shell_defect"] != "0":
            raise AssertionError("stored odd-L row left shell")
        for channel in row["parity_channels"]:
            for fixture in channel["basis_fixtures"]:
                fixtures += 1
                pairings = [parse(item) for item in fixture["scaled_pairings"]]
                coefficients += len(pairings)
                has_witness = False
                for pairing, stored in zip(pairings, fixture["pairing_intervals"], strict=True):
                    if pairing == 0:
                        zeros += 1
                        if stored is not None:
                            raise AssertionError("zero pairing acquired an interval")
                    else:
                        if stored is None:
                            raise AssertionError("nonzero pairing lost its interval")
                        interval = certified_nonzero_interval(pairing)
                        if interval is None:
                            raise AssertionError("nonzero interval replay failed")
                        expected = [fraction_string(interval[0][0]), fraction_string(interval[0][1])]
                        if expected != [stored["lower"], stored["upper"]]:
                            raise AssertionError("stored interval changed")
                        has_witness = True
                if fixture["bounded_status"] != ("OBSTRUCTED" if has_witness else "OPEN"):
                    raise AssertionError("stored fixture verdict changed")
                obstructed += has_witness
    observed = (fixtures, coefficients, zeros, obstructed)
    expected = (
        summary["ordered_input_basis_fixtures"],
        summary["target_adjoint_coefficients"],
        summary["zero_target_adjoint_coefficients"],
        summary["basis_fixtures_with_nonzero_cokernel_vector"],
    )
    if observed != expected:
        raise AssertionError(f"stored nonaxisymmetric summary changed: {observed}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--write-certificate", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--recompute-exhaustive", action="store_true")
    arguments = parser.parse_args()
    if arguments.write:
        SLICE.write_text(json.dumps(build_slice(), indent=2, sort_keys=True) + "\n")
        OUTPUT.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    elif arguments.write_certificate:
        OUTPUT.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    elif arguments.check:
        fast_check()
    elif json.loads(SLICE.read_text()) != build_slice() or json.loads(OUTPUT.read_text()) != compute():
        raise AssertionError("stale exhaustive nonaxisymmetric L1/L3 matrix")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_NONAXISYMMETRIC_L1_L3_MATRIX: PASS")


if __name__ == "__main__":
    main()
