"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsConformalCount.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.conformal_count_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_CONFORMAL_COUNT_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_CONFORMAL_COUNT_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-conformal-count-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsConformalCount.v"}

THEOREMS = [
    {
        "name": "curvature_scalar_weight_is_even",
        "statement": "every polynomial curvature scalar has EVEN conformal weight, namely -(2m + D)",
        "role": "the structural fact the whole obstruction rests on; D is even because every index is contracted in a pair",
    },
    {
        "name": "conformal_density_iff_balance",
        "statement": "a density is conformally invariant exactly when 2m + D = d",
        "role": "the volume element carries weight +d, so invariance is weight cancellation",
    },
    {
        "name": "conformal_density_forces_even_dimension",
        "statement": "a conformally invariant density forces the dimension to be even",
    },
    {
        "name": "no_conformal_density_in_odd_dimension",
        "statement": "in odd dimension no curvature scalar balances the volume weight",
        "role": "THE OBSTRUCTION, by parity rather than by accident",
    },
    {
        "name": "no_conformal_dof_density_on_a_cauchy_surface",
        "statement": "no conformally invariant degree-of-freedom density exists on a three-manifold",
        "role": "a Cauchy surface is three-dimensional, and three is odd; this is the case the Carcassi-Aidala GR conjecture needs",
    },
    {
        "name": "dimension_four_balance",
        "statement": "in dimension four the balance requires 2m + D = 4",
    },
    {
        "name": "weyl_squared_is_a_conformal_density_in_dimension_four",
        "statement": "(m, D) = (2, 0) balances in dimension four",
        "role": "that is the weight carried by C_abcd C^abcd, the conformally invariant action of Weyl gravity",
    },
    {
        "name": "weyl_squared_is_not_one_in_dimension_three",
        "statement": "and the same weights do not balance on a Cauchy surface",
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
        "result_state": "CONFORMAL_INVARIANCE_EXCLUDES_THE_DENSITY_BRANCH_OF_THE_DOF_COUNTING_TRILEMMA_IN_ODD_DIMENSION",
        "generality_level": "G3_ALL_POLYNOMIAL_CURVATURE_SCALARS_ALL_DIMENSIONS_CONSTANT_RESCALING",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT \u2014 the mathematics is in rocq/ReversePhysicsConformalCount.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-CONFORMAL-INVARIANCE"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
            "new_tag_note": "RP-CONFORMAL-INVARIANCE is introduced by this certificate: physically equivalent configurations, related by a Weyl rescaling, must receive the same count.",
        },
        "what_it_engages": {
            "target": "the degree-of-freedom counting trilemma in Carcassi and Aidala, Reverse Physics for GR (Michigan, 16 Nov 2024)",
            "their_trilemma": [
                "every point is a single DOF",
                "finite volume carries finitely many DOFs",
                "the count is additive for disjoint regions",
            ],
            "their_resolutions": "drop 1 -> a density measure; drop 2 -> the counting measure; drop 3 -> a non-additive quantum measure. They drop 3 for quantum mechanics and conjecture quantum gravity does the same for the DOF count.",
            "our_addition": "conformal invariance is not a fourth item in the trilemma but a FILTER on which resolutions are admissible, and it is not idle: it closes the density branch in odd dimension.",
        },
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "In odd dimension there is no conformally invariant density built from the metric alone. A Cauchy surface is three-dimensional.",
            "why_parity": (
                "Under g -> Omega^2 g with constant Omega, a polynomial curvature scalar with m curvature "
                "factors and D derivative indices has weight -(2m + D), and D is even because every index is "
                "contracted in a pair. So every such weight is even. The volume element has weight +d. "
                "Invariance requires 2m + D = d, which has no solution for odd d."
            ),
            "consequence": (
                "An informative and conformally invariant DOF count must be NON-ADDITIVE: the density branch is "
                "closed by parity and the counting branch carries no information. That is the same branch "
                "quantum mechanics forced them to, reached here by a purely classical symmetry with no quantum "
                "input."
            ),
            "the_weyl_connection": (
                "In dimension four the balance IS achievable: 2m + D = 4 admits (m, D) = (2, 0), a quadratic "
                "curvature invariant -- exactly the weight of C_abcd C^abcd, the conformally invariant action of "
                "Weyl gravity. Conformal gravity is the even-dimensional case where a conformal density exists; "
                "a Cauchy surface is the odd-dimensional case where it cannot."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "8/8 for this module; 79/79 across the ten modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none \u2014 no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 15 green (0 red) \u2014 GATE: PASS",
        "gate_negative_controls": [
            "nine inherited from the earlier modules, all rejected",
            "a FALSE claim that a conformally invariant density exists in dimension three is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "obstruction_is_a_parity_argument_not_a_case_check": True,
            "even_dimensional_counterpart_exhibited": True,
        },
        "claim_flags": {
            "DENSITY_BRANCH_EXCLUDED_IN_ODD_DIMENSION": True,
            "CAUCHY_SURFACE_CASE_SETTLED": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "NON_ADDITIVE_COUNT_CONSTRUCTED": False,
            "NON_ADDITIVE_COUNT_RULED_OUT": False,
            "REALISABILITY_OF_WEIGHTS_ADDRESSED": False,
            "NON_CONSTANT_RESCALINGS_ADDRESSED": False,
            "EXTRA_STRUCTURE_CASE_ADDRESSED": False,
            "CLAIM_ABOUT_GR_OR_ITS_DYNAMICS": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development, no polynomial curvature scalar balances the volume weight in odd "
            "dimension, so no conformally invariant degree-of-freedom density built from the metric alone exists "
            "on a Cauchy surface. In dimension four the balance is achievable and is the Weyl-squared weight."
        ),
        "does_not_establish": [
            "that a non-additive conformally invariant count exists. The density branch is closed; the non-additive branch is neither constructed nor ruled out",
            "anything about densities built with EXTRA STRUCTURE. A compensator or dilaton of nonzero weight evades the parity argument -- by choosing a scale, which is what conformal invariance forbids. That fork is stated, not resolved",
            "REALISABILITY. The arithmetic says which weights are available, not which (m, D) are realised by an actual invariant. The negative result needs only the necessary condition and is unaffected; the dimension-four positive statement is about weights, not about a constructed invariant",
            "anything about non-constant conformal factors. The weight bookkeeping is for constant Omega; a full treatment carries derivative-of-Omega terms",
            "that there are NO conformal invariants on a 3-manifold. There are: the gravitational Chern-Simons invariant is a global conformal invariant of oriented Riemannian 3-manifolds (Chern and Simons, Ann. Math. 1974). It is not a local density, so the parity argument does not reach it; and it is real-valued modulo a framing ambiguity, not monotone, not positive and not region-additive, so it is not a COUNT. It bounds what these results claim rather than contradicting them",
            "any claim about general relativity or its dynamics. Conformal weights are kinematic",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_NONADDITIVE_CONFORMAL_COUNT: the density branch is closed and the counting branch is uninformative, so construct or refute a non-additive conformally invariant DOF count. That is the constructive half and it is open.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.conformal_count_rocq --check",
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
