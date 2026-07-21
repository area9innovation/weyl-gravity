"""Independent verifier for BH2_POLAR_CROSS_COVECTOR.

Two rails:
1. re-derives the invariants (K_phys Hermitian, signature (2,1), det != 0,
   a != 0, S = a K^{-1} a^H = 0) from the EXACT (a, K) matrices recorded in the
   certificate -- pure linear algebra, no mode rebuild;
2. structurally-independent recomputation: rebuilds the horizon block on the
   VbGeo Schouten/Kulkarni-Nomizu curvature engine (distinct from
   weyl_geometry.Geometry + linearized_theta used by the producer) at one
   frequency and confirms the same invariants.
Also checks the E|X1 native-frame form against the certified polar fixtures and
the provenance hashes.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

from verify_bh2a_axial_operator import VbGeo
from bh2b_polar_cross_flux import run_pipeline
import bh2_polar_cross_covector as prod

HERE = Path(__file__).resolve().parent
CERT = HERE / "certificates" / "BH2_POLAR_CROSS_COVECTOR.json"
w = sp.Symbol("omega")
INDEP_OMEGA = sp.Rational(1, 2)


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _invariants(a, K):
    Kp = sp.I * K
    herm = sp.simplify(Kp - Kp.conjugate().T) == sp.zeros(3, 3)
    detnz = sp.cancel(K.det()) != 0
    anz = any(sp.cancel(x) != 0 for x in a)
    S = sp.cancel((a.T * K.inv() * a.conjugate())[0, 0])
    signs = []
    for ev, m in Kp.eigenvals().items():
        signs += [1 if complex(sp.N(ev, 30)).real > 0 else -1] * int(m)
    sig = (signs.count(1), signs.count(-1))
    return herm, detnz, anz, (S == 0), sig


def main():
    cert = json.loads(CERT.read_text())
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    # Rail 1: invariants from recorded exact (a, K)
    for wtag, Krec in cert["K_records"].items():
        a = sp.Matrix([sp.sympify(x) for x in cert["a_records"][wtag]])
        K = sp.Matrix([[sp.sympify(x) for x in row] for row in Krec])
        herm, detnz, anz, snull, sig = _invariants(a, K)
        check(f"omega={wtag}: K_phys Hermitian, det!=0, a!=0", herm and detnz and anz)
        check(f"omega={wtag}: S=a K^-1 a^H = 0 (K-null cross covector)", snull)
        check(f"omega={wtag}: extra-block signature (2,1)", sig == (2, 1))

    # Rail 2: independent VbGeo recomputation at one frequency
    res = run_pipeline(VbGeo, INDEP_OMEGA, [sp.Rational(1, 4)], lean=True)
    a, K = prod._block(res)
    herm, detnz, anz, snull, sig = _invariants(a, K)
    check(f"VbGeo-independent omega={INDEP_OMEGA}: S=0, sig(2,1), a!=0",
          snull and sig == (2, 1) and anz and herm and detnz)
    # and it recovers the recorded a at that frequency (frame-consistent)
    if str(INDEP_OMEGA) in cert["a_records"]:
        arec = sp.Matrix([sp.sympify(x)
                          for x in cert["a_records"][str(INDEP_OMEGA)]])
        check("VbGeo a matches recorded a (same frame)",
              all(sp.cancel(a[j] - arec[j]) == 0 for j in range(3)))

    # E|X1 native form recovers the certified polar fixtures
    ex1 = sp.sympify(cert["EX1_native_frame_rational"])
    fix = json.loads((HERE / "certificates"
                      / "BH2B_COMPOSED_REPAIR.json").read_text())
    for tag in ("3/5", "2/7"):
        p, q = tag.split("/")
        wv = sp.Rational(int(p), int(q))
        check(f"E|X1 native form recovers fixture {tag}",
              sp.cancel(ex1.subs(w, wv)
                        - sp.sympify(fix["fixtures"][tag]["E|X1"])) == 0)

    # provenance hashes
    prov = cert["provenance"]
    check("normal-form hash matches",
          _sha256(HERE.parent / prov["normal_form_certificate"])
          == prov["normal_form_sha256"])
    check("polar fixture hash matches",
          _sha256(HERE.parent / prov["polar_fixture_certificate"])
          == prov["polar_fixture_sha256"])
    check("no real exceptional frequency recorded",
          cert["real_exceptional_frequencies"] == [])

    ok = all(c for _, c in checks)
    print(f"\n{'ALL CHECKS PASSED' if ok else 'VERIFICATION FAILED'} "
          f"({sum(c for _, c in checks)}/{len(checks)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
