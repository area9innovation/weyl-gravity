"""Exact generic-ell axial Einstein Lee--Wald current coefficient.

This producer is deliberately restricted to the homogeneous Einstein image.
It imports the Phase-2 generic-ell radial recurrence by exact content and Git
blob identities, builds the literal Lee--Wald current before choosing a
spherical harmonic, and only then applies the closed Legendre identities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
INPUT = ROOT / "black_hole_programme/phase2/general_l_axial_asymptotics/certificate.json"
LEGACY = ROOT / "black_hole_programme/certificates/BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json"
SCHEMA = HERE / "schema.json"
DEFAULT_OUTPUT = HERE / "certificate.json"
sys.path.insert(0, str(ROOT / "black_hole_programme"))

from linearized_theta import LinearizedTheta  # noqa: E402
from weyl_geometry import Geometry  # noqa: E402

INPUT_CONTENT_SHA256 = "6742e049806d3122a4c1b3a2b01d1305448f0ee6287e955083a0749cbe304523"
INPUT_GIT_BLOB = "707467bb2a4b279b8355bc79b0b9482a8f2da8f0"
R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega", positive=True)
M = sp.Symbol("M", positive=True)
LAMBDA = sp.Symbol("Lambda", integer=True, positive=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def require_import() -> dict:
    if sha256(INPUT) != INPUT_CONTENT_SHA256:
        raise RuntimeError("generic-ell recurrence content SHA256 drift")
    if git_blob(INPUT) != INPUT_GIT_BLOB:
        raise RuntimeError("generic-ell recurrence Git-blob drift")
    payload = json.loads(INPUT.read_text())
    if payload["claim_flags"]["literal_lee_wald_current_computed"]:
        raise RuntimeError("input claim boundary drift")
    return payload


def master_coefficients(rate: sp.Expr, power: sp.Expr, depth: int) -> list[sp.Expr]:
    """Formal coefficients of F=e^(rate*r) r^power sum f_n r^-n."""
    fs: list[sp.Expr] = [sp.Integer(1)]
    for n in range(1, depth + 1):
        k = power - n
        a = (2 * rate * k - 2 * M * rate**2 + 2 * sp.I * W * k
             + 2 * rate + 6 * sp.I * W)
        kp = power - n + 1
        b = kp * (kp - 1) - 4 * M * rate * kp + 2 * kp + 2 * M * rate - LAMBDA
        km = power - n + 2
        c = -2 * M * km * (km - 2)
        rhs = b * fs[n - 1] + (c * fs[n - 2] if n >= 2 else 0)
        fs.append(sp.cancel(-rhs / a))
    return fs


def _poly_in_inverse_r(expr: sp.Expr, r: sp.Symbol, depth: int) -> list[sp.Expr]:
    t = sp.Symbol("t")
    ser = sp.series(expr.subs(r, 1 / t), t, 0, depth + 1).removeO().expand()
    return [sp.cancel(ser.coeff(t, n)) for n in range(depth + 1)]


def metric_profile_series(rate: sp.Expr, power: sp.Expr, depth: int = 4):
    """Return formal (base power, coefficients) for H0,H1 at F-leading 1."""
    r, omega, mass = R, W, M
    fs = master_coefficients(rate, power, depth + 2)
    phase = sp.exp(rate * r)
    Fnorm = sum(fs[n] * r**(-n) for n in range(depth + 2))
    F = phase * r**power * Fnorm
    if rate == 0:
        bs = [sp.cancel(fs[n] / (power - n + 1)) for n in range(depth + 1)]
        h1_power = power + 1
        H1norm = sum(bs[n] * r**(-n) for n in range(depth + 1))
    else:
        bs: list[sp.Expr] = []
        for n in range(depth + 1):
            prev = (power - n + 1) * bs[n - 1] if n else 0
            bs.append(sp.cancel((fs[n] - prev) / rate))
        h1_power = power
        H1norm = sum(bs[n] * r**(-n) for n in range(depth + 1))

    A = (-2 * mass - sp.I * omega * r**2) / r**2
    B = (2 * mass - r) / r
    if rate == 0:
        h0_power = power + 2
        ds = _poly_in_inverse_r(A * H1norm + B * Fnorm / r, r, depth)
        cs = [sp.cancel(ds[n] / (h0_power - n)) for n in range(depth + 1)]
    else:
        h0_power = power
        ds = _poly_in_inverse_r(A * H1norm + B * Fnorm, r, depth)
        cs: list[sp.Expr] = []
        for n in range(depth + 1):
            prev = (power - n + 1) * cs[n - 1] if n else 0
            cs.append(sp.cancel((ds[n] - prev) / rate))
    return ((h0_power, cs), (h1_power, bs))


def metric_profile(rate: sp.Expr, power: sp.Expr, depth: int = 4) -> tuple[sp.Expr, sp.Expr]:
    """Return (H0,H1), normalized by leading master coefficient F=1."""
    phase = sp.exp(rate * R)
    rows = metric_profile_series(rate, power, depth)
    return tuple(sp.expand(phase * R**base * sum(cs[n] * R**(-n)
                                                for n in range(len(cs))))
                 for base, cs in rows)


def literal_unsummed_current() -> tuple[sp.Expr, dict[str, sp.Expr]]:
    """Build r^2 omega^v with an arbitrary smooth axial profile S(x)."""
    v, x, phi = sp.symbols("v x phi")
    r = R
    alpha = sp.Symbol("alpha")
    B = 1 - 2 / r
    g = sp.zeros(4)
    g[0, 0] = -B
    g[0, 1] = g[1, 0] = 1
    g[2, 2] = r**2 / (1 - x**2)
    g[3, 3] = r**2 * (1 - x**2)
    geo = Geometry([v, r, x, phi], g)
    theta = LinearizedTheta(geo, alpha)
    S = sp.Function("S")(x)
    h0a, h1a, h0b, h1b = [sp.Function(n)(v, r) for n in
                            ("h0a", "h1a", "h0b", "h1b")]
    hA = sp.zeros(4)
    hB = sp.zeros(4)
    hA[0, 3] = hA[3, 0] = h0a * S
    hA[1, 3] = hA[3, 1] = h1a * S
    hB[0, 3] = hB[3, 0] = h0b * S
    hB[1, 3] = hB[3, 1] = h1b * S
    return sp.expand(theta.omega(hA, hB)[0] * r**2), {
        "v": v, "r": r, "x": x, "alpha": alpha, "S": S,
        "h0a": h0a, "h1a": h1a, "h0b": h0b, "h1b": h1b,
    }


def _radial_jet(rate: sp.Expr, base: sp.Expr, coeffs: list[sp.Expr],
                dr: int, dv_factor: sp.Expr) -> tuple[sp.Expr, dict[int, sp.Expr]]:
    data = {n: dv_factor * c for n, c in enumerate(coeffs)}
    for _ in range(dr):
        nxt: dict[int, sp.Expr] = {}
        for n, c in data.items():
            nxt[n] = nxt.get(n, 0) + rate * c
            nxt[n + 1] = nxt.get(n + 1, 0) + (base - n) * c
        data = {n: sp.expand(c) for n, c in nxt.items() if c != 0}
    return base, data


def paired_r_minus_two(current: sp.Expr, names: dict[str, sp.Expr],
                       rate: sp.Expr, power: sp.Expr,
                       rows=None) -> sp.Expr:
    v, r = names["v"], names["r"]
    rows = metric_profile_series(rate, power) if rows is None else rows
    atom_map: dict[sp.Expr, sp.Symbol] = {}
    jet_data: dict[sp.Symbol, tuple[sp.Expr, dict[int, sp.Expr]]] = {}
    for side in ("a", "b"):
        for field_index, field in enumerate(("h0", "h1")):
            fn = names[field + side]
            atoms = [fn] + [d for d in current.atoms(sp.Derivative) if d.expr == fn]
            for atom in atoms:
                dv = 0 if atom == fn else sum(int(pair[1]) for pair in atom.args[1:]
                                               if pair[0] == v)
                dr = 0 if atom == fn else sum(int(pair[1]) for pair in atom.args[1:]
                                               if pair[0] == r)
                symbol = sp.Symbol(f"J_{side}_{field}_{dv}_{dr}")
                atom_map[atom] = symbol
                base, coeffs = rows[field_index]
                if side == "a":
                    jet_data[symbol] = _radial_jet(
                        rate, base, coeffs, dr, (sp.I * W)**dv)
                else:
                    jet_data[symbol] = _radial_jet(
                        sp.conjugate(rate), sp.conjugate(base),
                        [sp.conjugate(c) for c in coeffs], dr, (-sp.I * W)**dv)

    encoded = sp.expand(current.xreplace(atom_map))
    answer = 0
    jet_symbols = set(jet_data)
    for term in sp.Add.make_args(encoded):
        present = list(term.free_symbols & jet_symbols)
        if len(present) != 2:
            raise RuntimeError(f"current term is not bilinear in two jets: {term}")
        ja, jb = present
        coeff = sp.factor_terms(term / (ja * jb))
        angular, r_power = coeff.as_coeff_exponent(r)
        if r in angular.free_symbols:
            raise RuntimeError(f"radial coefficient was not a monomial: {coeff}")
        base_a, data_a = jet_data[ja]
        base_b, data_b = jet_data[jb]
        target = sp.simplify(r_power + base_a + base_b + 2)
        if not target.is_Integer:
            raise RuntimeError(f"nonintegral target series order {target}")
        n_target = int(target)
        if n_target < 0:
            continue
        radial = sum(ca * data_b.get(n_target - na, 0)
                     for na, ca in data_a.items())
        answer += angular * radial
    return answer


def angular_reduce(expr: sp.Expr, names: dict[str, sp.Expr], ell: sp.Symbol) -> sp.Expr:
    """Apply the evaluated Legendre norms; no generic integral remains."""
    x, S = names["x"], names["S"]
    p0, p1 = sp.symbols("P Pprime")
    replacements = {S: -(1 - x**2) * p1}
    for derivative in expr.atoms(sp.Derivative):
        if derivative.expr != S:
            continue
        order = sum(int(pair[1]) for pair in derivative.args[1:] if pair[0] == x)
        if order == 1:
            replacements[derivative] = LAMBDA * p0
        elif order == 2:
            replacements[derivative] = LAMBDA * p1
        else:
            raise RuntimeError(f"unsupported angular derivative order {order}")

    norm_p2 = 2 / (2 * ell + 1)
    norm_xpp = 2 * ell / (2 * ell + 1)
    norm_dp2 = LAMBDA
    norm_x2dp2 = LAMBDA * (2 * ell - 1) / (2 * ell + 1)
    grouped: dict[tuple[int, int], sp.Expr] = {}
    reduced = sp.expand(expr.xreplace(replacements))
    for term in sp.Add.make_args(reduced):
        powers = term.as_powers_dict()
        a, b = int(powers.get(p0, 0)), int(powers.get(p1, 0))
        coeff = sp.cancel(term / (p0**a * p1**b))
        grouped[(a, b)] = grouped.get((a, b), 0) + coeff

    answer = 0
    for (a, b), coefficient in grouped.items():
        coeff = sp.cancel(sp.together(coefficient))
        poly = sp.Poly(coeff, x)
        if (a, b) == (2, 0):
            if poly.degree() > 0:
                raise RuntimeError(f"unexpected P^2 weight {poly.as_expr()}")
            answer += poly.nth(0) * norm_p2
        elif (a, b) == (1, 1):
            if poly.degree() > 1 or poly.nth(0) != 0:
                raise RuntimeError(f"unexpected P P' weight {poly.as_expr()}")
            answer += poly.nth(1) * norm_xpp
        elif (a, b) == (0, 2):
            if poly.degree() > 2 or poly.nth(1) != 0:
                raise RuntimeError(f"unexpected P'^2 weight {poly.as_expr()}")
            answer += poly.nth(0) * norm_dp2 + poly.nth(2) * norm_x2dp2
        else:
            raise RuntimeError(f"unexpected angular monomial P^{a} P'^{b}")
    return sp.factor(sp.cancel(2 * sp.pi * answer))


def direct_harmonic_integral(expr: sp.Expr, names: dict[str, sp.Expr], ell: int) -> sp.Expr:
    x, S = names["x"], names["S"]
    polynomial = sp.legendre(ell, x)
    profile = -(1 - x**2) * sp.diff(polynomial, x)
    replacements = {S: profile}
    for derivative in expr.atoms(sp.Derivative):
        if derivative.expr == S:
            order = sum(int(pair[1]) for pair in derivative.args[1:] if pair[0] == x)
            replacements[derivative] = sp.diff(profile, x, order)
    specialized = expr.xreplace(replacements).subs(LAMBDA, ell * (ell + 1))
    integrated = sp.integrate(sp.expand(specialized), (x, -1, 1))
    return sp.factor(2 * sp.pi * integrated)


def build_debug() -> dict:
    require_import()
    omega, mass = W, M
    current, names = literal_unsummed_current()
    rows = {}
    ell = sp.Symbol("ell", integer=True, positive=True)
    e0_rows = ((sp.Integer(1), [-sp.I * omega / 2, (LAMBDA - 2) / 4, mass]),
               (sp.Integer(0), [sp.Rational(1, 2)]))
    sectors = {
        "E0": (sp.Integer(0), sp.Integer(0), e0_rows),
        "E2": (-2 * sp.I * omega, 1 - 4 * sp.I * mass * omega, None),
    }
    for name, (rate, power, radial_rows) in sectors.items():
        raw = paired_r_minus_two(current, names, rate, power, radial_rows).subs(mass, 1)
        generic = angular_reduce(raw, names, ell)
        rows[name] = {
            "generic": str(generic),
            "ell2_direct": str(direct_harmonic_integral(raw, names, 2)),
            "ell2_reduced": str(sp.factor(generic.subs({ell: 2, LAMBDA: 6}))),
        }
    return rows


def wall_data() -> dict[str, sp.Expr]:
    """Legacy E2 normalization and its exact real wall certificate."""
    u = sp.Symbol("u", positive=True)
    q = -2 * sp.I * W
    p = 1 - 4 * sp.I * M * W
    b3 = sp.factor(metric_profile_series(q, p)[1][1][3].subs(M, 1))
    kappa = sp.factor(-W / ((2 * W - sp.I) * b3))
    g = sp.factor(sp.denom(kappa) / (2 * W - sp.I))
    # Remove the harmless overall sign chosen by SymPy.
    if sp.LC(sp.Poly(sp.re(g.expand(complex=True)), W)) < 0:
        g = -g
        kappa = -kappa
    real = sp.expand(sp.re(g)).subs(W**2, u)
    imag_reduced = sp.factor(sp.im(g) / (12 * W)).subs(W**2, u)
    resultant = sp.factor(sp.resultant(real, imag_reduced, u))
    H = sp.factor(resultant / 2**24)
    ell = sp.Symbol("ell", integer=True, positive=True)
    k = sp.Symbol("k", integer=True, nonnegative=True)
    discrete = sp.expand(H.subs(LAMBDA, ell * (ell + 1)))
    shifted = sp.Poly(sp.expand(discrete.subs(ell, k + 4)), k)
    resultant_sign = "+"
    if all(c < 0 for c in shifted.all_coeffs()):
        H, discrete = -H, -discrete
        shifted = sp.Poly(-shifted.as_expr(), k)
        resultant_sign = "-"
    if any(c <= 0 for c in shifted.all_coeffs()):
        raise RuntimeError("shifted resultant polynomial lost coefficient positivity")
    return {
        "b3": b3, "kappa": kappa, "G": g,
        "real_G_in_u": real, "imag_G_over_12omega_in_u": imag_reduced,
        "wall": sp.factor(g * sp.conjugate(g)), "resultant": resultant,
        "resultant_relation": f"resultant={resultant_sign}2^24*H(Lambda)",
        "H": H, "H_discrete": discrete, "H_ell2": discrete.subs(ell, 2),
        "H_ell3": discrete.subs(ell, 3), "H_shifted_ell_ge_4": shifted.as_expr(),
    }


def _record(path: Path) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "content_sha256": sha256(path),
        "git_blob": git_blob(path),
    }


def build_certificate() -> dict:
    require_import()
    current, names = literal_unsummed_current()
    ell = sp.Symbol("ell", integer=True, positive=True)
    alpha = names["alpha"]
    e0_rows = ((sp.Integer(1), [-sp.I * W / 2, (LAMBDA - 2) / 4, M]),
               (sp.Integer(0), [sp.Rational(1, 2)]))
    e0_raw = paired_r_minus_two(current, names, 0, 0, e0_rows).subs(M, 1)
    e2_raw = paired_r_minus_two(
        current, names, -2 * sp.I * W, 1 - 4 * sp.I * M * W).subs(M, 1)
    e0 = angular_reduce(e0_raw, names, ell)
    e2_unit = angular_reduce(e2_raw, names, ell)
    expected_e0 = -4 * sp.I * sp.pi * alpha * W * LAMBDA * (LAMBDA - 2) / (2 * ell + 1)
    expected_e2 = -sp.I * sp.pi * alpha * LAMBDA * (LAMBDA - 2) / (
        W**3 * (2 * ell + 1))
    if sp.simplify(e0 - expected_e0) != 0 or sp.simplify(e2_unit - expected_e2) != 0:
        raise RuntimeError("literal current did not reduce to the closed all-ell formula")

    wall = wall_data()
    scale_sq = sp.factor(wall["kappa"] * sp.conjugate(wall["kappa"]))
    e2_legacy = sp.factor(e2_unit * scale_sq)
    legacy_payload = json.loads(LEGACY.read_text())
    old = legacy_payload["einstein_literal_flux_axial"]
    locals_ = {"omega": W, "alpha": alpha, "I": sp.I, "pi": sp.pi}
    old_e0 = sp.sympify(old["E0|E0"]["leading_coeff"], locals=locals_)
    old_e2 = sp.sympify(old["E2|E2"]["leading_coeff"], locals=locals_)
    ell2 = {ell: 2, LAMBDA: 6}
    if sp.simplify(e0.subs(ell2) - old_e0) != 0:
        raise RuntimeError("ell=2 E0 legacy coefficient mismatch")
    if sp.simplify(e2_legacy.subs(ell2) - old_e2) != 0:
        raise RuntimeError("ell=2 E2 legacy coefficient mismatch")

    direct = {}
    for lvalue in (2, 3):
        direct[str(lvalue)] = {
            "E0": str(direct_harmonic_integral(e0_raw, names, lvalue)),
            "E2_unit_F": str(direct_harmonic_integral(e2_raw, names, lvalue)),
            "Lambda": lvalue * (lvalue + 1),
        }

    H2, H3 = wall["H_ell2"], wall["H_ell3"]
    if H2 == 0 or H3 == 0:
        raise RuntimeError("resultant polynomial vanished at ell=2 or ell=3")
    return {
        "schema": "phase2-black-hole-general-l-axial-current-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha256(SCHEMA),
        "result_id": "PURE_WEYL_PHASE2_GENERAL_L_AXIAL_EINSTEIN_CURRENT",
        "result_token": "BH_PHASE2_GENERAL_L_AXIAL_EINSTEIN_CURRENT_NONVANISHING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "declaration": {
            "theory": "pure Weyl gravity, alpha_W integral sqrt(-g) C^2, alpha_W!=0",
            "background": "Schwarzschild M>0; formulas use M=1 and hat_omega=M*omega",
            "chart": "ingoing Eddington--Finkelstein",
            "sector": "axial integer ell>=2, Lambda=ell*(ell+1)",
            "frequency": "real omega!=0; producer symbol is omega>0 and the negative half-line follows exactly by conjugation/time reversal",
            "object": "fixed-representative sphere-integrated Lee--Wald slice density F^v(E,bar E)",
            "asymptotic_form": "F^v=A_EE*r^-2+O(r^-3)",
        },
        "normalization": {
            "E0": "H1=1/2 and H0=-i*omega*r/2+(Lambda-2)/4+M/r (legacy-compatible)",
            "E2_unit_F": "F=dH1/dr has leading coefficient 1 in exp(-2*i*omega*r)*r^(1-4*i*M*omega)",
            "rescaling_law": "E -> c E sends A_EE -> |c|^2 A_EE",
            "legacy_E2_scale_kappa": str(wall["kappa"]),
            "legacy_reading": "the G denominator is a basis-normalization wall only; the unit-F current has no such wall",
        },
        "angular_reduction": {
            "S_ell": "-(1-x**2)*P_ell'(x)",
            "derivative_identities": ["S_ell'=Lambda*P_ell", "S_ell''=Lambda*P_ell'"],
            "evaluated_norms": {
                "integral_P2": "2/(2*ell+1)",
                "integral_x_P_Pprime": "2*ell/(2*ell+1)",
                "integral_Pprime2": "Lambda",
                "integral_x2_Pprime2": "Lambda*(2*ell-1)/(2*ell+1)",
            },
            "unevaluated_integral_remaining": False,
        },
        "coefficients": {
            "E0": str(sp.factor(e0)),
            "E2_unit_F": str(sp.factor(e2_unit)),
            "E2_legacy": str(e2_legacy),
            "leading_power": -2,
            "all_nonzero_on_declared_domain": True,
        },
        "legacy_wall": {
            "G": str(wall["G"]),
            "G_abs_squared": str(wall["wall"]),
            "real_G_in_u": str(wall["real_G_in_u"]),
            "imag_G_over_12omega_in_u": str(wall["imag_G_over_12omega_in_u"]),
            "resultant_u": str(wall["resultant"]),
            "resultant_relation": wall["resultant_relation"],
            "resultant_factor_H": str(wall["H"]),
            "H_at_ell2": str(H2),
            "H_at_ell3": str(H3),
            "H_shifted_ell_ge_4": str(wall["H_shifted_ell_ge_4"]),
            "proof": "For omega!=0, G=0 implies simultaneous zeros of Re(G) and Im(G)/(12*omega) in u=omega^2. Their resultant is a nonzero signed factor 2^24 times H(Lambda). H(6) and H(12) are nonzero; after Lambda=ell(ell+1), ell=k+4, every coefficient of H is positive. Hence no common real zero for integer ell>=2.",
        },
        "frequency_extension": {
            "identity": "A_EE(-omega)=-A_EE(omega)=conjugate(A_EE(omega))",
            "reason": "all displayed denominators are real and even in omega while the imaginary numerator is odd",
            "nonvanishing_preserved": True,
        },
        "mass_restoration": {
            "dimensionless_frequency": "hat_omega=M*omega",
            "rule": "replace every omega in the dimensionless M=1 wall polynomials by hat_omega; mode-normalization powers restore the overall dimension and cannot create a zero for M>0",
            "nonvanishing_invariant_for_M_positive": True,
        },
        "literal_controls": direct,
        "representative_ambiguity": {
            "fixed_representative": "LinearizedTheta for L=alpha_W C^2 used by the existing BH2C certificate",
            "closed_sphere_angular_exact_forms": "integrate to zero for regular integer-ell harmonics",
            "radial_exact_form_quotient_analyzed": False,
            "reading": "the theorem is for this factorized Lee--Wald representative; it does not assert invariance under every symplectic-potential exact-form redefinition",
        },
        "provenance": {
            "generic_ell_recurrence": _record(INPUT),
            "legacy_ell2_certificate": _record(LEGACY),
            "lee_wald_engine": _record(ROOT / "black_hole_programme/linearized_theta.py"),
            "geometry_engine": _record(ROOT / "black_hole_programme/weyl_geometry.py"),
        },
        "claim_flags": {
            "literal_all_ell_axial_einstein_current_certified": True,
            "all_ell_einstein_finite_radial_form_certified": True,
            "legacy_normalization_wall_excluded": True,
            "extra_branch_selection_certified": False,
            "polar_certified": False,
            "asymptotic_phase_space_constructed": False,
            "hilbert_norm_constructed": False,
        },
        "does_not_establish": [
            "extra-branch exclusion or an Einstein-image selection theorem",
            "a polar-parity statement",
            "a complete asymptotic phase space, Hilbert norm or scattering flux topology",
            "invariance under unrestricted Lee--Wald exact-form ambiguities",
            "convergence of the formal radial series, stability, QNMs, particles, positivity or a quantum statement",
        ],
        "verification": {
            "producer": "python3 black_hole_programme/phase2/general_l_axial_current/general_l_axial_current.py --check",
            "independent": "python3 black_hole_programme/phase2/general_l_axial_current/verify_general_l_axial_current.py",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.debug:
        print(json.dumps(build_debug(), indent=2, sort_keys=True))
        return
    payload = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text() != payload:
            raise SystemExit("certificate drift")
        print("PASS certificate reproduces byte-for-byte")
        return
    args.out.write_text(payload)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
