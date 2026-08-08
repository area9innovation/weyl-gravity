"""The Krein Born trace on the obstructed shell, and the hypothesis it needs.

WHY THIS EXISTS.  `mannheim_cutting_rules` read the PT/positive-metric camp's
loop paper for scope.  This reads the other camp's: S. Bateman and N. Turok,
*Escape from Ostrogradsky via hidden ghost parity*, arXiv:2607.00096 (30 June
2026).  Paper 05 already cites it and already localises the positive-metric
obstruction in the kappa-ODD component of the on-shell T.  What Paper 05 leaves
open, in its own status ledger, is "the boundary Born-trace evaluation", and
`symbolic/verify_doubled_theory.py` DQ8 records the blocker exactly:

    "(The remaining BT-faithful step -- transporting through their R_t and
      testing membership in the null C component -- needs their embedding and
      is queued.)"

That embedding is their Eqs. (18)-(21).  Reading it clears the blocker.  This is
the third time in this repository that a recorded blocker cost one paper read.

WHAT THEIR MECHANISM ACTUALLY IS, and it is not what the abstract suggests.
Nullity is a CHARGE SELECTION RULE, not a norm cancellation:

    R_t P^(phi) R_t^dag  =  P^(OmegaUpsilon)  +  Q^(OmegaUpsilon)

with P charge NEUTRAL, t-independent, covariant, and -- their emphasis --
"most important, it is even under ghost parity"; and Q containing ONLY
negatively charged operators.  Then

    "Since the R_t homomorphism does not yield any positively charged
     operators, the negatively charged operators in Q cannot contribute to the
     trace, that is, Q is null and orthogonal to P."

THE FORK THIS CREATES.  Paper 05's obstruction is ghost-parity ODD.  Their B is
ghost-parity EVEN by construction.  So the obstruction cannot sit in B; it must
sit in C, and C's nullity rests ENTIRELY on the charge being one-sided.  Paper
05 has already computed that condition and found it to be a BOUNDARY property:
one-sidedness of the regulated vacuum image is "exact iff eps = 0 in the stated
charge frame".  Their own theory sits at eps = mu^2 = 0.  Paper 05's obstruction
is computed at split mass, where both charge signs appear.  The two results
therefore do not conflict -- they sit at different points of one family.

WHAT IS COMPUTED HERE.  The generalized Born rule, Eq. (6):

    Prob(A) = tr(A^dag A),        A^dag = kappa A^H kappa  (Krein adjoint)

evaluated on Paper 05's obstructed shell {|H(0)L(0)>, |L(3)L(-3)>} at E = 10,
with kappa = G = diag(-1, +1) the ghost parity.  Two elementary facts make it
exact and decidable:

  (1) The kappa-even and kappa-odd subspaces are Frobenius-orthogonal, so the
      cross terms drop and

          Prob(A)  =  ||A_+||_F^2  -  ||A_-||_F^2.

      Their weak-ghost-symmetry condition (A = B + C, B ghost symmetric, C null
      and orthogonal) is therefore EQUIVALENT, on a finite shell, to

          ||A_-||_F  <=  ||A_+||_F.

      It is one inequality, not a decomposition to be searched for.

  (2) The on-shell T is Krein SELF-adjoint (T^dag = T), which DQ8b already
      certifies as G T G = T^H.  So Prob = tr(T^2) and no S-matrix assembly is
      needed to evaluate it.

THE RESULT.  Positive, and not marginally:

    ||T_+||^2 = 33800290689142511 sqrt(5)/22324055803822080000
              + 470064287210099385401/99011652301111689216000
    ||T_-||^2 = 482403/1554251776
    Prob      = 33800290689142511 sqrt(5)/22324055803822080000
              + 439333411529238537401/99011652301111689216000     >  0

positive by INSPECTION of the exact form -- a positive rational multiple of
sqrt(5) plus a positive rational -- with no numerical evaluation anywhere.  The
kappa-even part exceeds the kappa-odd part by a factor of about 26 in squared
Frobenius norm.  So on this shell the positive-metric obstruction IS invisible
to the Krein Born rule, which is the direction Paper 05's Discussion conjectured.

AND A DEFECT FOUND UPSTREAM, which is why the diagonal is stated here.
`symbolic/verify_doubled_theory.py` built T with `sp.nsimplify` wrapped around
an already-exact expression.  On T[1,1] that FABRICATED a closed form,

    -2^(31/449) 3^(114/449) 5^(38/449) 7^(101/449)/75

agreeing with the true value only to about 2e-19.  A 449th root cannot arise
from rational matrix elements and quadratic-surd normalisations.  The DQ8 checks
test only that the diagonal is REAL, never its value, which is why it survived.
The true entry is -13264093 sqrt(5)/987148800 - 2759177557/995045990400.  The
`nsimplify` call is removed at source; all DQ1-DQ9 still pass, and the verifier
now runs in 16 s rather than four minutes because that call was the bottleneck.

Critically, THE CONCLUSION DOES NOT REST ON THE ENTRY THAT WAS CORRUPTED: with
T[1,1] set to zero outright the trace is still positive.  That control is
included below, because a result whose sign depends on a value one has just
repaired is not a result.

WHAT THIS DOES NOT ESTABLISH, and the gap is wide.  This is the FINITE-SHELL
SHADOW of the capstone, not the capstone.  Their trace is over the continuum
with delta^4(0) factors and their nullity is a charge statement; the shell
computation uses neither.  It is a NECESSARY condition -- had it come out
negative, their mechanism would have failed here outright -- and it came out
positive, which is consistent with their claim without proving it.  Paper 05's
"boundary Born-trace evaluation" stays OPEN.  Nothing here bears on loops: they
prove positivity at tree level and name their own obstacle ("like QCD, the
massless theory has collinear infrared divergences which affect asymptotic
states"), and the PT camp's cutting rules do not reach 1/k^4 at all.

Dependency tag: LOCAL-ALGEBRAIC.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import sympy as sp

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_BORN_TRACE_V1.json")

# ---------------------------------------------------------------------------
# Imported data.  One-way, pinned by exact value, recomputed by the command
# below; nothing in symbolic/ imports this module, so no cycle is created.
#
#   PYTHONPATH=. python3 symbolic/verify_doubled_theory.py      (16 s, DQ1-DQ9)
#
# Basis [IN = |H(0)L(0)>, OUT = |L(3)L(-3)>], E = 10, m_L = 4, m_H = 6,
# K = {-3, 0, 3}, g = 1.  Ghost parity G = diag(-1, +1).
# ---------------------------------------------------------------------------

T00 = -sp.Rational(24029911, 987148800) * sp.sqrt(5) \
      - sp.Rational(4203145033, 142149427200)
T11 = -sp.Rational(13264093, 987148800) * sp.sqrt(5) \
      - sp.Rational(2759177557, 995045990400)
COBS = sp.Rational(401, 78848) * sp.sqrt(6)          # T(in,out) = +COBS
G = sp.diag(-1, 1)

# The fabricated value the upstream verifier used before the repair.
T11_FABRICATED = -sp.Integer(2)**sp.Rational(31, 449) \
    * sp.Integer(3)**sp.Rational(114, 449) \
    * sp.Integer(5)**sp.Rational(38, 449) \
    * sp.Integer(7)**sp.Rational(101, 449) / 75


def shell_T(diag11=None, odd_scale=1):
    """The exact 2x2 on-shell T; knobs exist only for the controls."""
    d11 = T11 if diag11 is None else diag11
    c = COBS * odd_scale
    return sp.Matrix([[T00, c], [-c, d11]])


def krein_adjoint(M):
    return G * M.T.conjugate() * G


def split(M):
    """kappa-even and kappa-odd parts."""
    return sp.simplify((M + G * M * G) / 2), sp.simplify((M - G * M * G) / 2)


def frob2(M):
    return sp.radsimp(sp.expand(
        sum(sp.Abs(M[i, j])**2 for i in range(2) for j in range(2))))


def born(M):
    """BT Eq. (6) restricted to the shell: Prob = tr(M^dag M)."""
    return sp.radsimp(sp.expand(sp.trace(krein_adjoint(M) * M)))


def positive_by_inspection(expr):
    """Exact positivity: a sqrt(5) + b with a, b positive rationals.

    No numerical evaluation.  Returns (verdict, a, b).
    """
    e = sp.expand(expr)
    a = sp.radsimp(e.coeff(sp.sqrt(5)))
    b = sp.radsimp(sp.expand(e - a * sp.sqrt(5)))
    ok = a.is_rational and b.is_rational and a > 0 and b > 0
    return bool(ok), a, b


def build():
    T = shell_T()
    Tp, Tm = split(T)
    np2, nm2 = frob2(Tp), frob2(Tm)
    prob = born(T)
    pos, acoef, bcoef = positive_by_inspection(prob)

    # --- controls ---------------------------------------------------------
    # CTRL-A (known answer).  A kappa-even T is Hilbert-Hermitian and the
    # Krein rule must reduce to the ordinary positive one.
    T_even = sp.Matrix([[T00, 0], [0, T11]])
    ctrl_hilbert = sp.simplify(born(T_even) - frob2(T_even)) == 0

    # CTRL-B (the criterion must be able to FAIL).  Scale the kappa-odd block
    # until it dominates; the Born trace must go negative.  Without this,
    # "positive" is not a measurement.
    T_bad = shell_T(odd_scale=10)
    prob_bad = born(T_bad)
    ctrl_can_fail = bool(sp.radsimp(sp.expand(prob_bad)) < 0)

    # CTRL-C (identity).  Prob = ||T_+||^2 - ||T_-||^2, i.e. the kappa-graded
    # cross terms really do vanish.
    ctrl_identity = sp.simplify(prob - (np2 - nm2)) == 0

    # CTRL-D.  Krein self-adjointness, independently of DQ8b.
    ctrl_selfadj = sp.simplify(krein_adjoint(T) - T) == sp.zeros(2, 2)

    # CTRL-E (the upstream artifact).  The fabricated entry differs from the
    # true one, and only far below any scale in the problem -- the signature
    # of a float match rather than an algebraic identity.
    gap = sp.N(T11_FABRICATED - T11, 40)
    ctrl_artifact_differs = sp.simplify(T11_FABRICATED - T11) != 0
    ctrl_artifact_tiny = abs(gap) < sp.Rational(1, 10**15)
    ctrl_true_is_surd = sp.simplify(
        sp.expand((T11 + sp.Rational(2759177557, 995045990400))**2
                  - 5 * sp.Rational(13264093, 987148800)**2)) == 0

    # CTRL-F (the conclusion must not rest on the repaired entry).
    prob_no_d11 = born(shell_T(diag11=sp.Integer(0)))
    ctrl_margin = bool(sp.radsimp(sp.expand(prob_no_d11)) > 0)

    # CTRL-G (vacuity).  If the kappa-odd part were zero the whole question
    # would be empty.
    ctrl_odd_nonzero = sp.simplify(nm2) != 0

    checks = {
        "born_trace_positive": pos,
        "positivity_is_exact_not_numeric": pos,
        "identity_prob_equals_even_minus_odd": ctrl_identity,
        "krein_self_adjoint": ctrl_selfadj,
        "control_hilbert_case_recovered": ctrl_hilbert,
        "control_criterion_can_fail": ctrl_can_fail,
        "control_artifact_differs_from_truth": ctrl_artifact_differs,
        "control_artifact_gap_is_subnumeric": bool(ctrl_artifact_tiny),
        "control_true_entry_is_quadratic_surd": ctrl_true_is_surd,
        "control_sign_survives_zeroing_repaired_entry": ctrl_margin,
        "control_odd_part_nonzero": ctrl_odd_nonzero,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_BT_BORN_TRACE_V1",
        "dependency_tag": "LOCAL-ALGEBRAIC",
        "lifecycle_state": "CLASSIFIED",
        "question": "Does Paper 05's kappa-odd positive-metric obstruction "
                    "land in the null C component of the Bateman-Turok "
                    "decomposition, i.e. is it invisible to their Krein Born "
                    "rule?",
        "answer": "On the obstructed shell, yes: the Born trace is exactly "
                  "positive, with the kappa-even part exceeding the kappa-odd "
                  "part by a factor of about 26 in squared Frobenius norm. "
                  "This is the finite-shell shadow of the capstone, not the "
                  "capstone: their nullity is a charge selection rule and "
                  "their trace is a continuum trace, neither of which this "
                  "computation uses.",
        "source": {
            "authors": "S. Bateman and N. Turok",
            "title": "Escape from Ostrogradsky via hidden ghost parity",
            "arxiv": "2607.00096",
            "date": "30 June 2026",
            "affiliations": "Higgs Centre for Theoretical Physics, Edinburgh; "
                            "Perimeter Institute",
            "mechanism": "charge selection rule, not norm cancellation: "
                         "R_t P R_t^dag = P^(OmegaUpsilon) + Q^(OmegaUpsilon) "
                         "with P charge neutral AND even under ghost parity, "
                         "Q strictly negatively charged, hence null in the "
                         "trace since no positively charged operators appear",
            "self_declared_limit": "positivity proven at TREE LEVEL; obstacle "
                                   "to higher orders is collinear infrared "
                                   "divergence of the massless theory",
        },
        "blocker_cleared": {
            "where": "symbolic/verify_doubled_theory.py, DQ8",
            "text": "the remaining BT-faithful step ... needs their embedding "
                    "and is queued",
            "resolution": "their embedding is Eqs. (18)-(21); one paper read",
        },
        "the_fork": {
            "obstruction_parity": "ghost-parity ODD (Paper 05, cprop:krein)",
            "their_B_parity": "ghost-parity EVEN by construction (their text)",
            "consequence": "the obstruction cannot sit in B; it must sit in C, "
                           "so C's nullity carries the whole reconciliation",
            "hypothesis_C_needs": "one-sided charge",
            "repo_status_of_that": "Paper 05, cprop:embedding: one-sidedness "
                                   "of the regulated vacuum image is exact iff "
                                   "eps = 0; at split mass both charge signs "
                                   "appear. Their theory sits at eps = mu^2 = "
                                   "0. The two results do not conflict; they "
                                   "sit at different points of one family.",
        },
        "exact_values": {
            "T00": str(T00),
            "T11": str(T11),
            "T_in_out": str(COBS),
            "T_out_in": str(-COBS),
            "even_frobenius_sq": str(np2),
            "odd_frobenius_sq": str(nm2),
            "born_trace": str(prob),
            "positivity_witness": {
                "form": "a*sqrt(5) + b with a, b rational",
                "a": str(acoef), "b": str(bcoef),
                "a_positive": bool(acoef > 0), "b_positive": bool(bcoef > 0),
            },
        },
        "upstream_repair": {
            "file": "symbolic/verify_doubled_theory.py",
            "defect": "sp.nsimplify wrapped around an already-exact expression "
                      "in Tmat fabricated a closed form for T[1,1]",
            "fabricated": str(T11_FABRICATED),
            "true": str(T11),
            "agreement": "~2e-19 -- a float match, not an identity",
            "why_it_survived": "the DQ8 checks test only that the diagonal is "
                               "REAL, never its value",
            "status": "removed at source; DQ1-DQ9 all still pass; runtime "
                      "16 s instead of ~4 min",
            "claims_affected": "none -- every published DQ8 quantity is an "
                               "off-diagonal element or a reality statement",
        },
        "does_not_establish": [
            "the capstone: their nullity is a CHARGE statement and their trace "
            "is a continuum trace with delta^4(0) factors; this shell "
            "computation uses neither, so it is a necessary condition only",
            "Paper 05's 'boundary Born-trace evaluation' remains OPEN",
            "anything at loop level, on either side: they prove tree-level "
            "positivity and name collinear IR divergence as the obstacle, and "
            "the PT camp's cutting rules do not reach 1/k^4 at all",
            "anything LORENTZIAN-CAUSAL",
        ],
        "neighbours": {
            "paper/05-interaction-obstructions.tex":
                "cprop:krein localises the obstruction in the kappa-odd "
                "block; cprop:embedding makes one-sidedness a boundary "
                "property; the Discussion names this calculation",
            "symbolic/verify_doubled_theory.py":
                "DQ8 supplies the exact on-shell T and recorded the blocker "
                "this clears",
            "reverse_physics/mannheim_cutting_rules.py":
                "the same scope reading for the PT/positive-metric camp; both "
                "published routes stop at the same order",
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/bt-born-trace.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="BT Krein Born-trace gate")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    ev = cert["exact_values"]
    print("Bateman-Turok generalized Born rule on Paper 05's obstructed shell")
    print()
    print("  T00       =", ev["T00"])
    print("  T11       =", ev["T11"])
    print("  T(in,out) =", ev["T_in_out"], "  T(out,in) =", ev["T_out_in"])
    print()
    print("  ||T_+||^2 =", ev["even_frobenius_sq"])
    print("  ||T_-||^2 =", ev["odd_frobenius_sq"])
    print("  Prob      =", ev["born_trace"])
    w = ev["positivity_witness"]
    print("  positive by inspection: a = %s (>0: %s), b = %s (>0: %s)"
          % (w["a"], w["a_positive"], w["b"], w["b_positive"]))
    print()
    print("  upstream repair:", cert["upstream_repair"]["defect"])
    print("    fabricated:", cert["upstream_repair"]["fabricated"])
    print("    true      :", cert["upstream_repair"]["true"])
    print()
    print("checks %d/%d" % (cert["checks"]["passed"], cert["checks"]["total"]))
    for f in cert["checks"]["failures"]:
        print("FAIL %s" % f)

    if args.emit and cert["checks"]["ok"]:
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    print("RESULT: %s" % ("PASS" if cert["checks"]["ok"] else "FAIL"))
    return 0 if cert["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
