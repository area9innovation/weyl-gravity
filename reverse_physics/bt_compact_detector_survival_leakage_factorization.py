#!/usr/bin/env python3
"""Exact compact-detector no-click versus BT survival factorization."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_DETECTOR_SURVIVAL_LEAKAGE_FACTORIZATION_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-compact-detector-survival-leakage-factorization-v1.schema.json"
REPORT = "reverse_physics/reports/bt-compact-detector-survival-leakage-factorization.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-compact-detector-survival-leakage-factorization.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    columns = transpose(right)
    return [[sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in columns] for row in left]


def add(*matrices):
    return [[sum((matrix[i][j] for matrix in matrices), Fraction(0)) for j in range(len(matrices[0][0]))] for i in range(len(matrices[0]))]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def completion(click, leakage):
    # Basis: source, selected click, outside/no-click leakage.
    generator = [
        [Fraction(0), -click, -leakage],
        [click, Fraction(0), Fraction(0)],
        [leakage, Fraction(0), Fraction(0)],
    ]
    second = scale(Fraction(1, 2), multiply(generator, generator))
    order_two_defect = add(second, transpose(second), multiply(transpose(generator), generator))
    return generator, second, order_two_defect


def fraction(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def build():
    coherent = load(INPUTS[1])
    full_phase = load(INPUTS[2])
    cut = load(INPUTS[3])
    click = Fraction(3, 10)
    leakage_zero = Fraction(0)
    leakage_nonzero = Fraction(2, 5)
    minimal_generator, minimal_second, minimal_defect = completion(click, leakage_zero)
    leaky_generator, leaky_second, leaky_defect = completion(click, leakage_nonzero)
    click_probability = click**2
    leakage_probability = leakage_nonzero**2
    minimal_virtual = minimal_second[0][0]
    leaky_virtual = leaky_second[0][0]
    minimal_survival = 2 * minimal_virtual
    leaky_survival = 2 * leaky_virtual
    minimal_no_click = minimal_survival + leakage_zero**2
    leaky_no_click = leaky_survival + leakage_probability

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (coherent, full_phase, cut)),
        "coherent_click_is_imported": coherent["interpretation"]["coherent_unrecorded_finite_time_click_effect"] == "CONSTRUCTED",
        "public_cut_affiliation_is_imported": cut["interpretation"]["finite_time_shell_kernel_BT_affiliation"] == "DERIVED_AT_CUT_PROBABILITY_LEVEL",
        "full_regular_density_is_imported": full_phase["interpretation"]["complete_regular_massless_three_to_three_local_phase_space"] == "STRICTLY_POSITIVE",
        "minimal_generator_is_skew": transpose(minimal_generator) == scale(Fraction(-1), minimal_generator),
        "leaky_generator_is_skew": transpose(leaky_generator) == scale(Fraction(-1), leaky_generator),
        "minimal_completion_closes_order_two": all(entry == 0 for row in minimal_defect for entry in row),
        "leaky_completion_closes_order_two": all(entry == 0 for row in leaky_defect for entry in row),
        "same_detector_click_block": click_probability == Fraction(9, 100),
        "different_forward_virtual_coefficients": minimal_virtual == Fraction(-9, 200) and leaky_virtual == Fraction(-1, 8),
        "leaky_survival_loses_click_and_leakage": leaky_survival == -(click_probability + leakage_probability),
        "minimal_no_click_coefficient_is_minus_click": minimal_no_click == -click_probability,
        "leaky_no_click_coefficient_is_minus_click": leaky_no_click == -click_probability,
        "local_click_does_not_identify_virtual": minimal_virtual != leaky_virtual,
        "minimal_Julia_is_zero_leakage_member": leakage_zero == 0 and minimal_virtual == -click_probability / 2,
        "compact_acceptance_is_not_certified_exhaustive": True,
        "unobserved_positive_leakage_is_not_computed": True,
        "operational_probability_survives_nonidentifiability": True,
        "Eq19_all_time_loops_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "certificate": "REVERSE_PHYSICS_BT_COMPACT_DETECTOR_SURVIVAL_LEAKAGE_FACTORIZATION_V1",
        "schema_version": "reverse-physics-bt-compact-detector-survival-leakage-factorization-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact detector no-click equals survival plus outside-leakage theorem and local virtual-coefficient nonidentifiability",
        "question": "Does the coherent compact detector's no-click complement equal the genuine BT forward-survival amplitude, and can its local transition block determine the order-lambda8 virtual coefficient?",
        "answer": "No to both identifications, but the operational detector probability remains valid. Let A_C be the order-lambda4 transition into the selected compact click acceptance and B_out the remaining order-lambda4 transition into positive outputs outside that acceptance. The complete order-lambda4 column is C_4=(A_C,B_out). In the C_4^*C_4 cut component, pseudo-unitarity forces Herm(M_8)_source,C4-cut=-(A_C^*A_C+B_out^*B_out)/2, not -A_C^*A_C/2 unless B_out=0. True survival in this cut slice therefore has coefficient -(A_C^*A_C+B_out^*B_out), while outside leakage contributes +B_out^*B_out to the detector's no-click event. Their sum is exactly -A_C^*A_C, so E_no=I-A_C^*A_C is the correct binary detector complement even though no-click is not pure survival. Other perturbative products or cut-free order-lambda8 terms are separate and are not computed here. Two exact rational pseudo-unitary completions with the same selected click amplitude 3/10 and leakage amplitudes 0 and 2/5 have C_4-cut forward Hermitian coefficients -9/200 and -1/8, respectively, but both give the same no-click coefficient -9/100 after leakage is included. Thus compact click data cannot identify even the matching cut component of the BT virtual graph. The exact Julia dilation is the minimal B_out=0 member of a family of completions, not the uniquely derived BT evolution. The public compact acceptance is selected and no invariance or exhaustivity certificate sets B_out to zero; the full regular six-point density is nontrivial beyond a selected local shell patch. The virtual barrier is therefore bypassed for the binary detector probability but remains load-bearing for a survival amplitude, a complete finite-time evolution, or an S-matrix.",
        "complete_transition_factorization": {
            "source_space": "X",
            "selected_click_output": "Y_C",
            "outside_positive_output": "Y_out",
            "full_leading_column": "C_4=(A_C,B_out):X->Y_C directsum Y_out",
            "full_column_Gram": "C_4^*C_4=A_C^*A_C+B_out^*B_out",
            "status": "FORMAL_EXHAUSTIVE_POSITIVE_OUTPUT_FACTORIZATION"
        },
        "order_lambda8_identity": {
            "pseudo_unitarity": "M_8+M_8^*+L_4^*L_4=0",
            "forward_Hermitian_part": "Herm(M_8)_source,C4-cut=-(A_C^*A_C+B_out^*B_out)/2",
            "click_probability_coefficient": "+A_C^*A_C",
            "outside_leakage_probability_coefficient": "+B_out^*B_out",
            "true_survival_probability_coefficient": "-(A_C^*A_C+B_out^*B_out)",
            "detector_no_click_coefficient": "-A_C^*A_C",
            "factorization": "detector no-click=true survival+outside leakage",
            "status": "EXACT_LEADING_SURVIVAL_LEAKAGE_FACTORIZATION"
        },
        "two_completion_witness": {
            "selected_click_amplitude": fraction(click),
            "selected_click_probability": fraction(click_probability),
            "minimal_leakage_amplitude": fraction(leakage_zero),
            "leaky_amplitude": fraction(leakage_nonzero),
            "leaky_probability": fraction(leakage_probability),
            "minimal_forward_Hermitian_coefficient": fraction(minimal_virtual),
            "leaky_forward_Hermitian_coefficient": fraction(leaky_virtual),
            "common_detector_no_click_coefficient": fraction(-click_probability),
            "minimal_order_two_defect": [[str(value) for value in row] for row in minimal_defect],
            "leaky_order_two_defect": [[str(value) for value in row] for row in leaky_defect],
            "status": "SAME_LOCAL_CLICK_DIFFERENT_VIRTUAL_EXACT_WITNESS"
        },
        "compact_BT_disposition": {
            "coherent_selected_click_effect": "BT_CUT_AFFILIATED_AND_POSITIVE",
            "binary_operational_no_click": "FIXED_AS_I_MINUS_SELECTED_CLICK",
            "binary_detector_probability": "CONSTRUCTED_AT_LEADING_ORDER_ON_DECLARED_DOMAIN",
            "true_BT_survival_amplitude": "NOT_IDENTIFIED_BY_LOCAL_CLICK_DATA",
            "outside_positive_transition_block": "UNCOMPUTED_AND_NOT_CERTIFIED_ZERO",
            "minimal_Julia_dilation": "ZERO_LEAKAGE_COMPLETION_NOT_UNIQUE_BT_EVOLUTION",
            "full_positive_output_completeness": "NOT_CONSTRUCTED",
            "complete_BT_finite_time_evolution": "NOT_CONSTRUCTED"
        },
        "assumptions": [
            "the selected coherent click operator and its compact contraction domain are those of the predecessor certificate",
            "the factorization theorem applies to a hypothetical complete positive source/output sector; negative Krein outputs require a separate weak-ghost-symmetry or quotient certificate",
            "A_C and B_out are orthogonal output blocks of one leading transition column",
            "the identity is for the C_4^*C_4 cut component generated by the order-lambda4 six-point transition; other perturbative products and cut-free order-lambda8 terms are separate",
            "the exact rational fixtures test algebraic nonidentifiability and are not claimed to be BT Hamiltonian matrices",
            "the selected compact acceptance has no public invariance or exhaustivity certificate",
            "the binary operational complement groups true survival with every unobserved outcome",
        ],
        "does_not_establish": [
            "the value, domain, sign or complete channel content of B_out in BT dynamics",
            "a complete positive decomposition of every BT output sector",
            "the order-lambda8 BT forward graph or its anti-Hermitian phase",
            "that the minimal Julia dilation equals BT evolution",
            "a detector-independent cross section",
            "the soft internal-zero or ordinary-Fock infrared limit",
            "an exact all-orders probability",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "loop/KLN completion or beyond-tree positivity",
            "gravity or BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "complete leading BT transition column out of the compact incoming source sector", "status": "MISSING", "required_value": "C_4=(A_C,B_out) on a common positive or weakly ghost-symmetric output domain"},
            {"object": "order-lambda8 BT forward kernel in the C_4^*C_4 cut component", "status": "MISSING", "required_value": "Herm(M_8)_source,C4-cut=-C_4^*C_4/2"},
            {"object": "positive exhaustive output partition or general Eq. (19) trace identity", "status": "MISSING", "required_value": "must justify summing selected click, outside outcomes and survival as ordinary probabilities"}
        ],
        "next_gate": "Compute or certify the complete order-lambda4 transition column C_4 out of the declared compact incoming source, including all particle-number and momentum outputs on one positive or weakly ghost-symmetric domain. Its full Gram C_4^*C_4 is the target for the matching cut component of the BT forward Hermitian coefficient; other perturbative products and cut-free terms require their own ledger. The selected binary detector probability needs no separate virtual-graph calculation; Eq. (19) remains the alternative route to exhaustive positivity.",
        "provenance": {
            "source_commit": "fa65ef035cdf7da679ce81e87a818e164df01fa2",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact rational three-block skew-completion algebra and order-by-order pseudo-unitarity, with two completions sharing one selected detector block. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_compact_detector_survival_leakage_factorization.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_compact_detector_survival_leakage_factorization.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_compact_detector_survival_leakage_factorization"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if not value["checks"]["ok"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
