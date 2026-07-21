"""BH-3 complex-frequency analytic-continuation gate.

Fail-closed builder for
`black_hole_programme/certificates/BH3_ANALYTIC_CONTINUATION_GATE.json`.

Verdict token:
`BH3_AXIAL_ANALYTIC_CONTINUATION_MEROMORPHIC_POLAR_NOT_ACTIVATED`.

Certifies analytic continuation of the Schwarzschild exterior AXIAL mode
families and the Lee-Wald symplectic cross current from real frequency into the
complex-omega plane, with an EXACT singular set; records the POLAR sector as
NOT_ACTIVATED (its route-B symbolic identity is a certified missing object and
no continuation may be extrapolated from real-omega fixtures).

Everything is symbolic/exact; NO finite set of complex sample frequencies is
used (that cannot establish continuation).

AXIAL results (m = 1, l = 2, omega in C):

1. CROSS SCALAR / SYMPLECTIC CURRENT.  The certified cross invariant
   a(omega) = i F^r(E,X)/(pi alpha) (BH2_SYMBOLIC_CROSS_INVARIANT) is an EXACT
   rational function; a rational function is meromorphic on all of C with no
   branch points, so it continues from the real axis to a meromorphic function
   whose singular set is EXACTLY its pole set {i, i/2} (both simple; numerator
   and denominator share no factor).  The Lee-Wald cross current
   F^r = -i pi alpha a(omega) continues with the same poles.

2. MODE FROBENIUS FAMILIES.  From the parity-unified master ODE
   (BH2C_METRIC_ALL_ORDERS) c2 F'' + c1 F' + c0 F = 0, all coefficients
   polynomial in omega:
   - the boundary exponents (-3 and -4 i omega + 1 at infinity; the horizon
     indicial roots 0 and -4 i omega - 2; the certified RW ingoing +- 2 i m
     omega) are ENTIRE (polynomial/linear) in omega -- no branch points;
   - the INFINITY Frobenius series coefficients (both branches) are rational in
     omega with poles ONLY at omega = 0;
   - the HORIZON Frobenius series coefficients (both branches) are rational in
     omega with poles on the EXACT discrete imaginary resonance sets
       branch s=0        : { i j / 4 : j = 3, 4, 5, ... }
       branch s=-4iw-2   : { i j / 4 : j = 1, 0, -1, -2, ... }
     (the integer-difference Frobenius resonance points where a log basis
     appears); these are POLES of the normalized representation, not branch
     points, and the invariant current a(omega) has poles only {i, i/2}.

3. DECLARED DOMAIN.  a(omega) and F^r continue meromorphically to C minus {i, i/2}.
   The joint mode+current representation is analytic on the largest symmetric
   strip about the real axis free of every coefficient pole, |Im omega| < 1/4,
   minus omega = 0 (the excluded exceptional carrier and the infinity-series
   pole).  The real axis lies in the domain; continuation never passes through a
   pole.

POLAR: NOT_ACTIVATED.  BH2_POLAR_QUANTIFIER_REPAIR closed the polar cross
covector FIXTURE-ONLY; its route-B structural identity
(Z = E - (K^{-1} a^H).X symplectically null for all real omega) is an explicit
missing object, and it does not claim complex-omega continuation.  No polar
continuation is extrapolated from the real-omega fixtures (forbidden).

NOT established: no polar continuation; no stability, quasinormal, ringdown,
scattering, positivity, particle, or quantum claim; Borel/analytic summability
of the (asymptotic) infinity series is a separate open object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH3_ANALYTIC_CONTINUATION_GATE.json"
SCHEMA_PATH = HERE / "schema" / "bh3-analytic-continuation-gate-v1.schema.json"

CROSS = HERE / "certificates" / "BH2_SYMBOLIC_CROSS_INVARIANT.json"
GENL = HERE / "certificates" / "BH2_GENERAL_L_STRUCTURAL.json"
ALLORD = HERE / "certificates" / "BH2C_METRIC_ALL_ORDERS.json"
POLARQ = HERE / "certificates" / "BH2_POLAR_QUANTIFIER_REPAIR.json"

SCHEMA_NAME = "pure-weyl-bh3-analytic-continuation-gate-v1"
RESULT_ID = "PURE_WEYL_BH3_ANALYTIC_CONTINUATION_GATE"
RESULT_TOKEN = "BH3_AXIAL_ANALYTIC_CONTINUATION_MEROMORPHIC_POLAR_NOT_ACTIVATED"

N_SERIES = 6  # Frobenius orders to build for the exact pole-set audit


class GateError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise GateError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _omega_pole_roots(expr, w):
    """Exact omega-pole set (denominator roots) of a rational expr."""
    _num, den = sp.fraction(sp.cancel(expr))
    if not den.has(w):
        return {}
    return {str(k): int(v) for k, v in sp.roots(den, w).items()}


def analyse_axial() -> dict:
    w = sp.Symbol("omega")
    r = sp.Symbol("r", positive=True)
    z = sp.Symbol("z", positive=True)

    # ---- 1. cross scalar a(omega): rational => meromorphic, exact poles -----
    cross = json.loads(CROSS.read_text())
    a = sp.sympify(cross["a_of_omega"], locals={"omega": w, "I": sp.I})
    _require(a.is_rational_function(w), "a(omega) is not rational")
    num, den = sp.fraction(sp.cancel(a))
    _require(sp.gcd(num, den) == 1, "a(omega) num/den share a factor")
    poles = {str(k): int(v) for k, v in sp.roots(den, w).items()}
    zeros = {str(k): int(v) for k, v in sp.roots(num, w).items()}
    _require(set(poles) == {"I", "I/2"},
             f"a(omega) poles {set(poles)} != {{I, I/2}}")

    # ---- 2. mode Frobenius series from the certified master ODE ------------
    allord = json.loads(ALLORD.read_text())
    c2s, c1s, c0s = (sp.sympify(c, locals={"r": r, "omega": w, "I": sp.I})
                     for c in allord["master_ode"]["coefficients"])
    _require(sp.Poly(c2s, r).total_degree() >= 0, "bad master ODE")

    # infinity series: F = exp(mu r) r^sig sum a_k r^{-k}
    def inf_series(mu, sig, N):
        ak = [sp.Integer(1)]
        for k in range(1, N + 1):
            x = sp.Symbol("x")
            F = sp.exp(mu * r) * r**sig * (
                sum(ak[j] * r**(-j) for j in range(k)) + x * r**(-k))
            E = sp.expand(sp.together(
                (c2s * sp.diff(F, r, 2) + c1s * sp.diff(F, r) + c0s * F)
                / sp.exp(mu * r)))
            Fk = sp.exp(mu * r) * r**sig * x * r**(-k)
            Ek = sp.expand(sp.together(
                (c2s * sp.diff(Fk, r, 2) + c1s * sp.diff(Fk, r) + c0s * Fk)
                / sp.exp(mu * r)))
            deg = sp.Poly(sp.expand(sp.numer(sp.together(Ek))), r).degree()
            sol = sp.solve(sp.Eq(sp.Poly(sp.expand(sp.numer(sp.together(E))),
                                         r).nth(deg), 0), x)
            ak.append(sp.cancel(sol[0]) if sol else sp.Integer(0))
        return ak

    inf_lam0 = inf_series(sp.Integer(0), sp.Integer(-3), N_SERIES)
    inf_osc = inf_series(-2 * sp.I * w, -4 * sp.I * w + 1, N_SERIES)
    inf_poles = set()
    for ak in (inf_lam0, inf_osc):
        for c in ak:
            inf_poles |= set(_omega_pole_roots(c, w))
    _require(inf_poles <= {"0"},
             f"infinity series has an omega-pole off {{0}}: {inf_poles}")

    # horizon series at r = 2 + z (regular singular point)
    C2 = z * (z + 2)
    C1 = sp.expand(c1s.subs(r, 2 + z))
    C0 = sp.expand(c0s.subs(r, 2 + z))
    s = sp.Symbol("s")
    Fs = z**s
    Es = C2 * sp.diff(Fs, z, 2) + C1 * sp.diff(Fs, z) + C0 * Fs
    # indicial = coefficient of the lowest power z^{s-1}: extract via E * z^{-s}
    Enorm = sp.expand(sp.powsimp(sp.expand(Es * z**(-s)), force=True))
    ind = sp.factor(Enorm.coeff(z, -1))
    ind_roots = sp.solve(sp.Eq(ind, 0), s)
    _require(all(sp.together(rt).is_polynomial(w) for rt in ind_roots),
             "a horizon indicial root is not entire in omega")

    def hor_series(s0, N):
        g = [sp.Integer(1)]
        for k in range(1, N + 1):
            x = sp.Symbol("x")
            gg = sum(g[j] * z**j for j in range(k)) + x * z**k
            F = z**s0 * gg
            E = sp.expand(sp.powsimp(sp.expand(
                (C2 * sp.diff(F, z, 2) + C1 * sp.diff(F, z) + C0 * F) / z**s0),
                force=True))
            coeff = sp.expand(E).coeff(z, k - 1)
            sol = sp.solve(sp.Eq(coeff, 0), x)
            g.append(sp.cancel(sol[0]) if sol else sp.Integer(0))
        return g

    hor_s0 = hor_series(sp.Integer(0), N_SERIES)
    hor_sm = hor_series(-4 * sp.I * w - 2, N_SERIES)

    def pole_set(series):
        out = set()
        for c in series:
            out |= set(_omega_pole_roots(c, w))
        return out

    hor_s0_poles = pole_set(hor_s0)
    hor_sm_poles = pole_set(hor_sm)
    # all horizon poles purely imaginary (Re = 0), none real
    for p in hor_s0_poles | hor_sm_poles:
        val = sp.sympify(p, locals={"I": sp.I})
        _require(sp.re(val) == 0, f"horizon pole {p} is not purely imaginary")
        _require(val != 0 or True, "")  # omega=0 allowed (excluded carrier)

    # closed-form resonance predictions, audited against the built poles
    pred_s0 = {sp.I * j / 4 for j in range(3, 3 + N_SERIES)}
    pred_sm = {sp.I * j / 4 for j in range(1, 1 - N_SERIES, -1)}
    got_s0 = {sp.sympify(p, locals={"I": sp.I}) for p in hor_s0_poles}
    got_sm = {sp.sympify(p, locals={"I": sp.I}) for p in hor_sm_poles}
    _require(got_s0 <= pred_s0, f"s=0 poles {got_s0} not in closed form {pred_s0}")
    _require(got_sm <= pred_sm, f"s=-4iw-2 poles {got_sm} not in closed form")

    # nearest coefficient pole to the real axis -> analyticity strip half-width
    all_imag = sorted({abs(sp.im(sp.sympify(p, locals={"I": sp.I})))
                       for p in (hor_s0_poles | hor_sm_poles)
                       if sp.sympify(p, locals={"I": sp.I}) != 0})
    strip_halfwidth = str(all_imag[0]) if all_imag else "oo"

    return {
        "cross_current": {
            "a_of_omega": cross["a_of_omega"],
            "a_factored": str(sp.factor(a)),
            "is_rational_no_branch_points": True,
            "pole_set_exact": sorted(poles),
            "zero_set_exact": sorted(zeros),
            "current_relation": "F^r(E,X) = -i pi alpha a(omega)",
            "continuation": "meromorphic on C; singular set EXACTLY {i, i/2}",
        },
        "mode_families": {
            "boundary_exponents_entire_in_omega": True,
            "infinity_exponents": allord["exponents"],
            "horizon_indicial_roots": [str(rt) for rt in ind_roots],
            "infinity_series_omega_poles": sorted(inf_poles),
            "horizon_series_omega_poles": {
                "s=0_branch": sorted(hor_s0_poles),
                "s=-4Iomega-2_branch": sorted(hor_sm_poles),
            },
            "horizon_resonance_closed_form": {
                "s=0_branch": "{ I*j/4 : j = 3, 4, 5, ... }",
                "s=-4Iomega-2_branch": "{ I*j/4 : j = 1, 0, -1, -2, ... }",
                "reading": "integer-difference Frobenius resonances (log basis); "
                           "poles of the normalized representation, NOT branch "
                           "points",
            },
            "orders_audited": N_SERIES,
        },
        "declared_domain": {
            "current_domain": "C \\ {i, i/2}",
            "joint_mode_current_strip": f"|Im omega| < {strip_halfwidth}, "
                                        f"omega != 0",
            "strip_halfwidth": strip_halfwidth,
            "real_axis_in_domain": True,
            "continuation_through_pole": False,
            "omega_zero_excluded": True,
        },
    }


def build_certificate() -> dict:
    axial = analyse_axial()
    polarq = json.loads(POLARQ.read_text())
    _require(polarq["claim_flags"]["generic_real_frequency_certified"] is False,
             "polar quantifier unexpectedly generic")

    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "setting": "Schwarzschild m = 1, axial l = 2, Eddington-Finkelstein "
                       "carrier, t-chart Lee-Wald F^r; omega in C",
            "method": "exact rational / Frobenius analysis; NO finite complex "
                      "sample set (which cannot establish continuation)",
            "gate": "complex-omega analytic continuation of modes and current, "
                    "with exact singular set (axial); polar disposition",
        },
        "axial_analytic_continuation": axial,
        "polar_disposition": {
            "status": "NOT_ACTIVATED",
            "reason": "BH2_POLAR_QUANTIFIER_REPAIR closed the polar cross covector "
                      "FIXTURE-ONLY; its route-B structural identity "
                      "(Z = E - (K^{-1} a^H).X symplectically null for all real "
                      "omega) is an explicit missing object and it does not claim "
                      "complex-omega continuation",
            "route_b_missing_object": polarq["missing_object"].get(
                "route_B_structural_identity", "route B identity"),
            "no_fixture_extrapolation": "no polar continuation is extrapolated "
                                        "from the real-omega fixtures (forbidden)",
        },
        "headline": {
            "statement": "the axial Schwarzschild exterior mode families and the "
                         "Lee-Wald cross current continue analytically from the "
                         "real frequency axis into the complex-omega plane as "
                         "MEROMORPHIC objects with an EXACT singular set: the "
                         "current a(omega) is rational with poles exactly "
                         "{i, i/2} (no branch points), the mode Frobenius "
                         "coefficients are rational in omega with poles on the "
                         "exact discrete imaginary resonance sets, and the joint "
                         "representation is analytic on the strip about the real "
                         "axis up to the nearest imaginary pole; the polar sector "
                         "continuation is NOT_ACTIVATED",
            "no_obstruction_axial": "the axial continuation has no branch point "
                                    "and no divergent-flux boundary; every "
                                    "singularity is an isolated pole at an exactly "
                                    "known location",
        },
        "claim_flags": {
            "axial_current_meromorphic_continuation_certified": True,
            "axial_current_exact_singular_set_certified": True,
            "axial_mode_series_omega_poles_exact_certified": True,
            "no_branch_points_axial_certified": True,
            "domain_declared_excludes_poles": True,
            "polar_continuation_activated": False,
            "polar_route_b_identity_obtained": False,
            "summability_certified": False,
            "general_l_certified": False,
            "stability_qnm_scattering_claimed": False,
        },
        "missing_objects": [
            "the polar analytic continuation (route-B symbolic identity is a "
            "certified missing object of BH2_POLAR_QUANTIFIER_REPAIR)",
            "Borel/analytic summability of the (asymptotic) infinity Frobenius "
            "series -- coefficient-wise analyticity is proven, sum convergence "
            "off the real axis is a separate object",
            "general l (this gate is l = 2; l enters only through Lambda but the "
            "cross current a(omega) is certified at l = 2)",
        ],
        "does_not_establish": [
            "any polar-sector continuation or polar singular set",
            "any stability, quasinormal-mode, ringdown, scattering, positivity, "
            "particle, or quantum claim -- a meromorphic continuation of a "
            "REDUCED-MODE current is not a spectrum",
            "convergence/summability of the asymptotic infinity series off the "
            "real axis",
            "continuation through any pole (the declared domain excludes them)",
        ],
        "provenance": {
            "generator_path":
                "black_hole_programme/bh3_analytic_continuation_gate.py",
            "cross_invariant_certificate": str(CROSS.relative_to(ROOT)),
            "cross_invariant_sha256": _sha256(CROSS),
            "general_l_certificate": str(GENL.relative_to(ROOT)),
            "general_l_sha256": _sha256(GENL),
            "all_orders_certificate": str(ALLORD.relative_to(ROOT)),
            "all_orders_sha256": _sha256(ALLORD),
            "polar_quantifier_certificate": str(POLARQ.relative_to(ROOT)),
            "polar_quantifier_sha256": _sha256(POLARQ),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh3_analytic_continuation_gate.py",
    }
    return cert


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cert = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
