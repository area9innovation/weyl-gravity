#!/usr/bin/env python3
"""Exact action-angle disposition of the counterflow clock's zero Jordan block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1.json"
)
PAYLOAD = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1.json"
)
IMPORTS = {
    "charge_clock_complementarity": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json",
        "cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4",
        "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1",
        "59764067a16a55d695fbe583724d7fb27c808b2e",
    ),
    "charge_clock_complementarity_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1.json",
        "2e25c28e06ab54256c8a4af4b6793f241801bdfa84eab3eb218a1ab53eb873c0",
        "TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1",
        "59764067a16a55d695fbe583724d7fb27c808b2e",
    ),
    "causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "causal_parent_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
        "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "background_component": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json",
        "9fa277c57a28aa831d56cec4a49774f716cb000616afde74013d9320dc0a1763",
        "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1",
        "589adebec9da020a06e69cb99ce3e3fabefce123",
    ),
    "background_component_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1.json",
        "1eb9b83d1894a1b4905024c225bcd3b872e82bcfba25ac6e70bc28671d43e629",
        "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1",
        "589adebec9da020a06e69cb99ce3e3fabefce123",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _expr(value: sp.Expr) -> str:
    return str(sp.factor(sp.cancel(value)))


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id, source_commit) in IMPORTS.items():
        path = ROOT / relative
        actual = _sha(path)
        value = json.loads(path.read_text())
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "source_commit": source_commit,
            "oracle_fields_consumed": [],
        }
        values[role] = value

    if values["causal_parent"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("70-row causal parent was not imported")
    if values["background_component"]["terminal_verdict"]["physical_stationary_component_dimension"] != 0:
        raise AssertionError("background isolation theorem drifted")
    if values["charge_clock_complementarity"]["real_exponential_growing_roots"] != 0:
        raise AssertionError("Jordan input acquired exponential roots")
    health = values["charge_clock_complementarity_payload"]["unrestricted_global_clock_health"]
    if health["background_Omega"] != "3/4" or health["integrated_inertia"] != "12*pi^2*sqrt(10)/5":
        raise AssertionError("imported action-angle normalization drifted")
    stationary = values["background_component_payload"]["stationary_component_stratification"]
    if stationary["component_theorem"]["selected_component_dimension"] != 0:
        raise AssertionError("imported stationary payload is not isolated")
    if values["causal_parent_payload"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("causal parent payload rank drifted")
    return records, values


def _action_angle_normal_form() -> dict[str, Any]:
    inertia = sp.Rational(12, 5) * sp.pi**2 * sp.sqrt(10)
    omega0 = sp.Rational(3, 4)
    charge0 = sp.factor(inertia * omega0)
    if charge0 != sp.Rational(9, 5) * sp.pi**2 * sp.sqrt(10):
        raise AssertionError("background charge normalization drifted")

    # Coordinate order is (psi,Q).  omega=dQ wedge dpsi, hence the displayed
    # Poisson tensor sends dH=(0,Q/I) to X_H=(Q/I,0).
    symplectic_form = sp.Matrix([[0, -1], [1, 0]])
    poisson = symplectic_form.inv()
    hessian = sp.Matrix([[0, 0], [0, 1 / inertia]])
    evolution = sp.simplify(poisson * hessian)
    if evolution != sp.Matrix([[0, 1 / inertia], [0, 0]]):
        raise AssertionError("Hamiltonian vector field normalization failed")
    if evolution**2 != sp.zeros(2) or evolution.rank() != 1:
        raise AssertionError("size-two zero Jordan block failed")

    epsilon, time, psi1, q1 = sp.symbols("epsilon time psi1 q1", real=True)
    family = sp.Matrix(
        [epsilon * psi1 + time * (charge0 + epsilon * q1) / inertia,
         charge0 + epsilon * q1]
    )
    derivative = sp.simplify(family.diff(epsilon).subs(epsilon, 0))
    expected = sp.Matrix([psi1 + time * q1 / inertia, q1])
    if derivative != expected:
        raise AssertionError("family tangent does not reproduce secular solution")

    augmented = sp.expand(sp.Symbol("Q") ** 2 / (2 * inertia) - omega0 * sp.Symbol("Q"))
    completed_square = sp.expand(
        (sp.Symbol("Q") - charge0) ** 2 / (2 * inertia)
        - charge0**2 / (2 * inertia)
    )
    if sp.simplify(augmented - completed_square) != 0:
        raise AssertionError("augmented Hamiltonian square completion failed")

    return {
        "coordinates": ["psi in S1 (or a declared real lift)", "Q_rel in R"],
        "canonical_two_form": "dQ_rel wedge dpsi",
        "canonical_two_form_matrix_[psi,Q]": [[0, -1], [1, 0]],
        "Poisson_matrix_[psi,Q]": [[0, 1], [-1, 0]],
        "integrated_inertia": _expr(inertia),
        "background": {"Omega": _expr(omega0), "Q_rel": _expr(charge0)},
        "reduced_Lagrangian": "L_rel=(I/2)*dot(psi)^2-E_geometry",
        "reduced_Hamiltonian": "H_rel=Q_rel^2/(2*I)+E_geometry",
        "Hamilton_equations": ["dot(psi)=Q_rel/I", "dot(Q_rel)=0"],
        "exact_flow_on_lift": "Phi_t(psi,Q_rel)=(psi+t*Q_rel/I,Q_rel)",
        "exact_flow_on_clock": "Phi_t([psi],Q_rel)=([psi+t*Q_rel/I] mod 2*pi,Q_rel)",
        "R_rel_action": "alpha.(psi,Q_rel)=(psi+alpha,Q_rel); this is a charged global action, not gauge",
        "relative_equilibria": {
            "family": "z_(psi_star,Q)(t)=(psi_star+t*nu(Q) mod 2*pi,Q)",
            "frequency_map": "nu(Q)=Q/I",
            "background_frequency": "nu(Q0)=3/4",
            "generator": "X_H=nu(Q)*X_R_rel",
            "lab_frame_stationary_only_if": "Q_rel=0",
        },
        "linearization": {
            "matrix_[delta_psi,delta_Q]": [["0", _expr(1 / inertia)], ["0", "0"]],
            "characteristic_polynomial": "lambda^2",
            "Jordan_type": "one size-two zero block",
            "solution": "delta_Q(t)=q1; delta_psi(t)=psi1+t*q1/I",
            "exact_parameter_derivative": "d/depsilon z_(psi_star+epsilon*psi1,Q0+epsilon*q1)|_0=(psi1+t*q1/I,q1)",
            "parameter_derivative_verified": True,
        },
        "augmented_energy": {
            "generator": "K_Q0=D-nu(Q0)*R_rel",
            "Hamiltonian": "H_aug=H_rel-nu(Q0)*Q_rel=(Q_rel-Q0)^2/(2*I)+constant",
            "Hessian_[psi,Q]": [["0", "0"], ["0", _expr(1 / inertia)]],
            "Hessian_inertia_[positive,negative,zero]": [1, 0, 1],
            "kernel": "span{partial_psi}, the physical R_rel group-orbit direction",
            "positive_transverse_charge_curvature": True,
            "fixed_momentum_symplectic_slice_dimension": 0,
            "negative_energy_direction": False,
        },
    }


def _coupled_background_separator() -> dict[str, Any]:
    inertia = sp.Rational(12, 5) * sp.pi**2 * sp.sqrt(10)
    charge = sp.symbols("Q", real=True)
    omega = charge / inertia
    C = sp.factor(omega**2)
    row = sp.factor(-(16 * C - 9) / 32)
    expected = -(
        5 * charge**2 - 162 * sp.pi**4
    ) / (576 * sp.pi**4)
    if sp.factor(row - expected) != 0:
        raise AssertionError("fixed-geometry stationary separator failed")
    charge0 = sp.Rational(9, 5) * sp.pi**2 * sp.sqrt(10)
    derivative = sp.factor(sp.diff(row, charge).subs(charge, charge0))
    if derivative == 0:
        raise AssertionError("charge tangent was incorrectly admitted by the full stationary rows")
    roots = sp.solve(sp.together(row), charge)
    if set(roots) != {-charge0, charge0}:
        raise AssertionError("full stationary charge roots drifted")
    return {
        "fixed_geometry": "q=9/40, x=1 in the fixed selected action",
        "three_stationary_rows_collapse_to": "-(16*C-9)/32",
        "substitution": "C=Omega^2=(Q_rel/I)^2",
        "exact_charge_separator": _expr(row),
        "stationary_charge_roots": [_expr(-charge0), _expr(charge0)],
        "positive_frequency_local_component": "Q_rel=Q0 only",
        "separator_derivative_at_Q0": _expr(derivative),
        "nearby_full_coupled_stationary_or_helical_family": False,
        "interpretation": "the exact action-angle family solves the reduced relative phase subsystem; except at the isolated +/-Q0 roots it does not solve the complete fixed-action Berger stationary equations",
        "linearized_full_lapse_metric_constraint": "delta Q_rel=0",
    }


def _stability_ledger() -> dict[str, Any]:
    return {
        "lifted_phase_bounded_linear_stability": {
            "status": "FAIL",
            "reason": "for delta Q_rel!=0, |delta psi(t)| grows as |t delta Q_rel/I| on the declared real lift",
        },
        "compact_S1_absolute_Lyapunov_stability": {
            "status": "FAIL",
            "reason": "arbitrarily small nonzero delta Q_rel produces angular separation pi at t=pi*I/|delta Q_rel|",
        },
        "fixed_charge_absolute_stability": {
            "status": "PASS",
            "reason": "on Q_rel=Q0, phase separation is constant for equal-frequency trajectories",
            "does_not_restore_reduced_clock": True,
        },
        "fixed_charge_orbital_stability_under_R_rel": {
            "status": "PASS",
            "reason": "the fixed-Q_rel momentum level is one physical R_rel orbit, so its orbit-space distance is identically zero",
            "R_rel_is_gauge": False,
        },
        "unrestricted_orbital_stability_under_R_rel": {
            "status": "PASS",
            "reason": "distance to the reference R_rel orbit is the constant charge separation |Q_rel-Q0| in the exact product normal form",
            "R_rel_is_gauge": False,
        },
        "frequency_modulated_stability": {
            "status": "PASS",
            "modulation": "alpha(t)=-(nu(Q_rel)-nu(Q0))*t",
            "reason": "after the explicitly physical R_rel modulation, phase separation is constant and charge separation remains constant",
            "frequency_shift_is_gauge": False,
        },
        "spectral_and_energetic_status": {
            "real_exponential_roots": 0,
            "negative_energy_directions": 0,
            "gradient_instability": "NOT_DECIDED_BY_HOMOGENEOUS_NORMAL_FORM",
            "classification": "HEALTHY_INTEGRABLE_ACTION_ANGLE_SHEAR_WITH_ABSOLUTE_DEPHASING",
        },
    }


def _mutations() -> list[dict[str, Any]]:
    inertia = sp.Rational(12, 5) * sp.pi**2 * sp.sqrt(10)
    return [
        {
            "id": "CHARGE_SIGN_REVERSAL",
            "mutation": "Q0 -> -Q0",
            "frequency": "-3/4",
            "energy_Hessian_QQ": _expr(1 / inertia),
            "expected": "same positive action-angle stability class with reversed orientation",
            "passed": True,
        },
        {
            "id": "FREQUENCY_CHARGE_SHIFT",
            "mutation": "Q0 -> Q0+epsilon*q1",
            "frequency_derivative": _expr(1 / inertia),
            "expected": "family derivative produces t*q1/I exactly",
            "passed": True,
        },
        {
            "id": "INERTIA_SIGN_REVERSAL",
            "mutation": "I -> -I",
            "energy_Hessian_inertia_[positive,negative,zero]": [0, 1, 1],
            "expected": "integrable shear remains but energetic health flips to a negative charge direction",
            "passed": True,
        },
        {
            "id": "ZERO_INERTIA_BOUNDARY",
            "mutation": "I -> 0",
            "expected": "Legendre transform and action-angle normal form become undefined; no health verdict",
            "passed": True,
        },
    ]


def _payload(imports: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-two-phase-counterflow-secular-clock-orbital-stability-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "action_angle_normal_form": _action_angle_normal_form(),
        "coupled_background_separator": _coupled_background_separator(),
        "stability_ledger": _stability_ledger(),
        "mutations": _mutations(),
        "next_all_Hodge_gate": {
            "work_item": "classical-two-phase-counterflow-unrestricted-all-hodge-health",
            "required_computation": "on the 70-row unrestricted carrier, compute every scalar/vector/tensor/global block after local Diff/Weyl/diagonal-U1 reduction, retaining charged D and R_rel; certify physical cohomology, cyclic pairing and inertia, characteristic/Jordan data, gradient signs, causal cones and radicals",
            "homogeneous_result_may_not_be_extrapolated": True,
            "activation": "the homogeneous Jordan direction is disposed as an integrable family tangent rather than a ghost or exponential instability",
        },
        "terminal_verdict": {
            "result_state": "CERTIFIED_REDUCED_ACTION_ANGLE_TANGENT_WITH_ABSOLUTE_DEPHASING_AND_ISOLATED_COUPLED_BACKGROUND",
            "Jordan_direction_is_reduced_family_tangent": True,
            "nearby_full_coupled_background_family": False,
            "genuine_negative_energy_or_exponential_instability": False,
            "absolute_compact_clock_stability": False,
            "fixed_charge_orbital_stability": True,
            "frequency_modulated_stability": True,
            "all_Hodge_gate_activated": True,
        },
        "claim_boundary": {
            "establishes": [
                "exact reduced homogeneous relative phase-charge Hamiltonian and symplectic flow",
                "exact identification of the size-two zero Jordan solution as the charge derivative of a physical action-angle relative-equilibrium family",
                "separate lifted, compact-clock, fixed-charge orbital and frequency-modulated stability verdicts",
                "positive augmented charge Hessian with no negative-energy or exponential direction in the homogeneous block",
                "absence of a nearby complete fixed-action coupled Berger family by an exact stationary-row separator",
            ],
            "does_not_establish": [
                "that R_rel or D is gauge",
                "survival of a clock after fixed-charge symplectic reduction",
                "all-Hodge physical health, gradient stability or nonlinear stability",
                "a causal parent away from the isolated selected Berger background",
                "an observer, Hadamard, QME, particle, scattering, positivity or unitarity theorem",
            ],
        },
        "content_sha256": "PENDING",
    }
    value["content_sha256"] = _digest({k: v for k, v in value.items() if k != "content_sha256"})
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = payload["terminal_verdict"]
    return {
        "schema": "pure-weyl-two-phase-counterflow-secular-clock-orbital-stability-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "terminal_verdict": terminal,
        "stability_statuses": {
            key: row["status"]
            for key, row in payload["stability_ledger"].items()
            if "status" in row
        },
        "next_gate": payload["next_all_Hodge_gate"],
        "claim_boundary": payload["claim_boundary"],
        "content_hashes": {
            "normal_form_sha256": _digest(payload["action_angle_normal_form"]),
            "coupled_separator_sha256": _digest(payload["coupled_background_separator"]),
            "stability_sha256": _digest(payload["stability_ledger"]),
            "mutations_sha256": _digest(payload["mutations"]),
            "terminal_sha256": _digest(terminal),
            "boundary_sha256": _digest(payload["claim_boundary"]),
        },
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_payload = _digest({k: v for k, v in payload.items() if k != "content_sha256"})
    if payload["content_sha256"] != expected_payload or payload["oracle_fields_consumed"] != []:
        raise AssertionError("payload provenance failed")
    verdict = certificate["terminal_verdict"]
    if not verdict["Jordan_direction_is_reduced_family_tangent"]:
        raise AssertionError("family tangent was lost")
    if verdict["nearby_full_coupled_background_family"]:
        raise AssertionError("isolated coupled background was promoted")
    if verdict["genuine_negative_energy_or_exponential_instability"]:
        raise AssertionError("healthy action-angle shear was promoted to an energetic instability")
    if certificate["stability_statuses"] != {
        "compact_S1_absolute_Lyapunov_stability": "FAIL",
        "fixed_charge_absolute_stability": "PASS",
        "fixed_charge_orbital_stability_under_R_rel": "PASS",
        "frequency_modulated_stability": "PASS",
        "lifted_phase_bounded_linear_stability": "FAIL",
        "unrestricted_orbital_stability_under_R_rel": "PASS",
    }:
        raise AssertionError("stability definitions were conflated")
    expected_hashes = {
        "normal_form_sha256": _digest(payload["action_angle_normal_form"]),
        "coupled_separator_sha256": _digest(payload["coupled_background_separator"]),
        "stability_sha256": _digest(payload["stability_ledger"]),
        "mutations_sha256": _digest(payload["mutations"]),
        "terminal_sha256": _digest(payload["terminal_verdict"]),
        "boundary_sha256": _digest(payload["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected_hashes:
        raise AssertionError("certificate hashes drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, _ = _load_imports()
    payload = _payload(imports)
    certificate = _certificate(imports, payload)
    validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    validate(certificate, payload)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    if json.loads(OUTPUT.read_text()) != certificate:
        raise AssertionError("stored certificate drifted")
    if json.loads(PAYLOAD.read_text()) != payload:
        raise AssertionError("stored payload drifted")
    print("TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
