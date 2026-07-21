"""Independent verifier for BH2_SYMBOLIC_CROSS_INVARIANT.

Structurally-independent rail: the producer computes the horizon cross constants
on the `weyl_geometry.Geometry` + `linearized_bach` curvature engine; this
verifier recomputes them on the VbGeo Schouten/Kulkarni-Nomizu engine (the same
one used by verify_bh2b_composed_repair), and checks that the certificate's
CLOSED FORM a(omega) predicts every independently recomputed value.  It also
re-derives the pole/zero classification, the conjugate-frequency law, the
recovery of the two certified fixtures, and the provenance hashes -- all from
the certificate string, not from the producer's Python objects.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

from verify_bh2a_axial_operator import VbGeo
from bh2_cross_invariant_axial_modes import cross_ee_axial

HERE = Path(__file__).resolve().parent
CERT = HERE / "certificates" / "BH2_SYMBOLIC_CROSS_INVARIANT.json"
w = sp.Symbol("omega")

# independent recomputation frequencies (kept small; VbGeo rail is exact)
INDEP_OMEGAS = [sp.Rational(3, 5), sp.Rational(2, 7), sp.Rational(5, 3)]


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    cert = json.loads(CERT.read_text())
    cross = sp.sympify(cert["cross_of_omega"])
    a_of_w = sp.sympify(cert["a_of_omega"])
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    # 1. a = i*cross
    check("a(omega) == i*cross(omega)",
          sp.cancel(a_of_w - sp.I * cross) == 0)

    # 2. INDEPENDENT curvature rail: recompute cross on VbGeo, predict via form
    nord = cert["provenance"]["series_order_NORD"]
    kwin = cert["provenance"]["flux_window_KWIN"]
    for wv in INDEP_OMEGAS:
        cv, _ee = cross_ee_axial(wv, VbGeo, NORD=nord, KWIN=kwin)
        check(f"VbGeo-independent cross({wv}) matches closed form",
              sp.cancel(cross.subs(w, wv) - cv) == 0)

    # 3. classification: no real zero (except origin) and no real pole
    num = sp.Poly(sp.numer(sp.cancel(cross)), w)
    den = sp.Poly(sp.denom(sp.cancel(cross)), w)
    zeros = sp.roots(num)
    poles = sp.roots(den)
    check("no nonzero real zero of a(omega)",
          not [z for z in zeros if sp.im(z) == 0 and sp.re(z) != 0])
    check("no real pole of a(omega) (no real exceptional frequency)",
          not [p for p in poles if sp.im(p) == 0])
    check("omega=0 is a simple zero (excluded exceptional carrier)",
          zeros.get(sp.Integer(0)) == 1)

    # 4. conjugate-frequency law on a set of reals
    check("cross(-omega)=conj(cross(omega)) and a(-omega)=-conj(a(omega))",
          all(sp.cancel(cross.subs(w, -wv) - sp.conjugate(cross.subs(w, wv))) == 0
              and sp.cancel(a_of_w.subs(w, -wv)
                            + sp.conjugate(a_of_w.subs(w, wv))) == 0
              for wv in (sp.Rational(1, 2), sp.Rational(3, 5),
                         sp.Rational(2, 7), sp.Rational(5, 3))))

    # 5. certified fixtures recovered
    fix = json.loads((HERE / "certificates"
                      / "BH2A_COMPOSED_REPAIR.json").read_text())
    for tag in ("3/5", "2/7"):
        p, q = tag.split("/")
        wv = sp.Rational(int(p), int(q))
        cv = sp.sympify(fix["fixtures"][tag]["cross"])
        check(f"certified fixture {tag} recovered by closed form",
              sp.cancel(cross.subs(w, wv) - cv) == 0)

    # 6. provenance hashes
    prov = cert["provenance"]
    check("normal-form certificate hash matches",
          _sha256(HERE.parent / prov["normal_form_certificate"])
          == prov["normal_form_sha256"])
    check("axial fixture certificate hash matches",
          _sha256(HERE.parent / prov["axial_fixture_certificate"])
          == prov["axial_fixture_sha256"])

    # 7. mutations flagged rejected
    check("all representative mutations recorded rejected",
          all(cert["mutations_rejected"].values()))

    ok = all(c for _, c in checks)
    print(f"\n{'ALL CHECKS PASSED' if ok else 'VERIFICATION FAILED'} "
          f"({sum(c for _, c in checks)}/{len(checks)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
