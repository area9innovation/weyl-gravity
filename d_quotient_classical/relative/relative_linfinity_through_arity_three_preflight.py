#!/usr/bin/env python3
"""Fail-closed receiver for the compact-product relative L-infinity problem."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-linfinity-through-arity-three-preflight.md"
TRIANGLE_SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-triangle-input-v2.schema.json"
INPUT_SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-product-taylor-input-v2.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-product-pbw-payload-v1.schema.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-through-arity-three-preflight-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_relative_linfinity_through_arity_three_preflight.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_relative_linfinity_through_arity_three_preflight.py"

TRIANGLE_CANDIDATES = (
    ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_v1.json",
)
EINSTEIN_CANDIDATES = (
    ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
    ROOT / "bridge/certificates/einstein_maxwell_product_linfinity_through_arity_three_v1.json",
)
WEYL_CANDIDATES = (
    ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
    ROOT / "bridge/certificates/weyl_maxwell_product_linfinity_through_arity_three_v1.json",
)
TRIANGLE_FLAGS = (
    "OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS",
    "SUPPORT_LOCAL_MAPPING_COFIBER",
    "GLOBAL_ENDPOINTS_INCLUDED",
    "THREE_ACTION_DERIVED_FORMS_EXPORTED",
    "GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED",
    "H_PRODUCT_EQUIVARIANT",
    "INDEPENDENT_VERIFIER_PASS",
)
TAYLOR_FLAGS = (
    "FULL_BV_ROWS",
    "SUPPORT_LOCAL",
    "ACTION_DERIVED",
    "EXECUTABLE_PBW_PAYLOAD",
    "CYCLIC_PAIRING_VERIFIED",
    "Q1_Q2_IDENTITY_VERIFIED",
    "ARITY_THREE_IDENTITY_VERIFIED",
    "H_PRODUCT_EQUIVARIANT",
    "INDEPENDENT_VERIFIER_PASS",
)
DEPENDENCIES = {
    "source_transfer_dictionary": ROOT / "d_quotient_classical/certificates/NONLINEAR_SOURCE_TRANSFER_TANGENT_CONE_DICTIONARY_V1.json",
    "finite_harmonic_tangent_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "berger_filtered_ell3_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json",
    "generic_cyclic_map_inertia_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json",
}
BACKGROUND_ID = "compact_magnetic_Plebanski_Hacyan_product"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _rational(value: str) -> sp.Rational:
    try:
        parsed = sp.Rational(value)
    except Exception as error:
        raise ValueError(f"coefficient is not rational: {value}") from error
    if not parsed.is_Rational:
        raise ValueError(f"coefficient escaped Q: {value}")
    return parsed


def _artifact(path: Path, value: Mapping[str, object]) -> dict[str, str]:
    return {"result_id": str(value["result_id"]), "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}


def validate_triangle(value: Mapping[str, object], *, verify_artifacts: bool = True) -> None:
    schema = _load(TRIANGLE_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value.get("result_id") != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1":
        raise ValueError("relative triangle result id drifted")
    if value.get("claim_status") not in {"CERTIFIED", "THEOREM_FROZEN", "CERTIFIED_OFF_SHELL_LINEAR_TRIANGLE"}:
        raise ValueError("relative triangle is not certified")
    if value.get("background_id") != BACKGROUND_ID:
        raise ValueError("relative triangle is not on the compact-product interaction background")
    missing = [flag for flag in TRIANGLE_FLAGS if value["acceptance_flags"].get(flag) is not True]
    if missing:
        raise ValueError("relative triangle misses acceptance flags: " + ", ".join(missing))
    disposition = value["pairing_disposition"]
    if disposition != {
        "triangle_kind": "NONCYCLIC_THREE_FORM",
        "standard_pairing_cyclic_map_exists": False,
        "three_forms_kept_distinct": True,
    }:
        raise ValueError("relative triangle does not preserve the noncyclic three-form disposition")
    obstruction = value["triangle_artifacts"]["generic_cyclic_map_inertia_obstruction"]
    if obstruction["result_id"] != "EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1":
        raise ValueError("relative triangle does not pin the generic cyclic-map inertia obstruction")
    if verify_artifacts:
        for artifact in value["triangle_artifacts"].values():
            path = ROOT / artifact["path"]
            if not path.is_file() or _sha256(path) != artifact["sha256"]:
                raise ValueError(f"triangle artifact drifted: {artifact['path']}")


def validate_taylor(value: Mapping[str, object], *, expected_result_id: str, expected_theory: str, verify_artifacts: bool = True) -> None:
    schema = _load(INPUT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["result_id"] != expected_result_id or value["theory_id"] != expected_theory:
        raise ValueError("product Taylor payload is routed to the wrong theory")
    missing = [flag for flag in TAYLOR_FLAGS if value["acceptance_flags"].get(flag) is not True]
    if missing:
        raise ValueError("product Taylor payload misses acceptance flags: " + ", ".join(missing))
    expected_kinds = {
        "row_layout": "row_layout",
        "action": "action",
        "q1": "operation",
        "q2": "operation",
        "q3": "operation",
        "pairing": "pairing",
        "independent_verifier": "independent_verifier",
        "verification_receipt": "verification_receipt",
    }
    for name, kind in expected_kinds.items():
        if value["taylor_artifacts"][name]["kind"] != kind:
            raise ValueError(f"Taylor artifact has wrong kind: {name}")
    if verify_artifacts:
        payload_schema = _load(PAYLOAD_SCHEMA)
        Draft202012Validator.check_schema(payload_schema)
        payloads: dict[str, dict] = {}
        for name, artifact in value["taylor_artifacts"].items():
            path = ROOT / artifact["path"]
            if not path.is_file() or _sha256(path) != artifact["sha256"]:
                raise ValueError(f"Taylor artifact drifted: {artifact['path']}")
            if name in {"row_layout", "action", "q1", "q2", "q3", "pairing"}:
                payload = _load(path)
                Draft202012Validator(payload_schema).validate(payload)
                if payload["result_id"] != artifact["result_id"]:
                    raise ValueError(f"Taylor artifact result id drifted: {name}")
                if payload["theory_id"] != expected_theory or payload["background_id"] != BACKGROUND_ID:
                    raise ValueError(f"Taylor artifact scope drifted: {name}")
                if payload["carrier_id"] != value["carrier_id"]:
                    raise ValueError(f"Taylor artifact carrier drifted: {name}")
                payloads[name] = payload
        contract = value["executable_contract"]
        row_layout = payloads["row_layout"]["content"]
        row_count = contract["row_count"]
        if row_count != row_layout["row_count"] or len(row_layout["rows"]) != row_count:
            raise ValueError("row-layout count drifted")
        indices = [row["index"] for row in row_layout["rows"]]
        if sorted(indices) != list(range(row_count)) or len({row["row_id"] for row in row_layout["rows"]}) != row_count:
            raise ValueError("row layout is not a complete uniquely named index set")
        if any(row["dual_row"] >= row_count for row in row_layout["rows"]):
            raise ValueError("row-layout dual index escaped the carrier")
        rows_by_index = {row["index"]: row for row in row_layout["rows"]}
        if any(rows_by_index[row["dual_row"]]["dual_row"] != row["index"] for row in row_layout["rows"]):
            raise ValueError("row-layout duality is not involutive")
        if contract["row_layout_sha256"] != value["taylor_artifacts"]["row_layout"]["sha256"]:
            raise ValueError("row-layout contract hash drifted")
        if contract["action_sha256"] != value["taylor_artifacts"]["action"]["sha256"]:
            raise ValueError("action contract hash drifted")
        operation_metadata: dict[str, tuple[int, int]] = {}
        for name, arity in (("q1", 1), ("q2", 2), ("q3", 3)):
            operation = payloads[name]["content"]
            if operation["arity"] != arity or operation["row_count"] != row_count:
                raise ValueError(f"{name} arity or carrier size drifted")
            if operation["term_count"] != len(operation["terms"]):
                raise ValueError(f"{name} term count drifted")
            profiles = operation.get("coefficient_profiles", [])
            if profiles:
                indices = [profile["index"] for profile in profiles]
                if sorted(indices) != list(range(len(profiles))):
                    raise ValueError(f"{name} coefficient profiles are not a contiguous index set")
            profile_jets = {
                profile["index"]: profile["coefficient_jets"]
                for profile in profiles
            }
            term_keys = set()
            maximum_order = 0
            maximum_input_word_order = 0
            maximum_coefficient_jet_order = 0
            for term in operation["terms"]:
                if term["output_row"] >= row_count or len(term["inputs"]) != arity:
                    raise ValueError(f"{name} has an ill-typed output or input arity")
                if any(item["row"] >= row_count for item in term["inputs"]):
                    raise ValueError(f"{name} input escaped the carrier")
                coefficient = _rational(term["coefficient"])
                if "coefficient_profile" in term:
                    if term["coefficient_profile"] not in profile_jets:
                        raise ValueError(f"{name} references a missing coefficient profile")
                    jets = profile_jets[term["coefficient_profile"]]
                else:
                    jets = term["coefficient_jets"]
                jet_keys = [tuple(item["word"]) for item in jets]
                if len(jet_keys) != len(set(jet_keys)) or any(tuple(sorted(key)) != key for key in jet_keys):
                    raise ValueError(f"{name} contains duplicate or nonnormal coefficient jets")
                jet_values = {tuple(item["word"]): _rational(item["coefficient"]) for item in jets}
                if any(value == 0 for value in jet_values.values()):
                    raise ValueError(f"{name} contains an explicit zero coefficient jet")
                if coefficient != jet_values.get((), sp.S.Zero):
                    raise ValueError(f"{name} base coefficient disagrees with its empty coefficient jet")
                maximum_coefficient_jet_order = max(
                    maximum_coefficient_jet_order,
                    max((len(word) for word in jet_keys), default=0),
                )
                key = (term["output_row"], tuple((item["row"], tuple(item["word"])) for item in term["inputs"]))
                if key in term_keys:
                    raise ValueError(f"{name} contains duplicate PBW support")
                term_keys.add(key)
                maximum_order = max(maximum_order, sum(len(item["word"]) for item in term["inputs"]))
                maximum_input_word_order = max(
                    maximum_input_word_order,
                    max(len(item["word"]) for item in term["inputs"]),
                )
            if maximum_order != operation["maximum_total_order"]:
                raise ValueError(f"{name} maximum derivative order drifted")
            declared_operation_order = operation.get("coefficient_jet_order")
            if expected_theory == "Weyl-Maxwell" and declared_operation_order is None:
                raise ValueError(f"{name} omits the Weyl coefficient-jet completeness order")
            if declared_operation_order is not None:
                if maximum_coefficient_jet_order > declared_operation_order:
                    raise ValueError(f"{name} contains a coefficient jet beyond its declared order")
                if contract.get("coefficient_jet_order") != declared_operation_order:
                    raise ValueError(f"{name} coefficient-jet order disagrees with the executable contract")
            operation_metadata[name] = (
                maximum_input_word_order,
                declared_operation_order
                if declared_operation_order is not None
                else maximum_coefficient_jet_order,
            )
        required_composition_order = max(order for order, _ in operation_metadata.values())
        available_composition_order = min(order for _, order in operation_metadata.values())
        if available_composition_order < required_composition_order:
            raise ValueError(
                "coefficient-jet depth is insufficient for independent PBW composition: "
                f"need {required_composition_order}, have {available_composition_order}"
            )
        pairing = payloads["pairing"]["content"]
        if pairing["row_count"] != row_count or pairing["term_count"] != len(pairing["terms"]):
            raise ValueError("pairing carrier size or term count drifted")
        if any(term["left_row"] >= row_count or term["right_row"] >= row_count for term in pairing["terms"]):
            raise ValueError("pairing row escaped the carrier")
        pairing_matrix = sp.zeros(row_count)
        for term in pairing["terms"]:
            pairing_matrix[term["left_row"], term["right_row"]] += _rational(term["coefficient"])
        if pairing_matrix.rank() != row_count:
            raise ValueError("declared cyclic pairing is degenerate")


def _select(candidates: tuple[Path, ...], validator) -> tuple[dict | None, Path | None]:
    present = [path for path in candidates if path.exists()]
    if len(present) > 1:
        raise ValueError("multiple authoritative candidates exist")
    if not present:
        return None, None
    value = _load(present[0])
    validator(value)
    return value, present[0]


def build() -> dict:
    triangle, triangle_path = _select(TRIANGLE_CANDIDATES, validate_triangle)
    einstein_id = "EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1"
    weyl_id = "WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1"
    einstein, einstein_path = _select(EINSTEIN_CANDIDATES, lambda value: validate_taylor(value, expected_result_id=einstein_id, expected_theory="Einstein-Maxwell"))
    weyl, weyl_path = _select(WEYL_CANDIDATES, lambda value: validate_taylor(value, expected_result_id=weyl_id, expected_theory="Weyl-Maxwell"))
    ready = all(value is not None for value in (triangle, einstein, weyl))

    dependencies = {name: _artifact(path, _load(path)) for name, path in DEPENDENCIES.items()}
    for name, path, value in (("relative_linear_triangle", triangle_path, triangle), ("einstein_product_taylor", einstein_path, einstein), ("weyl_product_taylor", weyl_path, weyl)):
        if value is not None:
            dependencies[name] = _artifact(path, value)
    source_paths = (Path(__file__), VERIFIER, TESTS, TRIANGLE_SCHEMA, INPUT_SCHEMA, PAYLOAD_SCHEMA, SCHEMA)
    status = {"relative_linear_triangle": "IMPORTED" if triangle else "MISSING", "einstein_product_q2_q3": "IMPORTED" if einstein else "MISSING", "weyl_product_q2_q3": "IMPORTED" if weyl else "MISSING"}
    value = {
        "schema": "pure-weyl-relative-linfinity-through-arity-three-preflight-v1",
        "result_id": "EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1",
        "result_state": "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY" if ready else "INPUT_BLOCKED_FULL_TRIANGLE_AND_PRODUCT_TAYLOR_PAYLOADS_MISSING",
        "lifecycle_status": "OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "setting": {"background_id": BACKGROUND_ID, "boundaries": "closed S1_L x S2 before final residual quotient", "generator": "H_product"},
        "input_status": status,
        "input_contracts": {
            "relative_triangle": {"required_result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1", "required_background_id": BACKGROUND_ID, "candidate_paths": [str(path.relative_to(ROOT)) for path in TRIANGLE_CANDIDATES], "required_flags": list(TRIANGLE_FLAGS)},
            "einstein_taylor": {"required_result_id": einstein_id, "required_background_id": BACKGROUND_ID, "candidate_paths": [str(path.relative_to(ROOT)) for path in EINSTEIN_CANDIDATES], "required_flags": list(TAYLOR_FLAGS)},
            "weyl_taylor": {"required_result_id": weyl_id, "required_background_id": BACKGROUND_ID, "candidate_paths": [str(path.relative_to(ROOT)) for path in WEYL_CANDIDATES], "required_flags": list(TAYLOR_FLAGS)},
            "triangle_schema": {"path": str(TRIANGLE_SCHEMA.relative_to(ROOT)), "sha256": _sha256(TRIANGLE_SCHEMA)},
            "taylor_schema": {"path": str(INPUT_SCHEMA.relative_to(ROOT)), "sha256": _sha256(INPUT_SCHEMA)},
            "taylor_payload_schema": {"path": str(PAYLOAD_SCHEMA.relative_to(ROOT)), "sha256": _sha256(PAYLOAD_SCHEMA)},
        },
        "dependency_refs": dependencies,
        "required_computation": [
            "Delta2=q2_Weyl(iota,iota)-iota*q2_Einstein on every declared channel",
            "exact iota2 primitive or normalized cofiber obstruction witness",
            "complete arity-three defect including q3, q2*iota2 and iota2*q2 terms",
            "exact iota3 primitive or normalized obstruction witness",
            "EE_to_X, EX_to_E_plus_X and XX_to_E_plus_X channel table",
            "H_product equivariance and action on cohomology with the three forms tracked separately",
            "deformation nontriviality or displayed admissible removal without asserting a cyclic quasi-equivalence",
        ],
        "scope_guard": {
            "berger_tensors_eligible": False,
            "reason": "The certified Berger q2/q3/ell3 tensors live on a different background and carrier.",
            "berger_filtered_obstruction_preserved": True,
            "q4_authorized": False,
        },
        "claim_flags": {
            "PREFLIGHT_READY": True,
            "ALL_SCIENTIFIC_INPUTS_IMPORTED": ready,
            "RELATIVE_ARITY_TWO_DEFECT_COMPUTED": False,
            "RELATIVE_ARITY_THREE_DEFECT_COMPUTED": False,
            "COHOMOLOGY_OPERATION_DECIDED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "Q4_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPUTE_RELATIVE_ARITY_TWO_AND_THREE_DEFECTS" if ready else "SUPPLY_FULL_TRIANGLE_AND_SAME_BACKGROUND_PRODUCT_Q2_Q3_PAYLOADS",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths},
        "verification_commands": [
            "PYTHONPATH=. python3 -m d_quotient_classical.relative.relative_linfinity_through_arity_three_preflight --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/relative/verify_relative_linfinity_through_arity_three_preflight.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.relative.tests.test_relative_linfinity_through_arity_three_preflight -v",
            "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-product-taylor-input-v2.schema.json",
            "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-product-pbw-payload-v1.schema.json",
            "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-triangle-input-v2.schema.json",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-through-arity-three-preflight-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1.json",
        ],
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {
                "commands": [
                    "python3 -m py_compile <scoped relative preflight Python paths>",
                    "python3 -m json.tool <scoped relative preflight JSON schemas>",
                    "git diff --cached --check",
                ],
                "status": "PASS",
            },
            "tier_1": {
                "commands_and_elapsed_seconds": [
                    {"command": "PYTHONPATH=. python3 -m d_quotient_classical.relative.relative_linfinity_through_arity_three_preflight --check --guards", "elapsed_seconds": 0.39},
                    {"command": "PYTHONPATH=. python3 d_quotient_classical/relative/verify_relative_linfinity_through_arity_three_preflight.py", "elapsed_seconds": 0.35},
                    {"command": "PYTHONPATH=. python3 -m unittest d_quotient_classical.relative.tests.test_relative_linfinity_through_arity_three_preflight -v", "elapsed_seconds": 0.62},
                    {"command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-product-taylor-input-v2.schema.json", "elapsed_seconds": 1.46},
                    {"command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-product-pbw-payload-v1.schema.json", "elapsed_seconds": 1.22},
                    {"command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-triangle-input-v2.schema.json", "elapsed_seconds": 1.06},
                    {"command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-linfinity-through-arity-three-preflight-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1.json", "elapsed_seconds": 1.09},
                ],
                "status": "PASS",
            },
            "tier_2": {
                "commands_and_elapsed_seconds": [
                    {"command": "PYTHONPATH=. python3 -m d_quotient_classical.atlas.generate_nonlinear_atlas_fragment --check", "elapsed_seconds": 0.18},
                    {"command": "PYTHONPATH=. python3 residual_atlas/validate_fragment.py d_quotient_classical/atlas/nonlinear-atlas-fragment.json", "elapsed_seconds": 0.12},
                    {"command": "PYTHONPATH=. python3 -m unittest d_quotient_classical.atlas.tests.test_nonlinear_atlas_fragment -v", "elapsed_seconds": 0.56},
                ],
                "status": "PASS",
            },
            "tier_3": {
                "status": "NOT_RUN",
                "reason": "No shared core algebra, theorem lifecycle promotion, freeze, release or publication boundary changed.",
            },
        },
        "claim_boundary": "This preflight prepares the compact-product relative L_infinity calculation but does not substitute sectoral solution cofibers or selected D^2E source fixtures for the full off-shell triangle and complete same-background Einstein/Weyl q2,q3 payloads. Berger tensors are explicitly ineligible. Until all three inputs arrive, Delta2, the arity-three morphism defect, cohomology survival, cyclic deformation nontriviality and admissible removal remain NO_CERTIFIED_MAP or OPEN. The Berger filtered-cyclic ell3 obstruction is preserved and q4 is not authorized.",
    }
    verify(value)
    return value


def verify(value: Mapping[str, object]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    ready = all(status == "IMPORTED" for status in value["input_status"].values())
    if value["claim_flags"]["ALL_SCIENTIFIC_INPUTS_IMPORTED"] is not ready:
        raise ValueError("input readiness drifted")
    expected_state = "INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY" if ready else "INPUT_BLOCKED_FULL_TRIANGLE_AND_PRODUCT_TAYLOR_PAYLOADS_MISSING"
    expected_gate = "COMPUTE_RELATIVE_ARITY_TWO_AND_THREE_DEFECTS" if ready else "SUPPLY_FULL_TRIANGLE_AND_SAME_BACKGROUND_PRODUCT_Q2_Q3_PAYLOADS"
    if value["result_state"] != expected_state or value["next_gate"] != expected_gate:
        raise ValueError("input lifecycle and next gate drifted")
    if any(value["claim_flags"][flag] for flag in ("RELATIVE_ARITY_TWO_DEFECT_COMPUTED", "RELATIVE_ARITY_THREE_DEFECT_COMPUTED", "COHOMOLOGY_OPERATION_DECIDED", "CYCLIC_DEFORMATION_CLASS_DECIDED", "Q4_AUTHORIZED", "QUANTUM_CLAIM")):
        raise ValueError("preflight promoted a downstream claim")
    if value["scope_guard"]["berger_tensors_eligible"] or not value["scope_guard"]["berger_filtered_obstruction_preserved"]:
        raise ValueError("cross-background scope guard drifted")
    for dependency in value["dependency_refs"].values():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency hash drifted: {dependency['path']}")
    for path, digest in value["source_manifest"].items():
        if _sha256(ROOT / path) != digest:
            raise ValueError(f"source hash drifted: {path}")


def synthetic_taylor(result_id: str, theory_id: str) -> dict:
    kinds = {
        "row_layout": "row_layout",
        "action": "action",
        "q1": "operation",
        "q2": "operation",
        "q3": "operation",
        "pairing": "pairing",
        "independent_verifier": "independent_verifier",
        "verification_receipt": "verification_receipt",
    }
    schema_hash = _sha256(INPUT_SCHEMA)
    return {
        "schema": "pure-weyl-relative-linfinity-product-taylor-input-v2",
        "result_id": result_id,
        "claim_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theory_id": theory_id,
        "background_id": BACKGROUND_ID,
        "carrier_id": "synthetic_test_carrier",
        "coefficient_field": "Q",
        "executable_contract": {
            "operator_encoding": "sparse-multilinear-pbw-v1",
            "derivative_algebra": "coordinate-product-coefficient-jet-pbw-v1",
            "row_count": 1,
            "row_layout_sha256": schema_hash,
            "action_sha256": schema_hash,
            "q1_arity": 1,
            "q2_arity": 2,
            "q3_arity": 3,
            "pairing_arity": 2,
            "coefficient_jet_order": 4 if theory_id == "Weyl-Maxwell" else 2,
        },
        "taylor_artifacts": {name: {"result_id": f"synthetic_{name}", "kind": kind, "path": str(INPUT_SCHEMA.relative_to(ROOT)), "sha256": schema_hash} for name, kind in kinds.items()},
        "acceptance_flags": {flag: True for flag in TAYLOR_FLAGS},
        "claim_boundary": "Synthetic receiver fixture only; no scientific Taylor tensor.",
    }


def synthetic_triangle() -> dict:
    return {
        "schema": "pure-weyl-relative-linfinity-triangle-input-v2",
        "result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
        "claim_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theory_map": "Einstein-Maxwell_to_Weyl-Maxwell",
        "background_id": BACKGROUND_ID,
        "boundaries": "closed S1_L x S2 before final residual quotient",
        "carrier_id": "synthetic_test_relative_triangle",
        "coefficient_field": "Q(sqrt(3))",
        "triangle_artifacts": {
            name: {
                "result_id": (
                    "EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1"
                    if name == "generic_cyclic_map_inertia_obstruction"
                    else f"synthetic_{name}"
                ),
                "path": str(TRIANGLE_SCHEMA.relative_to(ROOT)),
                "sha256": _sha256(TRIANGLE_SCHEMA),
            }
            for name in (
                "source_q1",
                "target_q1",
                "inclusion",
                "projection_or_cofiber",
                "source_pairing",
                "target_pairing",
                "relative_pairing",
                "generic_cyclic_map_inertia_obstruction",
            )
        },
        "pairing_disposition": {
            "triangle_kind": "NONCYCLIC_THREE_FORM",
            "standard_pairing_cyclic_map_exists": False,
            "three_forms_kept_distinct": True,
        },
        "acceptance_flags": {flag: True for flag in TRIANGLE_FLAGS},
        "claim_boundary": "Synthetic receiver fixture only; no scientific relative triangle.",
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: Mapping[str, object]) -> str:
    return f"""# Einstein--Weyl relative L-infinity preflight

Result: `{value['result_state']}`.

The full noncyclic three-form relative triangle and both same-background
product Taylor payloads are required.  The Taylor handoff is now executable:
each theory must provide a complete row layout, the declared BV action,
sparse multilinear PBW tables for `q1`, `q2`, and `q3`, and the cyclic
pairing.  The receiver validates row bounds, arities, term counts, carrier
identity, background identity, action and layout hashes, and every artifact
hash.  It also requires the Weyl--Maxwell payload to declare coefficient jets
through at least order four, because the Bach unary row differentiates inner
coefficients four times during the independent `Q^2` replay.  Opaque hashes,
self-declared booleans, or a second-order coefficient-jet truncation no longer
satisfy the gate.

Sectoral cofibers and selected quadratic sources remain useful evidence but
do not satisfy this input gate. The standard-pairing cyclic correction is
obstructed, Berger tensors are rejected as cross-background inputs, and `q4`
remains unauthorized.
"""


def guards(value: Mapping[str, object]) -> None:
    fixture = synthetic_taylor("WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1", "Weyl-Maxwell")
    validate_taylor(fixture, expected_result_id=fixture["result_id"], expected_theory="Weyl-Maxwell", verify_artifacts=False)
    for name, mutate in (
        ("Berger background", lambda item: item.__setitem__("background_id", "fixed_rational_positive_Berger_clock")),
        ("missing arity three", lambda item: item["acceptance_flags"].__setitem__("ARITY_THREE_IDENTITY_VERIFIED", False)),
    ):
        mutant = deepcopy(fixture)
        mutate(mutant)
        try:
            validate_taylor(mutant, expected_result_id=fixture["result_id"], expected_theory="Weyl-Maxwell", verify_artifacts=False)
        except Exception:
            continue
        raise ValueError(f"mutation accepted: {name}")
    triangle = synthetic_triangle()
    validate_triangle(triangle)
    for name, mutate in (
        ("triangle background", lambda item: item.__setitem__("background_id", "fixed_rational_positive_Berger_clock")),
        ("triangle artifact hash", lambda item: item["triangle_artifacts"]["inclusion"].__setitem__("sha256", "0" * 64)),
        ("generic inertia obstruction ignored", lambda item: item["acceptance_flags"].__setitem__("GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED", False)),
        ("cyclic triangle silently restored", lambda item: item["pairing_disposition"].__setitem__("standard_pairing_cyclic_map_exists", True)),
    ):
        mutant = deepcopy(triangle)
        mutate(mutant)
        try:
            validate_triangle(mutant)
        except Exception:
            continue
        raise ValueError(f"mutation accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report(value))
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report(value)):
        raise ValueError("relative L-infinity preflight outputs drifted")
    if args.guards:
        guards(value)
    print("EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
