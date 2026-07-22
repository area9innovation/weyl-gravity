"""Generic-Lambda polar Bach-carrier asymptotic system at Schwarzschild infinity."""

from __future__ import annotations

import sympy as sp

from black_hole_programme.phase2.general_l_polar.symbolic_reconstruction import (
    _cancel,
)
from black_hole_programme.weyl_geometry import Geometry


def derive_generic_carrier_asymptotics() -> dict:
    v, r, x, phi = sp.symbols("v r x phi")
    mass = sp.Symbol("m", positive=True)
    lam = sp.Symbol("Lambda")
    omega = sp.Symbol("omega", real=True, nonzero=True)
    coords = [v, r, x, phi]
    b0 = 1 - 2 * mass / r
    metric = sp.zeros(4)
    metric[0, 0] = -b0
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geometry = Geometry(coords, metric)
    inverse = geometry.ginv
    connection = geometry.Gamma
    p = sp.Function("P")(x)
    q = sp.diff(p, x)
    tensor_xx = _cancel((x * q - lam * p / 2) / (1 - x**2))
    tensor_pp = _cancel(-(1 - x**2) * (x * q - lam * p / 2))

    def strip_scalar_light(expression: sp.Expr) -> sp.Expr:
        result = sp.expand(expression)
        for order in range(8, 1, -1):
            derivative = sp.diff(p, (x, order))
            if result.has(derivative):
                replacement = sp.diff((2 * x * q - lam * p) / (1 - x**2), x, order - 2)
                result = sp.expand(sp.together(result.subs(derivative, replacement)))
        ps, qs = sp.symbols("Pslot Qslot")
        slotted = sp.together(result.xreplace({p: ps, q: qs}))
        coefficient_p = _cancel(sp.diff(slotted, ps))
        coefficient_q = _cancel(sp.diff(slotted, qs))
        remainder = _cancel(slotted - coefficient_p * ps - coefficient_q * qs)
        if coefficient_q != 0 or remainder != 0 or coefficient_p.has(x, ps, qs):
            raise RuntimeError("scalar carrier row did not strip")
        return coefficient_p

    time_fields = [sp.Function(name)(v, r) for name in ("A", "Bc", "Cc", "D", "Ec", "F", "Gc")]
    at, bt, ct, dt, et, ft, gt = time_fields
    raw = sp.zeros(4)
    raw[0, 0] = at * p
    raw[0, 1] = raw[1, 0] = bt * p
    raw[1, 1] = ct * p
    raw[0, 2] = raw[2, 0] = dt * q
    raw[1, 2] = raw[2, 1] = et * q
    raw[2, 2] = metric[2, 2] * ft * p + gt * tensor_xx
    raw[3, 3] = metric[3, 3] * ft * p + gt * tensor_pp
    trace = _cancel(sum(inverse[i, j] * raw[i, j] for i in range(4) for j in range(4)))

    def bianchi(index: int) -> sp.Expr:
        expression = sum(
            inverse[i, e] * geometry.covd2(raw, e, i, index)
            for i in range(4) for e in range(4) if inverse[i, e] != 0
        ) - sp.diff(trace, coords[index]) / 2
        if index < 2:
            return strip_scalar_light(expression)
        # The vector row divided by P' can be reduced cheaply because it is
        # linear in the harmonic after the Legendre identity.
        return strip_scalar_light(sp.together(expression * p / q))

    brows = [bianchi(i) for i in range(3)]
    dsol = sp.solve(sp.Eq(brows[0], 0), dt)[0]
    esol = sp.solve(sp.Eq(_cancel(brows[1].subs(dt, dsol).doit()), 0), et)[0]
    gsol = sp.solve(sp.Eq(_cancel(brows[2].subs({dt: dsol, et: esol}).doit()), 0), gt)[0]
    phase = sp.exp(sp.I * omega * v)
    a, b, c, f = [sp.Function(name)(r) for name in ("a", "b", "c", "f")]
    fmap = {at: a * phase, bt: b * phase, ct: c * phase, ft: f * phase}

    def fourier(expression: sp.Expr) -> sp.Expr:
        substitutions: dict[sp.Expr, sp.Expr] = {}
        for field, value in fmap.items():
            for derivative in expression.atoms(sp.Derivative):
                if derivative.expr == field:
                    result = value
                    for variable, count in derivative.variable_count:
                        result = sp.diff(result, variable, count)
                    substitutions[derivative] = result
            substitutions[field] = value
        return _cancel(expression.subs(substitutions).doit() / phase)

    drad = fourier(dsol)
    erad = fourier(esol.subs(dt, dsol).doit())
    grad = fourier(gsol.subs({dt: dsol, et: esol}).doit())
    psi = sp.zeros(4)
    psi[0, 0] = a * p * phase
    psi[0, 1] = psi[1, 0] = b * p * phase
    psi[1, 1] = c * p * phase
    psi[0, 2] = psi[2, 0] = drad * q * phase
    psi[1, 2] = psi[2, 1] = erad * q * phase
    psi[2, 2] = (metric[2, 2] * f * p + grad * tensor_xx) * phase
    psi[3, 3] = (metric[3, 3] * f * p + grad * tensor_pp) * phase
    scalar = _cancel(sum(inverse[i, j] * psi[i, j] for i in range(4) for j in range(4)))

    first = [[[sp.together(geometry.covd2(psi, e, i, j)) for j in range(4)] for i in range(4)] for e in range(4)]

    def second(e: int, h: int, i: int, j: int) -> sp.Expr:
        value = sp.diff(first[h][i][j], coords[e])
        for k in range(4):
            value -= connection[k][e][h] * first[k][i][j]
            value -= connection[k][e][i] * first[h][k][j]
            value -= connection[k][e][j] * first[h][i][k]
        return value

    raised = sp.Matrix(4, 4, lambda i, j: sp.together(sum(
        inverse[i, e] * inverse[j, h] * psi[e, h] for e in range(4) for h in range(4)
    )))
    dscalar = [sp.diff(scalar, coordinate) for coordinate in coords]
    ddscalar = sp.Matrix(4, 4, lambda i, j: sp.together(
        sp.diff(dscalar[i], coords[j]) - sum(connection[k][i][j] * dscalar[k] for k in range(4))
    ))
    boxscalar = sp.together(sum(
        inverse[e, h] * ddscalar[e, h] for e in range(4) for h in range(4) if inverse[e, h] != 0
    ))

    def operator_raw(i: int, j: int) -> sp.Expr:
        boxpsi = sum(inverse[e, h] * second(e, h, i, j) for e in range(4) for h in range(4) if inverse[e, h] != 0)
        curvature = sum(geometry.Weyl[i][k][j][l] * raised[k, l] for k in range(4) for l in range(4))
        return (boxpsi / 2 + curvature - ddscalar[i, j] / 6 - metric[i, j] * boxscalar / 12) / phase

    traceless = -b - b0 * c / 2
    substitutions = {f: traceless}
    for order in (1, 2, 3, 4):
        substitutions[sp.Derivative(f, (r, order))] = sp.diff(traceless, r, order)
    fields = [a, b, c]
    raw_rows = [operator_raw(0, 0), operator_raw(0, 1), operator_raw(1, 1)]
    coefficients: list[list[list[sp.Expr]]] = []
    for raw_row in raw_rows:
        sliced = raw_row.subs(substitutions).doit()
        row_coefficients: list[list[sp.Expr]] = []
        for field in fields:
            field_coefficients: list[sp.Expr] = []
            for order in range(5):
                target = field if order == 0 else sp.Derivative(field, (r, order))
                field_coefficients.append(strip_scalar_light(sp.diff(sliced, target)))
            if field_coefficients[3] != 0 or field_coefficients[4] != 0:
                raise RuntimeError("traceless carrier row retained derivatives above second order")
            row_coefficients.append(field_coefficients)
        coefficients.append(row_coefficients)
    second_matrix = sp.Matrix(3, 3, lambda i, j: coefficients[i][j][2])
    inverse_second = second_matrix.inv()
    variables = [(j, order) for j in range(3) for order in range(2)]
    index = {entry: k for k, entry in enumerate(variables)}
    system = sp.zeros(6)
    for j in range(3):
        system[index[(j, 0)], index[(j, 1)]] = 1
    for top in range(3):
        row_index = index[(top, 1)]
        for field_index, order in variables:
            coefficient = sum(inverse_second[top, equation] * coefficients[equation][field_index][order] for equation in range(3))
            system[row_index, index[(field_index, order)]] = _cancel(-coefficient)

    leading = sp.Matrix(6, 6, lambda i, j: sp.limit(system[i, j], r, sp.oo))
    subleading = sp.Matrix(6, 6, lambda i, j: sp.limit(r * (system[i, j] - leading[i, j]), r, sp.oo))

    def projected_powers(rate: sp.Expr) -> tuple[sp.Expr, int, int, dict[str, list[str]]]:
        right = sp.Matrix.hstack(*(leading - rate * sp.eye(6)).nullspace())
        left = sp.Matrix.hstack(*(leading.T - rate * sp.eye(6)).nullspace())
        gram = left.T * right
        effective = _matrix_cancel(gram.inv() * left.T * subleading * right)
        sigma = sp.Symbol("sigma")
        modes: dict[str, list[str]] = {}
        for power in effective.eigenvals():
            kernel = (effective - power * sp.eye(effective.rows)).nullspace()
            if len(kernel) != 1:
                raise RuntimeError("projected carrier power is not simple")
            vector = _matrix_cancel(right * kernel[0])
            pivot = next(value for value in vector if value != 0)
            vector = _matrix_cancel(vector / pivot)
            modes[sp.sstr(power)] = [sp.sstr(value) for value in vector]
        return sp.factor(effective.charpoly(sigma).as_expr()), right.shape[1], left.shape[1], modes

    def _serialize(matrix: sp.Matrix) -> list[list[str]]:
        return [[sp.sstr(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]

    zero_poly, zero_right, zero_left, zero_modes = projected_powers(sp.Integer(0))
    osc_rate = -2 * sp.I * omega
    osc_poly, osc_right, osc_left, osc_modes = projected_powers(osc_rate)
    sigma = sp.Symbol("sigma")
    expected_zero = (sigma + 1) * (sigma + 2) * (sigma + 3)
    expected_osc = (sigma + 1 + 4 * sp.I * mass * omega) * (sigma + 2 + 4 * sp.I * mass * omega) * (sigma + 3 + 4 * sp.I * mass * omega)
    if sp.factor(zero_poly - expected_zero) != 0 or sp.factor(osc_poly - expected_osc) != 0:
        raise RuntimeError(f"generic carrier power polynomial changed: {zero_poly}, {osc_poly}")
    return {
        "state": ["a", "a_prime", "b", "b_prime", "c", "c_prime"],
        "leading_matrix": _serialize(leading),
        "subleading_matrix": _serialize(subleading),
        "rates": ["0", "-2*I*omega"],
        "power_polynomials": {"zero": sp.sstr(expected_zero), "oscillatory": sp.sstr(expected_osc)},
        "powers": {
            "zero": ["-1", "-2", "-3"],
            "oscillatory": ["-1-4*I*m*omega", "-2-4*I*m*omega", "-3-4*I*m*omega"],
        },
        "right_left_dimensions": {
            "zero": [zero_right, zero_left],
            "oscillatory": [osc_right, osc_left],
        },
        "leading_modes": {"zero": zero_modes, "oscillatory": osc_modes},
        "full_first_order_system": _serialize(system),
        "dependent_source_components": {"D": sp.sstr(drad), "Ec": sp.sstr(erad), "Gc": sp.sstr(grad)},
        "lambda_independent": not zero_poly.has(lam) and not osc_poly.has(lam),
        "slice": {
            "condition": "trace psi=2*b+(1-2*m/r)*c+2*f=0",
            "status": "FORMALLY_REACHABLE_CONFORMAL_QUOTIENT_SLICE",
            "reachability_input": "Box pivots 2*I*omega*(p+1) and -2*I*omega*(p+1+4*I*m*omega), with nonzero log generalized pivots at the unique resonances",
            "scope": "real omega!=0 on the two-rate exponential-polyhomogeneous-log module",
        },
    }


def _matrix_cancel(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.applyfunc(_cancel)
