"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsEntropyConverse.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.entropy_converse_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_ENTROPY_CONVERSE_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_ENTROPY_CONVERSE_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-entropy-converse-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsEntropyConverse.v"}

THEOREMS = [
    {"name": "cancel_pos_r", "statement": "a positive factor can be cancelled from a vanishing product"},
    {"name": "row_deficit_nonneg", "statement": "every row deficit is nonnegative"},
    {
        "name": "total_deficit",
        "statement": "purity p - purity (M p) is the sum of the four row deficits",
        "role": "column sums enter here and only here: they are what lets the input purity be rewritten as a double sum",
    },
    {
        "name": "each_row_deficit_zero",
        "statement": "if purity is preserved then every row deficit vanishes",
        "role": "four nonnegative quantities summing to zero -- the step that exhausted memory on the first attempt and is cheap once the terms are kept opaque",
    },
    {"name": "p_test_sq_pos", "statement": "distinct entries give strictly positive squared differences"},
    {
        "name": "pair_products_vanish",
        "statement": "a vanishing row deficit forces every off-diagonal coefficient product in that row to vanish",
    },
    {
        "name": "row_is_point_mass",
        "statement": "a nonnegative row summing to one whose off-diagonal products vanish is a point mass",
    },
    {
        "name": "purity_preserved_forces_reversible",
        "statement": "preserving purity on ONE distribution with distinct entries forces reversibility",
        "role": "THE CONVERSE. Reconstructs the permutation via col_arg and proves it injective.",
    },
    {
        "name": "no_entropy_production_iff_reversible",
        "statement": "for doubly stochastic M: reversible M <-> purity is preserved on p_test",
        "role": "THE BICONDITIONAL. The loop between this stream's two laws is closed.",
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
        "result_state": "NO_ENTROPY_PRODUCTION_IFF_REVERSIBLE_BICONDITIONAL_ESTABLISHED",
        "generality_level": "G1_FOUR_STATE_STOCHASTIC_EVOLUTION_ONE_STEP_RENYI_2",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "EQUIVALENCE_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT \u2014 the mathematics is in rocq/ReversePhysicsEntropyConverse.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-REVERSIBLE", "RP-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_ENTROPY_CONVERSE",
            "opened_by": "REVERSE_PHYSICS_ENTROPY_EQUALITY_ROCQ_V1",
            "how": "That certificate proved the forward direction and recorded the converse as not done, naming the cause (a case analysis that exhausted memory) and the cheaper route. This file takes that route: keep the deficit terms OPAQUE and split the sum ONCE rather than per case. It compiled in 2.2 s.",
        },
        "why_the_first_attempt_failed": (
            "The abandoned proof case-split over (row, pair, pair) with the test distribution's values expanded "
            "by 'compute in *', producing enormous goals; coqc was killed after 2m40s. The repair is entirely "
            "structural: row_deficit_expr stays a folded Definition, p_test stays opaque and is used only "
            "through p_test_sq_pos, and the four-way split happens once in each_row_deficit_zero on four atoms."
        ),
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "For doubly stochastic evolution, reversibility and the absence of entropy production are the same condition.",
            "detail": (
                "Forward, nothing is lost because nothing is mixed. Backward, any mixing shows up as a strictly "
                "positive deficit, so preserving purity forces every row to be a point mass; unit column sums "
                "then make the resulting map a permutation."
            ),
            "one_distribution_suffices": (
                "No quantification over distributions is needed: a single p with pairwise distinct entries "
                "detects every failure, because no squared difference can be the vanishing factor. The gate "
                "carries a negative control showing this is essential -- every doubly stochastic map preserves "
                "the UNIFORM distribution exactly, so a uniform test would prove nothing."
            ),
            "lattice_status": (
                "The stream's two laws are now linked in BOTH directions on this carrier. conserves_information "
                "makes reversibility redundant and entails the arrow of disorder; and reversibility is exactly "
                "the absence of entropy production. This is the first closed loop in the lattice rather than a "
                "directed edge."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "10/10 for this module; 71/71 across the eight modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none \u2014 no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 13 green (0 red) \u2014 GATE: PASS",
        "gate_negative_controls": [
            "seven inherited from the earlier modules, all rejected",
            "a FALSE claim that a UNIFORM test distribution suffices is REJECTED -- the mixer preserves it exactly and is not reversible, which is why p_test has distinct entries",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "no_logarithms_anywhere": True,
            "biconditional_proved_in_both_directions": True,
            "necessity_of_a_distinguishing_test_distribution_shown_by_control": True,
        },
        "claim_flags": {
            "BICONDITIONAL_ESTABLISHED": True,
            "CONVERSE_ESTABLISHED": True,
            "PERMUTATION_RECONSTRUCTED": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "SHANNON_ENTROPY_FORMALISED": False,
            "GENERAL_FINITE_STATE_SPACE_COVERED": False,
            "MULTI_STEP_OR_EQUILIBRATION_COVERED": False,
            "TRANSFERS_TO_THE_HAMILTONIAN_CARRIERS": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "On a four-state space with one step of doubly stochastic evolution over Q, in a zero-axiom Rocq "
            "development kernel-rechecked by coqchk, an evolution is reversible if and only if it preserves "
            "purity on a distribution with pairwise distinct entries. Both directions are proved and the "
            "permutation is explicitly reconstructed."
        ),
        "does_not_establish": [
            "anything about SHANNON entropy; Renyi-2 purity only",
            "a general finite state space; the proof is written for four states and the case analyses are sized to it",
            "anything about many steps, equilibration, or approach to the uniform distribution",
            "any transfer to the Hamiltonian carriers of the other certificates",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_STOCHASTIC_GENERAL_N: lift the four-state case analyses to a general finite state space. This is a refinement, not a new finding.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.entropy_converse_rocq --check",
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
