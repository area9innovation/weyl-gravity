"""Provenance record for the CHARGE-BOUND AUDIT of the coprime-ratio obstruction.

This record does not add a mathematical claim to the coprime hierarchy. It
RETRACTS an interpretation attached to it and certifies the replacement.

Computes no mathematics. The theorems live in `rocq/CoprimeHierarchyChargeBound.v`;
the polynomial identities live in tango
`forge/tools/physics-moyal/ghost_channel_gate.forge`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.charge_bound_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_COPRIME_CHARGE_BOUND_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_COPRIME_CHARGE_BOUND_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-coprime-charge-bound-rocq-v1"

PINNED = {
    "charge_bound": ROOT / "rocq/CoprimeHierarchyChargeBound.v",
    "order_law": ROOT / "rocq/CoprimeHierarchyOrderLaw.v",
}

# Lives in the tango repo, so it cannot be hash-verified by this rail; the digest
# is RECORDED, and the command that re-derives it is in verification_commands.
UPSTREAM_GATE = {
    "path": "tango forge/tools/physics-moyal/ghost_channel_gate.forge",
    "sha256": "df756eea830c59112338416b3c43fbcc5d5c7f5fea5652aa3428d9274d1d1e3d",
    "result": "exit 56, 56/56 checks, 2 s; forge verify -full: c==native, ASan-clean on both backends",
    "not_verified_here": (
        "the digest is recorded, not re-checked — the file is in another repository. "
        "Re-derive it with sha256sum before trusting this line."
    ),
}

THEOREMS = [
    {
        "name": "conserves_charge_iff_resonant",
        "statement": "the commutant of J = p n1 + q n2 is EXACTLY the resonant sector at ratio p:q",
        "role": "THE MECHANISM. The bracket eigenvalue {J, M} = i[(n1-m1)p + (n2-m2)q] M is literally the resonance frequency ker_split uses to define the kernel, so J-conservation and resonance are the same condition. Nothing about the conversion kernel is special.",
    },
    {
        "name": "kernel_conserves_charge",
        "statement": "the conversion kernel a1^q a2b^p conserves J",
        "role": "charge (+q,-p): the q and p contributions cancel identically",
    },
    {
        "name": "every_critical_obstruction_conserves_charge",
        "statement": "EVERY nonnegative resonant monomial at the critical degree conserves J -- diagonal, kernel, or conjugate alike",
        "role": "consumes resonant_at_critical_degree from the order law. There is no J-breaking candidate the obstruction could have been, so the conclusion does not depend on which kernel appears.",
    },
    {
        "name": "pair_creation_breaks_charge",
        "statement": "pair creation a1^q a2^p does NOT conserve J",
        "role": "THE CONTRAST. Charge (+q,+p): the contributions add to 2pq, never zero for p,q>0. This is the structure that actually runs away.",
    },
    {
        "name": "pair_creation_conserves_the_indefinite_charge",
        "statement": "it conserves p n1 - q n2 instead",
        "role": "and the conversion kernel breaks THAT one -- kernel_breaks_the_indefinite_charge. The two structures are exchanged, which is why they behave oppositely.",
    },
    {
        "name": "positive_charge_bounds_both_occupations",
        "statement": "conserving p n1 + q n2 with p,q > 0 and n1,n2 >= 0 gives p n1 <= J and q n2 <= J",
        "role": "WHY IT SETTLES THE READING. Both occupations are bounded for all time at any coupling. Over Q, so the development stays axiom-free where R would not.",
    },
    {
        "name": "indefinite_charge_level_set_is_unbounded",
        "statement": "the level set of p n1 - q n2 contains physical states with n1 above any bound",
        "role": "positivity of J is doing real work: the indefinite charge bounds nothing",
    },
]

RETRACTED = {
    "where": "reverse_physics/reports/coprime-hierarchy-rocq.md §5, in the version at weyl-gravity 6cb0d8f6",
    "text": (
        "\"An obstruction at a p:q resonance means there is a genuine on-shell q <-> p quanta "
        "conversion between the modes. That conversion is the channel through which the ghost "
        "sector talks to the healthy one — the perturbative mechanism of the instability. On that "
        "reading, the result says: the ghost-conversion channel is closed at every even-p resonance.\""
    ),
    "why_it_is_wrong": [
        "GROUND 1. The coded free Hamiltonian has no ghost sign. moyal.model returns h0 = 1/2(w1 w2 p^2 + (w1/w2) x^2 + (w2/w1) q^2 + w1 w2 y^2): four pure squares with four positive coefficients whenever w1 > w2 > 0, which the model already requires (disc > 0). In mode variables it is exactly w1 a1 a1b + w2 a2 a2b, both frequencies positive -- which is also what ker_split's resonance encodes. The object the obstruction is computed in is bounded below.",
        "GROUND 2. The obstruction conserves a POSITIVE charge, so it bounds rather than destabilises. The bound is kinematic and never refers to the sign of either frequency, so it would survive a genuine ghost. A channel that conserves a positive-definite charge cannot be the mechanism of a runaway.",
    ],
    "replacement": (
        "The coprime-ratio obstruction is the benign conversion channel, not the instability. "
        "\"The channel is closed at even p\" is still true as stated about the obstruction, but it "
        "does not mean the ghost sector is protected -- there is no ghost sector in this model, and "
        "the channel would not be the danger if there were."
    ),
    "unaffected": (
        "Nothing mathematical. The order law, the selection rule, the kernel-parity clause, the "
        "even-p refutation and the four new instances all stand exactly as certified in "
        "REVERSE_PHYSICS_COPRIME_HIERARCHY_ROCQ_V1. Only the physical gloss changes."
    ),
}


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
        "result_state": "INTERPRETATION_RETRACTED_AND_REPLACED",
        "generality_level": "G4_ALL_p_q_POSITIVE",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "PROVENANCE_IMPORT — the mathematics is in rocq/CoprimeHierarchyChargeBound.v and "
            "tango ghost_channel_gate.forge; this file computes nothing"
        ),
        "assumption_tags": {
            "consumed": [],
            "under_test": [],
            "namespace_note": (
                "Not an RP-* assumption test. This record is a SELF-AUDIT: it retracts an "
                "interpretation this stream published and certifies the replacement."
            ),
        },
        "audits": {
            "certificate": "REVERSE_PHYSICS_COPRIME_HIERARCHY_ROCQ_V1",
            "conjecture": "sf:program/conjecture/coprime-ratio-hierarchy (tango repo)",
            "what_is_audited": "the PHYSICS READING, which that certificate already flagged as interpretation in its does_not_establish list",
            "what_is_not_audited": "every mathematical claim in it, all of which stand",
        },
        "retracted_interpretation": RETRACTED,
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "11/11 in CoprimeHierarchyChargeBound.v; 126/126 across the sixteen modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
            "rationals_not_reals": "the bounding argument is over Q. Coq's R is axiomatised, and importing it would put axioms in the ledger for a statement that does not need them.",
        },
        "gate_result": "RESULT: 21 green (0 red) — GATE: PASS",
        "upstream_gate": UPSTREAM_GATE,
        "gate_negative_controls": [
            "fifteen inherited from the earlier modules, all rejected",
            "a FALSE claim that pair creation conserves the positive charge is REJECTED — without this the contrast between a conversion channel and an instability would be vacuous",
            "a FALSE claim that the indefinite charge bounds n1 is REJECTED — without this, positivity of J would be doing no work",
            "the Forge gate carries its own non-vacuity clauses: pb_mode is CALIBRATED against the position-space {x,p} = {y,q} = 1 rather than assumed, and the pair-creation bracket is asserted NONZERO",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
            "upstream_repo": "tango (forge/tools/physics-moyal)",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "exact_polynomial_arithmetic_upstream": True,
            "no_floating_point": True,
            "no_time_integration": True,
        },
        "claim_flags": {
            "PRIOR_INTERPRETATION_RETRACTED": True,
            "CODED_FREE_HAMILTONIAN_IS_POSITIVE_DEFINITE": True,
            "OBSTRUCTION_CONSERVES_A_POSITIVE_CHARGE": True,
            "BOUND_IS_INDEPENDENT_OF_THE_GHOST_SIGN": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "FULL_HAMILTONIAN_CONSERVES_J": False,
            "PU_GHOST_MODEL_ANALYSED": False,
            "STABILITY_OF_WEYL_GRAVITY_ADDRESSED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development, for all positive p and q the commutant of "
            "J = p n1 + q n2 is exactly the resonant sector at ratio p:q, so every possible "
            "obstruction at the critical degree conserves J; J is positive definite, hence bounds "
            "both occupation numbers; and pair creation, the structure that does run away, provably "
            "breaks J while conserving only the indefinite combination. Separately, the free "
            "Hamiltonian as coded in moyal.model is certified positive definite. Together these "
            "retract the reading of the coprime-ratio obstruction as a ghost-instability channel."
        ),
        "does_not_establish": [
            "that the FULL Hamiltonian conserves J. It does not. The raw cubic vertex has non-resonant terms, and those are exactly the ones J fails to commute with; the conservation statement is about the resonant sector, which is where the normal form and the obstruction live",
            "stability of the interacting model. A cubic potential is unbounded below at large amplitude regardless of charges; what is refuted is the specific claim that the OBSTRUCTION is the destabilising channel",
            "anything about a genuine Pais-Uhlenbeck ghost Hamiltonian. Ground 1 says the coded model does not have one; analysing one is separate work",
            "the bracket action from the mpoly implementation. In Rocq {J,M} = i freq M is the DEFINITION of freq; the Forge gate certifies it as a polynomial identity on all 70 monomials of degree <= 4 at four loci, which is a check, not a derivation",
            "any claim about Weyl gravity, the BV-BFV complex, or the residual classes. The Pais-Uhlenbeck model was a toy for the higher-derivative sector and this audit does not reach past it",
        ],
        "next_gate": (
            "GHOST_MODEL_OBSTRUCTION: redo the deformation in a genuinely indefinite free Hamiltonian "
            "(h0 = w1 n1 - w2 n2) and ask whether the obstruction structure changes. Under a2 <-> a2b "
            "the conversion kernel becomes pair creation, so the two models may see mirror-image "
            "obstruction loci -- which would make the coprime hierarchy a statement about which "
            "channel is resonant, not about stability at all."
        ),
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.charge_bound_rocq --check",
            "cd forge && FORGE_LIB=$PWD/lib forge -run -I tools/physics-moyal tools/physics-moyal/ghost_channel_gate.forge   # exit 56",
            "cd forge && FORGE_LIB=$PWD/lib forge verify -full tools/physics-moyal/ghost_channel_gate.forge                 # c==native, asan clean",
            "sha256sum forge/tools/physics-moyal/ghost_channel_gate.forge   # must match upstream_gate.sha256",
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
