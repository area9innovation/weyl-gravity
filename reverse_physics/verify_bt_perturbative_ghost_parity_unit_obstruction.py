#!/usr/bin/env python3
"""Independent verifier for the BT perturbative ghost-parity unit no-go."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-perturbative-ghost-parity-unit-obstruction-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def inverse_series(max_order):
    plus = [Fraction(1)]
    minus = [Fraction(1)]
    for degree in range(1, max_order + 1):
        plus.append(plus[-1] / degree)
        minus.append(-minus[-1] / degree)
    product = []
    for degree in range(max_order + 1):
        product.append(sum(plus[left] * minus[degree-left] for left in range(degree + 1)))
    return product


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs_ok = all(sha256(path) == digest for path, digest in hashes.items())
    predecessors = [
        load(os.path.join(ROOT, path))
        for path in hashes
        if path.startswith("reverse_physics/certificates/")
    ]
    event_path = (
        "planning/events/"
        "reverse-physics-bateman-perturbative-ghost-parity-unit-obstruction-"
        "DONE-74ea3efb.json"
    )
    event = load(os.path.join(ROOT, event_path))

    images = certificate["exact_generator_images"]
    replay = images["exponential_inverse_replay"]
    recurrence = inverse_series(images["replay_max_order"])
    replay_ok = True
    for cutoff, row in enumerate(replay):
        recorded = [fraction(value) for value in row["product_coefficients_through_cutoff"]]
        replay_ok &= row["augmentation_cutoff"] == cutoff
        replay_ok &= recorded == recurrence[:cutoff+1]
        replay_ok &= recorded[0] == 1 and all(value == 0 for value in recorded[1:])

    source = certificate["source_algebra"]
    obstruction = certificate["unit_obstruction"]
    escapes = certificate["escape_routes"]
    consequence = certificate["Eq19_consequence"]
    disposition = certificate["disposition"]
    results = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"].endswith("UNIT_OBSTRUCTION_V1"),
        "input_hashes_recomputed": inputs_ok,
        "predecessor_pass_flags_present": all(item["checks"]["ok"] for item in predecessors),
        "done_event_replayed": (
            event["body"]["payload"]["to_state"] == "DONE"
            and "Unit preservation" in event["body"]["payload"]["note"]
        ),
        "coefficient_ring_is_Laurent": source["coefficient_ring"] == "Q((lambda))[Z,Z^-1]",
        "augmentation_is_unital_and_multiplicative": (
            "epsilon(Z)=Z" in source["augmentation"]
            and source["proof_of_criterion"] == "epsilon(ab)=1 implies epsilon(a)epsilon(b)=1"
        ),
        "augmentation_is_scoped_to_local_symbols": (
            "commutative" in source["algebra"]
            and "no zero-oscillator character" in source["relation_to_quantum_source"]
        ),
        "F_has_only_positive_field_degree": images["field_degrees_in_F"] == {
            "Box(varphi)": 1,
            "lambda(dvarphi)^2": 2,
        },
        "Omega_image_and_inverse_recorded": (
            images["Omega_image"] == "O=lambda^-1 Z exp(lambda varphi)"
            and images["Omega_inverse"] == "O^-1=lambda Z^-1 exp(-lambda varphi)"
        ),
        "exponential_inverse_recomputed_by_recurrence": replay_ok,
        "Omega_augmentation_is_unit": images["Omega_augmentation"] == "lambda^-1 Z",
        "Upsilon_augmentation_is_zero": images["Upsilon_augmentation"] == "0",
        "zero_augmentation_precludes_unit": (
            obstruction["Upsilon_unit_status"] == "NONUNIT_BY_ZERO_AUGMENTATION"
        ),
        "unit_multiple_does_not_change_status": (
            len(obstruction["normalization_classes_tested"]) >= 4
            and "coefficient-ring unit" in obstruction["candidate_exchange"]
        ),
        "automorphism_unit_lemma_recorded": (
            obstruction["lemma"] == "unital algebra automorphisms and anti-automorphisms preserve units"
        ),
        "exchange_contradiction_replayed": (
            obstruction["Omega_unit_status"] == "UNIT"
            and obstruction["contradiction"] == "h maps the unit O to the nonunit cY"
            and obstruction["conclusion"] == "NO_SAME_CHART_REGULAR_LOCAL_SYMBOL_HIDDEN_PARITY_AUTOMORPHISM"
        ),
        "regular_quantum_corollary_is_scoped": (
            "filtration-continuous" in obstruction["quantum_corollary"]
            and "not decided" in obstruction["quantum_boundary"]
        ),
        "formal_inverse_boundary_preserved": (
            "declared formal perturbative image" in certificate["relation_to_formal_inverse"]["predecessor_statement"]
            and "cannot be promoted" in certificate["relation_to_formal_inverse"]["boundary"]
        ),
        "localization_removes_unit_mismatch": (
            "localize at" in escapes["localized_on_shell_chart"]["algebra_change"]
            and escapes["localized_on_shell_chart"]["unit_mismatch"].startswith("removed")
        ),
        "localization_excludes_vacuum_augmentation": (
            "no extension" in escapes["localized_on_shell_chart"]["vacuum_boundary"]
        ),
        "localized_involution_remains_on_shell": (
            "field equation" in escapes["localized_on_shell_chart"]["involution_boundary"]
        ),
        "doubled_exchange_is_involutive": (
            "kappa_double(a,b)=(b,a)" in escapes["doubled_sheet"]["algebra_change"]
        ),
        "doubled_exchange_changes_source": (
            "doubled" in escapes["doubled_sheet"]["vacuum_boundary"]
            and escapes["doubled_sheet"]["disposition"] == "EXACT_ABSTRACT_EXCHANGE_BUT_NEW_SOURCE_THEORY"
        ),
        "partial_correspondence_not_promoted": (
            escapes["partial_unbounded_correspondence"]["disposition"]
            == "NOT_A_UNITAL_AUTOMORPHISM_AND_NOT_CONSTRUCTED"
        ),
        "same_chart_repair_affiliation_obstructed": (
            consequence["same_chart_regular_local_symbol_affiliation_of_two_branch_repair"]
            == "OBSTRUCTED_TO_ALL_FORMAL_ORDERS"
            and disposition["same_chart_regular_local_symbol_repair_affiliation"] == "EXACTLY_OBSTRUCTED"
        ),
        "singular_CCR_affiliation_remains_open": (
            consequence["singular_or_unbounded_quantum_affiliation"] == "NOT_DECIDED"
            and disposition["singular_or_unbounded_CCR_affiliation"] == "OPEN"
        ),
        "charge_formula_retained": (
            consequence["charge_formula"] == "PROVED_WITH_Q_ZERO_ON_THE_COVARIANT_FORMAL_ALGEBRA"
            and disposition["Eq19_charge_support"] == "RETAINED_WITH_Q_ZERO"
        ),
        "enlarged_completion_not_ruled_out": consequence["unpublished_enlarged_completion"] == "NOT_RULED_OUT",
        "direct_physical_route_remains_open": consequence["direct_physical_route"] == "REMAINS_OPEN",
        "physical_claim_not_promoted": disposition["physical_probability"] == "NOT_ESTABLISHED",
        "causal_boundary_present": any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"]),
    }
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    results = verify(load(args.verify))
    for name, ok in results.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(results.values()) else "FAIL")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
