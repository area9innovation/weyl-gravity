#!/usr/bin/env python3
"""Independent ledger and domain replay for repaired-q70 health assembly.

This verifier does not import the producer.  It reads the three immutable
scientific inputs, reconstructs the certified/remaining isotype partition,
and checks every copied dimension, instability and charge-boundary claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CERT = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json"
CERT_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-payload-v1.schema.json"

EXPECTED_IMPORTS = {
    "repaired_parent": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json", "3f41cb5258f0883b217c9343e037074faf841728f29e03c306f101487411d2cf"),
    "repaired_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json", "c59b1a74aced082155db3446c40aa1b14e3982e66670a3c097539b25d5d5c938"),
    "generic_health": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json", "d78fa16e9772924ded1b8262f33e3989a9e94acd01891257309bc07f7f7f282c"),
    "generic_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json", "43595d6e974dd3ff852db658014fb34dcd1521f050a752e5732fb0c3b5f27797"),
    "low_j_health": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json", "fa0d158301a1bf2076d7d7622866f4545d6a15370ec576ddcbe120837224d364"),
    "low_j_payload": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json", "291071bab2494a4b4bdb21702be1bf28d672a2a6157b588003743aec5d0b5b5e"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _validate(value: dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise AssertionError(errors[0].message)


def main() -> None:
    cert = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    _validate(cert, CERT_SCHEMA)
    _validate(payload, PAYLOAD_SCHEMA)

    imports: dict[str, dict[str, Any]] = {}
    for role, (relative, expected_hash) in EXPECTED_IMPORTS.items():
        path = ROOT / relative
        value = json.loads(path.read_text())
        if _sha(path) != expected_hash:
            raise AssertionError(f"independent import hash failure: {role}")
        if payload["imports"][role]["path"] != relative or payload["imports"][role]["sha256"] != expected_hash:
            raise AssertionError(f"serialized import ledger failure: {role}")
        imports[role] = value

    parent = imports["repaired_parent"]
    generic = imports["generic_health"]
    generic_payload = imports["generic_payload"]
    low = imports["low_j_health"]
    low_payload = imports["low_j_payload"]
    if parent["terminal_verdict"]["result_state"] != "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT":
        raise AssertionError("parent verdict failure")
    if low["representation_census"]["exceptional_two_j"] != [0, 2]:
        raise AssertionError("independent exceptional census failure")
    if generic["carrier"]["labels"]["two_j"] != 1:
        raise AssertionError("independent generic-label failure")

    blocks = payload["certified_block_ledger"]
    if [block["two_j"] for block in blocks] != [0, 1, 2]:
        raise AssertionError("certified isotype ordering failure")
    expected_sources = ["low_j_health", "generic_health", "low_j_health"]
    expected_physical = [
        low_payload["exceptional_blocks"]["j0"]["localized_nonzero_frequency_quotient"]["physical_dimension"],
        generic["physical_quotient_summary"]["dimension"],
        low_payload["exceptional_blocks"]["j1"]["localized_nonzero_frequency_quotient"]["physical_dimension"],
    ]
    for two_j, block in enumerate(blocks):
        n = two_j + 1
        if block["source_role"] != expected_sources[two_j]:
            raise AssertionError("block source failure")
        if len(block["m_values"]) != n or len(block["k_values"]) != n:
            raise AssertionError("all-m/all-k degeneracy failure")
        if block["q70_dimension_per_fixed_m"] != 70 * n:
            raise AssertionError("q70 dimension failure")
        if block["q70_total_dimension"] != 70 * n * n:
            raise AssertionError("q70 isotype total failure")
        if block["retained_dimension_per_fixed_m"] != 26 * n:
            raise AssertionError("retained dimension failure")
        if block["retained_total_dimension"] != 26 * n * n:
            raise AssertionError("retained isotype total failure")
        if block["physical_dimension_per_fixed_m"] != expected_physical[two_j] or expected_physical[two_j] != 7 * n:
            raise AssertionError("physical quotient dimension failure")
        if block["physical_total_dimension"] != 7 * n * n:
            raise AssertionError("physical isotype total failure")
        if block["pairing_radical_dimension"] != 0 or not block["unstable_factors"]:
            raise AssertionError("physical pairing/instability failure")

    j0_factor = low["exceptional_block_summary"]["j0"]["unstable"]["factor"]
    jhalf_factor = generic["terminal_verdict"]["complex_frequency_factor"]
    j1_factors = [item["factor"] for item in low["exceptional_block_summary"]["j1"]["unstable"]]
    if blocks[0]["unstable_factors"] != [j0_factor] or blocks[1]["unstable_factors"] != [jhalf_factor] or blocks[2]["unstable_factors"] != j1_factors:
        raise AssertionError("unstable-factor copy failure")
    if blocks[1].get("physical_factor_count") != len(generic_payload["physical_quotient"]["factor_audits"]):
        raise AssertionError("generic factor census failure")

    totals = payload["certified_domain_summary"]
    if totals["q70_total_dimension_all_m_k"] != sum(70 * n * n for n in (1, 2, 3)):
        raise AssertionError("q70 aggregate failure")
    if totals["retained_total_dimension_all_m_k"] != sum(26 * n * n for n in (1, 2, 3)):
        raise AssertionError("retained aggregate failure")
    if totals["physical_total_dimension_all_m_k"] != sum(7 * n * n for n in (1, 2, 3)):
        raise AssertionError("physical aggregate failure")

    partition = payload["cross_isotype_partition"]
    # Exhaustive symbolic partition: every n in N0 is either one of 0,1,2 or n>=3.
    for n in range(64):
        certified = n in partition["certified_two_j"]
        remaining = n >= 3
        if certified == remaining or not (certified or remaining):
            raise AssertionError("finite audit of symbolic partition failed")
    if partition["stabilizer_exceptional_two_j"] != [0, 2] or partition["first_nonstabilizer_counterexample_two_j"] != 1:
        raise AssertionError("partition provenance failure")
    remaining = payload["remaining_carrier"]
    if any(remaining[key] != "NO_CERTIFIED_MAP" for key in ("physical_quotient_status", "characteristic_spectrum_status", "pairing_inertia_status")):
        raise AssertionError("remaining carrier did not fail closed")
    if "higher-j" not in " ".join(generic["claim_boundary"]["does_not_establish"]):
        raise AssertionError("remaining-carrier source boundary failure")

    if payload["branch_verdicts"]["unrestricted"]["linear_physical_health"] != "OBSTRUCTED":
        raise AssertionError("unrestricted verdict failure")
    if payload["branch_verdicts"]["fixed_Q_rel"]["linear_physical_health"] != "OBSTRUCTED":
        raise AssertionError("fixed-charge verdict failure")
    if not low["terminal_verdict"]["fixed_charge_removes_global_action_angle_but_not_nonzero_frequency_instabilities"]:
        raise AssertionError("fixed-charge source theorem failure")

    core = dict(payload)
    content_hash = core.pop("content_sha256")
    if _digest(core) != content_hash:
        raise AssertionError("payload content hash failure")
    if cert["payload_ref"]["sha256"] != _sha(PAYLOAD) or cert["payload_ref"]["content_sha256"] != content_hash:
        raise AssertionError("payload reference failure")
    if cert["content_hashes"]["certified_block_ledger"] != _digest(blocks):
        raise AssertionError("block-ledger content hash failure")
    if cert["content_hashes"]["cross_isotype_partition"] != _digest(partition):
        raise AssertionError("partition content hash failure")
    if cert["terminal_verdict"]["health_obstruction_complete"] is not True or cert["terminal_verdict"]["all_isotype_spectral_census_complete"] is not False:
        raise AssertionError("terminal two-axis verdict failure")

    print("TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_INDEPENDENT: PASS")


if __name__ == "__main__":
    main()
