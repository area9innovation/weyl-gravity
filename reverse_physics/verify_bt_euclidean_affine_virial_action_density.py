#!/usr/bin/env python3
"""Independent verifier for the BT affine virial/action-density theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-affine-virial-action-density-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def alternating_log_two_lower() -> Fraction:
    return sum(
        (Fraction(1 if index % 2 else -1, index) for index in range(1, 21)),
        Fraction(0),
    )


def exponential_partial_sum(x: Fraction, degree: int) -> Fraction:
    total = Fraction(1)
    power = Fraction(1)
    factorial = 1
    for index in range(1, degree + 1):
        power *= x
        factorial *= index
        total += power / factorial
    return total


def dyadic_exponent(weight: Fraction) -> int:
    numerator = weight.numerator
    denominator = weight.denominator
    exponent = 0
    while numerator > 1 and numerator % 2 == 0:
        numerator //= 2
        exponent += 1
    while denominator > 1 and denominator % 2 == 0:
        denominator //= 2
        exponent -= 1
    if numerator != 1 or denominator != 1:
        raise ValueError("non-dyadic fixture")
    return exponent


def reconstruct_fixture(row: dict) -> dict[str, Fraction]:
    weights = [decode(value) for value in row["weights"]]
    degree = len(weights)
    total = sum(weights, Fraction(0))
    residual = total - degree
    coefficient = sum(
        (weight * dyadic_exponent(weight) for weight in weights),
        Fraction(0),
    )
    return {
        "sum": total,
        "residual": residual,
        "coefficient": coefficient,
        "product_coefficient": residual * coefficient,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    errors = list(Draft202012Validator(schema).iter_errors(certificate))
    checks["strict_schema"] = not errors
    checks["closed_internal_check_ledger"] = (
        certificate.get("checks", {}).get("ok") is True
        and certificate["checks"]["passed"] == certificate["checks"]["total"] == 15
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    theorem = certificate.get("pointwise_affine_virial_theorem", {})
    log_data = theorem.get("q8_log_certificate", {})
    lower = alternating_log_two_lower()
    exp_lower = exponential_partial_sum(Fraction(7, 10), 4)
    checks["rational_log_brackets_rederived"] = (
        lower == Fraction(155685007, 232792560)
        and lower > Fraction(2, 3)
        and exp_lower == Fraction(482921, 240000)
        and exp_lower > 2
        and decode(log_data["log_two_lower_bound"]) == lower
        and decode(log_data["exp_7_over_10_degree_four_lower_bound"])
        == exp_lower
    )

    # Independent proof ledger. Convexity of x log x gives Jensen's lower
    # bound. Its superadditivity follows because
    # (a+b)log(a+b)-a log(a)-b log(b)
    # = a log(1+b/a)+b log(1+a/b)>0. For y>=1,
    # y log y>=y-1 follows by differentiating y log y-y+1.
    q = 8
    log_q_upper = 3 * Fraction(7, 10)
    negative_defect = Fraction(q * q, 4) * log_q_upper
    total_defect = q * q + negative_defect
    checks["scalar_proof_constants_rederived"] = (
        log_q_upper == Fraction(21, 10)
        and negative_defect == Fraction(168, 5)
        and total_defect == Fraction(488, 5)
        and theorem.get("general_bound")
        == "D>=2A-N*q^2*(1+log(q)/4)"
        and theorem.get("q8_rational_bound") == "D>=2A-(488/5)*N"
    )

    fixtures = theorem.get("scalar_regime_fixtures", [])
    fixture_ok = len(fixtures) == 3
    if fixture_ok:
        rebuilt = [reconstruct_fixture(row) for row in fixtures]
        fixture_ok = all(
            data["sum"] == decode(row["sum_s"])
            and data["residual"] == decode(row["residual_r"])
            and data["coefficient"] == decode(row["t_log_two_coefficient"])
            and data["product_coefficient"]
            == decode(row["r_times_t_log_two_coefficient"])
            for data, row in zip(rebuilt, fixtures)
        )
        fixture_ok = fixture_ok and [data["residual"] > 0 for data in rebuilt] == [
            True,
            False,
            False,
        ]
    checks["three_scalar_regimes_reconstructed"] = fixture_ok

    gibbs = certificate.get("actual_gibbs_action_density", {})
    coupling = decode(gibbs.get("lambda", {"numerator": 0, "denominator": 1}))
    action_bound = total_defect / 2 + coupling * coupling / 2
    checks["gibbs_dimension_and_action_bound_rederived"] = (
        coupling == Fraction(2, 5)
        and "N-1" in gibbs.get("radial_integration_by_parts", "")
        and action_bound == Fraction(1222, 25)
        and decode(gibbs["lambda_point_four_uniform_action_density_bound"])
        == action_bound
        and gibbs.get("half_weight_squarefree_radicand") == 1247
        and gibbs.get("half_weight_rational_denominator") == 5
    )

    bilap = certificate.get("actual_bilaplacian_consequence", {})
    bilap_second = 16 * q * q * action_bound
    phi_first_prefactor = Fraction(4 * q, 1) / (coupling * coupling * 5)
    checks["bilaplacian_consequence_rederived"] = (
        bilap_second == Fraction(1251328, 25)
        and decode(bilap["second_moment_density_bound_rational"])
        == bilap_second
        and phi_first_prefactor == 40
        and bilap.get("status") == "PROVED_BUT_INSUFFICIENT_FOR_H_MINUS_ONE"
    )

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["input_hashes_match"] = len(inputs) == 2 and all(
        item.get("sha256") == file_hash(item.get("path", "")) for item in inputs
    )

    disposition = certificate.get("method_disposition", {})
    checks["claim_boundary_is_fail_closed"] = (
        disposition.get("actual_uniform_action_density_moment") == "PROVED"
        and disposition.get("actual_annealed_half_action_density_factor")
        == "PROVED"
        and disposition.get("global_orthogonal_hessian_block_positivity")
        == "OPEN"
        and disposition.get("actual_interacting_h_minus_one_second_moment_bound")
        == "OPEN"
        and disposition.get("interacting_tightness") == "NOT_ESTABLISHED"
        and disposition.get("continuum_limit") == "NOT_ESTABLISHED"
        and disposition.get("born_rule") == "NOT_ESTABLISHED"
        and disposition.get("krein_reconstruction") == "NOT_ASSESSED"
        and disposition.get("lorentzian_transfer") == "NOT_ESTABLISHED"
        and certificate.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]
    )

    checks["required_nonclaims_are_explicit"] = all(
        any(token in item for item in certificate.get("does_not_establish", []))
        for token in (
            "global convexity",
            "H^-1",
            "continuum",
            "Born",
            "Krein",
            "LORENTZIAN-CAUSAL",
        )
    )

    passed = sum(checks.values())
    if not all(checks.values()):
        if errors:
            for error in errors[:3]:
                print(f"[FAIL] schema: {error.message}")
        for name, ok in checks.items():
            if not ok:
                print(f"[FAIL] {name}")
        return False
    print(f"[PASS] independent BT affine virial verifier ({passed}/{len(checks)})")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
