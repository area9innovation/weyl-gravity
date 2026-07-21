"""BH-2 polar cross-covector universal-quantifier repair (fail-closed).

Certificate `black_hole_programme/certificates/BH2_POLAR_QUANTIFIER_REPAIR.json`.
Verdict token `BH2_POLAR_CROSS_COVECTOR_NINE_FIXTURE_THEOREM_UNIVERSAL_SHORTFALL`.
Dependency tags LOCAL-ALGEBRAIC + REDUCED-MODE.  Lifecycle CLASSIFIED.

WHAT THIS REPAIRS
-----------------
BH2_POLAR_CROSS_COVECTOR reported, from nine exact rational frequencies, that
the polar l=2 extra-block Gram K_phys=iK is Hermitian of inertia (2,1),
nondegenerate, and that the nonzero cross covector a is K-null
(S = a K^{-1} a^H = 0), concluding "there is NO real exceptional frequency".
The last clause is a UNIVERSAL statement over real omega!=0 inferred from a
finite sample; its `no_real_exceptional_frequency_certified` flag is an
unsupported quantifier.  This module decides the quantifier by the one route
that closes with the available machinery, and fail-closes the rest.

WHAT IS PRESERVED (the valid fixture theorem, re-derived independently here)
---------------------------------------------------------------------------
Imported by exact content hash from BH2_POLAR_CROSS_COVECTOR: at each of the
nine recorded rational omega, from the EXACT (a, K),
  * K_phys = i K is Hermitian, det K != 0, inertia (2,1) -- re-derived by the
    Jacobi leading-principal-minor sign rule (independent of the producer's
    eigenvalue computation);
  * a != 0 and a K^{-1} a^H = 0 -- S re-derived by solving K x = a^H and
    forming a . x (independent of the producer's explicit inverse).

WHAT IS UPGRADED TO A GENUINE ALL-REAL-FREQUENCY THEOREM (route A, partial)
--------------------------------------------------------------------------
a(omega) != 0 for ALL real omega != 0.  The single component that IS rational
in the tower's native frame,
    E|X1 = 48(64w^3 - 200 i w^2 - 240 w + 49 i) / (35(4w + i)),
has numerator P(w) + i Q(w) with P = 64w^3 - 240w and Q = 49 - 200w^2 two REAL
polynomials whose resultant is nonzero (= 98626146304), so P and Q share no
common (real) root; the denominator 4w+i has no real zero.  Hence E|X1 != 0 at
every real omega, so the covector a is nonzero there (a=0 is basis-invariant;
one nonzero component in any frame forces a!=0).  This uses one rational
component only as a NON-VANISHING witness, never as a degree bound for the
covector or the Gram.

WHY THE UNIVERSAL SIGNATURE / NO-EXCEPTIONAL-FREQUENCY STATEMENT DOES NOT CLOSE
------------------------------------------------------------------------------
Only frame-INVARIANT scalars may be reconstructed across the nine independently
normalized samples.  Under a change of additional-mode basis X -> X B(omega)
(B in GL(3,C)) one has a -> a B*, K -> B^T K B*, so
  * S = a K^{-1} a^H is INVARIANT (reconstructible; it is 0 at all nine), and
  * a = 0 is invariant, but
  * det K and the char-poly coefficients t1,t2,t3 of K_phys are frame-COVARIANT
    (det K -> |det B|^2 det K; the t_i change under congruence), so they are a
    single rational function of omega only if B(omega) is.
The sampler builds X0,X1,X2 from an independent numeric nullspace at each omega,
which is NOT a canonical rational frame: E|X0 and E|X2 are non-rational in it
(no rational fit up to degree (6,6) over 24 exact points -- recorded in the
polar report), and here t1,t2,t3 admit NO rational fit up to total degree 8
(seven-point fit, two disjoint held-out points).  Therefore det K(omega) and the
inertia are NOT reconstructible from this data, the real zeros of det K cannot be
isolated, and "no real exceptional frequency" is NOT established for generic omega.

FAIL-CLOSED DISPOSITION
-----------------------
generic_real_frequency and no_real_exceptional_frequency are set FALSE.  The
result is an exact NINE-FIXTURE classification with a UNIVERSAL SHORTFALL; the
null-cone structure at nine exact frequencies is retained in full.

MINIMAL MISSING OBJECT (either closes the universal statement)
--------------------------------------------------------------
(A) a canonical rational/meromorphic omega-frame for the three additional lifts
    X0,X1,X2 -- equivalently a rational nullspace normalization of the
    compose/einstein_mode step of bh2b_polar_cross_flux -- in which a(omega) and
    K(omega) are exact rational matrices; then det K factors, its real zeros are
    Sturm-isolable, and inertia is constant on each sign of omega between them.
    (Direct symbolic construction is presently intractable: NORD=16 Frobenius
    recursion with a per-order nullspace at symbolic omega does not terminate in
    a usable time.)
(B) a first-principles current / exact-sequence identity: S=0 is equivalent to
    the full 4x4 Gram G=[[E|E,a],[a^H,K]] (with E|E=0) being degenerate, i.e. the
    modified Einstein direction Z = E - (K^{-1} a^H).X lying in the radical of
    F^r on span(E,X0,X1,X2).  Proving Z is symplectically null / pure gauge for
    all real omega!=0 (with a separate nondegeneracy/inertia-constancy argument)
    closes the quantifier structurally.  This is the natural even-parity twin of
    the axial RW-null theorem and is flagged as the successor route.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_PATH = HERE / "schema" / "bh2-polar-quantifier-repair-v1.schema.json"
OUTPUT = HERE / "certificates" / "BH2_POLAR_QUANTIFIER_REPAIR.json"
POLAR_COVECTOR = HERE / "certificates" / "BH2_POLAR_CROSS_COVECTOR.json"
POLAR_FIXTURE = HERE / "certificates" / "BH2B_COMPOSED_REPAIR.json"

SCHEMA_NAME = "pure-weyl-bh2-polar-quantifier-repair-v1"
RESULT_ID = "PURE_WEYL_BH2_POLAR_QUANTIFIER_REPAIR"
RESULT_TOKEN = "BH2_POLAR_CROSS_COVECTOR_NINE_FIXTURE_THEOREM_UNIVERSAL_SHORTFALL"

w = sp.Symbol("omega")

# E|X1 exact native-frame rational form (from BH2_POLAR_CROSS_COVECTOR)
EX1_NATIVE = ("48*(64*omega**3 - 200*I*omega**2 - 240*omega + 49*I)"
              " / (35*(4*omega + I))")


class QuantifierRepairError(RuntimeError):
    pass


def _require(cond, msg):
    if not cond:
        raise QuantifierRepairError(msg)


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
#  fixture theorem, re-derived independently from imported exact (a, K)        #
# --------------------------------------------------------------------------- #
def _load_ak(cert):
    out = {}
    for wtag in cert["K_records"]:
        a = sp.Matrix([sp.sympify(x) for x in cert["a_records"][wtag]])
        K = sp.Matrix([[sp.sympify(x) for x in row]
                       for row in cert["K_records"][wtag]])
        out[wtag] = (a, K)
    return out


def _inertia_by_minors(Kp):
    """Inertia of a 3x3 Hermitian Kp by the Jacobi leading-principal-minor sign
    rule (independent of eigenvalue extraction).  Returns (n_pos, n_neg) or
    None if a leading minor vanishes (rule inconclusive).  For a Hermitian Kp
    the leading principal minors are real; here the entries are exact complex
    rationals, so each minor reduces to an exact rational."""
    minors = [sp.Integer(1),
              sp.cancel(Kp[0, 0]),
              sp.cancel(Kp[:2, :2].det()),
              sp.cancel(Kp.det())]
    reals = [sp.re(sp.expand(m)) for m in minors]
    if any(r == 0 for r in reals[1:]):
        return None
    signs = [1 if r > 0 else -1 for r in reals]
    neg = sum(1 for k in range(1, 4) if signs[k - 1] * signs[k] < 0)
    return (3 - neg, neg)


def _S_by_solve(a, K):
    """S = a K^{-1} a^H via solving K x = a^H (independent of explicit inverse)."""
    x = K.solve(a.conjugate())
    return sp.cancel((a.T * x)[0, 0])


def verify_fixture_theorem(cert):
    samples = _load_ak(cert)
    per = {}
    for wtag, (a, K) in samples.items():
        Kp = sp.I * K
        herm = sp.simplify(Kp - Kp.conjugate().T) == sp.zeros(3, 3)
        _require(herm, f"K_phys not Hermitian at {wtag}")
        d = sp.cancel(K.det())
        _require(d != 0, f"K degenerate at {wtag}")
        inertia = _inertia_by_minors(Kp)
        _require(inertia == (2, 1),
                 f"inertia (Jacobi minors) != (2,1) at {wtag}: {inertia}")
        anz = any(sp.cancel(x) != 0 for x in a)
        _require(anz, f"covector zero at {wtag}")
        S = _S_by_solve(a, K)
        _require(S == 0, f"S (solve rail) != 0 at {wtag}: {S}")
        per[wtag] = {"inertia": list(inertia), "S": "0", "a_nonzero": True,
                     "detK_nonzero": True}
    return per


# --------------------------------------------------------------------------- #
#  universal upgrade: a != 0 for all real omega != 0                           #
# --------------------------------------------------------------------------- #
def prove_covector_nonzero():
    ex1 = sp.sympify(EX1_NATIVE)
    num, den = sp.fraction(sp.together(ex1))
    # split numerator into real/imag polynomial parts (real omega)
    P = sp.expand(64 * w**3 - 240 * w)          # Re(numerator)/48*35-normalized
    Q = sp.expand(-200 * w**2 + 49)             # Im(numerator)
    # sanity: numerator == 48*(P + I*Q)
    _require(sp.expand(num - 48 * (P + sp.I * Q)) == 0,
             "E|X1 numerator real/imag split mismatch")
    resPQ = sp.resultant(P, Q, w)
    _require(resPQ != 0, "resultant(P,Q)=0: a real common root is possible")
    # denominator has no real zero
    den_real_zeros = [r for r in sp.solve(sp.Eq(den, 0), w) if sp.im(r) == 0]
    _require(den_real_zeros == [], f"E|X1 denominator has real zero {den_real_zeros}")
    # off-sample non-vanishing witnesses (frequencies not among the nine)
    off = [sp.Rational(7, 3), sp.Rational(9, 2), -sp.Rational(1, 2),
           -sp.Rational(3, 5)]
    witnesses = {}
    for wv in off:
        val = sp.cancel(ex1.subs(w, wv))
        _require(val != 0, f"E|X1 unexpectedly zero at off-sample {wv}")
        witnesses[sp.sstr(wv)] = sp.sstr(val)
    return {
        "statement": "a(omega) != 0 for all real omega != 0",
        "method": "E|X1 = 48(P + iQ)/(35(4w+i)); P,Q real polynomials with "
                  "nonzero resultant (no common real root); denominator has no "
                  "real zero; one nonzero component forces the covector nonzero "
                  "(a=0 is basis-invariant)",
        "P": sp.sstr(P),
        "Q": sp.sstr(Q),
        "resultant_P_Q": sp.sstr(resPQ),
        "denominator_real_zeros": [],
        "off_sample_witnesses": witnesses,
        "proven": True,
    }


# --------------------------------------------------------------------------- #
#  obstruction: the sampler frame is not a single rational function of omega   #
# --------------------------------------------------------------------------- #
def _chi(K):
    # char-poly coefficients of the Hermitian Kp = iK are real; the entries are
    # exact complex rationals, so each reduces to an exact rational via re().
    Kp = sp.I * K
    t1 = Kp.trace()
    t2 = (Kp[0, 0] * Kp[1, 1] - Kp[0, 1] * Kp[1, 0]
          + Kp[0, 0] * Kp[2, 2] - Kp[0, 2] * Kp[2, 0]
          + Kp[1, 1] * Kp[2, 2] - Kp[1, 2] * Kp[2, 1])
    t3 = Kp.det()
    return (sp.re(sp.expand(t1)), sp.re(sp.expand(t2)), sp.re(sp.expand(t3)))


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
    free = [v for v in list(pj) + list(qj) if v not in s]
    if free:
        return None
    numv = sum(s.get(pj[k], pj[k]) * w**k for k in range(m + 1))
    denv = 1 + sum(s.get(qj[k], qj[k]) * w**(k + 1) for k in range(n))
    return sp.cancel(numv / denv)


def obstruction_no_rational_frame(cert, max_total=8):
    samples = _load_ak(cert)
    wpts = []
    for wtag, (a, K) in samples.items():
        p, q = wtag.split("/")
        wpts.append((sp.Rational(int(p), int(q)), K))
    tdata = {"t1": [], "t2": [], "t3": []}
    for wv, K in wpts:
        t1, t2, t3 = _chi(K)
        tdata["t1"].append((wv, t1))
        tdata["t2"].append((wv, t2))
        tdata["t3"].append((wv, t3))
    results = {}
    for name, data in tdata.items():
        found = None
        fit_pts, hold_pts = data[:7], data[7:]
        for total in range(1, max_total + 1):
            for mm in range(total + 1):
                nn = total - mm
                fit = _rational_fit(fit_pts, mm, nn)
                if fit is None:
                    continue
                if all(sp.cancel(fit.subs(w, wv) - val) == 0
                       for wv, val in hold_pts):
                    found = (mm, nn)
                    break
            if found:
                break
        results[name] = ("rational fit deg %s" % (found,) if found
                         else "NO rational fit up to total degree %d "
                              "(7-point fit + 2 held-out)" % max_total)
    all_fail = all("NO rational fit" in v for v in results.values())
    return {
        "invariant_candidates": "char-poly coefficients t1,t2,t3 of K_phys=iK "
                                "(would be rational if the sampler frame were a "
                                "single rational function of omega)",
        "held_out_reconstruction": results,
        "sampler_frame_is_rational": (not all_fail),
        "corroborating_report_fact": "E|X0, E|X2 non-rational in the native "
                                     "frame: no rational fit up to degree (6,6) "
                                     "over 24 exact points (polar report)",
        "consequence": "det K(omega) and the inertia are NOT reconstructible "
                       "from these independently normalized samples; real zeros "
                       "of det K cannot be isolated; the universal "
                       "no-real-exceptional-frequency statement is not established",
    }


def non_null_mutation(cert):
    samples = _load_ak(cert)
    wtag = next(iter(samples))
    a, K = samples[wtag]
    a_mut = a + sp.Matrix([1, 0, 0])
    S_mut = _S_by_solve(a_mut, K)
    return {"frequency": wtag, "rejected": bool(S_mut != 0),
            "S_mut_nonzero": sp.sstr(S_mut) != "0"}


def build_certificate():
    _require(POLAR_COVECTOR.exists(), "polar covector certificate missing")
    cert_in = json.loads(POLAR_COVECTOR.read_text())
    polar_hash = _sha256(POLAR_COVECTOR)
    fixture_hash = _sha256(POLAR_FIXTURE)

    fixture_theorem = verify_fixture_theorem(cert_in)
    nonzero = prove_covector_nonzero()
    obstruction = obstruction_no_rational_frame(cert_in)
    mutation = non_null_mutation(cert_in)
    _require(mutation["rejected"], "non-null mutation not rejected")
    _require(not obstruction["sampler_frame_is_rational"],
             "unexpected: sampler frame reconstructed rationally -- rerun "
             "route A reconstruction of det K and isolate real zeros")

    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH) if SCHEMA_PATH.exists() else None,
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "disposition": "NINE_FIXTURE_THEOREM + UNIVERSAL_SHORTFALL",
        "parity": "polar l=2",
        "setting": "Schwarzschild m=1, real frequency omega != 0, "
                   "Eddington-Finkelstein carrier, t-chart Lee-Wald F^r",
        "repairs": {
            "target_certificate": str(POLAR_COVECTOR.relative_to(ROOT)),
            "target_sha256": polar_hash,
            "unsupported_quantifier": "no_real_exceptional_frequency_certified "
                                      "(universal over real omega != 0 from a "
                                      "nine-point sample)",
        },
        "provenance": {
            "polar_covector_certificate": str(POLAR_COVECTOR.relative_to(ROOT)),
            "polar_covector_sha256": polar_hash,
            "polar_fixture_certificate": str(POLAR_FIXTURE.relative_to(ROOT)),
            "polar_fixture_sha256": fixture_hash,
            "imported_records": "nine exact (a,K) at omega in "
                                "{1/2,1/3,1/4,2/3,2/7,3/4,3/5,4/5,5/7}",
        },
        "preserved_fixture_theorem": {
            "statement": "at each of the nine recorded omega: K_phys=iK "
                         "Hermitian, det K != 0, inertia (2,1), a != 0, "
                         "a K^{-1} a^H = 0",
            "independent_rails": "inertia by Jacobi leading-principal-minor "
                                 "signs; S by solving K x = a^H",
            "per_frequency": fixture_theorem,
            "over_determination_points": len(fixture_theorem),
        },
        "universal_results": {
            "covector_nonzero_all_real_omega": nonzero,
        },
        "obstruction_to_universal_signature": obstruction,
        "non_null_mutation": mutation,
        "claim_flags": {
            "covector_nonzero_all_real_omega_certified": True,
            "K_null_nine_fixture_certified": True,
            "signature_2_1_nine_fixture_certified": True,
            "generic_real_frequency_certified": False,
            "no_real_exceptional_frequency_certified": False,
        },
        "missing_object": {
            "route_A_canonical_frame": "a canonical rational/meromorphic "
                "omega-frame for X0,X1,X2 (rational nullspace normalization of "
                "the compose/einstein_mode step); direct symbolic construction "
                "intractable at NORD=16",
            "route_B_structural_identity": "prove Z = E - (K^{-1} a^H).X is "
                "symplectically null / pure gauge for all real omega != 0 "
                "(radical of F^r on span(E,X0,X1,X2)); the even-parity twin of "
                "the axial RW-null theorem",
        },
        "not_claimed": {
            "universal_signature_or_exceptional_frequency":
                "generic-omega inertia constancy and absence of real "
                "exceptional frequencies are NOT established (fail closed)",
            "universal_K_null":
                "S = 0 is an exact frame-invariant fact at nine frequencies; a "
                "closed-form all-omega proof is left to route A or B",
            "general_l": False,
            "omega_zero": "excluded (certified exceptional carrier)",
            "complex_omega_continuation": False,
            "finite_flux_scattering_qnm_ringdown_stability_positivity_particle":
                "none asserted",
        },
    }
    return cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUTPUT))
    args = ap.parse_args()
    cert = build_certificate()
    Path(args.out).write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    print("  disposition:", cert["disposition"])
    print("  a != 0 for all real omega != 0:",
          cert["universal_results"]["covector_nonzero_all_real_omega"]["proven"])
    print("  sampler frame rational (route A reconstructible):",
          cert["obstruction_to_universal_signature"]["sampler_frame_is_rational"])


if __name__ == "__main__":
    main()
