"""Independent exact verifier for the generic-ell axial asymptotic theorem.

The decisive rail recomputes ell=3 from the explicit Legendre polynomial P3
on the verifier-side Schouten/Kulkarni--Nomizu geometry engine.  It never uses
the producer's symbolic-Lambda harmonic reduction.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
BH = HERE.parents[1]
ROOT = BH.parent
if str(BH) not in sys.path:
    sys.path.insert(0, str(BH))

from linearized_bach import LinearizedBach
from verify_bh2a_axial_operator import VbGeo

CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def _cancel(expression):
    return sp.cancel(sp.together(expression))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _background():
    v, ph = sp.symbols("v phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    mass = sp.Symbol("M", positive=True)
    omega = sp.Symbol("omega")
    B = 1 - 2 * mass / r
    metric = sp.zeros(4, 4)
    metric[0, 0] = -B
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    return (v, r, x, ph), mass, omega, metric


def concrete_metric_l3():
    (v, r, x, ph), mass, omega, metric = _background()
    geo = VbGeo([v, r, x, ph], metric)
    P3 = (5 * x**3 - 3 * x) / 2
    S3 = sp.expand(-(1 - x**2) * sp.diff(P3, x))
    T3 = sp.expand(12 * P3 - 2 * x * sp.diff(P3, x))
    h0, h1 = sp.Function("h0v")(v, r), sp.Function("h1v")(v, r)
    perturbation = sp.zeros(4, 4)
    perturbation[0, 3] = perturbation[3, 0] = h0 * S3
    perturbation[1, 3] = perturbation[3, 1] = h1 * S3
    linearized = LinearizedBach(geo)
    linearized.build(perturbation)
    rx = _cancel(linearized.dRic[2, 3] / T3)
    rr = _cancel(linearized.dRic[1, 3] / S3)
    _check(not rx.has(x) and not rr.has(x), "concrete ell=3 metric stripping failed")
    H0, H1 = sp.Function("H0v")(r), sp.Function("H1v")(r)
    phase = sp.exp(sp.I * omega * v)
    rx = _cancel(sp.expand(rx.subs({h0: H0 * phase, h1: H1 * phase}).doit() / phase))
    rr = _cancel(sp.expand(rr.subs({h0: H0 * phase, h1: H1 * phase}).doit() / phase))
    H0p = sp.solve(sp.Eq(rx, 0), sp.Derivative(H0, r))[0]
    H0pp = sp.diff(H0p, r).subs(sp.Derivative(H0, r), H0p)
    reduced = rr.subs({sp.Derivative(H0, (r, 2)): H0pp,
                       sp.Derivative(H0, r): H0p}).doit()
    H1pp = sp.solve(sp.Eq(sp.expand(reduced), 0), sp.Derivative(H1, (r, 2)))[0]
    state = [H0, H1, sp.Derivative(H1, r)]
    matrix = sp.zeros(3, 3)
    for j, entry in enumerate(state):
        matrix[0, j] = _cancel(sp.expand(H0p).coeff(entry))
        matrix[2, j] = _cancel(sp.expand(H1pp).coeff(entry))
    matrix[1, 2] = 1
    return matrix, r, omega, mass


def concrete_carrier_l3():
    (v, r, x, ph), mass, omega, metric = _background()
    geo = VbGeo([v, r, x, ph], metric)
    gi, Gamma = geo.ginv, geo.Gamma
    P3 = (5 * x**3 - 3 * x) / 2
    S3 = sp.expand(-(1 - x**2) * sp.diff(P3, x))
    T3 = sp.expand(12 * P3 - 2 * x * sp.diff(P3, x))
    p, q, c = (sp.Function("pv")(v, r), sp.Function("qv")(v, r),
               sp.Function("cv")(v, r))
    carrier = sp.zeros(4, 4)
    carrier[0, 3] = carrier[3, 0] = p * S3
    carrier[1, 3] = carrier[3, 1] = q * S3
    carrier[2, 3] = carrier[3, 2] = c * T3
    divergence = sum(gi[a, e] * geo.covd2(carrier, e, a, 3)
                     for a in range(4) for e in range(4) if gi[a, e] != 0)
    csol = sp.solve(sp.Eq(_cancel(divergence), 0), c)
    _check(len(csol) == 1, "concrete ell=3 carrier divergence did not close")
    carrier = sp.Matrix(4, 4, lambda i, j: _cancel(
        carrier.subs(c, csol[0]).doit()[i, j]))
    first = [[[_cancel(geo.covd2(carrier, e, a, b)) for b in range(4)]
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
            * sum(gi[cc, e] * gi[d, f] * carrier[e, f]
                  for e in range(4) for f in range(4))
            for cc in range(4) for d in range(4)
        )
        return _cancel(box / 2 + curvature)

    lv, lr = _cancel(operator_row(0, 3) / S3), _cancel(operator_row(1, 3) / S3)
    _check(not lv.has(x) and not lr.has(x), "concrete ell=3 carrier stripping failed")
    Pc, Qc = sp.Function("Pcv")(r), sp.Function("Qcv")(r)
    phase = sp.exp(sp.I * omega * v)
    lv = sp.expand(_cancel(lv.subs({p: Pc * phase, q: Qc * phase}).doit() / phase))
    lr = sp.expand(_cancel(lr.subs({p: Pc * phase, q: Qc * phase}).doit() / phase))
    P2, Q2 = sp.Derivative(Pc, (r, 2)), sp.Derivative(Qc, (r, 2))
    solved = sp.solve([sp.Eq(lv, 0), sp.Eq(lr, 0)], [P2, Q2], dict=True)
    _check(len(solved) == 1, "concrete ell=3 carrier principal solve failed")
    state = [Pc, sp.Derivative(Pc, r), Qc, sp.Derivative(Qc, r)]
    matrix = sp.zeros(4, 4)
    matrix[0, 1] = matrix[2, 3] = 1
    for row, expression in ((1, sp.expand(solved[0][P2])),
                            (3, sp.expand(solved[0][Q2]))):
        for j, entry in enumerate(state):
            matrix[row, j] = _cancel(expression.coeff(entry))
    return matrix, r, omega, mass


def _parse_matrix(rows, symbols):
    return sp.Matrix([[sp.sympify(entry, locals=symbols) for entry in row]
                      for row in rows])


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    for record in payload["provenance"].values():
        _check(record["sha256"] == _sha256(ROOT / record["path"]),
               f"provenance drift: {record['path']}")

    metric, r, omega, mass = concrete_metric_l3()
    symbols = {"r": r, "omega": omega, "M": mass, "Lambda": sp.Integer(12),
               "I": sp.I}
    expected_metric = _parse_matrix(payload["metric"]["matrix"], symbols).subs(
        sp.Symbol("Lambda"), 12)
    _check((metric - expected_metric).applyfunc(sp.simplify) == sp.zeros(3),
           "independent ell=3 metric matrix mismatch")

    carrier, rc, omegac, massc = concrete_carrier_l3()
    substitutions = {rc: r, omegac: omega, massc: mass}
    carrier = carrier.subs(substitutions).applyfunc(_cancel)
    expected_carrier = _parse_matrix(payload["carrier"]["matrix"], symbols).subs(
        sp.Symbol("Lambda"), 12)
    _check((carrier - expected_carrier).applyfunc(sp.simplify) == sp.zeros(4),
           "independent ell=3 carrier matrix mismatch")

    A0 = carrier.applyfunc(lambda entry: sp.simplify(sp.limit(entry, r, sp.oo)))
    z = sp.Symbol("z")
    _check(sp.factor(A0.charpoly(z).as_expr())
           == z**2 * (z + 2 * sp.I * omega)**2,
           "independent ell=3 carrier rates mismatch")
    A1 = (r * (carrier - A0)).applyfunc(
        lambda entry: sp.simplify(sp.limit(entry, r, sp.oo)))
    for rate, expected_powers in (
        (sp.Integer(0), {sp.Integer(0), sp.Integer(-1)}),
        (-2 * sp.I * omega,
         {-4 * sp.I * mass * omega, -4 * sp.I * mass * omega - 1}),
    ):
        eigenspace = (A0 - rate * sp.eye(4)).nullspace()
        other = -2 * sp.I * omega if rate == 0 else sp.Integer(0)
        complement = (A0 - other * sp.eye(4)).nullspace()
        basis = sp.Matrix.hstack(*(eigenspace + complement))
        reduced = (basis.inv() * A1 * basis)[:2, :2]
        powers = set(sp.solve(sp.Eq(reduced.charpoly(z).as_expr(), 0), z))
        _check(all(any(sp.simplify(value - wanted) == 0 for value in powers)
                   for wanted in expected_powers),
               f"independent ell=3 powers mismatch at rate {rate}")

    # Exact recurrence and exception mutation checks, reconstructed from fields.
    n = sp.Symbol("n", integer=True, nonnegative=True)
    for sector in payload["carrier"]["sectors"].values():
        top = sp.sympify(sector["top_recurrence_pivot"], locals={"n": n, "omega": omega})
        lower = sp.sympify(sector["lower_recurrence_pivot"], locals={"n": n, "omega": omega})
        _check(sp.simplify(top + 4 * n * (n - 1) * omega**2) == 0,
               "top recurrence pivot mutation survived")
        _check(sp.simplify(lower + 4 * n * (n + 1) * omega**2) == 0,
               "lower recurrence pivot mutation survived")
        _check(sector["top_n1_resonance"]["compatible"] is True
               and sector["logarithm_forced"] is False,
               "resonance/log disposition changed")
    _check(payload["exceptional_set"]["frequency"] == ["omega=0"],
           "omega=0 exceptional carrier omitted")
    _check(payload["exceptional_set"]["angular_representations"]
           == ["ell=0", "ell=1"], "angular exceptional set changed")
    flags = payload["claim_flags"]
    _check(flags["literal_lee_wald_current_computed"] is False
           and flags["finite_pairing_selection_certified"] is False
           and flags["polar_certified"] is False,
           "forbidden successor claim activated")
    print("PASS schema and provenance")
    print("PASS independent explicit-P3/VbGeo metric and carrier systems")
    print("PASS ell=3 rates/powers, recurrence pivots, exceptions and claim boundary")


if __name__ == "__main__":
    verify()
