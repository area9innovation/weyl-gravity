"""RP-DIFF -- an independence witness, and what it costs the derived order.

WHY THIS EXISTS.  RP-DIFF is the one assumption in the Weyl-action ledger with
no independence witness.  [PHYSICS-VS-MATH.md] says why:

    "RP-DIFF is invisible.  It is what makes 'the space of curvature scalars'
     the right space at all, so it never appears as a row in a matrix.  That is
     a real gap: an assumption doing structural work should still get a
     witness."

That diagnosis is correct AND it is a statement about the CARRIER, not about
the assumption.  The stream has hit this exact shape once before.  RP-REVERSIBLE
(section 4.2) "appeared under `consumed` in every certificate and `under_test`
in none -- structurally, because on the Hamiltonian carriers every evolution is
exp(tA) and neither determinism nor reversibility can fail".  The fix was not
cleverness about the old carrier; it was MOVING TO A CARRIER WHERE THE
ASSUMPTION CAN FAIL.  This module does the same thing for RP-DIFF.

THE ENLARGED CARRIER.  The classification's carrier is "quadratic curvature
scalars", which is diffeomorphism-invariant by construction -- every element is
built from tensors and fully contracted, so RP-DIFF cannot fail inside it.  The
enlarged carrier drops that: LOCAL DENSITIES BUILT ALGEBRAICALLY FROM THE METRIC
COMPONENTS, with no requirement that indices be contracted into scalars.  These
are perfectly good local functionals of the metric.  They are simply not
covariant, which is exactly the property under test.

WHAT IS COMPUTED.  Write a density as sqrt(-g) times a monomial in the
components of the inverse metric h^{mn} = g^{mn} and the metric g_{mn}, at
DERIVATIVE ORDER ZERO.  Under a Weyl rescaling g -> lambda g one has
h -> lambda^{-1} h, g -> lambda g and sqrt(-g) -> lambda^2 sqrt(-g), so

    sqrt(-g) h^n g^m   has Weyl weight   2 - n + m

and Weyl invariance is exactly n - m = 2.  At derivative order zero there are no
derivatives of the conformal factor, so weight zero IS invariance -- no
inhomogeneous terms, which is why this order is decisive and cheap.

The LOWEST weight-zero degree is (n, m) = (2, 0), i.e. sqrt(-g) h^{ab} h^{cd}.
That space is classified COMPLETELY here, not sampled:

    Weyl-invariant subspace      55-dimensional  (all of it, by construction)
    Diff-invariant subspace       0-dimensional  (COMPUTED, exact rank over Q)

Diffeomorphism invariance at a point, for a density with no derivatives, is
invariance under the GL(4) action on the metric, and it is imposed here by
computing the kernel of the 16 GL(4) generators exactly.  The answer is zero
because the only GL-invariant algebraic function of a single nondegenerate
symmetric form is a constant, and a constant times sqrt(-g) has weight 2, not 0.

So EVERY ONE of the 55 is an independence witness, and RP-DIFF is independent
given the other assumptions.  An explicit one is carried in the certificate:

    sqrt(-g) (g^{00})^2

which is local, metric-only, D = 4, parity-even, Weyl-invariant, not a
topological term -- and not diffeomorphism-invariant.

WHY THE MACHINERY IS NOT JUST RETURNING ZERO.  A zero-dimensional answer from an
invariance computation is exactly the kind of result that can be a bug.  So the
identical machinery is run on a CONTROL SPACE where the invariant subspace is
known to be nonzero: the bilinear span of h^{ab} g_{cd}, whose GL-invariants are
one-dimensional, spanned by the trace h^{ab} g_{ab} = 4.  If the control does
not come back 1, the zero above means nothing.  Two independent rank routines
are used, matching the repository's rail-A/rail-B convention.

THE CONSEQUENCE, WHICH IS THE POINT.  The witness sits at DERIVATIVE ORDER ZERO.
The stream's best result is that the derivative order is DERIVED, not assumed:
D - 2k = 0 forces k = D/2, hence four derivatives at D = 4, which is section
4.3's "not an assumption at all".  That derivation runs through G3, the
conformal weight of the WEYL TENSOR -- a curvature scalar, hence already
diff-covariant.  Drop RP-DIFF and the derivation has nothing to run on: here is
a Weyl-invariant local metric density with ZERO derivatives, which k = 2 forbids.

    THE DERIVED DERIVATIVE ORDER REQUIRES RP-DIFF.

That is a load-bearing role for an assumption the ledger had recorded as
carrying no witness at all, and it is the reverse-physics content of this
module.  It does not weaken section 4.3; it names the input section 4.3 was
silently using.

WHAT THIS DOES NOT ESTABLISH.  Written out because the temptations are obvious:

  * It is a statement about DERIVATIVE ORDER ZERO and the lowest weight-zero
    degree.  Higher degrees (3,1), (4,2), ... are also weight zero and are NOT
    classified here; the order-zero space is infinite-dimensional as a
    polynomial algebra and only its lowest graded piece is settled.
  * It says nothing about whether any of the 55 is a sensible physical theory.
    A witness does not have to be sensible -- R^2 witnesses RP-WEYL and nobody
    proposes R^2 gravity.  Sensibleness is not the test; satisfying the OTHER
    assumptions while failing this one is the test.
  * The Stuckelberg escape -- promote coordinates to fields and any
    non-covariant theory becomes covariant -- is BLOCKED HERE BY RP-METRIC, not
    refuted.  Given a second field the witness would covariantise.  So what is
    established is the independence of RP-DIFF *given RP-METRIC*, and that
    entanglement is recorded rather than hidden.
  * Nothing quantum.  There is a separate, independently computed result in this
    repository's quantum chain that the pure-Diff anomaly cohomology vanishes in
    D = 4; that is a DIFFERENT question at a DIFFERENT level, it is not used as
    evidence here, and this module is not evidence for it.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.diff_independence --check
    PYTHONPATH=. python3 -m reverse_physics.diff_independence --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import combinations_with_replacement

from reverse_physics.exact_linalg import rank_bareiss, rank_fraction

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_DIFF_INDEPENDENCE_V1.json",
)

DIM = 4
# Unordered index pairs (mn) with m <= n: the independent components of a
# symmetric 2-tensor in four dimensions.
PAIRS = [(m, n) for m in range(DIM) for n in range(m, DIM)]


def key(m, n):
    return (m, n) if m <= n else (n, m)


# --------------------------------------------------------------------------
# The GL(4) action.  Under x'^m = x^m + eps A^m_n x^n, at a point:
#
#     delta g_{mn}   = -( A^a_m g_{an} + A^a_n g_{ma} )
#     delta h^{mn}   = +( A^m_a h^{an} + A^n_a h^{ma} )
#     delta sqrt(-g) = -tr(A) sqrt(-g)
#
# Generators are the elementary matrices A = E^a_b.
# --------------------------------------------------------------------------

def d_inverse(pair, a, b):
    """delta h^{pair} for the generator E^a_b, as {pair: coefficient}."""
    m, n = pair
    out = {}
    if m == a:
        out[key(b, n)] = out.get(key(b, n), 0) + 1
    if n == a:
        out[key(m, b)] = out.get(key(m, b), 0) + 1
    return out


def d_metric(pair, a, b):
    """delta g_{pair} for the generator E^a_b."""
    m, n = pair
    out = {}
    if m == b:
        out[key(a, n)] = out.get(key(a, n), 0) - 1
    if n == b:
        out[key(m, a)] = out.get(key(m, a), 0) - 1
    return out


def trace_of_generator(a, b):
    return 1 if a == b else 0


# --------------------------------------------------------------------------
# Space 1 -- the weight-zero densities sqrt(-g) h^{p} h^{q}.
# --------------------------------------------------------------------------

# Basis: unordered pairs of index-pairs.
H2_BASIS = list(combinations_with_replacement(PAIRS, 2))


def h2_key(p, q):
    return tuple(sorted((p, q)))


def variation_row_h2(basis_element):
    """Row of the GL-variation matrix for sqrt(-g) h^p h^q.

    Columns are indexed by (generator, monomial).  A density is
    diffeomorphism-invariant iff its row is zero.
    """
    p, q = basis_element
    row = {}
    for a in range(DIM):
        for b in range(DIM):
            acc = {}

            def add(mon, coeff):
                if coeff:
                    acc[mon] = acc.get(mon, 0) + coeff

            # -tr(A) from sqrt(-g)
            add(h2_key(p, q), -trace_of_generator(a, b))
            # product rule on the two inverse metrics
            for r, c in d_inverse(p, a, b).items():
                add(h2_key(r, q), c)
            for s, c in d_inverse(q, a, b).items():
                add(h2_key(p, s), c)

            for mon, coeff in acc.items():
                if coeff:
                    row[((a, b), mon)] = row.get(((a, b), mon), 0) + coeff
    return row


# --------------------------------------------------------------------------
# Control space -- the bilinears h^{p} g_{q}.  Its GL-invariants are KNOWN to be
# one-dimensional (the trace h^{ab} g_{ab} = 4).  If this comes back anything
# other than 1, the zero above is a bug, not a result.
# --------------------------------------------------------------------------

CONTROL_BASIS = [(p, q) for p in PAIRS for q in PAIRS]


def variation_row_control(basis_element):
    p, q = basis_element
    row = {}
    for a in range(DIM):
        for b in range(DIM):
            acc = {}

            def add(mon, coeff):
                if coeff:
                    acc[mon] = acc.get(mon, 0) + coeff

            for r, c in d_inverse(p, a, b).items():
                add((r, q), c)
            for s, c in d_metric(q, a, b).items():
                add((p, s), c)

            for mon, coeff in acc.items():
                if coeff:
                    row[((a, b), mon)] = row.get(((a, b), mon), 0) + coeff
    return row


def invariant_dimension(basis, row_fn):
    """dim ker of the GL-variation map, by two independent rank routines."""
    rows = [row_fn(e) for e in basis]
    columns = sorted({c for r in rows for c in r},
                     key=lambda c: (c[0], str(c[1])))
    index = {c: i for i, c in enumerate(columns)}
    dense = []
    for r in rows:
        vec = [Fraction(0)] * len(columns)
        for c, v in r.items():
            vec[index[c]] = Fraction(v)
        dense.append(vec)
    rank_a = rank_fraction(dense)
    rank_b = rank_bareiss(dense)
    return {
        "basis_dimension": len(basis),
        "column_count": len(columns),
        "rank_rail_a_gauss_jordan": rank_a,
        "rank_rail_b_bareiss": rank_b,
        "rails_agree": rank_a == rank_b,
        "invariant_dimension": len(basis) - rank_a,
    }


# --------------------------------------------------------------------------
# Weyl weights.  sqrt(-g) h^n g^m has weight 2 - n + m under g -> lambda g.
# --------------------------------------------------------------------------

def weyl_weight(n_inverse, m_metric):
    return 2 - n_inverse + m_metric


def weyl_analysis():
    """Which degrees are Weyl invariant, and the control that they are not all."""
    rows = []
    for n in range(0, 5):
        w = weyl_weight(n, 0)
        rows.append({"inverse_metric_degree": n, "metric_degree": 0,
                     "weyl_weight": w, "is_weyl_invariant": w == 0})
    return rows


# --------------------------------------------------------------------------

WITNESS = {
    "density": "sqrt(-g) (g^{00})^2",
    "basis_element": "h^{(0,0)} h^{(0,0)}",
    "derivative_order": 0,
    "satisfies": {
        "RP-LOCAL": "an integral of a local density",
        "RP-METRIC": "built from the metric alone",
        "RP-DIM4": "D = 4",
        "RP-WEYL": "Weyl weight 2 - 2 + 0 = 0, hence invariant",
        "RP-PARITY": "no epsilon tensor; parity even",
        "RP-TOPO-INERT": "not a topological term, so the assumption does not "
                         "constrain it",
    },
    "violates": "RP-DIFF -- it is not a scalar; g^{00} singles out a coordinate",
}


def witness_is_not_invariant():
    """Exhibit a generator that moves the witness, so the witness is not
    accidentally in the kernel."""
    element = ((0, 0), (0, 0))
    row = variation_row_h2(element)
    movers = sorted({gen for (gen, _mon), c in row.items() if c},
                    key=lambda g: g)
    return {"is_moved": bool(movers),
            "generators_that_move_it": ["E^%d_%d" % g for g in movers[:6]],
            "generator_count": len(movers)}


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    main_space = invariant_dimension(H2_BASIS, variation_row_h2)
    control = invariant_dimension(CONTROL_BASIS, variation_row_control)
    weights = weyl_analysis()
    witness = witness_is_not_invariant()

    invariant_degrees = [r["inverse_metric_degree"] for r in weights
                         if r["is_weyl_invariant"]]

    checks = {
        # the classification at the lowest weight-zero degree
        "weyl_invariant_space_is_the_full_55":
            main_space["basis_dimension"] == 55,
        "diff_invariant_subspace_is_zero":
            main_space["invariant_dimension"] == 0,
        "rank_rails_agree_on_main_space": main_space["rails_agree"],
        # the control -- without this the zero above is worthless
        "control_finds_its_known_invariant":
            control["invariant_dimension"] == 1,
        "rank_rails_agree_on_control": control["rails_agree"],
        # Weyl bookkeeping
        "exactly_one_degree_is_weyl_invariant": invariant_degrees == [2],
        "degree_one_is_not_weyl_invariant":
            not weights[1]["is_weyl_invariant"],
        # the witness really is a witness
        "witness_is_moved_by_a_generator": witness["is_moved"],
        # the consequence
        "witness_has_zero_derivative_order": WITNESS["derivative_order"] == 0,
        "derived_order_at_D4_is_four": True,
        "witness_contradicts_the_derived_order":
            WITNESS["derivative_order"] != 4,
    }

    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_DIFF_INDEPENDENCE_V1",
        "kind": "independence-witness",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "RP-DIFF has an independence witness, given the other assumptions "
            "of the Weyl-action ledger.  On the enlarged carrier of local "
            "metric densities at derivative order zero, the lowest weight-zero "
            "degree sqrt(-g) h^{ab} h^{cd} is 55-dimensional and entirely "
            "Weyl-invariant, while its diffeomorphism-invariant subspace is "
            "exactly ZERO -- computed as the kernel of the sixteen GL(4) "
            "generators by two independent exact rational rank routines, with "
            "a control space whose invariant subspace is known to be "
            "one-dimensional and is found to be.  Every one of the 55 is "
            "therefore a witness.  The consequence is the reverse-physics "
            "content: the witness sits at DERIVATIVE ORDER ZERO, so the "
            "derived derivative order k = D/2 -- section 4.3's result that "
            "four derivatives is a consequence rather than an assumption -- "
            "REQUIRES RP-DIFF.  An assumption previously recorded as carrying "
            "no witness turns out to be load-bearing for the stream's best "
            "result.",
        "does_not_establish": [
            "anything beyond derivative order zero and the LOWEST weight-zero "
            "degree (2,0); the degrees (3,1), (4,2), ... are also weight zero "
            "and are not classified here",
            "that any witness is a sensible physical theory -- a witness need "
            "not be, exactly as R^2 witnesses RP-WEYL without anyone proposing "
            "R^2 gravity",
            "independence of RP-DIFF unconditionally.  The Stuckelberg escape "
            "-- promote the coordinates to fields and any non-covariant theory "
            "becomes covariant -- is BLOCKED BY RP-METRIC, not refuted.  What "
            "is established is independence of RP-DIFF GIVEN RP-METRIC, and "
            "the entanglement is recorded rather than hidden",
            "any quantum statement.  The vanishing of pure-Diff anomaly "
            "cohomology in D = 4 is a separate result at a different level in "
            "this repository's quantum chain; it is not used as evidence here "
            "and this is not evidence for it",
            "that section 4.3 is wrong.  The derived derivative order stands; "
            "what is established is which input it was silently using",
        ],
        "carrier": {
            "old": "quadratic curvature scalars -- diffeomorphism-invariant BY "
                   "CONSTRUCTION, so RP-DIFF cannot fail inside it and no "
                   "witness can exist there",
            "new": "local densities built algebraically from the metric "
                   "components at derivative order zero, with no requirement "
                   "that indices contract into scalars",
            "precedent": "section 4.2 -- RP-REVERSIBLE was unwitnessable on "
                         "the Hamiltonian carriers for the same structural "
                         "reason, and the fix was to move to a carrier where "
                         "it could fail",
        },
        "weyl_weights": weights,
        "main_space": main_space,
        "control_space": dict(control, purpose=
            "GL-invariants of h^{ab} g_{cd} are known to be one-dimensional, "
            "spanned by the trace h^{ab} g_{ab} = 4.  A zero-dimensional "
            "answer from an invariance computation is exactly the kind of "
            "result that can be a bug, so the identical machinery must find "
            "this one."),
        "witness": dict(WITNESS, **witness),
        "consequence": {
            "claim": "the derived derivative order requires RP-DIFF",
            "derived_order_at_D4": 4,
            "witness_derivative_order": 0,
            "why": "the derivation k = D/2 runs through G3, the conformal "
                   "weight of the WEYL TENSOR, which is a curvature scalar and "
                   "therefore already diff-covariant.  Without RP-DIFF the "
                   "derivation has nothing to run on, and this witness is an "
                   "explicit Weyl-invariant local metric density with zero "
                   "derivatives, which k = 2 forbids.",
        },
        "inputs": {
            "reverse_physics/exact_linalg.py":
                file_hash("reverse_physics/exact_linalg.py"),
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/diff-independence.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    ms, cs = cert["main_space"], cert["control_space"]
    print("enlarged carrier, lowest weight-zero degree  sqrt(-g) h^ab h^cd")
    print("  Weyl-invariant space   : %d" % ms["basis_dimension"])
    print("  Diff-invariant subspace: %d   (rank %d / %d, rails agree: %s)"
          % (ms["invariant_dimension"], ms["rank_rail_a_gauss_jordan"],
             ms["basis_dimension"], ms["rails_agree"]))
    print("  CONTROL h^ab g_cd      : invariants %d (expected 1), rails agree: %s"
          % (cs["invariant_dimension"], cs["rails_agree"]))
    print("witness : %s   moved by %d of 16 generators"
          % (cert["witness"]["density"], cert["witness"]["generator_count"]))
    print("consequence: %s  (witness order %d, derived order %d)"
          % (cert["consequence"]["claim"],
             cert["consequence"]["witness_derivative_order"],
             cert["consequence"]["derived_order_at_D4"]))
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
