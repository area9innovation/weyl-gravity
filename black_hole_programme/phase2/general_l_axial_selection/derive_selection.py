"""Scratch-to-certificate exact recurrence for generic-ell axial selection."""
from __future__ import annotations

import sympy as sp

R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega", positive=True, real=True)
M = sp.Symbol("M", positive=True, real=True)
L = sp.Symbol("Lambda", positive=True, real=True)
I = sp.I


def cancel(x):
    return sp.factor(sp.cancel(sp.together(x)))


def rational_series(expr, depth):
    """Return coefficients d[n] of r^-n, including possible Laurent n."""
    numerator, denominator = sp.fraction(sp.cancel(expr))
    pn, pd = sp.Poly(sp.expand(numerator), R), sp.Poly(sp.expand(denominator), R)
    nmax, dmax = pn.degree(), pd.degree()
    den = [pd.coeff_monomial(R ** (dmax - k)) if dmax - k >= 0 else 0
           for k in range(depth + 1)]
    inverse = [sp.Integer(1) / den[0]]
    for k in range(1, depth + 1):
        inverse.append(cancel(-sum(den[j] * inverse[k - j]
                                   for j in range(1, k + 1)) / den[0]))
    num = [pn.coeff_monomial(R ** (nmax - k)) if nmax - k >= 0 else 0
           for k in range(depth + 1)]
    shift = nmax - dmax
    out = {}
    for k in range(depth + 1):
        value = sum(num[j] * inverse[k - j] for j in range(k + 1))
        if value != 0:
            out[k - shift] = sp.expand(value)
    return out


def carrier_slots(depth=9):
    P = sp.Function("P")(R)
    Q = sp.Function("Q")(R)
    rows = [
        sp.diff(P, R, 2)
        - (L * R - 4 * M) / (R**2 * (R - 2 * M)) * P
        + 2 * I * W * R / (R - 2 * M) * sp.diff(P, R)
        + 2 * I * M * W / (R * (R - 2 * M)) * Q,
        sp.diff(Q, R, 2)
        + 2 / (R - 2 * M) * sp.diff(P, R)
        - (L * R - 4 * M - 2 * I * W * R**2) / (R**2 * (R - 2 * M)) * Q
        + (2 * I * W * R + 2) / (R - 2 * M) * sp.diff(Q, R),
    ]
    sigma = sp.Symbol("sigma")

    def apply(row, rate, fn):
        y = sp.exp(rate * R) * R**sigma
        sub = {fn: y}
        for derivative in row.atoms(sp.Derivative):
            if derivative.expr == fn:
                sub[derivative] = sp.diff(y, R, derivative.derivative_count)
        for other in (P, Q):
            if other == fn:
                continue
            sub[other] = 0
            for derivative in row.atoms(sp.Derivative):
                if derivative.expr == other:
                    sub[derivative] = 0
        return rational_series(sp.expand(row.subs(sub).doit()
                                         / (sp.exp(rate * R) * R**sigma)), depth)

    return rows, sigma, apply


def carrier_series(rate, top, depth=5):
    rows, sigma, apply = carrier_slots(depth + 4)
    P, Q = sp.Function("P")(R), sp.Function("Q")(R)
    slots = [[apply(rows[i], rate, fn) for fn in (P, Q)] for i in range(2)]
    leading = min(min(series) for row in slots for series in row)

    def matrix(order, power):
        return sp.Matrix(2, 2, lambda i, j: cancel(
            sp.sympify(slots[i][j].get(leading + order, 0)).subs(sigma, power)))

    y0 = matrix(0, top).nullspace()[0]
    y0 = y0.applyfunc(lambda x: cancel(x / y0[0]))
    coefficients = [y0]
    pivots = []
    for n in range(1, depth + 1):
        rhs = -sum((matrix(n - j, top - j) * coefficients[j]
                    for j in range(n)), sp.zeros(2, 1))
        pivot = matrix(0, top - n)
        pivots.append(cancel(pivot.det()))
        if pivot.det() != 0:
            value = pivot.inv() * rhs
        else:
            value, parameters = pivot.gauss_jordan_solve(rhs)
            value = value.subs({parameter: 0 for parameter in parameters})
        coefficients.append(value.applyfunc(cancel))
    return coefficients, pivots


def series_derivative(data, base, rate):
    out = {}
    for n, value in data.items():
        out[n] = out.get(n, 0) + rate * value
        out[n + 1] = out.get(n + 1, 0) + (base - n) * value
    return {n: cancel(value) for n, value in out.items() if value != 0}


def series_add(*terms):
    out = {}
    for scale, shift, data in terms:
        for n, value in data.items():
            out[n - shift] = out.get(n - shift, 0) + scale * value
    return {n: cancel(value) for n, value in out.items() if value != 0}


def series_conv(a, b, maximum):
    out = {}
    for na, va in a.items():
        for nb, vb in b.items():
            if na + nb <= maximum:
                out[na + nb] = out.get(na + nb, 0) + va * vb
    return {n: cancel(value) for n, value in out.items() if value != 0}


def source_series(rate, base, carrier, depth=8):
    p = {n: carrier[n][0] for n in range(len(carrier))}
    q = {n: carrier[n][1] for n in range(len(carrier))}
    dp = series_derivative(p, base, rate)
    dq = series_derivative(q, base, rate)
    c = series_add(
        (1, 2, dp), (1, 2, dq), (I * W, 2, q),
        (2, 1, p), (2, 1, q), (-2, 1, dq), (-2, 0, q),
    )
    c = {n: cancel(value / (L - 2)) for n, value in c.items()}
    dc = series_derivative(c, base, rate)
    dc_minus_q = series_add((1, 0, dc), (-1, 0, q))
    ratio = {n: 2 * (2 * M)**n for n in range(depth + 1)}
    s2 = series_conv(ratio, dc_minus_q, depth)
    return [{n: 2 * value for n, value in c.items()}, {}, s2], c


def metric_matrix_series(depth=10):
    matrix = sp.Matrix([
        [0, (-2 * M - I * W * R**2) / R**2, (2 * M - R) / R],
        [0, 0, 1],
        [-2 / (R * (R - 2 * M)),
         (L * R + 4 * M - 2 * I * W * R**2 - 2 * R) / (R**2 * (R - 2 * M)),
         (-4 * M - 2 * I * W * R**2) / (R * (R - 2 * M))],
    ])
    return [sp.Matrix(3, 3, lambda i, j: rational_series(matrix[i, j], depth).get(k, 0))
            for k in range(depth + 1)]


def lift_series(rate, carrier_base, carrier, njet=5, unit_mass=False, substitutions=None):
    source, c = source_series(rate, carrier_base, carrier, njet + 6)
    substitutions = dict(substitutions or {})
    if substitutions:
        source = [{n: value.subs(substitutions) for n, value in row.items()} for row in source]
        c = {n: value.subs(substitutions) for n, value in c.items()}
        rate = rate.subs(substitutions) if hasattr(rate, "subs") else rate
        carrier_base = carrier_base.subs(substitutions) if hasattr(carrier_base, "subs") else carrier_base
    if unit_mass:
        source = [{n: value.subs(M, 1) for n, value in row.items()} for row in source]
        c = {n: value.subs(M, 1) for n, value in c.items()}
        rate = rate.subs(M, 1) if hasattr(rate, "subs") else rate
        carrier_base = carrier_base.subs(M, 1) if hasattr(carrier_base, "subs") else carrier_base
    kmin = min(n for row in source for n in row)
    shift = 1 - kmin
    base = carrier_base + shift
    matrices = metric_matrix_series(njet + 4)
    if substitutions:
        matrices = [matrix.subs(substitutions) for matrix in matrices]
    if unit_mass:
        matrices = [matrix.subs(M, 1) for matrix in matrices]
    b0 = matrices[0] - rate * sp.eye(3)

    def av(n, letter):
        return sp.Matrix(3, 1, lambda i, _: sp.Symbol(f"{letter}_{n}_{i}"))

    a_unknowns = [sp.Symbol(f"a_{n}_{i}") for n in range(njet + 1) for i in range(3)]
    b_unknowns = [sp.Symbol(f"b_{n}_{i}") for n in range(njet + 1) for i in range(3)]
    equations = []
    for n in range(-1, njet):
        a = av(n, "a") if 0 <= n <= njet else sp.zeros(3, 1)
        b = av(n, "b") if 0 <= n <= njet else sp.zeros(3, 1)
        lhs_log = (base - n) * b
        lhs_plain = (base - n) * a + b
        rhs_log = sp.zeros(3, 1)
        rhs_plain = sp.zeros(3, 1)
        for k in range(n + 2):
            j = n + 1 - k
            if 0 <= j <= njet:
                mk = b0 if k == 0 else matrices[k]
                rhs_log += mk * av(j, "b")
                rhs_plain += mk * av(j, "a")
        sv = sp.Matrix(3, 1, lambda i, _: source[i].get(n + 1 - shift, 0))
        equations.extend(sp.expand(x) for x in lhs_log - rhs_log)
        equations.extend(sp.expand(x) for x in lhs_plain - rhs_plain - sv)
    unknowns = a_unknowns + b_unknowns
    A, rhs = sp.linear_eq_to_matrix(equations, unknowns)
    sol, parameters = A.gauss_jordan_solve(rhs)
    sol = sol.subs({parameter: 0 for parameter in parameters})
    na = len(a_unknowns)
    aa = [sp.Matrix(3, 1, lambda i, _: cancel(sol[3 * n + i]))
          for n in range(njet + 1)]
    bb = [sp.Matrix(3, 1, lambda i, _: cancel(sol[na + 3 * n + i]))
          for n in range(njet + 1)]
    residual = (A * sol - rhs).applyfunc(cancel)
    if residual != sp.zeros(residual.rows, 1):
        raise RuntimeError("lift recurrence residual")
    return base, aa, bb, source, c, len(parameters)


def source_master(rate, carrier_base, carrier):
    source, c = source_series(rate, carrier_base, carrier, len(carrier) + 4)
    q = {n: carrier[n][1] for n in range(len(carrier))}
    dc = series_derivative(c, carrier_base, rate)
    ddc = series_derivative(dc, carrier_base, rate)
    dq = series_derivative(q, carrier_base, rate)
    rhs = series_add((2, 2, ddc), (-2, 2, dq), (-4, 1, q),
                     (4, 1, dc), (-4, 0, c))
    return rhs, c, source


def poly_derivative(data, base, rate):
    """Differentiate dict n -> (plain, log) at fixed exponential/base."""
    out = {}
    for n, (a, b) in data.items():
        p, q = out.get(n, (0, 0))
        out[n] = (p + rate * a, q + rate * b)
        p, q = out.get(n + 1, (0, 0))
        out[n + 1] = (p + (base - n) * a + b, q + (base - n) * b)
    return {n: (sp.expand(a), sp.expand(b)) for n, (a, b) in out.items()
            if a != 0 or b != 0}


def poly_add(*terms):
    out = {}
    for scale, shift, data in terms:
        for n, (a, b) in data.items():
            p, q = out.get(n - shift, (0, 0))
            out[n - shift] = (p + scale * a, q + scale * b)
    return {n: (sp.expand(a), sp.expand(b)) for n, (a, b) in out.items()
            if a != 0 or b != 0}


def scalar_master_lift(rate, carrier_base, carrier, njet=7, unit_mass=True):
    rhs0, c0, state_source0 = source_master(rate, carrier_base, carrier)
    subs = {M: 1} if unit_mass else {}
    rate = rate.subs(subs) if hasattr(rate, "subs") else rate
    carrier_base = carrier_base.subs(subs) if hasattr(carrier_base, "subs") else carrier_base
    rhs = {n: sp.expand(v.subs(subs)) for n, v in rhs0.items()}
    c = {n: sp.expand(v.subs(subs)) for n, v in c0.items()}
    state_source = [{n: sp.expand(v.subs(subs)) for n, v in row.items()}
                    for row in state_source0]
    first = min(n for n, value in rhs.items() if value != 0)
    fbase = carrier_base - first - 1
    aa = [sp.Symbol(f"fa_{n}") for n in range(njet + 1)]
    bb = [sp.Symbol(f"fb_{n}") for n in range(njet + 1)]
    fdata = {n: (aa[n], bb[n]) for n in range(njet + 1)}
    df = poly_derivative(fdata, fbase, rate)
    ddf = poly_derivative(df, fbase, rate)
    operated = poly_add(
        (1, 2, ddf), (-2, 1, ddf),
        (2 * I * W, 2, df), (2, 1, df), (2, 0, df),
        (6 * I * W, 1, fdata), (-L, 0, fdata),
    )
    source_relative = {n - first - 1: value for n, value in rhs.items()}
    equations = []
    # The maximal current-leading jet only needs output through njet-2;
    # two extra equations fix resonant freedoms without reading the omitted tail.
    for n in range(-1, njet - 1):
        plain, log = operated.get(n, (0, 0))
        equations.append(sp.expand(log))
        equations.append(sp.expand(plain - source_relative.get(n, 0)))
    matrix, vector = sp.linear_eq_to_matrix(equations, aa + bb)
    solution, parameters = matrix.gauss_jordan_solve(vector)
    solution = solution.subs({parameter: 0 for parameter in parameters})
    fa = [cancel(solution[n]) for n in range(njet + 1)]
    fb = [cancel(solution[njet + 1 + n]) for n in range(njet + 1)]
    return {
        "rate": rate, "carrier_base": carrier_base, "F_base": fbase,
        "F_plain": fa, "F_log": fb, "rhs": rhs,
        "rhs_first": first, "c": c, "state_source": state_source,
        "free_parameters_set_zero": len(parameters),
    }


def corrected_x0_lift(depth=5):
    """Canonical rate-zero lift; the F~r^-3 Einstein freedom is set to zero."""
    carrier, _ = carrier_series(sp.Integer(0), sp.Integer(0), depth + 2)
    rhs, c, _ = source_master(0, 0, carrier)
    f = []
    base = sp.Integer(-2)
    for n in range(depth + 1):
        k = base - n
        pivot = 2 * I * W * (k + 3)
        previous = ((base - n + 1) * (base - n + 2) - L) * f[n - 1] if n else 0
        lower = (-2 * M * (base - n + 2) * (base - n)) * f[n - 2] if n >= 2 else 0
        target = rhs.get(1 + n, 0)
        if n == 1:
            obstruction = cancel(target - previous - lower)
            if obstruction != 0:
                raise RuntimeError(f"rate-zero F resonance obstruction: {obstruction}")
            f.append(sp.Integer(0))
        else:
            f.append(cancel((target - previous - lower) / pivot))
    h1 = [cancel(-f[n] / (n + 1)) for n in range(len(f))]
    # Reconstruct H0' = (-i*w-2M/r^2)H1+(-1+2M/r)F+2c.
    g = dict(c)
    g = {n: 2 * value for n, value in g.items()}
    for n, value in enumerate(h1):
        g[n + 1] = g.get(n + 1, 0) - I * W * value
        g[n + 3] = g.get(n + 3, 0) - 2 * M * value
    for n, value in enumerate(f):
        g[n + 2] = g.get(n + 2, 0) - value
        g[n + 3] = g.get(n + 3, 0) + 2 * M * value
    g = {n: cancel(value) for n, value in g.items() if value != 0}
    log_obstruction = cancel(g.get(1, 0))
    h0 = {}
    for j, value in g.items():
        if j == 1:
            continue
        h0[j + 1] = cancel(value / (1 - j))
    # H0' cannot determine the constant coefficient.  The original F' row
    # fixes it after the H1 integration constant (Einstein shift) is set to 0.
    h0[2] = cancel((L**2 - 2 * L - 4 * I * M * W) /
                   (4 * W**2 * (L - 2)))
    return {
        "carrier": carrier, "F": f, "H1_base": -1, "H1": h1,
        "H0_base": 2, "H0": h0, "H0_log_obstruction": log_obstruction,
        "c": c,
    }


def main():
    for name, rate, top in (("X0", 0, 0), ("X2", -2 * I * W, -4 * I * M * W)):
        print("carrier", name)
        carrier, pivots = carrier_series(rate, top, 5)
        print("head", carrier[:3])
        print("pivots", pivots[:4])
        print("scalar lift", name)
        lift = scalar_master_lift(rate, top, carrier, 7, True)
        print("F base", lift["F_base"], "rhs first", lift["rhs_first"],
              "params", lift["free_parameters_set_zero"])
        print("F A", lift["F_plain"])
        print("F B", lift["F_log"])


if __name__ == "__main__":
    main()
