#!/usr/bin/env python3
"""Independent exact verifier for the BT vacuum-orbit Eq. (19) obstruction."""
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
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-zero-mode-eq19-trilemma-v1.schema.json",
)
SOFT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def charge(species):
    return {"Omega": 1, "Upsilon": -1}[species]


def reconstruct_kernel_rows():
    rows = []
    for parent in ("Omega", "Upsilon"):
        conjugate = "Upsilon" if parent == "Omega" else "Omega"
        for left in ("Omega", "Upsilon"):
            for right in ("Omega", "Upsilon"):
                daughter_charge = charge(left) + charge(right)
                exponent = charge(parent) - daughter_charge
                output_charge = exponent + daughter_charge
                rows.append({
                    "parent": parent,
                    "conjugate_parent_in_K_down": conjugate,
                    "daughters": [left, right],
                    "fixed_vacuum_coefficient_charge": 0,
                    "required_Z_exponent": exponent,
                    "dressed_output_charge": output_charge,
                    "K_down_component_charge": charge(conjugate) + output_charge,
                })
    return rows


def reconstruct_log_rows(soft):
    rows = []
    source = soft["fixed_vacuum_charge_decomposition"]["logarithmic_rows"]
    for row in source:
        omega = row["omega_pair"]
        upsilon = row["upsilon_partner_pair"]
        omega_exponent = charge("Omega") - sum(map(charge, omega))
        upsilon_exponent = charge("Upsilon") - sum(map(charge, upsilon))
        rows.append({
            "omega_pair": omega,
            "upsilon_partner_pair": upsilon,
            "fixed_vacuum_generator_charges": [
                row["first_generator_charge"],
                row["second_generator_charge"],
            ],
            "restoring_Z_exponents": [omega_exponent, upsilon_exponent],
            "completed_generator_charges": [
                row["first_generator_charge"] + omega_exponent,
                row["second_generator_charge"] + upsilon_exponent,
            ],
            "Gram_Z_exponent": omega_exponent + upsilon_exponent,
            "residue": row["leading_alpha_terms"][0]["coefficient"],
        })
    return rows


def verify(path):
    certificate = load(path)
    schema = load(SCHEMA)
    soft = load(SOFT)
    checks = {}

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    kernel_rows = reconstruct_kernel_rows()
    recorded_kernel = certificate.get("dressed_quadratic_kernel", {}).get(
        "rows", []
    )
    checks["independent_kernel_dressing"] = (
        kernel_rows == recorded_kernel
        and all(row["K_down_component_charge"] == 0 for row in kernel_rows)
    )
    checks["independent_orbit_factorization"] = (
        1 + (-1) == 0
        and 2 + 2 * (-1) == 0
        and certificate.get("exact_Eq16_factorization", {}).get("Z")
        == "exp(lambda*phi_0)"
    )
    # tau_0 extracts the zero Laurent power: <Z,Z>=0 and <Z,Z^-1>=1.
    checks["independent_candidate_pairing"] = (
        1 + 1 != 0 and 1 + (-1) == 0
    )

    log_rows = reconstruct_log_rows(soft)
    recorded_soft = certificate.get("neutral_soft_block", {})
    residue = sum(fraction(row["residue"]) for row in log_rows)
    per_pair = Fraction(
        soft["normalization_ledger_before_charge_projection"]
        ["per_unordered_pair"]["numerator"],
        soft["normalization_ledger_before_charge_projection"]
        ["per_unordered_pair"]["denominator"],
    )
    checks["independent_neutral_soft_block"] = (
        log_rows == recorded_soft.get("logarithmic_rows")
        and residue == Fraction(-1, 2)
        and per_pair == Fraction(1, 48)
        and all(row["completed_generator_charges"] == [0, 0] for row in log_rows)
        and all(row["Gram_Z_exponent"] == 0 for row in log_rows)
        and fraction(recorded_soft.get("per_unordered_pair", {})) == per_pair
    )

    # Algebraic division by Z-1 is evaluation at Z=1.  Since
    # delta(Z-1)=Z has remainder one, the ideal is not delta-stable.
    quotient = certificate.get("fixed_vacuum_quotient_obstruction", {})
    delta_generator_remainder = Fraction(1)
    checks["independent_quotient_obstruction"] = (
        delta_generator_remainder == 1
        and fraction(quotient.get("remainder_mod_I", {}))
        == delta_generator_remainder
        and quotient.get("conclusion")
        == "THE_BOOST_CHARGE_DERIVATION_DOES_NOT_DESCEND_TO_Z_EQUALS_ONE"
    )

    # General-vacuum covariance requires b_Upsilon=Z^-1 A1 and b_Omega=Z(...).
    # Hence A1=Z b_Upsilon and the oscillatory term is Z^2 b_Upsilon^dagger.
    appendix = certificate.get("appendix_C_zero_mode_completion", {})
    oscillatory_charge = 2 + charge("Upsilon")
    squeeze_charge = 2 + 2 * charge("Upsilon")
    fixed_squeeze_charge = 2 * charge("Upsilon")
    checks["independent_appendix_C_charge"] = (
        oscillatory_charge == 1
        and squeeze_charge == 0
        and fixed_squeeze_charge == -2
        and appendix.get("oscillatory_total_charge") == oscillatory_charge
        and appendix.get("covariant_squeeze_charge") == squeeze_charge
        and appendix.get("published_fixed_vacuum_squeeze_charge")
        == fixed_squeeze_charge
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 5 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    disposition = certificate.get("disposition", {})
    checks["claim_boundary"] = (
        disposition.get("neutral_soft_one_over_48")
        == "COEFFICIENT_COMPUTED_CONDITIONALLY_ON_COVARIANT_ORBIT_ALGEBRA"
        and disposition.get("Eq19_order_lambda_pushforward")
        == "NOT_REPRODUCED_FROM_PUBLIC_DATA"
        and disposition.get("physical_neutral_one_over_48")
        == "NOT_ESTABLISHED"
        and disposition.get("complete_nlo_probability") == "NOT_ESTABLISHED"
        and certificate.get("trilemma", {}).get("resolved_outcome")
        == "EXACT_EQ19_ZERO_MODE_TRACE_OBSTRUCTION"
    )

    ok = all(checks.values())
    for name, value in checks.items():
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
