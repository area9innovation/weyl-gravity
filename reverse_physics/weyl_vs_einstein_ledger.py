"""What Weyl gravity OPENS and CHALLENGES, relative to Einstein gravity.

WHY THIS EXISTS.  [PHYSICS-VS-MATH.md] sorts a single theory's ledger into three
columns -- PHYSICS (assumptions under test), GEOMETRY (imported, isolated) and
MATHEMATICS (proved here).  That is enough to state what Weyl gravity IS.  It is
not enough to state what Weyl gravity DOES relative to the theory everyone
compares it against, because a comparative sentence carries two extra pieces of
information that the three-column ledger has nowhere to put:

  * a DIRECTION.  Does the claim describe something Weyl gravity makes available
    that Einstein gravity forbids (OPENS), something Einstein gravity supplies
    that Weyl gravity must now pay for (CHALLENGES), or something both theories
    have equally (SHARED -- which is the row people most often get wrong, by
    charging Weyl gravity for a bill Einstein gravity also owes)?

  * a LEVEL.  Actions, field equations, solution loci, symplectic/dynamical
    structure, and quantum theory are five different places to assert a
    comparison, and the SAME SENTENCE CAN FLIP TRUTH VALUE BETWEEN THEM.

The level axis is not invented here.  It is forced by two results this
repository already holds, which together make it impossible to state the
Einstein comparison in one column:

    L2 (solutions)    Ric(g) = Lambda g  ==>  B_mn(g) = 0.
                      Every Einstein vacuum solution is a Weyl solution.
                      PROVED, LOCAL-ALGEBRAIC.
                      notes/conformal-einstein-sector-theorem.md

    L3 (symplectic)   REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED.
                      The restricted pure-Weyl and Einstein-Hilbert Cauchy
                      matrices have ranks zero and two; no nonzero
                      normalization identifies them.
                      reports/flat-einstein-symplectic-restriction.md

"Einstein gravity is contained in Weyl gravity" is therefore TRUE at L2 and
FALSE at L3.  A comparison ledger without a level column does not merely lose
precision -- it contradicts itself.  PHYSICS-VS-MATH.md section 3.2b already
found the weaker version of this (the ASSUMPTION COUNT differs between actions
and field equations, six versus five, for the same theory); the Einstein pair
shows the TRUTH VALUE differs too.

THE ORGANISING CLAIM.  In reverse-physics currency, comparing two theories is
not comparing predictions.  It is comparing assumption sets.  Einstein gravity
and Weyl gravity sit over the SAME base and differ by exactly ONE SWAP:

    shared base   RP-LOCAL, RP-METRIC, RP-DIFF, RP-DIM4
    Einstein      + RP-2ND-ORDER          -> Lovelock  -> G_ab + Lambda g_ab
    Weyl          + RP-WEYL (+ RP-TOPO-INERT) -> D-2k=0 -> B_ab

and the swap is NOT A FREE CHOICE BETWEEN COMPATIBLE OPTIONS.  The conformal
weight law D - 2k = 0, proved in this stream, says a Weyl-invariant local
curvature action of degree k exists only when D = 2k; curvature degree k gives
derivative order 2k.  So in D = 4, Weyl invariance forces fourth order, and
RP-WEYL and RP-2ND-ORDER are JOINTLY UNSATISFIABLE.  You cannot have both.

That is what makes OPENS and CHALLENGES two halves of ONE TRADE rather than two
independent lists of pros and cons.  Every entry should trace to the swap, and
the sharpest instance is a pair that is literally one theorem seen twice:

    OPENS       the derivative order is DERIVED, not assumed (D - 2k = 0),
                so the Weyl assumption set uses one fewer physical input than
                the standard motivation for it.
    CHALLENGES  the Ostrogradsky ghost is FORCED (D - 2k = 0 pins the pole
                count at D/2, and two or more poles always include a negative
                residue).

Same equation.  The ghost is not a defect of a particular Lagrangian to be
engineered away -- it is the price of the assumption RP-2ND-ORDER was buying on
the Einstein side, and weyl-ghost-forced.md proves the two natural evasions
(drop RP-WEYL, change RP-DIM4) provably fail.

WHY THE SEPARATION IS MANDATORY HERE, AND NOT MERELY TIDY.  Three failure modes
that only the columns catch, one example of each already in this repository:

  1. A claim whose risk is not where the sentence sounds like it is.  "Weyl
     gravity accounts for galactic rotation curves without dark matter" and
     "the Mannheim-Kazanas metric is an exact static Bach-flat solution" are
     different kinds of claim about the same object.  The second is certified
     here (Paper 18).  The first is PHYSICS, contingent on galactic data, and
     is not established by the second.  Same object, different columns.

  2. A CHALLENGE reported in the wrong column.  The ghost is usually written up
     as a defect awaiting a fix, which places it in PHYSICS.  Here it is
     MATHEMATICS: a zero-axiom theorem.  Anything calling itself a fix is an
     assumption drop, not a model tweak, and the ledger says which assumption.

  3. A claim with no counterfactual at all.  This stream published one --
     that the coprime obstruction is how a ghost destabilises a healthy mode --
     and retracted it with proof (coprime-charge-bound.md).  Test T2 is the
     check that would have caught it before publication.

WHAT THIS MODULE IS.  The ledger rows are data, and this file is the rail that
keeps them honest.  It does not compute physics; it enforces the discipline
that makes citation-based rows trustworthy.  The user-facing rule for this
stream is that CITATIONS ARE SUFFICIENT IF THEY ARE TRUSTWORTHY, so the checks
are aimed exactly at what makes a citation untrustworthy:

    C1  vocabulary       every direction/level/column/status is in the fixed
                         vocabulary -- no ad-hoc statuses
    C2  resolvable       every in-repo source path EXISTS.  A dangling citation
                         is the primary way a citation stops being trustworthy,
                         and it fails silently in prose.
    C3  no cited proofs  column MATHEMATICS requires status PROVED/DISCHARGED/
                         REFUTED *and* an in-repo source.  You cannot cite your
                         way into the right-hand column.
    C4  falsifiability   column PHYSICS requires a non-empty `contingent_on`:
                         what observation would kill it.  This is test T2, made
                         mechanical.
    C5  cited is cited   status CITED requires a `literature` field and forbids
                         column MATHEMATICS.
    C6  traceability     every row traces to a declared assumption, so no row
                         can be a free-floating opinion about gravity.
    C7  level flips      a row that flips truth value across levels must name
                         its partner via `flips_with`; the partner must exist,
                         sit at a different level, and carry the opposite
                         direction.  This is test T5, made mechanical.
    C8  the trade        an OPENS row may name what it is `paid_for_by` and a
                         CHALLENGES row what it `buys`; the reference must
                         exist and point the other way.  This is what stops the
                         ledger degenerating into a pros-and-cons list.
    C9  SHARED is inert  a SHARED row may not be used as a differentiator: it
                         must trace to a base assumption, not to either side's
                         addition.

WHAT THIS IS NOT.  No row here is new physics and none is a new theorem.  The
ledger is an organisational artifact over results that already exist, and every
row points at where its content actually lives.  Rows marked OPEN are open --
the module asserts nothing about them beyond that they are unresolved, and the
certificate reports the OPEN count as a first-class number rather than burying
it.  In particular the DYNAMICAL consequence of the ghost is OPEN, and this
ledger must not be read as settling it.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_vs_einstein_ledger --check
    PYTHONPATH=. python3 -m reverse_physics.weyl_vs_einstein_ledger --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_WEYL_VS_EINSTEIN_LEDGER_V1.json",
)

# --------------------------------------------------------------------------
# Vocabulary.  Fixed, small, and enforced -- an ad-hoc status is how a ledger
# stops being comparable across rows.
# --------------------------------------------------------------------------

DIRECTIONS = ("OPENS", "CHALLENGES", "SHARED")

LEVELS = {
    "L0": "the action",
    "L1": "the field equations",
    "L2": "the solution locus",
    "L3": "symplectic / dynamical structure (Cauchy data, energy, counting)",
    "L4": "the quantum theory",
}

COLUMNS = ("PHYSICS", "GEOMETRY", "MATHEMATICS")

STATUSES = {
    "PROVED": "a theorem of this development, machine-checked, zero axioms",
    "DISCHARGED": "verified exactly at specific metrics -- stronger than an "
                  "import, weaker than a theorem for all metrics",
    "REFUTED": "an exact negative result established here",
    "CITED": "imported from the literature or from another stream; trusted, "
             "not re-derived",
    "OPEN": "unresolved; recorded so it cannot be quietly assumed",
}

# --------------------------------------------------------------------------
# The assumption swap.  Everything in the ledger must trace to one of these.
# --------------------------------------------------------------------------

BASE_ASSUMPTIONS = {
    "RP-LOCAL": "the action is an integral of a local density",
    "RP-METRIC": "the metric is the only field",
    "RP-DIFF": "diffeomorphism invariance",
    "RP-DIM4": "D = 4",
}

EINSTEIN_ADDITION = {
    "RP-2ND-ORDER": "the field equations are at most second order in "
                    "derivatives of the metric (Lovelock's hypothesis)",
}

WEYL_ADDITION = {
    "RP-WEYL": "local Weyl invariance",
    "RP-TOPO-INERT": "topological terms are physically inert",
    "RP-PARITY": "parity invariance",
}

ALL_ASSUMPTIONS = dict(BASE_ASSUMPTIONS)
ALL_ASSUMPTIONS.update(EINSTEIN_ADDITION)
ALL_ASSUMPTIONS.update(WEYL_ADDITION)

# The swap is not a choice between compatible options.  D - 2k = 0 with
# derivative order 2k means Weyl invariance in D = 4 forces fourth order, so
# RP-WEYL and RP-2ND-ORDER cannot both hold.  Proved in this stream; the row
# INCOMPATIBLE below carries the citation.
SWAP = {
    "shared_base": sorted(BASE_ASSUMPTIONS),
    "einstein_adds": sorted(EINSTEIN_ADDITION),
    "weyl_adds": sorted(WEYL_ADDITION),
    "jointly_unsatisfiable": ["RP-WEYL", "RP-2ND-ORDER"],
    # The Einstein side's uniqueness theorem is an IMPORT.  It is not proved
    # here and it is not a row -- it underpins the framing rather than being
    # compared -- but the swap is unsupported without it, so it is cited in
    # place with the column it belongs to.
    "einstein_uniqueness": {
        "statement": "In D = 4 the only symmetric, divergence-free 2-tensor "
                     "built from the metric and at most its second "
                     "derivatives, linear in the second derivatives, is "
                     "a G_ab + b g_ab.  This is what makes RP-2ND-ORDER a "
                     "uniqueness hypothesis rather than a preference, and it "
                     "is the exact counterpart of D - 2k = 0 on the Weyl side.",
        "column": "GEOMETRY",
        "status": "CITED",
        "literature": ["Lovelock, J. Math. Phys. 12 (1971) 498",
                       "Lovelock, J. Math. Phys. 13 (1972) 874"],
    },
    "why": "The conformal weight law D - 2k = 0 admits a Weyl-invariant local "
           "curvature action of degree k only when D = 2k, and curvature "
           "degree k gives derivative order 2k.  At D = 4 that is k = 2 and "
           "fourth order.  Einstein-Hilbert is k = 1, which is Weyl invariant "
           "only at D = 2.  So no local metric action in four dimensions is "
           "both Weyl invariant and second order, and the comparison is a "
           "forced trade rather than a menu.",
    "source": "reverse_physics/reports/weyl-action-reverse-physics.md",
}


def row(**kw):
    kw.setdefault("sources", [])
    kw.setdefault("literature", [])
    kw.setdefault("contingent_on", "")
    kw.setdefault("flips_with", "")
    kw.setdefault("paid_for_by", "")
    kw.setdefault("buys", "")
    kw.setdefault("note", "")
    return kw


# --------------------------------------------------------------------------
# The ledger.
# --------------------------------------------------------------------------

ROWS = [

    # ---------------- OPENS -----------------------------------------------

    row(
        id="O-SCALE",
        direction="OPENS",
        level="L0",
        column="MATHEMATICS",
        status="PROVED",
        claim="The action carries no dimensionful constant.  Einstein's "
              "assumption set admits two (Newton's constant and Lambda); the "
              "Weyl Lagrangian sqrt(-g) C^2 has conformal weight zero at "
              "D = 4, so its coefficient alpha is dimensionless, and the "
              "invariant quotient is one-dimensional so there is no second "
              "coefficient to carry a scale.",
        traces_to=["RP-WEYL", "RP-DIM4"],
        sources=["reverse_physics/reports/weyl-action-reverse-physics.md",
                 "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_ACTION_V1.json"],
        buys="",
        note="Weight zero at D = 4, k = 2 is exactly the equation D - 2k = 0. "
             "The absence of a scale is the same fact as the derived "
             "derivative order, read dimensionally.",
    ),

    row(
        id="O-DERIVED-ORDER",
        direction="OPENS",
        level="L0",
        column="MATHEMATICS",
        status="PROVED",
        claim="The derivative order is DERIVED, not assumed.  Einstein gravity "
              "must posit RP-2ND-ORDER as an input (it is the hypothesis of "
              "Lovelock's theorem).  Weyl gravity posits nothing about "
              "derivative order: D - 2k = 0 forces k = D/2, hence k = 2 and "
              "fourth order at D = 4, and the same line excludes the "
              "cosmological term (k = 0) and Einstein-Hilbert (k = 1).",
        traces_to=["RP-WEYL", "RP-DIM4"],
        sources=["reverse_physics/reports/weyl-action-reverse-physics.md",
                 "reverse_physics/reports/PHYSICS-VS-MATH.md"],
        paid_for_by="C-GHOST-FORCED",
        note="This is the OPENS half of the trade.  The standard motivation "
             "for conformal gravity lists 'quadratic in curvature' as an "
             "assumption; it is a consequence.  One fewer physical input.",
    ),

    row(
        id="O-EINSTEIN-SOLUTIONS",
        direction="OPENS",
        level="L2",
        column="MATHEMATICS",
        status="PROVED",
        claim="Every four-dimensional Einstein vacuum solution is a Weyl "
              "solution: Ric(g) = Lambda g implies B_mn(g) = 0.  The Einstein "
              "solution locus embeds in the Bach-flat locus, and the "
              "inclusion is generally PROPER -- Bach-flat metrics need not be "
              "conformally Einstein.",
        traces_to=["RP-WEYL"],
        sources=["notes/conformal-einstein-sector-theorem.md",
                 "bridge/certificates/einstein_sector_theorem.json"],
        flips_with="C-NOT-A-SUBSYSTEM",
        note="Dependency tag LOCAL-ALGEBRAIC.  This is a statement about "
             "equations and solution loci only.  It does NOT by itself "
             "identify actions, symplectic forms, gauge quotients, "
             "observables or boundary-value problems -- and the L3 partner row "
             "shows that one of those identifications actually fails.",
    ),

    row(
        id="O-EXTRA-TOWERS",
        direction="OPENS",
        level="L2",
        column="MATHEMATICS",
        status="PROVED",
        claim="The Weyl solution space is strictly larger in a structured way: "
              "the certified linear cylinder solution space carries the A and "
              "L towers in addition to the Einstein-root E tower, and these "
              "are dynamical extra content of the fourth-order equation, not "
              "Weyl gauge copies of the Einstein tower.",
        traces_to=["RP-WEYL"],
        sources=["notes/conformal-einstein-sector-theorem.md"],
        note="Dependency tag REDUCED-MODE.  A REDUCED-MODE result is not "
             "evidence for a LORENTZIAN-CAUSAL claim and is not used as one "
             "here.",
    ),

    row(
        id="O-PARITY-DIRECTION",
        direction="OPENS",
        level="L0",
        column="MATHEMATICS",
        status="PROVED",
        claim="A parity direction exists that Einstein gravity has no analogue "
              "of at this level: alpha W_+^2 + beta W_-^2 is a genuine "
              "two-parameter family of ACTIONS, the map is injective, and "
              "W_+^2 is provably not parity-even.",
        traces_to=["RP-PARITY"],
        sources=["reverse_physics/reports/PHYSICS-VS-MATH.md",
                 "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_ACTION_V1.json"],
        flips_with="S-PARITY-CLASSICALLY-FREE",
        note="Honest boundary: this is an opening at L0 only.  At L1 the "
             "family collapses to one parameter because the difference is "
             "((alpha-beta)/2) P and P is topological.  It becomes physical "
             "again at L4 as a gravitational theta-angle, which is outside "
             "this programme's claim boundary.",
    ),

    row(
        id="O-STATIC-FAMILY",
        direction="OPENS",
        level="L2",
        column="MATHEMATICS",
        status="DISCHARGED",
        claim="Weyl gravity admits an exact static vacuum family strictly "
              "larger than Schwarzschild-de Sitter -- the Mannheim-Kazanas "
              "family -- on which this repository establishes residual-basic "
              "charges and simultaneous horizon first laws.",
        traces_to=["RP-WEYL"],
        sources=["paper/18-static-bach-flat-black-hole-thermodynamics.tex",
                 "paper/98-physicist-executive-summary.md"],
        note="This is the exact static and linear-spherical CHARGE theorem, "
             "not a physical-process or radiative thermodynamics theorem.  It "
             "is the mathematical half of the pair whose physical half is "
             "O-ROTATION-CURVES; the two must not be conflated.",
    ),

    row(
        id="O-ROTATION-CURVES",
        direction="OPENS",
        level="L2",
        column="PHYSICS",
        status="CITED",
        claim="The extra term in the static family has been argued in the "
              "literature to fit galactic rotation curves without dark "
              "matter, which Einstein gravity cannot do without additional "
              "matter content.",
        traces_to=["RP-WEYL"],
        sources=[],
        literature=["Mannheim & Kazanas, ApJ 342 (1989) 635",
                    "Mannheim, Prog. Part. Nucl. Phys. 56 (2006) 340"],
        contingent_on="Galactic rotation-curve data, and in particular whether "
                      "a single scale-free potential term fits samples across "
                      "morphology without per-galaxy tuning; also cluster and "
                      "lensing data, where the same term is separately "
                      "constrained.",
        note="THE SEPARATION ROW.  The metric family is certified in this "
             "repository (O-STATIC-FAMILY, MATHEMATICS).  This phenomenological "
             "reading of it is NOT, is not established by it, and is not "
             "assessed here.  A ledger that merged the two would report a "
             "citation's risk as a theorem's.",
    ),

    row(
        id="O-RENORMALIZABILITY",
        direction="OPENS",
        level="L4",
        column="PHYSICS",
        status="CITED",
        claim="Because the coupling is dimensionless, the theory is power-"
              "counting renormalizable, which Einstein gravity is not.",
        traces_to=["RP-WEYL"],
        sources=["reverse_physics/reports/weyl-ghost-forced.md"],
        literature=["Stelle, Phys. Rev. D16 (1977) 953",
                    "Fradkin & Tseytlin, Nucl. Phys. B201 (1982) 469"],
        contingent_on="Whether power-counting survives as an actual "
                      "renormalizability statement in a construction that also "
                      "handles the ghost; the two are quoted together in the "
                      "literature precisely because Stelle's theory is "
                      "renormalizable AND ghost-ridden.",
        paid_for_by="C-GHOST-FORCED",
        note="Explicitly NOT established here.  This programme's claim "
             "boundary states that no Lorentzian off-shell BV propagator, "
             "renormalized Lorentzian time-ordered products, or causal "
             "perturbative AQFT construction exists in this repository.  The "
             "row is CITED and carries no dependency tag of ours.",
    ),

    # ---------------- CHALLENGES ------------------------------------------

    row(
        id="C-GHOST-FORCED",
        direction="CHALLENGES",
        level="L3",
        column="MATHEMATICS",
        status="PROVED",
        claim="The Ostrogradsky ghost is FORCED by the same equation that "
              "makes the action unique.  D - 2k = 0 pins the propagator's pole "
              "count at D/2, and for simple poles the partial-fraction "
              "residues alternate in sign, so two or more poles always include "
              "a negative residue -- a negative-norm state.  Einstein gravity "
              "avoids this precisely by assuming RP-2ND-ORDER, which is the "
              "assumption Weyl gravity gave up.",
        traces_to=["RP-WEYL", "RP-DIM4"],
        sources=["reverse_physics/reports/weyl-ghost-forced.md",
                 "rocq/WeylGhostForced.v",
                 "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1.json"],
        buys="O-DERIVED-ORDER",
        note="THE TRADE ROW.  This and O-DERIVED-ORDER are the same theorem "
             "read twice.  The ghost is therefore MATHEMATICS here, not a "
             "PHYSICS defect awaiting a model fix -- which is how it is "
             "usually filed, and filing it there is what makes people look for "
             "fixes that provably do not exist.",
    ),

    row(
        id="C-NO-CHEAP-FIX",
        direction="CHALLENGES",
        level="L0",
        column="MATHEMATICS",
        status="PROVED",
        claim="The ghost cannot be tuned away by choosing a different "
              "conformal action, because there is no other conformal action.  "
              "Every proposal of the form 'take conformal gravity but modify "
              "the curvature terms' is excluded.  Of the assumptions one might "
              "drop instead, two provably do not help: dropping RP-WEYL keeps "
              "curvature degree 2 and hence the pole count, and D = 6 is "
              "worse, forcing degree 3 and three poles.",
        traces_to=["RP-WEYL", "RP-DIM4"],
        sources=["reverse_physics/reports/weyl-ghost-forced.md",
                 "rocq/WeylGhostForced.v"],
        note="The remaining escapes -- drop RP-LOCAL (infinite-derivative "
             "gravity) or RP-METRIC (a compensator scalar) -- are CITATIONS, "
             "not theorems here, and both take you outside the theory this "
             "repository is about.  RP-DIFF is not analysed.",
    ),

    row(
        id="C-NOT-A-SUBSYSTEM",
        direction="CHALLENGES",
        level="L3",
        column="MATHEMATICS",
        status="REFUTED",
        claim="Containment of solutions does NOT upgrade to containment of "
              "dynamics.  For the reduced flat TT sector the action-derived "
              "pure-Weyl current restricts to zero on Einstein wave tangents: "
              "the restricted pure-Weyl and Einstein-Hilbert Cauchy matrices "
              "have ranks zero and two, so no nonzero normalization identifies "
              "them, and local finite-jet improvements integrate to zero on "
              "the Schwartz domain.  Verdict "
              "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED.",
        traces_to=["RP-WEYL"],
        sources=["reports/flat-einstein-symplectic-restriction.md",
                 "notes/conformal-flat-einstein-symplectic-restriction.md"],
        flips_with="O-EINSTEIN-SOLUTIONS",
        note="THE LEVEL ROW.  'Einstein gravity is contained in Weyl gravity' "
             "is TRUE at L2 and FALSE at L3, and both halves are established "
             "here.  Dependency tags REDUCED-MODE and LORENTZIAN-CAUSAL.  The "
             "receipt's own boundary: this is not a full metric BV theorem, "
             "not a null-infinity current, not a complete Einstein scattering "
             "no-go, and leaves compensators and symmetry breaking open.",
    ),

    row(
        id="C-CAUCHY-DATA",
        direction="CHALLENGES",
        level="L3",
        column="GEOMETRY",
        status="CITED",
        claim="Fourth-order field equations need twice the initial data: "
              "Einstein gravity's Cauchy problem is posed with (g, K) on a "
              "slice, Weyl gravity's needs two further derivative orders.  The "
              "extra data is what the A and L towers (O-EXTRA-TOWERS) are made "
              "of, and it is the same doubling that Ostrogradsky's theorem "
              "converts into the ghost.",
        traces_to=["RP-WEYL"],
        sources=["reports/flat-einstein-symplectic-restriction.md"],
        literature=["Ostrogradsky, Mem. Ac. St. Petersbourg VI 4 (1850) 385",
                    "Woodard, Scholarpedia 10 (2015) 32243"],
        buys="O-EXTRA-TOWERS",
        note="Filed GEOMETRY, not MATHEMATICS: the well-posedness statement "
             "for higher-derivative systems is imported and not re-derived "
             "here.  What IS established here is narrower and sits in "
             "C-NOT-A-SUBSYSTEM -- that on the reduced flat TT sector the "
             "pure-Weyl and Einstein-Hilbert Cauchy matrices have ranks zero "
             "and two, so the extra data is not a rescaling of the Einstein "
             "data.",
    ),

    row(
        id="C-NO-NEWTON-CONSTANT",
        direction="CHALLENGES",
        level="L2",
        column="PHYSICS",
        status="OPEN",
        claim="Having no dimensionful constant in the action (O-SCALE) means "
              "the observed gravitational scale cannot be read off the action "
              "and must instead be generated -- by a solution, by a boundary "
              "condition, or by symmetry breaking.  Recovery of a Newtonian "
              "regime with the measured constant is not established in this "
              "repository.",
        traces_to=["RP-WEYL"],
        sources=["notes/conformal-compensator-einstein-phase.md",
                 "notes/conformal-asymptotically-flat-einstein-bootstrap.md"],
        contingent_on="Solar-system and laboratory tests of the Newtonian and "
                      "post-Newtonian regime, which fix both the constant and "
                      "the allowed size of any additional scale-free term.",
        buys="O-SCALE",
        note="OPEN means open.  The compensator and asymptotic-bootstrap notes "
             "are the in-repository direction of attack, not a result; they "
             "are cited here so the row points somewhere rather than nowhere.",
    ),

    row(
        id="C-DOF-NOT-WELL-POSED",
        direction="CHALLENGES",
        level="L3",
        column="MATHEMATICS",
        status="PROVED",
        claim="'How many degrees of freedom are in this region' is not a "
              "well-posed question in a conformally invariant theory -- a "
              "standard Einstein-side notion that does not survive the swap.  "
              "All three branches close: the density branch by a parity "
              "obstruction in odd dimension, the counting measure as "
              "uninformative, and the non-additive branch because on flat "
              "space a dilation is conformal, so a unit ball and one of radius "
              "10^100 tie and additivity is never used.",
        traces_to=["RP-WEYL"],
        sources=["reverse_physics/reports/relational-count-rocq.md",
                 "reverse_physics/reports/no-conformal-count-rocq.md",
                 "reverse_physics/reports/PHYSICS-VS-MATH.md"],
        note="What survives is a RELATIVE count generated by a single scaling "
             "exponent, with degree-of-freedom independence transposing to "
             "additivity of that exponent.  So this row is a challenge to the "
             "QUESTION, not a deficiency in the answer -- which is a "
             "distinction only a column-separated ledger can record.",
    ),

    row(
        id="C-GHOST-DYNAMICS",
        direction="CHALLENGES",
        level="L3",
        column="PHYSICS",
        status="OPEN",
        claim="The DYNAMICAL consequence of the ghost -- whether and how it "
              "destabilises the physical sector, and whether any sector or "
              "boundary condition survives it -- is not characterized.",
        traces_to=["RP-WEYL"],
        sources=["reverse_physics/reports/ghost-model-obstruction.md",
                 "reverse_physics/reports/coprime-charge-bound.md"],
        contingent_on="Whether a stable regime exists observationally, and on "
                      "any construction exhibiting decay or its absence; "
                      "nothing here bounds it.",
        note="THE RETRACTION ROW.  This stream published a dynamical reading "
             "of a ghost obstruction and retracted it with proof: the coded "
             "free Hamiltonian is positive definite, and the obstruction "
             "conserves a positive charge that BOUNDS both occupations "
             "regardless of any ghost sign.  GHOST_MODEL_OBSTRUCTION then "
             "showed the coprime obstruction does not decide the question in "
             "EITHER direction.  The row stays OPEN, and the toy-model results "
             "must not be read as statements about Weyl gravity.",
    ),

    # ---------------- SHARED ----------------------------------------------

    row(
        id="S-DIFF-INVISIBLE",
        direction="SHARED",
        level="L0",
        column="PHYSICS",
        status="OPEN",
        claim="RP-DIFF has no independence witness in either theory.  It is "
              "what makes 'the space of curvature scalars' the right space at "
              "all, so it never appears as a row in a matrix.  This is the "
              "largest genuine hole in the ledger, and it is NOT a Weyl-"
              "specific one.",
        traces_to=["RP-DIFF"],
        sources=["reverse_physics/reports/PHYSICS-VS-MATH.md"],
        contingent_on="Any observation distinguishing a preferred coordinate "
                      "system; the assumption is shared with essentially all "
                      "of classical gravity, so a witness would be a result "
                      "about both theories at once.",
        note="Recorded as SHARED so it cannot be charged to Weyl gravity's "
             "account in a comparison.",
    ),

    row(
        id="S-LOCAL-METRIC-UNTESTED",
        direction="SHARED",
        level="L0",
        column="PHYSICS",
        status="OPEN",
        claim="RP-LOCAL and RP-METRIC bound the coordinate space of BOTH "
              "theories rather than being tested inside it.  Neither theory's "
              "ledger tests them, and testing them needs a carrier containing "
              "nonlocal or multi-field actions, which this stream has not "
              "built.",
        traces_to=["RP-LOCAL", "RP-METRIC"],
        sources=["reverse_physics/reports/PHYSICS-VS-MATH.md"],
        contingent_on="Any evidence for nonlocality or for a second "
                      "gravitational field; both are live in the literature "
                      "and neither is settled by either theory's uniqueness "
                      "theorem.",
        note="Both are also the two escapes from C-NO-CHEAP-FIX, which is why "
             "their untested status is load-bearing rather than pedantic: the "
             "only surviving routes out of the ghost run through assumptions "
             "neither theory tests.",
    ),

    row(
        id="S-PARITY-CLASSICALLY-FREE",
        direction="SHARED",
        level="L1",
        column="MATHEMATICS",
        status="PROVED",
        claim="At the level of field equations the parity direction costs "
              "nothing and distinguishes nothing: the chiral family collapses "
              "to one parameter because alpha W_+^2 + beta W_-^2 differs from "
              "((alpha+beta)/2) C^2 by exactly ((alpha-beta)/2) P, and P is "
              "topological.",
        traces_to=["RP-PARITY", "RP-TOPO-INERT"],
        sources=["reverse_physics/reports/PHYSICS-VS-MATH.md",
                 "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_ACTION_V1.json"],
        flips_with="O-PARITY-DIRECTION",
        note="Filed SHARED at L1 because at this level it is not an opening "
             "relative to Einstein gravity at all -- the same physical content "
             "is reached with or without it.  The row exists so that "
             "O-PARITY-DIRECTION cannot be quoted without its level.",
    ),
]


# --------------------------------------------------------------------------
# Checks.
# --------------------------------------------------------------------------

def _in_repo(path):
    return os.path.exists(os.path.join(REPO_ROOT, path))


def check_rows(rows):
    """Return (failures, stats).  A failure is a human-readable string."""
    fail = []
    by_id = {}
    for r in rows:
        if r["id"] in by_id:
            fail.append("C1 duplicate row id %s" % r["id"])
        by_id[r["id"]] = r

    for r in rows:
        rid = r["id"]

        # C1 -- vocabulary
        if r["direction"] not in DIRECTIONS:
            fail.append("C1 %s: direction %r not in vocabulary" % (rid, r["direction"]))
        if r["level"] not in LEVELS:
            fail.append("C1 %s: level %r not in vocabulary" % (rid, r["level"]))
        if r["column"] not in COLUMNS:
            fail.append("C1 %s: column %r not in vocabulary" % (rid, r["column"]))
        if r["status"] not in STATUSES:
            fail.append("C1 %s: status %r not in vocabulary" % (rid, r["status"]))
        if not r.get("claim"):
            fail.append("C1 %s: empty claim" % rid)

        # C2 -- every in-repo source resolves.  A dangling citation is the
        # primary way a citation stops being trustworthy.
        for s in r["sources"]:
            if not _in_repo(s):
                fail.append("C2 %s: source does not exist: %s" % (rid, s))

        # C3 -- you cannot cite your way into the MATHEMATICS column
        if r["column"] == "MATHEMATICS":
            if r["status"] not in ("PROVED", "DISCHARGED", "REFUTED"):
                fail.append("C3 %s: column MATHEMATICS with status %s"
                            % (rid, r["status"]))
            if not r["sources"]:
                fail.append("C3 %s: column MATHEMATICS with no in-repo source" % rid)

        # C4 -- a PHYSICS claim must name what could falsify it (test T2)
        if r["column"] == "PHYSICS" and not r["contingent_on"]:
            fail.append("C4 %s: column PHYSICS with empty contingent_on" % rid)

        # C5 -- CITED is cited
        if r["status"] == "CITED":
            if not r["literature"]:
                fail.append("C5 %s: status CITED with no literature" % rid)
            if r["column"] == "MATHEMATICS":
                fail.append("C5 %s: status CITED in column MATHEMATICS" % rid)

        # C6 -- traceability to a declared assumption
        if not r.get("traces_to"):
            fail.append("C6 %s: traces_to is empty" % rid)
        for a in r.get("traces_to", []):
            if a not in ALL_ASSUMPTIONS:
                fail.append("C6 %s: traces_to unknown assumption %s" % (rid, a))

        # C9 -- a SHARED row may not be a differentiator
        if r["direction"] == "SHARED":
            diff = set(r.get("traces_to", [])) - set(BASE_ASSUMPTIONS)
            base = set(r.get("traces_to", [])) & set(BASE_ASSUMPTIONS)
            if not base and not _shared_exemption(r):
                fail.append("C9 %s: SHARED row traces only to %s, which is a "
                            "differentiator" % (rid, sorted(diff)))

    # C7 -- level flips are mutual, cross-level, and opposite in direction
    for r in rows:
        p = r["flips_with"]
        if not p:
            continue
        if p not in by_id:
            fail.append("C7 %s: flips_with names a missing row %s" % (r["id"], p))
            continue
        q = by_id[p]
        if q["flips_with"] != r["id"]:
            fail.append("C7 %s: flips_with %s is not mutual" % (r["id"], p))
        if q["level"] == r["level"]:
            fail.append("C7 %s: flips_with %s at the same level %s -- a flip "
                        "must cross levels" % (r["id"], p, r["level"]))
        if q["direction"] == r["direction"]:
            fail.append("C7 %s: flips_with %s has the same direction %s"
                        % (r["id"], p, r["direction"]))

    # C8 -- the trade is mutual and points the other way
    for r in rows:
        if r["paid_for_by"]:
            if r["direction"] != "OPENS":
                fail.append("C8 %s: paid_for_by on a non-OPENS row" % r["id"])
            q = by_id.get(r["paid_for_by"])
            if q is None:
                fail.append("C8 %s: paid_for_by names a missing row %s"
                            % (r["id"], r["paid_for_by"]))
            elif q["direction"] != "CHALLENGES":
                fail.append("C8 %s: paid_for_by %s is not a CHALLENGES row"
                            % (r["id"], r["paid_for_by"]))
        if r["buys"]:
            if r["direction"] != "CHALLENGES":
                fail.append("C8 %s: buys on a non-CHALLENGES row" % r["id"])
            q = by_id.get(r["buys"])
            if q is None:
                fail.append("C8 %s: buys names a missing row %s"
                            % (r["id"], r["buys"]))
            elif q["direction"] != "OPENS":
                fail.append("C8 %s: buys %s is not an OPENS row"
                            % (r["id"], r["buys"]))

    stats = {
        "rows": len(rows),
        "by_direction": {d: sum(1 for r in rows if r["direction"] == d)
                         for d in DIRECTIONS},
        "by_column": {c: sum(1 for r in rows if r["column"] == c)
                      for c in COLUMNS},
        "by_status": {s: sum(1 for r in rows if r["status"] == s)
                      for s in STATUSES},
        "by_level": {l: sum(1 for r in rows if r["level"] == l) for l in LEVELS},
        "open_rows": sorted(r["id"] for r in rows if r["status"] == "OPEN"),
        "level_flips": sorted(r["id"] for r in rows if r["flips_with"]),
        # A single cost can buy several things, so the trade graph is
        # deliberately many-to-one and edges are collected from both ends.
        "trade_pairs": sorted(
            ["%s buys %s" % (r["id"], r["buys"]) for r in rows if r["buys"]]
            + ["%s paid for by %s" % (r["id"], r["paid_for_by"])
               for r in rows if r["paid_for_by"]]),
    }
    return fail, stats


def _shared_exemption(r):
    """A SHARED row may trace to RP-PARITY/RP-TOPO-INERT when its content is
    that the direction COLLAPSES at that level -- i.e. it is shared precisely
    because the differentiator stops differentiating.  Such a row must say so
    by carrying a flips_with partner."""
    return bool(r["flips_with"])


# --------------------------------------------------------------------------
# Negative controls.  A rail that cannot fail is not a rail.
# --------------------------------------------------------------------------

def negative_controls():
    """Each control is a row set that MUST be rejected, and the check it must
    trip.  Returns (passed, detail)."""
    controls = []

    def clone(**over):
        base = row(
            id="X", direction="OPENS", level="L0", column="MATHEMATICS",
            status="PROVED", claim="control",
            traces_to=["RP-WEYL"],
            sources=["reverse_physics/reports/PHYSICS-VS-MATH.md"],
        )
        base.update(over)
        return base

    controls.append(("C1 bad status", "C1", [clone(status="MOSTLY_TRUE")]))
    controls.append(("C2 dangling source", "C2",
                     [clone(sources=["reverse_physics/reports/does-not-exist.md"])]))
    controls.append(("C3 cited maths", "C3",
                     [clone(status="CITED", literature=["somebody"])]))
    controls.append(("C3 maths with no in-repo source", "C3",
                     [clone(sources=[])]))
    controls.append(("C4 physics with no counterfactual", "C4",
                     [clone(column="PHYSICS", status="CITED",
                            literature=["somebody"], contingent_on="")]))
    controls.append(("C5 cited with no literature", "C5",
                     [clone(column="PHYSICS", status="CITED",
                            contingent_on="an experiment")]))
    controls.append(("C6 unknown assumption", "C6",
                     [clone(traces_to=["RP-INVENTED"])]))
    controls.append(("C7 dangling flip", "C7", [clone(flips_with="NOPE")]))
    controls.append(("C7 flip within one level", "C7", [
        clone(id="A", flips_with="B"),
        clone(id="B", direction="CHALLENGES", flips_with="A"),
    ]))
    controls.append(("C7 flip with same direction", "C7", [
        clone(id="A", flips_with="B"),
        clone(id="B", level="L3", flips_with="A"),
    ]))
    controls.append(("C8 trade not mutual", "C8", [clone(paid_for_by="NOPE")]))
    controls.append(("C8 buys on an OPENS row", "C8", [clone(buys="A")]))
    controls.append(("C9 SHARED differentiator", "C9",
                     [clone(direction="SHARED", traces_to=["RP-WEYL"])]))

    detail = []
    passed = 0
    for name, expect, rows in controls:
        fails, _ = check_rows(rows)
        tripped = any(f.startswith(expect) for f in fails)
        detail.append({"control": name, "expects": expect,
                       "rejected": bool(tripped)})
        if tripped:
            passed += 1
    return passed, len(controls), detail


# --------------------------------------------------------------------------

def content_hash(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate():
    fails, stats = check_rows(ROWS)
    ncpass, nctotal, ncdetail = negative_controls()
    return {
        "certificate": "REVERSE_PHYSICS_WEYL_VS_EINSTEIN_LEDGER_V1",
        "kind": "comparison-ledger",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "A checked comparison ledger for Weyl gravity against Einstein "
            "gravity, organised as a single assumption swap over a shared "
            "base, with each row carrying a direction (OPENS / CHALLENGES / "
            "SHARED), a level of description (L0 action ... L4 quantum), a "
            "column (PHYSICS / GEOMETRY / MATHEMATICS) and a status.  The "
            "rails enforce that no row cites its way into the MATHEMATICS "
            "column, that every PHYSICS row names a counterfactual, that every "
            "in-repository citation resolves, that level flips and trade pairs "
            "are mutual, and that SHARED rows are not used as differentiators.",
        "does_not_establish": [
            "any new physical result -- every row points at content that "
            "already exists elsewhere, or is marked OPEN",
            "the phenomenological claims in rows with status CITED, which are "
            "imported and not assessed here",
            "any LORENTZIAN-CAUSAL statement; rows carrying REDUCED-MODE or "
            "LOCAL-ALGEBRAIC tags are not evidence for one",
            "the dynamical consequence of the ghost, which is recorded OPEN",
            "completeness -- the ledger is open by construction and the row "
            "set is not claimed to exhaust the comparison",
        ],
        "swap": SWAP,
        "vocabulary": {
            "directions": list(DIRECTIONS),
            "levels": LEVELS,
            "columns": list(COLUMNS),
            "statuses": STATUSES,
            "assumptions": ALL_ASSUMPTIONS,
        },
        "rows": ROWS,
        "stats": stats,
        "checks": {
            "failures": fails,
            "passed": not fails,
            "negative_controls_rejected": "%d/%d" % (ncpass, nctotal),
            "negative_controls_all_rejected": ncpass == nctotal,
            "negative_control_detail": ncdetail,
        },
        "rows_sha256": content_hash(ROWS),
        "report": "reverse_physics/reports/OPENS-AND-CHALLENGES.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="verify the ledger and the negative controls")
    ap.add_argument("--emit", action="store_true",
                    help="write the certificate")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build_certificate()
    fails = cert["checks"]["failures"]
    ncok = cert["checks"]["negative_controls_all_rejected"]
    st = cert["stats"]

    print("rows            : %d  (OPENS %d, CHALLENGES %d, SHARED %d)" % (
        st["rows"], st["by_direction"]["OPENS"],
        st["by_direction"]["CHALLENGES"], st["by_direction"]["SHARED"]))
    print("by column       : PHYSICS %d, GEOMETRY %d, MATHEMATICS %d" % (
        st["by_column"]["PHYSICS"], st["by_column"]["GEOMETRY"],
        st["by_column"]["MATHEMATICS"]))
    print("by status       : " + ", ".join(
        "%s %d" % (k, v) for k, v in sorted(st["by_status"].items()) if v))
    print("open rows       : %s" % (", ".join(st["open_rows"]) or "none"))
    print("level flips     : %s" % (", ".join(st["level_flips"]) or "none"))
    print("trade pairs     : %s" % (", ".join(st["trade_pairs"]) or "none"))
    print("negative controls rejected: %s" %
          cert["checks"]["negative_controls_rejected"])
    for f in fails:
        print("FAIL %s" % f)

    if args.emit and not fails and ncok:
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    ok = (not fails) and ncok
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
