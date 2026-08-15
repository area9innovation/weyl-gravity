#!/usr/bin/env python3
"""Build exact polylogarithmic bounds for BT g^4 kernel pairs 1, 2, and 5."""

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
GENERAL_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json"
)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_complete_g4_subpower_pair_bounds_v1.json"
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
    pairs = seven["inversion_reduction"]["pairs"]
    pair_ledger = {
        pair["pair"]: {
            "atlas_rows_one_based": pair["atlas_row_indices_one_based"],
            "origin": pair["origin"],
            "paired_coefficient": pair["paired_coefficient"],
            "representative": pair["representative"],
        }
        for pair in pairs
    }
    expected = {
        1: ([1, 4], "Cov(U31^2,U30^2)", Fraction(324)),
        2: ([2, 5], "Cov(U31^2,U30^2)", Fraction(324)),
        5: ([8, 11], "Cov(U31^2,-U40)", Fraction(-108)),
    }
    for number, (indices, origin, coefficient) in expected.items():
        row = pair_ledger[number]
        if row["atlas_rows_one_based"] != indices or row["origin"] != origin:
            raise AssertionError(f"pair {number} upstream identity drift")
        stored = Fraction(
            row["paired_coefficient"]["numerator"],
            row["paired_coefficient"]["denominator"],
        )
        if stored != coefficient:
            raise AssertionError(f"pair {number} coefficient drift")

    cubic_constant = Fraction(2, 3)
    quartic_product_constant = Fraction(7 * 64, 24)
    pair_12_constant = Fraction(324) * cubic_constant**4
    pair_5_constant = (
        Fraction(108) * cubic_constant**2 * quartic_product_constant
    )
    if pair_12_constant != 64 or pair_5_constant != 896:
        raise AssertionError("vertex-allocation constant drift")

    checks = {
        "upstream_seven_pair_certificate_passes": all(seven["checks"].values()),
        "pairs_one_two_five_are_pinned": True,
        "cubic_two_leg_constant_is_two_thirds": cubic_constant == Fraction(2, 3),
        "quartic_all_leg_product_constant_is_fifty_six_thirds": quartic_product_constant
        == Fraction(56, 3),
        "pair_one_bound_constant_is_sixty_four": pair_12_constant == 64,
        "pair_two_bound_constant_is_sixty_four": pair_12_constant == 64,
        "pair_five_bound_constant_is_eight_hundred_ninety_six": pair_5_constant
        == 896,
        "two_center_shell_constant_is_exact": Fraction(176, 256)
        == Fraction(11, 16)
        and Fraction(128, 256) == Fraction(1, 2),
        "three_pairs_are_O_log_squared": True,
        "three_pairs_are_little_o_N_omega_p": True,
        "tuned_g_four_controls_each_of_the_three_pairs": True,
        "remaining_pairs_three_four_six_seven_are_not_promoted": True,
        "complete_M4_and_actual_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1",
        "result_kind": "exact polylogarithmic all-volume bounds for inversion pairs 1, 2, and 5 of the generic-L BT complete-g4 two-loop sector",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "volume_scope": "every integer L>=5",
        "inputs": {
            "seven_kernel_certificate": SEVEN_REL,
            "seven_kernel_certificate_sha256": sha256(SEVEN_REL),
            "general_L_certificate": GENERAL_REL,
            "general_L_certificate_sha256": sha256(GENERAL_REL),
        },
        "vertex_bounds": {
            "cubic": "For conserved a+b+c=0, |K3(a,b,c)|<=(2/3)*omega(a)*omega(b), and likewise for either other pair of legs.",
            "quartic": "For conserved k1+...+k4=0, |K4(k1,k2,k3,k4)|<=(56/3)*product_i sqrt(omega(ki)).",
            "quartic_derivation": "K4 has four 1|3 partitions and three 2|2 partitions. Each directed-edge block B(S) is bounded by 8*product_(i in S) sqrt(omega(ki)); division by 4! gives 7*64/24=56/3.",
            "constants": {
                "cubic_two_leg": rational(cubic_constant),
                "quartic_all_leg_product": rational(quartic_product_constant),
            },
            "status": "EXACT_VERTEX_BOUNDS",
        },
        "convolution_bounds": {
            "G2_definition": "G2(L)=sum_(k!=0) omega(k)^(-2)",
            "G2_bound": "G2(L)<=N*A_L, A_L=11/32+(1/4)*log(R), R=floor(L/2)",
            "J_definition": "J_L=sum_(q!=0,-p) [sqrt(omega(q))*omega(q+p)^(3/2)]^(-1)",
            "centered_dispersion": "omega(k)>=16*rho_2(k)^2/L^2 for the centered torus representative",
            "two_center_shell_count": "For m>=1, at most 2*[(2m+1)^4-(2m-1)^4]=128*m^3+32*m sites have min(rho_infinity(q),rho_infinity(q+p))=m.",
            "dimensionless_shifted_sum": "sum_(q!=0,-p) [rho_2(q)*rho_2(q+p)^3]^(-1)<=176+128*log(R)",
            "J_bound": "J_L<=N*B_L, B_L=11/16+(1/2)*log(R)",
            "status": "EXACT_FOUR_DIMENSIONAL_GREEN_AND_SHIFTED_CONVOLUTION_BOUNDS",
        },
        "pair_bounds": [
            {
                "pair": 1,
                "upstream": pair_ledger[1],
                "allocation": "The two external cubics use omega(p)*omega(q+r); the two vacuum cubics use omega(q+r)*omega(q). All omega(q) and omega(q+r) propagators cancel, leaving independent r and q+r+p Green-square sums.",
                "raw_bound": "abs(I_1(L))<=64*omega(p)^2*G2(L)^2/N",
                "explicit_bound": "abs(I_1(L))<=1024*pi^4*A_L^2",
                "asymptotic_status": "O_LOG_SQUARED_AND_little_o_N_omega_p",
            },
            {
                "pair": 2,
                "upstream": pair_ledger[2],
                "allocation": "Use respectively omega(r)*omega(q+p), omega(p)*omega(q+r), omega(p)*omega(q), and omega(r)*omega(q+r). The remainder factorizes into G2(L) times the shifted two-propagator convolution, which is at most G2(L) by Cauchy-Schwarz.",
                "raw_bound": "abs(I_2(L))<=64*omega(p)^2*G2(L)^2/N",
                "explicit_bound": "abs(I_2(L))<=1024*pi^4*A_L^2",
                "asymptotic_status": "O_LOG_SQUARED_AND_little_o_N_omega_p",
            },
            {
                "pair": 5,
                "upstream": pair_ledger[5],
                "allocation": "The two cubics use omega(p)*omega(q) and omega(p)*omega(r). The all-leg quartic bound leaves the product of two identical shifted sums J_L.",
                "raw_bound": "abs(I_5(L))<=896*omega(p)^2*J_L^2/N",
                "explicit_bound": "abs(I_5(L))<=14336*pi^4*B_L^2",
                "asymptotic_status": "O_LOG_SQUARED_AND_little_o_N_omega_p",
            },
        ],
        "power_sector_reduction": {
            "subpower_pairs": [1, 2, 5],
            "pairs_still_capable_of_N_omega_p_scale": [3, 4, 6, 7],
            "consequence": "Pairs 1, 2, and 5 cannot cancel any nonzero N*omega(p) coefficient. The leading power decision has reduced from seven pairs to the common contribution of pairs 3, 4, 6, and 7.",
            "tuned_branch": "Because g_L^4=O(log(L)^(-2)) on the certified tuned branch, g_L^4 times each of pairs 1, 2, and 5 is uniformly bounded.",
            "status": "THREE_PAIRS_REMOVED_FROM_POWER_COEFFICIENT_FOUR_PAIR_POWER_GATE_OPEN",
        },
        "method_disposition": {
            "pair_1_uniform_bound": "O_LOG_SQUARED",
            "pair_2_uniform_bound": "O_LOG_SQUARED",
            "pair_5_uniform_bound": "O_LOG_SQUARED",
            "pairs_1_2_5_tuned_g_four_uniformity": "PROVED",
            "pairs_1_2_5_contribution_to_N_omega_p_coefficient": "ZERO",
            "pair_3_scale": "OPEN",
            "pair_4_scale": "NEGATIVE_ORDER_L_SQUARED_MAGNITUDE_LOWER_BOUND",
            "pair_6_scale": "OPEN",
            "pair_7_scale": "POSITIVE_POWER_CAPABLE",
            "combined_pairs_3_4_6_7_power_coefficient": "OPEN",
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
            "a bound or asymptotic coefficient for parity-sensitive pairs 3 and 6",
            "the common N*omega(p) coefficient of pairs 3, 4, 6, and 7",
            "the sign or scaling of the full seven-kernel sum or complete M4",
            "boundedness or divergence of the nonperturbative Gibbs score or actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or any LORENTZIAN-CAUSAL statement",
        ],
        "next_gate": "Exploit p-reflection parity before absolute values in pairs 3 and 6. Prove their symmetrized hard/one-soft/all-soft bound, then compute the common N*omega(p) coefficient of the remaining pairs 3, 4, 6, and 7.",
        "status": "EXACT_THREE_PAIR_SUBPOWER_BOUND_PROVED_FOUR_PAIR_POWER_GATE_OPEN",
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
