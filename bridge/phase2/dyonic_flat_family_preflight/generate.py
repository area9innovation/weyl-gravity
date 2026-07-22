#!/usr/bin/env python3
"""Exact fixed-Chern dyonic flat-product preflight.

The local Einstein--Maxwell/Weyl--Maxwell incidence admits a rational dyonic
family with flat Lorentzian factor.  On the compact spatial circle, however,
the electric field makes the connection holonomy evolve.  Thus time
translation preserves the metric and field strength but has no infinitesimal
global bundle lift when E is nonzero.  The same fixed-Chern global carrier also
rejects the parameter-dependent duality reflection that would restore the
background after spherical parity.

This producer certifies those exact statements and stops before constructing
any tangent cofiber, Lee--Wald current, or sign diagram.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "DYONIC_FLAT_FAMILY_PREFLIGHT_V1.json"
ATLAS = ROOT / "residual_atlas/phase2-sign-dyonic-flat-family-preflight-fragment-v1.json"
SCHEMA = HERE / "dyonic-flat-family-preflight-v1.schema.json"
PRODUCER = Path(__file__).resolve()
VERIFIER = HERE / "verify.py"
TESTS = HERE / "tests/test_dyonic_flat_family_preflight.py"

INPUTS = {
    "product_incidence": (
        ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
        "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
        "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
    ),
    "phase1_bridge_freeze": (
        ROOT / "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json",
        "7c045d4bde9e3961ad422faa0e6f8ca4d22cde76970e6071ca7a9bff392666d3",
        "BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1",
    ),
}


class DyonicFlatFamilyPreflightError(RuntimeError):
    """Raised when an exact preflight invariant fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DyonicFlatFamilyPreflightError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _import_gate() -> list[dict[str, str]]:
    imports: list[dict[str, str]] = []
    for name, (path, expected_hash, result_id) in INPUTS.items():
        _require(path.exists(), f"missing input: {path}")
        actual_hash = _sha256(path)
        _require(actual_hash == expected_hash, f"input hash drift: {name}")
        payload = _load(path)
        _require(payload.get("result_id") == result_id, f"result-id drift: {name}")
        imports.append(
            {
                "name": name,
                "path": str(path.relative_to(ROOT)),
                "result_id": result_id,
                "sha256": actual_hash,
            }
        )
    return imports


def exact_family() -> dict[str, Any]:
    tau, kappa, n, q = sp.symbols("tau kappa N q_min", real=True)
    beta = sp.factor(kappa * n**2 / (4 * q**2))
    alpha_critical = sp.factor(3 * n**2 / (4 * q**2))
    k_2 = sp.factor(1 / (beta * (1 + tau**2)))
    magnetic = sp.factor(n * k_2 / (2 * q))
    electric = sp.factor(tau * magnetic)
    alpha_b = sp.factor(3 / (kappa * k_2))
    electric_charge = sp.factor(electric / k_2)

    _require(
        sp.factor(electric**2 + magnetic**2 - k_2 / kappa) == 0,
        "Einstein-Maxwell energy incidence failed",
    )
    _require(
        sp.factor(alpha_b * kappa * k_2 - 3) == 0,
        "Weyl-Maxwell coupling incidence failed",
    )
    _require(
        sp.factor(alpha_b - alpha_critical * (1 + tau**2)) == 0,
        "critical-coupling parameterization failed",
    )
    _require(
        sp.factor(2 * q * magnetic / k_2 - n) == 0,
        "Chern quantization failed",
    )
    _require(
        sp.factor(electric_charge - n * tau / (2 * q)) == 0,
        "electric-charge normalization failed",
    )

    fixture = {n: 2, q: 1, kappa: 1}
    fixture_values = tuple(
        sp.factor(value.subs(fixture)) for value in (k_2, alpha_b, magnetic, electric)
    )
    expected_fixture = (
        1 / (1 + tau**2),
        3 * (1 + tau**2),
        1 / (1 + tau**2),
        tau / (1 + tau**2),
    )
    _require(
        all(sp.simplify(actual - expected) == 0 for actual, expected in zip(fixture_values, expected_fixture)),
        "unit normalization fixture failed",
    )

    return {
        "parameter_domain": "tau=E/P is real; the oriented branch tau>=0 is used for the phase diagram; N is a fixed nonzero integer; q_min,kappa,L>0",
        "beta": str(beta),
        "alpha_critical": str(alpha_critical),
        "k_1": "0",
        "k_2": str(k_2),
        "P": str(magnetic),
        "E": str(electric),
        "alpha_B": str(alpha_b),
        "Lambda": str(sp.factor(k_2 / 2)),
        "electric_charge_Qe": str(electric_charge),
        "electric_charge_convention": "Q_e=(1/(4*pi))*integral_S2 star F=E/k_2 for the declared orientation",
        "magnetic_chern_relation": "(q_min/(2*pi))*integral_S2 F=N",
        "fixed_coupling_open_family": False,
        "family_type": "COUPLING_BACKGROUND_FAMILY",
        "unit_fixture": {
            "N": 2,
            "q_min": 1,
            "kappa": 1,
            "k_2": "1/(tau**2 + 1)",
            "alpha_B": "3*tau**2 + 3",
            "P": "1/(tau**2 + 1)",
            "E": "tau/(tau**2 + 1)",
            "pure_magnetic_endpoint": "tau=0",
        },
    }


def exact_connection_and_symmetry() -> dict[str, Any]:
    tau = sp.symbols("tau", real=True)
    denominator = 1 + tau**2
    spherical_parity = sp.diag(1, -1)
    charge_conjugation = -sp.eye(2)
    duality = sp.Matrix(
        [
            [(tau**2 - 1) / denominator, -2 * tau / denominator],
            [2 * tau / denominator, (tau**2 - 1) / denominator],
        ]
    )
    combined = sp.simplify(duality * spherical_parity)
    background_charge = sp.Matrix([tau, 1])
    fixed_chern_electric_tangent = sp.Matrix([1, 0])

    _require(sp.simplify(combined * background_charge - background_charge) == sp.zeros(2, 1), "combined parity does not fix background")
    _require(sp.simplify(combined * combined - sp.eye(2)) == sp.zeros(2), "combined parity is not involutive")
    _require(sp.factor(combined.det() + 1) == 0, "combined parity determinant changed")
    transformed_tangent = sp.simplify(combined * fixed_chern_electric_tangent)
    _require(
        sp.factor(transformed_tangent[1] - 2 * tau / denominator) == 0,
        "fixed-Chern tangent defect changed",
    )
    _require(combined.subs(tau, 0) == charge_conjugation * spherical_parity, "pure-magnetic parity limit changed")

    return {
        "geometry": {
            "spacetime": "R_t x S1_L x S2(k_2)",
            "metric": "-dt^2+dx^2+k_2^(-1)(dtheta^2+sin(theta)^2 dphi^2)",
            "field_strength": "F=E dt wedge dx+P k_2^(-1) sin(theta) dtheta wedge dphi",
            "compact_cauchy_surface": "S1_L x S2",
            "global_vector_field_H": "partial_t",
            "global_metric_killing_H": True,
            "field_strength_invariant_under_H": True,
        },
        "bundle_connection": {
            "north_patch": "A_N=E t dx+(P/k_2)(1-cos(theta))dphi",
            "south_patch": "A_S=E t dx-(P/k_2)(1+cos(theta))dphi",
            "transition": "A_N-A_S=(N/q_min)dphi",
            "fixed_bundle": "P_N with N fixed and nonzero",
            "electric_charge_policy": "Q_e labels the background and is not topological; electric tangents are allowed unless a downstream fixed-Q_e carrier is separately declared",
        },
        "stabilizer_lifts": {
            "P_x": "global lift (partial_x,chi=0)",
            "sphere_rotations": "for i=x,y,z, use chi_i=-(i_{J_i}A_patch)-(P/k_2)n_i; since i_{J_i}F=(P/k_2)dn_i, L_{J_i}A+dchi_i=0 patchwise and the lifts respect the monopole transition",
            "H": "NO_CONTINUOUS_GLOBAL_CONNECTION_LIFT_FOR_E_NONZERO",
            "H_obstruction": "L_H A=E dx. For every single-valued infinitesimal U(1) parameter chi, integral_S1 dchi=0, whereas integral_S1 E dx=E L. Thus L_H A+dchi cannot vanish when E!=0.",
            "finite_time_remark": "A large gauge transformation can compensate only isolated time shifts satisfying q_min E L Delta_t in 2*pi*Z; this does not supply an infinitesimal H stabilizer.",
            "wilson_loop": "W_x(t)=exp(i q_min E L t) times the time-independent flat-holonomy factor",
            "pure_magnetic_endpoint": "at tau=0, E=0 and H has the lift (partial_t,chi=0)",
        },
        "parity_duality": {
            "charge_vector_order": ["E", "P"],
            "spherical_antipodal_parity": [["1", "0"], ["0", "-1"]],
            "charge_conjugation": [["-1", "0"], ["0", "-1"]],
            "background_vector_up_to_positive_scale": ["tau", "1"],
            "duality_rotation_restoring_background": [
                [str(sp.factor(duality[i, j])) for j in range(2)] for i in range(2)
            ],
            "combined_involution_D_tau_times_parity": [
                [str(sp.factor(combined[i, j])) for j in range(2)] for i in range(2)
            ],
            "combined_fixes_background": True,
            "combined_square_is_identity": True,
            "combined_determinant": "-1",
            "fixed_chern_electric_tangent": ["delta E", "0"],
            "transformed_magnetic_tangent_component": "2*tau*delta E/(tau**2+1)",
            "preserves_fixed_chern_tangent_for_tau_nonzero": False,
            "off_shell_single_potential_symmetry": False,
            "equation_level_duality_remark": "The source-free Maxwell equations and stress tensor admit the displayed SO(2) charge rotation, but it is not a local off-shell symmetry of the declared single-potential fixed-bundle action and it mixes allowed electric tangents into forbidden magnetic-Chern tangents.",
            "pure_magnetic_limit": "at tau=0 the combined involution is charge conjugation times spherical parity and the certified Phase-1 parity split may be recovered",
            "generic_disposition": "COMBINED_MIXED_PARITY_CARRIER_REQUIRED",
        },
    }


def build_certificate() -> dict[str, Any]:
    imports = _import_gate()
    family = exact_family()
    symmetry = exact_connection_and_symmetry()
    return {
        "schema": "dyonic-flat-family-preflight-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "DYONIC_FLAT_FAMILY_PREFLIGHT_V1",
        "result_state": "EXACT_LOCAL_FAMILY_CERTIFIED_GLOBAL_CONNECTION_STATIONARITY_OBSTRUCTED_MIXED_PARITY_REQUIRED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "declared_input_commit": "4a212883aefa5525cc847d0c12763c74c1c3411a",
            "implementation_base_commit": "1921878e20d1929a5ac2e6b882b8ae944622336d",
            "producer": str(PRODUCER.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER),
            "verifier": str(VERIFIER.relative_to(ROOT)),
            "verifier_sha256": _sha256(VERIFIER),
            "tests": str(TESTS.relative_to(ROOT)),
            "tests_sha256": _sha256(TESTS),
            "imported_artifacts": imports,
        },
        "scope": {
            "theory": "common Einstein-Maxwell and pure-Weyl-Maxwell background incidence",
            "background": "flat-factor dyonic R_t x S1_L x S2(k_2), parameter tau=E/P; coupling-background family, not fixed-alpha_B openness",
            "boundaries": "compact spatial circle and sphere; no asymptotic boundary",
            "charge_sector": "fixed nonzero magnetic Chern N; continuously varying background electric charge Q_e",
            "carrier": "background fields and exact symmetry preflight only",
            "degree": "background degree zero only",
            "parity": "generic tau requires a combined mixed-parity carrier; no split authorized",
            "ell": "not constructed",
            "m": "not constructed",
            "k": "not constructed",
            "omega": "not constructed",
        },
        "exact_family": family,
        "connection_and_symmetry": symmetry,
        "classification": {
            "exact_rational_local_background_family": True,
            "fixed_coupling_open_family": False,
            "global_metric_and_field_strength_stationary": True,
            "global_connection_stationary_for_tau_nonzero": False,
            "continuous_H_bundle_stabilizer_for_tau_nonzero": False,
            "ordinary_parity_preserves_dyonic_background": False,
            "equation_level_duality_reflection_fixes_background": True,
            "duality_reflection_preserves_fixed_chern_tangent": False,
            "generic_axial_polar_block_split_authorized": False,
            "combined_mixed_parity_carrier_required": True,
            "tangent_cofiber_constructed": False,
            "lee_wald_current_constructed": False,
            "sign_or_inertia_computed": False,
        },
        "next_gate": {
            "disposition": "OBSTRUCTED_AS_STATIONARY_FIXED_BUNDLE_SIGN_BASE",
            "reason": "For tau!=0, H has no continuous global lift to the compact-circle connection, and the only equation-level parity-duality involution fails to preserve the fixed-Chern tangent carrier.",
            "admissible_successors": [
                "enlarge to a duality-covariant two-potential/global charge lattice and re-audit the symplectic structure",
                "drop compact S1 and declare boundary conditions permitting the electric gauge compensator",
                "retain the compact fixed-bundle theory and use a nonstationary mixed-parity formulation without positive-frequency continuation",
            ],
        },
        "claim_flags": {
            "exact_background_incidence": True,
            "stationary_metric_field_strength": True,
            "stationary_global_connection": False,
            "positive_frequency_family_base": False,
            "axial_polar_family_split": False,
            "tangent_or_symplectic_claim": False,
            "sign_claim": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC preflight certifies the exact rational coupling-background incidence family and its bundle/charge conventions. It proves that for nonzero electric field on the compact spatial circle, time translation has no continuous global connection lift, and that the equation-level duality reflection restoring spherical parity does not preserve the fixed-Chern tangent carrier. It therefore obstructs this family as the proposed stationary positive-frequency sign-comparison base and requires a combined mixed-parity carrier in any nonstationary continuation. It constructs no tangent cofiber, Lee-Wald current, inertia, sign wall, causal evolution, observable, particle or quantum state.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.phase2.dyonic_flat_family_preflight.generate --check",
            "PYTHONPATH=. python3 -m bridge.phase2.dyonic_flat_family_preflight.verify",
            "PYTHONPATH=. python3 -m unittest bridge.phase2.dyonic_flat_family_preflight.tests.test_dyonic_flat_family_preflight",
            "python3 residual_atlas/validate_fragment.py residual_atlas/phase2-sign-dyonic-flat-family-preflight-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any], certificate_path: Path) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "phase2_sign",
        "generated_by": str(PRODUCER.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "phase2.sign.dyonic_flat_family.preflight",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "OBSTRUCTED",
                    "nonlinear": "OPEN",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "NO_CERTIFIED_MAP", "statement": "No dyonic tangent operator or harmonic shell is constructed."},
                    "lee_wald": {"status": "OBSTRUCTED", "statement": "The proposed stationary fixed-bundle positive-frequency comparison fails because H has no continuous global connection lift for tau!=0."},
                    "taub_maps": {"status": "NO_CERTIFIED_MAP", "statement": "No dyonic stabilizer moment map is defined."},
                    "resonance": {"status": "NO_CERTIFIED_MAP", "statement": "No dyonic source operator is defined."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "No tangent carrier exists yet."},
                        "smooth_secular": {"status": "OPEN", "statement": "No tangent carrier exists yet."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No causal complex is imported."},
                    },
                },
                "claim_boundary": certificate["claim_boundary"],
                "evidence": [
                    {
                        "path": str(certificate_path.relative_to(ROOT)),
                        "result_id": certificate["result_id"],
                        "sha256": _sha256(certificate_path),
                    }
                ],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def write_outputs() -> None:
    certificate = build_certificate()
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ATLAS.write_text(json.dumps(build_atlas(certificate, OUTPUT), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_outputs() -> None:
    expected = build_certificate()
    _require(_load(OUTPUT) == expected, f"stale certificate: {OUTPUT}")
    _require(_load(ATLAS) == build_atlas(expected, OUTPUT), f"stale atlas: {ATLAS}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
    if args.check:
        check_outputs()
    if not args.write and not args.check:
        print(json.dumps(build_certificate(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
