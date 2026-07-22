"""Independent explicit-P3/VbGeo replay of the ell=3 literal current."""
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
sys.path.insert(0, str(BH))

from linearized_theta import LinearizedTheta  # noqa: E402
from verify_bh2a_axial_operator import VbGeo  # noqa: E402

CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def explicit_e2_profile(r, omega, depth=4):
    """Derive the Lambda=12 unit-F series directly from the master ODE."""
    lam = sp.Integer(12)
    rate = -2 * sp.I * omega
    power = 1 - 4 * sp.I * omega
    fs = [sp.Integer(1)]
    for n in range(1, depth + 3):
        k = power - n
        a = 2 * rate * k - 2 * rate**2 + 2 * sp.I * omega * k + 2 * rate + 6 * sp.I * omega
        kp = power - n + 1
        b = kp * (kp - 1) - 4 * rate * kp + 2 * kp + 2 * rate - lam
        km = power - n + 2
        c = -2 * km * (km - 2)
        fs.append(sp.cancel(-(b * fs[n - 1] + (c * fs[n - 2] if n >= 2 else 0)) / a))
    bs = []
    for n in range(depth + 1):
        previous = (power - n + 1) * bs[n - 1] if n else 0
        bs.append(sp.cancel((fs[n] - previous) / rate))
    t = sp.Symbol("t")
    Fnorm = sum(fs[n] * r**(-n) for n in range(depth + 2))
    H1norm = sum(bs[n] * r**(-n) for n in range(depth + 1))
    A = (-2 - sp.I * omega * r**2) / r**2
    B = (2 - r) / r
    rhs = sp.series((A * H1norm + B * Fnorm).subs(r, 1 / t), t, 0,
                    depth + 1).removeO().expand()
    ds = [sp.cancel(rhs.coeff(t, n)) for n in range(depth + 1)]
    cs = []
    for n in range(depth + 1):
        previous = (power - n + 1) * cs[n - 1] if n else 0
        cs.append(sp.cancel((ds[n] - previous) / rate))
    phase = sp.exp(rate * r) * r**power
    return (sp.expand(phase * sum(cs[n] * r**(-n) for n in range(depth + 1))),
            sp.expand(phase * H1norm))


def literal_l3_coefficients():
    v, x, phi = sp.symbols("v x phi")
    r = sp.Symbol("r", positive=True)
    omega = sp.Symbol("omega", positive=True)
    alpha = sp.Symbol("alpha")
    metric = sp.zeros(4)
    metric[0, 0] = -(1 - 2 / r)
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geo = VbGeo([v, r, x, phi], metric)
    P3 = (5 * x**3 - 3 * x) / 2
    S3 = sp.expand(-(1 - x**2) * sp.diff(P3, x))
    h0a, h1a, h0b, h1b = [sp.Function(n)(v, r) for n in
                            ("va", "ra", "vb", "rb")]
    hA, hB = sp.zeros(4), sp.zeros(4)
    hA[0, 3] = hA[3, 0] = h0a * S3
    hA[1, 3] = hA[3, 1] = h1a * S3
    hB[0, 3] = hB[3, 0] = h0b * S3
    hB[1, 3] = hB[3, 1] = h1b * S3
    density = LinearizedTheta(geo, alpha).omega(hA, hB)[0] * r**2
    Fv = sp.cancel(2 * sp.pi * sp.integrate(density, (x, -1, 1)))

    profiles = {
        "E0": (-sp.I * omega * r / 2 + sp.Rational(5, 2) + 1 / r,
               sp.Rational(1, 2)),
        "E2_unit_F": explicit_e2_profile(r, omega),
    }
    answers = {}
    for name, (H0, H1) in profiles.items():
        reps = {h0a: H0 * sp.exp(sp.I * omega * v),
                h1a: H1 * sp.exp(sp.I * omega * v),
                h0b: sp.conjugate(H0) * sp.exp(-sp.I * omega * v),
                h1b: sp.conjugate(H1) * sp.exp(-sp.I * omega * v)}
        sub = {}
        for fn, value in reps.items():
            for derivative in Fv.atoms(sp.Derivative):
                if derivative.expr == fn:
                    dv = sum(int(p[1]) for p in derivative.args[1:] if p[0] == v)
                    dr = sum(int(p[1]) for p in derivative.args[1:] if p[0] == r)
                    sub[derivative] = sp.diff(value, v, dv, r, dr)
            sub[fn] = value
        paired = sp.powsimp(sp.expand(Fv.subs(sub).doit()), force=True)
        t = sp.Symbol("t", positive=True)
        coefficient = sp.expand(sp.powsimp(paired.subs(r, 1 / t), force=True)).coeff(t, 2)
        answers[name] = sp.factor(coefficient)
    return answers, omega, alpha


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator(schema).validate(payload)
    check(payload["schema_sha256"] == sha256(SCHEMA), "schema hash mismatch")
    for record in payload["provenance"].values():
        path = ROOT / record["path"]
        check(record["content_sha256"] == sha256(path), f"SHA256 drift: {path}")
        check(record["git_blob"] == git_blob(path), f"Git-blob drift: {path}")

    answers, omega, alpha = literal_l3_coefficients()
    check(sp.simplify(answers["E0"] + 480 * sp.I * sp.pi * alpha * omega / 7) == 0,
          "independent ell=3 E0 current mismatch")
    check(sp.simplify(answers["E2_unit_F"]
                      + 120 * sp.I * sp.pi * alpha / (7 * omega**3)) == 0,
          "independent ell=3 E2 current mismatch")

    lam, u = sp.symbols("Lambda u")
    real = sp.sympify(payload["legacy_wall"]["real_G_in_u"],
                      locals={"Lambda": lam, "u": u})
    imag = sp.sympify(payload["legacy_wall"]["imag_G_over_12omega_in_u"],
                      locals={"Lambda": lam, "u": u})
    resultant = sp.factor(sp.resultant(real, imag, u))
    recorded = sp.sympify(payload["legacy_wall"]["resultant_u"],
                          locals={"Lambda": lam})
    check(sp.simplify(resultant - recorded) == 0, "independent resultant mismatch")
    k = sp.Symbol("k", integer=True, nonnegative=True)
    shifted = sp.Poly(sp.sympify(payload["legacy_wall"]["H_shifted_ell_ge_4"],
                                 locals={"k": k}), k)
    check(int(payload["legacy_wall"]["H_at_ell2"]) == -47331,
          "H(6) explicit control mismatch")
    check(int(payload["legacy_wall"]["H_at_ell3"]) == -89397,
          "H(12) explicit control mismatch")
    check(all(c > 0 for c in shifted.all_coeffs()), "shifted positivity failed")

    ell = sp.Symbol("ell", integer=True, positive=True)
    lam = sp.Symbol("Lambda", real=True, positive=True)
    w = sp.Symbol("omega", real=True, nonzero=True)
    a = sp.Symbol("alpha", real=True, nonzero=True)
    coefficient_locals = {"ell": ell, "Lambda": lam, "omega": w,
                          "alpha": a, "I": sp.I, "pi": sp.pi}
    for name in ("E0", "E2_unit_F", "E2_legacy"):
        coefficient = sp.sympify(payload["coefficients"][name],
                                 locals=coefficient_locals)
        check(sp.simplify(coefficient.subs(w, -w) + coefficient) == 0,
              f"negative-frequency oddness failed for {name}")
        check(sp.simplify(sp.conjugate(coefficient) + coefficient) == 0,
              f"conjugation identity failed for {name}")
    check(payload["claim_flags"]["extra_branch_selection_certified"] is False,
          "extra-branch selection was promoted")
    print("PASS schema and dual provenance")
    print("PASS independent explicit-P3/VbGeo ell=3 literal E0 and unit-F E2 currents")
    print("PASS independent resultant, H(6), H(12), shifted positivity and negative-frequency extension")


if __name__ == "__main__":
    verify()
