"""Provenance record: THE UNIQUENESS THEOREM AND THE GHOST THEOREM ARE THE SAME.

REVERSE_PHYSICS_WEYL_ACTION_V1 classified the Weyl action. On its own that is a
textbook result and casts no new light. This record is the composition that does:
the same five assumptions that make the action unique also FORCE the Ostrogradsky
ghost, in every dimension where the action is non-trivial -- so the ghost cannot
be tuned away by choosing a better conformal action, because there is no other
conformal action.

Computes no mathematics. The theorems live in `rocq/WeylGhostForced.v`; the
independent exact-rational rail lives in tango
`forge/examples/weyl_ghost_forced_gate.forge`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_ghost_forced --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1.json"

RESULT_ID = "REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1"
SCHEMA_NAME = "reverse-physics-weyl-ghost-forced-v1"

PINNED = {
    "ghost_forced": ROOT / "rocq/WeylGhostForced.v",
    "classification": ROOT / "rocq/WeylActionClassification.v",
}

UPSTREAM_GATE = {
    "path": "tango forge/examples/weyl_ghost_forced_gate.forge",
    "sha256": "1a35bf0aaed39202a2e4d5f1e49e3560bdabea8d87a2a341c68bf285130681d4",
    "result": "exit 26, 26/26 checks; forge verify -full: c==native, ASan-clean on both backends",
    "why_it_is_a_second_rail": (
        "Different METHOD. The Rocq rail proves the residue signs from division-free sign lemmas "
        "over Q, never computing a residue. The Forge rail EVALUATES the residues as exact "
        "rationals for pole counts 1 through 6 and checks the partial-fraction identity itself by "
        "clearing denominators at five rational points. One argues about signs; the other computes "
        "the numbers."
    ),
    "what_the_second_rail_caught": (
        "The first version of the Forge residue used prod_{j != i} (r_j - r_i) instead of "
        "prod_{j != i} (r_i - r_j) -- off by (-1)^(n-1). The sign-alternation checks still passed; "
        "the partial-fraction identity check failed and located it. That is the difference between "
        "a check on the answer and a check on the object."
    ),
    "not_verified_here": (
        "the digest is recorded, not re-checked -- the file is in another repository. "
        "Re-derive it with sha256sum before trusting this line."
    ),
}

PHYSICS_INPUTS = {
    "O1": "a pole with negative residue in the propagator is a negative-norm state -- a ghost. Standard, and the whole physical reading rests on it.",
    "O2": "a conformally invariant curvature-degree-k action has a linearised kinetic operator of order 2k, hence k poles in k^2. Standard power counting. Carried as the EXPLICIT hypothesis two_distinct_poles, so the dependency appears in the statement of the theorem rather than in prose.",
    "O3": "Weyl gravity's own case is the DEGENERATE limit of the generic split: the kinetic operator is Box^2, the propagator 1/k^4, a double pole at k^2 = 0. That is a dipole ghost -- a Jordan block, not a diagonalisable pair -- which is WORSE than the generic case, not better. Riegert 1984; the 6 = 2 + 4 degree-of-freedom count.",
    "O4": "in two dimensions sqrt(-g) R is the Euler density, hence topological. This is what makes the single-pole case empty rather than interesting.",
}

THEOREMS = [
    {
        "name": "two_poles_have_opposite_residues",
        "statement": "two distinct simple poles always have residues of opposite sign, for EVERY placement",
        "role": "THE MECHANISM. A fourth-order propagator cannot be made ghost-free by tuning masses -- there is no choice of pole locations that avoids it. Division-free over Q.",
    },
    {
        "name": "three_poles_have_a_negative_middle_residue",
        "statement": "with three poles the middle residue is negative",
        "role": "adding poles never rescues the situation; the signs alternate. This is the D = 6 case.",
    },
    {
        "name": "one_pole_has_a_positive_residue",
        "statement": "a single simple pole has a positive residue",
        "role": "NON-VACUITY. Without it, 'a negative residue appears at two poles' would be a claim about a predicate that is negative everywhere, and the D = 2 case would not be genuinely different.",
    },
    {
        "name": "pole_count_is_half_the_dimension",
        "statement": "the conformal weight law D - 2k = 0 gives 2 * pole_count = D",
        "role": "THE BRIDGE FROM THE CLASSIFICATION. The same equation that forces the derivative order forces the pole count. This is where the two results become one.",
    },
    {
        "name": "at_least_two_poles_above_dimension_two / single_pole_iff_dimension_two",
        "statement": "two or more poles for every even D >= 4, and exactly one at D = 2",
        "role": "the threshold is sharp, and the ghost-free case is D = 2 alone -- where the action is sqrt(-g) R, topological by O4. The only ghost-free member of the family is empty.",
    },
    {
        "name": "the_uniqueness_theorem_is_the_ghost_theorem",
        "statement": "if D >= 4 and the weight law holds, then a residue is negative",
        "role": "THE COMPOSITION, and it is a real one: D >= 4 plus the weight law give the pole count, the pole count discharges the O2 bridge, and the bridge feeds the residue lemma. Nothing is decoration.",
    },
    {
        "name": "at_dimension_two_the_bridge_is_vacuous",
        "statement": "at D = 2 the two-pole hypothesis cannot be satisfied",
        "role": "the dimension hypothesis is doing work: the theorem does not secretly apply to everything.",
    },
    {
        "name": "raising_the_dimension_adds_poles",
        "statement": "D >= 6 forces three or more poles",
        "role": "ESCAPE LATTICE. Dropping RP-DIM4 upward makes the ghost WORSE, not better.",
    },
    {
        "name": "dropping_weyl_invariance_leaves_the_pole_count_at_two",
        "statement": "quadratic gravity is still curvature degree two, hence still fourth order",
        "role": "ESCAPE LATTICE. Dropping RP-WEYL does not remove the ghost -- this is why Stelle gravity is renormalisable and still has one.",
    },
]

ESCAPE_LATTICE = {
    "question": "the ghost is forced by RP-LOCAL, RP-METRIC, RP-DIFF, RP-WEYL, RP-DIM4. Which of the five, if dropped, could remove it?",
    "settled_here_by_arithmetic": {
        "RP-WEYL": "NO. Quadratic gravity keeps curvature degree 2, hence fourth order, hence the pole count and the ghost. Stelle 1977.",
        "RP-DIM4": "NO, and worse. D = 6 forces curvature degree 3, sixth order, three poles.",
    },
    "not_settled_here": {
        "RP-LOCAL": "PLAUSIBLY YES, but this is a citation, not a theorem. Infinite-derivative (nonlocal) gravity with an entire-function form factor has no extra poles and is advertised as ghost-free -- Biswas, Mazumdar, Siegel and the subsequent literature. Nothing in this development touches nonlocal actions.",
        "RP-METRIC": "PLAUSIBLY YES, same status. A conformal theory built with a compensator scalar can be second order, hence single-pole. Nothing here covers multi-field actions.",
        "RP-DIFF": "not analysed. It is what makes the space of curvature scalars the right space at all, so it has no witness in this framework -- an acknowledged gap.",
    },
    "the_point": (
        "The interesting content is the NEGATIVE half. It is routine to hope that some variant of "
        "conformal gravity is ghost-free; the arithmetic says the two most natural variations -- "
        "weaken the symmetry, or change the dimension -- provably do not help. That narrows where "
        "to look to locality and field content, both of which leave the theory this repository is "
        "about."
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    manifest = {}
    for name, path in PINNED.items():
        if not path.exists():
            raise AssertionError(f"pinned {name} missing at {path}")
        manifest[str(path.relative_to(ROOT))] = sha(path)

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_state": "UNIQUENESS_AND_GHOST_IDENTIFIED_AS_ONE_THEOREM",
        "generality_level": "G4_ALL_EVEN_DIMENSIONS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "PROVENANCE_IMPORT -- the mathematics is in rocq/WeylGhostForced.v and tango "
            "forge/examples/weyl_ghost_forced_gate.forge; this file computes nothing"
        ),
        "assumption_tags": {
            "under_test": ["RP-WEYL", "RP-DIM4", "RP-LOCAL", "RP-METRIC", "RP-NO-GHOST"],
            "consumed": ["RP-LOCAL", "RP-METRIC", "RP-DIFF", "RP-WEYL", "RP-DIM4"],
            "namespace_note": (
                "This is a NO-GO in the reverse-physics currency: the assumption set that makes the "
                "Weyl action unique is INCOMPATIBLE with RP-NO-GHOST. RP-NO-GHOST is under test in "
                "the sense that it is refuted relative to the others, not confirmed."
            ),
        },
        "builds_on": "REVERSE_PHYSICS_WEYL_ACTION_V1",
        "why_this_one_casts_new_light": (
            "The classification alone is textbook and, honestly reported, told nobody anything they "
            "did not know -- the value there was the ledger, which is methodological. This is the "
            "composition the ledger pointed at, and it is a statement about the subject: the "
            "uniqueness theorem and the ghost theorem are the SAME theorem. Both follow from the "
            "single equation D - 2k = 0. Because the action is unique, the ghost cannot be tuned "
            "away by choosing a better conformal action; and because dropping RP-WEYL or RP-DIM4 "
            "provably does not help, the only places left to look are locality and field content."
        ),
        "physics_asserted_not_derived": PHYSICS_INPUTS,
        "escape_lattice": ESCAPE_LATTICE,
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "14/14 in WeylGhostForced.v; 187/187 across the twenty modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none -- no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
            "rationals_not_reals": "the residue arithmetic is over Q and division-free. Coq's R is axiomatised and would put axioms in the ledger for statements that are rational-linear.",
        },
        "gate_result": "RESULT: 25 green (0 red) -- GATE: PASS",
        "upstream_gate": UPSTREAM_GATE,
        "gate_negative_controls": [
            "twenty-three inherited from the earlier modules, all rejected",
            "a FALSE claim that two distinct simple poles can both have positive residues is REJECTED -- that impossibility IS the ghost, and without it a fourth-order propagator could be tuned ghost-free",
            "a FALSE claim that a single pole has a negative residue is REJECTED -- otherwise the D = 2 case would not be genuinely different and the threshold at D = 4 would be meaningless",
            "the Forge rail carries its own: the one-pole case is asserted to have NO negative residue, and the partial-fraction identity is checked at five rational points for every pole count -- which is what caught a sign error in the residue formula that the alternation checks alone had passed",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
            "upstream_repo": "tango (forge/examples)",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "exact_rational_arithmetic_upstream": True,
            "no_floating_point": True,
            "two_independent_methods": True,
        },
        "claim_flags": {
            "UNIQUENESS_AND_GHOST_SHOWN_TO_SHARE_ONE_EQUATION": True,
            "GHOST_FORCED_IN_EVERY_NONTRIVIAL_DIMENSION": True,
            "DROPPING_RP_WEYL_SHOWN_NOT_TO_HELP": True,
            "DROPPING_RP_DIM4_SHOWN_NOT_TO_HELP": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "LINEARISED_ANALYSIS_OF_WEYL_GRAVITY_PERFORMED": False,
            "PROPAGATOR_COMPUTED": False,
            "DEGREE_OF_FREEDOM_COUNT_DERIVED": False,
            "NONLOCAL_OR_MULTIFIELD_ESCAPE_ROUTES_TESTED": False,
            "DEGENERATE_DIPOLE_CASE_PROVED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development over Q, and independently by exact rational residue "
            "evaluation in Forge: two or more distinct simple poles always include one with a "
            "negative residue; the conformal weight law D - 2k = 0 forces the pole count to be D/2; "
            "hence two or more poles for every even D >= 4, with D = 2 the unique single-pole case. "
            "Composed with the standard readings O1-O4, this says the assumption set that determines "
            "the Weyl action uniquely also forces an Ostrogradsky ghost in every dimension where the "
            "action is non-trivial. Dropping RP-WEYL leaves the curvature degree at two and dropping "
            "RP-DIM4 upward raises the pole count, so neither removes the ghost."
        ),
        "does_not_establish": [
            "any linearised analysis of Weyl gravity. No gauge fixing is performed, no propagator is computed, no degree-of-freedom count is derived. What is proved is a statement about pole counts and residue signs; everything connecting it to 'Weyl gravity has a ghost' is O1-O3, asserted",
            "the DEGENERATE case, which is the one that actually occurs. Weyl gravity's kinetic operator is Box^2, a DOUBLE pole at k^2 = 0, not two distinct simple poles. That it is a dipole ghost and therefore no better is O3, cited to Riegert 1984, not proved here. The theorems cover the generic split of which it is the limit",
            "that dropping RP-LOCAL or RP-METRIC actually removes the ghost. Those are citations to the nonlocal-gravity and compensator literature, recorded in escape_lattice.not_settled_here, and nothing in this development touches either class of action",
            "novelty of the ingredients. That a fourth-order propagator has a ghost is Ostrogradsky and Stelle; that the Weyl action is unique is textbook. The composition, the sharp dimension threshold, and the arithmetic half of the escape lattice are what this record adds",
            "anything about the BV-BFV complex, the residual classes, the physical spectrum, or the quantum theory. This is the LINEARISED CLASSICAL propagator. The programme's two scoped Lorentzian no-go theorems are neither used nor affected",
        ],
        "next_gate": (
            "WEYL_GHOST_DEGENERATE_LIMIT: prove the dipole case directly rather than citing it. The "
            "object is 1/k^4 -- a double pole -- and the statement to prove is that the Jordan block "
            "admits no positive-definite inner product, which is exact linear algebra over Q on a "
            "2x2 nilpotent block and is squarely in range. That would move O3 from the asserted "
            "column to the proved one, and O3 is currently the load-bearing citation for the case "
            "that actually occurs."
        ),
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.weyl_ghost_forced --check",
            "cd forge && FORGE_LIB=$PWD/lib forge -run examples/weyl_ghost_forced_gate.forge   # exit 26",
            "cd forge && FORGE_LIB=$PWD/lib forge verify -full examples/weyl_ghost_forced_gate.forge",
            "sha256sum forge/examples/weyl_ghost_forced_gate.forge   # must match upstream_gate.sha256",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    else:
        if not OUTPUT.exists():
            raise AssertionError(f"{RESULT_ID} record missing")
        recorded = json.loads(OUTPUT.read_text(encoding="utf-8"))
        for path, digest in recorded["provenance"]["source_manifest"].items():
            actual = sha(ROOT / path)
            if actual != digest:
                raise AssertionError(f"pinned source DRIFTED: {path} is {actual}, expected {digest}")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise AssertionError(f"{RESULT_ID} record is stale")
    print(f"{RESULT_ID}: PASS (pinned Rocq proofs hash-verified)")


if __name__ == "__main__":
    main()
