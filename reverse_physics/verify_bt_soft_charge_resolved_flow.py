#!/usr/bin/env python3
"""Independent exact verifier for the charge-resolved BT soft flow."""
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
    "REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-soft-charge-resolved-flow-v1.schema.json",
)
FULL = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json",
)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def terms(table):
    result = {}
    for term in table:
        powers = tuple(term["powers"])
        coefficient = term["coefficient"]
        real = fraction(coefficient["real"])
        imag = fraction(coefficient["imag"])
        if imag:
            raise ValueError("independent rail expects the recorded real kernel")
        result[powers] = result.get(powers, Fraction(0)) + real
    return {powers: value for powers, value in result.items() if value}


def multiply(left, right):
    result = {}
    for p, a in left.items():
        for q, b in right.items():
            powers = tuple(p[index] + q[index] for index in range(4))
            result[powers] = result.get(powers, Fraction(0)) + a * b
    return {powers: value for powers, value in result.items() if value}


def daughter_contribution(left, right):
    product = multiply(left, right)
    return {
        (e1 + 1, e2 + 1, deficit, time): 4 * coefficient
        for (e1, e2, deficit, time), coefficient in product.items()
    }


def soft_leading(value):
    blown_up = {}
    for (e1, _e2, deficit, time), coefficient in value.items():
        if time:
            raise ValueError("secular power in recorded off-resonant kernel")
        powers = (e1 + deficit, deficit)
        blown_up[powers] = blown_up.get(powers, Fraction(0)) + coefficient
    blown_up = {powers: value for powers, value in blown_up.items() if value}
    radial = min(powers[0] for powers in blown_up)
    leading = sorted(
        (alpha, coefficient)
        for (radial_power, alpha), coefficient in blown_up.items()
        if radial_power == radial
    )
    return radial, leading


def independent_rows(full):
    omega = full["off_resonant_kernel"]["delta_b_Omega"]
    upsilon = full["off_resonant_kernel"]["delta_b_Upsilon"]
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    charge = {"Omega": 1, "Upsilon": -1}
    rows = []
    for left in ("Omega", "Upsilon"):
        for right in ("Omega", "Upsilon"):
            partner = (opposite[left], opposite[right])
            first = terms(omega[f"{left}_{right}"])
            second = terms(upsilon[f"{partner[0]}_{partner[1]}"])
            radial, leading = soft_leading(daughter_contribution(first, second))
            pair_charge = charge[left] + charge[right]
            partner_charge = charge[partner[0]] + charge[partner[1]]
            q1 = -charge["Omega"] + pair_charge
            q2 = -charge["Upsilon"] + partner_charge
            rows.append({
                "omega_pair": [left, right],
                "upsilon_partner_pair": list(partner),
                "first_generator_charge": q1,
                "second_generator_charge": q2,
                "total_charge": q1 + q2,
                "leading_radial_power": radial,
                "leading_alpha_terms": [
                    {
                        "alpha_power": alpha,
                        "coefficient": {
                            "numerator": coefficient.numerator,
                            "denominator": coefficient.denominator,
                        },
                    }
                    for alpha, coefficient in leading
                ],
            })
    return rows


def verify(path):
    with open(path, encoding="utf-8") as handle:
        certificate = json.load(handle)
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    with open(FULL, encoding="utf-8") as handle:
        full = json.load(handle)

    checks = {
        "strict_schema": not list(
            Draft202012Validator(schema).iter_errors(certificate)
        )
    }
    rows = independent_rows(full)
    charge_data = certificate.get("fixed_vacuum_charge_decomposition", {})
    checks["independent_charge_rows"] = rows == charge_data.get("rows")

    log_rows = [row for row in rows if row["leading_radial_power"] == -3]
    checks["independent_charge_rows"] = (
        checks["independent_charge_rows"]
        and log_rows == charge_data.get("logarithmic_rows")
    )
    full_residue = sum(
        fraction(term["coefficient"])
        for row in log_rows
        for term in row["leading_alpha_terms"]
        if term["alpha_power"] == 0
    )
    one_sided = sum(
        fraction(term["coefficient"])
        for row in log_rows
        if row["first_generator_charge"] <= 0
        and row["second_generator_charge"] <= 0
        for term in row["leading_alpha_terms"]
        if term["alpha_power"] == 0
    )
    checks["charge_projection_obstruction"] = (
        full_residue == Fraction(-1, 2)
        and one_sided == 0
        and sorted(
            (row["first_generator_charge"], row["second_generator_charge"])
            for row in log_rows
        ) == [(-1, 1), (1, -1)]
    )

    raised = full_residue * Fraction(1, 2)
    bose = raised * Fraction(1, 2)
    shell = bose * Fraction(1, 2)
    response = -shell
    per_pair = response * Fraction(2, 6)
    total = 3 * per_pair
    hard_projector = -total
    hard = Fraction(3, 32) * hard_projector
    ledger = certificate.get("normalization_ledger_before_charge_projection", {})
    checks["independent_normalization"] = (
        raised == Fraction(-1, 4)
        and bose == Fraction(-1, 8)
        and shell == Fraction(-1, 16)
        and response == Fraction(1, 16)
        and per_pair == Fraction(1, 48)
        and total == Fraction(1, 16)
        and hard_projector == Fraction(-1, 16)
        and hard == Fraction(-3, 512)
        and fraction(ledger.get("per_unordered_pair", {"numerator": 0, "denominator": 1})) == per_pair
        and fraction(ledger.get("hard_projector_response", {"numerator": 0, "denominator": 1})) == hard_projector
        and fraction(ledger.get("absolute_hard_response", {"numerator": 0, "denominator": 1})) == hard
    )

    flow = certificate.get("finite_cutoff_flow", {})
    # For f_a(x)=x/(x+a), f_a(infinity)-f_a(0)=1.  Differentiating
    # -C int dr/r f_a(r/epsilon) therefore gives +C under log epsilon,
    # identical to a sharp lower cutoff.  The exact rational C is the shell response.
    smooth_endpoint_jump = Fraction(1) - Fraction(0)
    checks["sharp_smooth_response"] = (
        response * smooth_endpoint_jump == Fraction(1, 16)
        and flow.get("common_rescaling_response")
        == "I(c*epsilon)-I(epsilon)->+C*log(c)"
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 5 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    disposition = certificate.get("disposition", {})
    trichotomy = certificate.get("background_pushforward_trichotomy", {})
    checks["claim_boundary"] = (
        disposition.get("unprojected_soft_log_normalization")
        == "MATCHES_1_OVER_48_PER_PAIR"
        and disposition.get("one_sided_nonpositive_soft_residue") == "ZERO"
        and disposition.get("physical_neutral_one_over_48") == "NOT_ESTABLISHED"
        and disposition.get("complete_nlo_probability") == "NOT_ESTABLISHED"
        and trichotomy.get("resolved_outcome") == "UNDECIDED_FROM_PUBLIC_DATA"
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
