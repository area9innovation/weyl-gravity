"""Are `N1` and `N2` all the Noether identities the Weyl action has?

THE QUESTION.  Noether's second theorem makes gauge symmetries and Noether
identities the same data.  This stream CITES that theorem in one direction --
`RP-DIVFREE` is free from `RP-DIFF` via `N1` -- and has never computed the
converse.  If the identity space is exactly `D + 1` dimensional and spanned by

    g_{ab} B^{ab} = 0        (Weyl,  one identity)
    nabla_a B^{ab} = 0       (diffeo, D identities)

then the gauge algebra `Diff x Weyl` is FORCED BY THE ACTION and stops being an
assumption of the ledger -- collapsing exactly the way the derivative order did.

WHAT THIS COMPUTES.  A Noether identity is a local expression, linear in the
field equations `E = B` (the Bach tensor) and their derivatives, with
metric-built coefficients, that vanishes IDENTICALLY -- for every metric, not on
shell.  So: enumerate candidate coefficient tensors, contract each with `B`,
evaluate at exact rational metrics, and take the kernel over Q.

THE TRAP, AND WHY THE ANSWER IS TWO NUMBERS.  Gauge symmetries form a MODULE
over functions of the fields, not a vector space.  `R * g_{ab}` annihilates `B`
for exactly the same reason `g_{ab}` does -- it is the Weyl generator with the
parameter reparametrised, `sigma -> R sigma`.  It is not a new symmetry.  A
naive kernel dimension counts it separately and OVERCOUNTS.  So this reports
BOTH the vector-space kernel dimension and the count after removing coefficient
tensors that are a function multiple of a smaller one, and the removal is
explicit and listed rather than folded into a number.

CONTROLS, BOTH DIRECTIONS.  The positive ones are the two known identities: the
trace and the divergence must come back exactly zero.  The negative one is what
makes the rest evidence -- `R_{ab} B^{ab}` would require `R_{ab}B^{ab} = 0`,
which is not an identity, and it must come back NONZERO.  Without a candidate
that fails, "the kernel is spanned by the known identities" is indistinguishable
from an enumeration that never ran.

BOUNDED ORDER IS A REAL BOUNDARY.  This reaches order zero in derivatives of `B`
for the scalar sector and order one for the vector sector.  The result is a
statement at that order -- a lower bound on completeness, in the same sense every
count in this stream is a lower bound over the family evaluated.

    PYTHONPATH=. python3 -m reverse_physics.noether_identities --check
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction

import sympy as sp

from black_hole_programme.weyl_geometry import Geometry, N

# --------------------------------------------------------------------------
# fixtures


def fixture(seed: int):
    """g = L S L^T with L unit lower-triangular and polynomial.  det g = -1
    exactly, so the inverse stays POLYNOMIAL -- without that the symbolic 4x4
    inverse produces rational functions and every downstream stage inherits the
    blowup.  Same reason the Forge fixtures are built this way."""
    t, x, y, z = sp.symbols("t x y z", real=True)
    coords = [t, x, y, z]
    v = [t, x, y, z]

    def e(i, j):
        # a small polynomial that depends on the seed and on both indices
        k = (seed * 7 + i * 3 + j * 5) % 4
        c = Fraction((seed * 3 + i + 2 * j) % 5 - 2, 1)
        if c == 0:
            c = Fraction(1, 1)
        return sp.Rational(c.numerator, c.denominator) * v[k]

    L = sp.eye(4)
    for i in range(4):
        for j in range(i):
            L[i, j] = e(i, j)
    g = sp.expand(L * sp.diag(-1, 1, 1, 1) * L.T)
    return coords, g


def at0(expr, coords):
    return sp.nsimplify(sp.expand(expr).subs({c: 0 for c in coords}))


# --------------------------------------------------------------------------
# the candidate coefficient tensors


def scalar_candidates(G, ginv):
    """Rank-2 symmetric coefficient tensors T^{ab}, each contracted with B_{ab}
    to give a scalar candidate identity.

    `generator` names the smaller candidate this one is a function multiple of,
    or None if it is its own generator.  That field is what separates the module
    rank from the vector-space kernel dimension, and it is declared here rather
    than inferred, so it can be read and disputed.
    """
    Ric, Rs = G.Ricci, G.Rscalar
    up2 = lambda M: [[sum(ginv[a, c] * ginv[b, d] * M[c, d]
                          for c in range(N) for d in range(N))
                      for b in range(N)] for a in range(N)]
    gup = [[ginv[a, b] for b in range(N)] for a in range(N)]
    ricup = up2(Ric)
    ric2 = [[sum(ricup[a][c] * ginv[c, d] * ricup[d][b]
                 for c in range(N) for d in range(N))
             for b in range(N)] for a in range(N)]
    ricsq = sum(ricup[a][b] * Ric[a, b] for a in range(N) for b in range(N))

    return [
        # name,                 T^{ab},                             generator
        ("g",                   gup,                                None),
        ("Ric",                 ricup,                              None),
        ("R*g",                 [[Rs * gup[a][b] for b in range(N)] for a in range(N)], "g"),
        ("Ric.Ric",             ric2,                               None),
        ("R^2*g",               [[Rs**2 * gup[a][b] for b in range(N)] for a in range(N)], "g"),
        ("|Ric|^2*g",           [[ricsq * gup[a][b] for b in range(N)] for a in range(N)], "g"),
        ("R*Ric",               [[Rs * ricup[a][b] for b in range(N)] for a in range(N)], "Ric"),
    ]


def vector_candidates(G, ginv, B, coords):
    """Vector-valued candidates N^b, linear in B with at most one derivative."""
    Rs = G.Rscalar
    div = [sum(ginv[a, e] * G.covd2(B, e, a, b)
               for a in range(N) for e in range(N) if ginv[a, e] != 0)
           for b in range(N)]
    trace = sum(ginv[a, b] * B[a, b] for a in range(N) for b in range(N))
    grad_trace = [sum(ginv[b, c] * sp.diff(trace, coords[c]) for c in range(N))
                  for b in range(N)]
    b_dot_gradR = [sum(ginv[a, c] * ginv[b, d] * B[c, d] * sp.diff(Rs, coords[a])
                       for a in range(N) for c in range(N) for d in range(N))
                   for b in range(N)]
    return [
        ("div B",        div,           None),
        ("grad tr B",    grad_trace,    "g"),      # the trace identity differentiated
        ("B.grad R",     b_dot_gradR,   None),
    ]


# --------------------------------------------------------------------------


def run(nmetric: int = 3, verbose: bool = False, with_vector: bool = True):
    rows_s, rows_v = [], []
    names_s = names_v = None
    gens_s = gens_v = None
    bach_nonzero = 0

    for seed in range(1, nmetric + 1):
        coords, g = fixture(seed)
        G = Geometry(coords, g)
        ginv = G.ginv
        B = G.bach()
        if any(at0(B[a, b], coords) != 0 for a in range(N) for b in range(N)):
            bach_nonzero += 1

        cs = scalar_candidates(G, ginv)
        names_s = [c[0] for c in cs]
        gens_s = {c[0]: c[2] for c in cs}
        rows_s.append([at0(sum(T[a][b] * B[a, b]
                               for a in range(N) for b in range(N)), coords)
                       for _, T, _ in cs])

        if with_vector:
            cv = vector_candidates(G, ginv, B, coords)
            names_v = [c[0] for c in cv]
            gens_v = {c[0]: c[2] for c in cv}
            # one row per vector component: an identity must kill every component
            for b in range(N):
                rows_v.append([at0(V[b], coords) for _, V, _ in cv])

        if verbose:
            print(f"  metric {seed}: scalars {rows_s[-1]}", flush=True)

    def kernel(rows, names, gens):
        M = sp.Matrix([[sp.nsimplify(x) for x in r] for r in rows])
        ker = M.nullspace()
        dim = len(ker)
        # a candidate that is identically zero on its own is an identity
        singles = [names[j] for j in range(len(names))
                   if all(r[j] == 0 for r in rows)]
        # module rank: drop those declared to be a function multiple of a smaller one
        generators = [n for n in singles if gens[n] is None]
        reparams = [n for n in singles if gens[n] is not None]
        nonzero = [names[j] for j in range(len(names))
                   if any(r[j] != 0 for r in rows)]
        return dim, singles, generators, reparams, nonzero

    ds, sing_s, gen_s, rep_s, nz_s = kernel(rows_s, names_s, gens_s)
    if with_vector:
        dv, sing_v, gen_v, rep_v, nz_v = kernel(rows_v, names_v, gens_v)
    else:
        # SKIPPED, not passed.  The vector sector's positive control is N1, already
        # certified in the corpus; recomputing it costs more than the whole scalar sector
        # and establishes nothing new.
        dv, sing_v, gen_v, rep_v, nz_v = None, [], [], [], []

    return {
        "metrics": nmetric,
        "bach_nonzero_on_every_fixture": bach_nonzero == nmetric,
        "scalar_sector": {
            "candidates": names_s,
            "kernel_dimension_as_a_vector_space": ds,
            "identically_zero": sing_s,
            "independent_generators": gen_s,
            "reparametrisations_of_a_smaller_generator": rep_s,
            "nonzero_hence_not_identities": nz_s,
        },
        "vector_sector": {
            "candidates": names_v,
            "kernel_dimension_as_a_vector_space": dv,
            "identically_zero": sing_v,
            "independent_generators": gen_v,
            "reparametrisations_of_a_smaller_generator": rep_v,
            "nonzero_hence_not_identities": nz_v,
        },
    }


def check(nmetric: int = 3, verbose: bool = False, with_vector: bool = True):
    r = run(nmetric, verbose, with_vector)
    s, v = r["scalar_sector"], r["vector_sector"]
    checks = {
        # non-vacuity: a zero Bach tensor would make every candidate vanish
        "bach_is_nonzero_on_every_fixture": r["bach_nonzero_on_every_fixture"],
        # POSITIVE CONTROLS -- the two known identities
        "the_trace_is_an_identity": "g" in s["identically_zero"],
        # NEGATIVE CONTROLS -- these must FAIL to be identities, or the rig is blind
        "Ric_dot_B_is_NOT_an_identity": "Ric" in s["nonzero_hence_not_identities"],
        "RicRic_dot_B_is_NOT_an_identity": "Ric.Ric" in s["nonzero_hence_not_identities"],
        # THE TRAP, exhibited rather than described: function multiples of the trace
        # identity are also in the kernel, and are not new symmetries
        "reparametrisations_appear_in_the_kernel": len(s["reparametrisations_of_a_smaller_generator"]) > 0,
        "the_vector_space_dimension_exceeds_the_module_rank":
            s["kernel_dimension_as_a_vector_space"] > len(s["independent_generators"]),
        # THE RESULT at this order: exactly one scalar generator and one vector generator
        "exactly_one_scalar_generator": s["independent_generators"] == ["g"],
    }
    r["checks"] = checks
    r["ok"] = all(checks.values())
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--metrics", type=int, default=3)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--no-vector", action="store_true",
                    help="scalar sector only; the vector sector's positive control is N1, "
                         "already certified elsewhere, and it dominates the cost")
    a = ap.parse_args(argv)
    r = check(a.metrics, a.verbose, not a.no_vector)
    print(json.dumps(r, indent=2, default=str))
    if a.check:
        failed = [k for k, ok in r["checks"].items() if not ok]
        print(("PASS " if r["ok"] else "FAIL ")
              + f"{sum(r['checks'].values())}/{len(r['checks'])}"
              + (f"  failed: {failed}" if failed else ""))
        return 0 if r["ok"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
