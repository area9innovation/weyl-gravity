#!/usr/bin/env python3
"""Independent verifier for the complete nonaxisymmetric L=1,3 matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _action_operator
from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)
from bridge.einstein_sector.nonaxisymmetric_pbw_projector import (
    axisymmetric_conversion,
    canonical,
    reduced_source,
)


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_nonaxisymmetric_L1_L3_q2_slices.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
AXIAL_OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
ELL1_OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str, **symbols: sp.Expr) -> sp.Expr:
    return sp.sympify(
        value,
        locals={"sqrt": sp.sqrt, "pi": sp.pi, "I": sp.I, **symbols},
    )


def branch_mass(branch: str) -> sp.Expr:
    return {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }[branch]


def target_mass(output_ell: int, branch: str) -> sp.Expr:
    eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    if output_ell == 1:
        assert branch == "extra"
        return sp.Rational(4, 3)
    if branch == "p_extra":
        return eigenvalue - sp.Rational(2, 3)
    return eigenvalue + (-1 if branch == "q_minus" else 1) * sp.sqrt(
        2 * eigenvalue
    )


def axial_basis(
    branch: str, momentum: sp.Expr, frequency: sp.Expr
) -> list[sp.Matrix]:
    mass = branch_mass(branch)
    if branch != "p_extra":
        return [
            sp.Matrix(
                [
                    2 * momentum,
                    -2 * frequency,
                    momentum * (mass - 6),
                    -frequency * (mass - 6),
                ]
            )
        ]
    return [
        sp.Matrix([-momentum**2 - 6, momentum * frequency, 6, 0]),
        sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, 6]),
    ]


def polar_basis(
    branch: str, momentum: sp.Expr, frequency: sp.Expr
) -> list[sp.Matrix]:
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
    sphere_trace = -72 / (mass - 6)
    reconstruction = sphere_trace - 12
    common = -(frequency**2 + momentum**2) * reconstruction / mass
    return [
        sp.Matrix(
            [
                common + sphere_trace,
                2 * momentum * frequency * reconstruction / mass,
                common - sphere_trace,
                6,
            ]
        ).applyfunc(sp.factor)
    ]


def target_adjoints(
    parity: str,
    output_ell: int,
    branch: str,
    momentum: sp.Expr,
    frequency: sp.Expr,
) -> list[sp.Matrix]:
    if output_ell == 1:
        if parity == "axial":
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
    if parity == "axial":
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


def shell_remainder(
    value: sp.Expr, frequency: sp.Symbol, momentum: sp.Symbol, mass: sp.Expr
) -> sp.Expr:
    numerator, denominator = sp.fraction(sp.cancel(value))
    extension = [radical for radical in mass.atoms(sp.Pow) if radical.exp == sp.Rational(1, 2)]
    coefficient_domain = (
        sp.QQ.algebraic_field(*extension).frac_field(momentum)
        if extension
        else sp.QQ.frac_field(momentum)
    )
    numerator_poly = sp.Poly(numerator, frequency, domain=coefficient_domain)
    divisor = sp.Poly(
        frequency**2 - momentum**2 - mass,
        frequency,
        domain=coefficient_domain,
    )
    remainder = numerator_poly.rem(divisor).as_expr()
    return sp.factor(remainder / denominator)


def verify_target_kernels() -> None:
    momentum, frequency, eigenvalue = sp.symbols("k omega lambda", real=True)
    axial_record = json.loads(AXIAL_OPERATOR.read_text())["operator_algebra"]
    axial = sp.Matrix(
        [
            [
                parse(
                    item.replace("lambda", "lam"),
                    k=momentum,
                    omega=frequency,
                    lam=eigenvalue,
                )
                for item in row
            ]
            for row in axial_record["gauge_fixed_Hessian_operator"]
        ]
    ).subs(eigenvalue, 12)
    polar, polar_symbols = _action_operator()
    polar = polar.subs(
        {
            polar_symbols[0]: 12,
            polar_symbols[1]: momentum,
            polar_symbols[2]: frequency,
        }
    )
    for parity, matrix in (("axial", axial), ("polar", polar)):
        for branch in ("q_minus", "p_extra", "q_plus"):
            mass = target_mass(3, branch)
            for vector in target_adjoints(parity, 3, branch, momentum, frequency):
                assert all(
                    shell_remainder(item, frequency, momentum, mass) == 0
                    for item in matrix * vector
                )
    ell1 = json.loads(ELL1_OPERATOR.read_text())["direct_replay"]
    for parity in ("axial", "polar"):
        matrix = sp.Matrix(
            [
                [parse(item, k=momentum, omega=frequency) for item in row]
                for row in ell1[parity]["full_Fourier_action_Hessian"]
            ]
        )
        vector = target_adjoints(parity, 1, "extra", momentum, frequency)[0]
        assert all(
            shell_remainder(item, frequency, momentum, sp.Rational(4, 3)) == 0
            for item in matrix * vector
        )


def load_sources() -> tuple[
    tuple[sp.Symbol, ...],
    tuple[sp.Symbol, ...],
    tuple[sp.Symbol, ...],
    dict[tuple[str, str, int], sp.Matrix],
]:
    value = json.loads(SLICE.read_text())
    variables = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    first = sp.symbols("a_0:4", real=True)
    second = sp.symbols("b_0:4", real=True)
    local = {str(item): item for item in (*variables, *first, *second)}
    pairs = (("axial", "axial"), ("polar", "polar"), ("axial", "polar"), ("polar", "axial"))
    sources = {
        (left, right, ell): sp.Matrix(
            [parse(item, **local) for item in value["sources"][f"{left}_{right}_L{ell}"]]
        )
        for ell in (1, 3)
        for left, right in pairs
    }
    return variables, first, second, sources


def scaled_real(value: sp.Expr) -> tuple[sp.Expr, str]:
    scaled = canonical(sp.sqrt(sp.pi) * value)
    phase = "sqrt(pi)"
    if scaled.has(sp.I):
        scaled = canonical(-sp.I * scaled)
        phase = "-i*sqrt(pi)"
    assert not scaled.has(sp.I, sp.pi)
    return scaled, phase


def verify_projector_l4_calibration() -> None:
    from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import generic_source as aa_source
    from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix import generic_source as ap_source
    from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix import generic_source as pp_source

    first_vector = tuple(map(sp.Integer, (1, 2, 3, 4)))
    second_vector = tuple(map(sp.Integer, (5, 6, 7, 8)))
    k_1, omega_1, k_2, omega_2 = map(sp.Integer, (1, 2, -2, 3))
    conversion = axisymmetric_conversion(4)
    for first_parity, second_parity, source_function in (
        ("axial", "axial", aa_source),
        ("polar", "polar", pp_source),
        ("axial", "polar", ap_source),
    ):
        reduced = reduced_source(
            first_parity,
            second_parity,
            first_vector,
            second_vector,
            k_1,
            omega_1,
            k_2,
            omega_2,
            4,
        )
        variables, first, second, source, *_ = source_function()
        expected = source.subs(
            {
                variables[0]: k_1,
                variables[1]: omega_1,
                variables[2]: k_2,
                variables[3]: omega_2,
                **dict(zip(first, first_vector, strict=True)),
                **dict(zip(second, second_vector, strict=True)),
            },
            simultaneous=True,
        )
        assert (conversion * reduced - expected).applyfunc(canonical) == sp.zeros(4, 1)
    reduced = reduced_source(
        "polar",
        "axial",
        first_vector,
        second_vector,
        k_1,
        omega_1,
        k_2,
        omega_2,
        4,
    )
    variables, axial, polar, source, _ = ap_source()
    expected = source.subs(
        {
            variables[0]: k_2,
            variables[1]: omega_2,
            variables[2]: k_1,
            variables[3]: omega_1,
            **dict(zip(axial, second_vector, strict=True)),
            **dict(zip(polar, first_vector, strict=True)),
        },
        simultaneous=True,
    )
    assert (conversion * reduced - expected).applyfunc(canonical) == sp.zeros(4, 1)


def independently_verify(exhaustive: bool = False) -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    assert value["source_slices"]["sha256"] == sha(SLICE)
    for item in value["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    verify_target_kernels()
    workload = {
        row["candidate_index"]: row
        for row in json.loads(PARITY.read_text())["source_workload"]["rows"]
        if row["output_ell"] in (1, 3)
    }
    assert [row["candidate_index"] for row in value["candidate_rows"]] == sorted(workload)
    variables, first_symbols, second_symbols, sources = load_sources()
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        expected_row = workload[row["candidate_index"]]
        assert (row["first_branch"], row["second_branch"], row["target_branch"], row["output_ell"]) == (
            expected_row["first_branch"],
            expected_row["second_branch"],
            expected_row["target_branch"],
            expected_row["output_ell"],
        )
        rho = parse(row["rho"])
        momenta = [sign * sp.sqrt(rho) for sign in row["signed_momenta"]]
        positive = [
            sp.sqrt(momenta[0] ** 2 + branch_mass(row["first_branch"])),
            sp.sqrt(momenta[1] ** 2 + branch_mass(row["second_branch"])),
        ]
        frequencies = [row["temporal_signs"][index] * positive[index] for index in range(2)]
        target_momentum, target_frequency = sum(momenta), sum(frequencies)
        assert canonical(
            target_frequency**2
            - target_momentum**2
            - target_mass(row["output_ell"], row["target_branch"])
        ) == 0
        for channel in row["parity_channels"]:
            first_basis = (
                axial_basis if channel["first_parity"] == "axial" else polar_basis
            )(row["first_branch"], momenta[0], frequencies[0])
            second_basis = (
                axial_basis if channel["second_parity"] == "axial" else polar_basis
            )(row["second_branch"], momenta[1], frequencies[1])
            adjoints = target_adjoints(
                channel["target_parity"],
                row["output_ell"],
                row["target_branch"],
                target_momentum,
                target_frequency,
            )
            source = sources[(channel["first_parity"], channel["second_parity"], row["output_ell"])]
            index = 0
            for first_vector in first_basis:
                for second_vector in second_basis:
                    fixture = channel["basis_fixtures"][index]
                    index += 1
                    fixtures += 1
                    stored_pairings = [parse(item) for item in fixture["scaled_pairings"]]
                    if exhaustive:
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
                        reconstructed = [
                            scaled_real((adjoint.T * specialized)[0])
                            for adjoint in adjoints
                        ]
                        assert [item[1] for item in reconstructed] == fixture["phase_normalizations"]
                        assert all(
                            canonical(item[0] - stored) == 0
                            for item, stored in zip(reconstructed, stored_pairings, strict=True)
                        )
                    coefficients += len(stored_pairings)
                    has_witness = False
                    for pairing, interval_value in zip(stored_pairings, fixture["pairing_intervals"], strict=True):
                        if pairing == 0:
                            zeros += 1
                            assert interval_value is None
                        else:
                            interval = certified_nonzero_interval(pairing)
                            assert interval is not None and interval_value is not None
                            assert [fraction_string(interval[0][0]), fraction_string(interval[0][1])] == [interval_value["lower"], interval_value["upper"]]
                            has_witness = True
                    assert fixture["bounded_status"] == ("OBSTRUCTED" if has_witness else "OPEN")
                    obstructed += has_witness
    summary = value["matrix_summary"]
    assert (fixtures, coefficients, zeros, obstructed) == (
        summary["ordered_input_basis_fixtures"],
        summary["target_adjoint_coefficients"],
        summary["zero_target_adjoint_coefficients"],
        summary["basis_fixtures_with_nonzero_cokernel_vector"],
    ) == (48, 56, 0, 48)
    assert value["classification"]["certified_L3_submatrix_replayed"]
    assert value["classification"]["all_164_branch_basis_coefficients_classified"]
    assert not value["classification"]["arbitrary_amplitude_zero_variety_classified"]
    assert not value["classification"]["complete_two_fibre_tangent_cone_classified"]
    if exhaustive:
        verify_projector_l4_calibration()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive", action="store_true")
    arguments = parser.parse_args()
    independently_verify(arguments.exhaustive)
    print(
        "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_NONAXISYMMETRIC_L1_L3_MATRIX independent verification: PASS"
    )
