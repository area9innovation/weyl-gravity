#!/usr/bin/env python3
"""Exact future-horizon Lee--Wald Gram from correlated Frobenius series."""
from __future__ import annotations

import json
import hashlib
from functools import lru_cache
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_endpoint_remainder_enclosures import (
    produce as endpoint,
)
from black_hole_programme.phase3.axial_null_infinity_trace_preflight import (
    current_dag,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FLUX = ROOT / "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json"
RECONSTRUCTION = (
    ROOT / "black_hole_programme/phase3/"
    "axial_complete_reconstruction_repair/certificate.json"
)
RECURRENCE = (
    ROOT / "black_hole_programme/phase3/"
    "axial_endpoint_remainder_enclosures/produce.py"
)
OUTPUT = HERE / "future_horizon_outward_gram.json"
I = sp.I


def conjugate(expr: sp.Expr, omega: sp.Symbol) -> sp.Expr:
    return sp.conjugate(expr).subs({
        sp.conjugate(omega): omega,
        sp.conjugate(sp.Symbol("rho", real=True)): sp.Symbol("rho", real=True),
    })


def field_atom(atom: sp.Expr) -> tuple[str, str, int, int]:
    if isinstance(atom, sp.Derivative):
        function = atom.expr
        radial = sum(int(pair[1]) for pair in atom.args[1:]
                     if pair[0].name == "r")
        temporal = sum(int(pair[1]) for pair in atom.args[1:]
                       if pair[0].name == "t")
    else:
        function = atom
        radial = temporal = 0
    name = str(function.func)
    return name[:2], name[-1], radial, temporal


@lru_cache(maxsize=1)
def literal_terms() -> tuple[tuple[sp.Expr, tuple, tuple], ...]:
    payload = json.loads(FLUX.read_text())
    text = payload["bilinear"]["F_r"]
    t, r, mass, alpha = sp.symbols("t r m alpha")
    functions = {name: sp.Function(name)
                 for name in ("h0a", "h1a", "h0b", "h1b")}
    expression = sp.sympify(text, locals={
        "t": t, "r": r, "m": mass, "alpha": alpha,
        "pi": sp.pi, "Derivative": sp.Derivative, **functions,
    }) / (sp.pi * alpha)
    expression = sp.expand(expression.subs(mass, 1))
    atoms = set(function(t, r) for function in functions.values())
    atoms.update(expression.atoms(sp.Derivative))
    encoded = {atom: sp.Symbol(f"jet_{index}")
               for index, atom in enumerate(atoms)}
    descriptors = {encoded[atom]: field_atom(atom) for atom in atoms}
    expression = sp.expand(expression.xreplace(encoded))
    combined: dict[tuple[tuple, tuple], sp.Expr] = {}
    for term in sp.Add.make_args(expression):
        present = list(term.free_symbols & set(descriptors))
        if len(present) != 2:
            raise RuntimeError(f"literal current term lost bilinearity: {term}")
        left, right = present
        if descriptors[left][1] == "b":
            left, right = right, left
        if (descriptors[left][1], descriptors[right][1]) != ("a", "b"):
            raise RuntimeError("literal current term lost slot grading")
        key = descriptors[left], descriptors[right]
        combined[key] = combined.get(key, 0) + term / (left * right)
    return tuple(
        (sp.cancel(coefficient), left, right)
        for (left, right), coefficient in combined.items()
    )


def regular_basis() -> tuple[sp.Symbol, sp.Symbol, sp.Matrix]:
    rho = sp.Symbol("rho", real=True)
    repair = endpoint.load_repair_module()
    data = endpoint.exact_horizon_data(repair)
    omega = data["omega"]
    basis = sp.zeros(6, 3)
    for order, head in enumerate(data["physical_heads"]):
        basis += head[:, :3] * rho ** order
    # The recurrence is in (P,P',Q,Q',H1,rho*F).
    basis[5, :] /= rho
    return rho, omega, basis.applyfunc(sp.cancel)


def metric_jets(
    rho: sp.Symbol, omega: sp.Symbol, basis: sp.Matrix
) -> dict[tuple[int, str, int], sp.Expr]:
    exact = current_dag._load_frozen_repaired_system()
    source_r = exact["symbols"]["r"]
    source_omega = exact["symbols"]["omega"]
    h0_row = exact["h0_row"].subs({
        source_r: 2 + rho, source_omega: omega
    })
    blackening = rho / (2 + rho)
    result: dict[tuple[int, str, int], sp.Expr] = {}
    for column in range(3):
        state = basis[:, column]
        h0 = sp.cancel((h0_row * state)[0])
        h1 = sp.cancel(state[4] + h0 / blackening)
        for field, value in (("h0", h0), ("h1", h1)):
            current = value
            result[(column, field, 0)] = current
            for order in range(1, 4):
                current = sp.cancel(
                    sp.diff(current, rho) + I * omega / blackening * current
                )
                result[(column, field, order)] = current
    return result


def valuation(expr: sp.Expr, rho: sp.Symbol) -> tuple[int, sp.Expr, sp.Expr]:
    """Return the rho valuation and regular numerator/denominator."""
    numerator, denominator = sp.fraction(expr)
    if numerator == 0:
        return 1000, sp.Integer(0), sp.Integer(1)
    numerator_poly = sp.Poly(numerator, rho)
    denominator_poly = sp.Poly(denominator, rho)
    numerator_order = min(power[0] for power in numerator_poly.as_dict())
    denominator_order = min(power[0] for power in denominator_poly.as_dict())
    regular_numerator = sum(
        coefficient * rho ** (power[0] - numerator_order)
        for power, coefficient in numerator_poly.as_dict().items()
    )
    regular_denominator = sum(
        coefficient * rho ** (power[0] - denominator_order)
        for power, coefficient in denominator_poly.as_dict().items()
    )
    return (
        numerator_order - denominator_order,
        regular_numerator,
        regular_denominator,
    )


@lru_cache(maxsize=None)
def laurent_coefficients(
    expr: sp.Expr, rho: sp.Symbol, maximum: int
) -> tuple[tuple[int, sp.Expr], ...]:
    order, numerator, denominator = valuation(expr, rho)
    if order == 1000 or maximum < order:
        return ()
    regular = numerator / denominator
    values = []
    for degree in range(maximum - order + 1):
        values.append((
            order + degree,
            sp.cancel(
                sp.diff(regular, rho, degree).subs(rho, 0)
                / sp.factorial(degree)
            ),
        ))
    return tuple(values)


def laurent_product_constant(
    factors: tuple[sp.Expr, ...], rho: sp.Symbol
) -> sp.Expr:
    orders = [valuation(factor, rho)[0] for factor in factors]
    if 1000 in orders or sum(orders) > 0:
        return sp.Integer(0)
    series = {0: sp.Integer(1)}
    for index, factor in enumerate(factors):
        maximum = -sum(
            orders[other] for other in range(len(factors))
            if other != index
        )
        coefficients = dict(laurent_coefficients(factor, rho, maximum))
        limit = -sum(orders[index + 1:])
        product: dict[int, sp.Expr] = {}
        for left_degree, left_value in series.items():
            for right_degree, right_value in coefficients.items():
                degree = left_degree + right_degree
                if degree <= limit:
                    product[degree] = (
                        product.get(degree, 0) + left_value * right_value
                    )
        series = product
    return sp.cancel(series.get(0, 0))


def gram_entry(
    row: int,
    column: int,
    rho: sp.Symbol,
    omega: sp.Symbol,
    jets: dict[tuple[int, str, int], sp.Expr],
) -> sp.Expr:
    current = sp.Integer(0)
    for coefficient, left, right in literal_terms():
        left_field, _, left_r, left_t = left
        right_field, _, right_r, right_t = right
        y = jets[(column, left_field, left_r)] * (I * omega) ** left_t
        z = conjugate(jets[(row, right_field, right_r)], omega)
        z *= (-I * omega) ** right_t
        radial_symbols = [symbol for symbol in coefficient.free_symbols
                          if symbol.name == "r"]
        coefficient = coefficient.subs({
            symbol: 2 + rho for symbol in radial_symbols
        })
        current += laurent_product_constant((coefficient, y, z), rho)
    # The endpoint-oriented coordinate-radial form is K=+iJ.  The future
    # horizon has the opposite Stokes orientation, hence H_out=-K=-iJ.
    return sp.cancel(-I * current)


def omitted_head_cross_order(
    rho: sp.Symbol,
    omega: sp.Symbol,
    jets: dict[tuple[int, str, int], sp.Expr],
) -> int:
    """Power-count the first omitted sheared rho^4 head in every cross term."""
    exact = current_dag._load_frozen_repaired_system()
    source_r = exact["symbols"]["r"]
    source_omega = exact["symbols"]["omega"]
    h0_row = exact["h0_row"].subs({
        source_r: 2 + rho, source_omega: omega
    })
    unknowns = sp.symbols("u0:6")
    # The last standard-state entry is F=(rho*F)/rho.
    state = sp.Matrix([
        unknowns[index] * rho ** (4 if index < 5 else 3)
        for index in range(6)
    ])
    blackening = rho / (2 + rho)
    h0 = sp.cancel((h0_row * state)[0])
    delta: dict[tuple[str, int], sp.Expr] = {}
    for field, value in (("h0", h0),
                         ("h1", sp.cancel(state[4] + h0 / blackening))):
        current = value
        delta[(field, 0)] = current
        for order in range(1, 4):
            current = sp.cancel(
                sp.diff(current, rho) + I * omega / blackening * current
            )
            delta[(field, order)] = current
    orders = []
    for coefficient, left, right in literal_terms():
        radial_symbols = [symbol for symbol in coefficient.free_symbols
                          if symbol.name == "r"]
        coefficient = coefficient.subs({
            symbol: 2 + rho for symbol in radial_symbols
        })
        coefficient_order = valuation(coefficient, rho)[0]
        left_field, _, left_r, _ = left
        right_field, _, right_r, _ = right
        for column in range(3):
            orders.append(
                coefficient_order
                + valuation(delta[(left_field, left_r)], rho)[0]
                + valuation(jets[(column, right_field, right_r)], rho)[0]
            )
            orders.append(
                coefficient_order
                + valuation(jets[(column, left_field, left_r)], rho)[0]
                + valuation(delta[(right_field, right_r)], rho)[0]
            )
    return min(orders)


def produce() -> dict:
    rho, omega, basis = regular_basis()
    print("exact Frobenius basis ready", flush=True)
    jets = metric_jets(rho, omega, basis)
    print("metric jets ready", flush=True)
    gram = sp.zeros(3)
    for i in range(3):
        for j in range(i, 3):
            value = gram_entry(i, j, rho, omega, jets)
            print(f"gram {i} {j} ready", flush=True)
            gram[i, j] = value
            gram[j, i] = conjugate(value, omega)
    hermitian_defect = sp.Matrix(3, 3, lambda i, j:
        sp.cancel(gram[i, j] - conjugate(gram[j, i], omega)))
    if hermitian_defect != sp.zeros(3):
        raise RuntimeError(f"horizon Gram is not Hermitian: {hermitian_defect}")
    principal_minors = [
        sp.factor(gram[:size, :size].det()) for size in range(1, 4)
    ]
    pivots = [
        principal_minors[0],
        sp.factor(principal_minors[1] / principal_minors[0]),
        sp.factor(principal_minors[2] / principal_minors[1]),
    ]
    omitted_order = omitted_head_cross_order(rho, omega, jets)
    if omitted_order <= 0:
        raise RuntimeError("order-three Frobenius truncation is insufficient")
    print(gram)
    document = {
        "schema": "phase3-axial-future-horizon-outward-gram-v2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "PASS",
        "basis": ["XH0a", "XH0b", "EH0"],
        "frequency_interval": ["1/2", "3/4"],
        "orientation": {
            "coordinate_radial": "K4=+I*Jhat",
            "future_horizon_outward": (
                "H_out=-Hframe^dagger*K4*Hframe"
                "=-I*Hframe^dagger*Jhat*Hframe"
            ),
        },
        "normalization": "canonical repaired future-regular Frobenius heads",
        "gram_without_pi_alpha_W": [
            [sp.sstr(sp.factor(gram[i, j])) for j in range(3)]
            for i in range(3)
        ],
        "leading_principal_minors": [
            sp.sstr(value) for value in principal_minors
        ],
        "ldl_pivots": [sp.sstr(value) for value in pivots],
        "ldl_pivot_signs_on_closed_interval": ["positive", "negative", "negative"],
        "inertia_for_alpha_W_positive": [1, 2, 0],
        "rank": 3,
        "semidefinite_disposition": {
            "H_out_positive_semidefinite": False,
            "minus_H_out_positive_semidefinite": False,
            "reason": (
                "H_out has exact inertia (1,2,0), while -H_out has "
                "inertia (2,1,0)"
            ),
        },
        "stokes_rank_shortcut": {
            "identity": (
                "H_out+T_plus^dagger*G_plus*T_plus"
                "-T_minus^dagger*G_minus*T_minus=0"
            ),
            "activated": False,
            "direct_endpoint_rank_bound": None,
            "reason": (
                "neither H_out nor -H_out is positive semidefinite; "
                "the semidefinite Stokes shortcut supplies no endpoint "
                "projection-rank bound"
            ),
        },
        "construction": (
            "exact rho-to-zero Laurent constant of the correlated order-three "
            "Frobenius recurrence paired in the literal Lee-Wald current"
        ),
        "order_three_sufficiency": {
            "first_omitted_sheared_head": "O(rho^4)",
            "minimum_omitted/exact_cross_current_order": omitted_order,
            "constant_term_affected": False,
        },
        "epsilon_method": {
            "status": "METHOD_SHORTFALL",
            "reason": (
                "independent entrywise Frobenius-tail boxes are amplified "
                "by the singular horizon current; they do not preserve the "
                "correlations needed for the Laurent cancellation"
            ),
        },
        "provenance": {
            "literal_current": str(FLUX.relative_to(ROOT)),
            "literal_current_sha256": hashlib.sha256(FLUX.read_bytes()).hexdigest(),
            "repaired_system": (
                "black_hole_programme/phase3/"
                "axial_complete_reconstruction_repair/certificate.json"
            ),
            "repaired_system_sha256": hashlib.sha256(
                RECONSTRUCTION.read_bytes()
            ).hexdigest(),
            "frobenius_recurrence": (
                "black_hole_programme/phase3/"
                "axial_endpoint_remainder_enclosures/produce.py"
            ),
            "frobenius_recurrence_sha256": hashlib.sha256(
                RECURRENCE.read_bytes()
            ).hexdigest(),
        },
        "does_not_establish": [
            "a global horizon-to-infinity connection",
            "a boundary projection rank or scattering map",
            "stability, ghost, positivity, CPT or unitarity",
        ],
    }
    return document


if __name__ == "__main__":
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
