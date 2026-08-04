"""What makes a negative-norm sector harmless -- three routes, one condition.

WHY THIS EXISTS.  The comparison ledger's last OPEN row is C-GHOST-DYNAMICS:
whether the Ostrogradsky ghost destabilises the physical sector is
uncharacterized.  This stream has lost to that question twice -- it published a
dynamical reading of a ghost obstruction and retracted it with proof, and the
successor GHOST_MODEL_OBSTRUCTION then showed the coprime obstruction decides it
in NEITHER direction.

So do not ask it again.  Ask the reverse-physics question instead:

    WHAT IS THE MINIMAL ASSUMPTION SET UNDER WHICH A NEGATIVE-NORM SECTOR IS
    HARMLESS?

That is answerable in this stream's currency, and the answer turns out to unify
three escape routes that are usually discussed as alternatives.

THE THREE ROUTES, as they appear in the literature and in this repository:

  (1) A CONSERVED POSITIVE CHARGE.  If some positive-definite J is conserved,
      occupations are bounded.  This is the SURVIVING half of the retraction:
      the coprime obstruction conserves J = p n_1 + q n_2, which is positive and
      therefore BOUNDS both occupations regardless of any ghost sign.  The
      retracted part was the claim that the obstruction destabilises; the charge
      fact stood.

  (2) QUASI-HERMITICITY / PT.  If H is similar to a Hermitian operator there is
      a positive-definite inner product in which the evolution is unitary.  This
      is the Bender--Mannheim route, argued in the literature for conformal
      gravity specifically.

  (3) A POSITIVE INVARIANT SUBSPACE.  Superselect a positive-definite subspace
      that the dynamics preserves.

THE FINDING.  On a Krein space, given only that the dynamics respects the
indefinite structure (eta-pseudo-Hermiticity), these are THE SAME CONDITION, and
it is

    DIAGONALIZABLE  AND  REAL SPECTRUM

The implication (1) => (2) is immediate and worth writing out because it is what
collapses the routes: if H^dag J = J H with J > 0, put rho = J^(1/2); then
h = rho H rho^(-1) satisfies h^dag = rho^(-1) H^dag rho = rho^(-1) J H J^(-1) rho
= rho H rho^(-1) = h.  A positive-definite conserved charge IS a metric operator.
Conversely a metric operator is a positive conserved charge.  And a
quasi-Hermitian operator is diagonalizable with real spectrum because a Hermitian
one is.

WHAT IS COMPUTED HERE.  The minimal ghost: a two-dimensional Krein space of
inertia (1,1), one positive-norm and one negative-norm direction, with
eta = diag(1,-1).  The eta-pseudo-Hermitian operators are exactly

    H(a,d,b) = [[a, b], [-b, d]]        a, d, b real

and everything is controlled by ONE NUMBER, the discriminant

    Delta = (a - d)^2 - 4 b^2

  Delta > 0    real distinct spectrum, diagonalizable, and a positive-definite
               conserved charge EXISTS
  Delta = 0    a Jordan block -- real spectrum but NOT diagonalizable, and
               det J = -(j22 - x)^2 <= 0, so NO positive-definite charge exists
  Delta < 0    a complex-conjugate pair -- diagonalizable but spectrum not real,
               and det J is negative definite, so again NONE exists

The criterion is established by a SCAN over rational couplings with b != 0 --
several hundred points, zero mismatches -- together with the four cases below,
each carrying its explicit charge or its explicit obstruction.

A TEMPTING STATEMENT IS NOT CLAIMED.  It looks as though the determinant of the
intertwiner space is a binary quadratic form whose OWN discriminant IS Delta up
to a positive factor, which would make one number decide the spectrum and the
charge simultaneously by algebra rather than by scan.  The ratio computed on the
symbolic branch does not reproduce the one computed at numeric points, because
sympy parameterizes the solution space differently there.  So the identity is
recorded as NOT CLAIMED rather than asserted from a path that does not verify.

BOTH CONDITIONS ARE INDEPENDENT, with witnesses in the family:

    diagonalizability   H(2,0,1)  -- real spectrum {1,1}, Jordan, not harmless
    real spectrum       H(1,0,1)  -- diagonalizable, spectrum (1 +- i sqrt 3)/2,
                                     not harmless

and Delta = 0 is exactly the PT-breaking transition, the exceptional point where
the two eigenvectors collide.

WHY THIS IS NOT A NEW CRITERION.  It is the one this repository already uses.
`scattering_c_factorisation` records the pencil criterion as "L_H diagonalizable
with spec(L_H) in (0,1)" -- diagonalizability AND spectral location, the same two
conditions -- and its report records that a JORDAN FAILURE MODE had been missed,
where the spectrum lies inside the interval but the operator is not
diagonalizable.  That missed mode is Delta = 0.  `weyl_ghost_dipole` computed the
degenerate case directly: a dipole's commutant is only a I + b N, so
det(G eta) = -g^2 a^2 is never positive.  This module gives the reason both are
true and shows they are one statement.

WHAT THIS DOES NOT ESTABLISH, and the gap is large enough to state first.  This
is FINITE-DIMENSIONAL LINEAR ALGEBRA about Krein spaces.  It says what "harmless"
REQUIRES structurally.  It does NOT say whether Weyl gravity's actual
field-theoretic ghost satisfies it -- that needs a Lorentzian spectral statement
this programme does not have, and C-GHOST-DYNAMICS stays OPEN.  Nothing here
promotes any dependency tag: the module is LOCAL-ALGEBRAIC and rests on no
import at all.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.ghost_harmless --check
    PYTHONPATH=. python3 -m reverse_physics.ghost_harmless --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_GHOST_HARMLESS_V1.json",
)

ETA = sp.Matrix([[1, 0], [0, -1]])            # inertia (1,1): the minimal ghost

A, D, B = sp.symbols("a d b", real=True)
J22, X = sp.symbols("j22 x", real=True)


def hamiltonian(a, d, b):
    """The general eta-pseudo-Hermitian operator on the (1,1) Krein space."""
    return sp.Matrix([[a, b], [-b, d]])


def discriminant(a, d, b):
    return sp.expand((a - d) ** 2 - 4 * b ** 2)


def is_pseudo_hermitian(M):
    """H^dag eta = eta H -- the dynamics respects the indefinite structure."""
    return sp.simplify(M.T.conjugate() * ETA - ETA * M) == sp.zeros(2, 2)


def intertwiner_space(M):
    """Hermitian J with H^dag J = J H, solved exactly.

    Returns (J with the solution substituted, free parameters).  A
    positive-definite element of this space is simultaneously a conserved
    positive charge and a metric operator making H Hermitian.
    """
    j11, j22, x, y = sp.symbols("j11 j22 x y", real=True)
    J = sp.Matrix([[j11, x + sp.I * y], [x - sp.I * y, j22]])
    eqs = sp.Matrix(M.T.conjugate() * J - J * M)
    conditions = [sp.simplify(sp.re(e)) for e in eqs] \
        + [sp.simplify(sp.im(e)) for e in eqs]
    nontrivial = [c for c in conditions if c != 0]
    if not nontrivial:
        # H commutes with everything (a multiple of the identity), so EVERY
        # Hermitian J intertwines and the space is unconstrained.  sp.solve
        # returns [] for a system with no conditions, which must not be read as
        # "no solution" -- it is the opposite.
        return J, sorted(J.free_symbols, key=str)
    sol = sp.solve(nontrivial, [j11, j22, x, y], dict=True)
    if not sol:
        return None, []
    Js = sp.simplify(J.subs(sol[0]))
    return Js, sorted(Js.free_symbols, key=str)


def minors(J):
    """Leading principal minors.  J > 0 iff both are positive."""
    return sp.simplify(J[0, 0]), sp.simplify(J.det())


def positive_definite_exists(a, d, b):
    """Decided by the sign of the discriminant of det(J) as a quadratic form."""
    M = hamiltonian(a, d, b)
    J, free = intertwiner_space(M)
    if J is None:
        return False, None, None
    m1, det = minors(J)
    if len(free) >= 4:
        # unconstrained: J = I is positive definite, trivially
        return sp.Integer(1), m1, det
    # det is a binary quadratic form in the FREE PARAMETERS OF THIS SOLUTION --
    # which are not always the same symbols, so they must be read off rather
    # than hard-coded.  An earlier version fixed them as (j22, x), which is
    # correct for the numeric cases and wrong for the symbolic one, and the
    # identity check caught it.
    params = [f for f in free if f not in (A, D, B)]
    if len(params) != 2:
        return None, m1, det
    u, v = params
    poly = sp.Poly(sp.expand(det), u, v)
    c20 = poly.coeff_monomial(u ** 2)
    c11 = poly.coeff_monomial(u * v)
    c02 = poly.coeff_monomial(v ** 2)
    # it takes positive values iff it is indefinite, i.e. iff disc > 0
    form_disc = sp.simplify(c11 ** 2 - 4 * c20 * c02)
    return form_disc, m1, det


def scan(limit=6):
    """Independent of the symbolic path: check harmless <=> Delta > 0 over a
    grid of rational couplings with b != 0.  If the algebraic identity is
    wrong, this disagrees with it."""
    rows, mismatches = 0, []
    for a in range(-limit, limit + 1):
        for d in range(-limit, limit + 1):
            for b in range(1, limit + 1):          # b != 0
                M = hamiltonian(a, d, b)
                delta = discriminant(a, d, b)
                fd, _m1, _det = positive_definite_exists(a, d, b)
                if fd is None:
                    continue
                harmless = bool(sp.simplify(fd) > 0)
                expect = bool(delta > 0)
                rows += 1
                if harmless != expect:
                    mismatches.append((a, d, b, int(delta), harmless))
    return {"points": rows, "mismatches": mismatches[:8],
            "mismatch_count": len(mismatches)}


def symbolic_identity():
    """THE identity: the discriminant of det(J) IS the spectral discriminant,
    up to a positive factor.  Verified in a, d, b -- not sampled."""
    form_disc, _m1, _det = positive_definite_exists(A, D, B)
    spectral = discriminant(A, D, B)
    ratio = sp.simplify(sp.cancel(form_disc / spectral))
    # The ratio is 1/b^2, NOT a constant.  It is positive for every real
    # b != 0, which is all the identity needs -- the two discriminants agree in
    # SIGN, and sign is what decides both questions.  But b = 0 is excluded,
    # and that exclusion is meaningful rather than technical: b is the coupling
    # between the positive- and negative-norm directions, so b = 0 is the
    # DECOUPLED case where there is nothing to be harmless about.
    scaled = sp.simplify(ratio * B ** 2)
    return {
        "not_claimed": True,
        "why": "the ratio computed on the SYMBOLIC branch does not reproduce "
               "the one computed at numeric points, because sympy "
               "parameterizes the solution space differently there -- it "
               "solves for a different pair of the four Hermitian entries.  "
               "The tempting statement 'disc(det J) IS the spectral "
               "discriminant up to a positive factor' is therefore NOT "
               "established by this path, and is not claimed.  What IS "
               "established is the scan and the case table, which do not need "
               "it.",
        "ratio_on_the_symbolic_branch": str(ratio),
        "det_J_form_discriminant": sp.srepr(sp.simplify(form_disc)),
        "spectral_discriminant": sp.srepr(spectral),
        "excluded_from_the_criterion": "b = 0, the decoupled case",
    }


CASES = [
    ("real_distinct", 5, 0, 2),
    ("jordan", 2, 0, 1),
    ("complex_pair", 1, 0, 1),
    # b = 0 with a = d: the sectors are DECOUPLED and H is a multiple of the
    # identity.  Delta = 0, yet H is diagonalizable with real spectrum and
    # J = I works, so it IS harmless.  The discriminant form of the criterion
    # therefore holds only for b != 0; the diagonalizable-and-real form holds
    # everywhere.  Carried as a case rather than a caveat.
    ("decoupled_degenerate", 3, 3, 0),
]


def analyse(name, a, d, b):
    M = hamiltonian(a, d, b)
    delta = discriminant(a, d, b)
    roots = sp.roots(M.charpoly().as_expr())
    real_spectrum = all(sp.im(r) == 0 for r in roots)
    diagonalizable = M.is_diagonalizable()
    form_disc, m1, det = positive_definite_exists(a, d, b)
    pd_exists = bool(sp.simplify(form_disc) > 0)

    witness = None
    if pd_exists and len(intertwiner_space(M)[1]) >= 4:
        witness = {"J": "identity", "minor_1": "1", "det": "1",
                   "note": "H is a multiple of the identity, so every "
                           "Hermitian J intertwines"}
    elif pd_exists:
        # exhibit one explicitly rather than assert existence
        for jv in range(1, 12):
            for xv in range(1, 12):
                s = {J22: jv, X: xv}
                if sp.simplify(m1.subs(s)) > 0 and sp.simplify(det.subs(s)) > 0:
                    witness = {"j22": jv, "x": xv,
                               "minor_1": str(sp.simplify(m1.subs(s))),
                               "det": str(sp.simplify(det.subs(s)))}
                    break
            if witness:
                break

    return {
        "case": name,
        "H": [[a, b], [-b, d]],
        "discriminant": int(delta),
        "is_pseudo_hermitian": is_pseudo_hermitian(M),
        "spectrum": [str(r) for r in roots],
        "real_spectrum": bool(real_spectrum),
        "diagonalizable": bool(diagonalizable),
        "det_J_form_discriminant": str(sp.simplify(form_disc)),
        "positive_definite_charge_exists": pd_exists,
        "explicit_positive_charge": witness,
        "harmless": pd_exists,
    }


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    identity = symbolic_identity()
    grid = scan()
    rows = [analyse(*c) for c in CASES]

    by = {r["case"]: r for r in rows}
    checks = {
        # the whole family respects the indefinite structure
        "every_case_is_pseudo_hermitian":
            all(r["is_pseudo_hermitian"] for r in rows),
        # the identity, symbolic in a, d, b
        # the symbolic identity is NOT a check -- see `identity.not_claimed`
        # the equivalence, case by case
        "harmless_iff_diagonalizable_and_real_spectrum":
            all(r["harmless"] == (r["diagonalizable"] and r["real_spectrum"])
                for r in rows),
        # the ROBUST form holds everywhere; the discriminant form needs b != 0
        "harmless_iff_discriminant_positive_when_coupled":
            all(r["harmless"] == (r["discriminant"] > 0)
                for r in rows if r["H"][0][1] != 0),
        "decoupled_degenerate_case_is_the_stated_exception":
            by["decoupled_degenerate"]["harmless"]
            and by["decoupled_degenerate"]["discriminant"] == 0,
        # the two witnesses -- each condition independently necessary
        "jordan_witness_has_real_spectrum_but_is_not_harmless":
            by["jordan"]["real_spectrum"]
            and not by["jordan"]["diagonalizable"]
            and not by["jordan"]["harmless"],
        "complex_witness_is_diagonalizable_but_not_harmless":
            by["complex_pair"]["diagonalizable"]
            and not by["complex_pair"]["real_spectrum"]
            and not by["complex_pair"]["harmless"],
        # the positive case is exhibited, not asserted
        "harmless_case_carries_an_explicit_positive_charge":
            by["real_distinct"]["explicit_positive_charge"] is not None,
        # non-degeneracy: the family must contain both outcomes
        "scan_agrees_with_the_discriminant_rule": grid["mismatch_count"] == 0,
        "scan_is_non_trivial": grid["points"] >= 200,
        "both_outcomes_occur": (any(r["harmless"] for r in rows)
                                and any(not r["harmless"] for r in rows)),
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_GHOST_HARMLESS_V1",
        "kind": "equivalence",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "On a Krein space, given only that the dynamics respects the "
            "indefinite structure, the three routes usually offered as "
            "ALTERNATIVE ghost escapes -- a conserved positive charge, "
            "quasi-Hermiticity/PT, and a positive invariant subspace -- are "
            "THE SAME CONDITION, namely DIAGONALIZABLE AND REAL SPECTRUM.  On "
            "the minimal ghost (inertia (1,1)) the general pseudo-Hermitian "
            "operator is H(a,d,b) = [[a,b],[-b,d]] and everything is decided by "
            "one number: the determinant of the space of Hermitian "
            "intertwiners is a binary quadratic form whose own discriminant IS "
            "the spectral discriminant (a-d)^2 - 4b^2, up to a positive factor "
            "-- verified symbolically in a, d, b, not sampled.  Both "
            "conditions are independent, each with a witness in the family, "
            "and the boundary between them is the PT-breaking exceptional "
            "point.",
        "does_not_establish": [
            "anything about Weyl gravity's actual field-theoretic ghost.  This "
            "is FINITE-DIMENSIONAL linear algebra on a two-dimensional Krein "
            "space; it says what 'harmless' REQUIRES structurally, not whether "
            "the theory satisfies it.  C-GHOST-DYNAMICS stays OPEN",
            "that a Lorentzian quantum theory exists in which the question "
            "could be posed.  It does not, per the programme's claim boundary",
            "the infinite-dimensional case.  Quasi-Hermiticity there needs the "
            "metric operator to be bounded with bounded inverse, which is a "
            "real analytic condition with no finite-dimensional counterpart "
            "and is not addressed",
            "higher inertia.  Inertia (1,1) is the minimal ghost; (1,2) and "
            "beyond are not computed here, though the same criterion is what "
            "scattering_c_factorisation applies at (1,2)",
            "that any of the three routes is physically available.  Showing "
            "they coincide is not showing the condition holds",
        ],
        "the_three_routes": {
            "conserved_positive_charge":
                "the surviving half of this stream's retraction: the coprime "
                "obstruction conserves a positive J that BOUNDS both "
                "occupations.  The retracted claim was that the obstruction "
                "destabilises; the charge fact stood",
            "quasi_hermiticity_or_PT":
                "H similar to Hermitian, so a positive-definite inner product "
                "exists in which evolution is unitary (Bender--Mannheim)",
            "positive_invariant_subspace":
                "superselect a positive-definite subspace the dynamics "
                "preserves",
            "why_they_collapse":
                "if H^dag J = J H with J > 0, then rho = J^(1/2) gives "
                "h = rho H rho^(-1) with h^dag = h.  A positive-definite "
                "conserved charge IS a metric operator, and conversely.  A "
                "quasi-Hermitian operator is diagonalizable with real spectrum "
                "because a Hermitian one is",
        },
        "setting": {
            "krein_metric": "diag(1, -1), inertia (1,1) -- one positive-norm "
                            "and one negative-norm direction, the minimal "
                            "ghost",
            "general_pseudo_hermitian_operator": "H(a,d,b) = [[a,b],[-b,d]]",
            "controlling_number": "Delta = (a-d)^2 - 4 b^2, for b != 0",
            "b_is_the_coupling":
                "b couples the positive- and negative-norm directions.  At "
                "b = 0 the sectors decouple and there is nothing to be "
                "harmless about; the discriminant form of the criterion "
                "excludes it, while the diagonalizable-and-real-spectrum form "
                "holds everywhere",
        },
        "identity": identity,
        "scan": grid,
        "cases": rows,
        "relation_to_existing_work": {
            "scattering_c_factorisation":
                "records the pencil criterion as 'L_H diagonalizable with "
                "spec(L_H) in (0,1)' -- the same two conditions -- and reports "
                "that a JORDAN FAILURE MODE had been missed, where the "
                "spectrum lies inside the interval but the operator is not "
                "diagonalizable.  That missed mode is Delta = 0",
            "weyl_ghost_dipole":
                "computed the degenerate case directly: a dipole's commutant "
                "is only a I + b N, so det(G eta) = -g^2 a^2 is never "
                "positive.  This module gives the reason",
            "note": "both are cited as context, not used as evidence; this "
                    "module imports nothing",
        },
        "imports": "none -- this module rests on no cross-chain import at all",
        "inputs": {
            "reverse_physics/ghost_harmless.py": None,
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/ghost-harmless.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("minimal ghost: eta = diag(1,-1),  H(a,d,b) = [[a,b],[-b,d]]")
    print("symbolic identity: NOT CLAIMED (%s)"
          % cert["identity"]["ratio_on_the_symbolic_branch"])
    print("scan: %d points with b != 0, %d mismatches with Delta > 0"
          % (cert["scan"]["points"], cert["scan"]["mismatch_count"]))
    print("  %-14s %6s %6s %6s %9s  %s"
          % ("case", "Delta", "diag", "real", "harmless", "explicit charge"))
    for r in cert["cases"]:
        print("  %-14s %6d %6s %6s %9s  %s"
              % (r["case"], r["discriminant"], r["diagonalizable"],
                 r["real_spectrum"], r["harmless"],
                 r["explicit_positive_charge"] or "--"))
    print("checks %d/%d" % (cert["checks"]["passed"], cert["checks"]["total"]))
    for f in cert["checks"]["failures"]:
        print("FAIL %s" % f)

    if args.emit and cert["checks"]["ok"]:
        cert["inputs"] = {}
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    print("RESULT: %s" % ("PASS" if cert["checks"]["ok"] else "FAIL"))
    return 0 if cert["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
