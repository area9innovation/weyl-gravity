#!/usr/bin/env python3
"""Generate the standalone positive-Berger local receiver BV cocycle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1_PAYLOAD.json"
CONTRACT = P / "generated/POSITIVE_BERGER_LOCAL_RECEIVER_BV_INTEGRATION_CONTRACT_V1.json"
CERTIFICATE = P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json"
REPORT = P / "reports/positive-berger-local-receiver-action-preflight-v1.md"

DEPENDENCIES = {
    "terminal_nonactivation": P / "certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json",
    "typed_request": ROOT / "planning/forge-requests/positive-berger-action-derived-local-receiver-bv-cocycle.json",
    "apparatus_parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "apparatus_parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "detector_records": P / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "exact_profiles": P / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "positive_clock_background": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def physical_fields() -> list[dict[str, Any]]:
    rows = []
    for family, role in (
        ("X", "rod_orientation"),
        ("Y", "rod_momentum"),
        ("P", "detector_polarization"),
        ("N", "polarization_momentum"),
    ):
        for component in range(2):
            rows.append(
                {
                    "name": f"{family}{component}",
                    "role": role,
                    "component": component,
                    "bv_degree": 0,
                    "form_degree": 0,
                    "parity": "even",
                    "real_structure": "fixed",
                    "phase_representation": "real_U1_doublet",
                }
            )
    for name, role in (("m", "persistent_memory"), ("lambda", "memory_multiplier")):
        rows.append(
            {
                "name": name,
                "role": role,
                "component": None,
                "bv_degree": 0,
                "form_degree": 0,
                "parity": "even",
                "real_structure": "fixed",
                "phase_representation": "trivial",
            }
        )
    return rows


def antifields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "name": f"{row['name']}_plus",
            "dual_of": row["name"],
            "role": f"BV_dual_of_{row['role']}",
            "bv_degree": -1,
            "form_degree": 4,
            "parity": "odd",
            "real_structure": "fixed",
            "phase_representation": row["phase_representation"],
        }
        for row in fields
    ]


def build_payload() -> dict[str, Any]:
    fields = physical_fields()
    duals = antifields(fields)
    names = [row["name"] for row in fields]
    pairing_entries = []
    for index, name in enumerate(names):
        pairing_entries.extend(
            [
                {"left": name, "right": f"{name}_plus", "coefficient": 1},
                {"left": f"{name}_plus", "right": name, "coefficient": -1},
            ]
        )

    q1 = {
        "X0_plus": "-K(Y0) vol_0",
        "X1_plus": "-K(Y1) vol_0",
        "Y0_plus": "K(X0) vol_0",
        "Y1_plus": "K(X1) vol_0",
        "P0_plus": "-K(N0) vol_0",
        "P1_plus": "-K(N1) vol_0",
        "N0_plus": "K(P0) vol_0",
        "N1_plus": "K(P1) vol_0",
        "m_plus": "-u(lambda) vol_0",
        "lambda_plus": "u(m) vol_0",
    }

    return {
        "schema": "positive-berger-local-receiver-action-preflight-payload-v1",
        "result_id": "POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1_PAYLOAD",
        "coefficient_field": "Q[Omega_K]",
        "scope": {
            "theory": "standalone_first_order_Berger_D0_apparatus_BV_sector",
            "background": "positive_Berger_clock_Theta=3t/4",
            "boundaries": "compactly_supported_perturbations_in_interior_of_W0",
            "charge_sector": "unrestricted_local_apparatus_charge_fibre",
            "carrier": "one_detector_rod_polarization_memory_odd_cotangent_carrier",
            "degree": [-1, 0],
            "parity": ["odd", "even"],
            "ell": "NOT_APPLICABLE",
            "m": "NOT_APPLICABLE",
            "k": "NOT_APPLICABLE",
            "omega": "formal_real_clock_frequency",
        },
        "worldtube": {
            "id": "W0",
            "detector_id": "D0",
            "physical_time_interval": ["11/48", "13/48"],
            "clock_interval": ["11/64", "13/64"],
            "clock_center": "3/16",
            "clock_map": "Theta(t)=3*t/4",
            "clock_rate_v": "3/4",
            "rod_center": ["1/4", "0", "0"],
            "rod_radius": "1/128",
            "rod_density": "rho_0(R)=B3(128*(R-c_0))*128^3/C_B3",
            "rod_density_properties": {
                "normalization": "integral rho_0 d^3R=1",
                "support": "|R-c_0|<1/128<1/64",
                "reality": "real_nonnegative",
            },
            "volume_form": "vol_0=dt wedge rho_0(R)d^3R",
            "spatial_current_form": "rho_0(R)d^3R=i_u vol_0",
            "support_class": "C_c^infinity(W0) BV sections and jets",
        },
        "master_action": {
            "formula": "S_W0=integral_W0 [Y dot KX + N dot KP + lambda*(u(m)-P dot F)] vol_0",
            "K_on_doublets": "K=u+Omega_K*J; J=[[0,-1],[1,0]]",
            "K_on_phase_scalars": "K=u",
            "signal_port": {
                "name": "F",
                "type": "external_real_U1_doublet_test_input",
                "bv_row": False,
                "background_value": [0, 0],
                "boundary": "not an external current and not called a dynamical emitter",
            },
            "variational_fields": names,
            "action_origin": "one-detector restriction of BERGER_DYNAMICAL_APPARATUS_PARENT with the emitter sector omitted",
        },
        "background_solution": {
            "t0": "1/4",
            "Theta": "3*t/4",
            "Xbar": "exp(-Omega_K*J*(t-t0))*X0",
            "Ybar": [0, 0],
            "Pbar": "exp(-Omega_K*J*(t-t0))*(1,0)",
            "Nbar": [0, 0],
            "mbar": 0,
            "lambda_bar": 0,
            "Fbar": [0, 0],
            "equation_residuals": {
                "K_Xbar": 0,
                "K_Pbar": 0,
                "K_Ybar": 0,
                "K_Nbar": 0,
                "u_mbar_minus_Pbar_dot_Fbar": 0,
                "u_lambda_bar": 0,
            },
            "external_current_used": False,
        },
        "carrier": {
            "physical_fields": fields,
            "antifields_and_bv_duals": duals,
            "physical_count": len(fields),
            "antifield_count": len(duals),
            "total_row_count": len(fields) + len(duals),
            "gauge_generators": [],
            "ghosts": [],
            "gauge_ledger": "EMPTY: phase R is rigid covariance, not gauge redundancy",
            "ghost_ledger": "EMPTY: no gauge generator exists in the standalone apparatus action",
        },
        "odd_pairing": {
            "formula": "omega_BV=integral_W0 sum_phi delta(phi) wedge delta(phi_plus)",
            "ordered_rows": names + [f"{name}_plus" for name in names],
            "entries": pairing_entries,
            "shape": [20, 20],
            "rank": 20,
            "degree": -1,
        },
        "q1": {
            "degree": 1,
            "on_physical_fields": "zero",
            "on_antifields": q1,
            "apparatus_only_linearization": "F=0; the signal derivative is an integration input, not an apparatus q1 row",
            "derivation": "odd Hamiltonian vector field of the quadratic master action at the displayed background",
            "q1_squared": 0,
            "formal_cyclicity_defect": 0,
            "real_structure_defect": 0,
        },
        "receiver_cocycle": {
            "name": "memory_shift_receiver_descent",
            "A": "m_plus",
            "A_bv_degree": -1,
            "A_form_degree": 4,
            "B": "lambda*rho_0(R)d^3R",
            "B_bv_degree": 0,
            "B_form_degree": 3,
            "sA": "-u(lambda)*vol_0",
            "dB": "u(lambda)*vol_0",
            "identity": "sA+dB=0",
            "identity_defect": 0,
            "support": "support(A) union support(B) compactly contained in W0",
            "nontriviality": {
                "minimum_carrier_bv_degree": -1,
                "degree_minus_two_generator_count": 0,
                "Euler_derivative_of_A_with_respect_to_m_plus": 1,
                "conclusion": "A is neither s-exact nor a horizontal total derivative in the declared local polynomial carrier",
            },
            "operational_role": "BV receiver row dual to the persistent-memory shift equation; not the memory value itself",
        },
        "symmetry_actions": {
            "phase_generator": "R",
            "raw_generator": "D",
            "helical_generator": "K=D-vR",
            "v": "3/4",
            "on_Theta": {"D": "3/4", "R": 1, "K": 0},
            "on_doublets_and_duals": {
                "R": "J",
                "D": "u+(Omega_K+3/4)*J",
                "K": "u+Omega_K*J",
            },
            "on_m_lambda_and_duals": {"R": 0, "D": "u", "K": "u"},
            "on_signal_port_F": {
                "R": "J",
                "D": "u+(Omega_K+3/4)*J",
                "K": "u+Omega_K*J",
            },
            "support_action": "D,R,K act on the transported family of W0 fibres; no fixed-fibre invariance is asserted",
            "q1_commutator_defects": {"D": 0, "R": 0, "K": 0},
            "pairing_variation_defects": {"D": 0, "R": 0, "K": 0},
        },
        "distinguishing_mutations": {
            "delete_action_origin": {
                "mutation": "remove lambda*u(m)",
                "mutated_sA": 0,
                "mutated_dB": "u(lambda)*vol_0",
                "rejected": True,
            },
            "flip_descent_sign": {
                "mutation": "B -> -B",
                "mutated_defect": "-2*u(lambda)*vol_0",
                "rejected": True,
            },
            "delete_support_declaration": {
                "mutated_support_status": "NO_CERTIFIED_MAP",
                "rejected": True,
            },
            "delete_phase_action": {
                "mutated_K_decomposition": "undefined",
                "rejected": True,
            },
            "probe_smearing_substitution": {
                "candidate": "Q_0[F]",
                "failure": "external functional; no BV row, odd dual or action-derived descent",
                "rejected": True,
            },
            "advanced_covector_substitution": {
                "candidate": "dG_adv^* Q_0",
                "failure": "advanced preparation covector; not a variational apparatus field",
                "rejected": True,
            },
            "persistent_register_substitution": {
                "candidate": "m",
                "failure": "degree-zero record with descent length zero; distinct from A=m_plus and B=lambda*rho_0 d^3R",
                "rejected": True,
            },
        },
        "exact_identities": {
            "background_equation_defect": 0,
            "q1_squared": 0,
            "odd_pairing_rank": 20,
            "formal_cyclicity_defect": 0,
            "receiver_cocycle_defect": 0,
            "D_minus_vR_minus_K_defect": 0,
        },
        "claim_boundary": {
            "establishes": [
                "standalone action-derived local receiver BV cocycle",
                "exact D0 support and positive-Berger clock labelling",
                "nilpotent cyclic unary apparatus complex",
                "raw-D, phase-R and helical-K actions",
            ],
            "does_not_establish": [
                "ambient gravity-clock q70 inclusion",
                "residual quotient or nonradical period",
                "frequency denominator or relational redshift",
                "nonlinear response, recoil, particle or quantum result",
            ],
        },
    }


def build_contract(payload: dict[str, Any]) -> dict[str, Any]:
    components = {
        key: canonical_sha(payload[key])
        for key in (
            "scope",
            "worldtube",
            "master_action",
            "background_solution",
            "carrier",
            "odd_pairing",
            "q1",
            "receiver_cocycle",
            "symmetry_actions",
        )
    }
    contract_core = {
        "schema": "positive-berger-local-receiver-bv-integration-contract-v1",
        "result_id": "POSITIVE_BERGER_LOCAL_RECEIVER_BV_INTEGRATION_CONTRACT_V1",
        "source_result_id": payload["result_id"],
        "component_sha256": components,
        "required_parent_inputs": {
            "repaired_parent_q1_and_row_dictionary": "NO_CERTIFIED_MAP",
            "repaired_parent_odd_pairing": "NO_CERTIFIED_MAP",
            "same_background_row_embedding": "NO_CERTIFIED_MAP",
            "worldtube_support_embedding": "NO_CERTIFIED_MAP",
            "D_R_K_intertwiners": "NO_CERTIFIED_MAP",
            "signal_port_to_parent_field_map": "NO_CERTIFIED_MAP",
        },
        "acceptance_tests": [
            "injective degree/parity/real row map for all 20 apparatus rows",
            "q_parent i = i q_apparatus",
            "pullback of parent odd pairing equals the rank-20 apparatus pairing",
            "support map lands in the same positive-Berger D0 worldtube",
            "D, R and K intertwiners commute and K=D-(3/4)R",
            "image of A,B preserves sA+dB=0 exactly",
        ],
        "downstream_status": {
            "ambient_unary_inclusion": "NO_CERTIFIED_MAP",
            "receiver_residual_quotient": "NO_CERTIFIED_MAP",
            "nonradical_pairing_period": "NO_CERTIFIED_MAP",
            "frequency_denominator": "NO_CERTIFIED_MAP",
            "relational_redshift": "NO_CERTIFIED_MAP",
        },
        "fail_closed": True,
    }
    return {**contract_core, "contract_sha256": canonical_sha(contract_core)}


def build_certificate(payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    payload_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    contract_bytes = (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode()
    refs = {}
    for name, path in DEPENDENCIES.items():
        data = json.loads(path.read_text())
        refs[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": data.get("result_id", data.get("id")),
            "sha256": sha256(path),
        }
    return {
        "schema": "positive-berger-local-receiver-action-preflight-v1",
        "result_id": "POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1",
        "setting_id": "compact_positive_berger_D0_local_receiver_worldtube",
        "claim_status": "CERTIFIED_STANDALONE_ACTION_DERIVED_LOCAL_RECEIVER_BV_COCYCLE",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_bytes).hexdigest(),
        },
        "integration_contract_ref": {
            "path": str(CONTRACT.relative_to(ROOT)),
            "result_id": contract["result_id"],
            "sha256": hashlib.sha256(contract_bytes).hexdigest(),
            "contract_sha256": contract["contract_sha256"],
        },
        "gate_results": {
            "declared_master_action": "CERTIFIED",
            "background_equations_without_external_current": "CERTIFIED",
            "complete_field_ghost_antifield_inventory": "CERTIFIED",
            "q1_nilpotency": "CERTIFIED",
            "odd_pairing_cyclicity": "CERTIFIED",
            "compact_local_receiver_descent": "CERTIFIED",
            "raw_D_phase_R_helical_K_actions": "CERTIFIED",
            "ambient_q70_inclusion": "NO_CERTIFIED_MAP",
        },
        "receiver_result": {
            "A": payload["receiver_cocycle"]["A"],
            "B": payload["receiver_cocycle"]["B"],
            "identity": payload["receiver_cocycle"]["identity"],
            "support": payload["receiver_cocycle"]["support"],
            "nontriviality": "CERTIFIED_IN_DECLARED_LOCAL_POLYNOMIAL_CARRIER",
        },
        "downstream_disposition": contract["downstream_status"],
        "next_gate": "INTEGRATE_THE_CONTENT_ADDRESSED_20_ROW_RECEIVER_SECTOR_INTO_A_REPAIRED_SAME_BACKGROUND_PARENT",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight restricts the certified dynamical apparatus action to one positive-Berger D0 rod/polarization/memory worldtube. Ten real even fields and their ten odd BV cotangents form a rank-20 odd-paired Koszul-Tate complex; the rigid phase action is not gauge, so the complete gauge and ghost ledgers are empty. The displayed transported background solves every apparatus equation with F=0 and no external current. The action-derived unary differential is nilpotent and cyclic. The memory-shift descent A=m_plus, B=lambda*rho_0 d^3R has exact compact-worldtube identity sA+dB=0 and is nontrivial in the declared local polynomial carrier. Raw D, phase R and K=D-(3/4)R are serialized separately. Mutations distinguish this row from the probe smearing, advanced covector and persistent register. The signal F is only an external test-input port and is not promoted to a dynamical emitter. The content-addressed integration contract remains fail-closed: there is no claim of inclusion into an ambient gravity-clock parent, residual quotient, nonradical period, denominator, redshift, nonlinear response, recoil, particle or quantum result."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_positive_berger_local_receiver_action_preflight --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_positive_berger_local_receiver_action_preflight",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Positive-Berger local receiver action preflight

The smallest action-consistent sector is one D0 rod/polarization/memory
apparatus: ten real even fields and ten odd BV cotangents.  The phase U(1)
is rigid, so there are no gauge generators or ghosts.  A transported
positive-Berger background solves the apparatus equations at zero signal
without an external current.

The first-order memory term `lambda*u(m)` supplies the receiver descent.
For compactly supported BV sections in the exact D0 worldtube,

`A=m_plus`, `B=lambda*rho_0(R)d^3R`, and `sA+dB=0`.

This is not the persistent register `m`: it is the degree-minus-one BV row
dual to the memory shift equation, with a nonzero descent partner.  Probe
smearings and advanced covectors have no apparatus BV row or action origin.
The exact unary and odd-pairing checks pass, as do the separate raw-D,
phase-R and `K=D-(3/4)R` actions.

The integration contract deliberately leaves ambient parent inclusion,
residual quotient, period, denominator and redshift as `NO_CERTIFIED_MAP`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    contract = build_contract(payload)
    certificate = build_certificate(payload, contract)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CONTRACT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    else:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
