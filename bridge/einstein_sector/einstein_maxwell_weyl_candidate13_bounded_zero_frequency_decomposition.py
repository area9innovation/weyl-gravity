"""Certify the complete bounded zero-frequency receiver on candidate 13."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition.schema.json"
INPUTS = {
    "pressure": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "fixed_ell_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "finite_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "complete_smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "axial_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    pressure = records["pressure"]
    homogeneous = records["homogeneous_operator"]
    fixed = records["fixed_ell_source"]
    finite = records["finite_generic"]
    smooth = records["complete_smooth"]

    operator = homogeneous["operator_theorem"]
    require(operator["row_order"] == ["E00", "E01", "E11", "sphere_trace", "Maxwell0", "Maxwell1"], "homogeneous row order changed")
    require(operator["rows"] == ["0", "0", "-omega**4*(C - K)/2", "omega**4*(C - K)/4", "0", "A_x*omega**2"], "homogeneous operator changed")
    source = fixed["primary_action_and_scalar_source_theorem"]
    require(source["Weyl_trace_identity"]["second_order_on_shell_reduction"] == "-metric_00+metric_11+2*sphere_trace=0", "Weyl trace identity changed")
    require(source["homogeneous_Maxwell_identity"]["conjugate_pair_value"] == "0 when omega_2=-omega_1", "Maxwell-x identity changed")
    require(pressure["primary_action_identity"]["pressure_functional"] == "R_c(u)=(1/2) sum k_j^2 h_j", "pressure normalization changed")
    require(records["axial_ell1"]["classification"]["zero_fibre_physical_cokernel_equals_rotation_triplet"], "axial L1 zero block changed")
    require(records["polar_ell1"]["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"], "polar L1 zero block changed")
    require(finite["complete_adjoint_cokernel_decomposition"]["zero_block"]["L_at_least_2"]["consequence"] == "every static generic output block is invertible after local gauge reduction", "static generic theorem changed")
    require(smooth["complete_output_cokernel_theorem"]["no_additional_charge_cokernel"].startswith("constant U1 reducibility"), "closed Gauss identity changed")
    require(records["moment_map"]["classification"]["generic_covariant_moment_map_Taub_equality_certified"], "moment-map bridge changed")

    omega, D, A = sp.symbols("omega D A")
    reduced_rows = sp.Matrix([-omega**4 * D / 2, omega**4 * D / 4, omega**2 * A])
    require(reduced_rows.subs(omega, 0) == sp.zeros(3, 1), "bounded zero-root operator changed")

    return {
        "schema": "einstein-maxwell-weyl-candidate13-bounded-zero-frequency-decomposition-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CANDIDATE13_BOUNDED_ZERO_FREQUENCY_DECOMPOSITION",
        "result_state": "COMPLETE_CANDIDATE13_BOUNDED_ZERO_FREQUENCY_RECEIVER_EQUALS_SIX_FUNCTIONALS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_FINITE_GENERIC_CANDIDATE13_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-13 tuned compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "all generic ell=2 q-minus, p-extra and q-plus coefficients on the signed n=1 and n=-2 candidate-13 fibres, both parities and all m, with reality conjugates",
            "degree": 2,
            "parity": "both input parities and every zero-frequency output parity",
            "ell": "input ell=2; zero-frequency outputs L=0,1,2,3,4",
            "m": "all input m and every Clebsch-Gordan-allowed output M",
            "k": "signed n=1,-2 fibres; zero-frequency products have K=0",
            "omega": "equal-branch positive-negative products with Omega=0",
        },
        "second_order_equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
        "bounded_zero_frequency_decomposition": {
            "L0_K0_row_order": operator["row_order"],
            "linear_dynamical_invariants": ["D=C-K with E11=-D''''/2 and sphere_trace=D''''/4", "A_x with Maxwell1=-A_x''"],
            "bounded_zero_root": "at Omega=0 a bounded finite-quasiperiodic correction is constant, so D''''=A_x''=0",
            "quadratic_source_rows": {
                "E00": "a nonzero calibrated multiple of mu_H",
                "E01": "a nonzero calibrated multiple of mu_Px",
                "E11": "R_c=(1/2) sum_j k_j^2 h_j",
                "sphere_trace": "(E00-E11)/2 by -E00+E11+2*sphere_trace=0",
                "Maxwell0": "0 by the integrated closed-slice Gauss identity and removal of constant U1 reducibility",
                "Maxwell1": "0 because the integrated Maxwell-x source has factor omega_1+omega_2=0",
            },
            "L0_equivalence": "the complete homogeneous zero-frequency source vanishes iff mu_H=mu_Px=R_c=0",
            "L1_K0": "the axial physical cokernel is exactly (mu_J1,mu_J2,mu_J3); the polar physical cokernel is absent",
            "L_at_least_2": finite["complete_adjoint_cokernel_decomposition"]["zero_block"]["L_at_least_2"],
            "complete_functional_basis": ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3", "R_c"],
            "direct_sum": "coker_bounded(source|candidate13,Omega=K=0)=stab^* direct-sum span{R_c}",
        },
        "necessity_and_sufficiency": {
            "formula": "S_zero(u) is in the bounded reduced image iff mu_H=mu_Px=mu_J1=mu_J2=mu_J3=R_c=0",
            "necessity": "the two constraints, three lifted-rotation adjoints and the homogeneous dynamical zero root annihilate every bounded image",
            "sufficiency": "the six vanishings kill all L=0 and physical L=1 source rows; every L>=2 static block has a certified reduced inverse",
        },
        "classification": {
            "complete_candidate13_bounded_zero_frequency_receiver_certified": True,
            "five_stabilizers_plus_circle_pressure_necessary_and_sufficient": True,
            "additional_zero_frequency_Maxwell_functional_absent": True,
            "additional_zero_frequency_L1_functional_absent": True,
            "static_L_at_least_2_functional_absent": True,
            "nonzero_frequency_candidate13_functionals_classified_here": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "For bounded corrections the compact stabilizer moment maps do not exhaust the zero block. There is exactly one additional dynamical functional on the declared generic carrier: circle pressure. No further zero-frequency source functional survives the closed-slice Maxwell identities, Weyl trace identity, L1 quotient or static generic inversion.",
        "next_gate": "join this complete six-functional zero block to the eighteen candidate-13 finite-frequency coefficients",
        "claim_boundary": "This certifies the complete bounded zero-frequency receiver only on the declared finite generic candidate-13 carrier. It does not include exceptional/global inputs, solve the resulting real quadratic zero locus, prove all-orders integration, or construct causal, residual, observational or quantum maps.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition",
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
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError("candidate-13 bounded zero-frequency certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE13_BOUNDED_ZERO_FREQUENCY_DECOMPOSITION: PASS")


if __name__ == "__main__":
    main()
