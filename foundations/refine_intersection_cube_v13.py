#!/usr/bin/env python3
"""Project the named H2 weak-wave completion into cube v13."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V12 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V12.json"
H2_TEST = FOUNDATIONS / "results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V13.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v13.md"
EVIDENCE_ID = "FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1"

DECISIONS = [
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|KINEMATICS_OBSERVABLES",
        "previous_status": "LOCAL_RESULT", "new_status": "LOCAL_RESULT", "evidence_role": "DIRECT_LOCAL",
        "finding": "The finite localized tests now embed in a countable rational C1 piecewise-polynomial test carrier with an explicit H2 name and exact derivative-square arithmetic.",
        "boundary": "The named fixed-slab H2 carrier is not the unrestricted nonmetrizable LF topology of all compactly supported smooth tests.",
    },
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|STATE_REPRESENTATION",
        "previous_status": "REVIEWED_GAP", "new_status": "LOCAL_RESULT", "evidence_role": "DIRECT_LOCAL",
        "finding": "Every represented coded energy state now defines a continuous spacetime functional on the named H2 test completion, with squared pairing bound 2E times the H2 squared norm.",
        "boundary": "This is a distributional field-state representation, not a probability state, density operator, representation-independent distribution theory, or arbitrary-distribution classification.",
    },
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS",
        "previous_status": "PIECES_ONLY", "new_status": "LOCAL_RESULT", "evidence_role": "DIRECT_LOCAL",
        "finding": "The unique coded energy evolution has a continuous weak representation on every supplied fast H2 test name, with explicit primitive-recursive transport and wave-residual cutoffs.",
        "boundary": "Uniqueness is inside the represented energy-solution image; no uniqueness theorem is claimed among all abstract distributional weak solutions.",
    },
    {
        "coordinate": "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|RECONSTRUCTION_LIMITS",
        "previous_status": "PIECES_ONLY", "new_status": "PIECES_ONLY", "evidence_role": "SUPPORTING",
        "finding": "A named H2 completion closes the finite-to-completed weak-test extension, while the translator from conventional smooth-test names and the global support topology remain explicit reconstruction gates.",
        "boundary": "Density is by declared fast-name representation; no uniform name is extracted from a bare extensional smooth function.",
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
        "cells": [(key(cell), cell["status"], cell["evidence"], cell["evidence_roles"], cell["migration_status"], cell.get("classification_revision"), cell.get("interface_revision"), cell.get("bt_euclidean_revision"), cell.get("observable_reconstruction_revision"), cell.get("local_weak_wave_revision"), cell.get("h2_test_completion_revision")) for cell in cells],
        "interfaces": interfaces, "carrier_interfaces": carrier_interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old, theorem = load(V12), load(H2_TEST)
    flags = theorem.get("claim_flags", {})
    if theorem.get("result_id") != EVIDENCE_ID or theorem.get("lifecycle") != "CERTIFIED":
        raise ValueError("H2 test identity/lifecycle")
    for flag in ("named_h2_test_completion_constructed", "weak_solution_extended_to_every_named_h2_test", "continuous_distributional_state_map_constructed", "energy_image_evolution_wellposed"):
        if flags.get(flag) is not True:
            raise ValueError("missing theorem flag " + flag)
    for flag in ("bare_extensional_smooth_tests_uniformly_named", "full_lf_test_topology_reconstructed", "uniqueness_among_arbitrary_distributions_proved", "strict_causal_support_proved", "new_lorentzian_claim"):
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
            raise ValueError("unexpected v12 status " + coordinate)
        cell["status"] = decision["new_status"]
        cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
        cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: decision["evidence_role"]}
        cell["summary"], cell["boundary"] = decision["finding"], decision["boundary"]
        cell["h2_test_completion_revision"] = {key: decision[key] for key in ("previous_status", "new_status", "evidence_role")}
        cell["h2_test_completion_revision"]["certificate"] = EVIDENCE_ID
    if found != set(decisions):
        raise ValueError("decision coordinate closure")
    counts = Counter(cell["status"] for cell in cells)
    migrations = Counter(cell["migration_status"] for cell in cells)
    roles = Counter(role for cell in cells for role in cell["evidence_roles"].values())
    for status in ("LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"):
        counts.setdefault(status, 0)
    interfaces, carrier_interfaces = old["certified_interfaces"], old["certified_carrier_interfaces"]
    value: dict[str, Any] = {
        "schema_version": "foundational-intersection-cube-v13",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V13",
        "result_kind": "FULL_CARTESIAN_ASSESSMENT_CUBE_WITH_NAMED_H2_TEST_COMPLETION",
        "lifecycle": "EVIDENCE_AUGMENTED_FULL_CARTESIAN_SURFACE",
        "created": "2026-08-14", "repository_base_commit": "e75bac393108c75601a84f9b0931050a8a1f816d",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Preserve cube v12 while importing a representation-aware H2 test completion, continuous distributional state map, and weak-solution modulus without claiming the full LF test topology, arbitrary-distribution uniqueness, or causality.",
        "compatibility": {**old["compatibility"], "v12_full_surface_preserved": True, "v12_cells_preserved_except_four_declared_h2_test_decisions": True, "v12_interfaces_preserved": True, "coded_h2_test_completion": EVIDENCE_ID},
        "axes": old["axes"], "cell_statuses": old["cell_statuses"], "migration_statuses": old["migration_statuses"], "evidence_role_vocabulary": old["evidence_role_vocabulary"], "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {**old["dimensions"], "h2_test_evidence_augmented_cells": 4, "h2_test_status_changes": 2, "h2_test_direct_local_cells": 3, "h2_test_supporting_cells": 1, "status_counts": dict(sorted(counts.items())), "migration_status_counts": dict(sorted(migrations.items())), "evidence_role_counts": dict(sorted(roles.items())), "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells)},
        "certified_interfaces": interfaces, "certified_carrier_interfaces": carrier_interfaces, "cells": cells,
        "provenance": {"inputs": [{"path": str(V12.relative_to(ROOT)), "sha256": sha(V12)}, {"path": str(H2_TEST.relative_to(ROOT)), "sha256": sha(H2_TEST)}]},
        "independent_checker": {"path": "foundations/check_refined_intersection_cube_v13.py", "checks": ["exact 576-cell surface", "572 cube-v12 cells unchanged", "four declared evidence augmentations", "two direct local promotions", "evidence-role closure", "all interfaces preserved", "canonical digest"], "expected_digest": digest(cells, interfaces, carrier_interfaces)},
        "claim_flags": {"v12_surface_preserved": True, "all_576_coordinates_assessed": True, "named_h2_test_completion_imported": True, "distributional_state_map_imported": True, "energy_image_weak_evolution_imported": True, "full_lf_test_topology_established": False, "arbitrary_distributional_uniqueness_established": False, "causal_support_established": False, "green_operator_established": False, "empirical_agreement_assessed": False, "complete_physical_theory_established": False, "new_lorentzian_claim": False},
        "does_not_establish": ["a uniform H2 name constructor for every bare extensional smooth test", "the unrestricted LF topology of compactly supported smooth tests", "uniqueness among arbitrary distributional weak solutions", "strict finite propagation or causal Green support", "an advanced or retarded Green operator", "a Weyl, Bateman-Turok, metric-BV, or interacting equation", "empirical calibration or observational agreement", "that all 576 coordinates are jointly realizable", "a complete physical theory or new LORENTZIAN-CAUSAL result"],
        "human_report": "foundations/reports/refined-intersection-cube-v13.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    return "\n".join([
        "# Foundations cube v13: named H2 weak-test completion", "", f"**Result:** `{value['result_id']}`", "", "## Outcome", "",
        "Cube v13 preserves the full 576-coordinate v12 surface and augments exactly four weak-arithmetic smooth/distributional cells. State representation and evolution/well-posedness become scoped direct local results; kinematics remains a direct local result with the larger named carrier, while reconstruction remains pieces-only.", "",
        "The crucial scope is representation-sensitive: density holds in the declared fixed-slab H2 completion because the fast name is supplied. The result does not reconstruct the unrestricted classical LF test topology or prove uniqueness among arbitrary distributions.", "",
        f"The surface contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.", "",
        "## Reproduction", "", "```text", "python3 foundations/refine_intersection_cube_v13.py --check", "python3 foundations/check_refined_intersection_cube_v13.py", "python3 foundations/verify_refined_intersection_cube_v13.py", "python3 -m unittest foundations.tests.test_refined_intersection_cube_v13", "```", "", "## Boundaries", "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]], "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    result_bytes, report_bytes = generated(); outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_INTERSECTION_CUBE_V13: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))); return bool(stale)
    for path, content in outputs: path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V13: wrote result and report"); return 0


if __name__ == "__main__": raise SystemExit(main())
