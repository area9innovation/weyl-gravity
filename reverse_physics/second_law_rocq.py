"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsSecondLaw.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.second_law_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_SECOND_LAW_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_SECOND_LAW_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-second-law-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsSecondLaw.v"}

THEOREMS = [
    {
        "name": "jensen4_identity",
        "statement": "(sum w)(sum w x^2) - (sum w x)^2 = sum_{j<k} w_j w_k (x_j - x_k)^2",
        "role": "the whole analytic content with no analysis: stated with an unconstrained weight sum so ring alone decides it",
    },
    {
        "name": "jensen4_le",
        "statement": "for nonnegative weights summing to one, the square of the mean is at most the mean of the squares",
    },
    {
        "name": "purity_never_increases",
        "statement": "a doubly stochastic evolution never increases purity",
        "role": "THE SECOND LAW. Disorder never decreases.",
    },
    {
        "name": "mixing_strictly_increases_disorder",
        "statement": "purity of a point mass is 1; after uniform mixing it is 1/4",
        "role": "the bound is attained strictly, so the theorem is not vacuous",
    },
    {
        "name": "mixer_is_admissible",
        "statement": "the mixer satisfies every hypothesis of the theorem",
        "role": "so the strictness is not obtained by stepping outside the hypotheses",
    },
    {
        "name": "reversible_never_increases_purity",
        "statement": "reversible evolution is doubly stochastic, so it too can only increase disorder",
    },
    {
        "name": "the_second_law_is_entailed_by_information_conservation",
        "statement": "the second law restated as the reverse-physics claim",
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
        "result_state": "THE_SECOND_LAW_IS_ENTAILED_BY_INFORMATION_CONSERVATION_ON_THIS_CARRIER",
        "generality_level": "G1_FOUR_STATE_STOCHASTIC_EVOLUTION_ONE_STEP_RENYI_2",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the mathematics is in rocq/ReversePhysicsSecondLaw.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "why_this_is_a_second_law": (
            "Reverse physics pays off as a LATTICE of law/assumption pairs. Until now this stream had one law "
            "(Hamiltonian privilege) plus a vocabulary side-result. This adds a second, on the carrier the first "
            "left behind, and the two turn out to consume the SAME assumption."
        ),
        "how_exactness_is_preserved": {
            "problem": "the usual second law needs Shannon entropy, whose logarithms are not rational and would break the exactness this stream depends on",
            "rejected_route": "majorization (Hardy--Littlewood--Polya) is order-theoretic and logarithm-free, but stating it needs sorting, which is heavy to formalise",
            "chosen_route": (
                "purity, sum_i p_i^2 -- the collision probability. It is the exact rational content of the "
                "Renyi-2 entropy -log(sum p^2): since -log is monotone, 'entropy does not decrease' IS 'purity "
                "does not increase', with no logarithm anywhere. Purity is Schur-convex, so this is the "
                "majorization statement evaluated on one Schur-convex functional."
            ),
        },
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "On this carrier the second law is not an extra postulate. It is entailed by information conservation.",
            "detail": (
                "Both hypotheses are already in the vocabulary and neither is new: column sums one is "
                "conservation of probability (the evolution maps distributions to distributions), and row sums "
                "one is conserves_information -- stationarity of the uniform ensemble."
            ),
            "the_lattice_point": (
                "conserves_information is now load-bearing for BOTH laws in this stream: it is what makes "
                "reversibility redundant (REVERSE_PHYSICS_STOCHASTIC_ROCQ_V1) and what entails the arrow of "
                "disorder. Two laws, one assumption."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "7/7 for this module; 52/52 across the six modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 11 green (0 red) — GATE: PASS",
        "gate_negative_controls": [
            "a FALSE claim that uniform translation is exact at the zero mode is REJECTED",
            "a FALSE claim that marginal implies symplectic is REJECTED",
            "a FALSE claim that marginal alone gives the law is REJECTED",
            "a FALSE claim that marginal is invariant across admissible symplectic splits is REJECTED",
            "a FALSE claim that determinism alone gives reversibility is REJECTED",
            "a FALSE claim that purity is CONSERVED rather than non-increasing is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "no_logarithms_anywhere": True,
            "strictness_witnessed_inside_the_hypotheses": True,
        },
        "claim_flags": {
            "SECOND_LAW_ESTABLISHED_ON_THIS_CARRIER": True,
            "ENTAILED_BY_AN_ASSUMPTION_ALREADY_IN_THE_VOCABULARY": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "SHANNON_ENTROPY_FORMALISED": False,
            "FULL_MAJORIZATION_FORMALISED": False,
            "EQUALITY_CASE_CHARACTERISED": False,
            "MULTI_STEP_OR_EQUILIBRATION_COVERED": False,
            "TRANSFERS_TO_THE_HAMILTONIAN_CARRIERS": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "On a four-state space with one step of doubly stochastic evolution over Q, in a zero-axiom Rocq "
            "development, purity never increases -- equivalently the Renyi-2 entropy never decreases -- and the "
            "bound is attained strictly by uniform mixing, which is itself admissible. Both hypotheses are "
            "assumptions already in the stream's vocabulary."
        ),
        "does_not_establish": [
            "anything about SHANNON entropy. Renyi-2 only; the logarithmic quantity is not formalised",
            "full majorization. Purity is one Schur-convex functional, not the majorization order itself",
            "the EQUALITY case. That reversible evolution PRESERVES purity exactly is not proved -- only that it does not increase it -- so 'reversible iff no entropy production' is NOT established",
            "anything about many steps, equilibration, or approach to the uniform distribution",
            "any transfer to the Hamiltonian carriers of the other certificates",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_ENTROPY_EQUALITY: characterise the equality case, which would give 'reversible iff no entropy production' and close the loop between the two laws on this carrier.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.second_law_rocq --check",
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
