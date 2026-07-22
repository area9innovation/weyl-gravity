#!/usr/bin/env python3
"""Build the fail-closed Phase-2 full-BV Hadamard obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).parent / "certificates" / "PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json"

SOURCES = {
    "gauge_fixed_unary_pairing": (
        "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
    ),
    "causal_green_homotopy": (
        "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
        "e92642b3225ab87b6058987f73f9ade3909646f2d0d3b95cc45cc9c5712b9c3b",
    ),
    "graded_state_contract_and_real_structure": (
        "quantum-weyl/lorentzian/certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json",
        "99768cf1e444ef3525f19621702ee64a68aea83f83349a1c5d6223d9c959ca35",
    ),
    "hadamard_lift_preflight": (
        "quantum-weyl/lorentzian/certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json",
        "59d52928eb3e0063a4b0464b4592d4bd7d5d43e06860ee96999b6094a12b9723",
    ),
    "zero_frequency_readiness": (
        "quantum-weyl/lorentzian/certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json",
        "204b207b31b5df145e036f44762310af211a8353c721be4cb34aa7ac85e9cbfc",
    ),
    "stationary_generator_import_readiness": (
        "quantum-weyl/lorentzian/certificates/BERGER_RETAINED_26_STATIONARY_GENERATOR_IMPORT_READINESS.json",
        "cf3499a76ea0367db9d886f6b91c3de1ee392c4c1a376eb60d3060b8e37ca7de",
    ),
    "phase2_cpt_disposition": (
        "quantum-weyl/pt_cpt/synthesis/certificates/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1.json",
        "516415604952c1f835ea0d46095d8fa82b07fe36de3dc33d641e34f0b938223c",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_sources(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    loaded: dict[str, Any] = {}
    refs: dict[str, Any] = {}
    for role, (relative, expected) in SOURCES.items():
        path = root / relative
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"source hash mismatch for {role}: {actual} != {expected}")
        loaded[role] = json.loads(path.read_text())
        refs[role] = {"path": relative, "sha256": expected}
    return loaded, refs


def build_payload(root: Path = ROOT) -> dict[str, Any]:
    source, refs = _load_sources(root)
    unary = source["gauge_fixed_unary_pairing"]
    green = source["causal_green_homotopy"]
    state = source["graded_state_contract_and_real_structure"]
    lift = source["hadamard_lift_preflight"]
    zero = source["zero_frequency_readiness"]
    readiness = source["stationary_generator_import_readiness"]
    cpt = source["phase2_cpt_disposition"]

    checks = {
        "exactly_one_complete_causal_BV_complex_selected": (
            unary["row_layout"]["total_rows"] == 54
            and unary["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"]
            and green["flags"]["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"]
        ),
        "action_derived_differential_and_pairing_imported": (
            unary["claim_status"] == "CERTIFIED_COMPLETE_GAUGE_FIXED_UNARY_CONTRACTION"
            and unary["contraction"]["cyclic"]
            and unary["contraction"]["cyclic_pairing"]["shape"] == [54, 54]
        ),
        "real_structure_imported": (
            state["real_structure"]["status"]
            == "CERTIFIED_FROM_REAL_CLASSICAL_OPERATOR_AND_UNIQUENESS"
        ),
        "advanced_retarded_homotopies_imported": (
            green["claim_status"]
            == "CERTIFIED_COMPLETE_GAUGE_FIXED_CAUSAL_GREEN_HOMOTOPY_HADAMARD_OPEN"
        ),
        "causal_antisymmetric_part_and_BRST_descent_available": (
            state["claim_flags"]["BERGER_GRADED_CAUSAL_COMMUTATOR"]
            and state["claim_flags"]["BERGER_BRST_CAUSAL_PAIRING_DESCENT"]
        ),
        "conditional_26_to_54_covariance_lift_available": (
            lift["claim_flags"]["BERGER_COVARIANCE_LIFT_26_TO_54"]
        ),
        "zero_frequency_carrier_nonidentifiable": (
            zero["claim_flags"]["ZERO_FREQUENCY_INPUT_NONIDENTIFIABILITY_CERTIFIED"]
            and zero["nonidentifiability_witness"]["zero_eigenspace_dimension_difference"] == 24
        ),
        "stationary_generator_input_absent": (
            not readiness["claim_flags"]["STATIONARY_GENERATOR_INPUT_AVAILABLE"]
            and not readiness["claim_flags"]["STATIONARY_GENERATOR_ACCEPTED"]
        ),
        "P2A_supplies_no_full_BV_C_or_adjoint_replacement": (
            cpt["decision"]["genuine_Mannheim_C"] == "NONE_CERTIFIED"
            and "a full-BV Hadamard state" in cpt["claim_boundary"]["does_not_establish"][2]
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"import contract failed: {failed}")

    return {
        "$schema": "../schema/phase2-brst-hadamard-stretch-obstruction-v1.schema.json",
        "schema": "pure-weyl-phase2-brst-hadamard-stretch-obstruction-v1",
        "result_id": "PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1",
        "result_state": "COMPLETE_CAUSAL_BV_SELECTED_ZERO_FREQUENCY_CARRIER_EXACTLY_NOT_IDENTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "selected_complex": {
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "carrier": "complete gauge-fixed 54-row classical Berger BV complex",
            "row_count": 54,
            "selection_count": 1,
            "complete_causal_status": "CERTIFIED",
            "reduced_26_role": "conditional covariance construction and obstruction localization only; not substituted for the full BV complex",
        },
        "imported_contract": {
            "differential": "complete action-derived gauge-fixed q54",
            "pairing": "nondegenerate odd 54-row Darboux pairing",
            "real_structure": "componentwise conjugation on the real Berger row basis",
            "green_homotopies": "advanced and retarded contractions on all 54 rows",
            "zero_modes": "retained generalized zero space required but not determined by current exact exports",
            "P2A_adjoint_disposition": "no genuine Mannheim C or full-BV adjoint replacement is certified; retain the imported action-derived graded adjoint for this audit",
        },
        "bidistribution_contract_attempt": {
            "declared_Hadamard_wavefront_relation": "local singular structure certified; exact global covariance not constructed",
            "BRST_chain_identities": "AVAILABLE_FOR_CAUSAL_COMMUTATOR_AND_CONDITIONAL_LIFT",
            "antisymmetric_part_equals_i_causal_propagator": "TARGET_NORMALIZATION_FROZEN_AND_CAUSAL_PART_CERTIFIED",
            "reality": "IMPORTED",
            "positivity_on_ghost_number_zero_cohomology": "NOT_REACHED",
            "full_54_row_covariance": "NOT_CONSTRUCTED",
        },
        "first_exact_obstruction": {
            "type": "MISSING_COMPLETE_STATIONARY_CAUCHY_CARRIER",
            "required_result_id": "BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
            "missing_artifacts": ["A104", "q_Cauchy_104", "G_Cauchy_104", "real_structure_104"],
            "shape_each": [104, 104],
            "unknown_coordinates_in_current_A104": 288,
            "unknown_blocks": ["ghost_A12", "identity_A12"],
            "exact_witness": {
                "completion_A_endpoint_zero_eigenspace_dimension": 24,
                "completion_B_endpoint_zero_eigenspace_dimension": 0,
                "difference": 24,
                "meaning": "the current exact mask does not determine the zero/Jordan carrier",
            },
            "analytic_remainder_after_exact_import": "prove whether zero is isolated in a declared closed mixed-Sobolev/Krein realization",
            "consequence": "the smooth zero-frequency correction and hence the global BRST-compatible Hadamard covariance cannot be selected from current certified data",
        },
        "exact_checks": checks,
        "source_refs": refs,
        "claim_flags": {
            "COMPLETE_54_ROW_CAUSAL_BV_COMPLEX_IMPORTED": True,
            "P2A_FULL_BV_C_OPERATOR_CERTIFIED": False,
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "establishes": [
                "selection and hash-pinned import of exactly one complete causal 54-row BV complex",
                "the first exact obstruction to the requested global bidistribution contract",
                "that P2-A reduced-mode metrics do not authorize a full-BV adjoint replacement",
            ],
            "does_not_establish": [
                "nonexistence of a BRST-compatible Hadamard covariance after the missing stationary carrier is supplied",
                "a full-BV Mannheim C operator or a no-go for every possible ghost normalizer",
                "positivity, particles, scattering, renormalized products, QME restoration or unitarity",
            ],
        },
        "next_gate": "SUPPLY_AND_ACCEPT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_THEN_PROVE_ZERO_SPECTRAL_DISPOSITION",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("certificate is stale")
        print("PASS: Phase-2 full-BV Hadamard stretch obstruction certificate is current")
    else:
        OUTPUT.write_text(rendered)
        print(OUTPUT)


if __name__ == "__main__":
    main()
