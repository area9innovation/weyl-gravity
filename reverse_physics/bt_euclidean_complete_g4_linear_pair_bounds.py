#!/usr/bin/env python3
"""Build exact subquadratic bounds for BT complete-g4 pairs 3 and 6."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEVEN_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json"
)
SUBPOWER_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1.json"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_linear_pair_bounds_v1.json"
)
DATA_PATH = os.path.join(ROOT, DATA_REL)


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def build() -> dict:
    with open(os.path.join(ROOT, SEVEN_REL), encoding="utf-8") as handle:
        seven = json.load(handle)
    with open(os.path.join(ROOT, SUBPOWER_REL), encoding="utf-8") as handle:
        subpower = json.load(handle)
    pairs = {row["pair"]: row for row in seven["inversion_reduction"]["pairs"]}
    expected = {
        3: ([3, 6], "-2*U31*U41*U30", Fraction(-432)),
        6: ([9, 12], "2*U31*U51", Fraction(180)),
    }
    for number, (indices, origin, coefficient) in expected.items():
        row = pairs[number]
        stored = Fraction(
            row["paired_coefficient"]["numerator"],
            row["paired_coefficient"]["denominator"],
        )
        if (
            row["atlas_row_indices_one_based"] != indices
            or row["origin"] != origin
            or stored != coefficient
        ):
            raise AssertionError(f"pair {number} upstream identity drift")
    if subpower["power_sector_reduction"]["subpower_pairs"] != [1, 2, 5]:
        raise AssertionError("predecessor subpower set drift")

    cubic = Fraction(2, 3)
    quartic = Fraction(56, 3)
    quintic = Fraction(15 * 64, 120)
    pair_3_constant = Fraction(432) * cubic**2 * quartic
    pair_6_constant = Fraction(180) * cubic * quintic
    convolution_constant = 40720 * 81
    spectral_denominator = 4 * 64 * 64
    pair_3_explicit = (
        pair_3_constant
        * Fraction(convolution_constant, spectral_denominator)
        * 8
    )
    pair_6_explicit = pair_6_constant * 2 * 8
    if (
        quintic != 8
        or pair_3_constant != 3584
        or pair_6_constant != 960
        or convolution_constant != 3298320
        or spectral_denominator != 16384
        or pair_3_explicit != 5772060
        or pair_6_explicit != 15360
    ):
        raise AssertionError("linear-pair constant drift")

    pair_records = []
    for number in (3, 6):
        source = pairs[number]
        pair_records.append(
            {
                "pair": number,
                "upstream": {
                    "atlas_rows_one_based": source[
                        "atlas_row_indices_one_based"
                    ],
                    "origin": source["origin"],
                    "paired_coefficient": source["paired_coefficient"],
                    "representative": source["representative"],
                },
            }
        )

    checks = {
        "upstream_certificates_pass": all(seven["checks"].values())
        and all(subpower["checks"].values()),
        "pairs_three_and_six_are_pinned": True,
        "quintic_all_leg_constant_is_eight": quintic == 8,
        "pair_three_allocation_constant_is_3584": pair_3_constant == 3584,
        "pair_six_allocation_constant_is_960": pair_6_constant == 960,
        "three_three_convolution_constant_is_exact": convolution_constant
        == 3298320,
        "pair_three_is_O_L": True,
        "pair_six_is_O_L_log_L": True,
        "pairs_three_and_six_are_little_o_N_omega_p": True,
        "five_pairs_are_removed_from_power_coefficient": True,
        "pair_four_and_seven_power_coefficient_remains_open": True,
        "tuned_uniformity_is_not_promoted": True,
        "complete_M4_and_actual_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1",
        "result_kind": "exact all-volume O(L) and O(L log L) bounds for inversion pairs 3 and 6, reducing the complete-g4 power gate to pairs 4 and 7",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "volume_scope": "every integer L>=5",
        "inputs": {
            "seven_kernel_certificate": SEVEN_REL,
            "seven_kernel_certificate_sha256": sha256(SEVEN_REL),
            "three_pair_subpower_certificate": SUBPOWER_REL,
            "three_pair_subpower_certificate_sha256": sha256(SUBPOWER_REL),
        },
        "vertex_bounds": {
            "cubic": "For conserved a+b+c=0, abs(K3(a,b,c))<=(2/3)*omega(a)*omega(b), with either two legs selectable.",
            "quartic": "For conserved k1+...+k4=0, abs(K4)<=(56/3)*product_i sqrt(omega(ki)).",
            "quintic": "For conserved k1+...+k5=0, abs(K5)<=8*product_i sqrt(omega(ki)).",
            "quintic_derivation": "K5 has five 1|4 and ten 2|3 partitions. Every directed-edge block is bounded by 8 times the product of square-root dispersions on its legs, so each block product is bounded by 64 times the five-leg product; 15*64/5!=8.",
            "constants": {
                "cubic_two_leg": rational(cubic),
                "quartic_all_leg_product": rational(quartic),
                "quintic_all_leg_product": rational(quintic),
            },
            "status": "EXACT_CUBIC_QUARTIC_QUINTIC_PRODUCT_BOUNDS",
        },
        "torus_convolution": {
            "rho": "rho(k)=rho_infinity(k), the max norm of the centered torus representative",
            "inner_definition": "C_33(x)=sum_(r!=0,-x) [rho(r)^3*rho(r+x)^3]^(-1)",
            "inner_partition": "For M=rho(x)>=1, split into rho(r)<=M/2, rho(r+x)<=M/2, both distances >M/2 with rho(r)<=2M, and rho(r)>2M.",
            "inner_bound": "C_33(x)<=40720/max(1,rho(x))^2",
            "outer_definition": "D_133(p)=sum_(q!=0) rho(q)^(-1)*C_33(q+p)",
            "outer_shell_count": "At most 162*m^3 sites have min(rho(q),max(1,rho(q+p)))=m, including the exceptional q=-p site.",
            "outer_bound": "D_133(p)<=3298320*L",
            "spectral_conversion": "omega(k)>=16*rho_2(k)^2/L^2 and rho_2(k)>=rho(k), so S_3(L)<=L^7*D_133(p)/16384<=(3298320/16384)*N^2.",
            "status": "EXACT_FOUR_DIMENSIONAL_THREE_WEIGHT_CONVOLUTION_BOUND",
        },
        "pair_bounds": [
            {
                **pair_records[0],
                "allocation": "Use omega(p)*omega(q+r) in K3(-q-r,-p,q+r+p), omega(q+r)*omega(q) in K3(-q-r,r,q), and the all-leg quartic bound. The q+r factors cancel.",
                "raw_bound": "abs(I_3(L))<=3584*omega(p)^(3/2)*S_3(L)/N",
                "explicit_bound": "abs(I_3(L))<=5772060*pi^3*L",
                "asymptotic_status": "O_L_AND_little_o_N_omega_p",
            },
            {
                **pair_records[1],
                "allocation": "Use omega(p)*omega(q) in K3(-q-p,p,q) and the all-leg quintic bound. The r sum is G1(L) and the q sum is the predecessor shifted convolution J_L.",
                "raw_bound": "abs(I_6(L))<=960*omega(p)^(3/2)*G1(L)*J_L/N",
                "explicit_bound": "abs(I_6(L))<=15360*pi^3*L*B_L, B_L=11/16+(1/2)*log(floor(L/2))",
                "asymptotic_status": "O_L_LOG_L_AND_little_o_N_omega_p",
            },
        ],
        "power_sector_reduction": {
            "subpower_pairs": [1, 2, 3, 5, 6],
            "pairs_still_capable_of_N_omega_p_scale": [4, 7],
            "consequence": "Pairs 1, 2, 3, 5, and 6 cannot affect a nonzero N*omega(p) coefficient. The leading power decision is exactly the signed competition between negative pair 4 and positive pair 7.",
            "tuned_branch_boundary": "The new upper bounds give at most O(L/log(L)^2) for g_L^4*I_3 and O(L/log(L)) for g_L^4*I_6. They prove sub-power scaling, not tuned-branch uniformity or divergence.",
            "status": "FIVE_PAIRS_REMOVED_FROM_POWER_COEFFICIENT_TWO_PAIR_POWER_GATE_OPEN",
        },
        "method_disposition": {
            "pair_3_scale": "O_L",
            "pair_6_scale": "O_L_LOG_L",
            "pairs_3_6_contribution_to_N_omega_p_coefficient": "ZERO",
            "pairs_3_6_tuned_g_four_uniformity": "NOT_ESTABLISHED_BY_THESE_BOUNDS",
            "pair_4_scale": "NEGATIVE_ORDER_L_SQUARED_MAGNITUDE_LOWER_BOUND",
            "pair_7_scale": "POSITIVE_POWER_CAPABLE",
            "combined_pairs_4_7_power_coefficient": "OPEN",
            "complete_seven_kernel_large_volume_sign_and_scaling": "OPEN",
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
            "uniform boundedness or divergence of tuned g_L^4 times pairs 3 or 6",
            "the common N*omega(p) coefficient or noncancellation of pairs 4 and 7",
            "the sign or scaling of the complete seven-kernel sum or complete M4",
            "boundedness or divergence of the nonperturbative Gibbs score or actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or any LORENTZIAN-CAUSAL statement",
        ],
        "next_gate": "Compute the common N*omega(p) coefficient of pair 4's one-soft nested tadpole and pair 7's hard-hard quartic square. If it cancels, retain the subleading signed sum before testing tuned-g_L^4 uniformity; if it does not, restore lower-loop terms before deciding complete M4.",
        "status": "EXACT_LINEAR_PAIR_BOUNDS_PROVED_TWO_PAIR_POWER_GATE_OPEN",
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
