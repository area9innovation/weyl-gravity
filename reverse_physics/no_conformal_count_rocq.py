"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsNoConformalCount.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.no_conformal_count_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_NO_CONFORMAL_COUNT_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_NO_CONFORMAL_COUNT_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-no-conformal-count-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsNoConformalCount.v"}

THEOREMS = [
    {
        "name": "dilation_invariance",
        "statement": "naturality plus constant Weyl invariance imply invariance under dilations of flat space",
        "role": "a dilation pulls the flat metric back to a constant multiple of itself, so the two hypotheses compose",
    },
    {
        "name": "every_ball_has_the_same_count",
        "statement": "on flat space every ball has the count of the unit ball, whatever its radius",
    },
    {
        "name": "count_is_bounded_independently_of_the_region",
        "statement": "with monotonicity and mu(point) = 1, every nonempty bounded region has count between 1 and the unit ball's",
        "role": "the count is bounded by a universal constant that does not depend on the region",
    },
    {
        "name": "no_informative_conformal_count",
        "statement": "any two balls have equal count",
        "role": "THE REFUTATION. Additivity appears nowhere, which is exactly why the non-additive branch does not escape.",
    },
    {
        "name": "a_unit_ball_and_a_cosmological_ball_count_the_same",
        "statement": "the unit ball and a ball of radius 10^100 receive the same count",
        "role": "the concrete form, to make the failure legible",
    },
]

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
        "result_state": "NO_INFORMATIVE_CONFORMALLY_INVARIANT_DOF_COUNT_EXISTS_ADDITIVE_OR_NOT",
        "generality_level": "G3_ANY_NATURAL_WEYL_INVARIANT_COUNT_ON_FLAT_SPACE",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT \u2014 the mathematics is in rocq/ReversePhysicsNoConformalCount.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-CONFORMAL-INVARIANCE"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_NONADDITIVE_CONFORMAL_COUNT",
            "opened_by": "REVERSE_PHYSICS_CONFORMAL_COUNT_ROCQ_V1",
            "how": "That certificate closed the density branch by parity and left the non-additive branch as the only place an answer could live. This REFUTES it. Additivity is never used in the argument, which is exactly why the non-additive resolution does not escape.",
            "outcome": "REFUTED rather than constructed. The gate asked to construct or refute; the answer is refute.",
        },
        "the_argument": {
            "where": "flat space -- a Minkowski slice, certainly a physical configuration, so any proposed count must behave sensibly there",
            "step": "a dilation phi_lam(x) = lam x pulls the flat metric back to a CONSTANT rescaling, phi_lam^* delta = lam^2 delta. Naturality then turns a dilation of the region into a rescaling of the metric, and constant Weyl invariance kills it.",
            "conclusion": "mu(ball of radius lam) = mu(unit ball) for every lam > 0",
            "why_additivity_is_irrelevant": "it is never used; the argument is a group action on regions, not a decomposition of them",
        },
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "All three branches of the Carcassi-Aidala degree-of-freedom trilemma are closed under conformal invariance.",
            "table": [
                "drop 1, a density measure: excluded by parity in odd dimension (REVERSE_PHYSICS_CONFORMAL_COUNT_ROCQ_V1)",
                "drop 2, the counting measure: invariant but uninformative, every infinite region alike",
                "drop 3, a non-additive count: excluded here, and equally uninformative -- every ball ties",
            ],
            "reading": (
                "The honest reading is not that the count is hard to construct. It is that in a conformally "
                "invariant theory, 'how many degrees of freedom are in this region' is not a well-posed "
                "question. A quantity assigning the same value to a unit ball and a ball of radius 10^100 is "
                "not counting anything."
            ),
            "consequence_for_their_conjecture": (
                "Their conjecture 'GR <=> det/rev + DOF independence for infinitely many dense DOFs' is stated "
                "in terms of a DOF count. In a conformally invariant setting no such count exists, so the "
                "conjecture cannot be transported to conformal gravity as written -- not because the count is "
                "unknown but because it cannot exist."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "5/5 for this module; 84/84 across the eleven modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none \u2014 no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit; every geometric input is an explicit hypothesis of the theorem statements",
        },
        "gate_result": "RESULT: 16 green (0 red) \u2014 GATE: PASS",
        "gate_negative_controls": [
            "ten inherited from the earlier modules, all rejected",
            "a FALSE claim that a conformally invariant count grows with the radius is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "additivity_never_used": True,
            "only_constant_rescalings_used": True,
            "geometric_inputs_are_explicit_hypotheses": True,
        },
        "claim_flags": {
            "NON_ADDITIVE_BRANCH_REFUTED": True,
            "ALL_THREE_BRANCHES_CLOSED": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "GEOMETRIC_INPUTS_DERIVED_FROM_DIFFERENTIAL_GEOMETRY": False,
            "CURVED_OR_NON_CONFORMALLY_FLAT_CASE_ADDRESSED": False,
            "NON_CONSTANT_RESCALINGS_ADDRESSED": False,
            "EXTRA_STRUCTURE_CASE_ADDRESSED": False,
            "CLAIM_ABOUT_GR_OR_ITS_DYNAMICS": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development, any region-count on flat space that is natural under "
            "diffeomorphisms and invariant under constant Weyl rescaling assigns the same value to every ball "
            "regardless of radius; with monotonicity and unit value on points, every nonempty bounded region is "
            "squeezed into a fixed interval. Additivity is never used, so the non-additive branch is refuted "
            "along with the additive ones."
        ),
        "does_not_establish": [
            "the geometric inputs from differential geometry. That a dilation pulls the flat metric back to a constant multiple, that balls are dilations of the unit ball, that a bounded region contains a point and sits inside a ball -- all are explicit HYPOTHESES of the theorems, not derived here",
            "anything about curved or non-conformally-flat configurations. The argument runs on flat space, which suffices because flat space is a physical configuration any count must handle",
            "anything about non-constant conformal factors",
            "that there are NO conformal invariants on a 3-manifold. There are: the gravitational Chern-Simons invariant is a global conformal invariant of oriented Riemannian 3-manifolds (Chern and Simons, Ann. Math. 1974). It is not a local density, so the parity argument does not reach it; and it is real-valued modulo a framing ambiguity, not monotone, not positive and not region-additive, so it is not a COUNT. It bounds what these results claim rather than contradicting them",
            "anything about counts using EXTRA STRUCTURE. A compensator or dilaton breaks naturality-plus-Weyl-invariance by choosing a scale, which is what conformal invariance forbids; that fork is stated, not resolved",
            "any claim about general relativity or its dynamics",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation. It engages one conjecture from one talk",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_WHAT_REPLACES_A_COUNT: if a region-count cannot exist in a conformally invariant theory, what does the DOF-independence assumption become? A relational or ratio-valued notion is the obvious candidate and is not explored here.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.no_conformal_count_rocq --check",
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
    print(f"{RESULT_ID}: PASS (pinned Rocq proof hash-verified)")


if __name__ == "__main__":
    main()
