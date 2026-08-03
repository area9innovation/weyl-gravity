"""Provenance record: testing the two assumptions the stream had only consumed.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsStochastic.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.stochastic_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_STOCHASTIC_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_STOCHASTIC_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-stochastic-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsStochastic.v"}

THEOREMS = [
    {
        "name": "dmat_col_sum",
        "statement": "every deterministic matrix is column-stochastic",
        "role": "probability is conserved forwards whether or not anything else is",
    },
    {
        "name": "determinism_and_information_force_reversibility",
        "statement": "deterministic /\\ conserves_information -> reversible",
        "role": "THE RESULT. If two states merged, the fibre over their image would carry mass two, contradicting the uniform ensemble being stationary.",
    },
    {
        "name": "injective_row_sum_le_one",
        "statement": "with the underlying map injective, no state's fibre carries more than unit mass",
    },
    {
        "name": "reversibility_forces_information_conservation",
        "statement": "reversible -> conserves_information",
        "role": "four fibre masses each at most one, summing to four, are each exactly one",
    },
    {
        "name": "reversibility_is_not_independent",
        "statement": "reversible <-> (deterministic /\\ conserves_information)",
        "role": "the equivalence: reversibility is exactly the conjunction of the other two",
    },
    {
        "name": "collapse_is_deterministic_not_conserving",
        "statement": "the map sending every state to s0 is deterministic, destroys information, and is not reversible",
        "role": "determinism alone does not suffice",
    },
    {
        "name": "mixer_conserves_but_is_not_deterministic",
        "statement": "uniform mixing (every entry 1/4) conserves information, is not deterministic, and is not reversible",
        "role": "information conservation alone does not suffice",
    },
    {
        "name": "reversibility_is_redundant_given_the_other_two",
        "statement": "the same implication, stated as the vocabulary finding",
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
        "result_state": "REVERSIBILITY_IS_NOT_AN_INDEPENDENT_POSTULATE_ON_THIS_CARRIER",
        "generality_level": "G1_FOUR_STATE_STOCHASTIC_EVOLUTION_ONE_STEP",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "EQUIVALENCE_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the mathematics is in rocq/ReversePhysicsStochastic.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-DETERMINISTIC", "RP-REVERSIBLE", "RP-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
            "why_this_certificate_exists": (
                "RP-DETERMINISTIC and RP-REVERSIBLE appear under 'consumed' in EVERY other certificate of this "
                "stream and under 'under_test' in NONE of them. That was structural, not an oversight: on the "
                "Hamiltonian carriers every evolution is exp(tA), which is deterministic and invertible by "
                "construction, so those assumptions could not fail there and therefore could not be tested. "
                "This carrier is the first in which they can fail."
            ),
        },
        "carrier": {
            "states": 4,
            "evolution": "column-stochastic matrices over Q acting on probability distributions",
            "picture": "the ensemble picture rather than the point picture, closer to how Carcassi and Aidala set things up",
            "why_it_can_falsify": [
                "a non-deterministic evolution spreads a point mass over several states",
                "an irreversible evolution merges distinct states",
            ],
            "independence": "this development imports none of the torus modules and shares no definitions with them",
        },
        "assumption_readings": {
            "deterministic": "a point mass evolves to a point mass; the matrix is the graph of a function",
            "conserves_information": "the uniform (maximum-entropy) ensemble is stationary — the discrete Liouville condition",
            "reversible": "distinct states stay distinct; the underlying map is injective",
        },
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "On this carrier reversibility is NOT an independent postulate: it is exactly the conjunction of determinism and information conservation.",
            "consequence_for_the_vocabulary": (
                "Every certificate in this stream listed RP-DETERMINISTIC and RP-REVERSIBLE as two separate "
                "consumed assumptions. On this carrier that overstates how many assumptions are in play: the "
                "pair (determinism, information conservation) already entails reversibility. The vocabulary was "
                "redundant."
            ),
            "consequence_for_the_hamiltonian_results": (
                "It retroactively explains why the Hamiltonian carriers could bake reversibility in without "
                "loss. It does NOT transfer the equivalence to them: those carriers are continuous and this "
                "proof is about four states and one step."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "9/9 for this module; 45/45 across the five modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 10 green (0 red) — GATE: PASS",
        "gate_negative_controls": [
            "a FALSE claim that uniform translation is exact at the zero mode is REJECTED",
            "a FALSE claim that marginal implies symplectic is REJECTED",
            "a FALSE claim that marginal alone gives the law is REJECTED",
            "a FALSE claim that marginal is invariant across admissible symplectic splits is REJECTED",
            "a FALSE claim that determinism alone gives reversibility is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "equivalence_proved_in_both_directions": True,
            "both_conjuncts_shown_necessary_by_witness": True,
            "carrier_independent_of_the_hamiltonian_developments": True,
        },
        "claim_flags": {
            "PREVIOUSLY_UNTESTED_ASSUMPTIONS_NOW_TESTED": True,
            "REVERSIBILITY_SHOWN_REDUNDANT_ON_THIS_CARRIER": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "TRANSFERS_TO_THE_HAMILTONIAN_CARRIERS": False,
            "CONTINUOUS_STATE_SPACE_COVERED": False,
            "MULTI_STEP_OR_ASYMPTOTIC_BEHAVIOUR_COVERED": False,
            "ENTROPY_BEYOND_UNIFORM_STATIONARITY_COVERED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "On a four-state space with one step of column-stochastic evolution over Q, in a zero-axiom Rocq "
            "development, reversibility is equivalent to determinism together with information conservation, "
            "and neither conjunct alone suffices. This is the first certificate in the stream to place "
            "RP-DETERMINISTIC and RP-REVERSIBLE under test rather than under consumed."
        ),
        "does_not_establish": [
            "that the equivalence transfers to the Hamiltonian carriers of the other certificates. Those are continuous; this is four states and one step",
            "anything about continuous state spaces or about more than one time step",
            "anything about entropy beyond the stationarity of the uniform ensemble; Shannon entropy is not formalised here",
            "that the two assumptions are redundant in general — only on this carrier",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_STOCHASTIC_GENERAL_N: the proof is written for four states; a general finite state space would need a pigeonhole argument this development sidesteps by counting fibre masses over a fixed size.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.stochastic_rocq --check",
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
