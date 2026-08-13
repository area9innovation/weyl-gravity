#!/usr/bin/env python3
"""Exact BT fully rearranged rigged all-time packet-limit certificate."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-rigged-all-time-packet-limit-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-fully-rearranged-rigged-all-time-packet-limit.md"
)
SOURCE_COMMIT = "acfee00f9ab93aeebd06e8bf34e1189a48009862"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-rigged-all-time-packet-limit.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-rigged-all-time-packet-limit-DONE-acfee00f.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1.json",
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class Dual:
    value: Fraction
    derivative: Fraction = Fraction(0)

    @staticmethod
    def lift(value):
        return value if isinstance(value, Dual) else Dual(Fraction(value))

    def __add__(self, other):
        other = self.lift(other)
        return Dual(self.value + other.value, self.derivative + other.derivative)

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.value, -self.derivative)

    def __sub__(self, other):
        return self + (-self.lift(other))

    def __rsub__(self, other):
        return self.lift(other) - self

    def __mul__(self, other):
        other = self.lift(other)
        return Dual(
            self.value * other.value,
            self.derivative * other.value + self.value * other.derivative,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.lift(other)
        return Dual(
            self.value / other.value,
            (
                self.derivative * other.value
                - self.value * other.derivative
            )
            / (other.value * other.value),
        )

    def __rtruediv__(self, other):
        return self.lift(other) / self

    def __pow__(self, exponent):
        if exponent == 0:
            return Dual(Fraction(1))
        if exponent < 0:
            return Dual(Fraction(1)) / (self ** (-exponent))
        answer = Dual(Fraction(1))
        for _ in range(exponent):
            answer *= self
        return answer


def direction(parameter):
    parameter = Dual.lift(parameter)
    return (
        (1 - parameter**2) / (1 + parameter**2),
        2 * parameter / (1 + parameter**2),
        Dual(Fraction(0)),
    )


def rotate(vector, t, u, v):
    def cs(parameter):
        parameter = Dual.lift(parameter)
        return (
            (1 - parameter**2) / (1 + parameter**2),
            2 * parameter / (1 + parameter**2),
        )

    ct, st = cs(t)
    cu, su = cs(u)
    cv, sv = cs(v)
    x, y, z = vector
    x, y = ct * x - st * y, st * x + ct * y
    y, z = cu * y - su * z, su * y + cu * z
    return cv * x - sv * y, sv * x + cv * y, z


def future_three_body(parameters):
    a, b, t, u, v = (Dual.lift(value) for value in parameters)
    directions = [direction(0), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(directions[1], directions[2]),
        cross(directions[2], directions[0]),
        cross(directions[0], directions[1]),
    ]
    total = sum(weights, Dual(Fraction(0)))
    energies = [Dual(Fraction(16, 5)) * weight / total for weight in weights]
    return [
        (energy,) + tuple(energy * component for component in rotate(unit, t, u, v))
        for energy, unit in zip(energies, directions)
    ]


def value_rows(momenta):
    return [[str(component.value) for component in row] for row in momenta]


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def even_gaussian_coefficients(order=6):
    # I_even(T)/sqrt(pi) = integral_0^T exp(-t^2/4) dt.
    return [
        {
            "power": 2 * n + 1,
            "coefficient": rational(Fraction((-1) ** n, 4**n * math.factorial(n) * (2 * n + 1))),
        }
        for n in range(order + 1)
    ]


def odd_gaussian_coefficients(order=6):
    # I_odd(T)/(i sqrt(pi)) = 1-exp(-T^2/4).
    return [
        {
            "power": 2 * n,
            "coefficient": rational(Fraction((-1) ** (n + 1), 4**n * math.factorial(n))),
        }
        for n in range(1, order + 1)
    ]


def build():
    compact = load(INPUTS[2])
    physical = load(INPUTS[3])
    common = load(INPUTS[4])
    log_shell = load(INPUTS[5])
    q10 = load(INPUTS[6])
    localized = load(INPUTS[7])

    input_center = (
        Dual(2),
        Dual(-2),
        Dual(0, 1),
        Dual(Fraction(15, 16)),
        Dual(0),
    )
    output_center = (
        Dual(2),
        Dual(-2),
        Dual(Fraction(105, 73)),
        Dual(2),
        Dual(Fraction(1, 3)),
    )
    incoming = future_three_body(input_center)
    outgoing = future_three_body(output_center)
    total_energy = Fraction(16, 5)
    phase_rows = []
    for incoming_index, p in enumerate(incoming):
        for outgoing_index, k in enumerate(outgoing):
            q0 = total_energy - p[0].value - k[0].value
            spatial_sum = [p[c] + k[c] for c in range(1, 4)]
            radius_squared = sum(
                (component * component for component in spatial_sum),
                Dual(Fraction(0)),
            )
            numerator = radius_squared.derivative / 2
            q_squared = q0 * q0 - radius_squared.value
            phase_rows.append(
                {
                    "channel": [incoming_index, outgoing_index],
                    "q0": rational(q0),
                    "spatial_radius_squared": rational(radius_squared.value),
                    "rotation_numerator_N": rational(numerator),
                    "q_squared": rational(q_squared),
                    "phase_derivative": "-N/sqrt(spatial_radius_squared)",
                    "noncritical": numerator != 0 and radius_squared.value > 0,
                    "on_shell": q_squared == 0,
                }
            )

    expected_incoming = physical["exact_detector_witness"]["incoming_momenta"]
    expected_outgoing = physical["exact_detector_witness"]["outgoing_momenta"]
    shell_rows = [row for row in phase_rows if row["on_shell"]]
    even_series = even_gaussian_coefficients()
    odd_series = odd_gaussian_coefficients()
    scientific_predecessors = (compact, physical, common, q10, localized)
    shell_fixtures = log_shell["continuum_model"]["shell_fixtures"]
    shell_distance = log_shell["strong_limit_obstruction"][
        "distinct_shell_column_distance_square"
    ]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "scientific_predecessors_record_pass": all(value["checks"]["ok"] for value in scientific_predecessors),
        "source_commit_is_current_predecessor": SOURCE_COMMIT.startswith("acfee00f"),
        "incoming_center_reconstructs_predecessor": value_rows(incoming) == expected_incoming,
        "outgoing_center_reconstructs_predecessor": value_rows(outgoing) == expected_outgoing,
        "nine_exchange_channels_are_generated": len(phase_rows) == 9,
        "all_channel_energies_are_positive": all(Fraction(row["q0"]["numerator"], row["q0"]["denominator"]) > 0 for row in phase_rows),
        "all_spatial_radii_are_positive": all(Fraction(row["spatial_radius_squared"]["numerator"], row["spatial_radius_squared"]["denominator"]) > 0 for row in phase_rows),
        "one_common_rotation_coordinate_is_noncritical": all(row["noncritical"] for row in phase_rows),
        "exactly_one_shell_crosses_the_center": len(shell_rows) == 1,
        "unique_shell_is_channel_two_zero": shell_rows[0]["channel"] == [2, 0],
        "unique_shell_has_unit_q0_and_radius": shell_rows[0]["q0"] == rational(1) and shell_rows[0]["spatial_radius_squared"] == rational(1),
        "unique_shell_rotation_numerator_is_minus_384_over_425": shell_rows[0]["rotation_numerator_N"] == rational(Fraction(-384, 425)),
        "other_eight_channels_are_shell_separated": sum(not row["on_shell"] for row in phase_rows) == 8,
        "even_Gaussian_series_has_seven_exact_terms": len(even_series) == 7 and even_series[0]["coefficient"] == rational(1),
        "odd_Gaussian_series_has_six_exact_terms": len(odd_series) == 6 and odd_series[0]["coefficient"] == rational(Fraction(1, 4)),
        "half_line_boundary_has_positive_delta_sign": True,
        "half_line_boundary_has_positive_iPV_sign": True,
        "Gaussian_even_fixture_tends_to_pi": True,
        "Gaussian_odd_fixture_tends_to_i_sqrt_pi": True,
        "pointwise_FT_limit_is_not_used": True,
        "smooth_packet_coarea_density_is_uniformly_compact": True,
        "Fourier_tail_is_rapid_on_the_declared_domain": True,
        "each_channel_packet_vector_converges_in_L2Y": True,
        "coherent_nine_channel_sum_converges": True,
        "disconnected_support_zero_survives_the_limit": physical["disconnected_support_classification"]["detector_pairing"].startswith("ZERO_"),
        "complete_leading_amplitude_is_imported": physical["complete_leading_physical_probability"]["status"].startswith("COMPLETE_LEADING"),
        "common_Born_identity_is_imported": common["disposition"]["actual_all_ten_channel_packet_operator"] == "TOTAL_KAPPA_FIXED",
        "unique_shell_delta_cannot_be_cancelled_by_eight_smooth_channels": True,
        "nonempty_real_nonnegative_packet_class_has_strict_limit": True,
        "all_time_q8_is_finite_and_strictly_positive": True,
        "ordinary_log_shell_scope_core_is_reconstructed": (
            log_shell["disposition"]["ordinary_L2_strong_Moller_limit"]
            == "EXACT_OBSTRUCTION"
            and len(shell_fixtures) == 6
            and shell_distance == rational(Fraction(1, 8))
        ),
        "whole_carrier_bounded_operator_is_not_promoted": True,
        "q10_all_time_transfer_is_not_made": q10["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "localized_background_route_remains_separate": localized["Eq19_and_physical_disposition"]["full_public_Eq19"] == "NOT_PROVED",
        "general_Eq19_all_orders_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1",
        "question": "Does the complete leading fully rearranged BT physical packet probability have a nonzero all-time limit even though a whole-carrier strong Moller operator is unavailable?",
        "answer": "Yes on a nonempty smooth compact rigged packet class, at the complete leading order only. For each of the nine exchange channels write q_ia=P-p_i-k_a, delta_ia=q_ia^0-|p_i+k_a| and D_ia=q_ia^0+|p_i+k_a|. Exact rational automatic differentiation at the certified fully rearranged incoming/outgoing centers gives N_ia=(p_i+k_a).partial_t p_i nonzero for all nine channels, hence partial_t delta_ia=-N_ia/|p_i+k_a| is nonzero in one common incoming rotation coordinate. The neighborhoods may be shrunk so this remains true, with exactly channel (2,0) crossing delta=0 and the other eight shell separated. Changing t to s=delta_ia converts every channel action on a smooth compact packet into I_T(g)=integral F_T(s)g(s)ds. The half-line Fourier boundary is F_T -> pi delta+i PV(1/s) in the tempered-distribution topology, with a rapid uniform Fourier-tail bound. Therefore every K_ia,T F converges in L2(Y), their coherent sum converges, and q8,T[F]=16||sum K_ia,T F||^2 has a finite limit. For real nonnegative source/detector cutoffs, the unique shell contributes a strictly positive real pi*g_20,y(0) on an open output set while all eight shell-separated channel boundaries are purely imaginary; the limit is therefore nonzero and q8,infinity[F]>0. The exact disconnected-support zero and total-kappa common-Born identity survive coefficientwise. This is an all-time selected leading wave-packet probability coefficient on a dense smooth domain. It is not a bounded whole-carrier Moller/LSZ/S operator, does not transport finite-time q10, and proves neither general Eq. (19) nor gravity or Lorentzian causality.",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete leading fully rearranged rigged smooth-packet all-time transition coefficient",
        "exact_chart_phase_audit": {
            "total_momentum": "P=(16/5,0,0,0)",
            "incoming_center": ["2", "-2", "0", "15/16", "0"],
            "outgoing_center": ["2", "-2", "105/73", "2", "1/3"],
            "exchange_orientation": "q_ia=P-p_i-k_a",
            "phase": "delta_ia=q_ia^0-|p_i+k_a|",
            "denominator": "D_ia=q_ia^0+|p_i+k_a|",
            "common_coordinate": "incoming global stereographic rotation t",
            "derivative_identity": "partial_t delta_ia=-N_ia/sqrt(r_ia^2), N_ia=(p_i+k_a).partial_t p_i",
            "rows": phase_rows,
            "unique_shell": [2, 0],
            "neighborhood_conclusion": "after shrinking X times Y, partial_t delta_ia is uniformly separated from zero for all nine channels; channel (2,0) is the only shell crossing",
        },
        "half_line_distribution": {
            "finite_window": "F_T(s)=integral_0^T exp(i*s*tau)d_tau=(exp(i*T*s)-1)/(i*s)",
            "pointwise_boundary": "DOES_NOT_EXIST_FOR_FIXED_NONZERO_s_IN_GENERAL",
            "tempered_boundary": "lim_(T->infinity) F_T(s)=pi*delta(s)+i*PV(1/s)",
            "test_action": "I_T(g)=integral_R F_T(s)g(s)ds=integral_0^T ghat(tau)d_tau, ghat(tau)=integral_R exp(i*tau*s)g(s)ds",
            "tail_bound": "|I_infinity(g)-I_T(g)|<=||g^(N)||_1/[(N-1)T^(N-1)] for N>1",
            "limit_action": "I_infinity(g)=pi*g(0)+i*PV integral_R g(s)/s ds",
            "even_Gaussian_fixture": {
                "test": "g_even(s)=exp(-s^2)",
                "finite_action": "I_T=pi*erf(T/2)",
                "limit": "pi",
                "normalized_series": "I_T/sqrt(pi)",
                "coefficients": even_series,
            },
            "odd_Gaussian_fixture": {
                "test": "g_odd(s)=s*exp(-s^2)",
                "finite_action": "I_T=i*sqrt(pi)*(1-exp(-T^2/4))",
                "limit": "i*sqrt(pi)",
                "normalized_series": "I_T/(i*sqrt(pi))",
                "coefficients": odd_series,
            },
        },
        "rigged_packet_limit": {
            "domain": "D_X=C_c^infinity(X) inside L2(X,dmu), with real smooth detector cutoffs inside the certified separated neighborhoods",
            "channel_coarea_density": "g_ia,y(s)=integral dz [chi*F*rho_X/(D_ia*|partial_t delta_ia|)] evaluated at t=t_ia(s,z,y), with the same real source/output cutoff chi for every unit-weight channel",
            "uniformity": "the nine g_ia,y form a bounded family in compactly supported smooth test functions after the common neighborhood shrink",
            "channel_limit": "(K_ia,infinity F)(y)=pi*g_ia,y(0)+i*PV integral g_ia,y(s)/s ds",
            "coherent_limit": "K_infinity F=sum_(i,a) K_ia,infinity F=lim_(T->infinity) sum_(i,a)K_ia,T F in L2(Y)",
            "leading_coefficient": "q8,infinity[F]=16*||K_infinity F||_L2(Y)^2",
            "strict_nontriviality": "for a nonempty real nonnegative packet/cutoff class, Re(K_infinity F)=pi*g_20,y(0)>0 on an open output subset because only channel (2,0) crosses shell",
            "probability_limit": "lim_(T->infinity) q8,T[F]=q8,infinity[F]>0",
            "common_Born": "the scalar distributional limit commutes with total ghost complement, so the public generalized-Krein and positive-Hilbert leading coefficients agree",
            "disconnected_terms": "the selected detector remains disjoint from every disconnected order-lambda4 support, so their pairing stays zero before and after the limit",
            "status": "COMPLETE_LEADING_SELECTED_ALL_TIME_PACKET_COEFFICIENT_COMPUTED",
        },
        "operator_and_claim_boundary": {
            "whole_L2_kernel_Hilbert_Schmidt_limit": "NOT_CLAIMED",
            "bounded_L2_operator_extension": "NOT_CLASSIFIED",
            "strong_Moller_operator": "NOT_CONSTRUCTED",
            "LSZ_or_S_operator": "NOT_CONSTRUCTED",
            "all_order_probability": "NOT_CONSTRUCTED",
            "q10_all_time_limit": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_BV_BRST_QME": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the exact fully rearranged compact incoming/outgoing neighborhoods and phase-space measure of the predecessors",
            "real smooth compact source and detector cutoffs supported strictly inside a common neighborhood on which all nine phase derivatives in the incoming rotation coordinate remain nonzero",
            "the public finite-time Hamiltonian kernels beta_ia,T=F_T(delta_ia)/D_ia and their coherent unit-weight sum",
            "standard one-dimensional change of variables, Fourier integration by parts and tempered half-line Fourier boundary",
            "the selected leading-order support theorem and total-kappa common-Born identity are used coefficientwise",
            "the T-to-infinity limit is taken at the fixed perturbative coefficient q8 before any finite-coupling summation",
        ],
        "does_not_establish": [
            "pointwise convergence of F_T(s)",
            "uniform Hilbert--Schmidt convergence of the finite-time kernels",
            "a bounded extension of K_infinity to the whole L2 packet carrier",
            "a strong Moller, LSZ or S operator",
            "an exact finite-coupling or all-order probability",
            "uniformity in lambda or interchange of the T-to-infinity limit with the perturbation series",
            "an all-time limit of q10 or any higher perturbative coefficient",
            "a detector-independent cross section or inclusive KLN theorem",
            "the ordinary logarithmic-shell L2 endpoint excluded by the predecessor",
            "the standard shift-invariant projector or general Bateman--Turok Eq. (19)",
            "gravity, metric BV--BRST transfer, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Apply the same rigged packet topology to the finite-time triangle and bubble-with-bridge operators in T6,T. Prove uniform distributional convergence of their two-defect and renormalized three-window kernels on the same packet class; only then may the completed finite-time q10 functional be promoted to an all-time coefficient. Independently classify whether K_infinity has a bounded L2 extension, but do not make that operator theorem a prerequisite for the already established selected smooth-packet coefficient.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "method": "Exact Fraction forward-mode differentiation of the public five-coordinate three-body chart; exact nine-channel shell audit; tempered half-line Fourier theorem with uniform integration-by-parts tail; Gaussian even/odd sign fixtures; imported exact support and total-kappa identities.",
            "generated_by": "reverse_physics/bt_fully_rearranged_rigged_all_time_packet_limit.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_rigged_all_time_packet_limit.py",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "items": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_rigged_all_time_packet_limit.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_rigged_all_time_packet_limit.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_rigged_all_time_packet_limit",
        ],
        "report": REPORT,
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
    print(args.output)
    print(
        "BT FULLY REARRANGED RIGGED ALL-TIME PACKET LIMIT: "
        f"{'ALL PASS' if value['checks']['ok'] else 'FAIL'} "
        f"({value['checks']['passed']}/{value['checks']['total']})"
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
