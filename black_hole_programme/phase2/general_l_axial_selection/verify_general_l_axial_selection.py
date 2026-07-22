"""Independent exact replay of the generic-ell axial X0 counterexample."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
sys.path.insert(0, str(ROOT / "black_hole_programme/phase2/general_l_axial_current"))
from general_l_axial_current import LAMBDA as CUR_L, angular_reduce, literal_unsummed_current

r = sp.Symbol("r", positive=True)
w = sp.Symbol("omega", positive=True, real=True)
mass = sp.Symbol("M", positive=True, real=True)
Lam = CUR_L
I = sp.I


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def substitute_pair(current, names, left, right):
    v = names["v"]
    phase_a, phase_b = sp.exp(I * w * v), sp.exp(-I * w * v)
    replacements = {}
    for side, rows, phase in (("a", left, phase_a), ("b", right, phase_b)):
        for field, profile in zip(("h0", "h1"), rows):
            fn = names[field + side]
            value = profile * phase
            for derivative in current.atoms(sp.Derivative):
                if derivative.expr != fn:
                    continue
                dv = sum(int(pair[1]) for pair in derivative.args[1:] if pair[0] == v)
                dr = sum(int(pair[1]) for pair in derivative.args[1:] if pair[0] == r)
                replacements[derivative] = sp.diff(value, v, dv, r, dr)
            replacements[fn] = value
    return sp.powsimp(sp.expand(current.subs(replacements).doit()), force=True)


def independent_jet_coefficient(current, names, left, right, target):
    """Sparse target-power replay, independently implemented in this rail."""
    v = names["v"]
    symbols, data = {}, {}
    for side, profile, barred in (("a", left, False), ("b", right, True)):
        for field, (base, coefficients) in zip(("h0", "h1"), profile):
            fn = names[field + side]
            for atom in [fn] + [d for d in current.atoms(sp.Derivative) if d.expr == fn]:
                dv = 0 if atom == fn else sum(int(p[1]) for p in atom.args[1:] if p[0] == v)
                dr = 0 if atom == fn else sum(int(p[1]) for p in atom.args[1:] if p[0] == r)
                symbol = sp.Symbol(f"J_{side}_{field}_{dv}_{dr}")
                symbols[atom] = symbol
                entries = {n: value for n, value in enumerate(coefficients) if value != 0}
                factor = (-I * w) ** dv if barred else (I * w) ** dv
                if barred:
                    base = sp.conjugate(base)
                    entries = {n: sp.conjugate(value) for n, value in entries.items()}
                entries = {n: factor * value for n, value in entries.items()}
                for _ in range(dr):
                    differentiated = {}
                    for n, value in entries.items():
                        differentiated[n + 1] = differentiated.get(n + 1, 0) + (base - n) * value
                    entries = differentiated
                data[symbol] = (base, entries)
    encoded = sp.expand(current.xreplace(symbols))
    answer = 0
    jetset = set(data)
    for term in sp.Add.make_args(encoded):
        jets = list(term.free_symbols & jetset)
        if len(jets) != 2:
            continue
        coefficient = sp.factor_terms(term / (jets[0] * jets[1]))
        angular, rp = coefficient.as_coeff_exponent(r)
        b0, d0 = data[jets[0]]
        b1, d1 = data[jets[1]]
        needed = sp.simplify(rp + b0 + b1 - target)
        if not needed.is_Integer:
            continue
        needed = int(needed)
        answer += angular * sum(v0 * d1.get(needed - n0, 0)
                                for n0, v0 in d0.items())
    return sp.cancel(sp.together(answer))


def laurent_coeff(expr, power):
    t = sp.Symbol("t")
    value = sp.cancel(expr.subs(r, 1 / t))
    numerator, denominator = sp.fraction(value)
    independent, shift = denominator.as_coeff_exponent(t)
    if t in independent.free_symbols or not shift.is_Integer:
        raise RuntimeError("unexpected radial denominator in finite Laurent replay")
    return sp.cancel(sp.expand(numerator).coeff(t, -power + int(shift)) / independent)


def inverse_coeff(expr, order, t):
    value = sp.cancel(expr.subs(r, 1 / t))
    numerator, denominator = sp.fraction(value)
    independent, shift = denominator.as_coeff_exponent(t)
    if t in independent.free_symbols or not shift.is_Integer:
        raise RuntimeError("unexpected radial denominator in recurrence replay")
    return sp.cancel(sp.expand(numerator).coeff(t, order + int(shift)) / independent)


def main():
    payload = json.loads(CERT.read_text())
    repo = ROOT.parent.parent
    for rel, digest in payload["source_manifest"].items():
        path = repo / rel
        assert len(digest) == 40 and blob(path) == digest
        assert sha(path) == payload["content_sha256_manifest"][rel]

    # Independent source-row elimination.  The coefficient of F' in the
    # original r-phi Ricci row is -(r-2M)/(2r).
    c = sp.Function("c")(r)
    q = sp.Function("q")(r)
    actual = 2 * r * (sp.diff(c, r) - q) / (r - 2 * mass)
    legacy = -2 * r * q / (r - 2 * mass)
    ricci_coefficient = -(r - 2 * mass) / (2 * r)
    residual = sp.factor(ricci_coefficient * (legacy - actual))
    assert residual == sp.diff(c, r)

    # Independent carrier head and both resonance checks.
    t = sp.Symbol("t")
    p1 = I * Lam / (2 * w)
    p2 = -(Lam**2 - 2 * Lam + 8 * I * mass * w) / (8 * w**2)
    q2 = -Lam / (2 * w**2)
    p3 = -I * (Lam**3 - 8 * Lam**2 + 12 * Lam - 48 * I * mass * w) / (48 * w**3)
    q3 = -I * (Lam**2 - 2 * Lam + 4 * I * mass * w) / (4 * w**3)
    P = 1 + p1 / r + p2 / r**2 + p3 / r**3
    Q = q2 / r**2 + q3 / r**3
    carrier_p = (sp.diff(P, r, 2)
                 - (Lam * r - 4 * mass) / (r**2 * (r - 2 * mass)) * P
                 + 2 * I * w * r / (r - 2 * mass) * sp.diff(P, r)
                 + 2 * I * mass * w / (r * (r - 2 * mass)) * Q)
    carrier_q = (sp.diff(Q, r, 2) + 2 / (r - 2 * mass) * sp.diff(P, r)
                 - (Lam * r - 4 * mass - 2 * I * w * r**2)
                 / (r**2 * (r - 2 * mass)) * Q
                 + (2 * I * w * r + 2) / (r - 2 * mass) * sp.diff(Q, r))
    carrier_p_series = sp.series(carrier_p.subs(r, 1 / t), t, 0, 5).removeO().expand()
    carrier_q_series = sp.series(carrier_q.subs(r, 1 / t), t, 0, 5).removeO().expand()
    assert all(sp.factor(carrier_p_series.coeff(t, n)) == 0 for n in range(4))
    assert all(sp.factor(carrier_q_series.coeff(t, n)) == 0 for n in range(4))
    cexpr = sp.expand((r**2 * (sp.diff(P, r) + sp.diff(Q, r) + I * w * Q)
                       + 2 * r * (P + Q - sp.diff(Q, r)) - 2 * Q) / (Lam - 2))
    assert sp.limit(cexpr / r, r, sp.oo) == 2 / (Lam - 2)
    scalar_rhs = sp.expand(2 * (r**2 * sp.diff(cexpr, r, 2)
                                - r**2 * sp.diff(Q, r) - 2 * r * Q
                                + 2 * r * sp.diff(cexpr, r) - 2 * cexpr))
    rhs1 = inverse_coeff(scalar_rhs, 1, t)
    rhs2 = inverse_coeff(scalar_rhs, 2, t)
    f0 = sp.factor(rhs1 / (2 * I * w))
    assert sp.factor(rhs2 - (2 - Lam) * f0) == 0
    h1lead = -f0
    # H0' coefficient at r^-1: its vanishing excludes the inherited log.
    h0_rhs_reduced = sp.expand(((-I * w - 2 * mass / r**2) * h1lead / r
                                + (-1 + 2 * mass / r) * f0 / r**2
                                + 2 * cexpr - 4 * r / (Lam - 2)))
    h0_log = sp.factor(inverse_coeff(h0_rhs_reduced, 1, t))
    assert h0_log == 0
    assert sp.factor(sp.diff(2 * r**2 / (Lam - 2), r)
                     - 4 * r / (Lam - 2)) == 0

    # Literal-current replay, using only jets that can contribute at p>=-2.
    current, names = literal_unsummed_current()
    ell = sp.Symbol("ell", integer=True, positive=True)
    e0 = (-I * w * r / 2 + (Lam - 2) / 4 + mass / r, sp.Rational(1, 2))
    c2 = inverse_coeff(cexpr, 2, t)
    c1 = sp.factor(inverse_coeff(cexpr, 1, t))
    assert c1 == (Lam**2 - 2 * Lam + 4 * I * mass * w) / (4 * w**2 * (Lam - 2))
    assert sp.factor(inverse_coeff(sp.diff(cexpr, r) - 2 / (Lam - 2), 2, t)
                     + c1) == 0
    h0tail = sp.factor(f0 - 2 * c2)
    h0constant = sp.factor((Lam**2 - 2 * Lam - 4 * I * mass * w)
                           / (4 * w**2 * (Lam - 2)))
    x0 = (2 * r**2 / (Lam - 2) + h0constant + h0tail / r, h1lead / r)

    # Original forced rows through every jet capable of reaching p=-2.
    F = f0 / r**2
    h0, h1 = x0
    row_x = sp.expand(sp.diff(h0, r)
                      - ((-2 * mass - I * w * r**2) / r**2) * h1
                      - ((2 * mass - r) / r) * F - 2 * cexpr)
    assert all(sp.factor(inverse_coeff(row_x, n, t)) == 0
               for n in (-1, 0, 1, 2))
    assert sp.factor(sp.diff(h1, r) - F) == 0
    d = -2 / (r * (r - 2 * mass))
    e = (Lam * r + 4 * mass - 2 * I * w * r**2 - 2 * r) / (r**2 * (r - 2 * mass))
    fcoef = (-4 * mass - 2 * I * w * r**2) / (r * (r - 2 * mass))
    source_f = 2 * r * (sp.diff(cexpr, r) - Q) / (r - 2 * mass)
    row_f = sp.cancel(sp.diff(F, r) - d * h0 - e * h1 - fcoef * F - source_f)
    row_f_series = sp.series(row_f.subs(r, 1 / t), t, 0, 4).removeO().expand()
    assert all(sp.factor(row_f_series.coeff(t, n)) == 0 for n in range(3))
    # Mutation controls: the legacy omission and a changed leading lift are rejected.
    assert sp.diff(c, r) != 0
    legacy_row_f = sp.cancel(row_f + 2 * r * sp.diff(cexpr, r) / (r - 2 * mass))
    assert sp.factor(sp.series(legacy_row_f.subs(r, 1 / t), t, 0, 1)
                     .removeO().coeff(t, 0)) == 4 / (Lam - 2)
    assert sp.factor((sp.diff(-2 * r**2 / (Lam - 2), r)
                      - 4 * r / (Lam - 2)) / r) == -8 / (Lam - 2)
    e0_rows = ((sp.Integer(1), [-I * w / 2, (Lam - 2) / 4, mass]),
               (sp.Integer(0), [sp.Rational(1, 2)]))
    x0_rows = ((sp.Integer(2), [2 / (Lam - 2), 0, h0constant, h0tail]),
               (sp.Integer(-1), [h1lead]))
    ex_raw = independent_jet_coefficient(current, names, e0_rows, x0_rows, -2)
    ex_coeff = sp.factor(angular_reduce(ex_raw, names, ell).subs(mass, 1))
    expected = (-8 * I * sp.pi * names["alpha"] * Lam
                * (Lam**2 - 2 * Lam - 6 * I * w)
                / (w * (Lam - 2) * (2 * ell + 1)))
    assert sp.simplify(ex_coeff - expected) == 0
    for power in (1, 0, -1):
        raw = independent_jet_coefficient(current, names, x0_rows, x0_rows, power)
        if raw != 0:
            assert angular_reduce(raw, names, ell) == 0

    # Independent literal-current filtration: rate-zero radial derivatives
    # never raise power, and the exact maximal coefficient shifts are fixed.
    atom_map, metadata = {}, {}
    for side in "ab":
        for field in ("h0", "h1"):
            fn = names[field + side]
            for atom in [fn] + [d for d in current.atoms(sp.Derivative) if d.expr == fn]:
                dr = 0 if atom == fn else sum(int(pair[1]) for pair in atom.args[1:] if pair[0] == r)
                symbol = sp.Symbol(f"K_{side}_{field}_{dr}_{len(atom_map)}")
                atom_map[atom] = symbol
                metadata[symbol] = (field, dr)
    encoded = sp.expand(current.xreplace(atom_map))
    shifts = {}
    for term in sp.Add.make_args(encoded):
        jets = list(term.free_symbols & set(metadata))
        if len(jets) != 2:
            continue
        coeff = sp.factor_terms(term / (jets[0] * jets[1]))
        _, radial_power = coeff.as_coeff_exponent(r)
        key = tuple(sorted((metadata[jets[0]][0], metadata[jets[1]][0])))
        shift = int(radial_power) - metadata[jets[0]][1] - metadata[jets[1]][1]
        shifts[key] = max(shifts.get(key, -99), shift)
    assert shifts == {("h0", "h0"): -3, ("h0", "h1"): -2,
                      ("h1", "h1"): -1}

    assert payload["legacy_fixture_obstruction"]["X0_residual_head"] == \
        "2*S_ell/(Lambda-2)+O(r^-2)"
    assert payload["legacy_fixture_obstruction"]["ell2_control"] == \
        "Lambda=6 gives residual S_2/2+O(r^-2), nonzero"
    assert sp.factor((2 / (Lam - 2)).subs(Lam, 6)) == sp.Rational(1, 2)
    assert payload["disposition"]["headline_selection_theorem"] == "OBSTRUCTED_BY_COUNTEREXAMPLE"
    print("PASS independent source-row, recurrence, current and ell=2 replay")


if __name__ == "__main__":
    main()
