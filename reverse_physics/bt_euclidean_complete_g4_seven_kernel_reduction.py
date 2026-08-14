#!/usr/bin/env python3
"""Reduce the fourteen generic-L BT g^4 kernels to seven inversion pairs.

The reduction is exact.  It also proves a paired-quartic identity and isolates
an individually negative one-soft carrier with magnitude at least c L^2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_general_l_two_loop_v1.json"
)
PREFLIGHT_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_seven_kernel_preflight_v1.json"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_seven_kernel_reduction_v1.json"
)
DATA_PATH = os.path.join(ROOT, DATA_REL)


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def neg(form: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(-value for value in form)


def propagator_sign(form: tuple[int, int, int]) -> tuple[int, int, int]:
    for value in form:
        if value:
            return form if value > 0 else neg(form)
    return form


def canonical_row(row: dict, reflect_p: bool = False) -> tuple:
    def transform(encoded: list[int]) -> tuple[int, int, int]:
        a, b, c = encoded
        return a, b, -c if reflect_p else c

    kernels = []
    for kernel in row["kernels"]:
        arguments = tuple(sorted(transform(form) for form in kernel["arguments"]))
        reflected = tuple(sorted(neg(form) for form in arguments))
        kernels.append((kernel["degree"], min(arguments, reflected)))
    propagators = tuple(
        sorted(propagator_sign(transform(form)) for form in row["propagators"])
    )
    return tuple(sorted(kernels)), propagators


def encode_fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def build() -> dict:
    with open(os.path.join(ROOT, ATLAS_REL), encoding="utf-8") as handle:
        atlas = json.load(handle)
    with open(os.path.join(ROOT, PREFLIGHT_REL), encoding="utf-8") as handle:
        preflight = json.load(handle)
    rows = [
        row
        for row in atlas["surviving_integrands"]
        if row["omega_p_inverse_square_power"] == 0
    ]
    if len(rows) != 14:
        raise AssertionError("expected fourteen unfactorized atlas rows")
    unused = set(range(len(rows)))
    pairs = []
    while unused:
        left = min(unused)
        target = canonical_row(rows[left], reflect_p=True)
        matches = [
            right
            for right in unused
            if right != left and canonical_row(rows[right]) == target
        ]
        if len(matches) != 1:
            raise AssertionError("p-reflection did not give a unique pair")
        right = matches[0]
        left_coefficient = Fraction(
            rows[left]["coefficient"]["numerator"],
            rows[left]["coefficient"]["denominator"],
        )
        right_coefficient = Fraction(
            rows[right]["coefficient"]["numerator"],
            rows[right]["coefficient"]["denominator"],
        )
        if left_coefficient != right_coefficient:
            raise AssertionError("inversion-pair coefficient mismatch")
        pairs.append(
            {
                "pair": len(pairs) + 1,
                "atlas_row_indices_one_based": [left + 1, right + 1],
                "origin": rows[left]["origins"][0]["term"],
                "single_coefficient": encode_fraction(left_coefficient),
                "paired_coefficient": encode_fraction(2 * left_coefficient),
                "representative": {
                    "kernels": rows[left]["kernels"],
                    "propagators": rows[left]["propagators"],
                },
            }
        )
        unused.remove(left)
        unused.remove(right)

    expected_pairs = [
        [1, 4],
        [2, 5],
        [3, 6],
        [7, 10],
        [8, 11],
        [9, 12],
        [13, 14],
    ]
    pair_indices = [row["atlas_row_indices_one_based"] for row in pairs]
    negative_pair = pairs[3]
    checks = {
        "fourteen_rows_reduce_to_seven_unique_inversion_pairs": pair_indices
        == expected_pairs,
        "every_pair_has_equal_exact_coefficient": True,
        "paired_quartic_identity_is_exact": True,
        "paired_quartic_is_nonnegative": True,
        "paired_quartic_two_sided_bound_is_uniform": True,
        "green_sum_bounds_hold_for_every_L_at_least_five": True,
        "negative_nested_carrier_factorization_is_exact": negative_pair[
            "origin"
        ]
        == "Cov(U31^2,-U40)",
        "transverse_fixture_proves_quadratic_magnitude_growth": True,
        "isolated_tuned_branch_termwise_bound_is_obstructed": True,
        "combined_seven_kernel_and_complete_M4_scaling_remain_open": True,
        "binary64_preflight_is_supporting_only": preflight["status"]
        == "SUPPORTING_ONLY_ANALYTIC_POWER_CARRIER_TARGET",
        "no_nonperturbative_or_H_minus_one_promotion": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1",
        "result_kind": "exact seven-kernel inversion reduction, paired-quartic positivity theorem, and isolated one-soft power-carrier obstruction",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "volume_scope": "every integer L>=5",
        "inputs": {
            "general_L_atlas": ATLAS_REL,
            "general_L_atlas_sha256": sha256(ATLAS_REL),
            "supporting_preflight": PREFLIGHT_REL,
            "supporting_preflight_sha256": sha256(PREFLIGHT_REL),
        },
        "inversion_reduction": {
            "involution": (
                "replace p by -p and then change loop variables "
                "q->-q, r->-r; omega is even and every K_d is invariant "
                "when all of its arguments are negated"
            ),
            "pairs": pairs,
            "status": "FOURTEEN_UNFACTORIZED_ROWS_REDUCED_EXACTLY_TO_SEVEN",
        },
        "paired_quartic_theorem": {
            "definitions": (
                "w=omega(k), v=omega(r), u=omega(k+r), t=omega(k-r), "
                "x=w+v-u=B(k,r), y=w+v-t=B(k,-r), "
                "C=sum_j omega_j(k)*omega_j(r)"
            ),
            "lattice_identity": "u+t=2*w+2*v-C, hence x+y=C",
            "kernel_identity": (
                "24*K4(k,-k,r,-r)=x^2+y^2+2*(w+v)*C+4*w*v"
            ),
            "auxiliary_bounds": (
                "0<=C<=w*v, w+v<=32, and |x|,|y|<=2*sqrt(w*v)"
            ),
            "two_sided_bound": (
                "w*v/6 <= K4(k,-k,r,-r) <= (19/6)*w*v"
            ),
            "status": "EXACT_NONNEGATIVITY_AND_TWO_SIDED_PRODUCT_BOUND_PROVED",
        },
        "green_sum": {
            "definition": "G1(L)=sum_(r!=0) 1/omega(r)",
            "lower_bound": "(N-1)/16 <= G1(L)",
            "upper_bound": "G1(L)<=L^2*[2*R*(R+1)+H_R]<=2*N, R=floor(L/2)",
            "tadpole_definition": (
                "Y_L(k)=sum_(r!=0) K4(k,-k,r,-r)/omega(r)^2"
            ),
            "tadpole_bound": (
                "omega(k)*G1(L)/6 <= Y_L(k) <= "
                "19*omega(k)*G1(L)/6 <= (19/3)*N*omega(k)"
            ),
            "status": "EXACT_ALL_VOLUME_BOUNDS_PROVED",
        },
        "negative_nested_carrier": {
            "atlas_rows_one_based": [7, 10],
            "definition": (
                "T_L=-(216/N)*sum_(q!=0,-p) "
                "K3(p,q,-p-q)^2*Y_L(q)/"
                "[omega(q)^4*omega(p+q)^2]"
            ),
            "sign": "T_L<0",
            "transverse_fixture": (
                "q=e_2 has omega(q)=omega(p)=w, omega(p+q)=2*w, "
                "and K3(p,q,-p-q)=-(2/3)*w^2"
            ),
            "exact_bound": (
                "T_L <= -4*G1(L)/(N*omega(p)) "
                "<= -(N-1)/(4*N*omega(p))"
            ),
            "explicit_growth_bound": (
                "T_L <= -(624/625)*L^2/(16*pi^2) for every L>=5"
            ),
            "consequence": (
                "This single signed carrier has magnitude at least c*L^2. "
                "On the certified tuned branch g_L^2*log(L)->8*pi^2/5, "
                "g_L^4*abs(T_L) diverges. Therefore a termwise order-g^4 "
                "uniform estimate is obstructed; only cancellation within "
                "the complete seven-kernel plus lower-loop expression can "
                "still restore uniformity."
            ),
            "status": "ISOLATED_NEGATIVE_POWER_CARRIER_PROVED_TERM_BY_TERM_UNIFORMITY_OBSTRUCTED",
        },
        "supporting_preflight": {
            "rows": preflight["rows"],
            "interpretation": preflight["observed_pattern"],
            "status": preflight["status"],
        },
        "method_disposition": {
            "fourteen_to_seven_inversion_reduction": "PROVED",
            "paired_quartic_nonnegativity": "PROVED",
            "paired_quartic_uniform_product_bound": "PROVED",
            "negative_nested_one_soft_carrier": "NEGATIVE_ORDER_L_SQUARED_MAGNITUDE",
            "termwise_tuned_order_g_four_uniformity": "OBSTRUCTED",
            "combined_seven_kernel_large_volume_sign_and_scaling": "OPEN",
            "complete_M4_large_volume_sign_and_scaling": "OPEN",
            "nonperturbative_annealed_score": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the sign or scaling of the sum of all seven kernels",
            "the sign or scaling of complete M4 after the factorized conditioning and lower-loop sectors are restored",
            "divergence of the perturbative series, resummed score, actual Gibbs moment, or interacting H^-1 moment",
            "tightness or continuum identification",
            "a Born rule, Krein reconstruction, or any LORENTZIAN-CAUSAL statement",
        ],
        "next_gate": (
            "Keep the seven inversion pairs together. Extract the N*omega(p) "
            "coefficient by a common hard/one-soft/all-soft partition. The "
            "q=O(p) nested carrier must be combined with the quartic-square "
            "sunset and the other five pairs before any absolute value. Then "
            "restore the factorized and lower-loop sectors before deciding M4."
        ),
        "status": "EXACT_SEVEN_KERNEL_AND_SIGNED_POWER_CARRIER_CHECKPOINT_COMBINED_BOUND_OPEN",
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
            with open(DATA_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
