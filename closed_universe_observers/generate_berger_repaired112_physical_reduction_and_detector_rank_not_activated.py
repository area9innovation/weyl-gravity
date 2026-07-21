#!/usr/bin/env python3
"""Certify nonactivation of physical reduction after the fresh pushout no-go."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED.json"
X = P / "certificates/BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED_PAYLOAD.json"
SCHEMA = P / "schema/berger-repaired112-physical-reduction-and-detector-rank-not-activated-v1.schema.json"
REPORT = P / "reports/berger-repaired112-physical-reduction-and-detector-rank-not-activated.md"
DEPS = {
    "pushout_disposition": P / "certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION.json",
    "pushout_payload": P / "certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION_PAYLOAD.json",
    "repair_no_go": P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO.json",
    "repair_no_go_payload": P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO_PAYLOAD.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def validate_terminal_branch(values: dict[str, dict[str, Any]]) -> None:
    pushout = values["pushout_disposition"]
    payload = values["pushout_payload"]
    repair = values["repair_no_go"]
    repair_payload = values["repair_no_go_payload"]
    if sha(DEPS["pushout_payload"]) != pushout["payload_ref"]["sha256"]:
        raise AssertionError("pushout payload hash mismatch")
    if sha(DEPS["repair_no_go_payload"]) != repair["payload_ref"]["sha256"]:
        raise AssertionError("repair payload hash mismatch")
    if pushout["atlas_status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("pushout disposition is not fail-closed")
    if payload["category_of_complexes_gate"]["apparatus_pushout"] != "NONDEFINED":
        raise AssertionError("pushout is not terminally nondefined")
    if payload["category_of_complexes_gate"]["derived_combined_row_count"] != "NO_CERTIFIED_MAP":
        raise AssertionError("a combined row count was improperly promoted")
    if pushout["gate_results"]["physical_reduction"] != "NO_CERTIFIED_MAP":
        raise AssertionError("physical reduction was improperly activated")
    equation = repair_payload["nilpotency_equation"]
    if (equation["coefficient_matrix_rank"], equation["augmented_matrix_rank"]) != (1, 2):
        raise AssertionError("decisive rank separator drifted")


def reject_false_activation(values: dict[str, dict[str, Any]]) -> None:
    mutated = copy.deepcopy(values)
    mutated["pushout_payload"]["category_of_complexes_gate"]["apparatus_pushout"] = "CERTIFIED"
    try:
        validate_terminal_branch(mutated)
    except AssertionError:
        return
    raise AssertionError("false pushout activation was accepted")


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    validate_terminal_branch(values)
    reject_false_activation(values)
    pushout = values["pushout_payload"]
    repair = values["repair_no_go_payload"]
    equation = repair["nilpotency_equation"]
    return {
        "schema": "closed-universe-berger-repaired112-physical-reduction-and-detector-rank-not-activated-payload-v1",
        "result_id": "BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED_PAYLOAD",
        "activation_gate": {
            "required_input": "a serialized nilpotent combined apparatus unary (V,q1)",
            "apparatus_pushout": pushout["category_of_complexes_gate"]["apparatus_pushout"],
            "combined_row_count": pushout["category_of_complexes_gate"]["derived_combined_row_count"],
            "combined_q1": "NO_CERTIFIED_MAP",
            "verdict": "NOT_ACTIVATED",
        },
        "method_distinct_obstruction_replay": {
            "identity": "physical cohomology H(V,q1) requires q1^2=0 before kernels/images or contraction data are defined",
            "scalar_equation_count": equation["scalar_equation_count"],
            "coefficient_matrix_rank": equation["coefficient_matrix_rank"],
            "augmented_matrix_rank": equation["augmented_matrix_rank"],
            "canonical_augmented_determinant": equation["canonical_two_equation_augmented_determinant"],
            "correction_only_equation": equation["correction_only_equation"],
            "target_only_equation": equation["target_only_equation"],
            "background_preserving_correction_dimension": repair["background_preservation_gate"]["admissible_dimension"],
        },
        "sector_disposition": {
            sector: {
                "chain_groups": "NO_CERTIFIED_MAP",
                "kernel": "NO_CERTIFIED_MAP",
                "image": "NO_CERTIFIED_MAP",
                "cohomology": "NO_CERTIFIED_MAP",
            }
            for sector in ("generic_smooth", "compact_support", "spatial_zero_mode")
        },
        "contraction_and_pairing_disposition": {
            "pi_cl": "NO_CERTIFIED_MAP",
            "inclusion": "NO_CERTIFIED_MAP",
            "homotopy": "NO_CERTIFIED_MAP",
            "contraction_identities": "NO_CERTIFIED_MAP",
            "descended_odd_pairing": "NO_CERTIFIED_MAP",
            "radical_and_inertia": "NO_CERTIFIED_MAP",
            "reduced_real_structure": "NO_CERTIFIED_MAP",
            "reduced_K_Berger_action": "NO_CERTIFIED_MAP",
        },
        "observer_class_disposition": {
            "rod_classes": "NO_CERTIFIED_MAP",
            "polarization_classes": "NO_CERTIFIED_MAP",
            "emitter_classes": "NO_CERTIFIED_MAP",
            "detector_record_classes": "NO_CERTIFIED_MAP",
            "persistent_memory_classes": "NO_CERTIFIED_MAP",
            "two_record_detector_map_descends": "NO_CERTIFIED_MAP",
            "physical_detector_rank": "NO_CERTIFIED_MAP",
            "physical_detector_kernel": "NO_CERTIFIED_MAP",
        },
        "separate_material_fact": {
            "standalone_material_coordinate_detector_rank": 2,
            "status": "CERTIFIED_SEPARATE",
            "not_a_physical_combined_rank": True,
        },
        "forbidden_imports": {
            "pre_repair_160_row_cohomology": "REJECTED_DIFFERENT_TERMINAL_CARRIER",
            "raw_material_rows_as_observables": "REJECTED_NO_COMBINED_COHOMOLOGY_CLASS",
            "rank_from_dimensions": "REJECTED_NO_DESCENDED_MAP",
        },
        "downstream_disposition": {
            "same_background_q2_Z2_receiver": "NOT_ACTIVATED",
            "memory_redshift_recoil_positivity_particle_quantum": "NOT_REACHED",
        },
        "does_not_establish": [
            "any combined chain group, cohomology or contraction",
            "a descended detector map, rank or kernel",
            "physical rod, emitter, detector-record or memory classes",
            "a q2/Z2 receiver, redshift, recoil, positivity, particle or quantum claim",
        ],
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-repaired112-physical-reduction-and-detector-rank-not-activated-v1",
        "result_id": "BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED",
        "setting_id": values["pushout_disposition"]["setting_id"],
        "claim_status": "CERTIFIED_NOT_ACTIVATED_PHYSICAL_REDUCTION_FROM_NONDEFINED_PUSHOUT",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha(path)}
            for name, path in DEPS.items()
        },
        "payload_ref": {
            "path": str(X.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical(payload),
        },
        "activation_gate": payload["activation_gate"],
        "reduction_disposition": payload["contraction_and_pairing_disposition"],
        "detector_disposition": payload["observer_class_disposition"],
        "next_gate": "A_GENUINELY_NILPOTENT_COMBINED_UNARY_MUST_EXIST_BEFORE_PHYSICAL_REDUCTION_CAN_BE_REOPENED",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE NOT_ACTIVATED disposition imports the terminal post-repair apparatus-pushout certificate and its complete replacement-112 repair no-go by content hash. The fresh pushout is NONDEFINED and exports neither a combined row count nor a nilpotent combined q1. A method-distinct replay uses the serialized canonical correction-only and target-only equations: their two-by-two augmented minor has the certified nonzero determinant, reproducing coefficient rank one versus augmented rank two, while background preservation leaves correction dimension zero. Therefore there is no chain complex on which generic-smooth, compact-support or spatial-zero-mode kernels and images could be formed. The homological projection pi_cl, inclusion, homotopy, contraction identities, descended odd pairing, radical, inertia and reduced real/K_Berger actions are all NO_CERTIFIED_MAP. In particular, no rod, polarization, emitter, detector-record or persistent-memory row is promoted to a physical class, and the two-record detector map has neither a descended rank nor a kernel. The standalone material-parent coordinate selection remains exactly rank two, but it is a separate linear carrier fact and is not evidence for a combined physical observable. The pre-repair 160-row reduction is a different terminal carrier and is not imported. No q2/Z2 receiver, memory, redshift, recoil, positivity, particle or quantum claim is made. Physical reduction may be reopened only after a genuinely nilpotent same-background combined unary is serialized and independently verified."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_repaired112_physical_reduction_and_detector_rank_not_activated --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_repaired112_physical_reduction_and_detector_rank_not_activated",
            "producer_source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Repaired-112 physical reduction and detector-rank disposition

Physical reduction is `NOT_ACTIVATED`: the terminal fresh apparatus pushout is `NONDEFINED`, so there is no combined chain complex on which to compute kernels, images, contraction data, descended pairing or detector classes.  An independent exact replay reconstructs the nonzero two-equation augmented determinant and the rank-one/rank-two inconsistency.  The standalone material coordinate detector remains rank two, but it is not a combined physical observable.

CLOSE-OUT: OBSTRUCTED — no nilpotent combined unary exists, so physical cohomology and the descended two-record detector rank are not mathematically defined
EVIDENCE: closed_universe_observers/certificates/BERGER_REPAIRED112_PHYSICAL_REDUCTION_AND_DETECTOR_RANK_NOT_ACTIVATED.json
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        X.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        C.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
