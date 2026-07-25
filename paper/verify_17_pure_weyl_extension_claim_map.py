#!/usr/bin/env python3
"""Independent semantic, symbolic, and provenance verifier for Paper 17."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
DEFAULT_MAP = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"REFUSED: {message}")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def require_flag(data: dict, key: str, value: bool, label: str) -> None:
    actual = data.get("claim_flags", {}).get(key)
    if actual is not value:
        fail(f"{label} flag drift: {key}={actual!r}")


def verify_cocycle(claims: dict) -> None:
    r, omega = sp.symbols("r omega", nonzero=True)
    I = sp.I
    f = (r - 2) / r
    U = omega**2 - f * (6 / r**2 - 6 / r**3)

    def D(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(f * sp.diff(expr, r))

    q = sp.sympify(
        claims["exact_identities"]["bach_cocycle_normal_form"]["q"],
        locals={"I": I, "r": r, "omega": omega},
    )
    representative = sp.sympify(
        claims["exact_identities"]["bach_cocycle_normal_form"]["representative"],
        locals={"I": I, "r": r, "omega": omega},
    )
    Kq = D(D(D(q))) + 4 * U * D(q) + 2 * D(U) * q
    cocycle = I * (r - 2) * (2 * r * omega**2 + 3 * omega**2 + 12)
    cocycle /= 5 * r**4 * omega
    if sp.cancel(cocycle - Kq - representative) != 0:
        fail("Bach cocycle normal-form identity failed")
    slope = sp.limit(q / r, r, sp.oo)
    declared_slope = sp.sympify(
        claims["exact_identities"]["forced_gauge_asymptotic"][
            "q_slope_at_infinity"
        ],
        locals={"I": I, "omega": omega},
    )
    if sp.simplify(slope - declared_slope) != 0:
        fail("forced equivalence-gauge slope identity failed")
    if sp.simplify(4 * omega**2 * slope + I * omega / 2) != 0:
        fail("forced equivalence-gauge constant matching failed")

    q_minus_one = sp.sympify(
        claims["exact_identities"]["threshold_static_exactness"]["q_minus_one"],
        locals={"I": I, "r": r},
    )
    U0 = sp.simplify(U - omega**2)
    K0q = D(D(D(q_minus_one))) + 4 * U0 * D(q_minus_one)
    K0q += 2 * D(U0) * q_minus_one
    threshold_expansion = K0q / omega
    threshold_expansion += omega * (4 * D(q_minus_one) + I * f / 2)
    if sp.cancel(cocycle - threshold_expansion) != 0:
        fail("threshold static-exact cocycle decomposition failed")
    if sp.cancel(sp.limit(omega * cocycle, omega, 0) - K0q) != 0:
        fail("threshold cocycle residue identity failed")


def verify_static_nontriviality_and_curvature(claims: dict) -> None:
    r, k, Lambda, ell = sp.symbols("r k Lambda ell")
    f = (r - 2) / r
    U0 = -f * (Lambda / r**2 - 6 / r**3)

    def D(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(f * sp.diff(expr, r))

    def K0(expr: sp.Expr) -> sp.Expr:
        return sp.factor(
            D(D(D(expr))) + 4 * U0 * D(expr) + 2 * D(U0) * expr
        )

    monomial = sp.factor(K0(r**k))
    scaled_monomial = sp.Poly(
        sp.expand(sp.powsimp(monomial * r ** (6 - k), force=True)), r
    )
    zero_indicial = sp.factor(scaled_monomial.coeff_monomial(1))
    expected_zero = -8 * (k - 6) * (k - 2) * (k + 2)
    if sp.factor(zero_indicial - expected_zero) != 0:
        fail("static symmetric-square zero indicial polynomial failed")
    infinity_indicial = sp.factor(
        scaled_monomial.coeff_monomial(r**3).subs(
            Lambda, ell * (ell + 1)
        )
    )
    expected_infinity = (k - 1) * (k - 2 * ell - 2) * (k + 2 * ell)
    if sp.factor(infinity_indicial - expected_infinity) != 0:
        fail("static symmetric-square infinity degree polynomial failed")

    am2, am1, a0, a1 = sp.symbols("am2 am1 a0 a1")
    laurent = am2 / r**2 + am1 / r + a0 + a1 * r
    series = sp.expand(K0(laurent) - f)
    recurrence = {
        am1: am2 * (Lambda - 2) / 3,
        a0: am2 * (Lambda - 2) * (5 * Lambda - 4) / 72,
        a1: Lambda * am2 * (Lambda - 2) * (Lambda - 1) / 72,
    }
    for exponent in [-7, -6, -5]:
        if sp.factor(series.coeff(r, exponent).subs(recurrence)) != 0:
            fail("static exceptional-exponent Laurent recurrence failed")
    compatibility = sp.factor(series.coeff(r, -4).subs(recurrence))
    expected_compatibility = Lambda**2 * (Lambda - 2) ** 2 * am2 / 9
    if sp.factor(compatibility - expected_compatibility) != 0:
        fail("static exceptional-exponent resonant compatibility failed")

    scalar_monomial = sp.factor(
        (D(D(r**k)) + U0 * r**k) / f
    )
    scalar_scaled = sp.Poly(
        sp.expand(sp.powsimp(scalar_monomial * r ** (3 - k), force=True)), r
    )
    low_scalar = sp.factor(scalar_scaled.coeff_monomial(1))
    high_scalar = sp.factor(scalar_scaled.coeff_monomial(r))
    if sp.factor(low_scalar + 2 * (k - 3) * (k + 1)) != 0:
        fail("static RW recurrence denominator failed")
    if sp.factor(high_scalar - (k * (k - 1) - Lambda)) != 0:
        fail("static RW recurrence numerator failed")
    if low_scalar.subs(k, 3) != 0:
        fail("static RW polynomial lower termination failed")
    if sp.factor(
        high_scalar.subs({k: ell + 1, Lambda: ell * (ell + 1)})
    ) != 0:
        fail("static RW polynomial upper termination failed")

    a2, a3 = sp.symbols("a2 a3")
    cubic_one = (Lambda + 4) * a2 - 15 * a3
    cubic_two = (3 * Lambda + 4) * a2 - (6 * Lambda + 33) * a3
    obstruction = sp.factor(
        cubic_two.subs(a2, 15 * a3 / (Lambda + 4))
        * (Lambda + 4)
        / (-6 * a3)
    )
    if sp.factor(obstruction - (Lambda**2 + 2 * Lambda + 12)) != 0:
        fail("all-multipole static cubic obstruction failed")

    q1 = r**2 / 6 + r**3 / 15 + r**4 / 36
    if sp.factor(K0(q1).subs(Lambda, 2) - f) != 0:
        fail("static dipole rational preimage control failed")

    declared = claims["exact_identities"]["static_mass_direction_nontriviality"]
    if declared != {
        "field": "C(r)",
        "multipole_domain": "ell>=2, Lambda=ell*(ell+1)",
        "static_potential": "-f*(Lambda/r**2-6/r**3)",
        "target": "(r-2)/r",
        "zero_indicial": "-8*(k-6)*(k-2)*(k+2)",
        "infinity_indicial": "(k-1)*(k-2*ell-2)*(k+2*ell)",
        "exceptional_zero_compatibility": (
            "Lambda**2*(Lambda-2)**2*a_minus_2/9"
        ),
        "static_rw_recurrence": (
            "c_k=((k-1)*(k-2)-Lambda)"
            "*c_(k-1)/(2*(k-3)*(k+1))"
        ),
        "homogeneous_symmetric_square": "y_ell**2",
        "terminal_polynomial_degree": 3,
        "cubic_obstruction": "Lambda**2+2*Lambda+12",
        "rational_preimage_exists": False,
        "dipole_preimage": "r**2/6+r**3/15+r**4/36",
        "dipole_class_exact": True,
    }:
        fail("static mass-direction nontriviality declaration drift")

    alpha, nu, xi, bhb, l2, a_prime = sp.symbols(
        "alpha nu xi bhb l2 a_prime", nonzero=True
    )
    second_solvability = (
        -2 * bhb + xi * alpha + nu**2 * l2 + 2 * nu * a_prime
    )
    solved_xi = sp.solve(second_solvability, xi)[0]
    expected_xi = (2 * bhb - nu**2 * l2 - 2 * nu * a_prime) / alpha
    if sp.simplify(solved_xi - expected_xi) != 0:
        fail("second-order QNM curvature solvability formula failed")

    m, t, omega = sp.symbols("m t omega", nonzero=True)
    delta = nu * m + xi * m**2 / 2
    inverse_finite = sp.limit(1 / delta - 1 / (nu * m), m, 0)
    if sp.simplify(inverse_finite + xi / (2 * nu**2)) != 0:
        fail("refined inverse-gap coefficient failed")
    divided = (
        sp.exp(sp.I * (omega + delta) * t) - sp.exp(sp.I * omega * t)
    ) / m
    leading = sp.I * nu * t * sp.exp(sp.I * omega * t)
    order_m = sp.limit((divided - leading) / m, m, 0)
    expected_order_m = sp.exp(sp.I * omega * t) * (
        sp.I * xi * t / 2 - nu**2 * t**2 / 2
    )
    if sp.simplify(order_m - expected_order_m) != 0:
        fail("refined divided-exponential coefficient failed")


def verify_commutator() -> None:
    x = sp.symbols("x")
    y = sp.Function("y")(x)
    q = sp.Function("q")(x)
    U = sp.Function("U")(x)

    def L(expr: sp.Expr) -> sp.Expr:
        return sp.diff(expr, x, 2) + U * expr

    def Q(expr: sp.Expr) -> sp.Expr:
        return q * sp.diff(expr, x) - sp.diff(q, x) * expr / 2

    commutator = sp.expand(L(Q(y)) - Q(L(y)))
    on_kernel = commutator.subs(sp.diff(y, x, 2), -U * y)
    on_kernel = on_kernel.subs(
        sp.diff(y, x, 3), -sp.diff(U, x) * y - U * sp.diff(y, x)
    )
    expected = -(
        sp.diff(q, x, 3) + 4 * U * sp.diff(q, x) + 2 * sp.diff(U, x) * q
    ) * y / 2
    if sp.simplify(on_kernel - expected) != 0:
        fail("triangular-gauge commutator identity failed")

    def Q_direct(expr: sp.Expr) -> sp.Expr:
        return 2 * q * sp.diff(expr, x) - sp.diff(q, x) * expr

    direct = sp.expand(L(Q_direct(y)) - Q_direct(L(y)))
    direct = direct.subs(sp.diff(y, x, 2), -U * y)
    direct = direct.subs(
        sp.diff(y, x, 3), -sp.diff(U, x) * y - U * sp.diff(y, x)
    )
    direct_expected = -(
        sp.diff(q, x, 3) + 4 * U * sp.diff(q, x) + 2 * sp.diff(U, x) * q
    ) * y
    if sp.simplify(direct - direct_expected) != 0:
        fail("direct field-redefinition factor-of-two identity failed")


def verify_mass_jost_and_confluence(claims: dict) -> None:
    omega, m, sigma, nu, t = sp.symbols(
        "omega m sigma nu t", nonzero=True
    )
    I = sp.I

    kprime = -1 / (2 * omega)
    rho_prime = sp.simplify(sigma * I * (2 * kprime + 1 / omega))
    if rho_prime != 0:
        fail("Coulomb exponent mass-derivative cancellation failed")
    mass_phase_slope = -sigma * I / (2 * omega)
    bach_scale = I * omega / 2
    if sp.simplify(bach_scale * mass_phase_slope - sigma / 4) != 0:
        fail("moving massive phase and rational-gauge slope mismatch")

    z, a, b, c, d = sp.symbols("z a b c d")
    T0 = sp.Matrix([[z, -1], [0, z]])
    perturbation = sp.Matrix([[a, b], [c, d]])
    determinant = sp.expand((T0 + m * perturbation).det())
    leading = z**2 + m * (a + d) * z + m * c
    if sp.expand(determinant - leading - m**2 * (a * d - b * c)) != 0:
        fail("generic-versus-filtered determinant expansion failed")

    epsilon, delta = sp.symbols("epsilon delta", nonzero=True)
    T_two = sp.Matrix([[z, -1], [c * epsilon, z - nu * m]])
    declared_det = z**2 - nu * m * z + c * epsilon
    if sp.expand(T_two.det() - declared_det) != 0:
        fail("two-parameter unfolding determinant failed")
    gap_squared = nu**2 * m**2 - 4 * c * epsilon
    zp = (nu * m + delta) / 2
    zm = (nu * m - delta) / 2
    epsilon_from_gap = (nu**2 * m**2 - delta**2) / (4 * c)
    for root in [zp, zm]:
        value = sp.simplify(
            declared_det.subs({z: root, epsilon: epsilon_from_gap})
        )
        if value != 0:
            fail("two-parameter unfolding root formula failed")

    vp = sp.Matrix([1, zp])
    vm = sp.Matrix([1, zm])
    wp = sp.Matrix([[zp - nu * m, 1]])
    wm = sp.Matrix([[zm - nu * m, 1]])
    if sp.simplify((wp * vp)[0] - delta) != 0:
        fail("positive gap biorthogonal pairing failed")
    if sp.simplify((wm * vm)[0] + delta) != 0:
        fail("negative gap biorthogonal pairing failed")
    Pp = sp.simplify(vp * wp / delta)
    Pminus = sp.simplify(vm * wm / (-delta))
    gap_renormalized = sp.simplify(delta * (Pp - Pminus) / 2)
    gap_limit = gap_renormalized.subs({m: 0, delta: 0})
    intrinsic_N = sp.Matrix([[0, 1], [0, 0]])
    if gap_limit != intrinsic_N:
        fail("gap-renormalized nilpotent limit failed")
    Smodes = sp.Matrix([[1, 1], [zp, zm]])
    if sp.simplify(Smodes.det() + delta) != 0:
        fail("two-parameter eigenvector determinant failed")

    zeta = sp.symbols("zeta")
    centered = sp.expand(
        declared_det.subs(
            {
                z: zeta + nu * m / 2,
                epsilon: epsilon_from_gap,
            }
        )
    )
    if sp.simplify(centered - (zeta**2 - delta**2 / 4)) != 0:
        fail("centered resolvent denominator failed")

    Fww, Fwm, Fepsilon, unit = sp.symbols(
        "Fww Fwm Fepsilon unit", nonzero=True
    )
    nu_invariant = -2 * Fwm / Fww
    c_invariant = 2 * Fepsilon / Fww
    if sp.simplify((-2 * unit * Fwm / (unit * Fww)) - nu_invariant) != 0:
        fail("unit invariance of mass velocity failed")
    if sp.simplify((2 * unit * Fepsilon / (unit * Fww)) - c_invariant) != 0:
        fail("unit invariance of reverse-coupling coefficient failed")

    L0 = sp.Matrix([[0, -1], [0, 0]])
    L1 = sp.eye(2)
    V0 = sp.Matrix([1, 0])
    V1 = sp.Matrix([0, 1])
    W0 = sp.Matrix([[0, 1]])
    Bmix = sp.Matrix([[0, 0], [c, 0]])
    if L0 * V1 + L1 * V0 != sp.zeros(2, 1):
        fail("normalized EP2 root-chain identity failed")
    d_chain = (W0 * L1 * V1)[0]
    reverse = (W0 * Bmix * V0)[0]
    if sp.simplify(reverse / d_chain - c) != 0:
        fail("Lidskii reverse-coupling formula failed")
    if (W0 * sp.zeros(2) * V0)[0] != 0:
        fail("filtration-preserving mass reverse coupling failed")

    S = sp.Matrix([[1, 1], [0, m]])
    P0 = sp.simplify(S * sp.diag(1, 0) * S.inv())
    Pm = sp.simplify(S * sp.diag(0, 1) * S.inv())
    if P0 != sp.Matrix([[1, -1 / m], [0, 0]]):
        fail("massless confluent projector identity failed")
    if Pm != sp.Matrix([[0, 1 / m], [0, 1]]):
        fail("massive confluent projector identity failed")
    N = sp.Matrix([[0, 1], [0, 0]])
    if sp.simplify(m * P0).applyfunc(lambda x: sp.limit(x, m, 0)) != -N:
        fail("massless projector residue failed")
    if sp.simplify(m * Pm).applyfunc(lambda x: sp.limit(x, m, 0)) != N:
        fail("massive projector residue failed")

    C = sp.simplify(S * sp.diag(1, -1) * S.inv())
    if C != sp.Matrix([[1, -2 / m], [0, -1]]):
        fail("confluent branch involution identity failed")
    if (m * C).applyfunc(lambda x: sp.limit(x, m, 0)) != -2 * N:
        fail("confluent involution residue failed")

    J = sp.simplify(S.inv().T * sp.diag(1, -1) * S.inv())
    if J != sp.Matrix([[1, -1 / m], [-1 / m, 0]]):
        fail("confluent Krein form identity failed")
    H = sp.simplify(J * C)
    if H != sp.Matrix([[1, -1 / m], [-1 / m, 2 / m**2]]):
        fail("singular positive C-metric identity failed")
    if (m * J).applyfunc(lambda x: sp.limit(x, m, 0)) != sp.Matrix(
        [[0, -1], [-1, 0]]
    ):
        fail("renormalized hyperbolic Krein limit failed")
    if (m**2 * H).applyfunc(lambda x: sp.limit(x, m, 0)) != sp.Matrix(
        [[0, 0], [0, 2]]
    ):
        fail("rank-one positive-metric limit failed")

    contour_quotient = (
        sp.exp(I * (omega + nu * m) * t) - sp.exp(I * omega * t)
    ) / m
    if sp.simplify(
        sp.limit(contour_quotient, m, 0)
        - I * nu * t * sp.exp(I * omega * t)
    ) != 0:
        fail("local two-pole contour Jordan limit failed")

    e11, e12, e21, e22, a11, a12, a21, a22 = sp.symbols(
        "e11 e12 e21 e22 a11 a12 a21 a22"
    )
    E = sp.Matrix([[e11, e12], [e21, e22]])
    A = sp.Matrix([[a11, a12], [a21, a22]])
    resolvent = (E + m * A).inv()
    mass_derivative = resolvent.diff(m).subs(m, 0)
    expected_derivative = -E.inv() * A * E.inv()
    if sp.simplify(mass_derivative - expected_derivative) != sp.zeros(2):
        fail("parent inverse mass-derivative identity failed")
    secant = sp.simplify(
        (E.inv() - (E + m * A).inv()) / m
        - E.inv() * A * (E + m * A).inv()
    )
    if secant != sp.zeros(2):
        fail("finite-mass noncommutative secant identity failed")
    second_derivative = resolvent.diff(m, 2).subs(m, 0)
    expected_second = 2 * E.inv() * A * E.inv() * A * E.inv()
    if sp.simplify(second_derivative - expected_second) != sp.zeros(2):
        fail("second critical-jet derivative identity failed")

    w, w0, P, Pdot = sp.symbols("w w0 P Pdot")
    pole_family = (P + m * Pdot) / (w - w0 - nu * m)
    pole_derivative = sp.diff(pole_family, m).subs(m, 0)
    expected_pole_derivative = (
        nu * P / (w - w0) ** 2 + Pdot / (w - w0)
    )
    if sp.simplify(pole_derivative - expected_pole_derivative) != 0:
        fail("massive-pole Laurent derivative identity failed")

    zeta = sp.symbols("zeta")
    matrix_symbols = sp.symbols(
        "p11 p12 p21 p22 h11 h12 h21 h22 "
        "a011 a012 a021 a022 a111 a112 a121 a122"
    )
    (
        p11,
        p12,
        p21,
        p22,
        h11,
        h12,
        h21,
        h22,
        a011,
        a012,
        a021,
        a022,
        a111,
        a112,
        a121,
        a122,
    ) = matrix_symbols
    Pmtrx = sp.Matrix([[p11, p12], [p21, p22]])
    Hmtrx = sp.Matrix([[h11, h12], [h21, h22]])
    A0mtrx = sp.Matrix([[a011, a012], [a021, a022]])
    A1mtrx = sp.Matrix([[a111, a112], [a121, a122]])
    scaled_critical = sp.expand(
        zeta**2
        * (Pmtrx / zeta + Hmtrx)
        * (A0mtrx + zeta * A1mtrx)
        * (Pmtrx / zeta + Hmtrx)
    )
    double_coefficient = scaled_critical.subs(zeta, 0)
    simple_coefficient = scaled_critical.diff(zeta).subs(zeta, 0)
    if sp.simplify(double_coefficient - Pmtrx * A0mtrx * Pmtrx) != sp.zeros(2):
        fail("canonical critical double coefficient failed")
    expected_simple = (
        Pmtrx * A0mtrx * Hmtrx
        + Hmtrx * A0mtrx * Pmtrx
        + Pmtrx * A1mtrx * Pmtrx
    )
    if sp.simplify(simple_coefficient - expected_simple) != sp.zeros(2):
        fail("canonical simple-pole frequency-derivative term failed")

    root = claims["exact_identities"]["root_polarization"]
    if root["principal_coefficient_square"] != "0":
        fail("nilpotent principal coefficient declaration drift")


def verify_period_matrix(claims: dict) -> None:
    y1, y2, dy1, dy2, V = sp.symbols("y1 y2 dy1 dy2 V")
    Y = sp.Matrix([[y1, y2], [dy1, dy2]])
    dA = sp.Matrix([[0, 0], [-V, 0]])
    W = y1 * dy2 - y2 * dy1
    actual = sp.simplify(Y.inv() * dA * Y)
    declared = claims["exact_identities"]["period_matrix"]
    expected = V / W * sp.Matrix(
        [[y1 * y2, y2**2], [-y1**2, -y1 * y2]]
    )
    if declared != [["y1*y2", "y2**2"], ["-y1**2", "-y1*y2"]]:
        fail("declared period matrix drift")
    if sp.simplify(actual - expected) != sp.zeros(2):
        fail("symmetric-square period matrix identity failed")


def verify_spectral_velocity_and_contact_order(claims: dict) -> None:
    omega, omega_n, m, nu = sp.symbols(
        "omega omega_n m nu", nonzero=True
    )
    local_evans = omega - omega_n - nu * m
    spectral_response = (
        sp.I * omega * sp.diff(sp.log(local_evans), m) / 2
    ).subs(m, 0)
    residue = sp.simplify(
        sp.limit((omega - omega_n) * spectral_response, omega, omega_n)
    )
    kappa = -sp.I * omega_n * nu / 2
    if sp.simplify(residue - kappa) != 0:
        fail("spectral-velocity residue identity failed")
    if sp.simplify(omega_n * nu - 2 * sp.I * kappa) != 0:
        fail("selector weighted-velocity identity failed")

    kappa_re, kappa_im = sp.symbols("kappa_re kappa_im", real=True)
    reflected_pair_sum = (
        kappa_re + sp.I * kappa_im
        - (kappa_re - sp.I * kappa_im)
    )
    if sp.simplify(sp.re(reflected_pair_sum)) != 0:
        fail("reflection-symmetric selector sum failed")

    z, pdot = sp.symbols("z pdot")
    moving_pole = (1 + m * pdot) / (z - nu * m)
    first_jet = -sp.diff(moving_pole, m).subs(m, 0)
    if sp.simplify(first_jet + nu / z**2 + pdot / z) != 0:
        fail("first-jet moving-pole decomposition failed")
    stationary = sp.simplify(first_jet.subs(nu, 0))
    if sp.simplify(stationary + pdot / z) != 0:
        fail("stationary first-jet simple-pole classification failed")

    # Independent coefficient extraction for the contact-order law.
    for q in range(1, 5):
        coefficient = sp.Rational(2, sp.factorial(q))
        delta = coefficient * m**q
        for p in range(0, 13):
            series = sum(
                delta**j / z ** (j + 1)
                for j in range(0, p // q + 1)
            )
            jet = sp.expand(
                (-1) ** p
                * sp.diff(series, m, p).subs(m, 0)
                / sp.factorial(p)
            )
            terms = sp.Add.make_args(jet)
            observed = max(
                [
                    -term.as_powers_dict().get(z, 0)
                    for term in terms
                    if term != 0
                ]
                or [0]
            )
            expected_bound = p // q + 1
            if observed > expected_bound:
                fail("contact-order pole bound failed")
        first_visible = sp.expand(
            (-1) ** q
            * sp.diff(1 / z + delta / z**2, m, q).subs(m, 0)
            / sp.factorial(q)
        ).coeff(z, -2)
        expected_first = (-1) ** q * coefficient
        if sp.simplify(first_visible - expected_first) != 0:
            fail("contact-order first-visible coefficient failed")
        for multiple in range(1, 4):
            p = multiple * q
            top = sp.expand(
                (-1) ** p
                * sp.diff(delta**multiple / z ** (multiple + 1), m, p).subs(
                    m, 0
                )
                / sp.factorial(p)
            ).coeff(z, -(multiple + 1))
            expected_top = (-1) ** p * coefficient**multiple
            if sp.simplify(top - expected_top) != 0:
                fail("contact-order repeated-multiple coefficient failed")

    declared_spectral = claims["exact_identities"]["spectral_velocity_generator"]
    if declared_spectral != {
        "function": "S=b_B/a",
        "logarithmic_derivative": "S=I*omega*partial_m(log(a))/2+h",
        "simple_qnm_residue": "kappa=-I*omega_n*nu_n/2",
        "contour_sum": "integral_Gamma(S)/(2*pi*I)=sum(kappa_n)",
        "weighted_velocity_sum": (
            "sum(omega_n*nu_n)=2*I*integral_Gamma(S)/(2*pi*I)"
        ),
        "reflection_symmetric_sum": "purely_imaginary",
        "zero_sum_implies_all_zero": False,
    }:
        fail("spectral-velocity declaration drift")

    declared_dichotomy = claims["exact_identities"][
        "simple_qnm_first_jet_dichotomy"
    ]
    if declared_dichotomy != {
        "nonzero_velocity": (
            "nu_n!=0 iff b_B(omega_n)!=0 iff Smith=(0,0,2)"
        ),
        "zero_velocity": (
            "nu_n=0 iff b_B(omega_n)=0 iff Smith=(0,1,1)"
        ),
        "zero_velocity_double_coefficient": "0",
        "zero_velocity_simple_coefficient": "-Pdot",
        "shape_sensitive": "nu_n=0 and Pdot!=0",
        "first_jet_invisible": "nu_n=0 and Pdot=0",
    }:
        fail("simple-QNM first-jet dichotomy declaration drift")

    declared_contact = claims["exact_identities"]["critical_contact_order"]
    if declared_contact != {
        "branch": (
            "omega_n(m)=omega_n+nu_n_q*m**q/factorial(q)+O(m**(q+1))"
        ),
        "jet": "J_p=(-1)**p*partial_m**p(R_m)/factorial(p)",
        "pole_order_bound": "floor(p/q)+1",
        "p_less_q": (
            "no_pole_enhancement_from_motion;"
            "projector_derivatives_may_leave_simple_pole"
        ),
        "first_visible_double_coefficient": (
            "(-1)**q*nu_n_q*P/factorial(q)"
        ),
        "multiple_top_coefficient": (
            "(-1)**(k*q)*(nu_n_q/factorial(q))**k*P"
        ),
        "q1_specialization": "pole_order=p+1",
    }:
        fail("critical contact-order declaration drift")


def verify_spectral_acceleration_and_krein_jordan(claims: dict) -> None:
    z, m, nu, xi = sp.symbols("z m nu xi")
    moving_divisor = z - nu * m - xi * m**2 / 2
    theta_1 = -sp.diff(sp.log(moving_divisor), m).subs(m, 0)
    theta_2 = -sp.diff(sp.log(moving_divisor), m, 2).subs(m, 0)
    if sp.simplify(theta_1 - nu / z) != 0:
        fail("first spectral-flow principal part failed")
    if sp.simplify(theta_2 - nu**2 / z**2 - xi / z) != 0:
        fail("second spectral-flow principal part failed")

    phi0, phi1 = sp.symbols("phi0 phi1")
    weighted_second = sp.expand((phi0 + phi1 * z) * theta_2)
    if sp.simplify(weighted_second.coeff(z, -1) - (phi0 * xi + phi1 * nu**2)) != 0:
        fail("weighted acceleration residue failed")

    omega, omega0 = sp.symbols("omega omega0")
    u0, u_omega, u_m = sp.symbols("u0 u_omega u_m", nonzero=True)
    local_unit = u0 + u_omega * (omega - omega0) + u_m * m
    evans = local_unit * (
        omega - omega0 - nu * m - xi * m**2 / 2
    )
    subs0 = {omega: omega0, m: 0}
    a_omega = sp.diff(evans, omega).subs(subs0)
    a_mm = sp.diff(evans, m, 2).subs(subs0)
    a_omega_m = sp.diff(evans, omega, m).subs(subs0)
    a_omega_omega = sp.diff(evans, omega, 2).subs(subs0)
    recovered_xi = sp.simplify(
        -(a_mm + 2 * nu * a_omega_m + nu**2 * a_omega_omega)
        / a_omega
    )
    if sp.simplify(recovered_xi - xi) != 0:
        fail("Evans acceleration formula failed")

    v_omega, v_m = sp.symbols("v_omega v_m")
    renormalized = (
        1 + v_omega * (omega - omega0) + v_m * m
    ) * evans
    rw = sp.diff(renormalized, omega).subs(subs0)
    rmm = sp.diff(renormalized, m, 2).subs(subs0)
    rwm = sp.diff(renormalized, omega, m).subs(subs0)
    rww = sp.diff(renormalized, omega, 2).subs(subs0)
    renormalized_xi = sp.simplify(
        -(rmm + 2 * nu * rwm + nu**2 * rww) / rw
    )
    if sp.simplify(renormalized_xi - xi) != 0:
        fail("Evans acceleration unit invariance failed")

    P, Pdot, Pddot = sp.symbols("P Pdot Pddot")
    projector = P + m * Pdot + m**2 * Pddot / 2
    moving_resolvent = projector / moving_divisor
    second_jet = sp.expand(sp.diff(moving_resolvent, m, 2).subs(m, 0) / 2)
    expected_second_jet = (
        nu**2 * P / z**3
        + (nu * Pdot + xi * P / 2) / z**2
        + Pddot / (2 * z)
    )
    if sp.simplify(second_jet - expected_second_jet) != 0:
        fail("second critical-jet Laurent coefficients failed")

    t = sp.symbols("t", real=True)
    local_signal = sp.exp(
        sp.I * (omega0 + nu * m + xi * m**2 / 2) * t
    ) * projector
    second_signal = sp.simplify(
        sp.diff(local_signal, m, 2).subs(m, 0) / 2
    )
    expected_signal = sp.exp(sp.I * omega0 * t) * (
        Pddot / 2
        + sp.I * t * nu * Pdot
        + (sp.I * t * xi / 2 - t**2 * nu**2 / 2) * P
    )
    if sp.simplify(second_signal - expected_signal) != 0:
        fail("second critical-jet local contour failed")

    gamma = sp.symbols("gamma", positive=True)
    envelope = t * sp.exp(-gamma * t)
    if sp.simplify(sp.diff(envelope, t).subs(t, 1 / gamma)) != 0:
        fail("damped Jordan envelope maximizer failed")
    if sp.simplify(envelope.subs(t, 1 / gamma) - 1 / (sp.E * gamma)) != 0:
        fail("damped Jordan envelope maximum failed")

    # Canonical Krein-Jordan classification.
    a, b, d = sp.symbols("a b d", real=True, nonzero=True)
    N = sp.Matrix([[0, 1], [0, 0]])
    G = sp.Matrix([[a, b], [b, d]])
    relation = N.T * G - G * N
    if relation != sp.Matrix([[0, -a], [a, 0]]):
        fail("Krein-Jordan self-adjointness equation failed")
    G0 = G.subs(a, 0)
    chain = sp.Matrix([[1, -d / (2 * b)], [0, 1]])
    normalized = sp.simplify(chain.T * G0 * chain)
    if normalized != sp.Matrix([[0, b], [b, 0]]):
        fail("Krein-Jordan chain normalization failed")
    if sp.factor(G0.det() + b**2) != 0:
        fail("Krein-Jordan hyperbolic determinant failed")
    pole = sp.Matrix([[0, b], [0, 0]])
    if pole**2 != sp.zeros(2) or sp.trace(pole) != 0:
        fail("null rank-one pole geometry failed")
    s = sp.symbols("s")
    if sp.expand((sp.eye(2) + s * pole).det()) != 1:
        fail("nilpotent determinant invisibility failed")

    sigma0, sigma1 = sp.symbols("sigma0 sigma1", real=True)
    S = sp.Matrix([[1, 1], [0, m]])
    pulled = sp.simplify(
        S.inv().T * sp.diag(sigma0, sigma1) * S.inv()
    )
    expected_pulled = sp.Matrix(
        [
            [sigma0, -sigma0 / m],
            [-sigma0 / m, (sigma0 + sigma1) / m**2],
        ]
    )
    if pulled != expected_pulled:
        fail("branch-sign pullback failed")
    opposite_limit = pulled.subs(sigma1, -sigma0).applyfunc(
        lambda entry: sp.limit(m * entry, m, 0)
    )
    if opposite_limit != sp.Matrix([[0, -sigma0], [-sigma0, 0]]):
        fail("opposite-sign hyperbolic limit failed")
    same_limit = pulled.subs(sigma1, sigma0).applyfunc(
        lambda entry: sp.limit(m**2 * entry, m, 0)
    )
    if same_limit != sp.Matrix([[0, 0], [0, 2 * sigma0]]):
        fail("same-sign degenerate limit failed")

    spectral = claims["exact_identities"]["spectral_flow_forms"]
    if spectral != {
        "theta_1": "-partial_m(log(a))*domega",
        "theta_1_principal": "nu_n*domega/(omega-omega_n)",
        "theta_1_residue": "nu_n",
        "theta_2": "-partial_m**2(log(a))*domega",
        "theta_2_principal": (
            "(nu_n**2/(omega-omega_n)**2+xi_n/(omega-omega_n))*domega"
        ),
        "theta_2_residue": "xi_n",
        "unit_change": "holomorphic_one_form",
        "bach_representative": (
            "-2*b_B*domega/(I*omega*a)=theta_1+holomorphic"
        ),
        "velocity_moment": (
            "integral(phi*theta_1)/(2*pi*I)=sum(phi(omega_n)*nu_n)"
        ),
        "acceleration_moment": (
            "integral(phi*theta_2)/(2*pi*I)="
            "sum(phi(omega_n)*xi_n+phi_prime(omega_n)*nu_n**2)"
        ),
    }:
        fail("spectral-flow form declaration drift")

    acceleration = claims["exact_identities"]["evans_acceleration"]
    if acceleration != {
        "velocity": "-a_m/a_omega",
        "acceleration": (
            "-(a_mm+2*nu*a_omega_m+nu**2*a_omega_omega)/a_omega"
        ),
        "unit_invariant": True,
        "operator_formula": (
            "(2*pair(tilde_u,B*H*B*u)"
            "-nu**2*pair(tilde_u,L2*u)"
            "-2*nu*pair(tilde_u,A1*u))/alpha"
        ),
        "reflected_acceleration": "-conjugate(xi)",
    }:
        fail("Evans acceleration declaration drift")

    second = claims["exact_identities"]["second_critical_jet"]
    if second != {
        "definition": "partial_m**2(R_m)/2",
        "triple_coefficient": "nu**2*P",
        "double_coefficient": "nu*Pdot+xi*P/2",
        "simple_coefficient": "Pddot/2",
        "stationary_accelerating_double": "xi*P/2",
        "local_contour": (
            "exp(I*omega*t)*(Pddot/2+I*t*nu*Pdot"
            "+(I*t*xi/2-t**2*nu**2/2)*P)"
        ),
    }:
        fail("second critical-jet declaration drift")

    damped = claims["exact_identities"]["damped_jordan_envelope"]
    if damped != {
        "envelope": "t*exp(-gamma*t)",
        "maximum_time": "1/gamma",
        "maximum_value": "1/(E*gamma)",
        "certified_gamma": "0.0889623156889357",
        "certified_t_max_approx": "11.241",
        "certified_envelope_max_approx": "4.135",
        "global_stability_claim": False,
    }:
        fail("damped Jordan envelope declaration drift")

    krein = claims["exact_identities"]["krein_jordan_geometry"]
    if krein != {
        "nilpotent": [["0", "1"], ["0", "0"]],
        "self_adjoint_equation": "N_dagger*G=G*N",
        "general_form": [["0", "b"], ["b", "d"]],
        "nondegeneracy": "b!=0",
        "chain_shift": "V1->V1-d*V0/(2*b)",
        "normal_form": [["0", "1"], ["1", "0"]],
        "geometric_root_null": True,
        "positive_compatible_form_exists": False,
        "null_rank_one_pole": "gamma*V0 tensor flat(V0)",
        "pole_square": "0",
        "left_root": "W0 proportional flat(V0)",
        "trace_pole": "0",
        "det_I_plus_s_pole": "1",
    }:
        fail("Krein-Jordan declaration drift")

    opposite = claims["exact_identities"]["opposite_signature_confluence"]
    if opposite != {
        "branch_form": "diag(sigma_0,sigma_1)",
        "pulled_back": [
            ["sigma_0", "-sigma_0/m"],
            ["-sigma_0/m", "(sigma_0+sigma_1)/m**2"],
        ],
        "nondegenerate_first_order_iff": "sigma_1=-sigma_0",
        "opposite_limit": [["0", "-sigma_0"], ["-sigma_0", "0"]],
        "same_sign_m2_limit": [["0", "0"], ["0", "2*sigma_0"]],
        "same_sign_limit_rank": 1,
        "bounded_positive_critical_involution_exists": False,
    }:
        fail("opposite-sign confluence declaration drift")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args()

    paper = resolve(args.paper)
    claim_path = resolve(args.claim_map)
    claims = json.loads(claim_path.read_text())
    text = paper.read_text()

    if claims.get("paper_id") != "PAPER_17_PURE_WEYL_EXTENSION_RESONANCE":
        fail("wrong paper identity")
    if claims.get("lifecycle_state") != "DRAFT_ALLOWED":
        fail("paper lifecycle overpromotion")
    if claims.get("paper_sha256") != digest(paper):
        fail("paper hash drift")

    for name, authority in claims.get("authorities", {}).items():
        path = ROOT / authority["path"]
        if digest(path) != authority["sha256"]:
            fail(f"authority content drift: {name}")

    required = [
        "Mass-direction normal form",
        "All-radiative-multipole static mass direction",
        "\\frac{\\Lambda^2(\\Lambda-2)^2}{9}a_{-2}=0",
        "\\Lambda^2+2\\Lambda+12=0",
        "Exceptional dipole control",
        "\\mathcal K_{U_{1,0}}q_1=f",
        "What remains for all-\\(\\ell\\) Bach nonsplitting",
        "Static exactness and exact threshold valuation",
        "\\ord_{\\omega=0}[\\mathcal I_{\\rm Bach}]=1",
        "no rational triangular gauge holomorphic in \\(\\omega\\)",
        "\\operatorname*{Res}_{\\omega=0}\\mathcal I_{\\rm Bach}",
        "Bulk class versus spectral frame",
        "\\mathcal I_{\\rm Bach}",
        "\\mathcal K_{U_2}q+\\frac{i\\omega}{2}f",
        "Explicit triangular gauge",
        "Symmetric-square period matrix",
        "Non-split physical-axis extension",
        "Local commutant",
        "Certified defective Schwarzschild resonance",
        "Resonant evaluation theorem",
        "\\mathfrak M_n([K])",
        "-\\frac{\\kappa_n}{\\alpha_n}",
        "Nonzero carrier in the generalized root",
        "Finite-interval outgoing Green pole",
        "Exterior cut-off Green pole",
        "exact transparent boundary conditions",
        "\\chi_{\\rm o}R_{\\rm ext}(\\omega)\\chi_{\\rm s}",
        "C_c^\\infty((r_H,r_I);\\C^6)",
        "Conditional global Fredholm promotion",
        "Exact local critical-mass-jet identification",
        "[\\mathcal I_{\\rm mass}]=[f]",
        "m=\\frac{i\\omega}{2}\\tau",
        "Forced moving-phase gauge",
        "Q_q=2qD-D(q)",
        "Coulomb cancellation and differentiated Jost classes",
        "\\rho_\\sigma'(0)=0",
        "Critical-mass Evans derivative and QNM velocity",
        "\\frac{2i}{\\omega_n}\\kappa_n\\ne0",
        "Reflected EP2 pair",
        "\\omega_n^\\sharp",
        "Spectral-velocity generating function",
        "Spectral-velocity residues and contour sum",
        "\\operatorname*{Res}_{\\omega=\\omega_j}\\mathscr S(\\omega)",
        "Complete first-jet dichotomy at a simple QNM",
        "C_{-1}=-\\dot P_j",
        "Boundary transgression as an audit",
        "Universal critical resonance and the covariant parent",
        "Universal critical-resonance criterion",
        "C_{-2}=-\\nu_nP_n",
        "Canonical simple pole and tangent state",
        "Second-order massive-QNM curvature",
        "\\xi_n=\\omega_n''(0)",
        "Refined filtered confluence",
        "P_nA_n'P_n",
        "[-H_ng_n]",
        "Augmented QNM Hellmann--Feynman formula",
        "-\\frac{\\partial_ma}{\\partial_\\omega a}",
        "Spectral acceleration and the second critical jet",
        "First and second spectral-flow forms",
        "\\operatorname*{Res}_{\\omega=\\omega_n}\\Theta_2=\\xi_n",
        "Weighted velocity and acceleration moments",
        "Evans acceleration and second-jet Laurent coefficients",
        "Second-order isolated resonance contribution",
        "Damped Jordan envelope",
        "Second-order reflection audit",
        "[\\dot u_n]\\in D/\\C u_n",
        "exact finite-mass secant identity",
        "Spectral contact controls critical pole order",
        "\\left\\lfloor\\frac pq\\right\\rfloor+1",
        "Transverse higher jets",
        "Critical mass derivative of the metric Green operator",
        "G_{-2}=-\\frac{\\nu_n}{4\\alpha_{\\rm W}}P_n",
        "Isolated parent-resonance contribution",
        "Einstein-shaped",
        "The fourth result is stronger",
        "No global retarded",
        "Invariant two-parameter unfolding",
        "\\nu_n=-\\frac{2F_{\\omega m}}{F_{\\omega\\omega}}",
        "c_n=\\frac{2F_\\epsilon}{F_{\\omega\\omega}}",
        "Lidskii reverse-coupling coefficient",
        "\\gamma_n(B)=\\langle W_0,BV_0\\rangle",
        "\\Delta^2=\\nu_n^2m^2-4c_n\\epsilon",
        "Exceptional parabola and branch monodromy",
        "complexified deformation space",
        "Two meanings of transverse",
        "Filtration-error threshold",
        "\\chi=\\frac{4c_n\\epsilon}{\\nu_n^2m^2}",
        "Lower-left mutation certificate",
        "Gap-controlled projectors, nilpotent, and metrics",
        "\\frac{\\Delta}{2}(P_+-P_-)",
        "Filtered critical-mass unfolding normal form",
        "Root-space polarization and nilpotent pole",
        "R_{-2}^2=0",
        "Canonical Krein--Jordan geometry",
        "Null rank-one pole and determinant invisibility",
        "Opposite-sign confluence criterion",
        "No finite positive critical branch observable",
        "Confluent projectors and local contour",
        "Critical singularity of positive branch metrics",
        "Renormalized Krein limit",
        "Canonical pseudospectral scale",
        "does not establish a causal spacetime resolvent",
    ]
    for phrase in required:
        if phrase not in text:
            fail(f"required scoped statement missing: {phrase}")

    forbidden = [
        "the intrinsic radial parameter \\(\\tau\\) is the physical squared mass",
        "the causal spacetime resolvent has a second-order pole",
        "a rigorous \\(t e^{i\\omega_nt}\\) ringdown term",
        "the Bach self-extension is nonsplit for every \\(\\ell\\ge2\\)",
        "the full six-state commutant is the dual-number algebra",
        "the complete complex reducibility locus is known",
        "time-domain stability is established",
        "quantum unitarity is established",
        "the endpoint transgression vanishes",
        "the off-resonance normalization function \\(h(\\omega)\\) vanishes",
        "the physical mass deformation is a miniversal unfolding",
        "the local two-pole contour is the full retarded solution",
        "the projected metric Green coefficient is nilpotent",
        "the physical filtration-breaking coefficient \\(c_n\\) has been computed",
        "the general-\\(\\ell\\) Bach coefficient \\(c_\\ell(\\omega)\\) has been computed",
        "a numerical value of \\(\\xi_n\\) has been computed",
        "a threshold-uniform estimate for \\(b/a^2\\) is established",
        "a validated multi-QNM selector contour has been computed",
        "every Schwarzschild overtone is an EP2",
        "a validated multi-QNM acceleration contour has been computed",
        "a numerical QNM acceleration has been computed",
        "the Krein--Jordan theorem proves a global quantum no-go",
    ]
    for phrase in forbidden:
        if phrase in text:
            fail(f"forbidden promotion present: {phrase}")

    for key, value in claims["fail_closed_scope"].items():
        if value is not False:
            fail(f"fail-closed promotion: {key}")

    authorities = claims["authorities"]
    filtration = json.loads((ROOT / authorities["factor_filtration"]["path"]).read_text())
    require_flag(
        filtration,
        "complete_RW_RW_Lx_triangular_filtration_certified",
        True,
        "filtration",
    )
    require_flag(
        filtration,
        "complete_direct_RW_square_plus_Lx_decomposition_certified",
        False,
        "filtration",
    )

    cocycle = json.loads((ROOT / authorities["projective_cocycle"]["path"]).read_text())
    for key in [
        "projective_gauge_law_exact",
        "generic_rational_ansatz_exhaustive",
        "generic_rational_cocycle_nontrivial",
        "declared_reduced_representative_exact",
    ]:
        require_flag(cocycle, key, True, "cocycle")
    require_flag(cocycle, "QNM_double_pole_established", False, "cocycle")

    simple = json.loads(
        (ROOT / authorities["simplicity_endomorphisms"]["path"]).read_text()
    )
    for key in [
        "axial_ell2_nonsplit_all_positive_real",
        "spin2_endomorphism_ring_scalar_positive_real",
        "spin2_simple_all_ell_positive_real",
    ]:
        require_flag(simple, key, True, "simplicity")
    require_flag(simple, "all_ell_bach_nonsplitting_established", False, "simplicity")

    commutant = json.loads((ROOT / authorities["local_commutant"]["path"]).read_text())
    require_flag(commutant, "local_commutant_dual_numbers_exact", True, "commutant")
    require_flag(commutant, "full_six_state_commutant_dual_numbers", False, "commutant")

    winding = json.loads((ROOT / authorities["qnm_winding"]["path"]).read_text())
    for key in [
        "full_closed_contour_nonzero_certified",
        "winding_number_certified",
        "unique_simple_spin_two_QNM_in_disk_certified",
    ]:
        require_flag(winding, key, True, "winding")

    selector = json.loads((ROOT / authorities["qnm_selector"]["path"]).read_text())
    require_flag(selector, "intrinsic_tangent_selector_nonzero", True, "selector")
    require_flag(selector, "repeated_spin_two_smith_valuations_0_2", True, "selector")

    spin1 = json.loads((ROOT / authorities["spin_one_unit"]["path"]).read_text())
    require_flag(spin1, "spin_one_jost_factor_unit_on_local_disk", True, "spin-one")
    require_flag(spin1, "full_connection_smith_valuations_0_0_2", True, "spin-one")

    fredholm = json.loads(
        (ROOT / authorities["fredholm_promotion"]["path"]).read_text()
    )
    for key in [
        "analytic_finite_interval_pencil_certified",
        "connection_smith_transferred_to_operator",
        "radial_green_operator_second_order_pole_certified",
        "principal_laurent_coefficient_rank_one",
        "physical_metric_reconstruction_nonzero",
    ]:
        require_flag(fredholm, key, True, "Fredholm promotion")
    for key in [
        "exterior_spacetime_causal_resolvent_certified",
        "retarded_inverse_transform_certified",
        "t_exp_iomega_t_term_certified",
        "time_domain_stability_certified",
    ]:
        require_flag(fredholm, key, False, "Fredholm promotion")

    mass = json.loads(
        (ROOT / authorities["critical_mass_parent"]["path"]).read_text()
    )
    for key in [
        "parent_mass_variation_exact",
        "mass_derivative_modulo_einstein_kernel_exact",
        "tt_difference_quotient_exact",
    ]:
        require_flag(mass, key, True, "critical mass parent")
    for key in [
        "physical_b_equals_minus_mass_derivative_of_jost",
        "physical_mass_jet_equals_intrinsic_radial_tau",
        "physical_massive_qnm_slope_certified",
    ]:
        require_flag(mass, key, False, "critical mass parent")

    continuation = json.loads(
        (ROOT / authorities["analytic_continuation"]["path"]).read_text()
    )
    for key in [
        "axial_mode_series_omega_poles_exact_certified",
        "domain_declared_excludes_poles",
        "no_branch_points_axial_certified",
    ]:
        require_flag(continuation, key, True, "analytic continuation")
    require_flag(continuation, "stability_qnm_scattering_claimed", False, "continuation")

    reconstruction = json.loads(
        (ROOT / authorities["metric_reconstruction"]["path"]).read_text()
    )
    require_flag(
        reconstruction,
        "complete_three_row_reconstruction_certified",
        True,
        "reconstruction",
    )

    root = claims["exact_identities"]["generalized_root"]
    if root["carrier_quotient"] != "-a1/b0":
        fail("generalized root carrier quotient identity failed")
    triangular = claims["exact_identities"]["triangular_gauge"]
    if triangular != {
        "operator": "q*D - D(q)/2",
        "commutator_on_kernel": "-K_U(q)/2",
        "direct_field_gauge": "Q_q=2*q*D-D(q)",
        "direct_commutator_on_kernel": "-K_U(q)",
    }:
        fail("triangular gauge factor normalization drift")
    resonant = claims["exact_identities"]["resonant_evaluation"]
    if resonant != {
        "selector": "b0/a1",
        "normalized_overlap": "beta/alpha",
        "resonance_velocity": "-kappa",
        "physical_mass_velocity": "2*I*kappa/omega",
        "carrier_quotient": "-1/kappa",
        "fredholm_principal_coefficient": "-kappa/alpha",
    }:
        fail("resonant evaluation chain declaration drift")
    mass_jet = claims["exact_identities"]["critical_mass_jet"]
    if mass_jet != {
        "mass_operator": "L - m*f",
        "mass_cocycle_class": "[f]",
        "bach_to_mass_class": "I*omega/2",
        "parameter_relation": "m = I*omega*tau/2",
        "coulomb_exponent": "sigma*I*(2*k+m/k)",
        "coulomb_exponent_mass_derivative_at_zero": "0",
        "evans_derivative_at_qnm": "b_B=I*omega*partial_m(a)/2",
        "qnm_velocity": "2*I*kappa/omega",
    }:
        fail("critical mass-jet declaration drift")
    transgression = claims["exact_identities"]["boundary_transgression"]
    if transgression != {
        "base_gauge": "Q(q)=q*D-D(q)/2",
        "field_redefinition_gauge": "Q_q=2*Q(q)",
        "bulk_identity": "K_Bach-I*omega*K_mass/2=-[L,Q_q]",
        "finite_cut_term": "-[W(tilde_u,Q_q*u)]_xminus^xplus",
        "qnm_endpoint_effect": "h(omega)*a(omega)",
    }:
        fail("boundary-transgression normalization drift")
    unfolding = claims["exact_identities"]["filtered_unfolding"]
    if unfolding != {
        "normal_form": [["z", "-1"], ["0", "z-mu"]],
        "generic_determinant_leading": "z**2+m*(a+d)*z+m*c",
        "generic_split": "sqrt(m) if c != 0",
        "filtered_split": "mu=dz_domega*nu*m+O(m**2)",
        "projector_scale": "1/abs(m)",
        "positive_metric_condition_scale": "1/abs(m)**2",
        "pseudospectral_radius": "sqrt(epsilon)",
    }:
        fail("filtered unfolding declaration drift")
    two_parameter = claims["exact_identities"]["two_parameter_unfolding"]
    if two_parameter != {
        "nu_invariant": "-2*F_omega_m/F_omega_omega",
        "c_invariant": "2*F_epsilon/F_omega_omega",
        "normal_form": [["z", "-1"], ["c_n*epsilon", "z-nu*m"]],
        "determinant": "z**2-nu*m*z+c_n*epsilon",
        "gap_squared": "nu**2*m**2-4*c_n*epsilon",
        "exceptional_curve": "epsilon=nu**2*m**2/(4*c_n)",
        "exceptional_curve_derivatives": (
            "F_omega_m**2/(2*F_omega_omega*F_epsilon)"
        ),
        "physical_gap": "nu*m",
        "mixing_gap_squared": "-4*c_n*epsilon",
        "c_n_nonzero_requires_declared_transverse_direction": True,
        "complexified_parameter_space": True,
    }:
        fail("two-parameter unfolding declaration drift")
    lidskii = claims["exact_identities"]["lidskii_reverse_coupling"]
    if lidskii != {
        "chain_denominator": "pair(W0,L1*V1+L2*V0/2)",
        "reverse_numerator": "pair(W0,B*V0)",
        "c_n": "pair(W0,B*V0)/d_n",
        "mass_reverse_coupling": "0",
        "forward_extension_overlap": "beta_n",
    }:
        fail("Lidskii reverse-coupling declaration drift")
    gap = claims["exact_identities"]["gap_controlled_confluence"]
    if gap != {
        "right_vectors": ["(1,z_plus)", "(1,z_minus)"],
        "left_vectors": ["(z_plus-nu*m,1)", "(z_minus-nu*m,1)"],
        "left_right_pairings": ["Delta", "-Delta"],
        "projector_scale": "1/abs(Delta)",
        "nilpotent_limit": "Delta*(P_plus-P_minus)/2=N",
        "metric_condition_scale": "1/abs(Delta)**2",
    }:
        fail("gap-controlled confluence declaration drift")
    error_threshold = claims["exact_identities"]["filtration_error_threshold"]
    if error_threshold != {
        "required": "abs(c_n*epsilon_error)<<abs(nu**2*m**2)",
        "scaling_variable": "chi=4*c_n*epsilon/(nu**2*m**2)",
        "p_less_than_2": "mixing_dominated",
        "p_equal_2": "linear_coefficient_changed",
        "p_greater_than_2": "physical_velocity_recovered",
    }:
        fail("filtration-error threshold declaration drift")
    crossover = claims["exact_identities"]["two_parameter_resolvent"]
    if crossover != {
        "inverse_denominator": "z**2-nu*m*z+c_n*epsilon",
        "centered_frequency": "zeta=z-nu*m/2",
        "centered_denominator": "zeta**2-Delta**2/4",
        "unresolved_response": "zeta**(-2)*(1+O(Delta**2/zeta**2))",
        "resolved_projector_scale": "1/abs(Delta)",
    }:
        fail("two-parameter resolvent declaration drift")
    confluent = claims["exact_identities"]["confluent_limits"]
    if confluent != {
        "m_times_C": "-2*N",
        "tau_times_C": "4*I*N/omega",
        "m_times_J": [["0", "-1"], ["-1", "0"]],
        "m2_times_H": [["0", "0"], ["0", "2"]],
        "local_contour": "exp(I*omega*t)*(I+I*nu*t*N)",
    }:
        fail("confluent limit declaration drift")
    parent = claims["exact_identities"]["parent_mass_derivative"]
    if parent != {
        "metric_green": "-partial_m(E_m_inverse)/(4*alpha_W)",
        "finite_mass_secant": "(E_inverse-E_m_inverse)/m",
        "double_coefficient": "-nu*P/(4*alpha_W)",
        "simple_coefficient": "-Pdot/(4*alpha_W)",
        "overlap_velocity": "nu=-beta/alpha",
        "selector_coefficient": "-I*kappa*P/(2*alpha_W*omega)",
        "local_contour": (
            "-exp(I*omega*t)*(Pdot+I*t*nu*P)/(4*alpha_W)"
        ),
    }:
        fail("parent mass-derivative declaration drift")
    universal = claims["exact_identities"]["universal_critical_resonance"]
    if universal != {
        "critical_response": "R*A*R",
        "double_coefficient": "beta/alpha**2*u tensor tilde_u",
        "double_pole_iff": "beta != 0",
        "mass_velocity": "-beta/alpha",
        "canonical_tangent_class": "[u_dot] in D/(C*u)",
        "projected_coefficient_intrinsically_nilpotent": False,
        "full_extension_coefficient_nilpotent": True,
    }:
        fail("universal critical-resonance declaration drift")
    threshold = claims["exact_identities"]["threshold_static_exactness"]
    if threshold != {
        "q_minus_one": "-I*(15*r + 13 + 12/r + 9/r**2)/120",
        "symmetric_square_decomposition": "K_U=K_U0+4*omega**2*D",
        "cocycle_residue": "K_U0(q_minus_one)",
        "renormalized_class_limit": "I*[f]/2",
        "continuous_cokernel_identification_required": False,
        "exact_threshold_valuation": 1,
        "holomorphic_improvement_to_order_two": False,
    }:
        fail("threshold static-exactness declaration drift")
    simple_pole = claims["exact_identities"]["canonical_simple_pole"]
    if simple_pole != {
        "double_coefficient": "P*A0*P=-nu*P",
        "simple_coefficient": "P*A0*H+H*A0*P+P*A1*P=-Pdot",
        "frequency_derivative_term": "P*A1*P",
        "tangent_class": "-H*(A0+nu*L1)*u mod C*u",
        "left_tangent_class": "-tilde_u*(A0+nu*L1)*H mod C*tilde_u",
    }:
        fail("canonical simple-pole declaration drift")
    curvature = claims["exact_identities"]["second_order_qnm_curvature"]
    if curvature != {
        "B": "A0+nu*L1",
        "curvature": (
            "(2*pair(tilde_u,B*H*B*u)"
            "-nu**2*pair(tilde_u,L2*u)"
            "-2*nu*pair(tilde_u,A1*u))/alpha"
        ),
        "normalization_independent": True,
        "augmented_endpoint_derivatives_required": True,
        "scalar_bulk_A1": "0",
        "scalar_bulk_L2": "2",
    }:
        fail("second-order QNM curvature declaration drift")
    refined = claims["exact_identities"]["refined_filtered_confluence"]
    if refined != {
        "gap": "nu*m+xi*m**2/2+O(m**3)",
        "inverse_gap": "1/(nu*m)-xi/(2*nu**2)+O(m)",
        "divided_exponential_order_m": (
            "exp(I*omega*t)*(I*xi*t/2-nu**2*t**2/2)"
        ),
    }:
        fail("refined filtered-confluence declaration drift")
    hellmann = claims["exact_identities"]["augmented_hellmann_feynman"]
    if hellmann != {
        "evans_parameter_derivative": "integral(yminus*Qp*yplus)+B_p",
        "velocity": "-a_m/a_omega=-beta/alpha",
        "mass_potential_derivative": "-f",
        "frequency_potential_derivative": "2*omega",
        "pairing": "bilinear_augmented_qnm",
    }:
        fail("augmented Hellmann-Feynman declaration drift")
    reflection = claims["exact_identities"]["reflection_pair"]
    if reflection != {
        "frequency": "-conjugate(omega)",
        "velocity": "-conjugate(nu)",
        "selector": "-conjugate(kappa)",
        "simple_residue": "-conjugate(P)",
        "double_coefficient": "conjugate(C_minus_2)",
        "simple_coefficient": "-conjugate(C_minus_1)",
    }:
        fail("reflection-pair declaration drift")
    higher = claims["exact_identities"]["higher_critical_jets"]
    if higher != {
        "operator": "R*(A*R)**p",
        "mass_derivative": "(-1)**p*partial_m**p(R_m)/factorial(p)",
        "pole_order_if_beta_nonzero": "p+1",
        "leading_coefficient": "beta**p/alpha**(p+1)*u tensor tilde_u",
    }:
        fail("higher critical-jet declaration drift")
    green = claims["exact_identities"]["green_principal_coefficient"]
    if green != {
        "connection": "-b0/a1**2",
        "outgoing_green": "b0/a1**2",
        "rank": 1,
    }:
        fail("Green principal coefficient declaration drift")

    verify_cocycle(claims)
    verify_static_nontriviality_and_curvature(claims)
    verify_commutator()
    verify_period_matrix(claims)
    verify_mass_jost_and_confluence(claims)
    verify_spectral_velocity_and_contact_order(claims)
    verify_spectral_acceleration_and_krein_jordan(claims)

    print("PASS paper/17-pure-weyl-schwarzschild-extension-structure.tex")
    print(
        "PASS exact cocycle, endpoint-compatible mass jet, filtered "
        "unfolding, spectral velocity and acceleration, contact-order, "
        "Krein-Jordan, confluent metrics, and nilpotent root-space identities"
    )
    print("PASS authority provenance and fail-closed claim boundary")


if __name__ == "__main__":
    main()
