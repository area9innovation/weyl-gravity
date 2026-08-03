"""Provenance record for REVERSE PHYSICS ON WEYL GRAVITY ITSELF.

The first certificate in this stream whose subject is the programme's own theory
rather than a carrier built to demonstrate the method or the Pais-Uhlenbeck toy.

Computes no mathematics. The theorems live in `rocq/WeylActionClassification.v`
and `rocq/WeylParityAndTopology.v`; the independent exact-linear-algebra rail
lives in tango `forge/examples/weyl_action_classification_gate.forge`.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_action_rocq --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_WEYL_ACTION_V1.json"

RESULT_ID = "REVERSE_PHYSICS_WEYL_ACTION_V1"
SCHEMA_NAME = "reverse-physics-weyl-action-v1"

PINNED = {
    "classification": ROOT / "rocq/WeylActionClassification.v",
    "parity": ROOT / "rocq/WeylParityAndTopology.v",
    "field_equations": ROOT / "rocq/WeylFieldEquations.v",
}

UPSTREAM_GATE = {
    "path": "tango forge/examples/weyl_action_classification_gate.forge",
    "sha256": "df6662545b0404eab644bac2ed821ad280e9410e75029e22ca2c281a97cd256e",
    "result": "exit 40, 40/40 checks; forge verify -full: c==native, ASan-clean on both backends",
    "why_it_is_a_second_rail": (
        "Different METHOD, not a rerun. The Rocq rail argues by an explicit change of basis "
        "plus linear arithmetic over Q; the Forge rail runs Gaussian elimination over Q "
        "(math/qmat ranks, determinants, nullspace dimensions, solvability). Neither computes "
        "the other's answer."
    ),
    "not_verified_here": (
        "the digest is recorded, not re-checked — the file is in another repository. "
        "Re-derive it with sha256sum before trusting this line."
    ),
}

# The physical assumptions under test, in the RP-* namespace.
ASSUMPTIONS = {
    "RP-LOCAL": "the action is the integral of a local density; total derivatives do not reach the field equations",
    "RP-METRIC": "the metric is the only field",
    "RP-DIFF": "diffeomorphism invariance",
    "RP-WEYL": "local Weyl (conformal) invariance",
    "RP-DIM4": "spacetime is four-dimensional",
    "RP-PARITY": "parity invariance",
    "RP-TOPO-INERT": "a topological term is physically inert",
    "RP-TRACELESS": "the field equations are traceless -- the field-equation-side counterpart of RP-WEYL",
}

# Classical differential geometry, ASSERTED and isolated, never re-derived here.
GEOMETRY_INPUTS = {
    "G1": "E4 = Riem^2 - 4 Ric^2 + R^2 (Gauss-Bonnet), and C^2 = Riem^2 - 4/(D-2) Ric^2 + 2/((D-1)(D-2)) R^2 (Weyl decomposition)",
    "G2": "under g -> e^{2 sigma} g: delta R = -2 sigma R - 2(D-1) Box sigma, and delta sqrt(-g) = D sigma sqrt(-g)",
    "G3": "C^a_bcd is Weyl invariant, so sqrt(-g) C^2 has Weyl weight D - 4; more generally sqrt(-g) X with X of curvature degree k has constant-Weyl weight D - 2k",
    "G4": "Integral sqrt(-g) E4 is topological in D = 4 (Gauss-Bonnet theorem)",
    "G5": "NON-DEGENERACY: there is a metric with Box R not identically zero -- matter-dominated FRW, a(t) = t^(2/3), has R = 4/(3 t^2). That this input is load-bearing is PROVED (without_non_degeneracy_the_classification_is_vacuous), not asserted; the witness metric itself is named, not formalised.",
    "G6": "the parity-odd quadratic curvature invariants are spanned by the Pontryagin density P, and in D = 4, P = C_abcd Cdual^abcd",
    "G7": "Integral sqrt(-g) P is topological (the first Pontryagin number)",
    "G8": "W_+^2 = (C^2 + P)/2 and W_-^2 = (C^2 - P)/2",
    "N1": "NOETHER, DIFFEOMORPHISMS: the metric variation of a local diff-invariant action is identically divergence-free. This is why RP-DIVFREE is not an assumption and has no independence witness.",
    "N2": "NOETHER, WEYL: the trace of the metric variation is proportional to the conformal anomaly of the action, with a NONZERO constant. This is the bridge between the two ledgers, and the non-vanishing is load-bearing (with_zero_kappa_tracelessness_is_vacuous).",
    "N3": "a topological term has identically vanishing metric variation. This is RP-TOPO-INERT, and it is what makes the topological quotient DISAPPEAR on the field-equation side.",
}

THEOREMS = [
    {
        "name": "decomposition / decomposition_unique",
        "module": "WeylActionClassification",
        "statement": "{C^2, E4, R^2} is a basis of the parity-even quadratic curvature sector over Q",
        "role": "MATHEMATICS. The change of basis from {Riem^2, Ric^2, R^2} is invertible over Q; alpha = 2a + b/2, beta = -(a + b/2), gamma = (a + b + 3c)/3.",
    },
    {
        "name": "without_non_degeneracy_the_classification_is_vacuous",
        "module": "WeylActionClassification",
        "statement": "with the non-degeneracy input G5 replaced by False, EVERY action counts as Weyl invariant",
        "role": "G5 IS LOAD-BEARING, PROVED. The non-degeneracy input is not a footnote: it is the difference between a theorem and a tautology, and this makes that visible rather than asserted in prose. A witness is named (matter-dominated FRW, a(t) = t^(2/3), R = 4/(3t^2)) but not formalised -- that would need a Riemann tensor.",
    },
    {
        "name": "weyl_invariant_is_spanned_by_weyl_sq_and_euler + span_of_weyl_sq_and_euler_is_invariant",
        "module": "WeylActionClassification",
        "statement": "the Weyl-invariance condition is the single linear equation a + b + 3c = 0, whose solution space is EXACTLY span{C^2, E4}",
        "role": "THE NECESSITY HALF and THE SUFFICIENCY HALF together. Consumes G2 (which makes the R^2 component carry the whole anomaly) and G5.",
    },
    {
        "name": "weyl_action_is_unique_modulo_topological",
        "module": "WeylActionClassification",
        "statement": "modulo the Euler density, a Weyl-invariant quadratic action is a multiple of C^2, and the multiple is determined",
        "role": "THE CLASSIFICATION. Stated with Qeq rather than Coq's exists!, whose Leibniz equality is the wrong equality on Q.",
    },
    {
        "name": "derivative_order_is_forced / in_four_dimensions_only_quadratic_survives",
        "module": "WeylActionClassification",
        "statement": "sqrt(-g) X with X of curvature degree k has constant-Weyl weight D - 2k, which vanishes iff D = 2k; at D = 4 only k = 2 survives",
        "role": "THE ASSUMPTION THAT IS NOT ONE. 'Four derivatives' is normally listed as an input. It is a CONSEQUENCE of RP-WEYL and RP-DIM4. The same computation excludes the cosmological term (k=0) and Einstein-Hilbert (k=1).",
    },
    {
        "name": "dropping_weyl_invariance_admits_r_sq",
        "module": "WeylActionClassification",
        "statement": "R^2 is not Weyl invariant and is not in span{C^2, E4}",
        "role": "INDEPENDENCE WITNESS for RP-WEYL: dropping it takes the theory from one parameter to two (three before the topological quotient).",
    },
    {
        "name": "dropping_the_topological_quotient_admits_euler",
        "module": "WeylActionClassification",
        "statement": "E4 is Weyl invariant and is not a multiple of C^2",
        "role": "INDEPENDENCE WITNESS for RP-TOPO-INERT: without the quotient the answer is two-dimensional.",
    },
    {
        "name": "weyl_sq_density_invariant_iff_dimension_four",
        "module": "WeylActionClassification",
        "statement": "sqrt(-g) C^2 is Weyl invariant iff D = 4",
        "role": "INDEPENDENCE WITNESS for RP-DIM4. The Forge rail adds the sharper fact that C^2_D degenerates to E4 exactly at D = 3, where the Weyl tensor vanishes identically.",
    },
    {
        "name": "traceless_iff_action_is_weyl_invariant + the_two_ledgers_agree",
        "module": "WeylFieldEquations",
        "statement": "the field equations are traceless iff the action is Weyl invariant, and the two conditions pick out the same one-dimensional space",
        "role": "THE VOCABULARY SWAP. RP-WEYL on the action IS RP-TRACELESS on the field equations, via N2. Proved in both directions, so neither ledger is privileged.",
    },
    {
        "name": "topological_terms_have_the_field_equations_of_zero + the_weyl_action_has_nontrivial_field_equations",
        "module": "WeylFieldEquations",
        "statement": "a topological term and zero have the same field equations, and the Weyl action does not",
        "role": "AN ASSUMPTION THAT EXISTS IN ONE VOCABULARY AND NOT THE OTHER. RP-TOPO-INERT has an independence witness on the action side; on the field-equation side there is nothing to drop, because the quotient has already been taken by the time an equation is written. The second clause is the non-vacuity control.",
    },
    {
        "name": "no_conformal_curvature_action_in_odd_dimension / exactly_one_degree_in_even_dimension",
        "module": "WeylFieldEquations",
        "statement": "in ODD dimension no conformally invariant local curvature action exists at any derivative order; in even dimension exactly one degree survives, k = D/2",
        "role": "THE PREDICTION, and it is cheap to check. Weyl gravity is a four-dimensional accident in a precise sense, and D = 6 selects the CUBIC sector -- which is the declared next gate.",
    },
    {
        "name": "parity_is_independent_on_actions",
        "module": "WeylParityAndTopology",
        "statement": "W_+^2 is Weyl invariant and is not in span{C^2, E4}",
        "role": "INDEPENDENCE WITNESS for RP-PARITY at the level of ACTIONS.",
    },
    {
        "name": "parity_is_redundant_on_field_equations",
        "module": "WeylParityAndTopology",
        "statement": "al W_+^2 + be W_-^2 has the same field equations as ((al+be)/2) C^2",
        "role": "THE RESULT. The two-parameter chiral family of actions has a ONE-parameter family of field equations. Parity invariance may be deleted from the assumption list without changing the classical theory.",
    },
    {
        "name": "classification_survives_dropping_parity",
        "module": "WeylParityAndTopology",
        "statement": "every Weyl-invariant quadratic action, of either parity, has the field equations of a multiple of C^2",
        "role": "so the classification is stable under removing RP-PARITY -- the assumption is redundant, not merely weak.",
    },
    {
        "name": "weyl_sq_is_not_topological / w_plus_is_not_topological / euler_and_pontryagin_are_independent",
        "module": "WeylParityAndTopology",
        "statement": "the topological subspace is exactly two-dimensional and contains neither C^2 nor W_+^2",
        "role": "NON-VACUITY. Without these, 'same field equations' would hold of every pair and every theorem above would be empty.",
    },
]

FINDINGS = [
    {
        "finding": "The Weyl action is EQUIVALENT to five assumptions, not merely implied by them",
        "detail": "RP-LOCAL, RP-METRIC, RP-DIFF, RP-WEYL, RP-DIM4. Modulo topological terms the solution space is exactly one-dimensional, and each assumption has an independence witness.",
    },
    {
        "finding": "The derivative order is DERIVED, not assumed",
        "detail": "Usually listed as a sixth assumption. The constant-Weyl weight D - 2k forces k = 2 at D = 4, and the same computation excludes the cosmological and Einstein-Hilbert terms. One fewer physical input than the standard motivation uses.",
    },
    {
        "finding": "Parity invariance is independent on ACTIONS and redundant on FIELD EQUATIONS",
        "detail": "The chiral family al W_+^2 + be W_-^2 is a genuine two-parameter family of actions with a one-parameter family of field equations. The fibre is the Pontryagin direction -- a gravitational theta-angle. So the assumption is real, but the level at which it becomes physical is the quantum theory.",
    },
    {
        "finding": "The programme's two certified residual classes are the parity eigenbasis of this sector",
        "detail": "C^2 = W_+^2 + W_-^2 and P = W_+^2 - W_-^2. RP-PARITY is precisely the assumption that ties [W_+^2] and [W_-^2] together, and classically it is free of charge.",
    },
    {
        "finding": "The classification degenerates correctly at D = 3",
        "detail": "C^2_D equals E4 exactly at D = 3 and nowhere else in 3..12 -- the coordinate shadow of the Weyl tensor vanishing identically in three dimensions. A consistency check the D-dependent formula was not fitted to.",
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
        "result_state": "WEYL_ACTION_CLASSIFIED_AND_ASSUMPTIONS_SEPARATED",
        "generality_level": "G4_ALL_QUADRATIC_CURVATURE_ACTIONS_ALL_DIMENSIONS",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "REVERSAL_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "record_kind": (
            "PROVENANCE_IMPORT — the mathematics is in rocq/WeylActionClassification.v and "
            "rocq/WeylParityAndTopology.v, and the second rail is in tango "
            "forge/examples/weyl_action_classification_gate.forge; this file computes nothing"
        ),
        "assumption_tags": {
            "under_test": sorted(ASSUMPTIONS),
            "consumed": [],
            "definitions": ASSUMPTIONS,
            "namespace_note": (
                "RP-* is the physical-postulate namespace and is disjoint from the "
                "computational-regime tags. Every assumption here is UNDER TEST: each has an "
                "independence witness, and RP-PARITY is shown redundant at the level of field "
                "equations."
            ),
        },
        "geometry_asserted_not_derived": GEOMETRY_INPUTS,
        "the_separation": {
            "mathematics": (
                "Everything proved: the sector is Q^3 (Q^4 with parity), the change of basis is "
                "invertible over Q, the Weyl-invariance condition is the single linear equation "
                "a + b + 3c = 0, its solution space is exactly span{C^2, E4}, and the quotient by "
                "the topological subspace is one-dimensional. Exact rational arithmetic on both "
                "rails; no floating point anywhere."
            ),
            "geometry": (
                "G1-G8 above: the Gauss-Bonnet and Weyl-decomposition identities, the conformal "
                "transformation laws, the topological character of the Euler and Pontryagin "
                "densities, and the chiral split. Classical, standard, and NOT re-derived here. "
                "Each is isolated so a reader can see exactly what would have to fail."
            ),
            "physics": (
                "The seven RP-* assumptions. These are the content: they are what the law is being "
                "shown equivalent to, and they are the only place a physical commitment enters."
            ),
            "why_three_categories_not_two": (
                "The usual split is 'assumptions' versus 'derivation'. That hides the geometry: "
                "identities like Gauss-Bonnet are neither a physical postulate nor something this "
                "development proves. Naming them separately is what makes the ledger checkable — a "
                "reader who doubts the result knows whether to attack a postulate, a textbook "
                "identity, or a rational-arithmetic computation."
            ),
        },
        "findings": FINDINGS,
        "theorems": THEOREMS,
        "ledger": {
            "print_assumptions_closed": "47/47 across the three modules; 173/173 across the nineteen modules the shared gate drives",
            "coqchk_axiom_section": "<none>",
            "declared_assumptions_in_source": "none — no Axiom, Parameter, Hypothesis, Conjecture, Admitted or admit",
            "rationals_not_reals": (
                "everything is over Q. Coq's R is axiomatised; importing it would put axioms in the "
                "ledger for statements that are rational-linear."
            ),
        },
        "gate_result": "RESULT: 24 green (0 red) — GATE: PASS",
        "upstream_gate": UPSTREAM_GATE,
        "gate_negative_controls": [
            "seventeen inherited from the earlier modules, all rejected",
            "a FALSE claim that the Weyl action has the field equations of zero is REJECTED — otherwise conformal gravity is empty and both ledgers describe nothing",
            "a FALSE claim that a conformally invariant curvature action exists at D = 3 is REJECTED — otherwise the odd-dimension prediction is empty",
            "a FALSE claim that R^2 is Weyl invariant is REJECTED — otherwise RP-WEYL cuts nothing",
            "a FALSE claim that E4 is a multiple of C^2 is REJECTED — otherwise the topological quotient is empty",
            "a FALSE claim that C^2 is topological is REJECTED — otherwise conformal gravity has no field equations and every theorem here is about an empty theory",
            "a FALSE claim that W_+^2 is parity-even is REJECTED — otherwise 'parity is independent on actions' says nothing",
            "the Forge rail carries its own non-vacuity clauses: in_row_span is asserted TRUE on a vector that is in the span, and the anomaly test is asserted NONZERO on R^2, so neither predicate can be constantly false",
        ],
        "provenance": {
            "source_manifest": manifest,
            "gate_script_not_pinned": "rocq/run.sh is harness, deliberately not hash-pinned",
            "upstream_repo": "tango (forge/examples)",
        },
        "exact_checks": {
            "zero_axiom_development": True,
            "kernel_rechecked_by_coqchk": True,
            "exact_rational_linear_algebra_upstream": True,
            "no_floating_point": True,
            "two_independent_methods": True,
        },
        "claim_flags": {
            "ACTION_CLASSIFIED_MODULO_TOPOLOGICAL": True,
            "FIELD_EQUATION_LEDGER_PROVED_EQUIVALENT": True,
            "ODD_DIMENSIONS_ADMIT_NO_CONFORMAL_CURVATURE_ACTION": True,
            "EVERY_ASSUMPTION_HAS_AN_INDEPENDENCE_WITNESS": True,
            "DERIVATIVE_ORDER_DERIVED_NOT_ASSUMED": True,
            "PARITY_REDUNDANT_ON_FIELD_EQUATIONS": True,
            "FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT": True,
            "ZERO_AXIOM_DEVELOPMENT": True,
            "THEOREM_IS_NOVEL": False,
            "CONFORMAL_TRANSFORMATION_LAWS_DERIVED": False,
            "FIELD_EQUATIONS_DERIVED": False,
            "NON_POLYNOMIAL_OR_NONLOCAL_ACTIONS_COVERED": False,
            "MATTER_COUPLINGS_COVERED": False,
            "QUANTUM_CLAIM": False,
        },
        "the_two_ledgers": {
            "on_the_action": "RP-LOCAL, RP-METRIC, RP-DIFF, RP-WEYL, RP-DIM4, RP-TOPO-INERT",
            "on_the_field_equations": "RP-LOCAL, RP-METRIC, RP-DIFF, RP-TRACELESS, RP-DIM4",
            "what_the_translation_costs": (
                "Two things move. RP-TOPO-INERT is an assumption with an independence witness on the "
                "action side and DISAPPEARS on the field-equation side, because the variation of a "
                "topological term vanishes identically. And divergence-freedom, always quoted as a "
                "property of the Bach tensor, is FREE from RP-DIFF via Noether's second theorem, so "
                "it has no independence witness and is not an assumption at all. An assumption COUNT "
                "is therefore vocabulary-dependent, which is itself worth recording."
            ),
        },
        "claim_boundary": (
            "In a zero-axiom Rocq development over Q, and independently by exact rational Gaussian "
            "elimination in Forge: the space of parity-even quadratic curvature actions is "
            "three-dimensional; local Weyl invariance cuts it to exactly span{C^2, E4}; the quotient "
            "by topological terms leaves exactly the one-dimensional span of the Weyl action; each of "
            "RP-WEYL, RP-DIM4 and RP-TOPO-INERT has an explicit independence witness; the curvature "
            "degree is forced by the dimension rather than assumed; and adjoining the parity-odd "
            "sector leaves the classical theory unchanged, so RP-PARITY is independent on actions and "
            "redundant on field equations. On the field-equation side the same law is "
            "equivalent to RP-LOCAL, RP-METRIC, RP-DIFF, RP-TRACELESS and RP-DIM4, and no "
            "conformally invariant local curvature action exists in any odd dimension."
        ),
        "does_not_establish": [
            "the theorem's novelty. That conformal gravity is the unique conformally invariant quadratic gravity in four dimensions is CLASSICAL AND TEXTBOOK. What is new here is the machine-checked zero-axiom derivation with the geometric inputs isolated, the independence witness per assumption, the derived derivative order, and the parity result",
            "the conformal transformation laws (G2, G3) or the Gauss-Bonnet and Pontryagin theorems (G4, G7). These are asserted classical differential geometry, entered as coordinate vectors and weight formulas. A reader who rejects them rejects the result, and they are listed precisely so that is possible",
            "the Bach tensor. Nothing here evaluates a metric variation. What is proved is that the space of field equations reachable from this action space is one-dimensional, and that the two assumption vocabularies pick out the same line; calling its generator the Bach tensor is an identification made in prose on the strength of N1-N3, not a theorem. 'Same field equations' is DEFINED as 'differ by a topological term', which is RP-TOPO-INERT",
            "anything about non-polynomial, nonlocal, or higher-derivative-than-quadratic actions, or about matter couplings. The classification is of polynomial curvature scalars in the pure-metric sector",
            "that RP-PARITY is redundant in the QUANTUM theory. It is not: the coefficient of the Pontryagin density is a gravitational theta-angle. Everything called redundant here is redundant modulo RP-TOPO-INERT, which is a classical statement, and this programme's claim boundary does not reach the quantum theory",
            "any claim about the BV-BFV complex, the residual cohomology, or the physical spectrum. The identification of W_+^2 and W_-^2 as the parity eigenbasis is an identity between coordinate vectors, not a statement about the certified residual classes as cohomology",
            "the two scoped Lorentzian no-go theorems, which are untouched and unaffected",
        ],
        "next_gate": (
            "WEYL_ACTION_SIX_DERIVATIVE_D6: the weight argument says the conformally invariant "
            "curvature degree in D dimensions is k = D/2, so D = 6 selects the CUBIC sector. That "
            "sector is larger (ten invariants before identities) and its conformal subspace is known "
            "to be three-dimensional plus the Euler density. Running the same exact linear algebra "
            "there would test whether the method scales and whether the parity result has an "
            "analogue. Odd D has no such sector at all, which is itself a prediction worth stating."
        ),
        "verification_commands": [
            "cd rocq && ./run.sh",
            "PYTHONPATH=. python3 -m reverse_physics.weyl_action_rocq --check",
            "cd forge && FORGE_LIB=$PWD/lib forge -run examples/weyl_action_classification_gate.forge   # exit 37",
            "cd forge && FORGE_LIB=$PWD/lib forge verify -full examples/weyl_action_classification_gate.forge",
            "sha256sum forge/examples/weyl_action_classification_gate.forge   # must match upstream_gate.sha256",
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
    print(f"{RESULT_ID}: PASS (pinned Rocq proofs hash-verified)")


if __name__ == "__main__":
    main()
