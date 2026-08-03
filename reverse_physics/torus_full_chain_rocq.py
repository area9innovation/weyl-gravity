"""Provenance record for the Rocq proof of the FULL four-level chain on T^4.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsTorusChain.v`
and their evidence is `rocq/run.sh` exiting 0 with a zero-axiom ledger. This
module pins the proof source by content hash and fails closed on drift.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.torus_full_chain_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-torus-full-chain-rocq-v1"

# Only the mathematics is pinned. The gate script is named but NOT pinned: it is
# harness, and coupling this record to harness edits was the defect recorded in
# REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1's pin_repair field.
PINNED = {"proof": ROOT / "rocq/ReversePhysicsTorusChain.v"}

THEOREMS = [
    {
        "name": "hamiltonian_implies_symplectic",
        "statement": "at every mode, a globally Hamiltonian field preserves omega",
    },
    {
        "name": "closed_implies_intra_dof_closed",
        "statement": "closedness implies its two intra-degree-of-freedom equations",
    },
    {
        "name": "intra_dof_closed_implies_marginal",
        "statement": "the two intra-DOF equations ALONE imply the marginal condition",
        "role": "the sharp form: marginality consumes only 2 of the 6 closedness equations",
    },
    {
        "name": "symplectic_implies_marginal",
        "statement": "at every mode, preserving omega implies each DOF preserves its own area",
    },
    {
        "name": "marginal_implies_volume",
        "statement": "at every mode, per-DOF area preservation implies total volume preservation",
    },
    {
        "name": "the_chain",
        "statement": "Hamiltonian <= symplectic <= marginal <= volume-preserving, at every mode",
    },
    {
        "name": "marginal_not_symplectic",
        "statement": "X = cos(2 pi q2) d/dq1 is marginal and volume preserving but does NOT preserve omega",
        "role": "strictness of the symplectic <= marginal inclusion",
    },
    {
        "name": "volume_not_marginal",
        "statement": "X = cos(2 pi (q1+q2)) (d/dq1 - d/dq2) preserves total volume but no degree of freedom preserves its own area",
        "role": "strictness of the marginal <= volume inclusion; the torus form of the G0 witness diag(I, -I)",
    },
    {
        "name": "marginal_is_exactly_the_intra_dof_content",
        "statement": "symplectic implies intra-DOF closed implies marginal, and the shear witness is intra-DOF closed but not symplectic",
        "role": "THE STRUCTURAL RESULT: the marginal condition is precisely the intra-DOF content of symplecticity, and the four inter-DOF equations it drops are not recoverable",
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
        "result_state": "FULL_FOUR_LEVEL_CHAIN_PROVED_AT_EVERY_MODE_WITH_BOTH_INCLUSIONS_STRICT",
        "generality_level": "G4_ALL_FOURIER_MODES_HENCE_ALL_TRUNCATIONS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the mathematics is in rocq/ReversePhysicsTorusChain.v; this file computes nothing",
        "assumption_tags": {
            "consumed": ["RP-DETERMINISTIC", "RP-REVERSIBLE"],
            "under_test": ["RP-INFORMATION-CONSERVING", "RP-MARGINAL-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ",
            "opened_by": "REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1",
            "how": "The topological step was already proved for all modes. This adds the other two inclusions, also for all modes, and proves both of them STRICT by explicit witnesses -- an inclusion chain that silently collapsed would make the whole separation vacuous.",
        },
        "builds_on": {
            "result_id": "REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1",
            "relation": "this development Requires ReversePhysicsTorus and reuses exact_implies_closed and closed",
        },
        "proof_assistant": {
            "system": "Rocq (Coq) 8.20.1",
            "theory": "Set is predicative; rewrite rules not allowed",
        },
        "theorems": THEOREMS,
        "structural_result": {
            "statement": "The marginal condition is EXACTLY the intra-degree-of-freedom content of symplecticity: it is implied by the two closedness equations for the pairs (q1,p1) and (q2,p2), and the four inter-DOF equations it drops are not recoverable from it.",
            "why_it_matters": "This is the torus counterpart of the linear-carrier finding in the G0 certificate, where the residual obstruction sat precisely in the inter-DOF block J A_12 = -(A_21)^T J. Two structurally different carriers, the same localisation: what a per-degree-of-freedom condition cannot express is inter-degree-of-freedom coupling.",
        },
        "ledger": {
            "print_assumptions_closed": "18/18 across both modules, closed under the global context",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 7 green (0 red) — GATE: PASS",
        "gate_negative_controls": [
            "a FALSE claim that uniform translation is exact at the zero mode is REJECTED by coqc",
            "a FALSE claim that marginal implies symplectic -- which would collapse the chain -- is REJECTED by coqc",
        ],
        "provenance": {"source_manifest": manifest, "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned here"},
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "both_inclusions_proved_strict": True,
            "negative_controls_rejected": True,
            "quantified_over_all_modes": True,
        },
        "claim_flags": {
            "FULL_CHAIN_PROVED_FOR_ALL_MODES": True,
            "INCLUSIONS_PROVED_STRICT": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "RANK_COMPUTATIONS_FORMALISED": False,
            "DIMENSION_ARITHMETIC_FORMALISED": False,
            "GENERAL_MANIFOLD_COVERED": False,
            "EQUIVALENCE_OVER_A_BASE_THEORY_ESTABLISHED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development kernel-rechecked by coqchk, the four-level chain "
            "Hamiltonian <= symplectic <= marginal <= volume-preserving holds at every Fourier mode on T^4, and "
            "both inclusions above the topological step are strict, witnessed explicitly. Together with "
            "REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1 the entire inclusion structure of the G1 result is now "
            "proved rather than computed."
        ),
        "does_not_establish": [
            "the per-mode DIMENSIONS. The inclusion structure and its strictness are proved; the dimension counts (4, 2, 6, 8-2d per mode) and the totals tabulated in the G1 report remain the Forge gate's exact-rational computation at N <= 3",
            "anything about a general symplectic manifold; the model is the flat T^4 with its standard form",
            "anything about non-polynomial vector fields",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "an equivalence in the reverse-mathematics sense; every theorem here is an IMPLICATION, and no reversal over a base theory exists anywhere in this stream",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_REVERSAL: the whole stream proves implications. A reverse-mathematics result needs a base theory and a derivation of an assumption FROM the law. Nothing in this tree has one; that is the standing gap.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.torus_full_chain_rocq --check",
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
