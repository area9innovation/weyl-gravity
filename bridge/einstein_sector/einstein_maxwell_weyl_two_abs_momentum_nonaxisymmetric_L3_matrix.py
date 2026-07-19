"""Compute all 44 nonaxisymmetric L=3 cross-|n| adjoint coefficients."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    axial_basis,
    branch_mass,
    certified_nonzero_interval,
    fraction_string,
    parse,
)
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import polar_basis
from bridge.einstein_sector.nonaxisymmetric_pbw_projector import (
    Q2,
    axisymmetric_conversion,
    canonical,
    reduced_source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_nonaxisymmetric_L3_q2_slice.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generic_slice() -> dict[str, object]:
    k_1, omega_1, k_2, omega_2 = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    first, second = sp.symbols("a_0:4", real=True), sp.symbols("b_0:4", real=True)
    sources: dict[str, list[str]] = {}
    for first_parity, second_parity in (
        ("axial", "axial"),
        ("polar", "polar"),
        ("axial", "polar"),
        ("polar", "axial"),
    ):
        value = (
            sp.sqrt(sp.pi)
            * reduced_source(
                first_parity,
                second_parity,
                first,
                second,
                k_1,
                omega_1,
                k_2,
                omega_2,
                3,
                3,
                max_jet_order=0,
            )
        ).applyfunc(canonical)
        if any(entry.has(sp.pi) for entry in value):
            raise AssertionError("angular normalization failed to remove pi")
        sources[f"{first_parity}_{second_parity}"] = [str(entry) for entry in value]
    return {
        "schema": "einstein-maxwell-weyl-ell2-nonaxisymmetric-L3-q2-slice-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_NONAXISYMMETRIC_L3_Q2_SLICE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "parent": {
            "q2_sha256": sha(Q2),
            "row_layout_sha256": sha(ROW_LAYOUT),
            "action_sha256": sha(ACTION),
        },
        "variables": [str(value) for value in (k_1, omega_1, k_2, omega_2)],
        "first_amplitudes": [str(value) for value in first],
        "second_amplitudes": [str(value) for value in second],
        "coupled_carrier": "sum ClebschGordan(2,m1;2,m2|3,3) Y_2m1 tensor Y_2m2",
        "angular_normalization": "sqrt(pi) times the standard-normalized coupled coefficient; a fixed nonzero rescaling irrelevant to cokernel vanishing",
        "source_action_rows": sources,
        "claim_boundary": "Exact L3 reduced action sources before branch-shell specialization; no coefficient verdict is inferred by the slice alone.",
    }


def target_mass(branch: str) -> sp.Expr:
    return {
        "q_minus": 12 - 2 * sp.sqrt(6),
        "p_extra": sp.Rational(34, 3),
        "q_plus": 12 + 2 * sp.sqrt(6),
    }[branch]


def axial_adjoints(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    eigenvalue = sp.Integer(12)
    if branch == "p_extra":
        return [
            sp.Matrix([-momentum**2 - eigenvalue, momentum * frequency, eigenvalue, 0]),
            sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, eigenvalue]),
        ]
    mass = target_mass(branch)
    return [sp.Matrix([2 * momentum, -2 * frequency, momentum * (mass - eigenvalue), -frequency * (mass - eigenvalue)])]


def polar_adjoints(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    eigenvalue = sp.Integer(12)
    if branch == "p_extra":
        return [
            sp.Matrix([1, -(6 * momentum**2 + 3 * eigenvalue - 2) / (6 * momentum * frequency), 1, 0]),
            sp.Matrix([sp.Rational(4, 3), -2 * (momentum**2 + eigenvalue) / (3 * momentum * frequency), 0, 1]),
        ]
    mass = target_mass(branch)
    return [sp.Matrix([
        -2 * (eigenvalue * momentum**2 - mass * momentum**2 - eigenvalue),
        2 * momentum * frequency * (eigenvalue - mass),
        -2 * (eigenvalue * momentum**2 - mass * momentum**2 + eigenvalue**2 - eigenvalue * mass - eigenvalue),
        eigenvalue,
    ])]


def parse_slice(value: dict[str, object]) -> tuple[tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], dict[str, sp.Matrix]]:
    variables = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    first, second = sp.symbols("a_0:4", real=True), sp.symbols("b_0:4", real=True)
    local = {str(symbol): symbol for symbol in (*variables, *first, *second)}
    rows = {
        name: sp.Matrix([sp.sympify(entry, locals={"sqrt": sp.sqrt, **local}) for entry in entries])
        for name, entries in value["source_action_rows"].items()
    }
    return variables, first, second, rows


def build() -> dict[str, object]:
    slice_value = json.loads(SLICE.read_text())
    if slice_value != generic_slice():
        raise AssertionError("stale nonaxisymmetric L3 q2 slice")
    variables, first_symbols, second_symbols, sources = parse_slice(slice_value)
    workload = json.loads(PARITY.read_text())["source_workload"]["rows"]
    records: list[dict[str, object]] = []
    coefficients = fixtures = zeros = obstructed = 0
    for row in workload:
        if int(row["output_ell"]) != 3:
            continue
        rho = parse(row["rho"])
        signs = row["canonical_signed_momenta"]
        momenta = (signs[0] * sp.sqrt(rho), signs[1] * sp.sqrt(rho))
        frequencies = (
            sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])),
            sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"])),
        )
        total_momentum, total_frequency = sum(momenta), sum(frequencies)
        if canonical(total_frequency**2 - total_momentum**2 - target_mass(row["target_branch"])) != 0:
            raise AssertionError(f"candidate {row['candidate_index']} left its L3 shell")
        parity_records = []
        for channel in row["parity_channels"]:
            first_parity, second_parity = channel["first_parity"], channel["second_parity"]
            first_basis = (axial_basis if first_parity == "axial" else polar_basis)(row["first_branch"], momenta[0], frequencies[0])
            second_basis = (axial_basis if second_parity == "axial" else polar_basis)(row["second_branch"], momenta[1], frequencies[1])
            target_parity = channel["target_parity"]
            adjoints = (axial_adjoints if target_parity == "axial" else polar_adjoints)(row["target_branch"], total_momentum, total_frequency)
            source_template = sources[f"{first_parity}_{second_parity}"]
            basis_records = []
            for first_index, first_vector in enumerate(first_basis):
                for second_index, second_vector in enumerate(second_basis):
                    source = source_template.subs({
                        variables[0]: momenta[0], variables[1]: frequencies[0],
                        variables[2]: momenta[1], variables[3]: frequencies[1],
                        **dict(zip(first_symbols, first_vector, strict=True)),
                        **dict(zip(second_symbols, second_vector, strict=True)),
                    }, simultaneous=True).applyfunc(canonical)
                    pairings = [canonical((adjoint.T * source)[0]) for adjoint in adjoints]
                    intervals = [certified_nonzero_interval(pairing) for pairing in pairings]
                    witness = next((index for index, interval in enumerate(intervals) if interval is not None), None)
                    status = "OBSTRUCTED" if witness is not None else "OPEN"
                    fixtures += 1
                    coefficients += len(pairings)
                    zeros += sum(pairing == 0 for pairing in pairings)
                    obstructed += status == "OBSTRUCTED"
                    basis_records.append({
                        "first_basis_index": first_index,
                        "second_basis_index": second_index,
                        "pairings": [str(pairing) for pairing in pairings],
                        "pairing_intervals": [
                            None if interval is None else {
                                "lower": fraction_string(interval[0][0]),
                                "upper": fraction_string(interval[0][1]),
                                "decimal_digits": interval[1],
                            }
                            for interval in intervals
                        ],
                        "nonzero_component": witness,
                        "bounded_status": status,
                    })
            parity_records.append({
                "first_parity": first_parity,
                "second_parity": second_parity,
                "target_parity": target_parity,
                "basis_fixtures": basis_records,
            })
        records.append({
            "candidate_index": row["candidate_index"],
            "first_branch": row["first_branch"],
            "second_branch": row["second_branch"],
            "target_branch": row["target_branch"],
            "rho": row["rho"],
            "signed_momenta": signs,
            "parity_channels": parity_records,
        })
    if coefficients != 44:
        raise AssertionError(f"L3 coefficient workload changed: {coefficients}")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-nonaxisymmetric-L3-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_NONAXISYMMETRIC_L3_MATRIX",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_COMPLETE_NONAXISYMMETRIC_L3_BRANCH_BASIS_MATRIX",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 at six separately tuned algebraic circumference rows",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all Clebsch-Gordan-coupled L3 branch-basis cross products between |n|=1 and |n|=2",
            "degree": 2,
            "parity": "both same-parity and both ordered cross-parity inputs",
            "ell": "2 times 2 -> 3",
            "m": "coupled M=3 representative of the multiplicity-one V3 carrier",
            "k": "row-specific signed compact momenta",
            "omega": "row-specific positive-frequency SUM channel",
        },
        "source_slice": {"path": str(SLICE.relative_to(ROOT)), "sha256": sha(SLICE), "result_id": slice_value["result_id"]},
        "candidate_rows": records,
        "matrix_summary": {
            "candidate_rows": len(records),
            "ordered_input_basis_fixtures": fixtures,
            "target_adjoint_coefficients": coefficients,
            "zero_target_adjoint_coefficients": zeros,
            "nonzero_target_adjoint_coefficients": coefficients - zeros,
            "basis_fixtures_with_nonzero_cokernel_vector": obstructed,
            "basis_fixtures_without_this_resonant_witness": fixtures - obstructed,
        },
        "classification": {
            "complete_nonaxisymmetric_L3_basis_matrix_classified": True,
            "all_basis_fixtures_bounded_obstructed": obstructed == fixtures,
            "all_44_L3_adjoint_coefficients_classified": True,
            "arbitrary_amplitude_zero_variety_classified": False,
            "remaining_nonaxisymmetric_L1_coefficients": 12,
            "causal_or_quantum_claim": False,
        },
        "claim_boundary": "Complete 44-coefficient L3 branch-basis matrix. Arbitrary-amplitude cancellations, the twelve L1 coefficients, smooth-secular and causal correction classes, the complete two-fibre tangent cone, residual observables and quantum states remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                "parity_workload": {"path": str(PARITY.relative_to(ROOT)), "sha256": sha(PARITY)},
                "q2": {"path": str(Q2.relative_to(ROOT)), "sha256": sha(Q2)},
            },
        },
    }


def fast_check() -> None:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("L3 schema hash changed")
    if value["source_slice"]["sha256"] != sha(SLICE):
        raise AssertionError("L3 source slice hash changed")
    if value["provenance"]["generator_sha256"] != sha(Path(__file__)):
        raise AssertionError("L3 generator hash changed")
    for item in value["provenance"]["inputs"].values():
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise AssertionError(f"stale L3 input: {item['path']}")
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        for channel in row["parity_channels"]:
            for fixture in channel["basis_fixtures"]:
                fixtures += 1
                pairings = [parse(entry) for entry in fixture["pairings"]]
                coefficients += len(pairings)
                for pairing, interval in zip(pairings, fixture["pairing_intervals"], strict=True):
                    if pairing == 0:
                        zeros += 1
                        if interval is not None:
                            raise AssertionError("zero L3 pairing has an interval")
                    else:
                        if interval is None:
                            raise AssertionError("nonzero L3 pairing lacks an interval")
                        exact = certified_nonzero_interval(pairing)
                        if exact is None:
                            raise AssertionError("stored L3 nonzero pairing became zero")
                        bounds, digits = exact
                        if digits != interval["decimal_digits"] or [fraction_string(bounds[0]), fraction_string(bounds[1])] != [interval["lower"], interval["upper"]]:
                            raise AssertionError("L3 interval drifted")
                obstructed += fixture["bounded_status"] == "OBSTRUCTED"
    summary = value["matrix_summary"]
    if (fixtures, coefficients, zeros, obstructed) != (
        summary["ordered_input_basis_fixtures"],
        summary["target_adjoint_coefficients"],
        summary["zero_target_adjoint_coefficients"],
        summary["basis_fixtures_with_nonzero_cokernel_vector"],
    ):
        raise AssertionError("L3 matrix summary changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--recompute-exhaustive", action="store_true")
    args = parser.parse_args()
    if args.write:
        SLICE.write_text(json.dumps(generic_slice(), indent=2, sort_keys=True) + "\n")
        OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    elif args.check:
        fast_check()
    elif json.loads(OUTPUT.read_text()) != build():
        raise AssertionError("stale exhaustive nonaxisymmetric L3 matrix")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_NONAXISYMMETRIC_L3_MATRIX: PASS")


if __name__ == "__main__":
    main()
