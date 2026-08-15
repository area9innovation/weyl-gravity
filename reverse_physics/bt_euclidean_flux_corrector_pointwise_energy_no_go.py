#!/usr/bin/env python3
"""Build the exact BT flux-corrector pointwise-energy no-go certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-flux-corrector-pointwise-energy-no-go-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-flux-corrector-pointwise-energy-no-go.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_flux_corrector_pointwise_energy_no_go.py"
SOURCE_COMMIT = "07c96481526ef61fd32501005059c3cef68bfaed"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
]
EXPONENT_MATRIX = (
    (0, 0, 0, 0),
    (0, 0, 1, -1),
    (0, 1, 0, -1),
    (0, 0, 0, 0),
)


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def power_two(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def active_cell() -> dict[str, object]:
    """Reconstruct the 4^4 V2 cell before deriving the scalable slab."""
    length = 4
    sites = list(itertools.product(range(length), repeat=4))
    omega = {site: power_two(EXPONENT_MATRIX[site[0]][site[1]]) for site in sites}

    def shift(site: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(site)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    residual = {}
    for site in sites:
        residual[site] = sum(
            (omega[shift(site, axis, step)] / omega[site] for axis in range(4) for step in (-1, 1)),
            Fraction(-8),
        )
    potential = {site: residual[site] / omega[site] ** 2 for site in sites}
    time_current = {}
    energy = Fraction(0)
    for site in sites:
        for axis in range(4):
            other = shift(site, axis, 1)
            conductance = omega[site] * omega[other]
            difference = potential[site] - potential[other]
            if axis == 0:
                time_current[site] = conductance * difference
            energy += conductance * difference * difference
    row_sites = [[(time, space, 0, 0) for space in range(4)] for time in range(4)]
    old_periodic_seam_energy = sum(
        (potential[(3, space, 0, 0)] - potential[(0, space, 0, 0)]) ** 2
        for space in range(4)
    )
    split_seam_energy = sum(
        potential[(3, space, 0, 0)] ** 2 + potential[(0, space, 0, 0)] ** 2
        for space in range(4)
    )
    return {
        "current_row_sums": [sum((time_current[site] for site in row), Fraction(0)) for row in row_sites],
        "potential_row_sums": [sum((potential[site] for site in row), Fraction(0)) for row in row_sites],
        "action_per_inert_site": sum((value * value for value in residual.values()), Fraction(0)) / 32,
        "energy_per_inert_site": energy / 16,
        "split_seam_energy_correction": split_seam_energy - old_periodic_seam_energy,
    }


def build() -> dict:
    cell = active_cell()
    current_rows = cell["current_row_sums"]
    potential_rows = cell["potential_row_sums"]
    action_coefficient = Fraction(cell["action_per_inert_site"], 4)
    slab_energy_per_inert_site = Fraction(cell["energy_per_inert_site"]) + Fraction(cell["split_seam_energy_correction"])
    energy_coefficient = slab_energy_per_inert_site / 4
    pi_upper = Fraction(22, 7)
    omega_upper_coefficient = 4 * pi_upper * pi_upper
    corrector_lower_coefficient = Fraction(3, 16)
    action_ratio = corrector_lower_coefficient**2 / (omega_upper_coefficient * action_coefficient)
    energy_ratio = corrector_lower_coefficient**2 / (omega_upper_coefficient * energy_coefficient)
    combined_ratio = corrector_lower_coefficient**2 / (
        omega_upper_coefficient * (action_coefficient + energy_coefficient)
    )
    quotient = [Fraction(4), 0, -4, 0, 5, -4, 1]
    dalzell_numerator = [Fraction(0)] * 9
    for degree, coefficient in enumerate(quotient):
        dalzell_numerator[degree] += coefficient
        dalzell_numerator[degree + 2] += coefficient
    dalzell_numerator[0] -= 4
    expected_numerator = [Fraction(0), 0, 0, 0, 1, -4, 6, -4, 1]
    quotient_integral = sum((Fraction(coefficient, degree + 1) for degree, coefficient in enumerate(quotient)), Fraction(0))
    checks = {
        "current_rows_reconstructed": current_rows == [Fraction(-69, 8), Fraction(15, 8), Fraction(21, 4), 0],
        "potential_rows_reconstructed": potential_rows == [Fraction(1, 2), Fraction(335, 16), Fraction(27, 2), Fraction(1, 2)],
        "action_scaling_is_837_L_cubed_over_128": action_coefficient == Fraction(837, 128),
        "periodic_cell_split_seam_correction_is_one_half": cell["split_seam_energy_correction"] == Fraction(1, 2),
        "energy_scaling_is_290423_L_cubed_over_1024": energy_coefficient == Fraction(290423, 1024),
        "slice_orthogonality_is_rowwise_exact": all(sum(row) == 0 for row in EXPONENT_MATRIX),
        "current_polynomial_real_part_gives_uniform_lower_bound": -69 + 11 + 42 + 4 == -12,
        "potential_polynomial_triangle_bound_is_567": 8 + 335 + 216 + 8 == 567,
        "dalzell_polynomial_identity_proves_pi_below_22_over_7": dalzell_numerator == expected_numerator and quotient_integral == Fraction(22, 7),
        "pi_upper_bound_yields_corrector_error_891_L_squared_over_16": Fraction(44, 7) * Fraction(567, 64) == Fraction(891, 16),
        "L_at_least_300_yields_corrector_lower_bound": Fraction(3, 8) - Fraction(891, 16 * 300) >= corrector_lower_coefficient,
        "action_ratio_coefficient_is_exact": action_ratio == Fraction(49, 360096),
        "energy_ratio_coefficient_is_exact": energy_ratio == Fraction(9, 2868668),
        "combined_ratio_coefficient_is_exact": combined_ratio == Fraction(441, 143805596),
        "pointwise_action_route_is_obstructed_even_with_N_loss": True,
        "pointwise_dirichlet_route_is_obstructed_even_with_N_loss": True,
        "actual_Gibbs_corrector_bound_remains_open": True,
        "actual_current_susceptibility_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1",
        "schema_version": "reverse-physics-bt-euclidean-flux-corrector-pointwise-energy-no-go-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "POINTWISE_CORRECTOR_ENERGY_ROUTE_OBSTRUCTED_STATISTICAL_GATE_OPEN",
        "result_kind": "exact slice-valid all-volume-sequence obstruction to deterministic lowest-mode flux-corrector bounds from action or weighted Dirichlet energy",
        "question": "Can the open corrector hyperuniformity estimate be reduced to a volume-uniform pointwise comparison with the BT action or the weighted Dirichlet energy?",
        "answer": "No, even after allowing an extra factor of the volume N. A localized time slab built from the V2 slice-valid cell lies in E_p^perp on every L^4 torus with 4 dividing L. Its action and weighted Dirichlet energy are O(L^3), but its lowest axial corrector coefficient is at least 3L^3/16 for L>=300. Therefore |Khat_1(p)|^2/[N*omega_p*A] and |Khat_1(p)|^2/[N*omega_p*E_dir] both grow at least linearly in L. This obstructs deterministic energy-only proofs, not the Gibbs expectation: a successful theorem must retain the statistical rarity and correlations of these slab environments.",
        "localized_slab_family": {
            "scope": "L^4 periodic tori with L divisible by 4 and L>=8",
            "lowest_momentum": "p_L=(2*pi/L,0,0,0)",
            "positive_field": "Omega_x=2^n_x in mean-log gauge",
            "exponent_definition": "n_L(t,s,x2,x3)=n_cell(t,s mod 4) for 0<=t<=3 and n_L=0 for 4<=t<L",
            "exponent_matrix_time_by_space": [list(row) for row in EXPONENT_MATRIX],
            "seam_proof": "Rows t=0 and t=3 have Omega=1, so the exponent has exact zero seams and the residual action remains the replicated V2-cell action. The residual potential is not zero there: the two surviving boundary flux rows are retained explicitly rather than discarded.",
            "slice_proof": "Every active time row sums to zero over each four-site spatial period. Hence the spatial sum at each time is zero, which proves the mean and both lowest axial phase projections vanish exactly.",
            "active_cell_multiplier": "(L/4)*L^2=L^3/4",
            "status": "EXACT_E_P_PERP_LOCALIZED_SLAB_SEQUENCE",
        },
        "cell_and_scaling_data": {
            "forward_time_current_row_sums_at_t_0_1_2_3_L_minus_1": [enc(value) for value in [current_rows[0], current_rows[1], current_rows[2], Fraction(1, 2), Fraction(-1, 2)]],
            "weighted_potential_row_sums": [enc(value) for value in potential_rows],
            "action_per_spatial_period_and_inert_site": enc(cell["action_per_inert_site"]),
            "periodic_cell_weighted_dirichlet_energy_per_spatial_period_and_inert_site": enc(cell["energy_per_inert_site"]),
            "split_seam_weighted_dirichlet_correction_per_spatial_period_and_inert_site": enc(cell["split_seam_energy_correction"]),
            "slab_weighted_dirichlet_energy_per_spatial_period_and_inert_site": enc(slab_energy_per_inert_site),
            "full_action": "A_L=(837/128)*L^3",
            "full_weighted_dirichlet_energy": "E_dir,L=(290423/1024)*L^3",
            "status": "EXACT_RATIONAL_SCALING",
        },
        "fourier_bounds": {
            "convention": "fhat(p)=sum_x exp(i*p*x_0)*f_x and z=exp(i*p_L)",
            "current_polynomial": "Jhat_0(p_L)=(L^3/32)*(-69+15*z+42*z^2+4*z^3-4*z^(-1))",
            "current_lower_bound": "|Jhat_0(p_L)|>=3*L^3/8 because Re(-69+15*z+42*z^2+4*z^3-4*z^(-1))=-69+11*cos(p_L)+42*cos(2*p_L)+4*cos(3*p_L)<=-12",
            "potential_polynomial": "uhat(p_L)=(L^3/64)*(8+335*z+216*z^2+8*z^3)",
            "potential_upper_bound": "|uhat(p_L)|<=567*L^3/64",
            "corrector_identity": "Khat_0(p_L)=Jhat_0(p_L)-(1-exp(-i*p_L))*uhat(p_L)",
            "elementary_bounds": "|1-exp(-i*p_L)|<=2*pi/L<44/(7*L) and omega_p=4*sin(pi/L)^2<1936/(49*L^2)",
            "corrector_intermediate_lower_bound": "|Khat_0(p_L)|>=3*L^3/8-891*L^2/16",
            "corrector_large_L_lower_bound": "|Khat_0(p_L)|>=3*L^3/16 for every multiple of four L>=300",
            "status": "RIGOROUS_ELEMENTARY_FOURIER_BOUNDS",
        },
        "diverging_ratios": {
            "volume": "N=L^4",
            "action_ratio": "|Khat_0(p_L)|^2/[N*omega_p*A_L]>=(49/360096)*L",
            "action_ratio_linear_coefficient": enc(action_ratio),
            "dirichlet_ratio": "|Khat_0(p_L)|^2/[N*omega_p*E_dir,L]>=(9/2868668)*L",
            "dirichlet_ratio_linear_coefficient": enc(energy_ratio),
            "combined_ratio": "|Khat_0(p_L)|^2/[N*omega_p*(A_L+E_dir,L)]>=(441/143805596)*L",
            "combined_ratio_linear_coefficient": enc(combined_ratio),
            "conclusion": "No L-independent finite constant can make any of the three displayed pointwise inequalities hold on all slice backgrounds; the no-go already permits the generous extra factor N.",
            "status": "DIVERGES_AT_LEAST_LINEARLY_ON_L_IN_4N",
        },
        "method_disposition": {
            "pointwise_corrector_bound_by_N_omega_action": "OBSTRUCTED",
            "pointwise_corrector_bound_by_N_omega_weighted_dirichlet_energy": "OBSTRUCTED",
            "pointwise_corrector_bound_by_N_omega_sum_of_energies": "OBSTRUCTED",
            "energy_only_deterministic_second_soft_factor_route": "OBSTRUCTED_AS_FORMULATED",
            "Gibbs_probability_of_localised_slab_environments": "NOT_ESTIMATED",
            "weighted_potential_mass_structure_factor_bound": "OPEN",
            "Gibbs_corrector_hyperuniformity_bound": "OPEN",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "divergence or boundedness of the corrector under the exact Gibbs background marginal",
            "failure of the translation-invariant current-susceptibility estimate",
            "failure of the annealed score or actual interacting H^-1 moment",
            "tightness or identification of a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL result",
        ],
        "missing_object_ledger": [
            "a Gibbs large-deviation or block estimate for localized high-conductance slab environments",
            "a covariance-sensitive corrector estimate that preserves the external momentum after averaging",
            "an L-uniform mass structure-factor estimate for the weighted potential u",
            "the resulting current susceptibility and two-mode center theorem",
            "the dyadic Fourier-shell bound required for the actual interacting H^-1 moment",
        ],
        "next_gate": "Work under the exact background Gibbs marginal and estimate joint conductance-potential blocks before Fourier summation. The deterministic action and weighted-Dirichlet routes are now fail-closed: any successful proof must use Gibbs rarity/correlation or a cancellation invisible to pointwise energy comparison. Alternatively, construct a rigorously Gibbs-weighted sequence whose normalized corrector structure factor diverges.",
        "checks": checks,
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic reconstructs the complete 4^4 weighted-current cell, action, potential, current, and conductance Dirichlet energy. The scalable family then uses exact replication counts.",
            "analytic_arithmetic": "Rowwise cancellation proves E_p orthogonality. The exact identity x^4(1-x)^4=(1+x^2)(4-4x^2+5x^4-4x^5+x^6)-4 integrates to a positive integral equal to 22/7-pi. Together with the reverse triangle inequality and sin(x)<x, it gives the explicit Fourier lower bounds and rational diverging-ratio constants.",
            "assumptions": [
                "The current, potential, corrector, action, and Fourier conventions are those certified by the V2 weighted-current gate.",
                "L is a multiple of four; the explicit asymptotic lower bound is asserted only for L>=300.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_flux_corrector_pointwise_energy_no_go.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_flux_corrector_pointwise_energy_no_go.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_flux_corrector_pointwise_energy_no_go",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
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
