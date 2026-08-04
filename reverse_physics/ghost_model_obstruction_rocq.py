"""Provenance record: the successor question, answered — and the conjecture in it
partly corrected.

`CoprimeHierarchyChargeBound.v` refuted a physics gloss this stream had published,
and recorded the limit of its own replacement: the model it argued in has NO GHOST.
Its free Hamiltonian is `w1 n1 + w2 n2` with both frequencies positive, so the
positive charge `J = p n1 + q n2` that bounds the occupations is available for a
reason that has nothing to do with the obstruction. It declared the successor:

    GHOST_MODEL_OBSTRUCTION -- redo the deformation with a genuinely indefinite
    h0 = w1 n1 - w2 n2 and ask whether the obstruction structure changes. Under
    a2 <-> a2b the conversion kernel becomes pair creation, so the two models
    plausibly see MIRROR-IMAGE OBSTRUCTION LOCI. If that is right, the coprime
    hierarchy is a statement about which channel is resonant -- not about
    stability at all, in either model.

`rocq/GhostModelObstruction.v` settles it. The conclusion is CONFIRMED and the
phrasing is CORRECTED:

  THE LOCI DO NOT MIRROR -- THEY COINCIDE. The relabelling a2 <-> a2b is an
  involution preserving total degree, nonnegativity and diagonality, and it carries
  the ghost-resonant sector bijectively onto the healthy one. It acts on MONOMIALS,
  not on (p, q), so the set of ratios admitting an obstruction is literally the same
  in both models and the coprime hierarchy transports unchanged. What mirrors is the
  CHANNEL: at each ratio the obstructing monomial is conversion a1^q a2b^p in the
  healthy model and pair creation a1^q a2^p in the ghost model.

  THE CHARGE IS WHERE THE MODELS PART. A diagonal quadratic charge conserved on the
  ghost model's critical sector must satisfy q*al + p*be = 0, which for positive
  p, q forces al and be to have STRICTLY OPPOSITE SIGNS. The only surviving charge
  is proportional to p n1 - q n2, whose level sets are unbounded. The healthy
  model's same-shaped argument yields (p, q), both positive, which bounds.

WHY IT MATTERS, and it is the reverse-physics point rather than a fact about a toy:
the bound proved in the predecessor is a consequence of the DEFINITENESS of the free
Hamiltonian, not of the obstruction. The obstruction is identical across the two
models -- same ratios, same critical degree, same classification, exchanged by a
relabelling -- and it bounds in one and not the other. So the obstruction is
MATHEMATICS about a degree and a coprimality condition; the boundedness is PHYSICS
about a positive-definite h0. Conflating the two is exactly what produced the
original wrong gloss, and separating them is what this stream is for.

Computes no mathematics. The theorems live in `rocq/GhostModelObstruction.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.ghost_model_obstruction_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_GHOST_MODEL_OBSTRUCTION_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_GHOST_MODEL_OBSTRUCTION_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-ghost-model-obstruction-rocq-v1"

PINNED = {
    "ghost_model": ROOT / "rocq/GhostModelObstruction.v",
    "charge_bound": ROOT / "rocq/CoprimeHierarchyChargeBound.v",
    "order_law": ROOT / "rocq/CoprimeHierarchyOrderLaw.v",
}

THEOREMS = [
    {
        "name": "ghost_resonant_iff_resonant_of_conj2",
        "statement": "a monomial is resonant for h0 = p n1 - q n2 exactly when its a2 <-> a2b relabelling is resonant for h0 = p n1 + q n2",
        "role": "THE MIRROR. Everything else follows by transporting the healthy model's classification across this bijection.",
    },
    {
        "name": "conj2_kernel_is_pair_creation",
        "statement": "the relabelling carries the conversion kernel a1^q a2b^p to pair creation a1^q a2^p",
        "role": "the single fact the successor question was built on, now proved rather than conjectured",
    },
    {
        "name": "kernel_is_not_ghost_resonant",
        "statement": "the healthy model's obstructing monomial is NOT resonant in the ghost model",
        "role": "the channels genuinely differ; without this the two models would obstruct identically and the separation would be vacuous",
    },
    {
        "name": "ghost_resonant_at_critical_degree",
        "statement": "a nonnegative ghost-resonant monomial at total degree p+q is diagonal, pair creation, or pair annihilation",
        "role": "the classification transports with IDENTICAL hypotheses -- same positivity, same coprimality, same critical degree. Only the two named monomials change.",
    },
    {
        "name": "obstruction_ratios_are_unchanged",
        "statement": "the ghost and healthy critical sectors are in degree- and nonnegativity-preserving bijection at every (p, q)",
        "role": "CORRECTS the successor question. The loci do not mirror -- they coincide, because the involution acts on monomials and not on (p, q).",
    },
    {
        "name": "surviving_ghost_charge_is_indefinite",
        "statement": "q*al + p*be = 0 with p, q > 0 forces al*be < 0 unless the charge is trivial",
        "role": "WHERE THE MODELS PART. The only diagonal quadratic charge surviving in the ghost model is indefinite.",
    },
    {
        "name": "healthy_charge_is_not_conserved_on_pair_creation",
        "statement": "the positive charge (p, q) is NOT conserved on pair creation",
        "role": "the contrast made exact, and a non-vacuity check on the previous line",
    },
    {
        "name": "ghost_model_charge_does_not_bound_occupations",
        "statement": "for any bound B there is a physical state on the surviving charge's level set with n1 > B",
        "role": "an unbounded level set. Note the boundary: this PERMITS growth, it does not produce it.",
    },
    {
        "name": "healthy_model_charge_does_bound_occupations",
        "statement": "the same conservation law with the opposite sign bounds both occupations",
        "role": "restated in the ghost module so the dichotomy is readable in one place: same p, same q, same nonnegativity, only the sign of h0 differs",
    },
]

DOES_NOT_ESTABLISH = [
    "that the ghost model is unstable -- only that the charge argument bounding the healthy model has no counterpart here; an unbounded level set permits growth without producing it",
    "that the ghost model's cubic vertex actually contains the pair-creation monomial with nonzero coefficient, which is a computation in the deformation rather than a statement about the resonant sector",
    "that no conserved quantity of HIGHER degree bounds the ghost model; only diagonal quadratic charges al n1 + be n2 are considered",
    "the bracket action on monomials, which is the DEFINITION ghost_freq here as it is in the predecessor, certified in Forge as a polynomial identity rather than derived from the implementation inside Rocq",
    "anything about Weyl gravity, the BV-BFV complex, or the residual classes -- the Weyl ghost is a genuinely indefinite system, which is why the question was asked, but this is a two-mode toy",
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
        "result_state": "SUCCESSOR_QUESTION_ANSWERED",
        "generality_level": "G4_ALL_p_q_POSITIVE",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "PROVENANCE_IMPORT — the mathematics is in rocq/GhostModelObstruction.v; "
            "this file computes nothing"
        ),
        "answers": {
            "declared_by": "REVERSE_PHYSICS_COPRIME_CHARGE_BOUND_ROCQ_V1",
            "question": "GHOST_MODEL_OBSTRUCTION",
            "verdict": "CONFIRMED_WITH_A_CORRECTION",
            "confirmed": (
                "the coprime hierarchy is a statement about WHICH CHANNEL IS RESONANT, "
                "not about stability, in either model"
            ),
            "corrected": (
                "the successor question guessed MIRROR-IMAGE obstruction loci. The loci "
                "COINCIDE: the relabelling acts on monomials, not on (p, q), so the set of "
                "ratios admitting an obstruction is literally the same. It is the CHANNEL "
                "that mirrors."
            ),
        },
        "the_separation": {
            "mathematics": "the obstruction — a statement about a critical degree p+q and a coprimality condition, identical in both models",
            "physics": "the boundedness — a consequence of the free Hamiltonian being positive-definite, and absent as soon as it is not",
            "why_it_matters": (
                "conflating the two produced the original wrong gloss. The predecessor "
                "showed the obstruction does not destabilise; this shows the thing that "
                "bounds is not the obstruction either."
            ),
        },
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "17/17 in GhostModelObstruction.v; 234/234 across the twenty-three modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
            "rationals_not_reals": (
                "the unboundedness argument is over Q. Coq's R is axiomatised, and importing "
                "it would put axioms in the ledger for a statement that does not need them."
            ),
        },
        "gate_result": "RESULT: 28 green (0 red) — GATE: PASS",
        "gate_negative_controls": [
            "twenty-seven inherited, all rejected",
            "a FALSE claim that the conversion kernel is resonant in the ghost model is REJECTED — without it the two models would obstruct through the same channel and the separation would be vacuous",
            "a FALSE claim that the surviving ghost charge can be positive is REJECTED — without it the sign of h0 would be doing no work, which is the entire content of the module",
        ],
        "does_not_establish": DOES_NOT_ESTABLISH,
        "source_manifest": manifest,
        "verification_commands": [
            "cd rocq && ./run.sh   # RESULT: 28 green (0 red)",
            "PYTHONPATH=. python3 -m reverse_physics.ghost_model_obstruction_rocq --check",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the stored certificate")
    args = ap.parse_args()

    fresh = build()
    if args.check:
        if not OUTPUT.exists():
            print(f"FAIL: {OUTPUT.relative_to(ROOT)} is missing")
            return 1
        stored = json.loads(OUTPUT.read_text())
        if stored.get("source_manifest") != fresh["source_manifest"]:
            print("FAIL: the pinned Rocq sources drifted from the stored hashes")
            return 1
        for field in ("theorems", "answers", "does_not_establish", "ledger"):
            if stored.get(field) != fresh[field]:
                print(f"FAIL: {field} drifted from the stored certificate")
                return 1
        print(f"{RESULT_ID}: PASS (pinned Rocq proof hash-verified)")
        return 0

    OUTPUT.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
