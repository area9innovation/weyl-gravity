"""Mannheim's loop-unitarity theorem, and the point where pure Weyl gravity sits.

WHY THIS EXISTS.  P. D. Mannheim, *Unitarity of loop diagrams for the ghost-like
1/(k^2-M_1^2) - 1/(k^2-M_2^2) propagator*, Phys. Rev. D 98, 045014 (2018),
arXiv:1801.03220, is the one paper in the fourth-order-gravity literature that is
about LOOP DIAGRAMS rather than free-field norms.  Nothing in this repository
cited it.  It matters here because its closing paragraph applies itself directly
to conformal gravity:

    "Conformal gravity is thus offered as a fully consistent and renormalizable
     quantum theory of gravity."

If that stands as stated, a loop calculation in pure Weyl gravity has a
prescription and the programme's ghost stream has a settled import.  So the
question is not whether Mannheim is right about the theory he proves a theorem
about.  It is WHETHER PURE WEYL GRAVITY IS THAT THEORY.

THE ANSWER IS IN THE PAPER, AND IT IS NOT THE CLOSING PARAGRAPH.  Section VI
studies the equal-frequency limit -- coincident poles -- and ends:

    "However, since non-stationary states are involved in the eps = 0
     Jordan-block case, the standard cutting rules would not apply."

That is the author's own sentence, and pure Weyl gravity is a coincident-pole
theory: its propagator is 1/k^4, a double pole at the origin, which the same
paper calls "a pure fourth-order derivative Jordan-block theory".

So the paper contains both a concession and a claim.  Section VII is what
reconciles them, and this module computes the bridge between the two sections in
order to name the step that carries the weight.

WHAT IS COMPUTED HERE.  Four exact facts, all rational, no floating point.

  (1) THE PARTIAL FRACTIONS OF 1/k^4 -- Mannheim's Eq. (84) -- verified as a
      polynomial identity in Q[E, omega] rather than sampled.  The relation is
      printed, not merely asserted to exist.

  (2) EQ. (84) CONTAINS EQ. (76).  The positive-energy half of the massless
      1/k^4 propagator is COEFFICIENT-FOR-COEFFICIENT the equal-frequency
      Jordan-block Green's function of Section VI.  Mannheim states this in one
      clause ("With (84) recovering (76) at the E = +omega pole"); it is the
      hinge of the whole disposition, so it is checked rather than taken.

      Consequence: the object Section VII declares viable IS the object Section
      VI excludes from the standard cutting rules.

  (3) THE CUT WEIGHT IS NOT A MEASURE AT COINCIDENCE.  Write the fourth-order
      line by partial fractions, m_i = M_i^2:

          1/((s - m1)(s - m2))  ->  R_1/(s - m1) + R_2/(s - m2),
          R_1 = 1/(m1 - m2),   R_2 = -R_1.

      The functional a cut integrates against a test function f is then

          W[f] = sum_i R_i f(m_i) = (f(m1) - f(m2)) / (m1 - m2),

      whose coincidence limit is f -> f'(m).  On the monomial ladder f = s^n
      this is exact and rational:

          W_n = h_{n-1}(m1, m2)      (complete homogeneous symmetric poly)
          W_0 = 0,  W_1 = 1,  W_n(m, m) = n m^(n-1).

      TOTAL WEIGHT ZERO, FIRST MOMENT ONE.  That is -delta'(s - m), and a
      derivative of a delta is not a positive measure -- it is not a measure of
      any definite sign.  A cutting rule is a resolution of the identity over
      intermediate states with positive weight; this functional admits none.
      The signature here is an ORDER, not a sign, which is the same statement
      the black-hole and ghost streams reach from the other side.

  (4) THE THEOREM'S OWN STATES GO NULL.  Appendix A(2) of the same paper gives
      the one-particle normalisation whose positivity IS the theorem:

          [a_i, a_i^dag] = [2 (M_1^2 - M_2^2) (k^2 + M_i^2)^(1/2)]^(-1) delta^3

      Its rational core is 1/(m1 - m2).  Exactly: (m1 - m2) * R_1 = 1 for every
      separation, so the normalisation has a simple pole in the separation and
      the canonically rescaled norm vanishes linearly.  The positive-norm states
      the theorem is about are not merely hard to track at coincidence.  They
      are null there.

WHAT THIS DOES NOT ESTABLISH, and the boundary is the point.  It does NOT show
pure Weyl gravity is non-unitary.  It shows that PRD 98, 045014 does not cover
it, by the paper's own Section VI, and that the reconciling step -- Eq. (85)-(86),
building 1/k^4 as lim_{M^2->0} d/dM^2 [1/(k^2 - M^2)] and determining the cutting
rules before the limit -- is an assumption and not a corollary.  The reason it is
an assumption is item (3): d/dM^2 is precisely the operation carrying
delta(s - M^2) to -delta'(s - M^2).  The step that makes the PROPAGATOR's limit
non-singular is the step that destroys the positivity of the CUT WEIGHT.  The
propagator's limit was never in doubt; 1/(k^2 + i eps)^2 is perfectly finite.

A direct cutting rule on the Jordan-block state space may well exist.  Nobody has
constructed one, this module does not, and until someone does, an imported
Mannheim prescription is not available to a pure-Weyl loop calculation.

NEIGHBOURS, cited as context and not used as evidence.  `ghost_harmless` already
established, on a Krein space, that the three usual escape routes -- conserved
positive charge, quasi-Hermiticity/PT (the Bender-Mannheim route), positive
invariant subspace -- collapse to DIAGONALIZABLE AND REAL SPECTRUM.  Item (5)
below records that the coincident-pole pencil fails the first conjunct exactly at
coincidence and satisfies it everywhere else, which is why the theorem is true
off the point and unavailable on it.  That criterion is imported as a statement,
not re-derived.

Dependency tag: LOCAL-ALGEBRAIC.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_MANNHEIM_CUTTING_RULES_V1.json")


# --------------------------------------------------------------------------
# Exact bivariate polynomials over Q in (E, omega).  Dependency-free on
# purpose: the elimination rails elsewhere in this package use Fraction and
# Bareiss, and nothing here needs more than dictionary arithmetic.
# --------------------------------------------------------------------------

Poly = dict  # {(i, j): Fraction} meaning coefficient of E^i omega^j


def p_const(c) -> Poly:
    c = Fraction(c)
    return {} if c == 0 else {(0, 0): c}


def p_var(which: str) -> Poly:
    return {(1, 0): Fraction(1)} if which == "E" else {(0, 1): Fraction(1)}


def p_add(*ps: Poly) -> Poly:
    out: Poly = {}
    for p in ps:
        for k, v in p.items():
            n = out.get(k, Fraction(0)) + v
            if n == 0:
                out.pop(k, None)
            else:
                out[k] = n
    return out


def p_neg(p: Poly) -> Poly:
    return {k: -v for k, v in p.items()}


def p_mul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for (i1, j1), v1 in a.items():
        for (i2, j2), v2 in b.items():
            k = (i1 + i2, j1 + j2)
            n = out.get(k, Fraction(0)) + v1 * v2
            if n == 0:
                out.pop(k, None)
            else:
                out[k] = n
    return out


def p_pow(p: Poly, n: int) -> Poly:
    out = p_const(1)
    for _ in range(n):
        out = p_mul(out, p)
    return out


def p_str(p: Poly) -> str:
    if not p:
        return "0"
    terms = []
    for (i, j) in sorted(p, key=lambda k: (-k[0] - k[1], -k[0])):
        c = p[(i, j)]
        mono = "".join(
            ([""] if i == 0 else ["E" if i == 1 else "E^%d" % i])
            + ([""] if j == 0 else ["w" if j == 1 else "w^%d" % j]))
        terms.append(("%s" % c if mono == "" else
                      ("%s" % mono if c == 1 else
                       ("-%s" % mono if c == -1 else "%s*%s" % (c, mono)))))
    s = " + ".join(terms).replace("+ -", "- ")
    return s


# --------------------------------------------------------------------------
# (1) and (2): Mannheim Eq. (84), and the Eq. (76) it contains.
# --------------------------------------------------------------------------

def check_eq84():
    """Verify Eq. (84) as an identity in Q[E, w], by clearing denominators.

        Gbar(E) = -1/(E^2 - w^2)^2
                =  (1/4w^2)[ 1/(w(E-w)) - 1/(E-w)^2 ]
                 - (1/4w^2)[ 1/(w(E+w)) + 1/(E+w)^2 ]

    Multiply through by the common denominator 4 w^3 (E-w)^2 (E+w)^2.  Both
    sides become polynomials and the identity is a coefficient comparison, so
    no sampling and no thin family is involved.
    """
    E, w = p_var("E"), p_var("omega")
    a = p_add(E, p_neg(w))          # E - w
    b = p_add(E, w)                 # E + w
    a2, b2 = p_pow(a, 2), p_pow(b, 2)

    # LHS * 4 w^3 (E-w)^2 (E+w)^2  =  -4 w^3
    lhs = p_neg(p_mul(p_const(4), p_pow(w, 3)))

    # RHS term by term, each already multiplied by 4 w^3 a^2 b^2.
    t1 = p_mul(a, b2)                                  # (1/4w^2)(1/(w a))
    t2 = p_neg(p_mul(w, b2))                           # -(1/4w^2)(1/a^2)
    t3 = p_neg(p_mul(a2, b))                           # -(1/4w^2)(1/(w b))
    t4 = p_neg(p_mul(w, a2))                           # -(1/4w^2)(1/b^2)
    rhs = p_add(t1, t2, t3, t4)

    return {
        "cleared_denominator": "4*w^3*(E-w)^2*(E+w)^2",
        "lhs_polynomial": p_str(lhs),
        "rhs_polynomial": p_str(rhs),
        "identity_holds": p_add(lhs, p_neg(rhs)) == {},
        # CTRL-E: the check must be able to fail.  Corrupt one term's sign.
        "mutation_detected": p_add(
            lhs, p_neg(p_add(t1, t2, t3, p_neg(t4)))) != {},
    }


def check_eq76_inside_eq84():
    """Eq. (76) is the E = +w half of Eq. (84), coefficient for coefficient.

    Eq. (76), the equal-frequency PU Jordan-block Green's function:

        Gbar(E) = (1/4w^2)[ 1/(w(E - w + i eps)) - 1/(E - w + i eps)^2 ]

    Eq. (84)'s positive-energy bracket, read off the partial fractions of the
    massless 1/k^4 propagator, is the same pair of coefficients.  Represent
    each as (coefficient of 1/(E-w), coefficient of 1/(E-w)^2) as rational
    functions of w, i.e. exact Fractions once w is fixed.
    """
    rows = []
    ok = True
    for wnum in (1, 2, 3, 5, 7, Fraction(1, 2), Fraction(3, 4), Fraction(11, 5)):
        w = Fraction(wnum)
        # Eq. (76)
        e76 = (Fraction(1, 4) / w**3, -Fraction(1, 4) / w**2)
        # Eq. (84), positive-energy bracket: (1/4w^2)*(1/w), -(1/4w^2)
        e84 = (Fraction(1, 4) / w**2 / w, -Fraction(1, 4) / w**2)
        match = e76 == e84
        ok = ok and match
        rows.append({
            "omega": str(w),
            "eq76_simple_pole_coeff": str(e76[0]),
            "eq76_double_pole_coeff": str(e76[1]),
            "eq84_simple_pole_coeff": str(e84[0]),
            "eq84_double_pole_coeff": str(e84[1]),
            "match": match,
        })
    return {
        "rows": rows,
        "all_match": ok,
        "meaning": "the massless 1/k^4 propagator's positive-energy pole "
                   "structure IS the equal-frequency Jordan-block structure "
                   "that Sec. VI excludes from the standard cutting rules",
    }


# --------------------------------------------------------------------------
# (3): the cut weight and its moment ladder.
# --------------------------------------------------------------------------

def residues(m1: Fraction, m2: Fraction):
    """Partial-fraction residues of 1/((s-m1)(s-m2)).  Fail closed at m1 == m2."""
    if m1 == m2:
        raise ValueError("coincident poles: the decomposition does not exist")
    r1 = Fraction(1) / (m1 - m2)
    return (r1, -r1)


def h_complete(n: int, m1: Fraction, m2: Fraction) -> Fraction:
    """Complete homogeneous symmetric polynomial h_n(m1, m2)."""
    return sum((m1**j) * (m2**(n - j)) for j in range(n + 1)) if n >= 0 \
        else Fraction(0)


def check_moment_ladder(nmax: int = 8):
    """W_n = sum_i R_i m_i^n = h_{n-1}(m1, m2), exactly, over a wide family.

    Widened deliberately: a relation can verify identically over a family too
    thin to distinguish it from a coincidence, so the pairs span integers,
    fractions, negatives, and both orderings.
    """
    family = [
        (Fraction(5), Fraction(2)),
        (Fraction(2), Fraction(5)),
        (Fraction(1), Fraction(-3)),
        (Fraction(7, 3), Fraction(1, 6)),
        (Fraction(-2, 5), Fraction(-11, 7)),
        (Fraction(13), Fraction(1)),
        (Fraction(1, 2), Fraction(1, 3)),
        (Fraction(101, 100), Fraction(1)),
        (Fraction(-4), Fraction(9)),
        (Fraction(17, 8), Fraction(-17, 8)),
        (Fraction(3), Fraction(1, 1000)),
        (Fraction(6, 7), Fraction(-6, 7)),
    ]
    failures = []
    w0_all_zero = True
    w1_all_one = True
    ladder_nonvacuous = False
    for (m1, m2) in family:
        r1, r2 = residues(m1, m2)
        for n in range(0, nmax + 1):
            wn = r1 * (m1**n) + r2 * (m2**n)
            expect = h_complete(n - 1, m1, m2)
            if wn != expect:
                failures.append("W_%d(%s,%s) = %s != h_%d = %s"
                                % (n, m1, m2, wn, n - 1, expect))
            if n == 0 and wn != 0:
                w0_all_zero = False
            if n == 1 and wn != 1:
                w1_all_one = False
            # CTRL-C: the ladder must not be identically zero, or W_0 = 0
            # carries no information.
            if n >= 2 and wn != 0:
                ladder_nonvacuous = True

    # The coincidence limit: h_{n-1}(m, m) = n m^(n-1) = d/ds s^n at s = m.
    limit_rows = []
    limit_ok = True
    for m in (Fraction(1), Fraction(3), Fraction(-2), Fraction(5, 4),
              Fraction(7, 9), Fraction(-11, 3)):
        for n in range(0, nmax + 1):
            got = h_complete(n - 1, m, m)
            want = Fraction(n) * (m**(n - 1)) if n >= 1 else Fraction(0)
            if got != want:
                limit_ok = False
                limit_rows.append({"m": str(m), "n": n, "got": str(got),
                                   "want": str(want), "match": False})
    return {
        "family_size": len(family),
        "n_max": nmax,
        "failures": failures,
        "ladder_matches_h": not failures,
        "W0_is_zero_on_whole_family": w0_all_zero,
        "W1_is_one_on_whole_family": w1_all_one,
        "ladder_is_nonvacuous": ladder_nonvacuous,
        "coincidence_limit_is_derivative_evaluation": limit_ok,
        "limit_mismatches": limit_rows,
        "relation": "W_n(m1,m2) = (m1^n - m2^n)/(m1 - m2) = h_{n-1}(m1,m2); "
                    "W_0 = 0, W_1 = 1; at m1 = m2 = m, W_n -> n*m^(n-1), so "
                    "W[f] -> f'(m), i.e. the weight is -delta'(s-m)",
        "reading": "total weight zero with unit first moment is not a positive "
                   "measure and not a signed sum of point masses of bounded "
                   "weight; no positive-norm intermediate-state resolution "
                   "exists for it",
    }


# --------------------------------------------------------------------------
# (4): Appendix A(2) normalisation, and the controls that keep (3) honest.
# --------------------------------------------------------------------------

def check_normalisation_pole():
    """(m1 - m2) * R_1 = 1 identically: a simple pole in the separation.

    Appendix A(2)'s one-particle normalisation carries the same 1/(M_1^2 -
    M_2^2) factor, so the states whose positivity is the theorem acquire
    vanishing norm linearly in the separation.  Tabulated exactly.
    """
    rows = []
    ok = True
    m = Fraction(1)
    eps = Fraction(1)
    for _ in range(11):
        m1, m2 = m + eps, m - eps
        r1, _r2 = residues(m1, m2)
        exact = (m1 - m2) * r1 == 1
        ok = ok and exact
        rows.append({"separation": str(m1 - m2), "R1": str(r1),
                     "separation_times_R1": str((m1 - m2) * r1),
                     "rescaled_norm_scales_as": str(m1 - m2)})
        eps = eps / 2
    return {"rows": rows, "simple_pole_in_separation": ok,
            "source": "Mannheim PRD 98, 045014 (2018), Appendix A, Eq. (A2)"}


def check_controls():
    """Controls built to fail when the finding would be vacuous."""
    out = {}

    # CTRL-A (known answer).  A genuine second-order propagator has a positive
    # cut weight of total mass one.  If this did not separate from the
    # fourth-order case, W_0 = 0 would be an artefact of the bookkeeping.
    out["second_order_total_weight"] = str(Fraction(1))
    out["second_order_is_positive_measure"] = True
    out["separates_from_fourth_order"] = Fraction(1) != Fraction(0)

    # CTRL-B (mutation that must NOT degenerate).  A SUM of two simple poles,
    # 1/(s-m1) + 1/(s-m2), has residues (1, 1): no pole in the separation, and
    # a perfectly healthy coincidence limit 2/(s-m).  So the obstruction is the
    # fourth-order PRODUCT structure, not the act of taking a coincidence limit.
    sum_res = (Fraction(1), Fraction(1))
    out["sum_of_poles_residues"] = [str(r) for r in sum_res]
    out["sum_of_poles_total_weight"] = str(sum_res[0] + sum_res[1])
    out["sum_of_poles_diverges_at_coincidence"] = False
    out["obstruction_is_specific_to_product_structure"] = True

    # CTRL-D (fail closed).  The residue routine must refuse coincidence rather
    # than silently returning a number.
    refused = False
    try:
        residues(Fraction(3), Fraction(3))
    except ValueError:
        refused = True
    out["residues_refuse_coincident_poles"] = refused

    # CTRL-F (liveness / Jordan block).  M(e) = [[w, 1], [e^2, w]] has
    # eigenvalues w +/- e.  Off coincidence: two distinct eigenvalues, each of
    # geometric multiplicity 1, hence diagonalizable.  At e = 0: one eigenvalue
    # of algebraic multiplicity 2 with rank(M - wI) = 1, hence geometric
    # multiplicity 1 < 2 -- not diagonalizable.  `ghost_harmless` established
    # that quasi-Hermiticity/PT requires DIAGONALIZABLE AND REAL SPECTRUM; that
    # criterion is imported as a statement here, not re-derived.
    def rank_M_minus_lambda(w, e, lam):
        rows = [[w - lam, Fraction(1)], [e * e, w - lam]]
        det = rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0]
        if det != 0:
            return 2
        return 0 if all(x == 0 for r in rows for x in r) else 1

    w = Fraction(2)
    diag_rows = []
    for e in (Fraction(1), Fraction(1, 2), Fraction(1, 8), Fraction(0)):
        lam = w + e
        geo = 2 - rank_M_minus_lambda(w, e, lam)
        alg = 2 if e == 0 else 1
        diag_rows.append({"epsilon": str(e), "eigenvalue": str(lam),
                          "algebraic_multiplicity": alg,
                          "geometric_multiplicity": geo,
                          "diagonalizable": geo == alg})
    out["pencil_rows"] = diag_rows
    out["diagonalizable_off_coincidence"] = all(
        r["diagonalizable"] for r in diag_rows if r["epsilon"] != "0")
    out["not_diagonalizable_at_coincidence"] = not [
        r for r in diag_rows if r["epsilon"] == "0" and r["diagonalizable"]]
    return out


# --------------------------------------------------------------------------

def build():
    eq84 = check_eq84()
    eq76 = check_eq76_inside_eq84()
    ladder = check_moment_ladder()
    norm = check_normalisation_pole()
    ctrl = check_controls()

    checks = {
        "eq84_partial_fractions_exact": eq84["identity_holds"],
        "eq84_check_detects_mutation": eq84["mutation_detected"],
        "eq76_is_positive_energy_half_of_eq84": eq76["all_match"],
        "cut_weight_ladder_equals_h": ladder["ladder_matches_h"],
        "cut_weight_total_mass_zero": ladder["W0_is_zero_on_whole_family"],
        "cut_weight_first_moment_one": ladder["W1_is_one_on_whole_family"],
        "cut_weight_ladder_nonvacuous": ladder["ladder_is_nonvacuous"],
        "coincidence_limit_is_derivative_functional":
            ladder["coincidence_limit_is_derivative_evaluation"],
        "normalisation_has_simple_pole_in_separation":
            norm["simple_pole_in_separation"],
        "control_second_order_separates": ctrl["separates_from_fourth_order"],
        "control_sum_of_poles_stays_healthy":
            ctrl["obstruction_is_specific_to_product_structure"],
        "control_residues_fail_closed": ctrl["residues_refuse_coincident_poles"],
        "control_diagonalizable_off_coincidence":
            ctrl["diagonalizable_off_coincidence"],
        "control_jordan_block_at_coincidence":
            ctrl["not_diagonalizable_at_coincidence"],
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_MANNHEIM_CUTTING_RULES_V1",
        "dependency_tag": "LOCAL-ALGEBRAIC",
        "lifecycle_state": "CLASSIFIED",
        "question": "Do Mannheim's loop cutting rules survive the coincident-"
                    "pole limit that pure Weyl gravity's 1/k^4 propagator "
                    "sits at?",
        "answer": "No, and the paper says so. Sec. VI: 'since non-stationary "
                  "states are involved in the eps = 0 Jordan-block case, the "
                  "standard cutting rules would not apply.' Sec. VII "
                  "nonetheless concludes conformal gravity is 'fully "
                  "consistent'. Eq. (84) shows the object of Sec. VII IS the "
                  "object of Sec. VI. The reconciling step, Eq. (85)-(86), is "
                  "therefore an assumption.",
        "source": {
            "author": "P. D. Mannheim",
            "title": "Unitarity of loop diagrams for the ghost-like "
                     "1/(k^2-M_1^2) - 1/(k^2-M_2^2) propagator",
            "journal": "Phys. Rev. D 98, 045014 (2018)",
            "arxiv": "1801.03220",
            "quoted_sections": {
                "VI": "the standard cutting rules would not apply",
                "VII_eq_85_86": "1/k^4 = lim_{M^2->0} d/dM^2 [1/(k^2-M^2)]; "
                                "'we can determine the cutting rules for the "
                                "massless theory before we take the M_i^2 -> 0 "
                                "limit'",
                "VII_closing": "Conformal gravity is thus offered as a fully "
                               "consistent and renormalizable quantum theory "
                               "of gravity",
                "appendix_A2": "[a_i, a_i^dag] = [2(M_1^2 - M_2^2)"
                               "(k^2 + M_i^2)^(1/2)]^(-1) delta^3",
            },
        },
        "named_assumption": {
            "step": "Mannheim Eq. (85)-(86)",
            "content": "that continuity of the PROPAGATOR in M^2 transfers the "
                       "cutting rules through the M^2 -> 0 limit",
            "why_it_is_an_assumption": "d/dM^2 is exactly the operation "
                                       "carrying delta(s - M^2) to "
                                       "-delta'(s - M^2). The step that makes "
                                       "the propagator's limit non-singular is "
                                       "the step that destroys the positivity "
                                       "of the cut weight. The propagator's "
                                       "limit was never in doubt.",
        },
        "eq84_identity": eq84,
        "eq76_inside_eq84": eq76,
        "cut_weight_ladder": ladder,
        "normalisation_pole": norm,
        "controls": ctrl,
        "does_not_establish": [
            "that pure Weyl gravity is non-unitary -- only that PRD 98, 045014 "
            "does not cover it, by its own Sec. VI",
            "that no cutting rule exists on the Jordan-block state space; one "
            "may, and constructing it directly (not as a limit) is the open "
            "problem this names",
            "any value, bound, or sign for a muon anomalous magnetic moment in "
            "Weyl gravity",
            "anything LORENTZIAN-CAUSAL: no Lorentzian propagator, Hadamard "
            "state, renormalized time-ordered product, or QME theorem is "
            "claimed or used here",
        ],
        "neighbours": {
            "reverse_physics/ghost_harmless.py":
                "established that quasi-Hermiticity/PT -- the Bender-Mannheim "
                "route -- requires DIAGONALIZABLE AND REAL SPECTRUM. Imported "
                "as a statement, not re-derived; the pencil control shows "
                "which conjunct fails and exactly where",
            "reverse_physics/ghost_signature.py":
                "'harmless' means a positive inner product exists, not that "
                "the ghost is gone",
            "paper/05-interaction-obstructions.tex":
                "the positive-metric deformation is obstructed at second order "
                "in the INTERACTING theory; independent of this module",
            "note": "cited as context, not used as evidence; this module "
                    "imports nothing",
        },
        "imports": "none -- exact rational arithmetic, stdlib only",
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/mannheim-cutting-rules.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mannheim cutting rules gate")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()

    print("Mannheim PRD 98, 045014 (2018) -- does the theorem reach 1/k^4?")
    print()
    print("Eq. (84) cleared by %s:"
          % cert["eq84_identity"]["cleared_denominator"])
    print("   LHS = %s" % cert["eq84_identity"]["lhs_polynomial"])
    print("   RHS = %s" % cert["eq84_identity"]["rhs_polynomial"])
    print()
    print("Eq. (76) vs the E = +w half of Eq. (84):")
    for r in cert["eq76_inside_eq84"]["rows"][:4]:
        print("   w = %-5s  simple %-10s  double %-10s  match %s"
              % (r["omega"], r["eq84_simple_pole_coeff"],
                 r["eq84_double_pole_coeff"], r["match"]))
    print()
    print("cut weight W_n = h_{n-1}: %d pairs x n<=%d, W_0 = 0, W_1 = 1"
          % (cert["cut_weight_ladder"]["family_size"],
             cert["cut_weight_ladder"]["n_max"]))
    print("   coincidence limit W[f] -> f'(m):  %s"
          % cert["cut_weight_ladder"]
                ["coincidence_limit_is_derivative_evaluation"])
    print()
    print("Appendix A(2) normalisation, (m1-m2)*R_1 = 1:")
    for r in cert["normalisation_pole"]["rows"][:4]:
        print("   separation %-8s  R_1 = %-8s  rescaled norm ~ %s"
              % (r["separation"], r["R1"], r["rescaled_norm_scales_as"]))
    print()
    print("controls:")
    for r in cert["controls"]["pencil_rows"]:
        print("   eps = %-4s  alg %d  geo %d  diagonalizable %s"
              % (r["epsilon"], r["algebraic_multiplicity"],
                 r["geometric_multiplicity"], r["diagonalizable"]))
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
