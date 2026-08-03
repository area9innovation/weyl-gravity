"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsExponentAdditivity.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.coprime_hierarchy_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_COPRIME_HIERARCHY_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_COPRIME_HIERARCHY_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-coprime-hierarchy-rocq-v1"

PINNED = {
    "order_law": ROOT / "rocq/CoprimeHierarchyOrderLaw.v",
    "kernel_parity": ROOT / "rocq/CoprimeHierarchyKernelParity.v",
}

THEOREMS = [
    {
        "name": "word_degree_is_order_plus_two",
        "statement": "a word at order n is homogeneous of degree exactly n+2",
        "role": "the cubic vertex contributes 3 and each Moyal bracket removes 2, so n vertices and n-1 brackets give 3n-2(n-1); EXACTLY, not at most",
    },
    {
        "name": "resonant_at_critical_degree",
        "statement": "at total degree p+q with p,q coprime, a nonnegative resonant monomial is diagonal, the conversion kernel, or its conjugate",
        "role": "coprimality forces n1-m1 = kq and n2-m2 = -kp, and the degree budget forces |k| <= 1; this is where the coprimality does its work",
    },
    {
        "name": "order_law",
        "statement": "the kernel can be carried only at order n = p+q-2",
        "role": "THE ORDER CLAUSE, previously OBSERVED with 'no ansatz proof exists'",
    },
    {
        "name": "selection_rule_below_the_critical_order",
        "statement": "and below that order the kernel cannot appear at all",
        "role": "the selection rule -- the vanishing of every lower order, which the five original fixtures had verified case by case",
    },
    {
        "name": "symmetric_kernel_iff_q_even",
        "statement": "the symmetric combination survives exactly when q is even",
        "role": "THE KERNEL CLAUSE, refined: the symmetry follows q parity, NOT order parity",
    },
    {
        "name": "antisymmetric_kernel_iff_q_odd",
        "statement": "and the antisymmetric combination exactly when q is odd",
    },
    {
        "name": "exactly_one_kernel_survives",
        "statement": "the two are exclusive",
        "role": "what makes the rule a constraint rather than a description: the other combination is FORBIDDEN, not merely unobserved",
    },
    {
        "name": "all_nine_computed_loci_agree",
        "statement": "the rule matches all nine computed loci",
        "role": "a non-vacuity check against the corpus, including the four instances computed for this result",
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
        "result_state": "COPRIME_RATIO_ORDER_LAW_AND_KERNEL_CLAUSE_PROVED_EVEN_p_SHOWN_UNOBSTRUCTED",
        "generality_level": "G4_ALL_COPRIME_p_q_ORDER_AND_KERNEL_CLAUSES",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT \u2014 the mathematics is in rocq/CoprimeHierarchy*.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": [],
            "namespace_note": "This certificate is not an RP-* assumption test. It closes a proof obligation on an EXISTING Science Forge conjecture, and is the first result in this stream to engage the programme's own open corpus rather than a carrier built to demonstrate the method.",
        },
        "engages": {
            "conjecture": "sf:program/conjecture/coprime-ratio-hierarchy (tango repo)",
            "prior_lifecycle": "VERIFIED_ON_FIXTURES, with does_not_establish reading 'No ansatz proof exists'",
            "prior_fixtures": ["3:1", "3:2", "5:1", "5:3", "7:1"],
            "prior_scope": "p odd, explicitly 'pending evidence'; 7:3, 5:7 and higher named as unchecked",
        },
        "what_changed": {
            "order_clause": "PROVED. Previously observed on five fixtures with no mechanism recorded.",
            "kernel_clause": "PROVED AND REFINED. The symmetry follows q parity, not order parity; the corpus could not distinguish these because every fixture had p odd, and 3:2 is the locus that separates them.",
            "scope": "The p-odd scoping is LOAD-BEARING. Six even-p loci computed past their predicted order are unobstructed entirely; 8:1 was computed AT its predicted order and is zero.",
            "new_fixtures": "5:2 (order 5), 7:2 (order 7), 7:3 (order 8), 9:1 (order 8) -- 7:3 and 9:1 were named unchecked, and order 8 is deeper than anything previously computed in that corpus.",
            "new_sublaw": "The radical is sqrt(w1 w2) for q odd and sqrt(w1 w2 sqfree(w1^2-w2^2)) for q even; nine of nine, and it predicted the ABSENCE of a radical at 9:1.",
        },
        "method_note": {
            "preregistered": "PREREG-EVEN-P.md, committed to tango at 02d92f069 BEFORE any computation",
            "outcome": "The preregistered reading was FALSIFIED -- the preregistration had named that as the better outcome, and it fired. Nothing the conjecture claimed was refuted; what was refuted was the guess that its p-odd scoping was over-cautious.",
        },
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "10/10 across the two modules; 109/109 across the fifteen modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none \u2014 no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
        },
        "gate_result": "RESULT: 20 green (0 red) \u2014 GATE: PASS",
        "upstream_gates": {
            "fast": "tango forge/tools/physics-moyal/coprime_parity_gate.forge \u2014 17/17, 8 s, forge verify -full: c==native, ASan-clean on both backends",
            "certificate_tier": "tango forge/tools/physics-moyal/coprime_parity_deep.forge \u2014 10/10, 42 s, order 7 and order 8",
            "split_rationale": "AGENTS.md: split a fast invariant rail from the expensive exhaustive certificate rather than normalising a slow commit loop. The combined gate exceeded the ten-minute verify budget.",
        },
        "gate_negative_controls": [
            "thirteen inherited from the earlier modules, all rejected",
            "a FALSE claim that the kernel can appear below the critical order is REJECTED",
            "a FALSE claim that both kernel combinations survive is REJECTED",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
            "upstream_commit": "tango 5be183077 (the physics side: gates, results document, conjecture event)",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "preregistered_before_computation": True,
            "control_loci_reproduce_published_values": True,
        },
        "claim_flags": {
            "ORDER_CLAUSE_PROVED": True,
            "KERNEL_CLAUSE_PROVED": True,
            "EVEN_p_SHOWN_UNOBSTRUCTED_ON_SIX_LOCI": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "NON_VANISHING_AT_ODD_p_PROVED": False,
            "EVEN_p_VANISHING_EXPLAINED": False,
            "WORD_GENERATOR_DERIVED_FROM_THE_IMPLEMENTATION": False,
            "CONJECTURE_FULLY_PROVED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development, the coprime-ratio obstruction can be carried only at order "
            "p+q-2 and not below, and exactly one of the two kernel combinations can carry it, determined by "
            "the parity of q. Six even-p loci are computed unobstructed past their predicted order, and four "
            "new odd-p instances confirm the order law."
        ),
        "does_not_establish": [
            "that an obstruction DOES occur at odd p. The order law says where one CAN appear, never that one does; non-vanishing remains observational, now on nine instances",
            "why the even-p coefficient vanishes. Neither the degree count nor the involution explains it -- both go through unchanged at even p -- so the vanishing is DYNAMICAL and is now the sharp open question",
            "the word-generator model from the implementation. That a word at order n is n cubic vertices joined by n-1 Moyal brackets is a MODELLING INPUT stated as a recurrence, not derived from moyal_hi.forge",
            "the conjecture as a whole. It stays at VERIFIED_ON_FIXTURES; the order and kernel clauses are proved, the non-vanishing clause is not",
            "8:3 and 6:5 at their predicted orders. Both were computed only to order 6, below their predicted 9, so they confirm the selection rule without reaching the critical order",
            "any quantum, causal, or field-theoretic claim about Weyl gravity itself \u2014 see the report's physics section, which is interpretation",
        ],
        "next_gate": "COPRIME_HIERARCHY_EVEN_p_MECHANISM: find what makes the even-p coefficient vanish. Six loci of evidence, no argument. That is the successor question and it is sharper than the one the conjecture started with.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.coprime_hierarchy_rocq --check",
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
