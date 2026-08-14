#!/usr/bin/env python3
"""Project the localized coefficient-weak wave result into cube v12."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V11 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V11.json"
WEAK_WAVE = FOUNDATIONS / "results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V12.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v12.md"
EVIDENCE_ID = "FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1"

DECISIONS = [
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|KINEMATICS_OBSERVABLES",
        "previous_status": "REVIEWED_GAP",
        "new_status": "LOCAL_RESULT",
        "evidence_role": "DIRECT_LOCAL",
        "finding": "A ten-element characteristic-localized rational polynomial test family separates the declared labelled finite chiral carrier, and all pairings are exact rational data.",
        "boundary": "Separation retains the right/left labels and fixed rational resolution. It is not separation of arbitrary scalar distributions, gauge classes, or a continuum observable algebra.",
    },
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS",
        "previous_status": "PIECES_ONLY",
        "new_status": "PIECES_ONLY",
        "evidence_role": "SUPPORTING",
        "finding": "The existing RCA_0 coded energy evolution now has a finite localized weak-equation compatibility certificate, but no independent distributional existence/uniqueness theorem is added.",
        "boundary": "Coefficient-wise compatibility with ten tests does not prove well-posedness in a distribution topology or against every smooth test.",
    },
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|RECONSTRUCTION_LIMITS",
        "previous_status": "REVIEWED_GAP",
        "new_status": "PIECES_ONLY",
        "evidence_role": "SUPPORTING",
        "finding": "The localized measurements exactly reconstruct the ten labelled coefficients at the declared finite resolution, exposing the next density/modulus gate toward a distributional reconstruction theorem.",
        "boundary": "This finite labelled separation is not full-state reconstruction, representation invariance, or separation after forgetting chirality labels.",
    },
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(cell: dict[str, Any]) -> str:
    return "|".join(cell[name] for name in ("foundation", "carrier", "obligation"))


def digest(cells: list[dict[str, Any]], interfaces: list[dict[str, Any]], carrier_interfaces: list[dict[str, Any]]) -> str:
    projection = {
        "cells": [(key(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision"), cell.get("bt_euclidean_revision"), cell.get("observable_reconstruction_revision"), cell.get("local_weak_wave_revision")) for cell in cells],
        "interfaces": interfaces,
        "carrier_interfaces": carrier_interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old, theorem = load(V11), load(WEAK_WAVE)
    flags = theorem.get("claim_flags", {})
    if theorem.get("result_id") != EVIDENCE_ID or theorem.get("lifecycle") != "CERTIFIED":
        raise ValueError("weak-wave identity/lifecycle")
    for flag in ("finite_localized_test_class_constructed", "labelled_finite_carrier_separated", "coefficient_scalar_weak_wave_identity_proved", "rca0_completion_transfer"):
        if flags.get(flag) is not True:
            raise ValueError("missing theorem flag " + flag)
    for flag in ("all_smooth_tests_covered", "full_state_reconstruction_proved", "strict_causal_support_proved", "new_lorentzian_claim"):
        if flags.get(flag) is not False:
            raise ValueError("boundary theorem flag " + flag)
    decisions = {item["coordinate"]: item for item in DECISIONS}
    cells = json.loads(json.dumps(old["cells"]))
    found: set[str] = set()
    for cell in cells:
        coordinate = key(cell)
        decision = decisions.get(coordinate)
        if decision is None:
            continue
        found.add(coordinate)
        if cell["status"] != decision["previous_status"]:
            raise ValueError("unexpected v11 status " + coordinate)
        cell["status"] = decision["new_status"]
        cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
        cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: decision["evidence_role"]}
        cell["summary"] = decision["finding"]
        cell["boundary"] = decision["boundary"]
        cell["local_weak_wave_revision"] = {
            "certificate": EVIDENCE_ID,
            "previous_status": decision["previous_status"],
            "new_status": decision["new_status"],
            "evidence_role": decision["evidence_role"],
        }
    if found != set(decisions):
        raise ValueError("decision coordinate closure")
    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    for status in ("LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"):
        counts.setdefault(status, 0)
    interfaces = old["certified_interfaces"]
    carrier_interfaces = old["certified_carrier_interfaces"]
    value: dict[str, Any] = {
        "schema_version": "foundational-intersection-cube-v12",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V12",
        "result_kind": "FULL_CARTESIAN_ASSESSMENT_CUBE_WITH_LOCAL_WEAK_WAVE_TEST_CLASS",
        "lifecycle": "EVIDENCE_AUGMENTED_FULL_CARTESIAN_SURFACE",
        "created": "2026-08-14",
        "repository_base_commit": "3c295ffacc222271143df0018bdae167eae87a81",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Preserve cube v11 while importing a finite localized separating chiral test class and coefficient-wise weak spacetime wave identity without promoting a full distributional or causal theorem.",
        "compatibility": {**old["compatibility"], "v11_full_surface_preserved": True, "v11_cells_preserved_except_three_declared_weak_wave_decisions": True, "v11_interfaces_preserved": True, "coded_local_weak_wave_test_class": EVIDENCE_ID},
        "axes": old["axes"],
        "cell_statuses": old["cell_statuses"],
        "migration_statuses": old["migration_statuses"],
        "evidence_role_vocabulary": old["evidence_role_vocabulary"],
        "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {
            **old["dimensions"],
            "local_weak_wave_evidence_augmented_cells": 3,
            "local_weak_wave_status_changes": 2,
            "local_weak_wave_direct_local_promotions": 1,
            "local_weak_wave_pieces_only_promotions": 1,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": interfaces,
        "certified_carrier_interfaces": carrier_interfaces,
        "cells": cells,
        "provenance": {"inputs": [
            {"path": str(V11.relative_to(ROOT)), "sha256": sha(V11)},
            {"path": str(WEAK_WAVE.relative_to(ROOT)), "sha256": sha(WEAK_WAVE)},
        ]},
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v12.py",
            "checks": ["exact 576-cell surface", "573 cube-v11 cells unchanged", "three declared evidence augmentations", "one direct-local and one pieces-only promotion", "evidence-role closure", "all interfaces preserved", "canonical digest"],
            "expected_digest": digest(cells, interfaces, carrier_interfaces),
        },
        "claim_flags": {
            "v11_surface_preserved": True,
            "all_576_coordinates_assessed": True,
            "localized_test_class_imported": True,
            "finite_labelled_separation_imported": True,
            "coefficient_weak_wave_identity_imported": True,
            "full_distributional_test_space_established": False,
            "full_state_reconstruction_established": False,
            "causal_support_established": False,
            "green_operator_established": False,
            "empirical_agreement_assessed": False,
            "complete_physical_theory_established": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "a weak equation against every smooth compactly supported test",
            "separation of arbitrary scalar distributions or gauge classes",
            "full state or representation-independent field reconstruction",
            "well-posedness in a distribution topology from coefficient compatibility alone",
            "strict finite propagation or causal Green support",
            "an advanced or retarded Green operator",
            "a Weyl, Bateman-Turok, metric-BV, or interacting equation",
            "empirical calibration or observational agreement",
            "that all 576 coordinates are jointly realizable",
            "a complete physical theory or new LORENTZIAN-CAUSAL result",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v12.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    return "\n".join([
        "# Foundations cube v12: localized coefficient-weak wave import", "",
        f"**Result:** `{value['result_id']}`", "", "## Outcome", "",
        "Cube v12 preserves the full 576-coordinate v11 surface and augments exactly three weak-arithmetic smooth/distributional cells. The localized-test kinematics cell becomes a direct local result. Reconstruction moves from a reviewed gap to pieces-only, while distributional well-posedness remains pieces-only.", "",
        "The imported theorem has an exact rank-10 localized measurement matrix for ten labelled finite chiral coefficients and proves the weak transport and scalar wave identities coefficient by coefficient against ten rational localized tests. It does not cover every smooth test, forget the chiral labels, prove causal support, or construct a Green operator.", "",
        f"The surface contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/refine_intersection_cube_v12.py --check",
        "python3 foundations/check_refined_intersection_cube_v12.py",
        "python3 foundations/verify_refined_intersection_cube_v12.py",
        "python3 -m unittest foundations.tests.test_refined_intersection_cube_v12",
        "```", "", "## Boundaries", "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]], "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_INTERSECTION_CUBE_V12: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V12: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
