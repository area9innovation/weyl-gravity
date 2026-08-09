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
one-sidedness hypothesis is loop-stable in this ambient combinatorics.  This
removes one cheap obstruction; it does not construct the infrared completion,
prove closure of the trace quotient, or exclude a measure anomaly.

WHAT THAT DOES NOT BUY, ON THE REGULATOR QUESTION.  Paper 05 records the formal
mass splitting m_pm^2 = mu^2 +/- sqrt(eps g).  Charge arithmetic still
distinguishes the neutral term mu^2 Omega Upsilon from the charged perturbation
(eps/2) Omega^2, and at a HELD background the former retains a double root.
But this was previously promoted too far: at the BT branch (v,0), the neutral
mass term creates the tadpole d_Upsilon V = v mu^2.  It is not a compatible
vacuum regulator merely because its quadratic matrix preserves degeneracy.

    q(Omega Upsilon) =  0   -> preserves the grading; at a held background the
                               two formal poles coincide, but stationarity fails
    q(Omega^2)       = +2   -> breaks the grading, which is why cprop:embedding
                               finds one-sidedness "exact iff eps = 0"; and it
                               SPLITS the poles by 2 sqrt(eps g), destroying the
                               degeneracy as well

The exact correction is certified by BT_IR_REGULATOR_TRILEMMA: stationarity of
an invariant V=F(Omega Upsilon) at (v,0) forces F'(0)=0, hence a massless double
root.  Moving the mass-deformed theory to its true stationary branch instead
splits the polynomial into one massless and one massive simple root.  This
module establishes only that ambient charge bookkeeping does not stand in the
way; it does not supply a compatible infrared regulator.

TWO RISKS REMAIN.  The primary infrared gate is now a non-mass architecture:
dimensional or off-shell regulation, inclusive/KLN cancellation, or dressed
asymptotic states.  Separately, the classical SO+(1,1) bookkeeping assumes the
global boost charge survives quantization; a measure anomaly remains open.

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

    # --- regulator preflight: charge facts, not vacuum compatibility -------
    q_mu_term = CHARGE[OM] + CHARGE[UP]          # mu^2 Omega Upsilon
    q_eps_term = 2 * CHARGE[OM]                  # (eps/2) Omega^2
    reg_rows = [
        {"term": "mu^2 * Omega * Upsilon", "charge": q_mu_term,
         "preserves_grading": q_mu_term == 0,
         "held_background_poles": "m_+^2 = m_-^2 = mu^2  (coincident)",
         "preserves_quadratic_degeneracy_at_held_background": True,
         "vacuum_compatible": False,
         "vacuum_failure": "tadpole d_Upsilon V|(v,0) = v*mu^2 != 0"},
        {"term": "(eps/2) * Omega^2", "charge": q_eps_term,
         "preserves_grading": q_eps_term == 0,
         "held_background_poles": "split by 2*sqrt(eps*g)",
         "preserves_quadratic_degeneracy_at_held_background": False,
         "vacuum_compatible": False,
         "vacuum_failure": "charge +2 explicitly breaks SO+(1,1)"},
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
                  "one-sidedness hypothesis is loop-stable in this ambient "
                  "bookkeeping. This does not supply an infrared regulator or "
                  "exclude a measure anomaly.",
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
        "quadratic_regulator_preflight": {
            "imported_exactly": "Paper 05: m_pm^2 = mu^2 +/- sqrt(eps g)",
            "rows": reg_rows,
            "reading": "mu^2 Omega Upsilon preserves charge and the formal "
                       "double root at a held background, but it creates a "
                       "tadpole there. These quadratic facts do not certify "
                       "vacuum compatibility.",
            "vacuum_compatibility":
                "REFUTED_BY_REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1",
        },
        "successor_question": {
            "question": "Which non-mass infrared architecture makes the first "
                        "collinear inclusive sum well defined, and is the "
                        "negative-charge trace radical closed under it?",
            "candidate_architectures": [
                "dimensional or off-shell regulation",
                "inclusive/KLN cancellation",
                "dressed asymptotic states",
            ],
            "separate_open_risk": "Is the SO+(1,1) boost charge anomalous at "
                                  "one loop? The measure is the candidate locus.",
        },
        "does_not_establish": [
            "the loop extension itself -- no loop integral is computed, no "
            "infrared divergence is regulated, nothing is resummed",
            "a vacuum-compatible infrared mass; the neutral mass term fails "
            "the stationary-BT-vacuum test in the trilemma certificate",
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
    print("  quadratic regulator preflight:")
    for r in cert["quadratic_regulator_preflight"]["rows"]:
        print("    %-24s q = %+d  grading %-5s  held degeneracy %s"
              % (r["term"], r["charge"], r["preserves_grading"],
                 r["preserves_quadratic_degeneracy_at_held_background"]))
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
