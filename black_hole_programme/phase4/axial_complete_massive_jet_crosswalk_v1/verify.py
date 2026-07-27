#!/usr/bin/env python3
"""Independently verify the complete massive axial first-jet certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
R, W = sp.symbols("r omega", nonzero=True)
SIGMA = sp.symbols("sigma")
F = (R - 2) / R


def parse(value: str) -> sp.Expr:
    return sp.sympify(
        value, locals={"r": R, "omega": W, "sigma": SIGMA, "I": sp.I}
    )


def exact(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parsed_matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(entry) for entry in row] for row in rows])


def dstar(value: sp.Expr) -> sp.Expr:
    return exact(F * sp.diff(value, R))


def dstar_matrix(value: sp.Matrix) -> sp.Matrix:
    return value.applyfunc(dstar)


def projective(value: sp.Expr, potential: sp.Expr) -> sp.Expr:
    return exact(
        dstar(dstar(dstar(value)))
        + 4 * potential * dstar(value)
        + 2 * dstar(potential) * value
    )


def scalarize(block: sp.Matrix, potential: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    e00, e01, e10, e11 = block[0, 0], block[0, 1], block[1, 0], block[1, 1]
    s1 = exact(e11 + e00 + dstar(e01))
    s0 = exact(e10 + dstar(e00) - e01 * potential)
    return s1, s0, exact(s0 - sp.Rational(1, 2) * dstar(s1))


def verify(data: dict | None = None) -> None:
    if data is None:
        data = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(data, schema)

    assert data["status"] == "EXACT_COMPLETE_MASSIVE_FIRST_JET_FACTOR_THREE_PASS"
    flags = data["claim_flags"]
    for name in (
        "complete_coupled_massive_axial_equations_imported",
        "exact_massless_Maxwell_RW_factorization",
        "complete_first_mass_squared_jet_transformed",
        "reverse_tensor_to_vector_tangent_rationally_removed",
        "physical_tensor_projective_class_computed",
        "naive_unit_mass_class_rejected",
        "factor_three_Bach_mass_crosswalk_exact",
        "leading_differentiated_Jost_phase_match",
    ):
        assert flags[name] is True
    for name in (
        "all_order_differentiated_Jost_map_certified",
        "physical_QNM_velocity_certified",
        "global_causal_resolvent_certified",
    ):
        assert flags[name] is False

    # Reconstruct the imported equations in a representation independent of
    # the producer's stored residuals.
    u2 = exact(W**2 - F * (6 / R**2 - 6 / R**3))
    u1 = exact(W**2 - 6 * F / R**2)
    factor_flow = sp.Matrix(
        [
            [0, 1, 0, 0],
            [-u2, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, -u1, 0],
        ]
    )
    qz_flow = sp.Matrix(
        [
            [0, 1, 0, 0],
            [
                -exact(W**2 - F * (10 / R**2 - 16 / R**3)),
                0,
                8 * F * (R - 3) / R**3,
                0,
            ],
            [0, 0, 0, 1],
            [
                2 * F / R**2,
                0,
                -exact(W**2 - F * (4 / R**2 + 2 / R**3)),
                0,
            ],
        ]
    ).applyfunc(exact)
    mass_tangent = sp.zeros(4)
    mass_tangent[1, 0] = F
    mass_tangent[3, 2] = F

    q_row = sp.Matrix(
        [[
            4 * F / (3 * W**2 * R),
            4 / (3 * W**2),
            -2 * F / (W**2 * R),
            1 / W**2,
        ]]
    )
    z_row = sp.Matrix(
        [[
            -(7 * R - 6) / (3 * W**2 * R**2),
            -1 / W**2,
            -1 / (W**2 * R),
            0,
        ]]
    )
    derivative = lambda row: (dstar_matrix(row) + row * factor_flow).applyfunc(exact)
    transform = sp.Matrix.vstack(q_row, derivative(q_row), z_row, derivative(z_row))

    stored_transform = parsed_matrix(
        data["massless_factorization"]["transform_factor_to_QZ"]
    )
    assert (stored_transform - transform).applyfunc(exact) == sp.zeros(4)
    assert exact(transform.det() - W**-4) == 0
    assert exact(parse(data["massless_factorization"]["determinant"]) - W**-4) == 0
    assert (
        dstar_matrix(transform) + transform * factor_flow - qz_flow * transform
    ).applyfunc(exact) == sp.zeros(4)
    assert (
        parsed_matrix(data["complete_massive_axial_system"]["massless_flow"])
        - qz_flow
    ).applyfunc(exact) == sp.zeros(4)
    assert (
        parsed_matrix(data["complete_massive_axial_system"]["mass_tangent"])
        - mass_tangent
    ).applyfunc(exact) == sp.zeros(4)

    factor_tangent = (transform.inv() * mass_tangent * transform).applyfunc(exact)
    assert (
        parsed_matrix(data["complete_first_mass_jet"]["factor_tangent"])
        - factor_tangent
    ).applyfunc(exact) == sp.zeros(4)
    tensor_block = factor_tangent[:2, :2]
    reverse_block = factor_tangent[2:, :2]
    tensor_s1, tensor_s0, tensor_density = scalarize(tensor_block, u2)
    reverse_s1, reverse_s0, _ = scalarize(reverse_block, u2)

    projective_data = data["physical_tensor_projective_class"]
    assert projective_data["class"] == "[I_phys]=(1/3)[f]"
    assert exact(parse(projective_data["s1"]) - tensor_s1) == 0
    assert exact(parse(projective_data["s0"]) - tensor_s0) == 0
    assert exact(parse(projective_data["density"]) - tensor_density) == 0
    mass_primitive = parse(projective_data["primitive"])
    assert exact(tensor_density - projective(mass_primitive, u2) - F / 3) == 0

    reverse = data["complete_first_mass_jet"]["reverse_scalar_source"]
    reverse_multiplier = parse(reverse["removing_multiplier_P"])
    assert reverse_s1 == 0
    assert exact(reverse_multiplier * (u1 - u2) - reverse_s0) == 0

    crosswalk = data["bach_crosswalk"]
    scaling = 3 * sp.I * W / 2
    assert exact(parse(crosswalk["physical_scaling"]) - scaling) == 0
    bach_density = parse(crosswalk["bach_density"])
    bach_primitive = parse(crosswalk["bach_primitive"])
    assert exact(
        bach_density - projective(bach_primitive, u2) - sp.I * W * F / 2
    ) == 0
    combined_primitive = parse(crosswalk["combined_primitive"])
    assert exact(
        bach_density
        - scaling * tensor_density
        - projective(combined_primitive, u2)
    ) == 0
    assert "3*I*omega/2" in crosswalk["tangent_parameter_relation"]

    obstruction = data["naive_single_scalar_equality_obstruction"]
    assert obstruction["matrix_rank"] == 3
    assert obstruction["augmented_rank"] == 4
    assert exact(parse(obstruction["obstruction"])) != 0

    endpoint = data["endpoint_leading_crosswalk"]
    assert endpoint["leading_match_exact"] is True
    assert exact(
        parse(endpoint["scaled_physical_tangent_r_coefficient"])
        - parse(endpoint["bach_tangent_r_coefficient"])
    ) == 0

    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        assert path.is_file()
        assert sha256(path) == imported["sha256"]

    exclusions = set(data["does_not_establish"])
    assert "the physical massive-QNM velocity at the certified Weyl QNM" in exclusions
    assert "a global retarded contour deformation or causal ringdown theorem" in exclusions


if __name__ == "__main__":
    verify()
    print("PASS complete massive axial first-jet crosswalk")
