"""Exact finite-jet probe for the corrected generic-ell additional lift."""
from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "black_hole_programme/phase2/general_l_axial_current"))
from general_l_axial_current import (LAMBDA, M, R, W, angular_reduce,
                                     literal_unsummed_current,
                                     metric_profile_series)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_selection import corrected_x0_lift

I = sp.I


def radial_jet(rate, base, coeffs, dr, dv_factor):
    data = {n: sp.expand(dv_factor * c) for n, c in enumerate(coeffs) if c != 0}
    for _ in range(dr):
        nxt = {}
        for n, c in data.items():
            nxt[n] = nxt.get(n, 0) + rate * c
            nxt[n + 1] = nxt.get(n + 1, 0) + (base - n) * c
        data = {n: sp.expand(c) for n, c in nxt.items() if c != 0}
    return base, data


def pair_table(current, names, left, right, ell, minimum_power=-20):
    """Return all nonzero exact radial coefficients available in finite jets."""
    v, r = names["v"], names["r"]
    atom_map, jets = {}, {}
    for side, profile, conjugate in (("a", left, False), ("b", right, True)):
        rate, rows = profile
        for fi, field in enumerate(("h0", "h1")):
            fn = names[field + side]
            atoms = [fn] + [d for d in current.atoms(sp.Derivative) if d.expr == fn]
            for atom in atoms:
                dv = 0 if atom == fn else sum(int(p[1]) for p in atom.args[1:] if p[0] == v)
                dr = 0 if atom == fn else sum(int(p[1]) for p in atom.args[1:] if p[0] == r)
                symbol = sp.Symbol(f"J_{side}_{field}_{dv}_{dr}")
                atom_map[atom] = symbol
                base, coeffs = rows[fi]
                if conjugate:
                    jets[symbol] = radial_jet(sp.conjugate(rate), sp.conjugate(base),
                                              [sp.conjugate(c) for c in coeffs], dr,
                                              (-I * W) ** dv)
                else:
                    jets[symbol] = radial_jet(rate, base, coeffs, dr, (I * W) ** dv)
    encoded = sp.expand(current.xreplace(atom_map))
    collected = {}
    jet_symbols = set(jets)
    for term in sp.Add.make_args(encoded):
        present = list(term.free_symbols & jet_symbols)
        if len(present) != 2:
            raise RuntimeError(f"non-bilinear current term: {term}")
        ja, jb = present
        coefficient = sp.factor_terms(term / (ja * jb))
        angular, rp = coefficient.as_coeff_exponent(r)
        if r in angular.free_symbols:
            raise RuntimeError(f"nonmonomial radial coefficient: {coefficient}")
        ba, da = jets[ja]
        bb, db = jets[jb]
        for na, ca in da.items():
            for nb, cb in db.items():
                power = sp.simplify(rp + ba + bb - na - nb)
                if not power.is_Integer:
                    raise RuntimeError(f"nonintegral radial power {power}")
                if int(power) < minimum_power:
                    continue
                collected[int(power)] = collected.get(int(power), 0) + angular * ca * cb
    reduced = {}
    for power in sorted(collected, reverse=True):
        raw = sp.cancel(sp.together(collected[power]))
        if raw == 0:
            continue
        value = sp.factor(angular_reduce(raw, names, ell).subs(M, 1))
        if value != 0:
            reduced[power] = value
    return reduced


def main():
    current, names = literal_unsummed_current()
    ell = sp.Symbol("ell", integer=True, positive=True)
    e0 = (sp.Integer(0), ((sp.Integer(1), [-I * W / 2, (LAMBDA - 2) / 4, 1]),
                          (sp.Integer(0), [sp.Rational(1, 2)])))
    e2 = (-2 * I * W, metric_profile_series(-2 * I * W, 1 - 4 * I * M * W, 4))
    x0_lift = corrected_x0_lift(2)
    h0_x0 = [x0_lift["H0"].get(n, 0) for n in range(max(x0_lift["H0"]) + 1)]
    x0 = (sp.Integer(0), ((sp.Integer(2), h0_x0),
                          (sp.Integer(-1), x0_lift["H1"])))
    D = LAMBDA - 16 * W**2 + 4 * I * W + 2
    h1 = 2 * D / (LAMBDA - 2)
    h0 = (-LAMBDA * W - I * LAMBDA + 16 * W**3 + 12 * I * W**2
          + 2 * W - 2 * I) / (W * (LAMBDA - 2))
    x2 = (-2 * I * W, ((1 - 4 * I * W, [h0]), (1 - 4 * I * W, [h1])))
    profiles = {"E0": e0, "X0": x0, "E2": e2, "X2": x2}
    for a, b, floor in (("E0", "X0", -2), ("X0", "X0", -1)):
        table = pair_table(current, names, profiles[a], profiles[b], ell, floor)
        print(a + "|" + b, list(table.items())[:4])


if __name__ == "__main__":
    main()
