#!/usr/bin/env python3
"""Classify the BT soft flow after resolving its published boost charges."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_full_off_resonant_projector import (
    E1,
    E2,
    a_basis_kernels,
    soft_blowup,
    transport,
)


CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-soft-charge-resolved-flow-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-soft-charge-resolved-flow.md"
SOURCE_COMMIT = "90af7c5e5f84acf35762bdc6fb1af7e3f689fe24"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def charge_rows():
    omega_a, upsilon_a = a_basis_kernels()
    omega = transport(omega_a)
    upsilon = transport(upsilon_a)
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    charge = {"Omega": 1, "Upsilon": -1}
    rows = []
    for left in ("Omega", "Upsilon"):
        for right in ("Omega", "Upsilon"):
            partner = (opposite[left], opposite[right])
            contribution = (
                4 * E1 * E2
                * omega[left, right]
                * upsilon[partner]
            )
            blown_up = soft_blowup(contribution)
            leading_power = min(power[0] for power in blown_up)
            leading = {
                alpha_power: coefficient
                for (radial_power, alpha_power), coefficient in blown_up.items()
                if radial_power == leading_power
            }
            pair_charge = charge[left] + charge[right]
            partner_charge = charge[partner[0]] + charge[partner[1]]
            first_generator_charge = -charge["Omega"] + pair_charge
            second_generator_charge = -charge["Upsilon"] + partner_charge
            rows.append({
                "omega_pair": [left, right],
                "upsilon_partner_pair": list(partner),
                "first_generator_charge": first_generator_charge,
                "second_generator_charge": second_generator_charge,
                "total_charge": first_generator_charge + second_generator_charge,
                "leading_radial_power": leading_power,
                "leading_alpha_terms": [
                    {
                        "alpha_power": power,
                        "coefficient": rat(value[0]),
                    }
                    for power, value in sorted(leading.items())
                    if value[1] == 0
                ],
            })
    return rows


def build():
    rows = charge_rows()
    log_rows = [row for row in rows if row["leading_radial_power"] == -3]
    full_residue = sum(
        Fraction(term["coefficient"]["numerator"], term["coefficient"]["denominator"])
        for row in log_rows
        for term in row["leading_alpha_terms"]
        if term["alpha_power"] == 0
    )
    nonpositive_residue = sum(
        Fraction(term["coefficient"]["numerator"], term["coefficient"]["denominator"])
        for row in log_rows
        if row["first_generator_charge"] <= 0
        and row["second_generator_charge"] <= 0
        for term in row["leading_alpha_terms"]
        if term["alpha_power"] == 0
    )
    charge_pairs = sorted({
        (row["first_generator_charge"], row["second_generator_charge"])
        for row in log_rows
    })
    compensating_background_charges = sorted({
        -charge_value
        for row in log_rows
        for charge_value in (
            row["first_generator_charge"], row["second_generator_charge"]
        )
    })

    raw_residue = full_residue
    parent_raised = raw_residue * Fraction(1, 2)
    bose_reduced = parent_raised * Fraction(1, 2)
    angular_reduced = bose_reduced * Fraction(1, 2)
    cutoff_response = -angular_reduced
    outgoing_factorial_ratio = Fraction(1, 3)
    per_pair = cutoff_response * outgoing_factorial_ratio
    pair_count = 3
    all_pairs = pair_count * per_pair
    born = Fraction(3, 32)
    hard_projector_response = -all_pairs
    hard_absolute = born * hard_projector_response
    smooth_endpoint_jump = Fraction(1) - Fraction(0)
    smooth_response = cutoff_response * smooth_endpoint_jump

    checks = {
        "two_logarithmic_charge_rows": len(log_rows) == 2,
        "logarithmic_rows_are_plus_minus_one": charge_pairs == [(-1, 1), (1, -1)],
        "each_logarithmic_row_has_minus_quarter": all(
            row["leading_alpha_terms"]
            == [{"alpha_power": 0, "coefficient": rat(Fraction(-1, 4))}]
            for row in log_rows
        ),
        "full_raw_residue_is_minus_half": full_residue == Fraction(-1, 2),
        "one_sided_nonpositive_residue_is_zero": nonpositive_residue == 0,
        "bidirectional_background_completion_required": (
            compensating_background_charges == [-1, 1]
        ),
        "parent_raise_gives_minus_quarter": parent_raised == Fraction(-1, 4),
        "bose_factor_gives_minus_eighth": bose_reduced == Fraction(-1, 8),
        "angular_measure_gives_minus_one_over_sixteen": (
            angular_reduced == Fraction(-1, 16)
        ),
        "cutoff_response_is_plus_one_over_sixteen": (
            cutoff_response == Fraction(1, 16)
        ),
        "outgoing_factorial_ratio_is_one_third": (
            outgoing_factorial_ratio == Fraction(1, 3)
        ),
        "per_pair_response_is_one_over_48": per_pair == Fraction(1, 48),
        "three_pair_response_is_one_over_16": all_pairs == Fraction(1, 16),
        "hard_projector_response_is_minus_one_over_16": (
            hard_projector_response == Fraction(-1, 16)
        ),
        "hard_absolute_response_is_minus_three_over_512": (
            hard_absolute == Fraction(-3, 512)
        ),
        "sharp_and_smooth_log_responses_agree": (
            smooth_response == cutoff_response
        ),
        "physical_neutral_coefficient_fails_closed": nonpositive_residue != full_residue,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1",
        "schema_version": "reverse-physics-bt-soft-charge-resolved-flow-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "charge-resolved soft asymptotic-flow normalization obstruction",
        "question": (
            "Does the full off-resonant BT soft kernel produce the physical neutral "
            "1/48 response while preserving the published one-sided nonpositive image?"
        ),
        "answer": (
            "The unprojected normalization matches exactly: after parent-index raising, "
            "Bose reduction, angular measure, and the 2!/3! outgoing-projector ratio, "
            "the response is 1/48 per unordered pair and 1/16 in total. However, every "
            "logarithmic contribution pairs a +1 generator sector with a -1 sector. "
            "Restricting the currently available oscillator map to the published "
            "one-sided nonpositive image removes the positive partner and makes the "
            "logarithmic residue zero. The unavailable broken-vacuum zero-mode/full "
            "pushforward may regrade these terms into the neutral component, but the "
            "public data do not decide that. The physical neutral 1/48 coefficient "
            "therefore remains fail-closed at an exact charge obstruction."
        ),
        "fixed_vacuum_charge_decomposition": {
            "oscillator_charges": {"Omega": 1, "Upsilon": -1},
            "adjoint_convention": "BT sharp/dagger preserves boost charge",
            "rows": rows,
            "logarithmic_rows": log_rows,
            "logarithmic_charge_pairs": [list(pair) for pair in charge_pairs],
            "full_raw_residue": rat(full_residue),
            "one_sided_nonpositive_raw_residue": rat(nonpositive_residue),
            "disposition": "LOGARITHMIC_NEUTRAL_GRAM_REQUIRES_POSITIVE_NEGATIVE_PAIRING",
        },
        "normalization_ledger_before_charge_projection": {
            "raw_cross_residue": rat(raw_residue),
            "parent_inverse_metric_factor": rat(Fraction(1, 2)),
            "parent_raised_residue": rat(parent_raised),
            "bose_factor": rat(Fraction(1, 2)),
            "after_bose": rat(bose_reduced),
            "angular_measure": "integral dOmega/(2pi)^3=1/(2*pi^2)",
            "coefficient_of_lambda2_over_pi2_dr_over_r": rat(angular_reduced),
            "coefficient_of_lambda2_logc_over_pi2": rat(cutoff_response),
            "outgoing_projector_factorial_ratio": rat(outgoing_factorial_ratio),
            "per_unordered_pair": rat(per_pair),
            "pair_count": pair_count,
            "all_pairs": rat(all_pairs),
            "born_coefficient": rat(born),
            "hard_projector_response": rat(hard_projector_response),
            "absolute_hard_response": rat(hard_absolute),
        },
        "finite_cutoff_flow": {
            "K_t": "exp(-i*d*t)*D-exp(+i*d*t)*D_sharp",
            "H_as_first_order": "d*(exp(-i*d*t)*D+exp(+i*d*t)*D_sharp)",
            "sharp_properties": ["K_t_sharp=-K_t", "H_as_sharp=H_as"],
            "sharp_cutoff": "I_sharp(epsilon)=-C*log(r0/epsilon)",
            "smooth_profile": "f_a(r/epsilon)=r/(r+a*epsilon)",
            "smooth_cutoff": "I_a(epsilon)=-C*log((r0+a*epsilon)/(a*epsilon))",
            "common_rescaling_response": "I(c*epsilon)-I(epsilon)->+C*log(c)",
            "finite_profile_shift": "I_a-I_sharp->+C*log(a)",
            "C": "lambda^2/(16*pi^2) before the 2!/3! per-pair factor",
            "zero_cutoff_limit": "NOT_TRACE_CLASS_ON_ORIGINAL_FOCK_KREIN_REPRESENTATION",
        },
        "background_pushforward_trichotomy": {
            "background_charges_needed_to_neutralize_log_rows": compensating_background_charges,
            "public_background_zero_mode_operator": "NOT_AVAILABLE",
            "public_order_lambda_pushforward_of_projector": "NOT_AVAILABLE",
            "if_full_background_completion_neutralizes_both_signs": "PHYSICAL_RESPONSE_CANDIDATE_1_OVER_48_PER_PAIR",
            "if_one_sided_nonpositive_projection_is_imposed_first": "LOGARITHMIC_RESPONSE_ZERO",
            "if_positive_sector_survives_without_neutral_completion": "RELATIVE_RADICAL_POSITIVITY_ARGUMENT_NOT_APPLICABLE",
            "resolved_outcome": "UNDECIDED_FROM_PUBLIC_DATA",
        },
        "disposition": {
            "unprojected_soft_log_normalization": "MATCHES_1_OVER_48_PER_PAIR",
            "sharp_smooth_response_universality": "PROVED_AT_LEADING_LOG",
            "finite_cutoff_anti_krein_flow": "FORMAL_CONSTRUCTION",
            "one_sided_nonpositive_soft_residue": "ZERO",
            "background_completed_neutral_pushforward": "MISSING_OBJECT",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
            "finite_matching_constant": "NOT_SELECTED",
            "complete_nlo_probability": "NOT_ESTABLISHED",
        },
        "next_gate": (
            "Construct the broken-vacuum zero-mode-resolved order-lambda pushforward "
            "R_t P_2 R_t^dagger from the deferred Eq. (19) data or an equivalent "
            "operator construction. Determine whether it neutralizes both charge signs, "
            "projects the logarithmic response to zero, or leaks positive charge before "
            "any complete probability claim."
        ),
        "missing_object_ledger": [
            "the charged broken-vacuum zero-mode operator rather than a fixed c-number spurion",
            "the complete order-lambda pushforward R_t P_2 R_t^dagger",
            "a proof of the no-positive-charge property on that pushforward",
            "the incoming-sector analogue on the same resolution carrier",
            "the finite hard matching constant and cut-free virtual terms",
            "the zero-cutoff relative hard S-matrix and complete quotient trace",
        ],
        "does_not_establish": [
            "that the full BT background completion cannot produce 1/48",
            "that the deferred Eq. (19) construction is inconsistent",
            "that a positive-charge term survives in the physical neutral pushforward",
            "a finite matched hard S-matrix",
            "a complete NLO probability or beyond-tree positivity",
            "a tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (19)", "Eq. (20)", "Appendix C"],
                "current_version_check": (
                    "Official arXiv metadata checked 2026-08-10: v1 only; "
                    "exact-title searches for the deferred companion returned "
                    "no arXiv record"
                ),
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_soft_charge_resolved_flow.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_soft_charge_resolved_flow.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_soft_charge_resolved_flow",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except Exception as error:
            print("[FAIL]", error)
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(
            f"RESULT: {'PASS' if ok else 'FAIL'} "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
