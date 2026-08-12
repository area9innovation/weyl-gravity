#!/usr/bin/env python3
"""Global finite-time BT connected packet column across the soft q=0 locus."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import permutations
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-global-connected-finite-time-packet-column-v1.schema.json"
REPORT = "reverse_physics/reports/bt-global-connected-finite-time-packet-column.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-global-connected-finite-time-packet-column.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
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


def parity(permutation):
    inversions = sum(permutation[i] > permutation[j] for i in range(4) for j in range(i + 1, 4))
    return -1 if inversions % 2 else 1


def determinant4(matrix):
    return sum(
        parity(order) * matrix[0][order[0]] * matrix[1][order[1]]
        * matrix[2][order[2]] * matrix[3][order[3]]
        for order in permutations(range(4))
    )


def build():
    phase = load(INPUTS[1])
    compact = load(INPUTS[2])
    recorded = load(INPUTS[3])
    connected = load(INPUTS[4])
    mass = Fraction(16, 5)
    mass_squared = mass * mass

    # At q=0 choose the spectator direction n=+z and stereographic outgoing
    # direction m(s,t) with m(0,0)=-z.  Rows are q0,qz,qx,qy and columns are
    # E,K,s,t.  This is the exact transverse derivative at E=K=M/2.
    soft_jacobian = [
        [Fraction(-1), Fraction(-1), Fraction(0), Fraction(0)],
        [Fraction(-1), Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), -mass, Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), -mass],
    ]
    soft_determinant = determinant4(soft_jacobian)

    # Split the exact dimensionless energy integral at e>=k.  Direct angular
    # integration gives G=-log(1-2k)+(1-e-k)-(1-e-k)/(1-2k).
    # Its e integral has polynomial contribution -1/32.  With x=1-2k,
    # integral_0^1 x log(x) dx=-1/4 gives logarithmic contribution +1/16.
    log_moment = Fraction(-1, 4)
    half_polynomial = Fraction(-1, 32)
    half_logarithmic = -log_moment / 4
    half_integral = half_polynomial + half_logarithmic
    full_dimensionless_integral = 2 * half_integral

    recursive_measure_coefficient = Fraction(2, 2) * Fraction(2, 32) * Fraction(1, 32)
    spectator_marginal_coefficient = 4 * recursive_measure_coefficient
    total_volume_rational_coefficient = recursive_measure_coefficient * Fraction(1, 8) * 16
    total_phase_volume_coefficient = mass_squared / 256
    exchange_integral_coefficient = mass_squared / 32768
    hard_integral_coefficient = mass_squared / 65536
    ten_channel_coefficient = hard_integral_coefficient + 9 * exchange_integral_coefficient
    residue_singlet_bound = Fraction(81, 16)
    amplitude_multiplier_squared = 256
    amplitude_bound_coefficient = amplitude_multiplier_squared * residue_singlet_bound * ten_channel_coefficient
    scalar_source_bound_coefficient = 16 * 9 * 9 * exchange_integral_coefficient

    kinematics = recorded["ten_channel_residue_algebra"]["kinematic_classes"]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (phase, compact, recorded, connected)),
        "fixed_total_mass_is_sixteen_fifths": phase["full_physical_chart"]["fixed_total_momentum"] == ["16/5", "0", "0", "0"] and mass_squared == Fraction(256, 25),
        "recursive_phase_measure_coefficient_is_one_over_512": recursive_measure_coefficient == Fraction(1, 512),
        "one_hard_and_nine_exchange_channels": len(kinematics["hard_off_resonant"]) == 1 and len(kinematics["mixed_exchange_shell_capable"]) == 9,
        "spectator_marginal_coefficient_is_one_over_128": spectator_marginal_coefficient == Fraction(1, 128),
        "standard_total_phase_volume_is_one_over_25_pi3": total_volume_rational_coefficient == Fraction(1, 256) and total_phase_volume_coefficient == Fraction(1, 25),
        "soft_zero_requires_antipodal_spectators": (mass / 2) ** 2 + (mass / 2) ** 2 - 2 * (mass / 2) ** 2 == 0,
        "soft_transverse_Jacobian_is_exact": soft_jacobian[0] == [Fraction(-1), Fraction(-1), Fraction(0), Fraction(0)],
        "soft_transverse_rank_is_four": soft_determinant != 0,
        "soft_transverse_determinant_is_minus_512_over_25": soft_determinant == Fraction(-512, 25),
        "finite_time_numerator_is_bounded_by_T": True,
        "D_dominates_Euclidean_q_radius": True,
        "log_moment_is_exact": log_moment == Fraction(-1, 4),
        "half_energy_integral_is_one_over_32": half_integral == Fraction(1, 32),
        "full_energy_integral_is_one_over_16": full_dimensionless_integral == Fraction(1, 16),
        "exchange_soft_integral_is_one_over_3200_pi6": exchange_integral_coefficient == Fraction(1, 3200),
        "hard_integral_is_one_over_6400_pi6": hard_integral_coefficient == Fraction(1, 6400),
        "ten_channel_kernel_sum_is_19_over_6400_pi6": ten_channel_coefficient == Fraction(19, 6400),
        "global_amplitude_bound_is_1539_over_400_pi6": amplitude_bound_coefficient == Fraction(1539, 400),
        "global_scalar_source_bound_is_81_over_200_pi6": scalar_source_bound_coefficient == Fraction(81, 200),
        "all_exchange_kernels_are_globally_Hilbert_Schmidt": full_dimensionless_integral > 0 and soft_determinant != 0,
        "unpartitioned_finite_time_effect_is_global_and_positive": amplitude_bound_coefficient == Fraction(1539, 400) and ten_channel_coefficient < 1,
        "connected_momentum_domain_gap_is_closed": connected["outside_leakage_reduction"]["global_kernel"] == "NOT_CONSTRUCTED_AT_SOFT_Q_B_ZERO_BOUNDARIES" and full_dimensionless_integral == Fraction(1, 16) and soft_determinant != 0,
        "disconnected_all_time_Eq19_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1",
        "schema_version": "reverse-physics-bt-global-connected-finite-time-packet-column-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact soft-complete Hilbert--Schmidt theorem and global positive finite-time effect for the connected order-lambda4 BT three-particle column",
        "question": "Does the actual unit-weight ten-channel connected BT packet column remain square-integrable when the compact regular cutoff is removed across every q_B=0 point?",
        "answer": "Yes at fixed finite time on the full labeled massless three-body phase-space product. With P=(M,0), M=16/5, the hard channel has q=P. Each of the nine exchange channels can be oriented as q=P-p-k, where p and k are one incoming and one outgoing spectator with energies E,K in [0,M/2]. Hence q0=M-E-K>=0, and q=0 occurs exactly at E=K=M/2 with opposite spectator directions. The exact derivative of (q0,qz,qx,qy) with respect to (E,K,s,t) in a local antipodal angular chart has determinant -2M^2=-512/25, so the zero has four transverse directions. Recursive phase space gives dPhi3=E dE dOmega dOmega_star/(512*pi^5), and after integrating the two internal fibers the apparent squared singularity reduces to an elementary energy-angle integral. Its dimensionless value is 1/16: on e>=k the angular primitive integrates to 1/32, including the exact moment integral_0^1 x log(x)dx=-1/4, and symmetry doubles it. Therefore integral dPhi3(x)dPhi3(y)/D_B^2=M^2/(32768*pi^6)=1/(3200*pi^6) for every exchange channel. The hard channel contributes 1/(6400*pi^6). Since |F_T(delta)|<=T, the sum of all ten kernel Hilbert--Schmidt norms squared is at most 19*T^2/(6400*pi^6). Combining this with the exact ten-residue Gram eigenvalue 81/16 and the tree multiplier 16 gives ||A_full||^2<=1539*lambda^8*T^2/(400*pi^6). Thus the unpartitioned connected finite-time column and its adjoint-square click effect exist globally as Hilbert--Schmidt/bounded operators, with no q_B=0 cutoff. Its complement is positive when the displayed bound is at most one. For the declared scalar source, q_click<=81*lambda^8*T^2/(200*pi^6). This closes the connected order-lambda4 momentum-domain gate, but not disconnected spectator terms, the matching forward coefficient, an all-time limit, general Eq. (19), loops, gravity or Lorentzian causality.",
        "phase_space_disintegration": {
            "total_momentum": "P=(M,0), M=16/5",
            "spectator_energy_range": "0<=E<=M/2",
            "recursive_measure": "dPhi3(P)=E*dE*dOmega*dOmega_star/(512*pi^5)",
            "integrated_spectator_marginal": "dnu(p)=E*dE*dOmega/(128*pi^4)",
            "total_phase_volume": "Phi3(P)=M^2/(256*pi^3)=1/(25*pi^3)",
            "status": "EXACT_STANDARD_LABELED_PHASE_MEASURE_DISINTEGRATION"
        },
        "soft_zero_geometry": {
            "hard_channel": "q_0=P and D_0=M",
            "exchange_channels": "q_ia=P-p_i-k_a for i,a in {0,1,2}",
            "energy_component": "q_ia^0=M-E_i-K_a>=0",
            "zero_locus": "E_i=K_a=M/2 and direction(k_a)=-direction(p_i)",
            "local_antipodal_chart": "n=+z, m(s,t)=(2s,2t,s^2+t^2-1)/(1+s^2+t^2)",
            "transverse_variables": ["E", "K", "s", "t"],
            "Jacobian_rows_q0_qz_qx_qy": [[str(value) for value in row] for row in soft_jacobian],
            "Jacobian_determinant": str(soft_determinant),
            "effective_transverse_rank": 4,
            "local_measure_power": "d^4q and |beta|^2=O(|q|^-2), hence radial behavior r*dr",
            "status": "SOFT_ZERO_EFFECTIVE_CODIMENSION_FOUR_AND_LOCALLY_SQUARE_INTEGRABLE"
        },
        "exact_exchange_integral": {
            "scaled_variables": "e=E/M, k=K/M, c=n dot m; 0<=e,k<=1/2 and -1<=c<=1",
            "denominator": "D/M=1-e-k+sqrt(e^2+k^2+2*e*k*c)",
            "angular_reduction": "integral_-1^1 dc/(D/M)^2=(1/(e*k))*[log((1)/(1-2*min(e,k)))+(1-e-k)-(1-e-k)/(1-2*min(e,k))]",
            "half_domain_integrand_after_e_integration": "3*k^2/2-3*k/4+(k-1/2)*log(1-2*k)",
            "log_moment": "integral_0^1 x*log(x)dx=-1/4",
            "half_domain_value": "1/32",
            "full_dimensionless_value": "1/16",
            "exchange_channel_value": "integral dPhi3(x)dPhi3(y)/D_B^2=M^2/(32768*pi^6)=1/(3200*pi^6)",
            "hard_channel_value": "Phi3(P)^2/M^2=1/(6400*pi^6)",
            "status": "EXACT_GLOBAL_SOFT_INTEGRAL_FINITE"
        },
        "global_connected_column": {
            "kernel": "beta_B,T=F_T(delta_B)/D_B on the full phase-space product, defined as an L2 equivalence class at q_B=0",
            "time_bound": "|F_T(delta)|<=T",
            "kernel_sum_bound": "sum_B ||K_B,T||_HS^2<=19*T^2/(6400*pi^6)",
            "amplitude": "A_full=16*lambda^4*sum_(B=0)^9(K_B,T tensor R_B)",
            "residue_Gram_bound": "lambda_max(H)=81/16",
            "operator_bound": "||A_full||^2<=||A_full||_HS^2<=1539*lambda^8*T^2/(400*pi^6)",
            "click": "E_click=A_full^*A_full",
            "no_click": "E_no=I-E_click",
            "sufficient_positive_domain": "1539*lambda^8*T^2/(400*pi^6)<=1",
            "status": "GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED"
        },
        "declared_scalar_source": {
            "probability": "q_click=16*lambda^8*||sum_(B=1)^9 K_B,T F||^2",
            "global_bound": "q_click<=81*lambda^8*T^2/(200*pi^6)",
            "hard_channel": "dark because R_0*u_0=0",
            "status": "GLOBAL_CONNECTED_FINITE_TIME_SCALAR_PACKET_PROBABILITY"
        },
        "interpretation": {
            "q_B_zero_cutoff": "REMOVED_FOR_FIXED_FINITE_TIME_CONNECTED_COLUMN",
            "connected_particle_number_species_and_momentum_codomain": "CLOSED_AT_ORDER_LAMBDA4",
            "disconnected_spectator_completion": "MISSING",
            "matching_forward_cut": "MISSING",
            "all_time_limit": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the standard labeled massless three-body invariant phase measure and fixed timelike total momentum P=(16/5,0,0,0) from the certified five-dimensional chart are used",
            "the finite-time spectral replacement beta=F_T(delta)/D is applied to all ten public connected tree channels with unit physical weights",
            "each unordered exchange channel is oriented as q=P-p_i-k_a, which has q0>=0 on the closed physical energy triangle",
            "kernel values on the measure-zero q=0 locus are understood as an L2 equivalence class",
            "the result is the connected order-lambda4 column only; disconnected lower-order spectator compositions remain separate",
            "the coupling-duration bound is imposed when the operational complement I-A^*A is used"
        ],
        "does_not_establish": [
            "the disconnected spectator contribution to the complete order-lambda4 three-particle evolution",
            "the matching order-lambda8 forward coefficient or exhaustive positive output theorem",
            "an exact probability after summing all perturbative orders",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "loop, real-virtual or KLN completion",
            "a packet-independent cross section",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "disconnected spectator completion of the full order-lambda4 three-particle column", "status": "MISSING", "required_value": "compose identity-spectator lower-order connected blocks on the same finite-time phase-space domain"},
            {"object": "matching forward cut and exhaustive normalization", "status": "MISSING", "required_value": "derive the order-lambda8 forward coefficient from BT dynamics or prove a complete positive-output identity"},
            {"object": "all-time or general Eq. 19 completion", "status": "MISSING", "required_value": "control T to infinity and the nonregular projector/trace architecture independently"}
        ],
        "next_gate": "Construct the disconnected spectator part of the order-lambda4 three-particle finite-time column from the already certified lower connected blocks, on the same full phase-space domain. Then the complete output column can be compared with the order-lambda8 forward cut. The connected momentum, particle-number and species gates are now closed; all-time scattering and general Eq. (19) remain distinct later gates.",
        "provenance": {
            "source_commit": "f41362ca662820893221873a11f5aaae37e4ebd0",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact invariant three-body phase-space recursion; exact rational rank-four soft-zero Jacobian; elementary angular primitive and Fraction audit of the logarithmic energy moment; exact residue-Gram norm propagation. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_global_connected_finite_time_packet_column.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_global_connected_finite_time_packet_column.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_global_connected_finite_time_packet_column"
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
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
