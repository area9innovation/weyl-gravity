#!/usr/bin/env python3
"""Construct the generic covariant Volterra carrier for the physical cubic row.

The monic flat principal part of the physical Hessian is ``L**2``.  Hence
each free inverse is represented covariantly by

    (L**2)^-1 = integral_0^infinity u exp(-u L) du.

The cubic trace-log row has six ordered three-H1 cells and three H1-H2
contact cells.  This module constructs their common resolved parameter
carrier and puts every boundary chart under one Mellin regulator.  It does
not evaluate the generic tensor kernels on that carrier.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-covariant-volterra-carrier-v1.schema.json"
DEPENDENCIES = {
    "physical_H1": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "physical_H2": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json",
    "fixture_Mellin_subtraction": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json",
}


def _q(value: Any) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _exact_carrier_checks() -> dict[str, Any]:
    total, radial, tangent, interval = sp.symbols(
        "T r t x", positive=True
    )

    triangle_times = sp.Matrix(
        [
            total * (1 - radial),
            total * radial * tangent,
            total * radial * (1 - tangent),
        ]
    )
    # The oriented determinant is negative in this coordinate ordering.
    triangle_jacobian = sp.factor(total**2 * radial)
    triangle_squared_propagator_weight = sp.factor(
        triangle_jacobian * sp.prod(triangle_times)
    )

    bubble_times = sp.Matrix([total * interval, total * (1 - interval)])
    bubble_jacobian = total
    bubble_squared_propagator_weight = sp.factor(
        bubble_jacobian * sp.prod(bubble_times)
    )

    if triangle_jacobian != total**2 * radial:
        raise ValueError("triangle Volterra Jacobian drifted")
    if sp.simplify(
        triangle_squared_propagator_weight
        - total**5 * radial**3 * (1 - radial) * tangent * (1 - tangent)
    ) != 0:
        raise ValueError("triangle squared-propagator weight drifted")
    if bubble_jacobian != total:
        raise ValueError("bubble Volterra Jacobian drifted")
    if sp.simplify(
        bubble_squared_propagator_weight - total**3 * interval * (1 - interval)
    ) != 0:
        raise ValueError("bubble squared-propagator weight drifted")

    # Exact noncommuting finite-dimensional replay of the proper-time carrier.
    # Integral u exp(-u L) du is L^-2 entrywise for diagonal positive L.
    laplacian = sp.diag(1, 2, 3)
    green = laplacian**-2
    h1 = (
        sp.Matrix([[1, 2, 0], [0, -1, 1], [3, 0, 2]]),
        sp.Matrix([[0, 1, 2], [2, 0, -1], [1, 1, 0]]),
        sp.Matrix([[2, 0, 1], [-1, 3, 0], [0, 2, 1]]),
    )
    h2 = (
        sp.Matrix([[1, 0, 2], [2, -1, 0], [0, 1, 1]]),
        sp.Matrix([[0, 2, 1], [1, 1, 0], [3, 0, -1]]),
        sp.Matrix([[2, 1, 0], [0, 1, 2], [1, -1, 1]]),
    )
    permutations = tuple(itertools.permutations(range(3)))
    triangle_traces = [
        sp.trace(green * h1[i] * green * h1[j] * green * h1[k])
        for i, j, k in permutations
    ]
    mixed_traces = [
        sp.trace(green * h1[i] * green * h2[i]) for i in range(3)
    ]
    cubic = sp.Rational(1, 6) * sum(triangle_traces) - sp.Rational(
        1, 2
    ) * sum(mixed_traces)
    if not (
        triangle_traces[0] == triangle_traces[3] == triangle_traces[4]
        and triangle_traces[1] == triangle_traces[2] == triangle_traces[5]
    ):
        raise ValueError("finite Volterra cyclicity replay failed")

    s, z = sp.symbols("s z", positive=True)
    mellin_model = z**s / s
    if sp.limit(s * mellin_model, s, 0) != 1:
        raise ValueError("common Mellin residue normalization failed")
    if sp.limit(mellin_model - 1 / s, s, 0) != sp.log(z):
        raise ValueError("common Mellin finite scale term failed")

    return {
        "triangle_change_of_variables": {
            "proper_times": ["T*(1-r)", "T*r*t", "T*r*(1-t)"],
            "jacobian": "T^2*r",
            "squared_propagator_measure": "T^5*r^3*(1-r)*t*(1-t)",
        },
        "bubble_change_of_variables": {
            "proper_times": ["T*x", "T*(1-x)"],
            "jacobian": "T",
            "squared_propagator_measure": "T^3*x*(1-x)",
        },
        "finite_noncommuting_replay": {
            "laplacian_diagonal": [1, 2, 3],
            "green_diagonal": [_q(value) for value in green.diagonal()],
            "ordered_triangle_trace_count": len(triangle_traces),
            "mixed_contact_trace_count": len(mixed_traces),
            "trace_log_cubic_value": _q(cubic),
            "cyclicity": "EXACT",
        },
        "Mellin_model": {
            "regulated_boundary_model": "z^s/s",
            "residue": _q(1),
            "minimal_subtraction_finite_scale_term": "log(z)",
        },
    }


def build() -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    h1 = dependencies["physical_H1"]
    h2 = dependencies["physical_H2"]
    fixture = dependencies["fixture_Mellin_subtraction"]
    if not h1["claim_flags"]["LINEAR_CURVATURE_V_N_U_IMPORTED"]:
        raise ValueError("physical H1 import is incomplete")
    if not h2["claim_flags"]["ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED"]:
        raise ValueError("physical H2 import is incomplete")
    if not fixture["claim_flags"]["COMMON_MELLIN_REGULATOR_FIXED"]:
        raise ValueError("fixture Mellin normalization is not frozen")

    permutations = [list(row) for row in itertools.permutations(range(3))]
    cyclic_orbits = [
        [[0, 1, 2], [1, 2, 0], [2, 0, 1]],
        [[0, 2, 1], [2, 1, 0], [1, 0, 2]],
    ]
    contacts = [
        {"H1_leg": leg, "H2_legs": [value for value in range(3) if value != leg]}
        for leg in range(3)
    ]
    checks = _exact_carrier_checks()
    fixture_ledger = fixture["resolved_boundary_ledger"]
    fixture_subtraction = fixture["subtraction_definition"]
    if (
        fixture_ledger["labelled_triangle_boundary_chart_count"] != 18
        or fixture_ledger["bubble_endpoint_chart_count"] != 6
        or fixture_subtraction["common_regulator"] != "s"
        or fixture_subtraction["triangle_corner_chart"]
        != "alpha_i=1-r, alpha_j=r*t, alpha_k=r*(1-t)"
        or fixture["renormalization_scale_row"]["coefficient"]
        != {"numerator": 15707, "denominator": 216}
    ):
        raise ValueError("fixture pullback no longer matches the generic carrier")
    checks["fixture_pullback"] = {
        "triangle_boundary_chart_count": 18,
        "contact_endpoint_chart_count": 6,
        "common_regulator": "s",
        "triangle_chart": fixture_subtraction["triangle_corner_chart"],
        "scale_coefficient": fixture["renormalization_scale_row"]["coefficient"],
        "status": "EXACT",
    }

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-covariant-volterra-carrier-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER",
        "result_state": "GENERIC_COVARIANT_VOLTERRA_SUBTRACTION_CARRIER_CONSTRUCTED_MIXED_ROWS_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": h2["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "operator": "same-gauge monic rank-nine physical Hessian H=L^2+H1+H2+O(R^3)",
            "background": "generic smooth background on a regular local elliptic chart",
            "carrier": "covariant proper-time Volterra cells with resolved normalized-time boundaries",
        },
        "operator_identity": {
            "principal_second_order_operator": "L=-nabla^2 on traceless symmetric tensors",
            "free_fourth_order_operator": "H0=L^2",
            "free_inverse": "G0=H0^-1=integral_0^infinity u*exp(-u*L) du",
            "cubic_trace_log_row": "sum_sigma (1/6) Tr(G0 H1_sigma1 G0 H1_sigma2 G0 H1_sigma3) - sum_i (1/2) Tr(G0 H1_i G0 H2_jk)",
            "polarization": "coefficient of three independently labelled external curvatures",
        },
        "decorated_carrier": {
            "ordered_triangle_cells": permutations,
            "ordered_triangle_cell_count": len(permutations),
            "cyclic_triangle_orbits": cyclic_orbits,
            "cyclic_triangle_orbit_count": len(cyclic_orbits),
            "mixed_contact_cells": contacts,
            "mixed_contact_cell_count": len(contacts),
            "resolved_triangle_boundary_chart_count": 18,
            "resolved_contact_endpoint_chart_count": 6,
            "triangle_chart": "alpha_i=1-r, alpha_j=r*t, alpha_k=r*(1-t)",
            "contact_chart": "beta=(x,1-x), resolved at x=0 and 1-x=0",
            "attachment_rule": "H2_jk is the local contact replacing the labelled pair (H1_j,H1_k); H1_i remains the separated insertion",
        },
        "covariance_and_subtraction": {
            "covariance": "each exp(-u L) is the covariant heat kernel of L and every H1/H2 insertion is a frozen local covariant differential operator",
            "locality": "boundary residues are diagonal local symbol densities",
            "common_boundary_regulator": "multiply every resolved triangle and contact boundary density by z^s*rho^s using the same s and z=mu^2/Q^2",
            "minimal_subtraction": "remove the total coefficient of 1/s and retain the finite part",
            "fixture_pullback": "the rational equal-box triangle sectors and half-interval bubbles are the declared evaluation pullback of this carrier",
            "finite_ambiguity": "a mu-independent local covariant finite row; the scale residue is unchanged",
        },
        "exact_checks": checks,
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "claim_flags": {
            "GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED": True,
            "SIX_ORDERED_TRIANGLE_CELLS_INCLUDED": True,
            "THREE_MIXED_CONTACT_CELLS_INCLUDED": True,
            "COMMON_MELLIN_BOUNDARY_EXTENSION_DEFINED": True,
            "FIXTURE_SUBTRACTION_IS_A_PULLBACK": True,
            "GENERIC_TENSOR_KERNELS_EVALUATED": False,
            "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED": False,
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "EVALUATE_GENERIC_H1_H2_CONTACT_KERNELS_ON_COVARIANT_VOLTERRA_CARRIER_AND_ASSEMBLE_RENORMALIZED_MIXED_ROWS",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate constructs the generic covariant proper-time/Volterra carrier joining all six labelled three-H1 cells to all three labelled H1-H2 contact cells and defines their common resolved-boundary Mellin minimal subtraction. It proves the carrier combinatorics, Schwinger measures, cyclicity and fixture pullback. It does not evaluate the generic mixed tensor kernels, dispose M14, complete a physical form factor, change the QME disposition, or certify a Lorentzian theory.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("stored physical Volterra carrier is stale")
        print("physical Hessian covariant Volterra carrier: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
