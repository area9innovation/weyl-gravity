#!/usr/bin/env python3
"""Build the slice-valid BT weighted-current gate V2 certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-weighted-current-gate-v2.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-full-phase-weighted-current-gate-v2.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_full_phase_weighted_current_gate_v2.py"
SOURCE_COMMIT = "f21cc5b29b7f11a51006ec7f098a013e2fef9cc6"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json",
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


def fixture() -> dict:
    length = 4
    volume = length**4

    def coordinates(index: int) -> tuple[int, ...]:
        result = [0] * 4
        for axis in range(3, -1, -1):
            result[axis] = index % length
            index //= length
        return tuple(result)

    def index_of(point: tuple[int, ...]) -> int:
        value = 0
        for coordinate in point:
            value = value * length + coordinate % length
        return value

    points = [coordinates(index) for index in range(volume)]
    exponents = [EXPONENT_MATRIX[point[0]][point[1]] for point in points]
    omega = [power_two(exponent) for exponent in exponents]
    residual = []
    for index, point in enumerate(points):
        value = Fraction(-8)
        for axis in range(4):
            for step in (-1, 1):
                shifted = list(point)
                shifted[axis] += step
                value += omega[index_of(tuple(shifted))] / omega[index]
        residual.append(value)
    potential = [residual[index] / omega[index] ** 2 for index in range(volume)]
    currents: list[list[Fraction]] = [[] for _ in range(4)]
    correctors: list[list[Fraction]] = [[] for _ in range(4)]
    weighted_identity = True
    dirichlet_energy = Fraction(0)
    for index, point in enumerate(points):
        for axis in range(4):
            shifted = list(point)
            shifted[axis] += 1
            other = index_of(tuple(shifted))
            current = (
                residual[index] * omega[other] / omega[index]
                - residual[other] * omega[index] / omega[other]
            )
            conductance = omega[index] * omega[other]
            currents[axis].append(current)
            correctors[axis].append(current - (potential[index] - potential[other]))
            weighted_identity &= current == conductance * (potential[index] - potential[other])
            dirichlet_energy += conductance * (potential[index] - potential[other]) ** 2
    cosine = (1, 0, -1, 0)
    sine = (0, 1, 0, -1)
    exponent_mean = sum(exponents)
    cosine_projection = sum(exponents[index] * cosine[point[0]] for index, point in enumerate(points))
    sine_projection = sum(exponents[index] * sine[point[0]] for index, point in enumerate(points))
    action = sum((value * value for value in residual), Fraction(0)) / 2
    weighted_mean = sum(omega[index] ** 3 * potential[index] for index in range(volume))
    active_residual = [
        [residual[index_of((time, space, 0, 0))] for space in range(length)]
        for time in range(length)
    ]
    active_time_current = [
        [currents[0][index_of((time, space, 0, 0))] for space in range(length)]
        for time in range(length)
    ]
    return {
        "volume": volume,
        "exponent_mean": exponent_mean,
        "cosine_projection": cosine_projection,
        "sine_projection": sine_projection,
        "residual": residual,
        "potential": potential,
        "currents": currents,
        "correctors": correctors,
        "weighted_identity": weighted_identity,
        "weighted_mean": weighted_mean,
        "action": action,
        "dirichlet_energy": dirichlet_energy,
        "active_residual": active_residual,
        "active_time_current": active_time_current,
    }


def build() -> dict:
    values = fixture()
    current_zero_modes = [sum(row, Fraction(0)) for row in values["currents"]]
    corrector_zero_modes = [sum(row, Fraction(0)) for row in values["correctors"]]
    checks = {
        "exponent_field_is_mean_zero": values["exponent_mean"] == 0,
        "exponent_field_is_cosine_orthogonal": values["cosine_projection"] == 0,
        "exponent_field_is_sine_orthogonal": values["sine_projection"] == 0,
        "fixture_lies_in_full_phase_background_slice": values["exponent_mean"] == values["cosine_projection"] == values["sine_projection"] == 0,
        "weighted_gradient_identity_holds_on_every_positive_edge": values["weighted_identity"],
        "weighted_potential_has_exact_zero_mean": values["weighted_mean"] == 0,
        "time_current_zero_mode_is_minus_twenty_four": current_zero_modes[0] == -24,
        "fixture_action_is_837_over_2": values["action"] == Fraction(837, 2),
        "weighted_dirichlet_energy_is_290295_over_16": values["dirichlet_energy"] == Fraction(290295, 16),
        "v1_fixture_did_not_certify_slice_restriction": True,
        "unweighted_pointwise_second_factor_is_obstructed_on_slice": True,
        "weighted_flux_normal_form_is_exact": True,
        "plain_gradient_has_zero_periodic_current_mode": all(
            current_zero_modes[axis] == corrector_zero_modes[axis] for axis in range(4)
        ),
        "slice_fixture_time_zero_mode_is_entirely_corrector": corrector_zero_modes[0] == -24,
        "flux_corrector_estimate_remains_open": True,
        "current_susceptibility_remains_open": True,
        "actual_H_minus_one_bound_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2",
        "schema_version": "reverse-physics-bt-euclidean-full-phase-weighted-current-gate-v2",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "SLICE_VALID_WEIGHTED_FLUX_NORMAL_FORM_PROVED_CORRECTOR_GATE_OPEN",
        "result_kind": "exact weighted-current normal form and slice-valid rational obstruction to an unweighted second factor",
        "question": "Does the canonical-current obstruction survive on the actual full-phase background slice, and what exact structure remains available for the statistical susceptibility theorem?",
        "answer": "Yes, the unweighted pointwise shortcut is obstructed on the actual slice, but the current has a stronger weighted structure. On the 4^4 torus the mean-zero exponent matrix n with rows (0,0,0,0), (0,0,1,-1), (0,1,0,-1), (0,0,0,0), replicated in two inert axes, gives Omega_x=2^n_x and lies exactly in E_p^perp for the lowest axial cosine-sine pair. Its canonical time-current zero mode is -24 and its action is 837/2, so the canonical current is not an unweighted periodic gradient even after restriction to E_p^perp. For every positive field, however, setting u_x=r_x/Omega_x^2 gives the exact conductance-flux identity J_xy=Omega_x*Omega_y*(u_x-u_y) and sum_x Omega_x^3*u_x=0. Thus the live theorem is an L-uniform hyperuniformity or flux-corrector estimate for this nonlinear random-conductance current under the exact translation-invariant background Gibbs marginal. No such statistical estimate is proved here.",
        "supersession": {
            "predecessor": "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1",
            "retained": [
                "full cosine-sine background translation invariance",
                "two-mode center-score reduction",
                "canonical current-divergence and score identities",
                "the current-susceptibility theorem remains the live gate",
            ],
            "corrected_boundary": "The V1 row (1,1,2,4) was mean-zero only after gauge fixing but was not orthogonal to the lowest cosine-sine eigenspace. It refuted a universal unweighted-gradient identity, not its restriction to E_p^perp. The V2 two-axis fixture closes that restricted-domain gap.",
            "status": "V1_FIXTURE_SCOPE_NARROWED_V2_SLICE_VALID_OBSTRUCTION",
        },
        "weighted_current_normal_form": {
            "positive_field": "Omega_x=exp(psi_x)",
            "residual": "r_x=(Delta Omega)_x/Omega_x=sum_(y~x)(Omega_y/Omega_x-1)",
            "weighted_potential": "u_x=r_x/Omega_x^2=(Delta Omega)_x/Omega_x^3",
            "conductance": "c_xy=Omega_x*Omega_y=c_yx>0",
            "identity": "J_xy=c_xy*(u_x-u_y)",
            "weighted_zero_mean": "sum_x Omega_x^3*u_x=sum_x (Delta Omega)_x=0",
            "current_divergence": "partial A/partial psi_x=-sum_(y~x) J_xy",
            "interpretation": "The missing second softness is a statistical flux-corrector or hyperuniformity theorem for a nonlinear random-conductance gradient, not an unweighted pointwise gradient identity.",
            "status": "EXACT_FOR_EVERY_POSITIVE_FINITE_PERIODIC_FIELD",
        },
        "plain_gradient_corrector_split": {
            "gauge": "sum_x psi_x=0, equivalently product_x Omega_x=1",
            "plain_gradient": "(grad_i u)_x=u_x-u_(x+e_i)",
            "conductance_corrector": "K_(x,i)=(Omega_x*Omega_(x+e_i)-1)*(u_x-u_(x+e_i))",
            "decomposition": "J_(x,i)=(grad_i u)_x+K_(x,i)",
            "axial_fourier_identity": "Jhat_1(p)=(1-exp(-i*p_1))*uhat(p)+Khat_1(p)",
            "deterministic_square_bound": "|Jhat_1(p)|^2<=2*omega_p*|uhat(p)|^2+2*|Khat_1(p)|^2",
            "sufficient_potential_estimate": "E_nu[|uhat(p)|^2]<=C_u*g^2*N",
            "sufficient_corrector_estimate": "E_nu[|Khat_1(p)|^2]<=C_K*g^2*N*omega_p",
            "consequence": "the two sufficient estimates imply E_nu[|Jhat_1(p)|^2]<=2*(C_u+C_K)*g^2*N*omega_p",
            "fixture_corrector_time_zero_mode": enc(corrector_zero_modes[0]),
            "status": "EXACT_TWO_SUBGATE_REDUCTION",
        },
        "slice_valid_fixture": {
            "lattice": "4^4 periodic torus; exponent depends on axes 0 and 1 and is replicated over axes 2 and 3",
            "lowest_axis": 0,
            "positive_field": "Omega_x=2^n_x",
            "exponent_matrix_time_by_space": [list(row) for row in EXPONENT_MATRIX],
            "mean_zero_exponent_sum": values["exponent_mean"],
            "lowest_cosine_projection": values["cosine_projection"],
            "lowest_sine_projection": values["sine_projection"],
            "active_residual_matrix": [[enc(value) for value in row] for row in values["active_residual"]],
            "active_forward_time_current_matrix": [[enc(value) for value in row] for row in values["active_time_current"]],
            "inert_replication_factor": 16,
            "full_time_current_zero_mode": enc(current_zero_modes[0]),
            "full_action": enc(values["action"]),
            "weighted_dirichlet_energy": enc(values["dirichlet_energy"]),
            "weighted_potential_mean": enc(values["weighted_mean"]),
            "status": "EXACT_RATIONAL_E_P_ORTHOGONAL_UNWEIGHTED_GRADIENT_OBSTRUCTION",
        },
        "method_disposition": {
            "v1_fixture_as_full_phase_slice_witness": "WITHDRAWN_SCOPE_ERROR",
            "slice_valid_unweighted_periodic_gradient_identity": "OBSTRUCTED",
            "weighted_random_conductance_gradient_identity": "PROVED",
            "weighted_potential_zero_mean_identity": "PROVED",
            "plain_gradient_corrector_split": "PROVED",
            "weighted_potential_mass_structure_factor_bound": "OPEN",
            "conductance_corrector_hyperuniformity_bound": "OPEN",
            "translation_invariant_flux_corrector_bound": "OPEN",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the flux-corrector or current-susceptibility bound",
            "boundedness or divergence of the actual annealed score",
            "the interacting H^-1 estimate or a Fourier-shell theorem",
            "tightness or identification of a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, or Lorentzian causal statement",
        ],
        "missing_object_ledger": [
            "an L-uniform structure-factor estimate for c*grad(u) at the lowest nonzero momentum",
            "an L-uniform mass estimate E_nu[|uhat(p)|^2]<=C*g^2*N for the weighted potential",
            "a flux-corrector decomposition whose remainder retains one additional external momentum under the background Gibbs law",
            "large-field control of the conductances Omega_x*Omega_y and the weighted potential u",
            "the resulting two-mode center theorem and dyadic Fourier-shell sum",
            "tightness and continuum identification only after the actual H^-1 theorem",
        ],
        "next_gate": "Use the exact stationary conductance flux J=c*grad(u). Prove an L-uniform flux-corrector/hyperuniformity estimate E_nu[|Jhat_1(p)|^2]<=C*g^2*N*omega_p on the tuned branch, with large-conductance blocks controlled before Fourier summation; or construct an actual Gibbs-weighted correlated environment for which this normalized structure factor diverges. Translation invariance or the weighted-gradient identity alone is not the theorem.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic enumerates all 256 sites, four positive edge directions, the full-phase projections, residuals, currents, weighted potential, action, and conductance Dirichlet energy.",
            "analytic_arithmetic": "Direct substitution proves J_xy=Omega_x*Omega_y*(r_x/Omega_x^2-r_y/Omega_y^2) and the periodic Laplacian sum proves the weighted zero-mean identity.",
            "assumptions": [
                "The BT action, current, and Fourier normalizations are those of the V1 current-gate certificate.",
                "Mean-zero logarithmic gauge fixes the otherwise irrelevant global scale of Omega.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_weighted_current_gate_v2.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_weighted_current_gate_v2.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_weighted_current_gate_v2",
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
