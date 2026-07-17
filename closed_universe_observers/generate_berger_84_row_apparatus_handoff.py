#!/usr/bin/env python3
"""Generate the authoritative forward contract for the 84-row apparatus."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp

from closed_universe_observers import generate_berger_global_rod_q1_solvability as rod_q1


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_84_row_apparatus_handoff_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-84-row-apparatus-handoff-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-84-row-apparatus-handoff-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json"
REPORT = PACKAGE / "reports/berger-84-row-observer-apparatus-handoff.md"

DEPENDENCIES = {
    "global_rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_q1_solvability": PACKAGE / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json",
    "legacy_observer_interface": PACKAGE / "certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json",
    "base_64_carrier": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "base_64_causal": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "base_64_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "base_64_k_cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
    "retained_observer_k_gate": PACKAGE / "certificates/BERGER_RETAINED_OBSERVER_K_DESCENT_GATE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_84_row_apparatus_handoff.py",
    "tests": PACKAGE / "tests/test_berger_84_row_apparatus_handoff.py",
    "report": REPORT,
    "declared_input": INPUT,
    "input_schema": INPUT_SCHEMA,
    "certificate_schema": SCHEMA,
}

NEW_FIELDS = [
    "R0_1", "R0_2", "R0_3", "R1_1", "R1_2", "R1_3",
    "m0", "m1", "p0", "p1",
]
NEW_PLUS = [f"{row}_plus" for row in NEW_FIELDS]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _patched(data: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    output = deepcopy(data)
    output.update(patch)
    return output


def evaluate(data: dict[str, Any]) -> dict[str, bool]:
    dependencies = data["detector_channel_dependencies"]
    return {
        "carrier_is_84_rows": data["base_rows"] == 64 and data["detector_indexed_rods"] == 6,
        "bulk_memory_category_fixed": data["memory_realization"] == "BULK_CLOCK_TRANSPORTED_SCALARS",
        "memory_pairing_measure_fixed": data["memory_pairing_measure"] == "dvol_gHat",
        "profile_two_jet_fixed": data["profile_scope"] == "EXACT_TWO_JET_THROUGH_Q3_WITH_HIGHER_REMAINDER_OPEN",
        "multigrading_separated": data["rod_action_weight"] == "epsilon_R^2" and data["readout_coupling_weight"] == "kappa",
        "external_source_boundary_fixed": data["source_role"] == "EXTERNAL_Q_CLOSED_CONSERVED_SOURCE",
        "detector_channels_block_local": (
            set(dependencies["D0"]) == {"R0_1", "R0_2", "R0_3"}
            and set(dependencies["D1"]) == {"R1_1", "R1_2", "R1_3"}
        ),
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    payloads = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "global_rods": ("flags", "DETECTOR_INDEXED_ROD_ALLOCATION"),
        "rod_q1_solvability": ("flags", "GLOBAL_ROD_BACKREACTION_SOLVABLE_THROUGH_ORDER_EPSILON_R_SQUARED"),
        "legacy_observer_interface": ("flags", "FORMAL_RANK_TWO_STABILITY_CONDITIONAL_LEMMA"),
        "base_64_carrier": ("flags", "BERGER_PORTABLE_64_ROW_UNARY_Q1"),
        "base_64_causal": ("flags", "BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"),
        "base_64_q3": ("flags", "BERGER_MIXED_ARITY_THREE_IDENTITY"),
        "base_64_k_cartan": ("flags", "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"),
        "retained_observer_k_gate": ("flags", "APPARATUS_84_ROW_COMPLEX_REQUIRED"),
    }
    for name, (section, flag) in required.items():
        if payloads[name][section][flag] is not True:
            raise AssertionError(f"required compatibility flag dropped: {name}.{flag}")
    return payloads


def _carrier(base: dict[str, Any]) -> dict[str, Any]:
    base_rows = base["full_complex"]["component_rows"]
    if len(base_rows) != 64 or [row["index"] for row in base_rows] != list(range(64)):
        raise AssertionError("base carrier is not the canonical ordered 64-row carrier")
    additions = []
    for offset, row_id in enumerate(NEW_FIELDS):
        additions.append({
            "index": 64 + offset,
            "row_id": row_id,
            "degree": 0,
            "sector": "apparatus:rod" if row_id.startswith("R") else "apparatus:memory",
        })
    for offset, row_id in enumerate(NEW_PLUS):
        additions.append({
            "index": 74 + offset,
            "row_id": row_id,
            "degree": 1,
            "sector": "apparatus:rod_antifield_density" if row_id.startswith("R") else "apparatus:memory_antifield_density",
        })
    pairings = []
    for offset in range(10):
        field, antifield = 64 + offset, 74 + offset
        pairings.extend([
            {"left": field, "right": antifield, "coefficient": "1"},
            {"left": antifield, "right": field, "coefficient": "-1"},
        ])
    return {
        "base_rows": 64,
        "new_rows": 20,
        "total_rows": 84,
        "degree_ranks_minus1_0_1_2": [6, 36, 36, 6],
        "component_rows": base_rows + additions,
        "new_pairing_entries": pairings,
        "pairing_measure": "dvol_gHat",
        "pairing_rule": "<field,field_plus>=+1 and <field_plus,field>=-1 for every new degree-zero/degree-one pair",
        "internal_apparatus_gauge_rows_added": 0,
    }


def _primitive_matrix(block: dict[str, Any]) -> sp.Matrix:
    output = sp.zeros(100, 3)
    for column, records in enumerate(block["canonical_primitives_sparse"]):
        for row, raw in records:
            output[row, column] = sp.sympify(raw)
    return output


def _physical_phi2_synthesis(solvability: dict[str, Any]) -> dict[str, Any]:
    z0, z1 = sp.sqrt(10) / 12, sp.sqrt(10) / 6
    t0, t1 = sp.Rational(1, 4), sp.Rational(1, 2)
    frequency = sp.sqrt(58) / 3

    def phase_vector(z: sp.Expr) -> sp.Matrix:
        return sp.Matrix([sp.cos(z) ** 2, sp.sin(z) ** 2, sp.cos(z) * sp.sin(z)])

    zero_coefficients = (phase_vector(z0) + phase_vector(z1)).applyfunc(sp.simplify)
    positive_coefficients = (
        sp.exp(-sp.I * frequency * t0) * phase_vector(z0)
        + sp.exp(-sp.I * frequency * t1) * phase_vector(z1)
    ).applyfunc(sp.simplify)
    zero_primitive = _primitive_matrix(solvability["exact_blocks"]["zero"])
    positive_primitive = _primitive_matrix(solvability["exact_blocks"]["positive"])

    q1_record = json.loads(rod_q1.RETAINED_Q1.read_text())["q1_blocks"]["H_retained"]
    h_zero = rod_q1._operator_matrix(q1_record, sp.S.Zero)
    h_positive = rod_q1._operator_matrix(q1_record, 2 * rod_q1.OMEGA)
    source_zero = rod_q1._source_basis("zero")
    source_positive = rod_q1._source_basis("positive")
    residual_zero = (h_zero * zero_primitive + source_zero).applyfunc(sp.simplify)
    residual_positive = (h_positive * positive_primitive + source_positive).applyfunc(sp.simplify)
    if residual_zero != sp.zeros(100, 3) or residual_positive != sp.zeros(100, 3):
        raise AssertionError("normalized phase-basis primitives do not replay")
    actual_zero_residual = residual_zero * zero_coefficients
    actual_positive_residual = residual_positive * positive_coefficients
    if actual_zero_residual != sp.zeros(100, 1) or actual_positive_residual != sp.zeros(100, 1):
        raise AssertionError("physical two-detector Phi2 synthesis failed")
    return {
        "phase_basis": ["cos(z)^2", "sin(z)^2", "cos(z)*sin(z)"],
        "detectors": [
            {"id": "D0", "hopf_phase": "sqrt(10)/12", "physical_time": "1/4"},
            {"id": "D1", "hopf_phase": "sqrt(10)/6", "physical_time": "1/2"},
        ],
        "zero_frequency_coefficients": [sp.sstr(value) for value in zero_coefficients],
        "positive_frequency_coefficients": [sp.sstr(value) for value in positive_coefficients],
        "negative_frequency_coefficients": [sp.sstr(sp.conjugate(value)) for value in positive_coefficients],
        "primitive_reference": {
            "path": str(DEPENDENCIES["rod_q1_solvability"].relative_to(ROOT)),
            "zero_block_columns": [0, 1, 2],
            "positive_block_columns": [0, 1, 2],
            "negative_block_rule": "complex_conjugate_of_positive",
        },
        "real_background_formula": "Phi2(t,x)=Phi2_0(x)+2*Re(exp(i*sqrt(58)*t/3)*Phi2_plus(x))",
        "zero_frequency_residual_nonzero_count": 0,
        "positive_frequency_residual_nonzero_count": 0,
        "actual_combined_source_primitive_certified": True,
    }


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    requirements = evaluate(data)
    if not all(requirements.values()):
        raise AssertionError(f"base 84-row handoff input failed: {requirements}")
    mutations = []
    for mutation in data["mutations"]:
        observed = evaluate(_patched(data, mutation["patch"]))
        requirement = mutation["expected_failed_requirement"]
        mutations.append({
            "name": mutation["name"],
            "expected_failed_requirement": requirement,
            "observed_requirement_value": observed[requirement],
            "expected_failure_passed": observed[requirement] is False,
        })
    if not all(row["expected_failure_passed"] for row in mutations):
        raise AssertionError("84-row handoff mutation rail did not fail closed")

    dependencies = _load_dependencies()
    carrier = _carrier(dependencies["base_64_carrier"])
    phi2 = _physical_phi2_synthesis(dependencies["rod_q1_solvability"])
    payload = {
        "schema": "closed-universe-berger-84-row-apparatus-handoff-v1",
        "result_id": "BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF",
        "setting_id": data["setting_id"],
        "claim_status": "AUTHORITATIVE_FORWARD_INTERFACE_FROZEN_CONSTRUCTION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path), "result_id": dependencies[name]["result_id"]}
            for name, path in DEPENDENCIES.items()
        },
        "supersession": {
            "forward_authority": True,
            "historical_results_preserved": [
                "BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE",
                "BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE",
            ],
            "superseded_forward_assumptions": [
                "three shared rod fields",
                "78-row proposed carrier",
                "global compact rod source unavailable",
                "compact rod Taub disposition input-blocked",
            ],
            "rule": "all new apparatus construction must import this 84-row handoff; the historical gates remain valid only for the obstructions and conditional lemmas they actually certified",
        },
        "carrier": carrier,
        "detector_channels": [
            {"detector_id": "D0", "rod_rows": data["detector_channel_dependencies"]["D0"], "polarization": "dTheta_wedge_dR0_1", "memory_rows": ["m0", "p0"], "cross_channel_rod_dependence": False},
            {"detector_id": "D1", "rod_rows": data["detector_channel_dependencies"]["D1"], "polarization": "dTheta_wedge_dR1_2", "memory_rows": ["m1", "p1"], "cross_channel_rod_dependence": False},
        ],
        "bulk_memory_contract": {
            "category": data["memory_realization"],
            "fields": ["m0", "m1", "p0", "p1"],
            "spacetime_domain": "smooth scalar fields on R_t x S3 with detector-profile coefficients; retarded inverses act on compact-time-supported tests and their retarded images",
            "transport": "T=n_Theta^a nabla_a with n_Theta^a=nabla^a Theta/(nabla Theta)^2, so T(Theta)=1 and T=(4/3)e0 on the Berger background",
            "formal_adjoint": "T*=-T-div_gHat(n_Theta) with respect to dvol_gHat",
            "pairing_measure": data["memory_pairing_measure"],
            "action": "S_mem=sum_a integral dvol_gHat p_a (T m_a-kappa B_a[A;Theta,R_a,gHat])",
            "retarded_boundary_condition": "zero memory in the causal past of the detector profile; H_ret f is the clock-line Volterra integral",
            "persistence": "T m_a=0 after the detector profile support",
            "worldline_or_defect_interpretation_excluded": True,
        },
        "profile_operator_contract": {
            "operator": "B_a A=chi_a(Theta,R_a) <dA,dTheta wedge dR_aI(a)>_gHat with normalized transverse detector density included in chi_a",
            "maxwell_compatibility_required": ["B_a d=0", "delta B_a*=0"],
            "detector_block_locality": "B_a depends only on the three rods R_aI assigned to detector a",
            "taylor_scope": data["profile_scope"],
            "two_jet_formula": "B_a[barPhi+deltaPhi]=B_a^(0)+B_a^(1)[deltaPhi]+1/2 B_a^(2)[deltaPhi,deltaPhi]+O(deltaPhi^3), deltaPhi=(deltaTheta,deltaR_a,deltagHat)",
            "operation_assignment": ["kappa B^(0) contributes q1", "kappa B^(1) contributes q2", "kappa B^(2) contributes q3"],
            "q4_and_higher_status": "OPEN_FROM_THE_CUBIC_AND_HIGHER_PROFILE_REMAINDER",
        },
        "multigrading": {
            "rod_action_weight": data["rod_action_weight"],
            "readout_coupling_weight": data["readout_coupling_weight"],
            "weights_independent": True,
            "background": "gHat_epsilon=gHat_Berger+epsilon_R^2 Phi2+O(epsilon_R^4), with the displayed O(1) global rods and zero background A,m,p",
            "metric_euler_order_epsilon_R2": "cancelled by H_retained Phi2=-q0^rod",
            "rod_euler_bookkeeping": "epsilon_R^2 Box_gHat R=0 at order epsilon_R^2 because Box_Berger R_bar=0; the Phi2-induced rod correction first enters the un-divided Euler row at order epsilon_R^4",
            "readout_arity": "p*A is q1 at order kappa; p*A*deltaPhi is q2; p*A*deltaPhi^2 is q3",
            "mixed_orders_beyond_declared_gate": "epsilon_R^2*kappa corrections are construction inputs, not silently absorbed into either parameter",
        },
        "physical_backreaction_synthesis": phi2,
        "source_boundary": {
            "role": data["source_role"],
            "current_rows_added": 0,
            "emitter_recoil_included": False,
            "receiver_rod_and_memory_backreaction_targeted": True,
            "spatially_local_emitter_worldtubes_certified": False,
            "rule": "do not describe the 84-row gate as full apparatus recoil; the two J_b remain external until a separate dynamical-emitter extension is supplied",
        },
        "ordered_acceptance_gates": [
            {"order": 1, "id": "shifted_background_euler", "requirement": "all 84 Euler rows vanish through the declared epsilon_R and kappa orders", "status": "OPEN"},
            {"order": 2, "id": "unary_complex", "requirement": "q1^2=0 on 84 rows, nondegenerate odd pairing, unary cyclicity, and both advanced/retarded Green identities", "status": "OPEN"},
            {"order": 3, "id": "maxwell_profile_compatibility", "requirement": "B_a d=0, delta B_a*=0, support theorem, and detector block locality", "status": "OPEN"},
            {"order": 4, "id": "arity_two", "requirement": "q1 q2 identity, cyclicity, and K_Berger equivariance on every apparatus row", "status": "OPEN"},
            {"order": 5, "id": "arity_three", "requirement": "arity-three L_infinity identity, cyclicity, K_Berger equivariance, and explicit higher-remainder boundary", "status": "OPEN"},
            {"order": 6, "id": "observer_morphism", "requirement": "observer evaluation intertwines imported q1,q2,q3 on the declared record domain", "status": "OPEN"},
            {"order": 7, "id": "deformed_response", "requirement": "construct M_ab(epsilon_R,kappa), replay causal acquisition, and only then apply the determinant-unit rank-two lemma", "status": "OPEN"},
        ],
        "mutation_results": mutations,
        "flags": {
            "AUTHORITATIVE_84_ROW_FORWARD_INTERFACE": True,
            "SIX_DETECTOR_INDEXED_RODS_REQUIRED": True,
            "BULK_MEMORY_CATEGORY_FIXED": True,
            "PROFILE_TWO_JET_THROUGH_Q3_FIXED": True,
            "PHYSICAL_TWO_DETECTOR_PHI2_SYNTHESIZED": True,
            "EXTERNAL_SOURCE_BOUNDARY_FIXED": True,
            "84_ROW_Q1_CERTIFIED": False,
            "84_ROW_RETARDED_GREEN_CERTIFIED": False,
            "84_ROW_Q2_Q3_CERTIFIED": False,
            "OBSERVER_EVALUATION_MORPHISM_CERTIFIED": False,
            "DEFORMED_RANK_TWO_RESPONSE_CERTIFIED": False,
            "FULL_APPARATUS_RECOIL_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_SHIFTED_BACKGROUND_AND_84_ROW_UNARY_PAIRING_GREEN_COMPLEX",
        "provenance": {
            "declared_input_sha256": _sha256(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL handoff freezes the authoritative forward interface for a prospective 84-row Berger observer apparatus: six detector-indexed rods, four bulk clock-transported memory fields, canonical new pairings, independent epsilon_R and kappa bookkeeping, a two-jet profile scope through q3, external q-closed emitters, and an exact synthesis of the physical two-detector Phi2 from certified primitives. It resolves conflicting 78-row/three-rod forward assumptions but does not construct the shifted 84-row q1, prove nilpotency or cyclicity, export a Green homotopy, derive apparatus q2/q3, certify K_Berger equivariance, construct the deformed response, include emitter recoil, certify the classical observer map, or make a quantum claim.",
    }
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("84-row apparatus handoff certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
