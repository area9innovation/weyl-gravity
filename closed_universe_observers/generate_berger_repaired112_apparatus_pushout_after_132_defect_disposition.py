#!/usr/bin/env python3
"""Emit the fresh apparatus-pushout disposition after the complete repair no-go."""
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
C = P / "certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION.json"
X = P / "certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION_PAYLOAD.json"
SCHEMA = P / "schema/berger-repaired112-apparatus-pushout-after-132-defect-disposition-v1.schema.json"
REPORT = P / "reports/berger-repaired112-apparatus-pushout-after-132-defect-disposition.md"
DEPS = {
    "repair_no_go": P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO.json",
    "repair_no_go_payload": P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO_PAYLOAD.json",
    "material_parent": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE.json",
    "material_parent_payload": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE_PAYLOAD.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def validate_imports(values: dict[str, dict[str, Any]]) -> None:
    repair = values["repair_no_go"]
    repair_payload = values["repair_no_go_payload"]
    material = values["material_parent"]
    material_payload = values["material_parent_payload"]
    if sha(DEPS["repair_no_go_payload"]) != repair["payload_ref"]["sha256"]:
        raise AssertionError("repair no-go payload hash mismatch")
    if sha(DEPS["material_parent_payload"]) != material["payload_ref"]["sha256"]:
        raise AssertionError("material-parent payload hash mismatch")
    if repair["atlas_status"] != "OBSTRUCTED":
        raise AssertionError("complete repair theorem is not terminally obstructed")
    if repair["gate_results"]["complete_repaired_replacement112_q1"] != "NO_CERTIFIED_MAP":
        raise AssertionError("repair theorem unexpectedly exports a source differential")
    if repair_payload["nilpotency_equation"]["solution_status"] != "INCONSISTENT":
        raise AssertionError("complete repair coefficient system is not inconsistent")
    if repair_payload["background_preservation_gate"]["admissible_dimension"] != 0:
        raise AssertionError("fixed-background repair space is not exhausted")
    gates = material["gate_results"]
    if material["atlas_status"] != "CERTIFIED":
        raise AssertionError("material parent is not certified")
    if gates["complete_executable_material_parent56_internal_q1"] != "CERTIFIED":
        raise AssertionError("material-parent q1 is not certified")
    if gates["rank2_detector_chain_map"] != "CERTIFIED":
        raise AssertionError("material-parent detector map is not certified")
    if material_payload["carrier"]["row_count"] != 56:
        raise AssertionError("material-parent row count drifted")


def reject_source_success_mutation(values: dict[str, dict[str, Any]]) -> None:
    mutated = copy.deepcopy(values)
    mutated["repair_no_go"]["gate_results"]["complete_repaired_replacement112_q1"] = "CERTIFIED"
    try:
        validate_imports(mutated)
    except AssertionError:
        return
    raise AssertionError("mutated source success was accepted")


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    validate_imports(values)
    reject_source_success_mutation(values)
    repair = values["repair_no_go"]
    rp = values["repair_no_go_payload"]
    material = values["material_parent"]
    mp = values["material_parent_payload"]
    equation = rp["nilpotency_equation"]
    target = equation["target_only_equation"]
    correction = equation["correction_only_equation"]
    return {
        "schema": "closed-universe-berger-repaired112-apparatus-pushout-after-132-defect-disposition-payload-v1",
        "result_id": "BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION_PAYLOAD",
        "imported_terminal_dispositions": {
            "replacement112_repair": repair["claim_status"],
            "replacement112_atlas_status": repair["atlas_status"],
            "material_parent56": material["claim_status"],
            "material_parent56_atlas_status": material["atlas_status"],
        },
        "category_of_complexes_gate": {
            "required_source_object": "(V_112,q1_repaired) with q1_repaired^2=0",
            "replacement_source_object": "NONEXISTENT_IN_DECLARED_REPLACEMENT_FAMILY",
            "material_parent_object": "CERTIFIED_56_ROW_CHAIN_COMPLEX",
            "relative_detector_interface": "CERTIFIED_FOUR_BLOCK_ACTION_HESSIAN_CHAIN_INTERFACE",
            "identification_relation": "NOT_REACHED",
            "derived_combined_row_count": "NO_CERTIFIED_MAP",
            "apparatus_pushout": "NONDEFINED",
            "reason": "a pushout in chain complexes cannot be formed when one leg has no nilpotent source object",
        },
        "exact_nonactivation_separator": {
            "scalar_equation_count": equation["scalar_equation_count"],
            "coefficient_matrix_rank": equation["coefficient_matrix_rank"],
            "augmented_matrix_rank": equation["augmented_matrix_rank"],
            "canonical_augmented_determinant": equation["canonical_two_equation_augmented_determinant"],
            "target_only_equation": target,
            "correction_only_equation": correction,
            "background_preserving_correction_dimension": rp["background_preservation_gate"]["admissible_dimension"],
            "background_first_variation_anchor": rp["background_preservation_gate"]["specialized_anchor_coefficient"],
        },
        "material_parent_survivor": {
            "row_count": mp["carrier"]["row_count"],
            "internal_q1": "CERTIFIED",
            "signed_pairing_rank": mp["carrier"]["pairing_rank"],
            "detector_coordinate_rank": 2,
            "external_readout_block_count": mp["external_mixed_readout_interface"]["entry_count"],
            "combined_interpretation": "SEPARATE_ONLY",
        },
        "minimal_escape_signature": {
            "exhausted_action_hessian_amplitudes": rp["complete_local_action_hessian_ansatz"]["raw_block_amplitudes"],
            "fixed_control_blocks": rp["complete_local_action_hessian_ansatz"]["fixed_degree_zero_control_blocks"],
            "minimum_new_coefficient_image_dimension": 1,
            "required_new_column_properties": [
                "not proportional to the exhausted common-action commutator column",
                "nonzero on the inherited h_hat_star_00 <- sigma, time -2, j*x0^2 target-only coordinate",
                "admits a combination cancelling the h_hat_star_00 <- c_spatial_1, time -2, j*x0*x1 correction-only coordinate",
                "lies in the kernel of all remaining exact nilpotency, cyclicity, real, K_Berger and support constraints",
                "supplies a background-first-variation counterdirection so the combined correction can preserve the pinned background",
            ],
            "one_vertex_route": {
                "new_rows": 0,
                "required_type": "a genuinely new local invariant action-Hessian vertex outside S_nonrod-S_R,I6+S_R,H with the required coefficient-image and background signatures",
            },
            "one_pair_route": {
                "minimum_new_rows": 2,
                "field_row": "one real even degree-0 auxiliary carrier X in the K_Berger/support orbit of the separator",
                "antifield_row": "its real odd degree-1 BV dual X_plus",
                "required_path": "sigma(degree -1) -> X(degree 0) -> h_hat_star_00(degree 1), together with the pairing-dual transpose path",
                "action_requirement": "the path must be the Hessian of one local action and pass a principal-symbol/causality preflight",
            },
            "classification_status": "SIGNATURE_ONLY_NOT_A_VIABLE_EXTENSION",
            "next_classification_gate": "complete exact one-pair/one-vertex action-extension catalogue",
        },
        "nonactivation_disposition": {
            "replacement112_executable_q1": "NO_CERTIFIED_MAP",
            "apparatus_pushout": "NONDEFINED",
            "combined_q1_pairing_embeddings_quotient_real_K_detector_map": "NO_CERTIFIED_MAP",
            "physical_reduction": "NO_CERTIFIED_MAP",
            "detector_response_after_reduction": "NO_CERTIFIED_MAP",
            "memory_redshift_recoil_q2_q3_quantum": "NOT_REACHED",
        },
        "does_not_establish": [
            "a combined row count",
            "a repaired replacement unary",
            "a viable one-pair or one-vertex extension",
            "physical cohomology",
            "a reduced detector response",
            "memory, redshift, recoil, q2, q3 or quantum observer algebra",
        ],
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-repaired112-apparatus-pushout-after-132-defect-disposition-v1",
        "result_id": "BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION",
        "setting_id": values["repair_no_go"]["setting_id"],
        "claim_status": "CERTIFIED_NONACTIVATION_OF_APPARATUS_PUSHOUT_AFTER_COMPLETE_REPAIR_NO_GO",
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
        "gate_results": payload["nonactivation_disposition"],
        "exact_nonactivation_separator": payload["exact_nonactivation_separator"],
        "minimal_escape_signature": payload["minimal_escape_signature"],
        "next_gate": "CLASSIFY_THE_COMPLETE_ONE_PAIR_OR_ONE_VERTEX_ACTION_EXTENSION_BEFORE_REOPENING_THE_PUSHOUT",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE disposition imports by content hash the complete replacement-112 local action-Hessian repair no-go and the certified executable material-parent-56 unary with its typed external detector interface. The replacement leg has no nilpotent q1 in the declared family: its 4542-equation correction system has coefficient rank one and augmented rank two, the canonical two-equation augmentation has nonzero determinant, and background preservation leaves correction dimension zero. It is therefore not an object of the category of chain complexes, so a fresh apparatus pushout is NONDEFINED before any action-role identification relation, combined row count, pairing, embedding, quotient, real/K action or detector-smearing map can be generated. The 56-row material complex, rank-56 pairing, four relative readout blocks and rank-two coordinate detector remain certified but separate. Escaping the no-go requires at least one genuinely new action-Hessian coefficient-image direction: it must hit the inherited h_hat_star_00-from-sigma j*x0^2 coordinate, avoid or cancel the correction-only h_hat_star_00-from-c_spatial_1 direction, preserve the background and satisfy all cyclic, real, K_Berger and support identities. This may arise from a new invariant vertex or from at least one real degree-zero field with its degree-one BV dual; neither route is constructed here. No combined row count is assumed, physical reduction is not mathematically defined, and no detector, memory, redshift, recoil, q2, q3 or quantum claim is promoted."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_repaired112_apparatus_pushout_after_132_defect_disposition --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_repaired112_apparatus_pushout_after_132_defect_disposition",
            "producer_source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Repaired-112 apparatus pushout disposition after the 132-defect theorem

The fresh chain-complex pushout is `NONDEFINED`.  The complete declared replacement-112 repair theorem exports no nilpotent source differential, while the independently certified material-parent-56 complex remains a separate valid object.  Consequently no identification relation, combined row count, unary, pairing, embeddings, quotient, real/K actions or detector-smearing map is formed, and physical reduction is not mathematically defined.

The exact separator is the inherited 4,542-equation repair system: coefficient rank one, augmented rank two, with canonical nonzero augmented determinant `-1328324915314341/20393268025000000` and background-preserving correction dimension zero.  A successor must add at least one genuinely new action-Hessian coefficient-image direction.  It must hit the target-only `h_hat_star_00 <- sigma` `j*x0^2` coordinate, cancel the correction-only `h_hat_star_00 <- c_spatial_1` direction, and preserve cyclicity, reality, `K_Berger`, support and the pinned background.  The permitted next classification is one new invariant vertex or one real degree-zero field together with its degree-one BV dual; this disposition does not claim either is viable.

CLOSE-OUT: NO_CERTIFIED_MAP — the repaired replacement-112 source object does not exist in the complete declared family, so the apparatus pushout and physical reduction are nondefined
EVIDENCE: closed_universe_observers/certificates/BERGER_REPAIRED112_APPARATUS_PUSHOUT_AFTER_132_DEFECT_DISPOSITION.json
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
