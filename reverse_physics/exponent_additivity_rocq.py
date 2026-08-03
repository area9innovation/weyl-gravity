"""Provenance record for the SECOND LAW on the stochastic carrier.

Computes no mathematics. The theorems live in `rocq/ReversePhysicsExponentAdditivity.v`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.exponent_additivity_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_EXPONENT_ADDITIVITY_ROCQ_V1.json"

RESULT_ID = "REVERSE_PHYSICS_EXPONENT_ADDITIVITY_ROCQ_V1"
SCHEMA_NAME = "reverse-physics-exponent-additivity-rocq-v1"

PINNED = {"proof": ROOT / "rocq/ReversePhysicsExponentAdditivity.v"}

THEOREMS = [
    {"name": "qpow_mul", "statement": "powers of a product are the product of the powers"},
    {
        "name": "independence_makes_scale_factors_multiply",
        "statement": "f_AB(t) = f_A(t) f_B(t)",
        "role": "directly from the product structure: the composite dilation acts diagonally and the relative count factorises",
    },
    {"name": "generating_numbers_multiply", "statement": "g_AB = g_A g_B"},
    {
        "name": "exponents_add",
        "statement": "if g_A = 2^dA and g_B = 2^dB and g_AB = g_A g_B, then g_AB = 2^(dA + dB)",
        "role": "THE RESULT, and it needs no logarithm: 2^(dA+dB) = 2^dA * 2^dB, so the multiplicative statement about generating numbers IS the additive one about exponents",
    },
    {
        "name": "independent_subsystems_add_their_exponents",
        "statement": "the composite of two independent subsystems carries the sum of their exponents",
        "role": "the assembled form",
    },
    {"name": "composite_scaling_law", "statement": "the composite obeys the same power law with the product generating number"},
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
        "result_state": "DOF_INDEPENDENCE_TRANSPOSES_TO_ADDITIVITY_OF_THE_SCALING_EXPONENT",
        "generality_level": "G3_ANY_FACTORISING_RELATIVE_COUNT_INTEGER_EXPONENTS_ON_DYADIC_SCALES",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "NECESSITY_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": "PROVENANCE_IMPORT \u2014 the mathematics is in rocq/ReversePhysicsExponentAdditivity.v; this file computes nothing",
        "assumption_tags": {
            "consumed": [],
            "under_test": ["RP-CONFORMAL-INVARIANCE", "RP-MARGINAL-INFORMATION-CONSERVING"],
            "namespace_note": "RP-* names physical postulates; disjoint from the computational-regime tags in dependency_tags.",
        },
        "closes_gate": {
            "gate": "REVERSE_PHYSICS_EXPONENT_ADDITIVITY",
            "opened_by": "REVERSE_PHYSICS_RELATIONAL_COUNT_ROCQ_V1",
            "how": "That certificate STATED, without proof, that Carcassi-Aidala's '#states = product of #confDOF' should transpose to additivity of the exponent. It is now proved: a product structure on regions is formalised, the relative count factorises across independent subsystems, and the generating numbers multiply -- which is exactly exponent addition.",
        },
        "how_logarithms_are_avoided": {
            "problem": "'exponent' suggests a logarithm, which would leave the rationals and break the exactness this stream depends on",
            "resolution": (
                "It is not needed. If g_A = 2^dA and g_B = 2^dB then 'exponents add' is literally "
                "g_AB = g_A g_B, because 2^(dA + dB) = 2^dA 2^dB. The multiplicative statement IS the additive "
                "one, and it is exactly rational. Qpower_plus supplies the step over Z exponents."
            ),
        },
        "theorems": THEOREMS,
        "the_finding": {
            "statement": "Carcassi-Aidala's degree-of-freedom independence assumption survives the loss of the count.",
            "detail": (
                "'#states = product of #confDOF' is a product of COUNTS, and counts do not exist in a "
                "conformally invariant theory. It transposes: the relative count factorises across independent "
                "subsystems, so the single number generating each subsystem's scaling multiplies -- which is to "
                "say the exponents add."
            ),
            "the_arc": (
                "Four certificates now form one argument about their DOF-counting conjecture: the density branch "
                "closed by parity, the counting branch uninformative, the non-additive branch refuted, the "
                "positive answer a single exponent -- and now their assumption transposed into that setting "
                "rather than lost with the count."
            ),
        },
        "ledger": {
            "print_assumptions_closed": "6/6 for this module; 99/99 across the thirteen modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none \u2014 no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit; every structural input is an explicit hypothesis of the theorem statements",
        },
        "gate_result": "RESULT: 18 green (0 red) \u2014 GATE: PASS",
        "gate_negative_controls": [
            "twelve inherited from the earlier modules, all rejected",
            "a FALSE claim that the composite carries only one subsystem's exponent is REJECTED -- so independence genuinely ADDS rather than inheriting",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "no_logarithms_anywhere": True,
            "additivity_witnessed_as_nontrivial_by_a_negative_control": True,
            "structural_inputs_are_explicit_hypotheses": True,
        },
        "claim_flags": {
            "INDEPENDENCE_TRANSPOSED_TO_EXPONENT_ADDITIVITY": True,
            "PROVED_WITHOUT_LOGARITHMS": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "FACTORISATION_DERIVED_RATHER_THAN_ASSUMED": False,
            "REAL_VALUED_EXPONENTS_COVERED": False,
            "EXPONENT_SHOWN_POSITIVE_OR_EQUAL_TO_A_DIMENSION": False,
            "CLAIM_ABOUT_GR_OR_ITS_DYNAMICS": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development, if composite regions are products, the composite dilation acts "
            "diagonally, and the relative count factorises across independent subsystems, then the generating "
            "numbers multiply; and for integer exponents on dyadic scales that is exactly addition of the "
            "exponents."
        ),
        "does_not_establish": [
            "the FACTORISATION itself. That the relative count factorises across independent subsystems is a HYPOTHESIS -- it is the translation of their independence assumption, which is what is being transposed, not what is being proved",
            "real-valued exponents. Integer exponents on dyadic scales only; a real exponent needs a regularity argument this stream does not have",
            "that the exponent is positive or equals a dimension. Monotonicity is still not assumed",
            "anything about curved configurations, non-constant conformal factors, or extra structure",
            "any claim about general relativity or its dynamics",
            "a reproduction, confirmation or refutation of Carcassi--Aidala's own derivation",
            "any quantum, causal, or field-theoretic claim",
        ],
        "next_gate": "None declared. The arc from their DOF-counting trilemma to the transposed independence assumption is complete; what remains -- real-valued exponents, monotonicity, curved carriers -- are refinements rather than findings.",
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.exponent_additivity_rocq --check",
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
