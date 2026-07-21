#!/usr/bin/env python3
"""Assemble the repaired-q70 physical-health ledgers without filling gaps.

The two prerequisite health computations terminate at different logical
boundaries.  Together they give complete all-m/all-k physical blocks for
j=0, 1/2 and 1, but no physical quotient for j>=3/2.  This producer therefore
emits the typed maximal *certified* domain and the exact remaining carrier.
It does not extrapolate the first generic counterexample to uncomputed
isotypes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json"
SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-payload-v1.schema.json"

IMPORTS = {
    "repaired_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
        "3f41cb5258f0883b217c9343e037074faf841728f29e03c306f101487411d2cf",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2",
    ),
    "repaired_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json",
        "c59b1a74aced082155db3446c40aa1b14e3982e66670a3c097539b25d5d5c938",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2",
    ),
    "generic_health": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json",
        "d78fa16e9772924ded1b8262f33e3989a9e94acd01891257309bc07f7f7f282c",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1",
    ),
    "generic_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json",
        "43595d6e974dd3ff852db658014fb34dcd1521f050a752e5732fb0c3b5f27797",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1",
    ),
    "low_j_health": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json",
        "fa0d158301a1bf2076d7d7622866f4545d6a15370ec576ddcbe120837224d364",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1",
    ),
    "low_j_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json",
        "291071bab2494a4b4bdb21702be1bf28d672a2a6157b588003743aec5d0b5b5e",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id) in IMPORTS.items():
        path = ROOT / relative
        actual = _sha(path)
        value = json.loads(path.read_text())
        if actual != expected:
            raise AssertionError(f"{role} hash drift: {actual}")
        if value.get("result_id") != result_id:
            raise AssertionError(f"{role} result_id drift")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "oracle_fields_consumed": [],
        }
        values[role] = value
    _validate_inputs(values)
    return records, values


def _validate_inputs(values: dict[str, Any]) -> None:
    parent = values["repaired_parent"]
    generic = values["generic_health"]
    low_j = values["low_j_health"]
    if parent["terminal_verdict"]["result_state"] != "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT":
        raise AssertionError("repaired parent did not pass")
    required = ("q70_squared_zero", "q70_degree_plus_one", "q70_cyclic", "q70_S70_plus_S70_q70_identity")
    if not all(parent["exact_checks"][key] for key in required):
        raise AssertionError("repaired parent exact checks did not pass")
    if generic["carrier"]["labels"]["two_j"] != 1:
        raise AssertionError("generic health ledger is not the j=1/2 block")
    if generic["terminal_verdict"]["generic_all_j_health_theorem"] != "OBSTRUCTED_BY_EXPLICIT_GENERIC_BLOCK_COUNTEREXAMPLE":
        raise AssertionError("generic health stop condition drifted")
    if "the spectra of every higher-j" not in " ".join(generic["claim_boundary"]["does_not_establish"]):
        raise AssertionError("generic higher-j fail-closed boundary missing")
    if low_j["representation_census"]["exceptional_two_j"] != [0, 2]:
        raise AssertionError("exceptional-isotype census drifted")
    if low_j["terminal_verdict"]["health_assembly_activated"] is not True:
        raise AssertionError("low-j health assembly gate did not activate")


def _block_ledger(values: dict[str, Any]) -> list[dict[str, Any]]:
    generic = values["generic_health"]
    generic_payload = values["generic_payload"]
    low_j = values["low_j_health"]
    low_payload = values["low_j_payload"]
    j0_payload = low_payload["exceptional_blocks"]["j0"]
    j1_payload = low_payload["exceptional_blocks"]["j1"]
    j0_summary = low_j["exceptional_block_summary"]["j0"]
    j1_summary = low_j["exceptional_block_summary"]["j1"]
    blocks = [
        {
            "j": "0",
            "two_j": 0,
            "source_role": "low_j_health",
            "m_values": ["0"],
            "k_values": ["0"],
            "all_m": True,
            "all_k": True,
            "q70_dimension_per_fixed_m": 70,
            "q70_total_dimension": 70,
            "retained_dimension_per_fixed_m": 26,
            "retained_total_dimension": 26,
            "physical_dimension_per_fixed_m": j0_payload["localized_nonzero_frequency_quotient"]["physical_dimension"],
            "physical_total_dimension": j0_payload["localized_nonzero_frequency_quotient"]["physical_dimension"],
            "zero_frequency_cohomology_dimensions": j0_summary["zero_frequency"]["cohomology_dimensions_Hminus1_H0_H1_H2"],
            "pairing_radical_dimension": j0_summary["unstable"]["pairing_radical_dimension"],
            "unstable_factors": [j0_summary["unstable"]["factor"]],
            "instability_class": j0_summary["unstable"]["classification"],
            "energy_inertias": [j0_summary["unstable"]["energy"]["inertia_positive_negative_zero"]],
            "unrestricted_status": "OBSTRUCTED_REAL_EXPONENTIAL_PHYSICAL_MODE",
            "fixed_Q_rel_status": "OBSTRUCTED_REAL_EXPONENTIAL_PHYSICAL_MODE_SURVIVES_FIXED_CHARGE",
        },
        {
            "j": "1/2",
            "two_j": 1,
            "source_role": "generic_health",
            "m_values": ["-1/2", "+1/2"],
            "k_values": ["-1/2", "+1/2"],
            "all_m": True,
            "all_k": True,
            "q70_dimension_per_fixed_m": generic["carrier"]["per_fixed_m_dimension"],
            "q70_total_dimension": generic["carrier"]["per_fixed_m_dimension"] * 2,
            "retained_dimension_per_fixed_m": generic["carrier"]["retained_q26_component_dimension"],
            "retained_total_dimension": generic["carrier"]["retained_q26_component_dimension"] * 2,
            "physical_dimension_per_fixed_m": generic["physical_quotient_summary"]["dimension"],
            "physical_total_dimension": generic["physical_quotient_summary"]["dimension"] * 2,
            "zero_frequency_cohomology_dimensions": [0, 0, 0, 0],
            "pairing_radical_dimension": generic["physical_quotient_summary"]["cohomology_pairing_radical_dimension"],
            "unstable_factors": [generic["terminal_verdict"]["complex_frequency_factor"]],
            "instability_class": generic["unstable_sector"]["classification"],
            "energy_inertias": [generic["unstable_sector"]["two_copy_inertia_positive_negative_zero"]],
            "unrestricted_status": "OBSTRUCTED_HAMILTONIAN_HOPF_PHYSICAL_MODE",
            "fixed_Q_rel_status": "OBSTRUCTED_HAMILTONIAN_HOPF_PHYSICAL_MODE_SURVIVES_FIXED_CHARGE",
            "physical_factor_count": len(generic_payload["physical_quotient"]["factor_audits"]),
        },
        {
            "j": "1",
            "two_j": 2,
            "source_role": "low_j_health",
            "m_values": ["-1", "0", "+1"],
            "k_values": ["-1", "0", "+1"],
            "all_m": True,
            "all_k": True,
            "q70_dimension_per_fixed_m": 210,
            "q70_total_dimension": 630,
            "retained_dimension_per_fixed_m": 78,
            "retained_total_dimension": 234,
            "physical_dimension_per_fixed_m": j1_payload["localized_nonzero_frequency_quotient"]["physical_dimension"],
            "physical_total_dimension": j1_payload["localized_nonzero_frequency_quotient"]["physical_dimension"] * 3,
            "zero_frequency_cohomology_dimensions": j1_summary["zero_frequency"]["cohomology_dimensions_Hminus1_H0_H1_H2"],
            "pairing_radical_dimension": max(item["pairing_radical_dimension"] for item in j1_summary["unstable"]),
            "unstable_factors": [item["factor"] for item in j1_summary["unstable"]],
            "instability_class": "PHYSICAL_COMPLEX_FREQUENCY_SECTORS",
            "energy_inertias": [item["two_copy_inertia_positive_negative_zero"] for item in j1_summary["unstable"]],
            "unrestricted_status": "OBSTRUCTED_COMPLEX_FREQUENCY_PHYSICAL_MODES",
            "fixed_Q_rel_status": "OBSTRUCTED_COMPLEX_FREQUENCY_PHYSICAL_MODES_SURVIVE_FIXED_CHARGE",
        },
    ]
    if [block["two_j"] for block in blocks] != [0, 1, 2]:
        raise AssertionError("certified domain is not contiguous through two_j=2")
    for block in blocks:
        n = block["two_j"] + 1
        if block["q70_dimension_per_fixed_m"] != 70 * n:
            raise AssertionError("q70 dimension formula failed")
        if block["retained_dimension_per_fixed_m"] != 26 * n:
            raise AssertionError("retained dimension formula failed")
        if block["physical_dimension_per_fixed_m"] != 7 * n:
            raise AssertionError("physical dimension formula failed")
        if not block["all_m"] or not block["all_k"] or block["pairing_radical_dimension"] != 0:
            raise AssertionError("certified block coverage/pairing failed")
    return blocks


def _symmetry_ledger(values: dict[str, Any]) -> dict[str, Any]:
    actions = values["low_j_health"]["charge_actions"]
    return {
        "global_action_angle_unrestricted": actions["global_action_angle_carrier"]["unrestricted"],
        "global_action_angle_fixed_Q_rel": actions["global_action_angle_carrier"]["fixed_charge"],
        "spatial_Killing_stabilizers": actions["spatial_Killing_stabilizers"],
        "diagonal_U1": actions["repaired_diagonal_U1"],
        "nonzero_frequency_fixed_charge": actions["nonzero_characteristic_modes"],
        "j_half_nonzero_action": values["generic_health"]["charge_actions"],
        "j0_and_j1_nonzero_R_rel_K_action": {
            "status": "NO_SEPARATE_ACTION_MATRIX_EXPORTED",
            "certified_statement": "the nonzero-frequency physical modes have delta Q_rel=0 and survive the fixed-Q_rel restriction",
            "forbidden_inference": "survival of the fixed-charge restriction is not a diagonalization of R_rel or K on these quotient bases",
        },
    }


def build_payload() -> dict[str, Any]:
    imports, values = _load_imports()
    blocks = _block_ledger(values)
    payload: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "certified_block_ledger": blocks,
        "cross_isotype_partition": {
            "label_space": "two_j in Z_{>=0}",
            "certified_two_j": [0, 1, 2],
            "certified_j": ["0", "1/2", "1"],
            "remaining_predicate": "two_j >= 3 (equivalently j >= 3/2)",
            "disjoint": True,
            "union_is_all_declared_isotypes": True,
            "proof": "For every nonnegative integer n=two_j, exactly one of n<=2 or n>=3 holds; the certified sources cover n=0,1,2 without overlap.",
            "stabilizer_exceptional_two_j": [0, 2],
            "first_nonstabilizer_counterexample_two_j": 1,
        },
        "certified_domain_summary": {
            "domain_kind": "MAXIMAL_UNION_OF_IMPORTED_CERTIFIED_PHYSICAL_HEALTH_BLOCKS",
            "q70_total_dimension_all_m_k": sum(block["q70_total_dimension"] for block in blocks),
            "retained_total_dimension_all_m_k": sum(block["retained_total_dimension"] for block in blocks),
            "physical_total_dimension_all_m_k": sum(block["physical_total_dimension"] for block in blocks),
            "all_70_rows_present_in_each_block": True,
            "all_m_and_k_present_in_each_block": True,
            "all_certified_characteristic_pairings_nondegenerate": True,
            "every_certified_isotype_has_a_physical_instability": True,
        },
        "remaining_carrier": {
            "two_j_domain": "all integers two_j >= 3",
            "j_domain": "all half-integers j >= 3/2",
            "m_domain": "all m=-j,...,+j",
            "k_domain": "all k=-j,...,+j",
            "q70_rows_per_Peter_Weyl_coefficient": 70,
            "q70_dimension_per_fixed_m_formula": "70*(two_j+1)",
            "q70_total_dimension_per_isotype_formula": "70*(two_j+1)^2",
            "retained_dimension_per_fixed_m_formula": "26*(two_j+1)",
            "physical_quotient_status": "NO_CERTIFIED_MAP",
            "characteristic_spectrum_status": "NO_CERTIFIED_MAP",
            "pairing_inertia_status": "NO_CERTIFIED_MAP",
            "causal_parent_status": "CERTIFIED_IMPORTED",
            "why_remaining": "the generic prerequisite stopped after the first explicit nonstabilizer counterexample and expressly did not establish every higher-j spectrum",
        },
        "symmetry_and_charge_ledger": _symmetry_ledger(values),
        "branch_verdicts": {
            "unrestricted": {
                "linear_physical_health": "OBSTRUCTED",
                "witnesses": ["j=0 real exponential", "j=1/2 Hamiltonian-Hopf", "j=1 complex-frequency"],
                "global_relative_clock": "two-dimensional charged Darboux carrier with a size-two zero Jordan chain",
            },
            "fixed_Q_rel": {
                "linear_physical_health": "OBSTRUCTED",
                "witnesses": ["all three certified nonzero-frequency instability sectors survive"],
                "global_relative_clock": "removed by the derived level-set and R_rel quotient",
            },
            "complete_all_isotype_mode_census": "OPEN_ON_J_GE_3_OVER_2",
        },
        "terminal_verdict": {
            "result_state": "OBSTRUCTED_LINEAR_PHYSICAL_HEALTH_WITH_TYPED_HIGHER_J_CENSUS_SHORTFALL",
            "health_obstruction_complete": True,
            "all_isotype_spectral_census_complete": False,
            "maximal_certified_domain": "j=0,1/2,1 with every m,k and all q70 rows",
            "remaining_carrier": "j>=3/2 physical quotient and spectrum",
        },
        "claim_boundary": {
            "establishes": [
                "the exact union and disjoint remaining carrier of the imported repaired-q70 health ledgers",
                "complete all-m/all-k q70, retained and physical dimensions for j=0,1/2,1",
                "linear physical-health obstruction on unrestricted and fixed-Q_rel branches",
                "separation of the charged global action-angle carrier, local spatial stabilizers and contractible diagonal-U1 sector",
            ],
            "does_not_establish": [
                "a physical quotient, spectrum, pairing inertia or health classification for j>=3/2",
                "nonlinear instability or finite-time blow-up",
                "observer, Hadamard, anomaly, QME, particle, positivity or unitarity claims",
                "an R_rel or K action matrix on the j=0 and j=1 nonzero-frequency quotient bases",
            ],
        },
    }
    core = dict(payload)
    payload["content_sha256"] = _digest(core)
    return payload


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    cert: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1",
        "dependency_tags": payload["dependency_tags"],
        "lifecycle_state": "CLASSIFIED",
        "result_state": payload["terminal_verdict"]["result_state"],
        "imports": payload["imports"],
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(_render(payload).encode()).hexdigest(),
            "content_sha256": payload["content_sha256"],
        },
        "certified_domain_summary": payload["certified_domain_summary"],
        "cross_isotype_partition": payload["cross_isotype_partition"],
        "remaining_carrier": payload["remaining_carrier"],
        "branch_verdicts": payload["branch_verdicts"],
        "terminal_verdict": payload["terminal_verdict"],
        "claim_boundary": payload["claim_boundary"],
        "content_hashes": {
            "certified_block_ledger": _digest(payload["certified_block_ledger"]),
            "symmetry_and_charge_ledger": _digest(payload["symmetry_and_charge_ledger"]),
            "cross_isotype_partition": _digest(payload["cross_isotype_partition"]),
        },
    }
    return cert


def _validate(value: dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.path))
    if errors:
        raise AssertionError("; ".join(error.message for error in errors[:8]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    _validate(payload, PAYLOAD_SCHEMA)
    _validate(certificate, SCHEMA)
    if args.check:
        if json.loads(PAYLOAD.read_text()) != payload:
            raise AssertionError("health-assembly payload drifted")
        if json.loads(OUTPUT.read_text()) != certificate:
            raise AssertionError("health-assembly certificate drifted")
        print("TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN: PASS")
        return
    PAYLOAD.write_text(_render(payload))
    OUTPUT.write_text(_render(certificate))


if __name__ == "__main__":
    main()
