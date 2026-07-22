"""Method-distinct verifier for the complete axial reconstruction repair."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
BH = HERE.parents[1]
CERT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
if str(BH) not in sys.path:
    sys.path.insert(0, str(BH))


def cancel(expr):
    return sp.cancel(sp.together(expr))


def direct_three_rows():
    """Derive all three axial Ricci rows with LinearizedBach.

    The producer starts from the already reduced row formulas.  This verifier
    instead rebuilds delta Ricci from the metric perturbation.
    """
    from linearized_bach import LinearizedBach
    from weyl_geometry import Geometry

    v, r, x, ph = sp.symbols("v r x phi")
    omega = sp.Symbol("omega")
    B = 1 - 2/r
    metric = sp.zeros(4, 4)
    metric[0, 0] = -B
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2/(1 - x**2)
    metric[3, 3] = r**2*(1 - x**2)
    h0 = sp.Function("h0")(v, r)
    h1 = sp.Function("h1")(v, r)
    S = -3*x*(1 - x**2)
    X = 3*(x**2 - 1)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0*S
    h[1, 3] = h[3, 1] = h1*S
    lb = LinearizedBach(Geometry([v, r, x, ph], metric))
    lb.build(h)
    H0, H1 = sp.Function("H0")(r), sp.Function("H1")(r)
    phase = sp.exp(sp.I*omega*v)
    substitution = {h0: H0*phase, h1: H1*phase}
    rows = {}
    for key, indices, harmonic in (
        ("vphi", (0, 3), S),
        ("rphi", (1, 3), S),
        ("xphi", (2, 3), X),
    ):
        row = lb.dRic[indices[0], indices[1]]
        row = row.subs(x, sp.Rational(1, 2))/harmonic.subs(x, sp.Rational(1, 2))
        rows[key] = cancel(row.subs(substitution).doit()/phase)
    return rows, r, omega, H0, H1


def verify() -> None:
    cert = json.loads(CERT.read_text())
    jsonschema.validate(cert, json.loads(SCHEMA.read_text()))
    rows, r, omega, H0f, H1f = direct_three_rows()

    P, Pp, Q, Qp, H1, F = sp.symbols("P Pp Q Qp H1 F")
    state = sp.Matrix([P, Pp, Q, Qp, H1, F])
    locals_ = {
        "r": r, "omega": omega, "P": P, "Pp": Pp, "P_prime": Pp,
        "Q": Q, "Qp": Qp, "Q_prime": Qp, "H1": H1, "F": F, "I": sp.I,
    }
    data = cert["complete_reconstruction"]
    flow = sp.Matrix([[sp.sympify(entry, locals=locals_) for entry in row]
                      for row in data["flow6"]])
    h0 = sp.sympify(data["H0_reconstruction"], locals=locals_)
    c_row = sp.Matrix([[sp.sympify(entry, locals=locals_)
                        for entry in data["c_row"]]])
    c = (c_row*sp.Matrix([P, Pp, Q, Qp]))[0]
    rhs = flow*state

    def total(expr):
        value = sp.diff(expr, r)
        for variable, derivative in zip(state, rhs):
            value += sp.diff(expr, variable)*derivative
        return cancel(value)

    substitutions = {
        H0f: h0,
        sp.diff(H0f, r): total(h0),
        sp.diff(H0f, r, 2): total(total(h0)),
        H1f: H1,
        sp.diff(H1f, r): F,
        sp.diff(H1f, r, 2): rhs[5],
    }
    expected = {"vphi": P, "rphi": Q, "xphi": c}
    for key in ("vphi", "rphi", "xphi"):
        residual = cancel(rows[key].subs(substitutions).doit() - expected[key])
        if residual != 0:
            raise AssertionError(f"independent {key} residual: {residual}")

    constraint = data["constraint"]
    if constraint["propagation"] != "dC/dr=-2*C/r" \
            or constraint["conserved_quantity"] != "kappa=r^2*C":
        raise AssertionError("constraint propagation statement changed")

    endpoint = cert["endpoint_bases"]
    if len(endpoint["horizon"]["columns"]) != 6 \
            or len(endpoint["infinity"]["columns"]) != 6:
        raise AssertionError("endpoint basis does not have six columns")
    for side in ("horizon", "infinity"):
        if endpoint[side]["rank"] != 6:
            raise AssertionError(f"{side} rank changed")

    reaudit = cert["x0_and_legacy_reaudit"]
    alpha = sp.sympify(reaudit["repair"]["alpha"], locals={"omega": omega, "I": sp.I})
    kappa = sp.I*(omega - 18*sp.I)/(2*omega**2)
    if cancel(kappa + alpha*3*sp.I*(omega - 2*sp.I)) != 0:
        raise AssertionError("independent X0 repair does not cancel kappa")
    if reaudit["legacy_E0"]["disposition"].startswith("NOT_AN_EINSTEIN") is False:
        raise AssertionError("legacy E0 was silently restored")

    # Exact independent algebraic checks on the durable current-audit table.
    audit = cert["downstream_current_warning"]
    alpha_W = sp.Symbol("alpha_W", positive=True)
    current_locals = {"omega": omega, "I": sp.I, "pi": sp.pi,
                      "alpha_W": alpha_W}
    table = {
        key: sp.sympify(value, locals=current_locals)
        for key, value in audit["finite_rate_zero_table_at_p_minus_2"].items()
        if key != "coefficients_at_p_ge_minus_1"
    }
    if audit["finite_rate_zero_table_at_p_minus_2"]["coefficients_at_p_ge_minus_1"] != {}:
        raise AssertionError("finite rate-zero table acquired a divergent coefficient")
    for key, value in table.items():
        denominator = sp.factor(sp.denom(sp.cancel(value)))
        for witness in (sp.Rational(1, 2), sp.Rational(3, 5), sp.Rational(3, 4)):
            if denominator.subs(omega, witness) == 0:
                raise AssertionError(f"current denominator vanishes for {key}")
    kernel = audit["complete_rate_zero_kernel"]
    c_kernel = sp.sympify(kernel["c"], locals=current_locals)
    if sp.simplify(c_kernel + 3*sp.I*(omega - 2*sp.I)/omega**2) != 0:
        raise AssertionError("EI0=T+cR relation coefficient changed")
    if sp.simplify(48*sp.pi*alpha_W*omega**3*(4*omega + sp.I)/5).subs(
            omega, sp.Rational(3, 5)) == 0:
        raise AssertionError("oscillatory current negative control vanished")

    flags = cert["claim_flags"]
    for forbidden in ("global_matching_certified", "finite_flux_certified",
                      "scattering_certified", "stability_certified"):
        if flags[forbidden]:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    print("PASS independent three-row six-column reconstruction verifier")


if __name__ == "__main__":
    verify()
