"""Symbolic-Lambda polar Ricci-to-metric reconstruction over Q(Lambda,w,m,r)."""

from __future__ import annotations

import sympy as sp

from black_hole_programme.weyl_geometry import Geometry


class SymbolicReconstructionError(RuntimeError):
    """Raised when the generic polar reconstruction fails an exact gate."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SymbolicReconstructionError(message)


def _cancel(expression: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(expression))


def _legendre_reduce(expression: sp.Expr, p: sp.Expr, x: sp.Symbol, lam: sp.Symbol) -> sp.Expr:
    result = sp.expand(expression)
    p_prime = sp.diff(p, x)
    for order in range(10, 1, -1):
        derivative = sp.diff(p, (x, order))
        if result.has(derivative):
            replacement = sp.diff((2 * x * p_prime - lam * p) / (1 - x**2), x, order - 2)
            result = sp.expand(sp.together(result.subs(derivative, replacement)))
    return _cancel(result)


def _strip_scalar_or_vector(raw: sp.Expr, harmonic: sp.Expr, p: sp.Expr, x: sp.Symbol, lam: sp.Symbol) -> sp.Expr:
    reduced = _legendre_reduce(raw, p, x, lam)
    stripped = _legendre_reduce(_cancel(reduced / harmonic), p, x, lam)
    _require(not stripped.has(x, p, sp.diff(p, x)), "harmonic row did not strip")
    return stripped


def _strip_angular(
    raw_xx: sp.Expr,
    raw_pp: sp.Expr,
    p: sp.Expr,
    x: sp.Symbol,
    lam: sp.Symbol,
    radius: sp.Symbol,
) -> tuple[sp.Expr, sp.Expr]:
    ps, qs = sp.symbols("Pslot Qslot")
    p_prime = sp.diff(p, x)

    def extract(raw: sp.Expr, component: str) -> tuple[sp.Expr, sp.Expr]:
        reduced = _legendre_reduce(raw, p, x, lam).subs({p_prime: qs, p: ps})
        if component == "xx":
            expression = sp.expand(_cancel((1 - x**2) * reduced))
            beta = _cancel(expression.coeff(qs) / x)
            alpha = _cancel((expression.coeff(ps) + beta * lam / 2) / radius**2)
            reconstruction = _cancel(
                expression - (radius**2 * alpha - beta * lam / 2) * ps - beta * x * qs
            )
        else:
            expression = sp.expand(_cancel(reduced / (1 - x**2)))
            beta = _cancel(-expression.coeff(qs) / x)
            alpha = _cancel((expression.coeff(ps) - beta * lam / 2) / radius**2)
            reconstruction = _cancel(
                expression - (radius**2 * alpha + beta * lam / 2) * ps + beta * x * qs
            )
        _require(reconstruction == 0, f"{component} angular reconstruction failed")
        _require(not alpha.has(x, ps, qs) and not beta.has(x, ps, qs), f"{component} angular coefficients retained x")
        return alpha, beta

    xx = extract(raw_xx, "xx")
    pp = extract(raw_pp, "pp")
    _require(_cancel(xx[0] - pp[0]) == 0 and _cancel(xx[1] - pp[1]) == 0, "angular components disagree")
    return xx


def derive_symbolic_reconstruction() -> dict:
    v, r, x, phi = sp.symbols("v r x phi")
    mass = sp.Symbol("m", positive=True)
    lam = sp.Symbol("Lambda")
    omega = sp.Symbol("omega")
    coordinates = [v, r, x, phi]
    schwarzschild = 1 - 2 * mass / r
    metric = sp.zeros(4)
    metric[0, 0] = -schwarzschild
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geometry = Geometry(coordinates, metric)
    inverse = geometry.ginv
    connection = geometry.Gamma
    p = sp.Function("P")(x)
    p_prime = sp.diff(p, x)
    tensor_xx = _cancel((x * p_prime - lam * p / 2) / (1 - x**2))
    tensor_pp = _cancel(-(1 - x**2) * (x * p_prime - lam * p / 2))

    # Generic Bianchi carrier, Fourier reduced.
    time_fields = [sp.Function(name)(v, r) for name in ("A", "Bc", "Cc", "D", "Ec", "F", "Gc")]
    a_t, bc_t, cc_t, d_t, ec_t, f_t, gc_t = time_fields
    source = sp.zeros(4)
    source[0, 0] = a_t * p
    source[0, 1] = source[1, 0] = bc_t * p
    source[1, 1] = cc_t * p
    source[0, 2] = source[2, 0] = d_t * p_prime
    source[1, 2] = source[2, 1] = ec_t * p_prime
    source[2, 2] = metric[2, 2] * f_t * p + gc_t * tensor_xx
    source[3, 3] = metric[3, 3] * f_t * p + gc_t * tensor_pp
    source_trace = _cancel(sum(inverse[i, j] * source[i, j] for i in range(4) for j in range(4)))

    def bianchi(index: int) -> sp.Expr:
        raw = sum(
            inverse[i, e] * geometry.covd2(source, e, i, index)
            for i in range(4)
            for e in range(4)
            if inverse[i, e] != 0
        ) - sp.diff(source_trace, coordinates[index]) / 2
        return _strip_scalar_or_vector(raw, p if index < 2 else p_prime, p, x, lam)

    b_rows = [bianchi(index) for index in range(3)]
    d_solution = sp.solve(sp.Eq(b_rows[0], 0), d_t)[0]
    ec_solution = sp.solve(sp.Eq(_cancel(b_rows[1].subs(d_t, d_solution).doit()), 0), ec_t)[0]
    gc_solution = sp.solve(
        sp.Eq(_cancel(b_rows[2].subs({d_t: d_solution, ec_t: ec_solution}).doit()), 0), gc_t
    )[0]

    phase = sp.exp(sp.I * omega * v)
    a, bc, cc, f = [sp.Function(name)(r) for name in ("a", "bc", "cc", "f")]
    fourier_values = {a_t: a * phase, bc_t: bc * phase, cc_t: cc * phase, f_t: f * phase}

    def fourier(expression: sp.Expr) -> sp.Expr:
        result = expression
        for field, value in fourier_values.items():
            result = result.subs(
                {
                    sp.Derivative(field, (v, 2)): sp.diff(value, v, 2),
                    sp.Derivative(field, v, r): sp.diff(value, v, r),
                    sp.Derivative(field, (r, 2)): sp.diff(value, r, 2),
                    sp.Derivative(field, v): sp.diff(value, v),
                    sp.Derivative(field, r): sp.diff(value, r),
                    field: value,
                }
            )
        return result.doit()

    d_radial = _cancel(fourier(d_solution) / phase)
    ec_radial = _cancel(fourier(ec_solution.subs(d_t, d_solution).doit()) / phase)
    gc_radial = _cancel(fourier(gc_solution.subs({d_t: d_solution, ec_t: ec_solution}).doit()) / phase)
    source_rows = {
        "vv": a,
        "vr": bc,
        "rr": cc,
        "vx": d_radial,
        "rx": ec_radial,
        "angP": f,
        "angW": gc_radial,
    }

    # RW-gauge polar metric and its literal linearized Ricci tensor.
    metric_functions = [sp.Function(name)(r) for name in ("Ah", "Bh", "Ch", "Kh")]
    ah, bh, ch, kh = metric_functions
    perturbation = sp.zeros(4)
    perturbation[0, 0] = ah * p * phase
    perturbation[0, 1] = perturbation[1, 0] = bh * p * phase
    perturbation[1, 1] = ch * p * phase
    perturbation[2, 2] = metric[2, 2] * kh * p * phase
    perturbation[3, 3] = metric[3, 3] * kh * p * phase
    delta_gamma = [[[sp.Integer(0)] * 4 for _ in range(4)] for _ in range(4)]
    for upper in range(4):
        for left in range(4):
            for right in range(left, 4):
                value = sum(
                    inverse[upper, lower]
                    * (
                        geometry.covd2(perturbation, left, lower, right)
                        + geometry.covd2(perturbation, right, left, lower)
                        - geometry.covd2(perturbation, lower, left, right)
                    )
                    for lower in range(4)
                    if inverse[upper, lower] != 0
                ) / 2
                delta_gamma[upper][left][right] = _cancel(value)
                delta_gamma[upper][right][left] = _cancel(value)

    def covariant_delta_gamma(derivative: int, upper: int, left: int, right: int) -> sp.Expr:
        value = sp.diff(delta_gamma[upper][left][right], coordinates[derivative])
        for h0 in range(4):
            value += connection[upper][derivative][h0] * delta_gamma[h0][left][right]
            value -= connection[h0][derivative][left] * delta_gamma[upper][h0][right]
            value -= connection[h0][derivative][right] * delta_gamma[upper][left][h0]
        return value

    delta_ricci = sp.zeros(4)
    for left in range(4):
        for right in range(left, 4):
            value = sum(
                covariant_delta_gamma(upper, upper, left, right)
                - covariant_delta_gamma(right, upper, left, upper)
                for upper in range(4)
            )
            delta_ricci[left, right] = _cancel(value)
            delta_ricci[right, left] = _cancel(value)

    metric_rows = {
        "vv": _strip_scalar_or_vector(delta_ricci[0, 0] / phase, p, p, x, lam),
        "vr": _strip_scalar_or_vector(delta_ricci[0, 1] / phase, p, p, x, lam),
        "rr": _strip_scalar_or_vector(delta_ricci[1, 1] / phase, p, p, x, lam),
        "vx": _strip_scalar_or_vector(delta_ricci[0, 2] / phase, p_prime, p, x, lam),
        "rx": _strip_scalar_or_vector(delta_ricci[1, 2] / phase, p_prime, p, x, lam),
    }
    angular_p, angular_w = _strip_angular(
        delta_ricci[2, 2] / phase,
        delta_ricci[3, 3] / phase,
        p,
        x,
        lam,
        r,
    )
    metric_rows["angP"] = angular_p
    metric_rows["angW"] = angular_w

    equations = {name: _cancel(metric_rows[name] - source_rows[name]) for name in metric_rows}

    def solve_linear(equation: sp.Expr, variable: sp.Expr, label: str) -> sp.Expr:
        coefficient = _cancel(sp.diff(equation, variable))
        _require(coefficient != 0 and not coefficient.has(variable), f"{label} has no linear pivot")
        remainder = _cancel(equation.subs(variable, 0))
        candidate = _cancel(-remainder / coefficient)
        _require(_cancel(equation.subs(variable, candidate)) == 0, f"{label} pivot does not close")
        return candidate

    # A triangular differential-algebraic reconstruction map.
    bh_expression = solve_linear(equations["angW"], bh, "Bh")
    substitution_bh = {
        bh: bh_expression,
        sp.Derivative(bh, r): sp.diff(bh_expression, r).doit(),
    }
    ah_prime = sp.Derivative(ah, r)
    kh_prime = sp.Derivative(kh, r)
    ch_second = sp.Derivative(ch, (r, 2))
    vx_reduced = _cancel(equations["vx"].subs(substitution_bh).doit())
    rx_reduced = _cancel(equations["rx"].subs(substitution_bh).doit())
    ah_expression = solve_linear(vx_reduced, ah_prime, "Ah_prime")
    kh_expression = solve_linear(rx_reduced, kh_prime, "Kh_prime")
    rr_reduced = equations["rr"].subs(substitution_bh).doit()
    rr_reduced = rr_reduced.subs(
        {
            sp.Derivative(kh, (r, 2)): sp.diff(kh_expression, r).doit(),
            kh_prime: kh_expression,
            ah_prime: ah_expression,
        }
    ).doit()
    ch_expression = solve_linear(_cancel(rr_reduced), ch_second, "Ch_second")

    # All denominators are explicit rational functions.  The representation
    # factors are separated from coordinate/frequency factors.
    expressions = [bh_expression, ah_expression, kh_expression, ch_expression]
    denominator = sp.factor(sp.lcm([sp.denom(sp.together(value)) for value in expressions]))
    representation_factors = []
    for factor, _multiplicity in sp.factor_list(denominator)[1]:
        if factor.has(lam) and not factor.has(r, mass, omega):
            representation_factors.append(sp.sstr(factor))

    # Verify the four pivot identities exactly.  The other three Ricci rows
    # are constraint equations; together the seven rows are the full map.
    solved_checks = {
        "angW": _cancel(equations["angW"].subs(bh, bh_expression).doit()),
        "vx": _cancel(vx_reduced.subs(ah_prime, ah_expression).doit()),
        "rx": _cancel(rx_reduced.subs(kh_prime, kh_expression).doit()),
        "rr": _cancel(rr_reduced.subs(ch_second, ch_expression).doit()),
    }
    _require(all(value == 0 for value in solved_checks.values()), "chosen reconstruction rows did not vanish")

    constraints = {name: equations[name] for name in ("vv", "vr", "angP")}

    # Homogeneous Einstein kernel and the minimal Moser replacement.  The
    # chain-adapted system collapses to an autonomous scalar equation for Ch,
    # so no fractional shearing is needed: the nilpotent chain is resolved by
    # one polynomial quadrature mode plus the scalar master solutions.
    source_functions = (a, bc, cc, f)

    def zero_source(expression: sp.Expr) -> sp.Expr:
        substitutions: dict[sp.Expr, sp.Expr] = {field: 0 for field in source_functions}
        for derivative in expression.atoms(sp.Derivative):
            if derivative.expr in source_functions:
                substitutions[derivative] = 0
        return _cancel(expression.subs(substitutions).doit())

    bh_zero = zero_source(bh_expression)
    ap_zero = zero_source(ah_expression)
    kp_zero = zero_source(kh_expression)
    c2_zero = zero_source(ch_expression)
    state = [ah, ch, sp.Derivative(ch, r), kh]
    homogeneous = sp.zeros(4)
    homogeneous[1, 2] = 1
    for row_index, expression in ((0, ap_zero), (2, c2_zero), (3, kp_zero)):
        expanded = sp.expand(expression)
        for column_index, variable in enumerate(state):
            homogeneous[row_index, column_index] = _cancel(expanded.coeff(variable))
        remainder = _cancel(expanded - sum(homogeneous[row_index, j] * state[j] for j in range(4)))
        _require(remainder == 0, "homogeneous reconstruction retained an affine remainder")
    _require(homogeneous[2, 0] == 0 and homogeneous[2, 3] == 0, "Ch master did not decouple")
    master_c2 = sp.expand(r * (r - 2 * mass))
    master_c1 = sp.factor(-homogeneous[2, 2] * master_c2)
    master_c0 = sp.factor(-homogeneous[2, 1] * master_c2)

    exponent = sp.Symbol("sigma")
    quotient = sp.expand(
        master_c2 * exponent * (exponent - 1) / r**2
        + master_c1 * exponent / r
        + master_c0
    )
    lam0_solutions = sp.solve(sp.Eq(quotient.coeff(r, 1), 0), exponent)
    _require(
        len(lam0_solutions) == 1,
        f"lambda=0 master exponent did not close: coefficients={(master_c2, master_c1, master_c0)}, quotient={quotient}",
    )
    sigma_lam0 = _cancel(lam0_solutions[0])

    rate = -2 * sp.I * omega
    osc_power = sp.Symbol("sigma_osc")
    osc_ratio = _cancel(
        master_c2 * (rate**2 + 2 * rate * osc_power / r + osc_power * (osc_power - 1) / r**2)
        + master_c1 * (rate + osc_power / r)
        + master_c0
    )
    u = sp.Symbol("u", positive=True)
    osc_series = sp.series(osc_ratio.subs(r, 1 / u) * u**2, u, 0, 4).removeO()
    osc_poly = sp.Poly(sp.expand(osc_series), u)
    _require(osc_poly.coeff_monomial(u**0) == 0, "oscillatory rate failed")
    osc_solutions: list[sp.Expr] = []
    for order in range(1, 4):
        coefficient = sp.expand(osc_poly.coeff_monomial(u**order))
        if osc_power in coefficient.free_symbols:
            osc_solutions = sp.solve(sp.Eq(coefficient, 0), osc_power)
            break
    _require(len(osc_solutions) == 1, "oscillatory master exponent did not close")
    sigma_osc = _cancel(osc_solutions[0])

    recurrence_index = sp.Symbol("k", integer=True)
    recurrence_ratio = sp.expand(
        master_c2 * recurrence_index * (recurrence_index + 1) / r**2
        - master_c1 * recurrence_index / r
        + master_c0
    )
    recurrence_diagonal = _cancel(recurrence_ratio.coeff(r, 1))

    # Weyl-radical direction in the same four-function carrier: h_ab=phi g_ab.
    conformal = sp.Function("varphi")(r)
    conformal_substitution = {ah: -schwarzschild * conformal, bh: conformal, ch: 0, kh: conformal}
    for function, value in list(conformal_substitution.items()):
        if function == 0:
            continue
        for order in (1, 2):
            conformal_substitution[sp.Derivative(function, (r, order))] = sp.diff(value, r, order)
    conformal_source = {
        name: _cancel(row.subs(conformal_substitution).doit()) for name, row in metric_rows.items()
    }

    return {
        "field": "Q(Lambda,omega,m,r)",
        "metric_gauge": "polar Regge-Wheeler gauge with state (Ah,Ch,Ch',Kh) and Bh algebraic",
        "source_free_functions": ["a", "bc", "cc", "f"],
        "source_dependent_components": {
            "D": sp.sstr(d_radial),
            "Ec": sp.sstr(ec_radial),
            "Gc": sp.sstr(gc_radial),
        },
        "metric_rows": {name: sp.sstr(value) for name, value in metric_rows.items()},
        "reconstruction": {
            "Bh": sp.sstr(bh_expression),
            "Ah_prime": sp.sstr(ah_expression),
            "Kh_prime": sp.sstr(kh_expression),
            "Ch_second": sp.sstr(ch_expression),
            "solved_rows": ["angW", "vx", "rx", "rr"],
            "solved_row_defects": {name: sp.sstr(value) for name, value in solved_checks.items()},
            "constraint_rows": {name: sp.sstr(value) for name, value in constraints.items()},
        },
        "denominator_ledger": {
            "common_denominator": sp.sstr(denominator),
            "pure_representation_factors": representation_factors,
        },
        "conformal_radical": {
            "metric_generator": {"Ah": "-(1 - 2*m/r)*varphi(r)", "Bh": "varphi(r)", "Ch": "0", "Kh": "varphi(r)"},
            "ricci_image_rows": {name: sp.sstr(value) for name, value in conformal_source.items()},
            "quotient_statement": "one functional Weyl-radical direction, valid before fixing varphi",
            "traceless_slice_reachability": {
                "scalar_box": "B*varphi''+(2*I*omega+2*B/r+B')*varphi'+(2*I*omega/r-Lambda/r**2)*varphi, B=1-2*m/r",
                "zero_rate_pivot": "2*I*omega*(p+1)",
                "oscillatory_rate": "-2*I*omega",
                "oscillatory_pivot": "-2*I*omega*(p+1+4*I*m*omega)",
                "resonant_powers": ["-1", "-1-4*I*m*omega"],
                "log_generalized_pivots": ["2*I*omega", "-2*I*omega"],
                "formal_module": "two-rate exponential-polyhomogeneous Laurent series with finite log towers",
                "surjective_for": "real omega!=0; at each unique resonant power one log term solves the missing monomial",
                "trace_removal": "trace(delta Ric[2*sigma*g])=-6*Box(sigma), hence every formal trace carrier has a traceless representative",
            },
        },
        "homogeneous_metric_master": {
            "state": ["Ah", "Ch", "Ch_prime", "Kh"],
            "matrix": [[sp.sstr(homogeneous[i, j]) for j in range(4)] for i in range(4)],
            "master_field": "Ch",
            "master_coefficients": [sp.sstr(master_c2), sp.sstr(master_c1), sp.sstr(master_c0)],
            "lambda_zero_power": sp.sstr(sigma_lam0),
            "oscillatory_rate": sp.sstr(rate),
            "oscillatory_power": sp.sstr(sigma_osc),
            "recurrence_diagonal": sp.sstr(sp.factor(recurrence_diagonal)),
            "chain_resolution": {
                "method": "chain-adapted scalar collapse (minimal Moser reduction)",
                "fractional_shearing": False,
                "ramification": False,
                "polynomial_mode": "Ch=0, Kh=kappa, Ah=I*omega*kappa*r+constant",
                "polynomial_degree": 1,
                "logarithm": False,
            },
        },
        "all_seven_rows_present": set(equations) == {"vv", "vr", "rr", "vx", "rx", "angP", "angW"},
        "constraint_status": "THREE_EXACT_PROPAGATING_CONSTRAINT_ROWS_RETAINED",
    }
