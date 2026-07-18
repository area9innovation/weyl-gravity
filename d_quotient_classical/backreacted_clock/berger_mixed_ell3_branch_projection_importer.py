#!/usr/bin/env python3
"""Fail-closed importer for the branch map that activates Berger bridge 2.

Dependency tags: LOCAL-ALGEBRAIC, REDUCED-MODE.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA = ROOT / "d_quotient_classical/schema/berger-admissible-same-background-branch-map-v1.schema.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-mixed-ell3-branch-projection-importer-preflight-v1.schema.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-mixed-ell3-branch-projection-importer-preflight.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_mixed_ell3_branch_projection_importer.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_mixed_ell3_branch_projection_importer.py"
CANDIDATES = (
    ROOT / "d_quotient_classical/certificates/BERGER_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_V1.json",
    ROOT / "bridge/certificates/BERGER_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_V1.json",
)
DEPENDENCIES = {
    "mixed_ell3_filtered_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json",
    "source_transfer_dictionary": ROOT / "d_quotient_classical/certificates/NONLINEAR_SOURCE_TRANSFER_TANGENT_CONE_DICTIONARY_V1.json",
    "same_bundle_projector_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
}
REQUIRED_FLAGS = (
    "SAME_BACKGROUND_AS_INTERACTION",
    "EXPLICIT_CARRIER_CROSSWALK",
    "CHAIN_MAP_ALL_DECLARED_ROWS",
    "EINSTEIN_EXTRA_MAXWELL_BRANCH_MAPS",
    "GAUGE_AND_NONDYNAMICAL_DISPOSITION",
    "PAIRING_TRANSPORT_VERIFIED",
    "K_BERGER_EQUIVARIANT",
    "COHOMOLOGY_MAP_VERIFIED",
    "INDEPENDENT_VERIFIER_PASS",
)
REQUIRED_ARTIFACT_ROLES = (
    "carrier_crosswalk",
    "chain_map",
    "branch_inclusion_projection_or_cofiber",
    "pairing_transport",
    "gauge_nondynamical_disposition",
    "k_berger_equivariance",
    "cohomology_map",
    "independent_verifier",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate_candidate(value: Mapping[str, object], *, verify_artifacts: bool = True) -> None:
    schema = _load(INPUT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["result_id"] != "BERGER_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_V1":
        raise ValueError("branch-map result id drifted")
    if value["background_id"] != "fixed_rational_positive_Berger_clock":
        raise ValueError("branch map is not on the interaction background")
    flags = value["acceptance_flags"]
    missing = [flag for flag in REQUIRED_FLAGS if flags.get(flag) is not True]
    if missing:
        raise ValueError("branch map misses acceptance flags: " + ", ".join(missing))
    roles = {artifact["role"] for artifact in value["map_artifacts"]}
    missing_roles = [role for role in REQUIRED_ARTIFACT_ROLES if role not in roles]
    if missing_roles:
        raise ValueError("branch map misses evidence roles: " + ", ".join(missing_roles))
    if value["map_category"] == "REDUCED_MODE_NONLOCAL" and "REDUCED-MODE" not in value["dependency_tags"]:
        raise ValueError("nonlocal reduced-mode branch map lacks REDUCED-MODE dependency tag")
    interaction = value["interaction_dependency"]
    expected = DEPENDENCIES["mixed_ell3_filtered_obstruction"]
    if interaction["result_id"] != "BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1":
        raise ValueError("branch map is not bound to the landed interaction")
    if interaction["path"] != str(expected.relative_to(ROOT)) or interaction["sha256"] != _sha256(expected):
        raise ValueError("branch map does not pin the authoritative interaction bytes")
    if verify_artifacts:
        if _sha256(ROOT / interaction["path"]) != interaction["sha256"]:
            raise ValueError("interaction dependency hash drifted")
        for artifact in value["map_artifacts"]:
            path = ROOT / artifact["path"]
            if not path.is_file() or _sha256(path) != artifact["sha256"]:
                raise ValueError(f"branch-map artifact drifted: {artifact['path']}")


def _candidate() -> tuple[dict | None, Path | None]:
    present = [path for path in CANDIDATES if path.exists()]
    if len(present) > 1:
        raise ValueError("multiple authoritative branch-map candidates exist")
    if not present:
        return None, None
    value = _load(present[0])
    validate_candidate(value)
    return value, present[0]


def build() -> dict:
    dependencies = {}
    for name, path in DEPENDENCIES.items():
        value = _load(path)
        dependencies[name] = {
            "result_id": value["result_id"],
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        }
    candidate, candidate_path = _candidate()
    imported = candidate is not None
    if imported:
        dependencies["admissible_same_background_branch_map"] = {
            "result_id": candidate["result_id"],
            "path": str(candidate_path.relative_to(ROOT)),
            "sha256": _sha256(candidate_path),
        }
    source_paths = (Path(__file__), VERIFIER, TESTS, INPUT_SCHEMA, SCHEMA)
    value = {
        "schema": "pure-weyl-berger-mixed-ell3-branch-projection-importer-preflight-v1",
        "result_id": "BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1",
        "result_state": "BRIDGE_1_IMPORTED_BRIDGE_2_PROJECTION_READY" if imported else "INPUT_BLOCKED_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_MISSING",
        "lifecycle_status": "OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "active_bridge": {
            "order": 2,
            "name": "invariant interaction to physical branches",
            "activation_gate": "bridge 1 supplies an admissible same-background branch map",
            "status": "READY" if imported else "INPUT_BLOCKED",
        },
        "input_contract": {
            "required_result_id": "BERGER_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_V1",
            "schema_path": str(INPUT_SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(INPUT_SCHEMA),
            "candidate_paths": [str(path.relative_to(ROOT)) for path in CANDIDATES],
            "required_flags": list(REQUIRED_FLAGS),
            "required_artifact_roles": list(REQUIRED_ARTIFACT_ROLES),
            "accepted_map_categories": ["SUPPORT_LOCAL_MIXED_BUNDLE", "NONCONTRACTIBLE_COFIBER", "REDUCED_MODE_NONLOCAL"],
            "status": "IMPORTED" if imported else "MISSING",
        },
        "dependency_refs": dependencies,
        "downstream_disposition": {
            "projected_operation": "OPEN" if imported else "NO_CERTIFIED_MAP",
            "operation_on_cohomology": "OPEN" if imported else "NO_CERTIFIED_MAP",
            "cyclic_deformation_class": "OPEN" if imported else "NO_CERTIFIED_MAP",
            "admissible_redefinition": "OPEN" if imported else "NO_CERTIFIED_MAP",
            "q4": "NOT_AUTHORIZED",
        },
        "claim_flags": {
            "BRANCH_PROJECTION_IMPORTER_READY": True,
            "ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_IMPORTED": imported,
            "BRIDGE_2_ACTIVATED": imported,
            "PROJECTED_ELL3_COMPUTED": False,
            "COHOMOLOGY_OPERATION_DECIDED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "ADMISSIBLE_REDEFINITION_DISPLAYED": False,
            "Q4_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPUTE_PROJECTED_ELL2_ELL3_AND_INVARIANT_DISPOSITION" if imported else "SUPPLY_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_mixed_ell3_branch_projection_importer.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_mixed_ell3_branch_projection_importer.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_mixed_ell3_branch_projection_importer -v",
        ],
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {
                "status": "PASS",
                "commands_and_elapsed_seconds": [
                    {"command": "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_mixed_ell3_branch_projection_importer.py --check --guards", "elapsed_seconds": 0.53},
                    {"command": "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_mixed_ell3_branch_projection_importer.py", "elapsed_seconds": 1.15},
                    {"command": "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_mixed_ell3_branch_projection_importer d_quotient_classical.atlas.tests.test_nonlinear_atlas_fragment -v", "elapsed_seconds": 1.57},
                    {"command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true <two scoped schemas>", "elapsed_seconds": 3.10}
                ]
            },
            "tier_2_dependency_replay": {"status": "PASS", "command": "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json", "measured_elapsed_seconds_lower_bound": 300.01},
            "tier_3": {"status": "NOT_RUN", "reason": "No shared algebra, classical freeze, theorem lifecycle promotion, or release boundary changed."}
        },
        "claim_boundary": "This preflight prepares bridge 2 and imports only a schema-valid, content-addressed branch map on the exact Berger interaction background. The existing support-local same-bundle projector remains obstructed. Until bridge 1 supplies an admissible mixed-bundle, noncontractible-cofiber, or explicitly REDUCED-MODE map, projected ell2/ell3, cohomology survival, cyclic deformation nontriviality and removability are NO_CERTIFIED_MAP. It preserves the filtered-cyclic ell3 obstruction and does not authorize q4, particles, causality, QME promotion or quantum claims.",
    }
    verify(value)
    return value


def verify(value: Mapping[str, object]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    imported = value["input_contract"]["status"] == "IMPORTED"
    flags = value["claim_flags"]
    if flags["ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_IMPORTED"] is not imported or flags["BRIDGE_2_ACTIVATED"] is not imported:
        raise ValueError("bridge activation drifted")
    if any(flags[key] for key in ("PROJECTED_ELL3_COMPUTED", "COHOMOLOGY_OPERATION_DECIDED", "CYCLIC_DEFORMATION_CLASS_DECIDED", "ADMISSIBLE_REDEFINITION_DISPLAYED", "Q4_AUTHORIZED", "QUANTUM_CLAIM")):
        raise ValueError("preflight promoted a downstream claim")
    for dependency in value["dependency_refs"].values():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency hash drifted: {dependency['path']}")
    for path, digest in value["source_manifest"].items():
        if _sha256(ROOT / path) != digest:
            raise ValueError(f"source hash drifted: {path}")


def synthetic_candidate() -> dict:
    interaction = DEPENDENCIES["mixed_ell3_filtered_obstruction"]
    return {
        "schema": "pure-weyl-berger-admissible-same-background-branch-map-v1",
        "result_id": "BERGER_ADMISSIBLE_SAME_BACKGROUND_BRANCH_MAP_V1",
        "claim_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "background_id": "fixed_rational_positive_Berger_clock",
        "source_carrier_id": "synthetic_test_carrier",
        "map_category": "NONCONTRACTIBLE_COFIBER",
        "branch_ids": ["Einstein_like", "extra_Weyl", "Maxwell", "gauge_nondynamical"],
        "mode_scope": {
            "theory": "pure-Weyl gravity with Berger clock and Maxwell apparatus",
            "background": "fixed_rational_positive_Berger_clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": "fixed-coupling retained sector with K_Berger=D-omega R",
            "carrier": "synthetic test carrier only",
            "degree": "all declared BV degrees",
            "parity": "all declared parities",
            "ell": "all declared harmonics",
            "m": "all declared harmonics",
            "k": "NOT_APPLICABLE on compact Berger S3",
            "omega": "all declared K_Berger frequencies",
        },
        "interaction_dependency": {"result_id": "BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1", "path": str(interaction.relative_to(ROOT)), "sha256": _sha256(interaction)},
        "map_artifacts": [
            {"role": role, "path": str(INPUT_SCHEMA.relative_to(ROOT)), "sha256": _sha256(INPUT_SCHEMA)}
            for role in REQUIRED_ARTIFACT_ROLES
        ],
        "acceptance_flags": {flag: True for flag in REQUIRED_FLAGS},
        "claim_boundary": "Synthetic schema and mutation fixture only; never a scientific branch-map verdict.",
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: Mapping[str, object]) -> str:
    return f"""# Berger mixed-ell3 branch-projection importer preflight

Result: `{value['result_state']}`.

The importer is ready, but bridge 2 remains fail-closed until bridge 1 supplies
an admissible branch map on the exact Berger interaction background.  The
candidate must declare the full atlas mode scope and content-addressed evidence
for its carrier crosswalk, chain map, inclusion/projection/cofiber, pairing,
gauge/nondynamical disposition, `K_Berger` equivariance, cohomology map and
independent verifier.  The compact-product source atlas row is not such a map.

No projected operation, cohomology class, cyclic deformation verdict, or
`q4` claim is promoted.
"""


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
        raise ValueError("branch-projection importer outputs drifted")
    if args.guards:
        candidate = synthetic_candidate()
        validate_candidate(candidate, verify_artifacts=False)
        for name, mutate in (
            ("wrong background", lambda item: item.__setitem__("background_id", "compact_product")),
            ("missing pairing", lambda item: item["acceptance_flags"].__setitem__("PAIRING_TRANSPORT_VERIFIED", False)),
            ("missing cohomology artifact", lambda item: item["map_artifacts"].pop(6)),
        ):
            mutant = deepcopy(candidate)
            mutate(mutant)
            try:
                validate_candidate(mutant, verify_artifacts=False)
            except Exception:
                continue
            raise ValueError(f"mutation accepted: {name}")
    print("BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
