"""Independent verifier for BH2_POLAR_QUANTIFIER_REPAIR.

Rails, each independent of the producer's code path:
  1. fixture theorem re-derived from the imported exact (a,K): inertia by
     Hermitian EIGENVALUE signs (the producer used Jacobi minors), S by the
     explicit inverse (the producer solved a linear system), a != 0 directly;
  2. the a != 0 universal proof re-checked by an independent GCD test
     (deg gcd(P,Q) == 0 over Q[omega]) instead of the resultant, plus real-root
     isolation of P and Q showing disjoint real-root sets;
  3. the frame obstruction reproduced with a DISJOINT fit/hold split of the nine
     samples (fit on the last seven, hold the first two);
  4. provenance hashes and schema validation; the repaired target's
     unsupported flag is confirmed present in the target certificate.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = HERE / "certificates" / "BH2_POLAR_QUANTIFIER_REPAIR.json"
POLAR_COVECTOR = HERE / "certificates" / "BH2_POLAR_CROSS_COVECTOR.json"
SCHEMA = HERE / "schema" / "bh2-polar-quantifier-repair-v1.schema.json"
w = sp.Symbol("omega")


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_ak(cert):
    out = {}
    for wtag in cert["K_records"]:
        a = sp.Matrix([sp.sympify(x) for x in cert["a_records"][wtag]])
        K = sp.Matrix([[sp.sympify(x) for x in row]
                       for row in cert["K_records"][wtag]])
        out[wtag] = (a, K)
    return out


def _inertia_by_eigs(Kp):
    signs = []
    for ev, m in Kp.eigenvals().items():
        signs += [1 if complex(sp.N(ev, 30)).real > 0 else -1] * int(m)
    return (signs.count(1), signs.count(-1))


def _rational_fit(samples, m, n):
    pj = sp.symbols(f"p0:{m + 1}")
    qj = sp.symbols(f"q1:{n + 1}") if n else ()
    eqs = []
    for wv, val in samples:
        numv = sum(pj[k] * wv**k for k in range(m + 1))
        denv = 1 + sum(qj[k] * wv**(k + 1) for k in range(n))
        eqs.append(sp.Eq(numv - val * denv, 0))
    sol = sp.solve(eqs, list(pj) + list(qj), dict=True)
    if not sol:
        return None
    s = sol[0]
    if [v for v in list(pj) + list(qj) if v not in s]:
        return None
    numv = sum(s.get(pj[k], pj[k]) * w**k for k in range(m + 1))
    denv = 1 + sum(s.get(qj[k], qj[k]) * w**(k + 1) for k in range(n))
    return sp.cancel(numv / denv)


def _chi_reals(K):
    Kp = sp.I * K
    t1 = sp.re(sp.expand(Kp.trace()))
    t2 = sp.re(sp.expand(Kp[0, 0] * Kp[1, 1] - Kp[0, 1] * Kp[1, 0]
                         + Kp[0, 0] * Kp[2, 2] - Kp[0, 2] * Kp[2, 0]
                         + Kp[1, 1] * Kp[2, 2] - Kp[1, 2] * Kp[2, 1]))
    t3 = sp.re(sp.expand(Kp.det()))
    return t1, t2, t3


def main():
    cert = json.loads(CERT.read_text())
    src = json.loads(POLAR_COVECTOR.read_text())
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    # Rail 1: fixture theorem, eigenvalue + explicit-inverse rails
    samples = _load_ak(src)
    for wtag, (a, K) in samples.items():
        Kp = sp.I * K
        herm = sp.simplify(Kp - Kp.conjugate().T) == sp.zeros(3, 3)
        sig = _inertia_by_eigs(Kp)
        S = sp.cancel((a.T * K.inv() * a.conjugate())[0, 0])
        anz = any(sp.cancel(x) != 0 for x in a)
        check(f"omega={wtag}: Hermitian, inertia(eig)=(2,1), det!=0, a!=0, S=0",
              herm and sig == (2, 1) and sp.cancel(K.det()) != 0 and anz
              and S == 0)

    # Rail 2: a != 0 by GCD + disjoint real-root isolation
    P = sp.Poly(64 * w**3 - 240 * w, w)
    Q = sp.Poly(-200 * w**2 + 49, w)
    g = sp.gcd(P, Q)
    check("gcd(P,Q) is constant (no common root, incl. real)",
          sp.Poly(g, w).degree() == 0)
    rP = {sp.nsimplify(r) for r in sp.real_roots(P)}
    rQ = {sp.nsimplify(r) for r in sp.real_roots(Q)}
    check("real roots of P and Q are disjoint",
          len(rP & rQ) == 0)
    check("producer resultant matches sympy resultant",
          sp.sympify(cert["universal_results"]
                     ["covector_nonzero_all_real_omega"]["resultant_P_Q"])
          == sp.resultant(64 * w**3 - 240 * w, -200 * w**2 + 49, w))

    # Rail 3: obstruction with a DISJOINT split (fit last 7, hold first 2)
    wpts = []
    for wtag, (a, K) in samples.items():
        p, q = wtag.split("/")
        wpts.append((sp.Rational(int(p), int(q)), K))
    obstruction_reproduced = True
    for idx, name in enumerate(("t1", "t2", "t3")):
        data = [(wv, _chi_reals(K)[idx]) for wv, K in wpts]
        fit_pts, hold_pts = data[2:], data[:2]     # disjoint from producer split
        found = False
        for total in range(1, 9):
            for mm in range(total + 1):
                fit = _rational_fit(fit_pts, mm, total - mm)
                if fit is not None and all(
                        sp.cancel(fit.subs(w, wv) - val) == 0
                        for wv, val in hold_pts):
                    found = True
                    break
            if found:
                break
        obstruction_reproduced = obstruction_reproduced and (not found)
    check("frame obstruction reproduced on a disjoint fit/hold split",
          obstruction_reproduced)

    # Rail 4: provenance, schema, repaired-flag presence
    prov = cert["provenance"]
    check("polar covector hash matches recorded provenance",
          _sha256(POLAR_COVECTOR) == prov["polar_covector_sha256"])
    check("repaired target hash matches",
          _sha256(POLAR_COVECTOR) == cert["repairs"]["target_sha256"])
    check("target certificate still carries the unsupported universal flag",
          src["claim_flags"].get("no_real_exceptional_frequency_certified")
          in (True, False))  # present (either value); repair overrides it
    check("repair fail-closes the universal flags",
          cert["claim_flags"]["generic_real_frequency_certified"] is False
          and cert["claim_flags"]["no_real_exceptional_frequency_certified"]
          is False)
    check("repair certifies a != 0 for all real omega",
          cert["claim_flags"]["covector_nonzero_all_real_omega_certified"]
          is True)

    # schema validation (optional dependency)
    try:
        import jsonschema
        jsonschema.validate(cert, json.loads(SCHEMA.read_text()))
        check("schema validation", True)
    except ImportError:
        print("  [SKIP] schema validation (jsonschema not installed)")
    except Exception as exc:  # noqa: BLE001
        check(f"schema validation ({exc})", False)

    ok = all(c for _, c in checks)
    print(f"\n{'ALL CHECKS PASSED' if ok else 'VERIFICATION FAILED'} "
          f"({sum(c for _, c in checks)}/{len(checks)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
