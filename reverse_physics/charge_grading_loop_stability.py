"""Does a loop generate positive charge?  No -- because the propagator is off-diagonal.

WHY THIS EXISTS.  Bateman-Turok's positivity proof (arXiv:2607.00096) rests on
one hypothesis: "the R_t homomorphism does not yield any positively charged
operators", so the strictly-negatively-charged part is null in the trace.  They
prove positivity at TREE LEVEL and name their own obstacle to going further --
"like QCD, the massless theory has collinear infrared divergences which affect
asymptotic states".

Before any of that infrared work is worth doing, one cheaper question can kill
the whole route: IS THE HYPOTHESIS EVEN STABLE UNDER LOOPS?  If a one-loop
process operator acquires a positive-charge component, their mechanism fails at
loop level whatever regulator is chosen, and the extension is dead on arrival.

THE ANSWER IS NO, AND THE REASON IS STRUCTURAL RATHER THAN NUMERICAL.  Two facts
about the O(1,1) model, both read off their Eq. (14) and their Wightman
function:

  (1) THE VERTEX IS CHARGE NEUTRAL.  S_{1,1} = int [ dOmega dUpsilon
      + (1/2) lambda^2 Omega^2 Upsilon^2 ], and with q(Omega) = +1,
      q(Upsilon) = -1 under the SO+(1,1) scaling
      (Omega, Upsilon) -> (e^s Omega, e^-s Upsilon), the quartic vertex carries
      q = 2(+1) + 2(-1) = 0.

  (2) THE PROPAGATOR IS PURELY OFF-DIAGONAL.  The kinetic term is
      dOmega.dUpsilon, so the quadratic form in the basis (Omega, Upsilon) is
      [[0,1],[1,0]], whose inverse is again [[0,1],[1,0]].  Their Wightman
      function says the same thing: W^{OmegaUpsilon} = W^{UpsilonOmega} =
      theta(p0) delta(p^2) while W^{OmegaOmega} = W^{UpsilonUpsilon} = 0.
      So EVERY Wick contraction pairs one Omega with one Upsilon and therefore
      carries q = 0.

Vertices neutral and contractions neutral together give the grading theorem:

    THE CHARGE OF A PROCESS OPERATOR IS FIXED BY ITS EXTERNAL LEGS AND IS
    INDEPENDENT OF LOOP ORDER.

Loops dress an operator; they cannot move it up the charge ladder.  So a
tree-level image with charges <= 0 stays at charges <= 0 to all orders, and the
one-sidedness hypothesis is loop-stable.  The obstacle to the loop extension is
therefore EXACTLY the infrared one Bateman-Turok named, and nothing else in the
charge sector.

WHAT THAT BUYS, ON THE REGULATOR QUESTION.  Paper 05 records the mass splitting
of the regulated split theory as m_pm^2 = mu^2 +/- sqrt(eps g), for the
regulated Lagrangian carrying an IR mass mu^2 Omega Upsilon and a regulator
(eps/2) Omega^2.  Those two terms are not interchangeable, and the difference is
visible in one line of charge arithmetic:

    q(Omega Upsilon) =  0   -> preserves the grading; and at eps = 0 the two
                               poles COINCIDE at mu^2, so the degeneracy that
                               makes this a Jordan-block theory survives
    q(Omega^2)       = +2   -> breaks the grading, which is why cprop:embedding
                               finds one-sidedness "exact iff eps = 0"; and it
                               SPLITS the poles by 2 sqrt(eps g), destroying the
                               degeneracy as well

One parameter, both damages, for one reason.  So mu^2 Omega Upsilon is a
degeneracy-preserving, grading-preserving infrared mass -- which is the kind of
regulator the loop extension needs and which Bateman-Turok describe as not yet
supplied.  This module does not carry out that extension; it establishes that
the charge sector does not stand in its way.

WHERE THE RISK ACTUALLY SITS, now that charge counting is cleared.  The grading
argument is classical bookkeeping and assumes the SO+(1,1) charge survives
quantization.  It is a GLOBAL symmetry, and global symmetries can be anomalous.
Bateman-Turok themselves flag that the phi and (Omega, Upsilon) path integrals
are inequivalent -- "the former integrates over Omega > 0 whereas the latter
integrates over all Omega" -- so the measure is exactly where such an anomaly
would live.  IS THE O(1,1) BOOST CHARGE ANOMALOUS AT ONE LOOP?  That is the
successor question, it is not answered here, and it is answerable with the
anomaly machinery this repository already has.

Dependency tag: LOCAL-ALGEBRAIC.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from fractions import Fraction

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json")

OM, UP = "Omega", "Upsilon"
CHARGE = {OM: 1, UP: -1}
VERTEX = (OM, OM, UP, UP)                 # their Eq. (14) quartic


def charge(fields) -> int:
    return sum(CHARGE[f] for f in fields)


def contractions_allowed(a, b, diagonal_propagator=False):
    """Which pairs may be Wick-contracted.

    The kinetic term dOmega.dUpsilon gives quadratic form [[0,1],[1,0]], whose
    inverse is [[0,1],[1,0]]: only Omega-Upsilon contracts.  The knob exists
    solely so the control can switch it on and watch the theorem die.
    """
    if diagonal_propagator:
        return True
    return a != b


def dress(external, n_vertices, diagonal_propagator=False, vertex=VERTEX):
    """Every way of attaching n vertices to `external` and contracting.

    Enumerates partial matchings directly -- take the first free index and
    either leave it external or pair it with a later compatible one -- so the
    cost is the number of matchings rather than the number of pair-subsets.
    (The naive route cost 4m42s for this same table; this is instant.)

    Returns (set of surviving charges, number of patterns).  If the grading
    theorem holds the set is exactly {charge(external)}.
    """
    pool = list(external) + list(vertex) * n_vertices
    n = len(pool)
    charges, count = set(), 0

    def walk(i, used, ext_charge):
        nonlocal count
        while i < n and i in used:
            i += 1
        if i >= n:
            charges.add(ext_charge)
            count += 1
            return
        # leave i uncontracted (external)
        walk(i + 1, used, ext_charge + CHARGE[pool[i]])
        # or contract i with some later compatible j
        for j in range(i + 1, n):
            if j in used:
                continue
            if contractions_allowed(pool[i], pool[j], diagonal_propagator):
                walk(i + 1, used | {i, j}, ext_charge)

    walk(0, frozenset(), 0)
    return charges, count


def build():
    # --- the two structural inputs, verified rather than asserted ----------
    vertex_neutral = charge(VERTEX) == 0
    # quadratic form of dOmega.dUpsilon and its inverse, exactly over Q
    K = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    det = K[0][0] * K[1][1] - K[0][1] * K[1][0]
    Kinv = [[K[1][1] / det, -K[0][1] / det], [-K[1][0] / det, K[0][0] / det]]
    prop_offdiagonal = (Kinv[0][0] == 0 and Kinv[1][1] == 0
                        and Kinv[0][1] != 0 and Kinv[1][0] != 0)
    contraction_neutral = CHARGE[OM] + CHARGE[UP] == 0

    # --- the grading theorem, on every external content up to 4 legs ------
    rows, theorem_holds = [], True
    for n_ext in range(0, 5):
        for ext in itertools.combinations_with_replacement((OM, UP), n_ext):
            q0 = charge(ext)
            for nv in (0, 1, 2):
                got, npat = dress(ext, nv)
                ok = (got == {q0})
                theorem_holds = theorem_holds and ok
                if n_ext <= 2 and nv <= 2:
                    rows.append({
                        "external": "".join("O" if f == OM else "U"
                                            for f in ext) or "(none)",
                        "vertices": nv, "charge_in": q0,
                        "charges_out": sorted(got), "patterns": npat,
                        "invariant": ok,
                    })

    # --- controls, each built to break the theorem ------------------------
    # CTRL-A: a diagonal propagator (<OmegaOmega> != 0) must let charge move.
    got_diag, _ = dress((OM,), 1, diagonal_propagator=True)
    ctrl_diagonal_breaks = got_diag != {1}
    # CTRL-B: a charge-carrying vertex must let charge move.
    got_bad, _ = dress((OM,), 1, vertex=(OM, OM, OM, UP))
    ctrl_bad_vertex_breaks = got_bad != {1}
    # CTRL-C: vacuity -- the enumeration must actually explore something.
    _, npat_check = dress((OM, UP), 2)
    ctrl_nonvacuous = npat_check > 50

    # --- the regulator corollary, pure charge arithmetic -------------------
    q_mu_term = CHARGE[OM] + CHARGE[UP]          # mu^2 Omega Upsilon
    q_eps_term = 2 * CHARGE[OM]                  # (eps/2) Omega^2
    reg_rows = [
        {"term": "mu^2 * Omega * Upsilon", "charge": q_mu_term,
         "preserves_grading": q_mu_term == 0,
         "poles_at_eps_zero": "m_+^2 = m_-^2 = mu^2  (coincident)",
         "preserves_degeneracy": True},
        {"term": "(eps/2) * Omega^2", "charge": q_eps_term,
         "preserves_grading": q_eps_term == 0,
         "poles_at_eps_zero": "split by 2*sqrt(eps*g)",
         "preserves_degeneracy": False},
    ]
    ctrl_regulators_differ = q_mu_term == 0 and q_eps_term != 0

    checks = {
        "vertex_is_charge_neutral": vertex_neutral,
        "propagator_is_purely_off_diagonal": prop_offdiagonal,
        "every_contraction_is_charge_neutral": contraction_neutral,
        "charge_is_loop_order_invariant": theorem_holds,
        "control_diagonal_propagator_breaks_it": ctrl_diagonal_breaks,
        "control_charged_vertex_breaks_it": ctrl_bad_vertex_breaks,
        "control_enumeration_is_nonvacuous": ctrl_nonvacuous,
        "control_two_regulators_are_distinguished": ctrl_regulators_differ,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1",
        "dependency_tag": "LOCAL-ALGEBRAIC",
        "lifecycle_state": "CLASSIFIED",
        "question": "Can a loop generate positive charge, and so break the "
                    "one-sidedness hypothesis that Bateman-Turok's null "
                    "component relies on?",
        "answer": "No. The vertex Omega^2 Upsilon^2 is charge neutral and the "
                  "propagator is purely off-diagonal, so every Wick "
                  "contraction pairs Omega with Upsilon and is neutral too. "
                  "The charge of a process operator is therefore fixed by its "
                  "external legs and is independent of loop order: loops dress "
                  "an operator without moving it up the charge ladder. The "
                  "one-sidedness hypothesis is loop-stable, and the obstacle "
                  "to the loop extension is exactly the infrared one "
                  "Bateman-Turok named, nothing else in the charge sector.",
        "structural_inputs": {
            "vertex": "S_{1,1} = int [ dOmega.dUpsilon + (1/2) lambda^2 "
                      "Omega^2 Upsilon^2 ]  (their Eq. (14)); q = 0",
            "charges": "q(Omega) = +1, q(Upsilon) = -1 under "
                       "(Omega, Upsilon) -> (e^s Omega, e^-s Upsilon)",
            "kinetic_form": "[[0,1],[1,0]], inverse [[0,1],[1,0]]",
            "their_wightman": "W^{OmegaUpsilon} = W^{UpsilonOmega} = "
                              "theta(p0) delta(p^2); "
                              "W^{OmegaOmega} = W^{UpsilonUpsilon} = 0",
        },
        "grading_table": rows,
        "regulator_corollary": {
            "imported_exactly": "Paper 05: m_pm^2 = mu^2 +/- sqrt(eps g)",
            "rows": reg_rows,
            "reading": "mu^2 Omega Upsilon is a degeneracy-preserving AND "
                       "grading-preserving infrared mass; (eps/2) Omega^2 "
                       "destroys both, for the single reason that it carries "
                       "charge +2. This names the regulator the loop "
                       "extension should use.",
        },
        "successor_question": {
            "question": "Is the SO+(1,1) boost charge anomalous at one loop?",
            "why_it_is_the_risk": "the grading argument is classical "
                                  "bookkeeping and assumes the charge survives "
                                  "quantization; it is a GLOBAL symmetry and "
                                  "global symmetries can be anomalous",
            "where_it_would_live": "the measure -- Bateman-Turok note the phi "
                                   "and (Omega, Upsilon) path integrals are "
                                   "inequivalent, 'the former integrates over "
                                   "Omega > 0 whereas the latter integrates "
                                   "over all Omega'",
            "tractable_with": "the anomaly machinery already in quantum-weyl/",
        },
        "does_not_establish": [
            "the loop extension itself -- no loop integral is computed, no "
            "infrared divergence is regulated, nothing is resummed",
            "that the O(1,1) charge is non-anomalous; that is the successor "
            "question and it is open",
            "anything about the tensor (gravitational) case: this is the "
            "Bateman-Turok SCALAR model",
            "anything LORENTZIAN-CAUSAL, and nothing about g-2",
        ],
        "neighbours": {
            "reverse_physics/bt_born_trace.py":
                "the fixed-shell evaluation, and why it cannot decide this",
            "paper/05-interaction-obstructions.tex":
                "lem:chargenull, cprop:embedding, and the mass formula "
                "m_pm^2 = mu^2 +/- sqrt(eps g) imported above",
        },
        "imports": "none -- exact integer/rational bookkeeping, stdlib only",
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/charge-grading-loop-stability.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="charge grading loop-stability")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("Can a loop generate positive charge?")
    print()
    print("  vertex Omega^2 Upsilon^2 charge :", charge(VERTEX))
    print("  propagator                      : purely off-diagonal "
          "(<OO> = <UU> = 0)")
    print("  every contraction               : Omega + Upsilon, charge 0")
    print()
    print("  %-10s %-9s %-10s %-14s %s"
          % ("external", "vertices", "charge in", "charges out", "invariant"))
    for r in cert["grading_table"][:10]:
        print("  %-10s %-9d %-10d %-14s %s"
              % (r["external"], r["vertices"], r["charge_in"],
                 r["charges_out"], r["invariant"]))
    print()
    print("  regulators:")
    for r in cert["regulator_corollary"]["rows"]:
        print("    %-24s q = %+d  grading %-5s  degeneracy %s"
              % (r["term"], r["charge"], r["preserves_grading"],
                 r["preserves_degeneracy"]))
    print()
    print("  successor risk:", cert["successor_question"]["question"])
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
