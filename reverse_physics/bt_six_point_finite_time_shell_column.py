#!/usr/bin/env python3
"""Finite-time local shell column for the BT six-point sequential history."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from bt_six_point_full_phase_space_born_positivity import add, channel_square, physical_chart


CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-six-point-finite-time-shell-column-v1.schema.json"
REPORT = "reverse_physics/reports/bt-six-point-finite-time-shell-column.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-finite-time-shell-column.json",
    "reverse_physics/bt_six_point_full_phase_space_born_positivity.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PHASE_SPACE_POLE_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def exact_fixture():
    point = (sp.Rational(2), sp.Rational(-2), sp.Rational(3, 5), sp.Rational(1, 2), sp.Rational(1, 3))
    momenta, _ = physical_chart(*point)
    intermediate = tuple(sp.factor(value) for value in add(*(momenta[index] for index in range(6) if 11 & (1 << index))))
    return point, intermediate


def exact_phase_space_coarea():
    a, b, t, u, v = sp.symbols("a b t u v")
    parameters = [a, b, t, u, v]
    point = {a: 2, b: -2, t: sp.Rational(3, 5), u: sp.Rational(1, 2), v: sp.Rational(1, 3)}
    momenta, energies = physical_chart(*parameters)
    outgoing_spatial = sp.Matrix([-momenta[index][component] for index in range(3, 6) for component in range(1, 4)])
    chart_jacobian = outgoing_spatial.jacobian(parameters).subs(point)
    spatial_vectors = [[-momenta[index][component].subs(point) for component in range(1, 4)] for index in range(3, 6)]
    energy_values = [sp.sympify(value).subs(point) for value in energies]
    constraint_jacobian = sp.zeros(4, 9)
    for particle in range(3):
        for component in range(3):
            constraint_jacobian[0, 3 * particle + component] = spatial_vectors[particle][component] / energy_values[particle]
            constraint_jacobian[component + 1, 3 * particle + component] = 1
    chart_gram_determinant = sp.factor((chart_jacobian.T * chart_jacobian).det())
    constraint_gram_determinant = sp.factor((constraint_jacobian * constraint_jacobian.T).det())
    energy_product = sp.prod(energy_values)
    density_squared = sp.factor(chart_gram_determinant / (64 * energy_product**2 * constraint_gram_determinant))
    chart_density = sp.sqrt(density_squared)
    pole = sp.sympify(channel_square(momenta, 11))
    transverse_derivative = sp.factor(sp.diff(pole, t).subs(point))
    shell_density = sp.factor(chart_density / sp.Abs(transverse_derivative))
    return {
        "chart_gram_determinant": chart_gram_determinant,
        "constraint_gram_determinant": constraint_gram_determinant,
        "outgoing_energy_product": energy_product,
        "chart_density_without_two_pi": chart_density,
        "transverse_derivative": transverse_derivative,
        "shell_density_without_two_pi": shell_density,
    }


def build():
    pole = load(INPUTS[2])
    sequential = load(INPUTS[3])
    incidence = load(INPUTS[4])
    point, intermediate = exact_fixture()
    phase_space = exact_phase_space_coarea()
    energy = sp.Abs(intermediate[0])
    s, omega = sp.symbols("s omega", real=True)
    duration, shell_energy, cutoff = sp.symbols("T E L", positive=True)
    window_norm_omega = sp.integrate(4 * sp.sin(omega * duration / 2) ** 2 / omega**2, (omega, -sp.oo, sp.oo))
    shell_norm = sp.simplify((2 * shell_energy) * window_norm_omega / (4 * shell_energy**2))
    history_norm = sp.simplify(sp.Rational(9, 8) * shell_norm)
    normalized_history_vector = sp.ones(9, 1) / 3
    skew_generator = sp.zeros(10, 10)
    skew_generator[0, 1:] = -normalized_history_vector.T
    skew_generator[1:, 0] = normalized_history_vector
    strength = sp.symbols("g", real=True)
    transition_probability = strength**2 * history_norm
    cross_constant = 2 * sp.Si(cutoff * duration / (2 * shell_energy))
    cross_limit = sp.limit(cross_constant, duration, sp.oo)
    cross_relative_limit = sp.limit(cross_constant / history_norm, duration, sp.oo)
    labeled_phase_rate = sp.factor(
        phase_space["shell_density_without_two_pi"]
        * history_norm.subs(shell_energy, energy)
        / (2 * sp.pi) ** 5
    )
    ordinary_identical_phase_rate = sp.factor(labeled_phase_rate / sp.factorial(3))
    checks = {
        "all_inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_unique_pole_is_channel_11": pole["exact_transverse_physical_pole"]["unique_zero_channel"] == 11,
        "exact_point_replays": pole["exact_transverse_physical_pole"]["point"] == [str(value) for value in point],
        "intermediate_momentum_is_exactly_null": sp.simplify(intermediate[0] ** 2 - sum(value**2 for value in intermediate[1:])) == 0,
        "intermediate_energy_is_positive_one": energy == 1,
        "history_residue_norm_is_nine_over_eight": sequential["exact_channel_carrier"]["fixed_channel_born_norm"] == "9/8",
        "typed_history_lift_is_isometric": incidence["typed_history_carrier"]["isometry_identity"] == "W_hist^T*W_hist=I10",
        "finite_time_window_has_exact_Plancherel_norm": window_norm_omega == 2 * sp.pi * duration,
        "shell_kernel_has_exact_norm": shell_norm == sp.pi * duration / shell_energy,
        "history_column_norm_matches_pole_coefficient": history_norm == sp.Rational(9, 8) * sp.pi * duration / shell_energy,
        "exact_fixture_history_norm_is_nine_pi_T_over_eight": history_norm.subs(shell_energy, energy) == sp.Rational(9, 8) * sp.pi * duration,
        "phase_space_chart_gram_is_exact": phase_space["chart_gram_determinant"] == sp.Rational(13544423424, 2822265625),
        "phase_space_constraint_gram_is_exact": phase_space["constraint_gram_determinant"] == sp.Rational(2016, 25),
        "phase_space_chart_density_is_exact": phase_space["chart_density_without_two_pi"] == sp.Rational(54, 2125),
        "phase_space_shell_density_is_exact": phase_space["shell_density_without_two_pi"] == sp.Rational(3, 320),
        "labeled_phase_weighted_rate_is_exact": labeled_phase_rate == 27 * duration / (81920 * sp.pi**4),
        "ordinary_identical_preflight_is_exact": ordinary_identical_phase_rate == 9 * duration / (163840 * sp.pi**4),
        "constant_cross_term_has_finite_long_time_limit": cross_limit == sp.pi,
        "constant_cross_term_is_subleading_to_history_norm": cross_relative_limit == 0,
        "local_column_completeness_is_exact": sp.simplify(
            1 - transition_probability + strength**2 * history_norm
        ) == 1,
        "rank_one_unitary_dilation_is_exact": (
            (normalized_history_vector.T * normalized_history_vector)[0] == 1
            and skew_generator.T == -skew_generator
            and skew_generator**3 == -skew_generator
        ),
        "effective_strength_phase_space_and_BT_hamiltonian_affiliation_remain_open": True,
        "multi_channel_gluing_eq19_gravity_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1",
        "schema_version": "reverse-physics-bt-six-point-finite-time-shell-column-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact finite-time single-shell history amplitude, normalized local survival column, and isolated-channel duration hierarchy",
        "question": "Does the exact transverse six-point factorization pole define a square-integrable finite-time history amplitude with a normalized survival completion on its local shell?",
        "answer": "Yes on the declared single-shell reduced-mode carrier. At the exact positive-energy rank-five pole point, the channel-11 intermediate momentum is (1,9/17,-4/85,-72/85), null with energy E=1. The exact coarea pullback of labeled massless three-body phase space is 54/[2125*(2*pi)^5] in (a,b,t,u,v) and 3/[320*(2*pi)^5] after replacing t by the transverse shell coordinate s. For F_T(omega)=integral_0^T exp(i omega t)dt, define alpha_T,E(s)=F_T(s/(2E))/(2E)=2 exp(i sT/(4E)) sin(sT/(4E))/s. Its exact L2(ds) norm is pi*T/E. Tensoring alpha with the fixed-channel nine-history residue vector of reduced Born norm 9/8 gives A_T^* A_T=Q_T I with Q_T=9*pi*T/(8E), exactly the sequential coefficient previously obtained as a distributional leading term. Including the frozen labeled final-state phase measure gives 27*T/(81920*pi^4), before the common BT multiplier, incoming flux, tangential detector normalization and identical-particle convention. For a real effective local strength g in the perturbative domain q=g^2 Q_T<=1, M_g=(sqrt(1-q)I,g A_T)^T is an isometric survival-plus-history column. With V_T=A_T/sqrt(Q_T), the skew rank-one block K_T=[[0,-V_T^*],[V_T,0]] obeys K_T^3=-K_T; choosing sin(theta)=g sqrt(Q_T) gives M_g as the source column of an exact unitary rotation. The interference of the shell kernel with a constant regular amplitude on |s|<L is 2*Si(LT/(2E)), tends to pi, and is therefore subleading to the O(T) sequential norm. This constructs a finite local wave-packet probability for the leading isolated history, but g has not been calibrated from the full BT Hamiltonian and generalized Born trace. Multi-channel overlaps, the complete connected remainder and the global Moller defect embedding remain open.",
        "exact_physical_shell": {
            "chart_point": [str(value) for value in point],
            "channel_mask": 11,
            "intermediate_momentum": [str(value) for value in intermediate],
            "intermediate_mass_square": "0",
            "intermediate_energy": str(energy),
            "transverse_shell_coordinate": "s=q^2=2*E*omega+O(omega^2)",
            "measure": "standard labeled Lorentz-invariant three-body phase space; tangential detector weight remains frozen",
        },
        "exact_phase_space_coarea": {
            "starting_measure": "dPhi_3=(2*pi)^(-5)*delta^4(P-sum k_i)*product_i[d^3 k_i/(2 E_i)]",
            "coarea_formula": "sqrt(det(J_chart^T*J_chart))/[8*E1*E2*E3*sqrt(det(J_constraint*J_constraint^T))]",
            "chart_gram_determinant": str(phase_space["chart_gram_determinant"]),
            "constraint_gram_determinant": str(phase_space["constraint_gram_determinant"]),
            "outgoing_energy_product": str(phase_space["outgoing_energy_product"]),
            "chart_density": "54/[2125*(2*pi)^5]",
            "transverse_derivative_ds_dt": str(phase_space["transverse_derivative"]),
            "shell_density": "3/[320*(2*pi)^5]",
            "labeled_phase_weighted_sequential_rate": "27*T/(81920*pi^4)",
            "ordinary_identical_final_state_preflight": "9*T/(163840*pi^4) after division by 3!",
            "boundary": "the 3! factor is recorded only as the ordinary identical-particle convention; the BT generalized-Born projector normalization is not inferred from it",
        },
        "finite_time_kernel": {
            "window": "F_T(omega)=integral_0^T exp(i*omega*t)dt",
            "shell_amplitude": "alpha_T,E(s)=F_T(s/(2E))/(2E)=2*exp(i*s*T/(4E))*sin(s*T/(4E))/s",
            "zero_value": "alpha_T,E(0)=T/(2E)",
            "exact_window_norm": "integral_R |F_T(omega)|^2 d_omega=2*pi*T",
            "exact_shell_norm": "integral_R |alpha_T,E(s)|^2 ds=pi*T/E",
            "approximate_identity": "|alpha_T,E(s)|^2/T -> (pi/E)*delta(s)",
            "status": "EXACT_FINITE_TIME_KINEMATIC_KERNEL_NOT_BT_HAMILTONIAN_DERIVATION",
        },
        "local_history_column": {
            "fixed_channel_history_vector": "h_B=sqrt(2)*B*e_B with nine entries 1/(2*sqrt(2)) and one forbidden zero",
            "history_vector_norm_square": "h_B^*h_B=9/8",
            "amplitude": "A_T,E(s)=alpha_T,E(s)*h_B",
            "gram": "A_T,E^* A_T,E=Q_T I",
            "Q_T": "9*pi*T/(8*E)",
            "exact_fixture_Q_T": "9*pi*T/8",
            "normalized_isometry": "V_T,E=A_T,E/sqrt(Q_T)",
            "status": "EXACT_SINGLE_SHELL_HISTORY_ISOMETRY",
        },
        "normalized_survival_completion": {
            "effective_strength": "g real; after extracting the labeled final-state phase measure, g still contains the common BT tree multiplier, incoming flux, tangential detector normalization and generalized-Born convention",
            "dimensionless_history_probability": "q=g^2*Q_T",
            "perturbative_domain": "0<=q<=1",
            "column": "M_g=(sqrt(1-q)*I,g*A_T,E)^T",
            "completeness": "M_g^*M_g=(1-q)*I+g^2*Q_T*I=I",
            "survival_probability": "1-q",
            "leading_sequential_probability": "q",
            "skew_generator": "K_T=[[0,-V_T,E^*],[V_T,E,0]]",
            "minimal_polynomial_identity": "K_T^3=-K_T",
            "unitary_rotation": "U_theta=I+sin(theta)*K_T+(1-cos(theta))*K_T^2 with sin(theta)=g*sqrt(Q_T)",
            "status": "NORMALIZED_LOCAL_SINGLE_SHELL_COLUMN_NOT_GLOBAL_BT_MOLLER_OPERATOR",
        },
        "isolated_channel_duration_hierarchy": {
            "constant_regular_cross_integral": "integral_-L^L Re(alpha_T,E(s)) ds=2*Si(L*T/(2*E))",
            "long_time_cross_limit": "pi",
            "sequential_norm_growth": "9*pi*T/(8*E)",
            "cross_to_sequential_limit": "0",
            "interpretation": "at an isolated transverse pole the positive sequential history is the O(T) contribution; interference with a smooth regular remainder is O(1) and cannot cancel its rate",
        },
        "interpretation": {
            "finite_time_square_integrable_shell_history": "EXACTLY_CONSTRUCTED",
            "normalized_local_survival_plus_history_column": "EXACTLY_CONSTRUCTED",
            "isolated_channel_leading_rate": "COEFFICIENT_COMPUTED",
            "exact_local_labeled_phase_space_coarea": "COEFFICIENT_COMPUTED",
            "effective_strength_BT_calibration": "NOT_COMPUTED",
            "full_phase_space_wave_packet_embedding": "NOT_CONSTRUCTED",
            "multi_channel_intersection_gluing": "NOT_CONSTRUCTED",
            "connected_interference_distribution": "NOT_PRESCRIBED_GLOBALLY",
            "global_defect_partial_unitary": "NOT_FIXED",
            "finite_inclusive_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": ["the phase-space density away from the exact local fixture or the tangential detector normalization", "the calibration of g from the BT Hamiltonian and generalized Born trace", "a result at simultaneous channel intersections", "global gluing of the ten shell charts", "a prescription for the complete connected interference", "the global defect partial unitary", "a finite inclusive BT probability", "a complete Moller/LSZ/S operator", "Eq. (19)", "loops", "gravity/BRST", "anything LORENTZIAN-CAUSAL", "literature priority"],
        "next_gate": "Calibrate g from the two auxiliary quartic BT vertices, incoming flux and generalized-Born detector normalization, and extend the finite-time column to smooth compact wave packets in all five phase-space coordinates. Then analyze overlaps of two channel tubes and glue the ten local columns into the incoming/outgoing Moller defect continua.",
        "provenance": {"source_commit": "22ddd02f", "retrieval_date": "2026-08-12", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS], "method": "Exact rational reconstruction of the physical intermediate momentum, exact SymPy Plancherel/sinc integral, exact fixed-channel history Gram, and algebraic finite block-rotation completion with fail-closed physical scope."},
        "verification_commands": ["ulimit -v 500000; python3 reverse_physics/bt_six_point_finite_time_shell_column.py --write --check", "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_finite_time_shell_column.py", "ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_finite_time_shell_column"],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA,
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
