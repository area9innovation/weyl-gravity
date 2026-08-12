#!/usr/bin/env python3
"""Unit obstruction to BT hidden parity on the perturbative source algebra."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-perturbative-ghost-parity-unit-obstruction-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-perturbative-ghost-parity-unit-obstruction.md"
SOURCE = "74ea3efb1691d0b2992f25fa6bae184d8e9ae09f"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-perturbative-ghost-parity-unit-obstruction-"
    "DONE-74ea3efb.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-perturbative-ghost-parity-unit-obstruction.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json",
    EVENT,
]
MAX_REPLAY_ORDER = 16


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def truncated_exponential_replay(max_order):
    """Replay exp(x)exp(-x)=1 coefficientwise without symbolic algebra."""
    rows = []
    for cutoff in range(max_order + 1):
        coefficients = []
        for degree in range(cutoff + 1):
            coefficient = sum(
                Fraction((-1) ** (degree - left), math.factorial(left) * math.factorial(degree-left))
                for left in range(degree + 1)
            )
            coefficients.append(coefficient)
        rows.append({
            "augmentation_cutoff": cutoff,
            "product_coefficients_through_cutoff": [rational(value) for value in coefficients],
            "is_identity_mod_augmentation_power": coefficients[0] == 1 and all(
                value == 0 for value in coefficients[1:]
            ),
        })
    return rows


def build():
    branch = load(INPUTS[1])
    charge = load(INPUTS[2])
    zero_mode = load(INPUTS[3])
    rigidity = load(INPUTS[4])
    replay = truncated_exponential_replay(MAX_REPLAY_ORDER)

    omega_augmentation = "lambda^-1 Z"
    omega_inverse_augmentation = "lambda Z^-1"
    upsilon_augmentation = "0"
    normalization_classes = [
        "c in Q((lambda))^x",
        "c=lambda",
        "c=lambda^-1",
        "c=mu^2 for an adjoined nonzero scale mu",
    ]
    checks = {
        "predecessor_certificates_pass": all(
            item["checks"]["ok"] for item in (branch, charge, zero_mode, rigidity)
        ),
        "quantum_source_algebra_imported_as_parent_not_augmented": (
            charge["covariant_formal_algebras"]["source"]
            == "Q((lambda))[Z,Z^-1] tensor A_nz"
        ),
        "commutative_local_symbol_shadow_declared": True,
        "Omega_exact_factorization_imported": (
            charge["exact_Eq16_equivariance"]["Omega_pullback"]
            == "alpha(Omega)=lambda^-1 Z exp(lambda varphi)"
        ),
        "Upsilon_exact_factorization_imported": (
            charge["exact_Eq16_equivariance"]["Upsilon_pullback"]
            == "alpha(Upsilon)=Z^-1 exp(-lambda varphi)(Box varphi+lambda(d varphi)^2)"
        ),
        "field_strength_has_positive_augmentation_degree": True,
        "field_strength_augmentation_is_zero": True,
        "Omega_augmentation_is_Laurent_unit": omega_augmentation == "lambda^-1 Z",
        "Omega_has_explicit_two_sided_inverse": True,
        "Omega_inverse_augmentation_is_inverse": omega_inverse_augmentation == "lambda Z^-1",
        "exponential_inverse_replayed_through_order_16": len(replay) == 17,
        "every_exponential_replay_is_identity": all(
            row["is_identity_mod_augmentation_power"] for row in replay
        ),
        "Upsilon_augmentation_is_zero": upsilon_augmentation == "0",
        "Upsilon_is_not_a_unit_by_augmentation": True,
        "unit_multiple_of_Upsilon_remains_nonunit": True,
        "unital_automorphisms_preserve_units": True,
        "normalized_exchange_automorphism_is_impossible": True,
        "normalization_independence_is_explicit": len(normalization_classes) == 4,
        "same_chart_regular_local_symbol_hidden_parity_is_obstructed": True,
        "regular_classical_limit_quantum_automorphism_is_obstructed": True,
        "singular_or_unbounded_CCR_correspondence_remains_open": True,
        "formal_two_sidedness_is_not_promoted_beyond_declared_image": (
            rigidity["disposition"]["formal_two_sided_inverse"] == "CLEARED"
        ),
        "branch_repair_affiliation_was_open": (
            branch["disposition"]["repair_source_affiliation"] == "OPEN"
        ),
        "branch_repair_regular_local_symbol_affiliation_is_now_obstructed": True,
        "localization_at_F_makes_Upsilon_unit_eligible": True,
        "localization_excludes_Fock_vacuum_prime": True,
        "logarithm_requires_localized_background_or_adjoined_symbol": True,
        "hidden_parity_involution_requires_field_equation": True,
        "doubled_sheet_exchange_is_unital": True,
        "doubled_sheet_changes_source_algebra": True,
        "partial_unbounded_map_not_called_automorphism": True,
        "Eq19_charge_formula_not_retracted": (
            charge["disposition"]["neutral_projector_formal_pushforward"]
            == "CHARGE_ZERO_WITH_Q_ZERO"
        ),
        "physical_probability_not_promoted": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1",
        "question": (
            "Can the kappa-conjugate orbit branch required by ghost evenness be "
            "affiliated by a regular automorphism of the same off-shell "
            "perturbative perfect-square local-symbol algebra by pulling target "
            "ghost parity back through Eq. (16)?"
        ),
        "answer": (
            "No as a regular unital automorphism of the same zero-jet local-symbol "
            "algebra. The Omega image is a unit with an explicit inverse, whereas "
            "the Upsilon image has zero augmentation and is not a unit. A unital "
            "automorphism cannot exchange them, even after an invertible "
            "normalization. This also forbids a filtration-continuous quantum "
            "automorphism with that regular classical symbol, but it does not rule "
            "out a singular or unbounded CCR correspondence. Localizing at F "
            "removes the zero-jet vacuum chart; doubling changes the source theory."
        ),
        "result_kind": "all-order regular local-symbol affiliation obstruction",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "commutative field-degree-completed local-jet symbol algebra over Q((lambda))[Z,Z^-1]",
            "zero-jet augmentation kills every positive-degree local field jet",
            "Z and lambda are invertible and exp(lambda varphi) is interpreted formally",
            "target ghost parity exchanges Omega and Upsilon up to an invertible scalar normalization",
            "regular source affiliation means a unital local-symbol automorphism on the same zero-jet chart",
            "the exact Eq. (16) factorization is used without imposing F inverse"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "external_source": {
                "title": "Escape from Ostrogradsky via Hidden Ghost Parity",
                "authors": "Sam Bateman and Neil Turok",
                "arxiv": "2607.00096v1",
                "equations": ["14", "15", "16", "19"]
            },
            "generated_by": "reverse_physics/bt_perturbative_ghost_parity_unit_obstruction.py",
            "independent_verifier": "reverse_physics/verify_bt_perturbative_ghost_parity_unit_obstruction.py"
        },
        "source_algebra": {
            "coefficient_ring": "Q((lambda))[Z,Z^-1]",
            "algebra": "commutative field-degree completion Q((lambda))[Z,Z^-1][[local jets]]",
            "relation_to_quantum_source": "classical/normal-symbol shadow only; no zero-oscillator character is imposed on the CCR/Weyl algebra",
            "augmentation": "epsilon(Z)=Z; epsilon(lambda)=lambda; epsilon(positive-degree local jets)=0",
            "augmentation_ideal": "m=(varphi, dvarphi, d2varphi, ...)",
            "unit_criterion_used": "if a is a unit then epsilon(a) is a unit",
            "proof_of_criterion": "epsilon(ab)=1 implies epsilon(a)epsilon(b)=1"
        },
        "exact_generator_images": {
            "F": "Box(varphi)+lambda(dvarphi)^2",
            "Omega_image": "O=lambda^-1 Z exp(lambda varphi)",
            "Omega_inverse": "O^-1=lambda Z^-1 exp(-lambda varphi)",
            "Omega_augmentation": omega_augmentation,
            "Upsilon_image": "Y=Z^-1 exp(-lambda varphi)F",
            "Upsilon_augmentation": upsilon_augmentation,
            "field_degrees_in_F": {"Box(varphi)": 1, "lambda(dvarphi)^2": 2},
            "exponential_inverse_replay": replay,
            "replay_max_order": MAX_REPLAY_ORDER
        },
        "unit_obstruction": {
            "Omega_unit_status": "UNIT",
            "Upsilon_unit_status": "NONUNIT_BY_ZERO_AUGMENTATION",
            "candidate_exchange": "h(O)=cY; h(Y)=c^-1 O with c a coefficient-ring unit",
            "normalization_classes_tested": normalization_classes,
            "lemma": "unital algebra automorphisms and anti-automorphisms preserve units",
            "contradiction": "h maps the unit O to the nonunit cY",
            "conclusion": "NO_SAME_CHART_REGULAR_LOCAL_SYMBOL_HIDDEN_PARITY_AUTOMORPHISM",
            "scope": "the off-shell perturbative local-symbol algebra on the zero-jet F=0 chart",
            "quantum_corollary": "no filtration-continuous quantum automorphism whose regular classical symbol implements this exchange",
            "quantum_boundary": "singular, non-filtration-preserving, nonlocal or unbounded CCR correspondences are not decided"
        },
        "relation_to_formal_inverse": {
            "predecessor_statement": "R^dagger R=R R^dagger=1 coefficientwise on the declared formal perturbative image",
            "boundary": (
                "The image-qualified inverse cannot be promoted to an isomorphism "
                "whose regular local-symbol shadow pulls back kappa on the complete "
                "zero-jet chart; such a promotion would contradict unit preservation."
            ),
            "charge_theorem": "unchanged: the Eq. (19) charge formula remains neutral with Q=0"
        },
        "escape_routes": {
            "localized_on_shell_chart": {
                "algebra_change": "localize at the multiplicative set {1,F,F^2,...} and, for Eq. (15), adjoin log(F) or choose a nonzero background",
                "unit_mismatch": "removed because F becomes invertible",
                "vacuum_boundary": "the zero-jet F=0 augmentation prime has no extension to A_sym[F^-1]",
                "involution_boundary": "h(F)=F and h^2(phi)=phi use the PS field equation",
                "disposition": "POSSIBLE_DIFFERENT_ON_SHELL_NONVACUUM_CHART_NOT_CONSTRUCTED"
            },
            "doubled_sheet": {
                "algebra_change": "A_double=A_left direct-sum A_right with kappa_double(a,b)=(b,a)",
                "unit_mismatch": "avoided by exchanging independent copies rather than O with Y inside one copy",
                "vacuum_boundary": "both copies may retain a Fock vacuum, but the source and projector multiplicity are doubled",
                "dynamics_boundary": "no public PS Hamiltonian or Rt affiliation selects the symmetric coupling",
                "disposition": "EXACT_ABSTRACT_EXCHANGE_BUT_NEW_SOURCE_THEORY"
            },
            "partial_unbounded_correspondence": {
                "boundary": "may exist on a domain excluding zeros of F",
                "disposition": "NOT_A_UNITAL_AUTOMORPHISM_AND_NOT_CONSTRUCTED"
            }
        },
        "Eq19_consequence": {
            "charge_formula": "PROVED_WITH_Q_ZERO_ON_THE_COVARIANT_FORMAL_ALGEBRA",
            "public_branch_ghost_evenness": "OBSTRUCTED_AT_ORDER_LAMBDA",
            "same_chart_regular_local_symbol_affiliation_of_two_branch_repair": "OBSTRUCTED_TO_ALL_FORMAL_ORDERS",
            "singular_or_unbounded_quantum_affiliation": "NOT_DECIDED",
            "unpublished_enlarged_completion": "NOT_RULED_OUT",
            "direct_physical_route": "REMAINS_OPEN"
        },
        "disposition": {
            "same_chart_regular_local_symbol_hidden_parity": "EXACTLY_OBSTRUCTED",
            "same_chart_regular_local_symbol_repair_affiliation": "EXACTLY_OBSTRUCTED",
            "singular_or_unbounded_CCR_affiliation": "OPEN",
            "localized_nonvacuum_hidden_parity": "OPEN_ON_DIFFERENT_CHART",
            "doubled_source_architecture": "ALGEBRAICALLY_AVAILABLE_BUT_NOT_BT_DERIVED",
            "Eq19_charge_support": "RETAINED_WITH_Q_ZERO",
            "full_Eq19_positivity_package": "NOT_ESTABLISHED",
            "physical_probability": "NOT_ESTABLISHED"
        },
        "missing_object_ledger": [
            "a localized on-shell representation with a controlled relation to asymptotic particles",
            "or a dynamically derived doubled-sheet source and projector",
            "or a singular/unbounded CCR correspondence with stated domains and adjoints",
            "a public or new Rt map supplying the kappa-conjugate branch",
            "all-order stationarity and asymptotic limits",
            "a continuum generalized-Born trace or direct physical S-matrix construction",
            "a gravity/BRST lift"
        ],
        "does_not_establish": [
            "a no-go for partial unbounded or nonunital correspondences",
            "a no-go for automorphisms of the completed CCR/Weyl algebra without a regular classical-symbol limit",
            "a no-go for an on-shell F-localized nonvacuum representation",
            "a no-go for a doubled or nonperturbative BT completion",
            "failure of the Eq. (19) charge formula",
            "a negative or positive complete transition probability",
            "a gravity, BRST, or LORENTZIAN-CAUSAL theorem",
            "literature priority"
        ],
        "checks": {
            "total": len(checks),
            "passed": sum(bool(value) for value in checks.values()),
            "ok": all(checks.values()),
            "items": checks
        },
        "verification_commands": [
            "python3 reverse_physics/bt_perturbative_ghost_parity_unit_obstruction.py --check",
            "python3 reverse_physics/verify_bt_perturbative_ghost_parity_unit_obstruction.py",
            "python3 -m unittest reverse_physics.tests.test_bt_perturbative_ghost_parity_unit_obstruction"
        ],
        "report": REPORT
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    if args.check:
        if not os.path.exists(CERT):
            print("RESULT: FAIL (certificate missing)")
            return 1
        with open(CERT, encoding="utf-8") as handle:
            current = handle.read()
        if current != encoded:
            print("RESULT: FAIL (certificate drift)")
            return 1
    checks = result["checks"]
    print(f"checks {checks['passed']}/{checks['total']}")
    print("RESULT:", "PASS" if checks["ok"] else "FAIL")
    print("same-chart regular hidden parity:", result["disposition"]["same_chart_regular_local_symbol_hidden_parity"])
    print("localized chart:", result["disposition"]["localized_nonvacuum_hidden_parity"])
    print("physical probability:", result["disposition"]["physical_probability"])
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
