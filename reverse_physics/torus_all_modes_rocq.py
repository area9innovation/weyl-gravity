"""Provenance record for the Rocq proof that closes the torus truncation gate.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsTorus.v` and
their evidence is `rocq/run.sh` exiting 0 with a zero-axiom ledger. This module
pins the PROOF file by content hash and records what was and was not proved.
The gate script is named but not pinned — see `provenance.pin_repair`.

Fail-closed: if the pinned source no longer hashes to the recorded digest,
`--check` refuses.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.torus_all_modes_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-torus-all-modes-rocq-v1"

# Only the mathematics is pinned. The gate script is harness: pinning it coupled
# this certificate to edits that cannot affect its claims, and it tripped twice
# (see provenance.pin_repair). Removed rather than re-bumped.
PINNED = {"proof": ROOT / "rocq/ReversePhysicsTorus.v"}

THEOREMS = [
    {
        "name": "exact_implies_closed",
        "statement": "at every mode, an exact 1-form is closed",
        "role": "the easy inclusion; Hamiltonian implies symplectic",
    },
    {
        "name": "closed_at_zero_mode",
        "statement": "at k = 0 every 1-form is closed",
        "role": "every constant vector field on the torus preserves omega",
    },
    {
        "name": "exact_at_zero_mode_iff_vanishing",
        "statement": "at k = 0 a 1-form is exact iff it vanishes identically",
        "role": "the potential is a constant and d(constant) = 0, so the zero mode's classes are the whole space",
    },
    {
        "name": "zero_mode_has_four_independent_classes",
        "statement": "at k = 0 exactness is equivalent to all four components vanishing",
        "role": "b_1(T^4) = 4 in coordinates: four independent classes",
    },
    {
        "name": "closed_iff_exact_at_nonzero",
        "statement": "for every mode with some nonzero frequency, closed and exact COINCIDE",
        "role": "THE HEART: no cohomology away from the constants. The potential is built explicitly from a direction whose frequency does not vanish, so no bound on the mode is ever needed",
    },
    {
        "name": "nonzero_mode_contributes_no_class",
        "statement": "a nonzero mode contributes nothing to the gap",
        "role": "the quotient closed/exact is trivial there",
    },
    {
        "name": "mode_dichotomy",
        "statement": "every mode is either the zero mode or has a nonzero frequency",
        "role": "exhaustiveness, via decidability of rational equality; this is why quantifying over modes subsumes quantifying over truncations",
    },
    {
        "name": "gap_is_carried_entirely_by_the_zero_mode",
        "statement": "for every mode k and every closed 1-form at k, either k is the zero mode or the form is exact",
        "role": "THE THEOREM. No truncation appears in the statement, so it holds for every N simultaneously",
    },
    {
        "name": "translation_is_closed_but_not_exact",
        "statement": "the constant 1-form of X = d/dq1 is closed and not exact",
        "role": "the zero mode really does carry something; the witness is uniform translation on T^4",
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
        "result_state": "SYMPLECTIC_TO_HAMILTONIAN_GAP_PROVED_TO_BE_CARRIED_BY_THE_ZERO_MODE_AT_EVERY_MODE",
        "generality_level": "G4_ALL_FOURIER_MODES_HENCE_ALL_TRUNCATIONS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT — the mathematics is in rocq/ReversePhysicsTorus.v; this file computes nothing",
        "assumption_tags": {
            "consumed": ["RP-DETERMINISTIC", "RP-REVERSIBLE"],
            "under_test": ["RP-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_TORUS_ALL_TRUNCATIONS",
            "opened_by": "REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_TORUS_G1_V1",
            "how": "The Forge gate computed the gap at N = 0,1,2,3. This proves the per-mode statement for EVERY mode. Since any truncation is a set of modes, the per-mode result subsumes every truncation at once -- a stronger closure than an induction over N, and it needs no induction at all: the potential at a nonzero mode is constructed explicitly from a direction whose frequency does not vanish.",
        },
        "proof_assistant": {
            "system": "Rocq (Coq) 8.20.1",
            "theory": "Set is predicative; rewrite rules not allowed",
            "frequencies_modelled_in": "Q (integer frequencies embed; nothing in the proof needs integrality)",
        },
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "9/9 for this module; 28/28 across the three modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "coqchk_type_in_type": "<none>",
            "coqchk_unsafe_fixpoints": "<none>",
            "coqchk_assumed_positivity": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 8 green (0 red) — GATE: PASS (the shared gate now drives all three modules; it was 6 green when this development stood alone)",
        "gate_checks": [
            "coqc compiles the development",
            "source hygiene: no declared assumption and no admit",
            "Print Assumptions: 9/9 closed under the global context",
            "coqchk standalone kernel re-check succeeds",
            "coqchk axiom section is empty",
            "fail-closed negative control: a deliberately FALSE claim (that uniform translation is exact at the zero mode) is REJECTED by coqc",
        ],
        "provenance": {
            "source_manifest": manifest,
            "pin_repair": {
                "defect": "this record originally pinned rocq/run.sh, a HARNESS script, alongside the proof",
                "times_tripped": 2,
                "first_trip": {
                    "cause": "run.sh extended to drive ReversePhysicsTorusChain.v and a second negative control",
                    "previous_gate_sha256": "40cacdf73be07fa70b6b671633cf419935f5b136818fde2897c2a7cdd60235a1",
                    "action_taken": "hash bumped, lesson recorded, defect LEFT IN PLACE",
                },
                "second_trip": {
                    "cause": "run.sh extended again to drive ReversePhysicsTorusReversal.v and a third negative control",
                    "previous_gate_sha256": "a93236de5ddebd92ff6fa2ab675061bb2b310f9c78af9a1548c977d1ec6238fd",
                    "action_taken": "harness pin REMOVED; only rocq/ReversePhysicsTorus.v is pinned now",
                },
                "proof_sha256_unchanged_throughout": "634eacc8da7283733d2916ada12b123c6dd1dfea3594b90577cc57a9aa3f4e10",
                "why_no_claim_changed": "the proof file is byte-identical across both trips, so no theorem of this certificate was ever affected; only the harness grew",
                "lesson": "pinning a harness script alongside the mathematics couples a certificate to changes that cannot affect its claims. Recording the lesson without removing the defect let it recur; the later certificates pin only the .v.",
            },
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "negative_control_rejected": True,
            "quantified_over_all_modes": True,
            "no_bound_on_the_mode_anywhere_in_the_statement": True,
        },
        "claim_flags": {
            "GAP_STRUCTURE_PROVED_FOR_ALL_MODES": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "MARGINAL_AND_VOLUME_LEVELS_FORMALISED": False,
            "RANK_COMPUTATIONS_FORMALISED": False,
            "DIMENSION_ARITHMETIC_FORMALISED": False,
            "GENERAL_MANIFOLD_COVERED": False,
            "EQUIVALENCE_OVER_A_BASE_THEORY_ESTABLISHED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "This proves, in a zero-axiom Rocq development kernel-rechecked by coqchk, that at every Fourier mode "
            "with a nonzero frequency the closed and exact 1-forms coincide, and that at the zero mode exactness "
            "forces vanishing while closedness is automatic. Hence the symplectic-to-Hamiltonian gap on T^4 is "
            "carried entirely by the zero mode and equals its four independent constant classes, for every "
            "truncation whatsoever."
        ),
        "does_not_establish": [
            "the marginal or volume-preserving levels of the chain; only the symplectic/Hamiltonian (closed/exact) structure is formalised",
            "the per-mode rank computations, which remain the Forge gate's exact-rational computation",
            "the arithmetic summing per-mode dimensions into the totals tabulated in the G1 report; those totals are still computational, not proved",
            "anything about a general symplectic manifold; the model is the flat T^4 with its standard form",
            "anything about non-polynomial vector fields",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "an equivalence in the reverse-mathematics sense; proving one implication in Rocq is not a reversal over a base theory, and EQUIVALENCE_CERTIFIED remains unreached",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ: formalise the marginal and volume-preserving levels too, so the whole four-level chain — not just its topological step — is proved rather than computed.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.torus_all_modes_rocq --check",
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
    print(f"{RESULT_ID}: PASS (pinned Rocq sources hash-verified)")


if __name__ == "__main__":
    main()
