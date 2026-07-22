"""Exact generic-ell axial Schwarzschild asymptotic operators.

This producer stays at LOCAL-ALGEBRAIC + REDUCED-MODE scope.  It derives
the axial trace-free Ricci-carrier system and the homogeneous metric system
with ``Lambda = ell*(ell+1)`` kept symbolic.  It then classifies their formal
large-radius exponential rates, power exponents, recurrence pivots and exact
exceptional locus.  It computes no Lee--Wald current.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
BH = HERE.parents[1]
ROOT = BH.parent
if str(BH) not in sys.path:
    sys.path.insert(0, str(BH))

from linearized_bach import LinearizedBach
from weyl_geometry import Geometry
from bh2_general_l_structural import _legendre_reduce


CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
RECEIPT = HERE / "receipt.json"

INPUTS = {
    "general_l_structural": BH / "certificates" / "BH2_GENERAL_L_STRUCTURAL.json",
    "symbolic_indicial": BH / "certificates" / "BH2C_SYMBOLIC_INDICIAL.json",
    "metric_all_orders": BH / "certificates" / "BH2C_METRIC_ALL_ORDERS.json",
    "symbolic_flux": BH / "certificates" / "BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json",
    "omega_zero": BH / "certificates" / "BH2_OMEGA_ZERO.json",
    "endpoint_assembly": BH / "certificates" / "BH_ENDPOINT_NONSELECTION_ASSEMBLY.json",
    "asymptotic_jordan_l2": BH / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json",
}


class AsymptoticError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AsymptoticError(message)


def _cancel(expr):
    return sp.cancel(sp.together(expr))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_metric_system(geo_cls=Geometry):
    """Return the generic-Lambda EF system Y' = M_h Y, Y=(H0,H1,H1')."""
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    mass = sp.Symbol("M", positive=True)
    omega = sp.Symbol("omega")
    Lambda = sp.Symbol("Lambda")
    B = 1 - 2 * mass / r
    metric = sp.zeros(4, 4)
    metric[0, 0] = -B
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geo = geo_cls([v, r, x, ph], metric)
    P = sp.Function("Pell")(x)
    S = -(1 - x**2) * sp.diff(P, x)
    H2ang = Lambda * P - 2 * x * sp.diff(P, x)
    h0 = sp.Function("h0")(v, r)
    h1 = sp.Function("h1")(v, r)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0 * S
    h[1, 3] = h[3, 1] = h1 * S
    lb = LinearizedBach(geo)
    lb.build(h)
    rx = _legendre_reduce(lb.dRic[2, 3], P)
    rr = _legendre_reduce(lb.dRic[1, 3], P)
    Ps, Pps = sp.symbols("Ps Pps")
    rx = _cancel(rx.subs({P: Ps, sp.diff(P, x): Pps}) / (Lambda * Ps - 2 * x * Pps))
    rr = _cancel(rr.subs({P: Ps, sp.diff(P, x): Pps}) / (-(1 - x**2) * Pps))
    _require(not rx.has(x, Ps, Pps), "metric xphi harmonic did not strip")
    _require(not rr.has(x, Ps, Pps), "metric rphi harmonic did not strip")

    H0, H1 = sp.Function("H0")(r), sp.Function("H1")(r)
    phase = sp.exp(sp.I * omega * v)
    fourier = {h0: H0 * phase, h1: H1 * phase}
    rx = _cancel(sp.expand(rx.subs(fourier).doit() / phase))
    rr = _cancel(sp.expand(rr.subs(fourier).doit() / phase))
    H0p = sp.solve(sp.Eq(rx, 0), sp.Derivative(H0, r))[0]
    H0pp = sp.diff(H0p, r).subs(sp.Derivative(H0, r), H0p)
    row = rr.subs({sp.Derivative(H0, (r, 2)): H0pp,
                   sp.Derivative(H0, r): H0p}).doit()
    H1pp = sp.solve(sp.Eq(sp.expand(row), 0), sp.Derivative(H1, (r, 2)))[0]
    state = [H0, H1, sp.Derivative(H1, r)]
    matrix = sp.zeros(3, 3)
    e0, e2 = sp.expand(H0p), sp.expand(H1pp)
    for j, entry in enumerate(state):
        matrix[0, j] = _cancel(e0.coeff(entry))
        matrix[2, j] = _cancel(e2.coeff(entry))
    matrix[1, 2] = 1
    return matrix, r, omega, Lambda, mass


def build_carrier_system(geo_cls=Geometry):
    """Return the generic-Lambda EF Ricci-carrier system Z' = M_psi Z.

    The state is ``(P,P',Q,Q')`` after solving the divergence constraint for
    the third axial tensor-harmonic coefficient.
    """
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    mass = sp.Symbol("M", positive=True)
    omega = sp.Symbol("omega")
    Lambda = sp.Symbol("Lambda")
    B = 1 - 2 * mass / r
    metric = sp.zeros(4, 4)
    metric[0, 0] = -B
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geo = geo_cls([v, r, x, ph], metric)
    gi = geo.ginv
    Pleg = sp.Function("Pell")(x)
    Plegp = sp.diff(Pleg, x)
    S = -(1 - x**2) * Plegp
    H2ang = Lambda * Pleg - 2 * x * Plegp
    p, q, c = (sp.Function("p")(v, r), sp.Function("q")(v, r),
               sp.Function("c")(v, r))
    psi = sp.zeros(4, 4)
    psi[0, 3] = psi[3, 0] = p * S
    psi[1, 3] = psi[3, 1] = q * S
    psi[2, 3] = psi[3, 2] = c * H2ang
    divergence = sum(gi[a, e] * geo.covd2(psi, e, a, 3)
                     for a in range(4) for e in range(4) if gi[a, e] != 0)
    divergence = _legendre_reduce(divergence, Pleg)
    Ps, Pps = sp.symbols("Ps Pps")
    csol = sp.solve(sp.Eq(_cancel(divergence.subs({Pleg: Ps, Plegp: Pps})), 0), c)
    _require(len(csol) == 1, "carrier divergence constraint did not solve uniquely")
    cexpr = sp.expand(csol[0]).subs({Ps: Pleg, Pps: Plegp})
    psi = sp.Matrix(4, 4, lambda i, j: _cancel(psi.subs(c, cexpr).doit()[i, j]))
    Gamma = geo.Gamma
    first = [[[_cancel(geo.covd2(psi, e, a, b)) for b in range(4)]
              for a in range(4)] for e in range(4)]

    def second(e, f, a, b):
        value = sp.diff(first[f][a][b], [v, r, x, ph][e])
        for h in range(4):
            value -= Gamma[h][e][f] * first[h][a][b]
            value -= Gamma[h][e][a] * first[f][h][b]
            value -= Gamma[h][e][b] * first[f][a][h]
        return value

    def operator_row(a, b):
        box = sum(gi[e, f] * second(e, f, a, b)
                  for e in range(4) for f in range(4) if gi[e, f] != 0)
        curvature = sum(
            geo.Weyl[a][cc][b][d]
            * sum(gi[cc, e] * gi[d, f] * psi[e, f]
                  for e in range(4) for f in range(4))
            for cc in range(4) for d in range(4)
        )
        return _cancel(box / 2 + curvature)

    lv = _legendre_reduce(_cancel(_legendre_reduce(operator_row(0, 3), Pleg) / S), Pleg)
    lr = _legendre_reduce(_cancel(_legendre_reduce(operator_row(1, 3), Pleg) / S), Pleg)
    _require(not lv.has(x, Pleg), "carrier vphi harmonic did not strip")
    _require(not lr.has(x, Pleg), "carrier rphi harmonic did not strip")
    Pr, Qr = sp.Function("Pc")(r), sp.Function("Qc")(r)
    phase = sp.exp(sp.I * omega * v)
    lv = sp.expand(_cancel(lv.subs({p: Pr * phase, q: Qr * phase}).doit() / phase))
    lr = sp.expand(_cancel(lr.subs({p: Pr * phase, q: Qr * phase}).doit() / phase))
    P2, Q2 = sp.Derivative(Pr, (r, 2)), sp.Derivative(Qr, (r, 2))
    solved = sp.solve([sp.Eq(lv, 0), sp.Eq(lr, 0)], [P2, Q2], dict=True)
    _require(len(solved) == 1, "carrier principal system not uniquely solvable")
    solved = solved[0]
    state = [Pr, sp.Derivative(Pr, r), Qr, sp.Derivative(Qr, r)]
    matrix = sp.zeros(4, 4)
    matrix[0, 1] = matrix[2, 3] = 1
    for row, expr in ((1, sp.expand(solved[P2])), (3, sp.expand(solved[Q2]))):
        for j, entry in enumerate(state):
            matrix[row, j] = _cancel(expr.coeff(entry))
    return matrix, r, omega, Lambda, mass


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(_cancel(matrix[i, j])) for j in range(matrix.cols)]
            for i in range(matrix.rows)]


def _inverse_series(numerator: sp.Poly, denominator: sp.Poly,
                    variable: sp.Symbol, depth: int) -> dict[int, sp.Expr]:
    """Laurent coefficients at infinity for an exact rational function."""
    nmax = max(monomial[0] for monomial in numerator.monoms())
    dmax = max(monomial[0] for monomial in denominator.monoms())
    den = [denominator.coeff_monomial(variable ** (dmax - k))
           if dmax - k >= 0 else sp.Integer(0) for k in range(depth + 1)]
    inverse = [sp.Integer(1) / den[0]]
    for k in range(1, depth + 1):
        value = sum(den[j] * inverse[k - j] for j in range(1, k + 1))
        inverse.append(_cancel(-value / den[0]))
    num = [numerator.coeff_monomial(variable ** (nmax - k))
           if nmax - k >= 0 else sp.Integer(0) for k in range(depth + 1)]
    return {
        k - (nmax - dmax): sp.expand(
            sum(num[j] * inverse[k - j] for j in range(k + 1)))
        for k in range(depth + 1)
    }


def analyze_carrier(matrix, r, omega, Lambda, mass) -> dict:
    """Formal exponential/Frobenius classification of the carrier system."""
    A0 = matrix.applyfunc(lambda entry: _cancel(sp.limit(entry, r, sp.oo)))
    A1 = (r * (matrix - A0)).applyfunc(
        lambda entry: _cancel(sp.limit(entry, r, sp.oo)))
    z = sp.Symbol("z")
    characteristic = sp.factor(A0.charpoly(z).as_expr())
    _require(sp.simplify(characteristic - z**2 * (z + 2 * sp.I * omega)**2) == 0,
             f"carrier characteristic changed: {characteristic}")

    Pc, Qc = sp.Function("Pc")(r), sp.Function("Qc")(r)
    state = [Pc, sp.Derivative(Pc, r), Qc, sp.Derivative(Qc, r)]
    rows = [
        sp.Derivative(Pc, (r, 2))
        - sum(matrix[1, j] * state[j] for j in range(4)),
        sp.Derivative(Qc, (r, 2))
        - sum(matrix[3, j] * state[j] for j in range(4)),
    ]
    sigma = sp.Symbol("sigma")

    def apply_slot(row, rate, function, depth=4):
        profile = sp.exp(rate * r) * r**sigma
        substitutions = {
            derivative: sp.diff(profile, r, derivative.derivative_count)
            for derivative in row.atoms(sp.Derivative)
            if derivative.args[0] == function
        }
        substitutions[function] = profile
        for other in (Pc, Qc):
            if other == function:
                continue
            substitutions[other] = 0
            for derivative in row.atoms(sp.Derivative):
                if derivative.args[0] == other:
                    substitutions[derivative] = 0
        expression = _cancel(sp.expand(row.subs(substitutions).doit() / profile))
        numerator, denominator = sp.fraction(expression)
        return _inverse_series(sp.Poly(sp.expand(numerator), r),
                               sp.Poly(sp.expand(denominator), r), r, depth)

    expected = {
        sp.Integer(0): [sp.Integer(-1), sp.Integer(0)],
        -2 * sp.I * omega: [-4 * sp.I * mass * omega - 1,
                            -4 * sp.I * mass * omega],
    }
    sectors = {}
    n = sp.Symbol("n", integer=True, nonnegative=True)
    for rate, expected_roots in expected.items():
        slots = [[apply_slot(rows[i], rate, function) for function in (Pc, Qc)]
                 for i in range(2)]
        leading = min(min(series) for row in slots for series in row)

        def Mk(order, sigma_value):
            return sp.Matrix(2, 2, lambda i, j: sp.factor(
                sp.sympify(slots[i][j].get(leading + order, 0))
                .subs(sigma, sigma_value)))

        indicial = sp.factor(Mk(0, sigma).det())
        roots = sp.solve(sp.Eq(indicial, 0), sigma)
        _require(len(roots) == 2 and all(
            any(sp.simplify(root - wanted) == 0 for root in roots)
            for wanted in expected_roots),
            f"carrier powers at rate {rate} changed: {roots}")
        top = expected_roots[1]
        lower = expected_roots[0]
        top_pivot = sp.factor(Mk(0, top - n).det())
        lower_pivot = sp.factor(Mk(0, lower - n).det())
        expected_top_pivot = -4 * n * (n - 1) * omega**2
        expected_lower_pivot = -4 * n * (n + 1) * omega**2
        _require(sp.simplify(top_pivot - expected_top_pivot) == 0,
                 f"top carrier pivot changed at rate {rate}: {top_pivot}")
        _require(sp.simplify(lower_pivot - expected_lower_pivot) == 0,
                 f"lower carrier pivot changed at rate {rate}: {lower_pivot}")

        leading_vector = Mk(0, top).nullspace()
        _require(len(leading_vector) == 1, "top carrier leading kernel not a line")
        y0 = leading_vector[0]
        resonance_rhs = -Mk(1, top) * y0
        resonant_matrix = Mk(0, top - 1)
        _require(sp.simplify(resonant_matrix.det()) == 0,
                 "integer-spaced carrier resonance disappeared")
        try:
            y1, parameters = resonant_matrix.gauss_jordan_solve(resonance_rhs)
        except ValueError as error:
            raise AsymptoticError(
                f"carrier logarithm forced at rate {rate}, n=1") from error
        y1 = y1.subs({parameter: 0 for parameter in parameters})
        residual = (resonant_matrix * y1 - resonance_rhs).applyfunc(sp.simplify)
        _require(residual == sp.zeros(2, 1),
                 f"carrier resonance incompatible at rate {rate}")
        _require(not any(entry.has(sp.log(r)) for entry in y1),
                 "carrier resonance introduced a logarithm")
        sectors[sp.sstr(rate)] = {
            "indicial_determinant": sp.sstr(indicial),
            "powers": [sp.sstr(value) for value in expected_roots],
            "top_power": sp.sstr(top),
            "lower_power": sp.sstr(lower),
            "top_recurrence_pivot": sp.sstr(top_pivot),
            "lower_recurrence_pivot": sp.sstr(lower_pivot),
            "top_n1_resonance": {
                "compatible": True,
                "rhs": [sp.sstr(sp.factor(value)) for value in resonance_rhs],
                "particular_coefficient": [sp.sstr(sp.factor(value)) for value in y1],
                "free_parameter_reading":
                    "the one free coefficient is the independent lower-power solution; "
                    "setting it to zero fixes the top-power representative",
            },
            "all_orders_reading":
                "after the compatible n=1 resonance, the top pivot is nonzero "
                "for every integer n>=2; the lower pivot is nonzero for every "
                "integer n>=1 when omega!=0",
            "logarithm_forced": False,
        }

    return {
        "state": ["Pc", "dPc/dr", "Qc", "dQc/dr"],
        "matrix": _matrix_strings(matrix),
        "A0": _matrix_strings(A0),
        "A1": _matrix_strings(A1),
        "characteristic_polynomial": sp.sstr(characteristic),
        "rates": ["0", "-2*I*omega"],
        "sectors": sectors,
        "formal_class":
            "exp(rate*r)*r**sigma*sum_{n>=0} y_n*r**(-n), over "
            "Q(Lambda,omega,M,i), with omega!=0",
    }


def analyze_metric(matrix, r, omega, Lambda, mass) -> dict:
    """Reduce the homogeneous metric system to one master ODE and recurse."""
    m20, m21, m22 = matrix[2, 0], matrix[2, 1], matrix[2, 2]
    m01, m02 = matrix[0, 1], matrix[0, 2]
    H1 = sp.Function("H1")(r)
    H0 = _cancel((sp.diff(H1, r, 2) - m21 * H1 - m22 * sp.diff(H1, r)) / m20)
    equation = _cancel(sp.diff(H0, r) - m01 * H1 - m02 * sp.diff(H1, r))
    numerator = sp.expand(sp.fraction(equation)[0])
    undifferentiated = numerator
    for derivative in (sp.Derivative(H1, (r, 3)),
                       sp.Derivative(H1, (r, 2)), sp.Derivative(H1, r)):
        undifferentiated -= numerator.coeff(derivative) * derivative
    _require(sp.simplify(undifferentiated.subs(H1, 1)) == 0,
             "generic-Lambda metric equation retained H1")
    c2 = sp.expand(numerator.coeff(sp.Derivative(H1, (r, 3))))
    c1 = sp.expand(numerator.coeff(sp.Derivative(H1, (r, 2))))
    c0 = sp.expand(numerator.coeff(sp.Derivative(H1, r)))
    expected = (r**2 - 2 * mass * r,
                2 * sp.I * omega * r**2 + 2 * r + 2 * mass,
                6 * sp.I * omega * r - Lambda)
    normalization = _cancel(expected[0] / c2)
    _require(not normalization.has(r),
             f"metric master normalization is radial: {normalization}")
    c2, c1, c0 = (sp.expand(normalization * value)
                  for value in (c2, c1, c0))
    _require(all(sp.simplify(actual - wanted) == 0
                 for actual, wanted in zip((c2, c1, c0), expected)),
             f"generic-Lambda metric master changed: {(c2, c1, c0)}")

    k = sp.Symbol("k", integer=True)
    lam0_pivot = -2 * sp.I * omega * (k - 3)
    lam0_middle = k**2 - k - Lambda
    lam0_lower = -2 * mass * k * (k + 2)
    coefficients = {2: sp.Integer(0), 3: sp.Integer(1)}
    for index in range(4, 8):
        coefficients[index] = sp.factor(-(
            lam0_middle.subs(k, index - 1) * coefficients[index - 1]
            + lam0_lower.subs(k, index - 2) * coefficients[index - 2]
        ) / lam0_pivot.subs(k, index))

    n = sp.Symbol("n", integer=True, nonnegative=True)
    exp_sigma = 1 - 4 * sp.I * mass * omega
    exp_pivot = 2 * sp.I * n * omega
    exp_middle = (-Lambda + 16 * mass**2 * omega**2
                  - 8 * sp.I * mass * omega + n**2 - 3 * n + 2)
    exp_lower = -2 * mass * (4 * sp.I * mass * omega + n - 1) \
        * (4 * sp.I * mass * omega + n + 1)
    exp_coefficients = {-1: sp.Integer(0), 0: sp.Integer(1)}
    for index in range(1, 5):
        exp_coefficients[index] = sp.factor(-(
            exp_middle.subs(n, index - 1) * exp_coefficients[index - 1]
            + exp_lower.subs(n, index - 2) * exp_coefficients[index - 2]
        ) / exp_pivot.subs(n, index))

    generalized_H0 = sp.factor(-m21 / m20)
    expected_H0 = -sp.I * omega * r + Lambda / 2 - 1 + 2 * mass / r
    _require(sp.simplify(generalized_H0 - expected_H0) == 0,
             f"generic-Lambda polynomial mode changed: {generalized_H0}")
    return {
        "state": ["H0", "H1", "dH1/dr"],
        "matrix": _matrix_strings(matrix),
        "master": {
            "variable": "F=dH1/dr",
            "coefficients": [sp.sstr(c2), sp.sstr(c1), sp.sstr(c0)],
            "equation":
                "(r**2-2*M*r)*F'' + (2*I*omega*r**2+2*r+2*M)*F' "
                "+ (6*I*omega*r-Lambda)*F = 0",
        },
        "formal_sectors": {
            "rate_0": {
                "rate": "0",
                "power": "-3",
                "recurrence_pivot": sp.sstr(lam0_pivot),
                "pivot_domain":
                    "k=3 is the indicial root; nonzero for every integer k>=4 "
                    "when omega!=0",
                "series_head": {str(index): sp.sstr(coefficients[index])
                                for index in range(3, 7)},
                "logarithm_forced": False,
            },
            "rate_minus_2_i_omega": {
                "rate": "-2*I*omega",
                "power": sp.sstr(exp_sigma),
                "recurrence_pivot": sp.sstr(exp_pivot),
                "pivot_domain": "nonzero for every integer n>=1 when omega!=0",
                "series_head": {str(index): sp.sstr(exp_coefficients[index])
                                for index in range(0, 4)},
                "logarithm_forced": False,
            },
        },
        "generalized_polynomial_mode": {
            "condition": "H1=constant",
            "H0": sp.sstr(generalized_H0),
            "degree": 1,
            "logarithm": False,
            "ramified": False,
        },
        "all_orders_reading":
            "both scalar master recurrences have a nonzero diagonal pivot at "
            "every post-indicial order for omega!=0; Lambda and M occur only "
            "in recurrence numerators",
    }


def build_payload(geo_cls=Geometry) -> dict:
    for path in INPUTS.values():
        _require(path.exists(), f"missing prerequisite {path}")
    metric_matrix, rm, wm, Lm, Mm = build_metric_system(geo_cls)
    carrier_matrix, rc, wc, Lc, Mc = build_carrier_system(geo_cls)
    substitutions = {rc: rm, wc: wm, Lc: Lm, Mc: Mm}
    carrier_matrix = carrier_matrix.subs(substitutions).applyfunc(_cancel)
    carrier = analyze_carrier(carrier_matrix, rm, wm, Lm, Mm)
    metric = analyze_metric(metric_matrix, rm, wm, Lm, Mm)

    metric_l2 = json.loads(INPUTS["metric_all_orders"].read_text())
    expected_l2 = [sp.sympify(value, locals={"r": rm, "omega": wm, "I": sp.I})
                   for value in metric_l2["master_ode"]["coefficients"]]
    actual_l2 = [sp.sympify(value, locals={"r": rm, "omega": wm,
                                          "Lambda": Lm, "M": Mm, "I": sp.I})
                 .subs({Lm: 6, Mm: 1})
                 for value in metric["master"]["coefficients"]]
    _require(all(sp.simplify(a - b) == 0 for a, b in zip(actual_l2, expected_l2)),
             "ell=2 metric master positive control failed")
    jordan_l2 = json.loads(INPUTS["asymptotic_jordan_l2"].read_text())
    _require(jordan_l2["axial"]["0"]["sigma_roots"] == ["-1", "0"],
             "ell=2 carrier zero-rate control changed")
    _require(jordan_l2["axial"]["-2*omega"]["sigma_roots"]
             == ["-4*I*omega", "-4*I*omega - 1"],
             "ell=2 carrier oscillatory control changed")

    provenance = {}
    for name, path in INPUTS.items():
        provenance[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        }
    for name, path in {
        "producer": Path(__file__),
        "geometry_engine": BH / "weyl_geometry.py",
        "bach_engine": BH / "linearized_bach.py",
    }.items():
        provenance[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        }
    return {
        "schema": "phase2-black-hole-general-l-axial-asymptotics-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "PURE_WEYL_PHASE2_GENERAL_L_AXIAL_ASYMPTOTICS",
        "result_token": "BH_PHASE2_GENERAL_L_AXIAL_ASYMPTOTIC_RECURRENCES_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "declaration": {
            "theory": "pure Weyl gravity, S=alpha*integral sqrt(-g) C^2",
            "background": "Schwarzschild mass M>0; M=1 is the Paper-14 normalization",
            "chart": "ingoing Eddington--Finkelstein",
            "sector": "axial, Lambda=ell*(ell+1), ell>=2",
            "frequency": "real omega!=0",
            "coefficient_field": "Q(Lambda,omega,M,i)",
            "radial_class":
                "formal exponential/polyhomogeneous 1/r series; no convergence asserted",
            "future_consumer":
                "conjugate-frequency sphere-integrated Lee--Wald F^v; not computed here",
        },
        "provenance": provenance,
        "carrier": carrier,
        "metric": metric,
        "exceptional_set": {
            "frequency": ["omega=0"],
            "angular_representations": ["ell=0", "ell=1"],
            "declared_domain_exception_free": True,
            "proof":
                "all post-indicial pivots depend only on a nonzero integer and "
                "omega; Lambda occurs only in numerators. The two rates collide "
                "only at omega=0. The imported exact harmonic theorem isolates "
                "ell=0,1 before the generic ell>=2 reduction.",
        },
        "positive_controls": {
            "ell_2_metric_master_matches_BH2C_METRIC_ALL_ORDERS": True,
            "ell_2_carrier_powers_match_BH2C_ASYMPTOTIC_JORDAN": True,
            "ell_3_independent_recomputation":
                "required from verify_general_l_axial_asymptotics.py",
        },
        "claim_flags": {
            "generic_ell_carrier_operator_certified": True,
            "generic_ell_metric_operator_certified": True,
            "all_orders_formal_recurrences_certified": True,
            "exact_exceptional_set_certified": True,
            "carrier_logs_excluded_for_real_omega_nonzero": True,
            "literal_lee_wald_current_computed": False,
            "finite_pairing_selection_certified": False,
            "polar_certified": False,
            "asymptotic_phase_space_constructed": False,
        },
        "does_not_establish": [
            "a literal Lee--Wald current coefficient or finite-radial-pairing theorem",
            "a polar-parity or omega=0 statement",
            "convergence or summability of the formal radial series",
            "a full asymptotic phase space, Hilbert norm, scattering map, QNM, "
            "stability, particle, positivity or quantum statement",
        ],
        "verification": {
            "producer_check":
                "python3 black_hole_programme/phase2/general_l_axial_asymptotics/"
                "general_l_axial_asymptotics.py --check",
            "independent_ell3":
                "python3 black_hole_programme/phase2/general_l_axial_asymptotics/"
                "verify_general_l_axial_asymptotics.py",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=CERTIFICATE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--inspect", choices=("metric", "carrier"))
    args = parser.parse_args()
    if args.inspect:
        start = time.time()
        if args.inspect == "metric":
            matrix, r, omega, Lambda, mass = build_metric_system()
        else:
            matrix, r, omega, Lambda, mass = build_carrier_system()
        print("symbols", r, omega, Lambda, mass)
        print(sp.sstr(matrix))
        print("seconds", round(time.time() - start, 2))
        return
    payload = build_payload()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        _require(args.out.exists(), f"missing certificate {args.out}")
        _require(args.out.read_text() == encoded, "certificate is stale")
        print("PASS certificate reproduces byte-for-byte")
        return
    args.out.write_text(encoded)
    print(f"wrote {args.out}")
    print(payload["result_token"])


if __name__ == "__main__":
    main()
