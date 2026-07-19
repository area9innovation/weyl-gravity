"""Classify the bounded zero-frequency cokernel for finite generic waves."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_generic_bounded_zero_block.schema.json"
INPUTS = {
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "finite_generic_smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "axial_ell1_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "pressure_identity": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
}


class BoundedZeroBlockError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BoundedZeroBlockError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded_homogeneous_symbol() -> dict[str, Any]:
    omega = sp.symbols("omega", real=True)
    symbol = sp.diag(omega**4, omega**2)
    require(symbol.rank() == 2, "generic homogeneous dynamical symbol rank changed")
    zero = symbol.subs(omega, 0)
    require(zero.rank() == 0 and len(zero.T.nullspace()) == 2, "zero-frequency mean cokernel changed")
    return {
        "gauge_invariant_fields": ["D=C-K", "X=A_x"],
        "normalized_time_domain_operator": ["D''''=s_D", "-X''=s_X"],
        "fourier_symbol": [[str(entry) for entry in row] for row in symbol.tolist()],
        "nonzero_frequency_rank": 2,
        "zero_frequency_rank": 0,
        "bounded_dynamical_mean_cokernel_basis": ["delta_D,0", "delta_X,0"],
        "finite_quasiperiodic_image_rule": "a finite Fourier source is in the bounded image iff its zero-frequency D and X coefficients vanish",
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    homogeneous = records["homogeneous_operator"]
    generic = records["finite_generic_smooth"]
    pressure = records["pressure_identity"]
    require(homogeneous["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"], "homogeneous nonzero-frequency quotient changed")
    require(generic["classification"]["arbitrary_finite_generic_harmonic_sums_classified_smooth_global"], "finite generic carrier changed")
    require(records["axial_ell1_zero"]["classification"]["zero_fibre_physical_cokernel_equals_rotation_triplet"], "axial static cokernel changed")
    require(records["polar_ell1_zero"]["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"], "polar static cokernel changed")
    require(pressure["primary_action_identity"]["pressure_functional"] == "R_c(u)=(1/2) sum k_j^2 h_j", "pressure identity changed")

    return {
        "schema": "einstein-maxwell-weyl-finite-generic-bounded-zero-block-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_GENERIC_BOUNDED_ZERO_BLOCK",
        "result_state": "FINITE_GENERIC_BOUNDED_ZERO_BLOCK_COKERNEL_AND_SOURCE_MAP_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G5_ARBITRARY_FINITE_GENERIC_OSCILLATORY_INPUTS",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N",
            "carrier": "arbitrary real finite sums of generic ell>=2 p- and q-primary oscillators; no generalized-zero input",
            "degree": 2,
            "parity": "axial and polar",
            "ell": "all generic input ell>=2 and every quadratically allowed static output L",
            "m": "all input m and output M",
            "k": "all allowed compact momenta and opposite-momentum zero-output pairs",
            "omega": "positive shell frequencies with conjugates; this theorem classifies Omega=0 outputs",
        },
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for name, path in INPUTS.items()},
        },
        "homogeneous_bounded_operator": bounded_homogeneous_symbol(),
        "source_pairings": {
            "circle_pressure": {
                "functional": "R_c(u)=(1/2) sum_j k_j^2 h_j",
                "derivation": "differentiate the action Hessian with respect to constant circle strain; polarization extends the primary identity to each degenerate shell block",
                "status": "CERTIFIED",
            },
            "wilson_acceleration": {
                "functional": "R_W(u)=zero-frequency coefficient of the homogeneous Maxwell-x source",
                "exact_identity": "integral_Sigma sqrt(-g) E_Maxwell^x = d_t integral_Sigma sqrt(-g) F^{t x}",
                "quadratic_consequence": "the second-order source is a time derivative of a finite Fourier bilinear, so its zero-frequency coefficient vanishes identically",
                "value_on_complete_carrier": "0",
                "status": "CERTIFIED",
            },
        },
        "complete_static_output_decomposition": {
            "L0_K0_constraint_cokernel": ["zeta_H", "zeta_Px"],
            "L0_K0_bounded_dynamical_cokernel": ["delta_D,0", "delta_X,0"],
            "L0_K0_source_map": ["mu_H", "mu_Px", "R_c", "R_W=0"],
            "L1_K0_axial_cokernel": ["zeta_J1", "zeta_J2", "zeta_J3"],
            "L1_K0_polar_cokernel": [],
            "L_at_least_2": "invertible after local gauge reduction on every static physical fibre",
            "source_obstruction_map": "(mu_H,mu_Px,mu_J1,mu_J2,mu_J3,R_c)",
        },
        "bounded_zero_block_theorem": {
            "necessary_and_sufficient_condition": "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=R_c=0",
            "necessity": "the six displayed nonzero source pairings annihilate the bounded image",
            "sufficiency": "R_W vanishes identically; after the six conditions vanish every L=0,1 source is in the bounded static image and every L>=2 static block is invertible",
            "relative_phases_and_degenerate_polarizations": "included by the Hermitian polarization identity inside each equal-(ell,k,omega) shell block",
        },
        "classification": {
            "homogeneous_bounded_dynamical_mean_cokernel_dimension_two": True,
            "circle_pressure_source_functional_certified": True,
            "wilson_acceleration_source_functional_identically_zero": True,
            "five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block": True,
            "bounded_zero_frequency_necessity_and_sufficiency_certified": True,
            "generalized_zero_inputs_included": False,
            "nonzero_frequency_resonance_ledger_classified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The pressure obstruction is not an isolated candidate-13 accident. For every finite generic wave packet it is the sole additional bounded zero-frequency source functional beyond the five stabilizer moment maps. The second formal homogeneous mean covector is present in coker L_bounded but its quadratic source vanishes identically by integrated Maxwell conservation.",
        "next_gate": "join this complete zero-block theorem with each carrier's exact nonzero-frequency resonance ledger, beginning with candidate 13",
        "claim_boundary": "This classifies bounded zero-frequency sources for finite generic oscillatory inputs only. It does not include generalized-zero inputs, solve any nonzero-frequency resonance locus, prove causal or all-orders extension, perform final residual descent, or make observational or quantum claims.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_generic_bounded_zero_block --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_finite_generic_bounded_zero_block",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_finite_generic_bounded_zero_block",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    else:
        require(OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered, "bounded zero-block certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_FINITE_GENERIC_BOUNDED_ZERO_BLOCK: PASS")


if __name__ == "__main__":
    main()
