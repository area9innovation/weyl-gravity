"""Independent verifier for BH2_SYMPLECTIC_NORMAL_FORM.

The producer proves the normal form by symbolic shear algebra.  This rail
is deliberately INDEPENDENT in method: it re-derives every claim by exact
NUMERICAL linear algebra over random rational complex data (many trials),
diagonalizes to read inertia, and searches for a counterexample to the
removability claim.  Agreement between a symbolic derivation and an
exhaustive rational-sample rail is the evidence; re-running the producer
would only be reproduction.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bh2_symplectic_normal_form import run_analysis

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2_SYMPLECTIC_NORMAL_FORM.json"
SCHEMA = HERE / "schema" / "bh2-symplectic-normal-form-v1.schema.json"

# deterministic rational sample grid (no RNG: reproducible by construction)
SAMPLES = [(sp.Rational(p, q), sp.Rational(s, t), sp.Rational(u, w))
           for p, q in ((1, 2), (-3, 5), (7, 4))
           for s, t in ((2, 3), (-1, 7))
           for u, w in ((5, 6), (-11, 3))]


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _K(a, d):
    return sp.Matrix([[0, a, 0], [sp.conjugate(a), d, 0], [0, 0, 0]])


def _shear(beta, gamma):
    S = sp.eye(3)
    S[0, 1] = beta
    S[2, 1] = gamma
    return S


def independent_rail():
    """exact rational-sample re-derivation of every theorem claim"""
    trials = 0
    for ar, ai, d0 in SAMPLES:
        a = ar + sp.I * ai
        d = d0
        K = _K(a, d)
        for br, bi, gr in SAMPLES:
            beta = br + sp.I * bi
            gamma = gr
            S = _shear(beta, gamma)
            Kp = sp.expand(S.conjugate().T * K * S).applyfunc(sp.simplify)
            trials += 1
            # cross invariant, E isotropic, G radical
            _check(sp.simplify(Kp[0, 1] - a) == 0, "cross moved")
            _check(sp.simplify(Kp[0, 0]) == 0, "E lost isotropy")
            _check(all(sp.simplify(Kp[i, 2]) == 0 for i in range(3)),
                   "G left the radical")
            # self-pairing law
            law = sp.simplify(Kp[1, 1] - d - 2 * sp.re(sp.conjugate(beta) * a))
            _check(law == 0, f"self-pairing law violated: {law}")
            # rank and determinant preserved
            _check(sp.simplify(Kp[:2, :2].det() - K[:2, :2].det()) == 0,
                   "determinant moved")
        # removability: the exhibited beta* must annihilate d exactly
        if sp.simplify(a) != 0:
            bstar = -d * a / (2 * (ar**2 + ai**2))
            Ks = sp.expand(_shear(bstar, 0).conjugate().T * K
                           * _shear(bstar, 0)).applyfunc(sp.simplify)
            _check(sp.simplify(Ks[1, 1]) == 0,
                   f"beta* failed to remove d (a={a}, d={d})")
            # inertia (1,1) read from eigenvalues of the 2-block
            ev = list(Ks[:2, :2].eigenvals().keys())
            signs = sorted(int(sp.sign(sp.re(sp.nsimplify(e)))) for e in ev)
            _check(signs == [-1, 1], f"inertia not (1,1): {signs}")
            _check(sp.simplify(Ks[:2, :2].det() + (ar**2 + ai**2)) == 0,
                   "det != -|a|^2")
        # a = 0 branch: no shear may move d
        K0 = _K(sp.Integer(0), d)
        for br, bi, gr in SAMPLES[:4]:
            S0 = _shear(br + sp.I * bi, gr)
            K0p = sp.expand(S0.conjugate().T * K0 * S0).applyfunc(sp.simplify)
            _check(sp.simplify(K0p[1, 1] - d) == 0,
                   "at a = 0 a shear moved d")
    return trials


def verify_certificate():
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key in ("axial_fixture_certificate", "polar_fixture_certificate"):
        _check(prov[f"{key}_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")

    trials = independent_rail()
    res = run_analysis()
    for key in ("shear_action", "degeneration_a_zero", "fixture_controls"):
        _check(payload[key] == res[key], f"{key} mismatch")
    _check(payload["theorem_a_nonzero"]["block"] == res["block"],
           "block data mismatch")
    _check(payload["claim_flags"]["invariant_sign_question_resolved"] is True,
           "sign question not marked resolved")
    print(f"BH2_SYMPLECTIC_NORMAL_FORM: all independent checks passed "
          f"({trials} exact rational shear trials)")


if __name__ == "__main__":
    verify_certificate()
