"""Provenance record for the REVERSAL: the law is equivalent to three
independent assumptions.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsTorusReversal.v`
and their evidence is `rocq/run.sh` exiting 0 with a zero-axiom ledger. Only the
proof source is pinned; the gate script is harness (see the pin_repair note on
REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1).

Usage:
    PYTHONPATH=. python3 -m reverse_physics.torus_reversal_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_TORUS_REVERSAL_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_TORUS_REVERSAL_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-torus-reversal-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsTorusReversal.v"}

ASSUMPTIONS = [
    {
        "label": "A1",
        "name": "marginal",
        "statement": "each degree of freedom independently conserves its own phase-space area",
        "vocabulary": "PHYSICAL — a postulate about information conservation per degree of freedom",
        "independence_witness": "X = cos(2 pi q1) d/dq1 at mode e_{q1}: satisfies A2 and A3, violates A1",
    },
    {
        "label": "A2",
        "name": "inter_dof_closed",
        "statement": "the four cross-degree-of-freedom closedness equations",
        "vocabulary": "GEOMETRIC — no physical reading is offered here; see the honest finding below",
        "independence_witness": "X = cos(2 pi q2) d/dq1 at mode e_{q2}: satisfies A1 and A3, violates A2",
    },
    {
        "label": "A3",
        "name": "no_uniform_drift",
        "statement": "at the zero mode the field vanishes; equivalently, no uniform translation component",
        "vocabulary": "TOPOLOGICAL — it removes exactly the obstruction carried by the constants, i.e. b_1(T^4)",
        "independence_witness": "uniform translation X = d/dq1 at the zero mode: satisfies A1 and A2, violates A3",
    },
]

THEOREMS = [
    {
        "name": "marginal_iff_intra_dof_closed",
        "statement": "the marginal condition and the intra-DOF closedness equations are the SAME statement",
        "role": "this is what licenses calling A1 a physical postulate rather than a geometric one",
    },
    {
        "name": "closed_of_intra_and_inter",
        "statement": "the intra-DOF and inter-DOF equations together are exactly closedness",
    },
    {
        "name": "inter_of_closed",
        "statement": "closedness yields its inter-DOF equations",
    },
    {
        "name": "alpha_vanishes_iff",
        "statement": "the induced 1-form vanishes iff the vector field does",
    },
    {
        "name": "hamiltonian_iff_three_assumptions",
        "statement": "hamiltonian k a b <-> (A1 /\\ A2 /\\ A3), at every mode",
        "role": "THE REVERSAL. The forward direction derives each assumption FROM the law; that is the half this stream previously lacked.",
    },
    {"name": "A1_is_independent", "statement": "A2 and A3 hold, A1 fails, the law fails"},
    {"name": "A2_is_independent", "statement": "A1 and A3 hold, A2 fails, the law fails"},
    {"name": "A3_is_independent", "statement": "A1 and A2 hold, A3 fails, the law fails"},
    {
        "name": "marginal_depends_on_the_dof_split",
        "statement": "the SAME field is marginal for the split {(q1,p1),(q2,p2)} and not marginal for {(q1,q2),(p1,p2)}",
        "role": "the degree-of-freedom split has been a DECLARED ASSUMPTION throughout this stream; here it is a theorem that A1 is relative to it",
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
        "result_state": "LAW_PROVED_EQUIVALENT_TO_THREE_MUTUALLY_INDEPENDENT_ASSUMPTIONS",
        "generality_level": "G4_ALL_FOURIER_MODES_HENCE_ALL_TRUNCATIONS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "EQUIVALENCE_CERTIFIED",
        "lifecycle_note": (
            "This is the first result in the stream to reach EQUIVALENCE_CERTIFIED, and the promotion is "
            "scoped: it is an equivalence over the DECLARED CARRIER, not over a weakenable axiomatic base. "
            "See base_theory.honesty below before citing it as a reverse-mathematics reversal."
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the mathematics is in rocq/ReversePhysicsTorusReversal.v; this file computes nothing",
        "assumption_tags": {
            "consumed": ["RP-DETERMINISTIC", "RP-REVERSIBLE"],
            "under_test": ["RP-MARGINAL-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_REVERSAL",
            "how": "Every earlier theorem in the stream was an implication. hamiltonian_iff_three_assumptions derives each assumption FROM the law and back, and the three independence theorems show no assumption is redundant.",
        },
        "base_theory": {
            "role": "what RCA_0 plays in reverse mathematics",
            "content": [
                "state space T^4 with coordinates ordered (q1, p1, q2, p2)",
                "the symplectic form omega = dq1^dp1 + dq2^dp2 is fixed",
                "the degree-of-freedom split into (q1,p1) and (q2,p2) is fixed and part of the structure",
                "fields are trigonometric polynomials, treated one Fourier mode at a time",
                "coefficients are rational, so every statement is exact",
            ],
            "honesty": (
                "This is DEFINITIONAL CONTEXT, not an axiom schema. A genuine reverse-mathematics base is a "
                "system one can weaken and compare against; this is a carrier declaration. Turning it into a "
                "parameterised base -- quantifying over DOF splits and over symplectic forms -- is NOT done. "
                "The one result that gestures at it is marginal_depends_on_the_dof_split."
            ),
        },
        "assumptions_decomposition": ASSUMPTIONS,
        "theorems": THEOREMS,
        "honest_finding": {
            "statement": "The law decomposes into three independent pieces, only TWO of which this stream can state in physical vocabulary.",
            "detail": (
                "A1 is a physical postulate (per-degree-of-freedom information conservation) and A3 is a clean "
                "topological one (no uniform drift, removing exactly the b_1(T^4) obstruction). A2 is neither: "
                "it is a geometric consistency condition between degrees of freedom, and no physical reading of "
                "it is offered here."
            ),
            "why_it_matters": (
                "A reverse-physics programme wants the law to be equivalent to a set of PHYSICAL assumptions. "
                "Here a third of the decomposition resists that reading. Whether A2 has an honest physical "
                "formulation is open; if it does not, this is a bound on how much of Hamiltonian structure is "
                "physically axiomatisable at all."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "28/28 across all three modules, closed under the global context",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 8 green (0 red) — GATE: PASS",
        "gate_negative_controls": [
            "a FALSE claim that uniform translation is exact at the zero mode is REJECTED",
            "a FALSE claim that marginal implies symplectic is REJECTED",
            "a FALSE claim that marginal alone gives the law -- which would contradict A2/A3 independence -- is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "equivalence_proved_in_both_directions": True,
            "each_assumption_independent_by_explicit_witness": True,
            "dof_split_dependence_proved": True,
        },
        "claim_flags": {
            "REVERSAL_ESTABLISHED": True,
            "EQUIVALENCE_OVER_THE_DECLARED_CARRIER": True,
            "ASSUMPTIONS_MUTUALLY_INDEPENDENT": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "EQUIVALENCE_OVER_A_WEAKENABLE_AXIOMATIC_BASE": False,
            "ALL_ASSUMPTIONS_STATED_IN_PHYSICAL_VOCABULARY": False,
            "GENERAL_MANIFOLD_COVERED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "Over the declared carrier, in a zero-axiom Rocq development kernel-rechecked by coqchk, a vector "
            "field on T^4 is Hamiltonian if and only if it satisfies three assumptions, each of which is derived "
            "from the law and none of which is redundant. This is the first reversal in the stream: previously "
            "every theorem ran assumptions-to-law only."
        ),
        "does_not_establish": [
            "an equivalence over a WEAKENABLE AXIOMATIC BASE. The base here is a carrier declaration, not a system one can vary and compare against, so this is not yet reverse mathematics in the strict sense",
            "that the three assumptions are the ONLY such decomposition; minimality among alternative decompositions is not addressed",
            "a physical reading of A2; two of three assumptions are physical or topological, the third is geometric and unexplained",
            "anything about general symplectic manifolds, non-polynomial fields, or dimensions above four",
            "the per-mode dimension counts, which remain the Forge gate's computation",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_PARAMETERISED_BASE: quantify over degree-of-freedom splits and symplectic forms so the base becomes a system that can be weakened, which is what would turn this scoped equivalence into a reverse-mathematics reversal proper.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.torus_reversal_rocq --check",
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
