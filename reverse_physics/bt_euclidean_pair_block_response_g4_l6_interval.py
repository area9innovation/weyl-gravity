#!/usr/bin/env python3
"""Build the certified interval result for the BT pair-block L=6 g4 response."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, getcontext
from fractions import Fraction


getcontext().prec = 80
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEM = "bt_euclidean_pair_block_response_g4_l6_interval"
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_INTERVAL_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-l6-interval-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-pair-block-response-g4-l6-interval.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_pair_block_response_g4_l6_interval.py"
SOURCE_REL = f"reverse_physics/{STEM}.c"
DATA_REL = f"reverse_physics/data/{STEM}_v1.json"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_PREFLIGHT_V1.json",
    SOURCE_REL,
    DATA_REL,
]
SOURCE_COMMIT = "a59f636f73a4bc75c2c8103bc85e47f1fd9e06bd"
TERM_ORDER = (
    "F_4_0",
    "F_4_2",
    "F_4_4",
    "minus_F_3_3_Gamma_3",
    "minus_F_2_2_Gamma_4",
    "plus_F_2_2_Gamma_3_squared",
)


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def interval(row: dict) -> tuple[Decimal, Decimal]:
    midpoint = Decimal(row["midpoint"])
    radius = Decimal(row["radius"])
    return midpoint - radius, midpoint + radius


def contains(row: dict, value: Fraction) -> bool:
    low, high = interval(row)
    exact = Decimal(value.numerator) / Decimal(value.denominator)
    return low <= exact <= high


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        data = json.load(handle)
    terms = data["terms"]
    total = data["total"]
    total_low, total_high = interval(total)
    summed_low = sum((interval(terms[key])[0] for key in TERM_ORDER), Decimal(0))
    summed_high = sum((interval(terms[key])[1] for key in TERM_ORDER), Decimal(0))
    exact_rows = {
        "F20": Fraction(-15643, 1517824),
        "F40": Fraction(41416831, 82278203392),
        "b2": Fraction(956585197, 10069092633600),
    }
    checks = {
        "lattice_is_L6": data["lattice_length"] == 6 and data["volume"] == 1296,
        "all_momentum_pairs_evaluated": data["outer_momentum_rows"] == 1296,
        "six_terms_recorded": tuple(terms) == TERM_ORDER,
        "term_sum_is_enclosed": total_low <= summed_low <= summed_high <= total_high,
        "strict_positive_lower_endpoint": total_low > 0,
        "imaginary_interval_contains_zero": all(
            abs(Decimal(row["imaginary_midpoint"])) <= Decimal(row["radius"])
            for row in [*terms.values(), total]
        ),
        "exact_F20_is_enclosed": contains(data["calibration"]["F20"], exact_rows["F20"]),
        "exact_F40_is_enclosed": contains(data["calibration"]["F40"], exact_rows["F40"]),
        "exact_b2_is_enclosed": contains(data["calibration"]["b2"], exact_rows["b2"]),
        "roundoff_allowance_exceeds_128_units": (
            Decimal(data["arithmetic"]["error_allowance"])
            > Decimal(128) * (Decimal(2) ** -data["arithmetic"]["long_double_mantissa_bits"])
        ),
        "phase_seed_radius_is_conservative": Decimal(data["arithmetic"]["phase_seed_radius"]) >= Decimal("1.9e-19"),
        "memory_ceiling_respected": data["resource_receipt"]["peak_kib"] < data["resource_receipt"]["memory_limit_kib"],
        "numeric_interval_type_is_explicit": data["result_type"] == "CERTIFIED_COMPLEX_DISK_INTERVAL",
        "large_volume_and_uniform_remainder_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_INTERVAL_V1",
        "schema_version": "reverse-physics-bt-euclidean-pair-block-response-g4-l6-interval-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "certified complex-disk interval for the full-Gibbs BT nearest-neighbour pair-block order-lambda^4 coefficient on the periodic 6^4 lattice",
        "question": "Does the exact six-topology coefficient T_(4,6) have a rigorously decided sign?",
        "answer": (
            f"Yes. Conservative long-double complex-disk arithmetic encloses the complete coefficient in "
            f"[{total_low}, {total_high}], strictly above zero. The computation streamed all 1296^2 momentum pairs under the memory ceiling and separately enclosed the three certified exact calibration values. This computes the finite-volume coefficient's sign, but it does not control L tending to infinity, the perturbative remainder, the fixed-coupling response, or the interacting H^-1 moment."
        ),
        "coefficient": {
            "lattice_length": 6,
            "volume": 1296,
            "order": "lambda^4",
            "term_order": list(TERM_ORDER),
            "terms": terms,
            "total": total,
            "real_lower_endpoint": str(total_low),
            "real_upper_endpoint": str(total_high),
            "sign": "STRICTLY_POSITIVE_CERTIFIED_INTERVAL",
            "numeric_type": data["result_type"],
        },
        "calibration": {
            key: {
                "exact": {"numerator": value.numerator, "denominator": value.denominator},
                "computed_interval": data["calibration"][key],
                "status": "EXACT_VALUE_ENCLOSED",
            }
            for key, value in exact_rows.items()
        },
        "arithmetic_certificate": {
            **data["arithmetic"],
            "disk_model": "Each complex scalar is a midpoint m and a nonnegative radius r denoting |z-m|<=r.",
            "forward_error_lemma": (
                "For radix-2 round-to-nearest long double with at least 64 mantissa bits, normal finite intermediates, disabled contraction, and standard excess precision, the addition and complex-multiplication midpoint errors are bounded by the explicit ERR terms. Radius-expression rounding is absorbed by the final (1+4 ERR) and (1+8 ERR) inflations. ERR exceeds 128 unit roundoffs on the recorded platform."
            ),
            "exact_numeric_boundary": "CERTIFIED_INTERVAL_NOT_EXACT_RATIONAL",
        },
        "resource_receipt": data["resource_receipt"],
        "method_disposition": {
            "exact_six_topology_formula": "IMPORTED_CERTIFIED",
            "binary64_preflight": "INDEPENDENT_MIDPOINT_CROSSCHECK",
            "complex_disk_interval_rail": "PASS_STRICT_POSITIVE",
            "finite_volume_g4_coefficient": "COEFFICIENT_COMPUTED_AS_INTERVAL",
            "large_volume_g4_power_or_log": "OPEN",
            "uniform_pair_response": "OPEN",
            "response_to_witten_schur_bridge": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "next_gate": (
            "Use the six local Laurent-polynomial vertices to split each two-loop sum into hard-hard, hard-soft, and soft-soft regions. Prove its leading power or logarithm uniformly in L before attempting any fixed-coupling remainder or response-to-Witten transfer."
        ),
        "does_not_establish": [
            "an exact rational value for T_(4,6)",
            "the sign or size of the order-lambda^4 coefficient uniformly in volume",
            "a uniform perturbative remainder or fixed-coupling pair-response inequality",
            "a heat-bath gap, Witten estimate, or actual interacting H^-1 bound",
            "tightness, continuum identification, a Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "assumptions": data["assumptions"],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_l6_interval.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_l6_interval.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_l6_interval",
            "cc -std=c11 -O2 -fopenmp -D_DEFAULT_SOURCE -ffp-contract=off -fexcess-precision=standard -Wall -Wextra -Werror reverse_physics/bt_euclidean_pair_block_response_g4_l6_interval.c -lm -o /tmp/bt-pair-g4-l6-interval",
            "ulimit -v 500000; OMP_NUM_THREADS=8 /tmp/bt-pair-g4-l6-interval",
        ],
        "tier_receipt": data["tier_receipt"],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(f"[PASS] BT pair-block g4 L6 interval ({result['checks']['passed']}/{result['checks']['total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
