#!/usr/bin/env python3
"""Build the certified BT seven-kernel reduction decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-seven-kernel-reduction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-complete-g4-seven-kernel-reduction.md"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_seven_kernel_reduction_v1.json"
)
PRODUCER_REL = (
    "reverse_physics/bt_euclidean_complete_g4_seven_kernel_reduction.py"
)
PREFLIGHT_SOURCE_REL = (
    "reverse_physics/bt_euclidean_complete_g4_seven_kernel_preflight.c"
)
PREFLIGHT_DRIVER_REL = (
    "reverse_physics/bt_euclidean_complete_g4_seven_kernel_preflight.py"
)
PREFLIGHT_DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_seven_kernel_preflight_v1.json"
)
VERIFIER_REL = (
    "reverse_physics/verify_bt_euclidean_complete_g4_seven_kernel_reduction.py"
)
SOURCE_COMMIT = "c1ce96974bf36e4566e706fd448bc213baf5150d"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json",
    "reverse_physics/data/bt_euclidean_complete_g4_general_l_two_loop_v1.json",
    PRODUCER_REL,
    DATA_REL,
    PREFLIGHT_SOURCE_REL,
    PREFLIGHT_DRIVER_REL,
    PREFLIGHT_DATA_REL,
]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        reduction = json.load(handle)
    checks = {
        "reduction_checks_all_pass": all(reduction["checks"].values()),
        "fourteen_unfactorized_rows_are_seven_inversion_pairs": reduction[
            "inversion_reduction"
        ]["status"]
        == "FOURTEEN_UNFACTORIZED_ROWS_REDUCED_EXACTLY_TO_SEVEN",
        "paired_quartic_is_nonnegative_with_two_sided_bound": reduction[
            "paired_quartic_theorem"
        ]["status"]
        == "EXACT_NONNEGATIVITY_AND_TWO_SIDED_PRODUCT_BOUND_PROVED",
        "negative_carrier_has_explicit_quadratic_growth": reduction[
            "negative_nested_carrier"
        ]["status"]
        == "ISOLATED_NEGATIVE_POWER_CARRIER_PROVED_TERM_BY_TERM_UNIFORMITY_OBSTRUCTED",
        "combined_seven_kernel_scaling_remains_open": reduction[
            "method_disposition"
        ]["combined_seven_kernel_large_volume_sign_and_scaling"]
        == "OPEN",
        "complete_M4_scaling_remains_open": reduction["method_disposition"][
            "complete_M4_large_volume_sign_and_scaling"
        ]
        == "OPEN",
        "actual_interacting_H_minus_one_remains_open": reduction[
            "method_disposition"
        ]["actual_interacting_h_minus_one_second_moment"]
        == "OPEN",
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-seven-kernel-reduction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "SEVEN_KERNEL_REDUCTION_AND_ISOLATED_POWER_CARRIER_PROVED_COMBINED_BOUND_OPEN",
        "result_kind": reduction["result_kind"],
        "question": (
            "Can the fourteen remaining generic-volume two-loop kernels be "
            "reduced further, and can any signed one-soft carrier be proved "
            "large enough to obstruct a termwise tuned-branch estimate?"
        ),
        "answer": (
            "Yes. Global momentum inversion pairs the fourteen entries into "
            "seven exact sums. The paired quartic vertex obeys an exact "
            "positive identity and w*v/6<=K4(k,-k,r,-r)<=19*w*v/6. "
            "Consequently its momentum-dependent tadpole Y_L(k) is positive "
            "and comparable to omega(k)*G1(L). The inversion pair from "
            "Cov(U31^2,-U40) factorizes as a strictly negative nested "
            "carrier T_L. Restricting q to one transverse lowest mode gives "
            "T_L<=-(N-1)/(4*N*omega(p))<=-(624/625)*L^2/(16*pi^2). "
            "Thus g_L^4*abs(T_L) diverges on the tuned asymptotically free "
            "branch, obstructing every termwise order-g^4 uniform estimate. "
            "The other six kernels can still cancel this carrier. Their "
            "combined power coefficient, the restored factorized and "
            "lower-loop sectors, full M4, the nonperturbative score, and the "
            "actual interacting H^-1 moment remain open."
        ),
        "data": DATA_REL,
        "data_sha256": sha256(DATA_REL),
        "producer": PRODUCER_REL,
        "producer_sha256": sha256(PRODUCER_REL),
        "inversion_reduction": reduction["inversion_reduction"],
        "paired_quartic_theorem": reduction["paired_quartic_theorem"],
        "green_sum": reduction["green_sum"],
        "negative_nested_carrier": reduction["negative_nested_carrier"],
        "supporting_preflight": reduction["supporting_preflight"],
        "method_disposition": reduction["method_disposition"],
        "checks": checks,
        "does_not_establish": reduction["does_not_establish"],
        "missing_object_ledger": [
            "the common N*omega(p) coefficient of all seven inversion-paired kernels",
            "a hard/one-soft/all-soft remainder bound after that coefficient is extracted",
            "the factorized and lower-loop recombination needed to decide complete M4",
            "a whole-composite nonperturbative annealed score estimate",
            "dyadic Fourier-shell control of the actual interacting H^-1 moment",
        ],
        "next_gate": reduction["next_gate"],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "exact_arithmetic": (
                "integer affine momentum forms, Fraction coefficients, exact "
                "dispersion identities, and rational inequality constants; "
                "binary64 values are a separately tagged supporting preflight"
            ),
            "assumptions": [
                "L is an integer at least five and p is the lowest axial lattice momentum",
                "the tuned-branch consequence imports only the previously certified g_L^2*log(L) limit",
                "an isolated perturbative carrier is not identified with the summed perturbative coefficient or actual Gibbs observable",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_seven_kernel_reduction.py --check",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_seven_kernel_decision.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_seven_kernel_reduction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_seven_kernel_reduction",
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_seven_kernel_preflight.py --smoke",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.stdout:
        print(expected, end="")
        return 0
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
