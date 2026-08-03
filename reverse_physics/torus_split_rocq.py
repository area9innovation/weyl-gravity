"""Provenance record: why the third assumption is not physical, and a
correction to the earlier split-dependence claim.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsTorusSplit.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.torus_split_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_TORUS_SPLIT_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_TORUS_SPLIT_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-torus-split-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsTorusSplit.v"}

THEOREMS = [
    {
        "name": "standard_pairing_is_symplectic",
        "statement": "omega does not vanish on either block of {(q1,p1),(q2,p2)}",
        "role": "the standard pairing is a genuine degree-of-freedom split",
    },
    {
        "name": "alt_pairing_is_isotropic",
        "statement": "omega VANISHES on both blocks of {(q1,q2),(p1,p2)}",
        "role": "THE CORRECTION: this is the pairing the earlier split-dependence theorem compared against, and it is not a degree-of-freedom split at all",
    },
    {
        "name": "third_pairing_is_isotropic",
        "statement": "omega vanishes on both blocks of {(q1,p2),(p1,q2)}",
        "role": "so of the three ways to pair four coordinates, exactly ONE is a DOF split",
    },
    {
        "name": "rotated_split_is_admissible",
        "statement": "span(e_q1+e_q2, e_p1+e_p2) and span(e_q1-e_q2, e_p1-e_p2) are each symplectic and mutually omega-orthogonal",
        "role": "a legitimate alternative decomposition into two degrees of freedom",
    },
    {
        "name": "marginal_not_invariant_under_admissible_splits",
        "statement": "X = cos(2 pi q1) d/dq2 is marginal for the standard split and NOT marginal for the rotated one",
        "role": "THE HONEST SPLIT-DEPENDENCE: both splits are genuine symplectic decompositions, so this is dependence on a real choice of degrees of freedom, not on an arbitrary coordinate pairing",
    },
    {
        "name": "closed_iff_pairs",
        "statement": "closedness is exactly the twelve pair equations",
        "role": "and it mentions no split whatsoever",
    },
    {
        "name": "split_dependence_cancels",
        "statement": "for EVERY pairing P of the four coordinates, intra_P /\\ inter_P is the same proposition: closedness",
        "role": "THE EXPLANATION: the split is visible in each conjunct and invisible in the conjunction",
    },
    {
        "name": "law_decomposes_three_ways",
        "statement": "the law admits three different A1 /\\ A2 /\\ A3 decompositions, differing only in how the labour is divided",
        "role": "so the decomposition into a physical part and a geometric part is NOT canonical",
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
        "result_state": "THE_PHYSICAL_GEOMETRIC_SPLIT_OF_THE_ASSUMPTIONS_IS_NOT_CANONICAL",
        "generality_level": "G4_ALL_FOURIER_MODES_HENCE_ALL_TRUNCATIONS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "EQUIVALENCE_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the mathematics is in rocq/ReversePhysicsTorusSplit.v; this file computes nothing",
        "assumption_tags": {
            "consumed": ["RP-DETERMINISTIC", "RP-REVERSIBLE"],
            "under_test": ["RP-MARGINAL-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "corrects": {
            "target": "REVERSE_PHYSICS_TORUS_REVERSAL_ROCQ_V1",
            "theorem": "marginal_depends_on_the_dof_split",
            "what_was_wrong": (
                "The theorem is TRUE but its billing was too generous. It compared the standard pairing "
                "{(q1,p1),(q2,p2)} against {(q1,q2),(p1,p2)}, and the latter is ISOTROPIC -- omega vanishes on "
                "both of its blocks -- so it is not a decomposition into degrees of freedom at all. What was "
                "shown was dependence on an arbitrary COORDINATE PAIRING, not on a genuine choice of degrees of "
                "freedom."
            ),
            "how_it_is_repaired": (
                "alt_pairing_is_isotropic records the defect. marginal_not_invariant_under_admissible_splits "
                "supplies the honest and strictly stronger version: marginal is not invariant even between two "
                "genuinely SYMPLECTIC splits, the standard one and a rotated one proved admissible."
            ),
            "does_the_downstream_claim_survive": (
                "Yes, and strengthened. Every claim that rested on 'the DOF split is an input' still holds, now "
                "on an admissible-split witness instead of an isotropic one."
            ),
        },
        "the_explanation": {
            "question": "why is A2 (inter_dof_closed) neither physical nor topological?",
            "answer": (
                "Because it is the REMAINDER of a bookkeeping choice. A1 depends on the split; the law does not; "
                "so the dependence must cancel, and split_dependence_cancels shows where: for every pairing, "
                "intra_P /\\ inter_P is the same proposition, namely closedness, which mentions no split. Having "
                "elected to call two of the six closedness equations 'each degree of freedom conserves its own "
                "information', A2 is whatever is left over."
            ),
            "cost_to_the_programme": (
                "A reverse-physics assumption ought not to depend on a coordinate choice. marginal does. So "
                "'each degree of freedom independently conserves information' cannot stand as a fundamental "
                "assumption on its own; only its conjunction with the remainder is split-independent, and that "
                "conjunction is just 'preserves omega'. The decomposition into a physical part and a geometric "
                "part is therefore not canonical -- a real limitation on reverse-physics-style axiomatisations "
                "of this law, not a defect of the formalisation."
            ),
        },
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "8/8 for this module; 36/36 across the four modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 9 green (0 red) — GATE: PASS",
        "gate_negative_controls": [
            "a FALSE claim that uniform translation is exact at the zero mode is REJECTED",
            "a FALSE claim that marginal implies symplectic is REJECTED",
            "a FALSE claim that marginal alone gives the law is REJECTED",
            "a FALSE claim that marginal is invariant across admissible symplectic splits is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "admissibility_of_both_splits_proved": True,
            "isotropy_of_the_superseded_pairing_proved": True,
            "cancellation_proved_for_every_coordinate_pairing": True,
        },
        "claim_flags": {
            "SPLIT_DEPENDENCE_EXPLAINED": True,
            "DECOMPOSITION_PROVED_NON_CANONICAL": True,
            "EARLIER_CLAIM_CORRECTED_AND_STRENGTHENED": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "FULL_Sp4_INVARIANCE_ESTABLISHED": False,
            "A2_GIVEN_A_PHYSICAL_READING": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "Over the declared carrier, in a zero-axiom Rocq development, the split-dependence of the marginal "
            "condition cancels exactly against the inter-DOF condition: for every coordinate pairing their "
            "conjunction is closedness. Marginal is shown not invariant between two genuinely symplectic splits. "
            "Hence the law's decomposition into a physical and a geometric assumption is not canonical."
        ),
        "does_not_establish": [
            "full Sp(4) invariance. The cancellation is proved for the three COORDINATE pairings and split-dependence is witnessed between two admissible splits; the continuum of symplectic splits Sp(4)/(Sp(2)xSp(2)) is not quantified over",
            "a physical reading of A2. This explains WHY A2 resists one; it does not supply one",
            "that no other decomposition of the law into physical assumptions exists; only that the intra/inter one is not canonical",
            "anything about general symplectic manifolds, non-polynomial fields, or dimensions above four",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_SP4_ORBIT: quantify over the full continuum of symplectic splits rather than the three coordinate pairings and two sample splits, which would upgrade 'not canonical' to a statement about the whole orbit.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.torus_split_rocq --check",
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
