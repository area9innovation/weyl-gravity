#!/usr/bin/env python3
"""Independent source replay for the strict polarized-Bach benchmark contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.json"
SOURCES = {
    "linear": ROOT / "covariant_completion/certificates/linearized_bach.json",
    "lift": ROOT / "quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json",
    "direct": ROOT / "quantum-weyl/transfer/certificates/HT1B_DIRECT_CURVATURE_AUDIT.json",
    "ppwave": ROOT / "bridge/certificates/ppwave_bach_branch_closure.json",
    "nariai": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json",
    "antifield": ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
    "partial": ROOT / "quantum-weyl/classical_import/certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json",
}
FIXTURE_IDS = (
    "CYLINDER_LINEARIZED_ACTION_NORMALIZATION",
    "CYLINDER_HT1B_NONZERO_MODE_CHANNELS",
    "CYLINDER_DIRECT_CURVATURE_PROBES",
    "PPWAVE_ARBITRARY_PROFILE_ZERO_SLICE",
    "NARIAI_TRANSVERSE_HESSIAN_VARIATION",
)
GATE_IDS = (
    "TYPE_AND_EXACTNESS",
    "ARBITRARY_INPUT_COMPLETENESS",
    "POLARIZATION_SYMMETRY",
    "SUPPORT_INTERSECTION",
    "DIFFERENTIATED_WEYL_IDENTITY",
    "DIFFERENTIATED_DIFF_NOETHER_IDENTITY",
    "CYLINDER_UNARY_NORMALIZATION",
    "PPWAVE_ZERO_SLICE",
    "HT1B_NONZERO_CHANNELS",
    "NARIAI_PORTABILITY",
)
PIPELINE = (
    (1, "metric_inverse", 0),
    (2, "levi_civita_connection", 1),
    (3, "curvature", 2),
    (4, "weyl_tensor", 2),
    (5, "bach_standard", 4),
    (6, "action_normalize", 4),
    (7, "raise_and_densitize", 4),
    (8, "polarized_coefficient", 4),
)
FALSE_FLAGS = {
    "GENERAL_ARBITRARY_INPUT_CYLINDER_BACH_KERNEL_AVAILABLE",
    "STRICT_HSTAR_Q2_ROW_PORTABLE",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = {name: load(path) for name, path in SOURCES.items()}
    if value.get("result_state") != "BENCHMARK_CONTRACT_CERTIFIED_GENERAL_KERNEL_ABSENT" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state/lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("top-level dependency boundary drift")

    target = value.get("target_contract", {})
    gstar = next((item for item in source["antifield"].get("generators", []) if item.get("symbol") == "g_star"), {})
    expected_output = {
        "symbol": "h_star",
        "component_count": 10,
        "tensor_type": gstar.get("tensor_type"),
        "form_degree": gstar.get("form_degree"),
        "Weyl_weight": gstar.get("Weyl_weight"),
    }
    if target.get("output") != expected_output:
        errors.append("metric-antifield output type is not source-replayed")
    if target.get("action_normalization") != "B_action=-2 B_standard" or target.get("maximum_metric_jet_order") != 4:
        errors.append("target normalization/jet bound drift")
    if "coefficient of a*b" not in target.get("taylor_convention", "") or "factor of 1/2" not in target.get("taylor_convention", ""):
        errors.append("polarized Taylor convention weakened")
    if "intersection" not in target.get("support_rule", ""):
        errors.append("support-local target rule weakened")

    pipeline = value.get("candidate_program_contract", [])
    actual_pipeline = tuple((item.get("order"), item.get("operation"), item.get("maximum_metric_jet_order")) for item in pipeline)
    if actual_pipeline != PIPELINE:
        errors.append("geometric candidate pipeline drift")
    bach = next((item for item in pipeline if item.get("operation") == "bach_standard"), {})
    if "nabla^c nabla^d C_acbd+(1/2)Ric^cd C_acbd" not in bach.get("output", ""):
        errors.append("standard Bach formula drift")
    density = next((item for item in pipeline if item.get("operation") == "raise_and_densitize"), {})
    if "sqrt(-g)" not in density.get("output", ""):
        errors.append("Euler density conversion absent")

    fixtures = value.get("fixture_ledger", [])
    if tuple(item.get("fixture_id") for item in fixtures) != FIXTURE_IDS:
        errors.append("fixture inventory/order drift")
        by_id: dict[str, dict[str, Any]] = {}
    else:
        by_id = {item["fixture_id"]: item for item in fixtures}
    if len(by_id) != len(fixtures):
        errors.append("fixture ids are not unique")

    linear = source["linear"]
    expected_linear = {
        "construction": linear.get("construction"),
        "normalization": linear.get("normalization"),
        "gauge_maximum_order": linear.get("gauge_jet_test", {}).get("maximum_order"),
        "principal_maximum_order": linear.get("principal_jet_test", {}).get("maximum_order"),
        "principal_tracefree_components": linear.get("principal_jet_test", {}).get("tracefree_input_components"),
    }
    if by_id.get(FIXTURE_IDS[0], {}).get("expected") != expected_linear:
        errors.append("linearized cylinder fixture drift")

    lift_channels = source["lift"].get("seed_payload", {}).get("direct_local_channels", [])
    expected_channels = [
        {key: item[key] for key in ("channel_id", "external_modes", "bilinear_taylor_convention", "local_radial_density", "integrated_taub_charge", "raw_residual_kernel_entry", "canonical_residual_kernel_entry")}
        for item in lift_channels
    ]
    cylinder_modes = by_id.get(FIXTURE_IDS[1], {}).get("expected", {})
    if cylinder_modes != {"channel_count": 2, "channels": expected_channels}:
        errors.append("nonzero cylinder channel fixture drift")
    if len(expected_channels) != 2 or any(channel["integrated_taub_charge"] == "Integer(0)" for channel in expected_channels):
        errors.append("nonzero cylinder source assumption failed")

    direct_probes = source["direct"].get("direct_probe_results", [])
    expected_probes = [
        {key: item[key] for key in ("side", "reverse", "probe", "local_radial_density", "integrated_action_coefficient")}
        for item in direct_probes
    ]
    direct_fixture = by_id.get(FIXTURE_IDS[2], {}).get("expected", {})
    if direct_fixture != {"probe_count": 8, "probes": expected_probes}:
        errors.append("direct-curvature probe fixture drift")
    if sum(item["integrated_action_coefficient"] != "Integer(0)" for item in expected_probes) != 4:
        errors.append("direct-probe nonzero/zero partition drift")
    if source["direct"].get("checks", {}).get("arbitrary_input_bilinear_bach_tensor") != "NOT_COMPUTED":
        errors.append("direct source no longer has the recorded arbitrary-input gap")

    pp = source["ppwave"].get("restricted_nonlinear_tensor", {})
    expected_pp = {
        "taylor_convention": pp.get("Taylor_convention"),
        "q2_entries": pp.get("q2_entries"),
        "all_higher_taylor_coefficients_zero": pp.get("all_higher_Taylor_coefficients_zero"),
    }
    if by_id.get(FIXTURE_IDS[3], {}).get("expected") != expected_pp or not pp.get("q2_identically_zero_for_arbitrary_ppwave_profiles"):
        errors.append("pp-wave arbitrary-profile zero fixture drift")

    nariai = source["nariai"].get("exact_data", {})
    direct = nariai.get("direct_action_leading_derivation", {})
    full = nariai.get("identified_full_action_variation", {})
    noether = nariai.get("lower_order_noether_completion", {})
    expected_nariai = {
        "action_normalization": direct.get("action_normalization"),
        "orders_above_two_absent": direct.get("orders_above_two_absent"),
        "authoritative_order_two_sha256": direct.get("authoritative_order_two", {}).get("sha256"),
        "full_variation_sha256": full.get("sha256"),
        "full_variation_nonzero_coefficients": full.get("nonzero_coefficients"),
        "coefficient_map_shape": noether.get("coefficient_map_shape"),
        "coefficient_map_rank": noether.get("coefficient_map_rank"),
        "unique_completion": noether.get("unique_completion"),
    }
    if by_id.get(FIXTURE_IDS[4], {}).get("expected") != expected_nariai:
        errors.append("Nariai restricted Hessian-variation fixture drift")
    if expected_nariai["coefficient_map_shape"] != [60, 45] or expected_nariai["coefficient_map_rank"] != 45:
        errors.append("Nariai uniqueness control drift")

    evidence_classes = {item.get("evidence_class") for item in fixtures}
    if len(evidence_classes) != 5:
        errors.append("fixture evidence classes collapsed")
    for item in fixtures:
        if not item.get("cannot_establish") or "LORENTZIAN-CAUSAL" in item.get("dependency_tags", []):
            errors.append(f"fixture boundary promoted: {item.get('fixture_id')}")

    gates = value.get("acceptance_gates", [])
    if tuple(item.get("gate_id") for item in gates) != GATE_IDS or len({item.get("gate_id") for item in gates}) != len(gates):
        errors.append("acceptance gate inventory drift")
    if any(item.get("status") != "NOT_RUN_NO_GENERAL_EVALUATOR" for item in gates):
        errors.append("acceptance gate promoted without evaluator")
    weyl = next((item for item in gates if item.get("gate_id") == "DIFFERENTIATED_WEYL_IDENTITY"), {})
    diff = next((item for item in gates if item.get("gate_id") == "DIFFERENTIATED_DIFF_NOETHER_IDENTITY"), {})
    if "two unary cross terms" not in weyl.get("requirement", "") or "connection and density variations" not in diff.get("requirement", ""):
        errors.append("nonlinear Noether identity contract weakened")

    diagnosis = value.get("coverage_diagnosis", {})
    if diagnosis.get("general_arbitrary_input_cylinder_tensor_available") is not False or len(diagnosis.get("why_not_reconstructible", [])) != 4:
        errors.append("coverage gap improperly closed")
    if diagnosis.get("nonzero_cylinder_channel_count") != 2 or diagnosis.get("direct_curvature_probe_count") != 8:
        errors.append("coverage counts drift")
    stages = value.get("implementation_stages", [])
    if len(stages) != 5 or any(item.get("status") != "OPEN" for item in stages):
        errors.append("implementation stage promoted")

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "target_contract_sha256": digest(target),
        "candidate_program_contract_sha256": digest(pipeline),
        "fixture_ledger_sha256": digest(fixtures),
        "acceptance_gates_sha256": digest(gates),
        "coverage_diagnosis_sha256": digest(diagnosis),
        "implementation_stages_sha256": digest(stages),
    }
    if hashes != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(SOURCES):
        errors.append("provenance input count drift")
    for item in provenance:
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")

    flags = value.get("claim_flags", {})
    if flags.get("MULTI_FIXTURE_BENCHMARK_CONTRACT_CERTIFIED") is not True or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim boundary flag promoted")
    if source["partial"].get("claim_flags", {}).get("SIXTH_METRIC_ANTIFIELD_ROW_PORTABLE") is not False:
        errors.append("partial q2 source boundary changed")
    return errors


def main() -> int:
    value = load(RESULT)
    errors = check(value)
    print("STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - 5 distinct fixture classes source-replayed with exact hashes")
        print("  - 10 evaluator gates remain fail closed until a general kernel exists")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
