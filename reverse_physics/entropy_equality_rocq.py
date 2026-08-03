"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsEntropyEquality.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.entropy_equality_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_ENTROPY_EQUALITY_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_ENTROPY_EQUALITY_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-entropy-equality-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsEntropyEquality.v"}

THEOREMS = [
    {
        "name": "sparse_square",
        "statement": "with the underlying map injective, squaring a row's sum equals summing the squares",
        "role": "the whole reason a relabelling is entropy-neutral: at most one term survives, so nothing is mixed",
    },
    {
        "name": "reversible_preserves_purity",
        "statement": "reversible evolution preserves purity EXACTLY",
        "role": "THE RESULT. This is precisely what REVERSE_PHYSICS_SECOND_LAW_ROCQ_V1 recorded as not proved.",
    },
    {
        "name": "row_deficit",
        "statement": "the purity lost in a row is exactly sum_{j<k} M_ij M_ik (p_j - p_k)^2",
        "role": "jensen4_identity with the row sum set to one; where all the content of the equality case lives",
    },
    {
        "name": "spreading_produces_entropy",
        "statement": "a row putting positive weight on two states of differing probability has strictly positive deficit",
        "role": "the mathematical content of the converse, stated positively and proved",
    },
    {"name": "mul_pos2", "statement": "products of positives are positive"},
    {"name": "mul_pos3", "statement": "the three-factor version"},
    {"name": "sq_pos", "statement": "the square of a nonzero difference is positive"},
    {"name": "evolve_congr", "statement": "evolution respects pointwise equality of matrices"},
    {"name": "purity_congr", "statement": "purity respects pointwise equality of distributions"},
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
        "result_state": "REVERSIBLE_EVOLUTION_PRESERVES_PURITY_EXACTLY_CONVERSE_NOT_ESTABLISHED",
        "generality_level": "G1_FOUR_STATE_STOCHASTIC_EVOLUTION_ONE_STEP_RENYI_2",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT \u2014 the mathematics is in rocq/ReversePhysicsEntropyEquality.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-REVERSIBLE", "RP-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_ENTROPY_EQUALITY",
            "opened_by": "REVERSE_PHYSICS_SECOND_LAW_ROCQ_V1",
            "how": "PARTIALLY. That certificate recorded 'reversible evolution PRESERVES purity exactly is not proved'. It is now proved. The biconditional it also named is NOT established -- see partial_closure below.",
        },
        "partial_closure": {
            "established": "reversible ==> purity preserved exactly, and the strict mechanism of the converse (spreading over states of differing probability strictly produces entropy)",
            "not_established": "the converse itself: purity preserved ==> reversible",
            "what_the_converse_needs": [
                "(a) extracting from the vanishing TOTAL deficit that each of the twenty-four nonnegative terms vanishes, hence that every row has at most one nonzero entry",
                "(b) reconstructing the permutation from row sparsity plus unit column sums",
            ],
            "why_it_is_not_done": (
                "Step (a) was attempted and abandoned: the case analysis over (row, pair, pair) with the test "
                "distribution's values expanded exhausted memory (coqc killed after 2m40s). A cheaper route "
                "exists -- keep the twenty-four terms opaque and split the sum once rather than per case -- but "
                "it is not done here. This is recorded rather than quietly dropped."
            ),
        },
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "Reversible evolution is exactly entropy-neutral, and mixing is exactly what produces entropy.",
            "detail": (
                "sparse_square is the mechanism: with the underlying map injective at most one term of each row "
                "survives, so squaring the sum is the same as summing the squares. Nothing is lost because "
                "nothing is mixed. Conversely row_deficit shows the loss is exactly a sum of weighted squared "
                "differences, and spreading_produces_entropy shows any genuine spreading makes it strictly "
                "positive."
            ),
            "lattice_status": (
                "The two laws of this stream are now linked in one direction: reversibility (the first carrier's "
                "redundant assumption) implies no entropy production (the second law's equality case). The "
                "reverse link is open."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "9/9 for this module; 61/61 across the seven modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none \u2014 no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 12 green (0 red) \u2014 GATE: PASS",
        "gate_negative_controls": [
            "six inherited from the earlier modules, all rejected",
            "a FALSE claim that every doubly stochastic map preserves purity is REJECTED (the mixer refutes it)",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "no_logarithms_anywhere": True,
            "converse_explicitly_scoped_out": True,
        },
        "claim_flags": {
            "REVERSIBLE_PRESERVES_PURITY_PROVED": True,
            "SPREADING_STRICTLY_PRODUCES_ENTROPY_PROVED": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "BICONDITIONAL_ESTABLISHED": False,
            "CONVERSE_ESTABLISHED": False,
            "SHANNON_ENTROPY_FORMALISED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "On a four-state space with one step of evolution over Q, in a zero-axiom Rocq development, "
            "reversible evolution preserves purity exactly, and a row spreading positive weight over two states "
            "of differing probability has strictly positive purity deficit. The converse -- that preserving "
            "purity forces reversibility -- is NOT established."
        ),
        "does_not_establish": [
            "the biconditional 'no entropy production iff reversible'. Only the forward direction is proved",
            "that preserving purity forces reversibility; the two steps this would need are listed in partial_closure",
            "anything about Shannon entropy; Renyi-2 only",
            "anything about many steps, equilibration, or continuous state spaces",
            "any transfer to the Hamiltonian carriers",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_ENTROPY_CONVERSE: steps (a) and (b) of partial_closure, which would give the biconditional and close the loop between the two laws.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.entropy_equality_rocq --check",
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
