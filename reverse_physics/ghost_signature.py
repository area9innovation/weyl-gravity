"""Inertia (1,2): the criterion survives, and "harmless" does not mean "no ghost".

WHY THIS EXISTS.  REVERSE_PHYSICS_GHOST_HARMLESS_V1 showed that on the MINIMAL
ghost -- inertia (1,1) -- the three routes usually offered as alternative escapes
collapse to one condition, DIAGONALIZABLE AND REAL SPECTRUM.  Its own boundary
said "not higher inertia", and (1,2) is not an arbitrary next case: it is where
this repository's black-hole programme actually works.  `lh_assembly` records
`inertia(G_-) = inertia(H_out) = (1,2,0)`, and `scattering_c_factorisation`
states the pencil criterion there.  So the question is whether the (1,1) finding
was a small-dimension accident.

THE PARAMETERISATION IS CLEAN.  With eta = diag(1,-1,-1), eta-pseudo-Hermiticity
H^dag eta = eta H says exactly that eta H is Hermitian, so

    H = eta M,   M Hermitian

covers every case with no further conditions.  That is worth noting because at
(1,1) the family had to be written by hand; here the structure supplies it.

WHAT SURVIVES.  The criterion.  A positive-definite J with H^dag J = J H makes
rho = J^(1/2) conjugate H to a Hermitian operator, so H is diagonalizable with
real spectrum -- the same one-line argument as at (1,1), and it does not know the
dimension.  Verified on three cases: diagonalizable with real spectrum admits an
explicit positive J; a complex-conjugate pair and a degenerate non-diagonalizable
case do not.

WHAT IS NEW, AND IT IS THE POINT.  In the HARMLESS case the eta-norms of the
eigenvectors are

    [ +1, -1, -1 ]

TWO NEGATIVE-NORM DIRECTIONS SURVIVE.  The inertia is preserved in the
eigenbasis -- it has to be, being an invariant of eta -- and the criterion cannot
see it.  Quasi-Hermiticity says A POSITIVE INNER PRODUCT EXISTS; it says nothing
about how many directions were negative in the ORIGINAL one.  At (1,1) there was
exactly one ghost mode and the distinction was invisible, because "a ghost" and
"one ghost" coincide.  At (1,2) they come apart.

So the honest reading of the (1,1) result changes:

    "harmless"  means  A POSITIVE-DEFINITE INNER PRODUCT EXISTS
    it does NOT mean   THE GHOST IS GONE

and the ghost COUNT is an eta-invariant that no amount of quasi-Hermiticity
removes.  Whether replacing eta by J is physically legitimate is exactly the
Bender--Mannheim question, and it is a physics question this module does not
answer -- but it is now visibly the question, rather than being hidden by a
dimension in which it could not be asked.

WHAT THIS DOES NOT ESTABLISH.  Still finite-dimensional linear algebra, now on a
three-dimensional Krein space.  It does not say whether Weyl gravity's ghost
satisfies the criterion, and C-GHOST-DYNAMICS stays OPEN.  The POSITIVE direction
is constructive -- a positive J is exhibited -- while the NEGATIVE direction rests
on the one-line argument above rather than on an exhaustive search, and the grid
search is reported as corroboration, not proof.  This module imports nothing.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.ghost_signature --check
    PYTHONPATH=. python3 -m reverse_physics.ghost_signature --emit
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
    "REVERSE_PHYSICS_GHOST_SIGNATURE_V1.json",
)

ETA = sp.diag(1, -1, -1)          # inertia (1,2): the black-hole programme's
N = 3


def hamiltonian(M):
    """eta-pseudo-Hermiticity is exactly 'eta H is Hermitian', so H = eta M
    with M Hermitian covers every case."""
    return sp.simplify(ETA * M)


def is_pseudo_hermitian(H):
    return sp.simplify(H.T.conjugate() * ETA - ETA * H) == sp.zeros(N, N)


def intertwiners(H):
    """Hermitian J with H^dag J = J H."""
    j = sp.symbols("j0:9", real=True)
    J = sp.Matrix([[j[0], j[3] + sp.I * j[4], j[5] + sp.I * j[6]],
                   [j[3] - sp.I * j[4], j[1], j[7] + sp.I * j[8]],
                   [j[5] - sp.I * j[6], j[7] - sp.I * j[8], j[2]]])
    eqs = sp.Matrix(H.T.conjugate() * J - J * H)
    conds = [sp.simplify(sp.re(e)) for e in eqs] \
        + [sp.simplify(sp.im(e)) for e in eqs]
    conds = [c for c in conds if c != 0]
    if not conds:
        return J, sorted(J.free_symbols, key=str)
    sol = sp.solve(conds, list(j), dict=True)
    if not sol:
        return None, []
    Js = sp.simplify(J.subs(sol[0]))
    return Js, sorted(Js.free_symbols, key=str)


def positive_definite_witness(J, free, bound=3):
    """Exhibit a positive-definite element, or return None.

    Finding one is CONSTRUCTIVE.  Failing to find one is NOT a proof of absence
    -- the absence argument is the one-line similarity argument in the module
    docstring -- and the certificate says so.
    """
    if J is None:
        return None
    if not free:
        cand = [J]
    else:
        import itertools
        cand = []
        for vals in itertools.product(range(-bound, bound + 1),
                                      repeat=len(free)):
            cand.append(J.subs(dict(zip(free, vals))))
    for K in cand:
        try:
            m1 = sp.simplify(K[0, 0])
            m2 = sp.simplify((K[:2, :2]).det())
            m3 = sp.simplify(K.det())
        except Exception:                                  # pragma: no cover
            continue
        if all(m.is_number and m > 0 for m in (m1, m2, m3)):
            return {"J": str(K.tolist()),
                    "minors": [str(m1), str(m2), str(m3)]}
    return None


def eta_signature(H):
    """The eta-norms of the eigenvectors: the ghost COUNT, which is an
    invariant of eta and not of the criterion."""
    signs = []
    for r in sp.roots(H.charpoly().as_expr()):
        for v in (H - r * sp.eye(N)).nullspace():
            n = sp.simplify((v.T.conjugate() * ETA * v)[0, 0])
            signs.append(int(sp.sign(n)))
    return sorted(signs, reverse=True)


CASES = [
    ("diagonalizable_real", sp.diag(1, 2, 3), True),
    ("complex_pair", sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 1]]), False),
    ("degenerate", sp.Matrix([[1, 1, 0], [1, 1, 0], [0, 0, 1]]), False),
]


def analyse(name, M, expected_harmless):
    H = hamiltonian(M)
    roots = sp.roots(H.charpoly().as_expr())
    real = all(sp.im(r) == 0 for r in roots)
    diagble = H.is_diagonalizable()
    J, free = intertwiners(H)
    witness = positive_definite_witness(J, free)
    harmless = witness is not None
    row = {
        "case": name,
        "H": str(H.tolist()),
        "is_pseudo_hermitian": is_pseudo_hermitian(H),
        "spectrum": [str(r) for r in roots],
        "real_spectrum": bool(real),
        "diagonalizable": bool(diagble),
        "intertwiner_free_parameters": len(free),
        "positive_definite_witness": witness,
        "harmless": harmless,
        "expected_harmless": expected_harmless,
        "matches_criterion": harmless == (bool(diagble) and bool(real)),
    }
    if harmless:
        row["eta_signature_of_eigenbasis"] = eta_signature(H)
    return row


def build():
    rows = [analyse(*c) for c in CASES]
    by = {r["case"]: r for r in rows}
    harmless_row = by["diagonalizable_real"]
    signature = harmless_row.get("eta_signature_of_eigenbasis")

    checks = {
        "every_case_is_pseudo_hermitian":
            all(r["is_pseudo_hermitian"] for r in rows),
        "the_criterion_holds_at_inertia_1_2":
            all(r["matches_criterion"] for r in rows),
        "each_case_is_the_expected_one":
            all(r["harmless"] == r["expected_harmless"] for r in rows),
        "the_harmless_case_exhibits_a_positive_charge":
            harmless_row["positive_definite_witness"] is not None,
        "both_outcomes_occur":
            len({r["harmless"] for r in rows}) == 2,
        # the finding
        "two_negative_norm_directions_survive_in_the_harmless_case":
            signature is not None and signature.count(-1) == 2,
        "the_eta_inertia_is_preserved_in_the_eigenbasis":
            signature == [1, -1, -1],
        "the_criterion_is_blind_to_the_ghost_count":
            harmless_row["harmless"] and signature.count(-1) > 0,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_GHOST_SIGNATURE_V1",
        "kind": "extension",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "The harmlessness criterion -- diagonalizable AND real spectrum -- "
            "survives at inertia (1,2), which is where this repository's "
            "black-hole programme actually works (lh_assembly records "
            "inertia (1,2,0); scattering_c_factorisation states the pencil "
            "criterion there).  So the (1,1) result was not a small-dimension "
            "accident.  AND THE NEW CONTENT: in the harmless case the "
            "eta-norms of the eigenvectors are [+1,-1,-1] -- TWO "
            "NEGATIVE-NORM DIRECTIONS SURVIVE.  Quasi-Hermiticity says a "
            "positive inner product EXISTS; it says nothing about how many "
            "directions were negative in the original one.  So 'harmless' "
            "means a positive-definite inner product exists, NOT that the "
            "ghost is gone, and the ghost COUNT is an eta-invariant no amount "
            "of quasi-Hermiticity removes.  At (1,1) the distinction was "
            "invisible because 'a ghost' and 'one ghost' coincide; at (1,2) "
            "they come apart.",
        "does_not_establish": [
            "whether replacing eta by J is physically legitimate.  That is the "
            "Bender--Mannheim question and it is a PHYSICS question this "
            "module does not answer -- but it is now visibly the question, "
            "rather than hidden by a dimension in which it could not be asked",
            "anything about Weyl gravity's field-theoretic ghost.  Still "
            "finite-dimensional linear algebra, now on a three-dimensional "
            "Krein space.  C-GHOST-DYNAMICS stays OPEN",
            "the NEGATIVE direction by exhaustion.  A positive J is EXHIBITED "
            "where one exists, which is constructive; where none exists the "
            "argument is that a positive J would conjugate H to a Hermitian "
            "operator, forcing diagonalizability and real spectrum, and the "
            "grid search is reported as corroboration rather than proof",
            "inertia beyond (1,2), or the infinite-dimensional case where "
            "quasi-Hermiticity additionally needs the metric bounded with "
            "bounded inverse",
        ],
        "setting": {
            "krein_metric": "eta = diag(1,-1,-1), inertia (1,2)",
            "parameterisation": "eta-pseudo-Hermiticity says exactly that "
                                "eta H is Hermitian, so H = eta M with M "
                                "Hermitian covers every case with no further "
                                "conditions",
            "why_this_inertia": "lh_assembly records inertia(G_-) = "
                                "inertia(H_out) = (1,2,0), and "
                                "scattering_c_factorisation states the pencil "
                                "criterion there.  Cited as context; this "
                                "module imports nothing",
        },
        "cases": rows,
        "the_finding": {
            "eta_signature_in_the_harmless_case": signature,
            "reading": "'harmless' means A POSITIVE-DEFINITE INNER PRODUCT "
                       "EXISTS.  It does NOT mean THE GHOST IS GONE.  The "
                       "ghost count is an eta-invariant the criterion cannot "
                       "see",
            "why_it_was_invisible_at_1_1": "with one negative direction, 'a "
                                           "ghost' and 'one ghost' coincide",
        },
        "imports": "none",
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/ghost-signature.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("eta = diag(1,-1,-1), inertia (1,2);  H = eta M, M Hermitian")
    for r in cert["cases"]:
        print("  %-20s real=%-5s diag=%-5s harmless=%-5s %s"
              % (r["case"], r["real_spectrum"], r["diagonalizable"],
                 r["harmless"],
                 ("eta-signature %s" % r["eta_signature_of_eigenbasis"])
                 if r.get("eta_signature_of_eigenbasis") else ""))
    f = cert["the_finding"]
    print("FINDING: %s" % f["reading"])
    print("checks %d/%d" % (cert["checks"]["passed"], cert["checks"]["total"]))
    for x in cert["checks"]["failures"]:
        print("FAIL %s" % x)

    if args.emit and cert["checks"]["ok"]:
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    print("RESULT: %s" % ("PASS" if cert["checks"]["ok"] else "FAIL"))
    return 0 if cert["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
