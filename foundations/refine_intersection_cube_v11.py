#!/usr/bin/env python3
"""Project the coded observable reconstruction theorem into cube v11."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V10 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json"
RECONSTRUCTION = FOUNDATIONS / "results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V11.json"
REPORT = FOUNDATIONS / "reports/refined-intersection-cube-v11.md"
EVIDENCE_ID = "FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1"

DECISIONS = [
    {
        "coordinate": "WEAK_ARITHMETIC|HILBERT_OPERATOR|KINEMATICS_OBSERVABLES",
        "previous_status": "PIECES_ONLY",
        "new_status": "LOCAL_RESULT",
        "finding": "For the declared coded scalar-wave carrier, a rational periodic polygonal detector defines a bounded linear smeared chiral observable, with exact rational samples on every dyadic time grid.",
        "boundary": "This is one scalar-circle detector profile. It is not a separating observable algebra, a probability rule, a gauge-invariant Weyl observable, or an empirically calibrated instrument.",
    },
    {
        "coordinate": "WEAK_ARITHMETIC|HILBERT_OPERATOR|RECONSTRUCTION_LIMITS",
        "previous_status": "LITERATURE_RESULT",
        "new_status": "LOCAL_RESULT",
        "finding": "RCA_0 proves uniform reconstruction of the declared smeared observable from finite rational dyadic interpolants, with the explicit cutoff N(k)=k+ell(K)+1 on every rational bounded time interval.",
        "boundary": "The theorem reconstructs one bounded observable from named rational data. It does not reconstruct the full state, establish representation invariance, causal support, a continuum Weyl limit, or empirical equivalence.",
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
        "cells": [
            (
                key(cell), cell["status"], cell["evidence"], cell["evidence_roles"],
                cell["migration_status"], cell.get("classification_revision"),
                cell.get("interface_revision"), cell.get("bt_euclidean_revision"),
                cell.get("observable_reconstruction_revision"),
            )
            for cell in cells
        ],
        "interfaces": interfaces,
        "carrier_interfaces": carrier_interfaces,
    }
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    old, theorem = load(V10), load(RECONSTRUCTION)
    flags = theorem.get("claim_flags", {})
    if theorem.get("result_id") != EVIDENCE_ID or theorem.get("lifecycle") != "CERTIFIED":
        raise ValueError("reconstruction identity/lifecycle")
    for flag in ("declared_bounded_linear_observable", "finite_rational_approximants_constructed", "uniform_bounded_time_convergence_proved", "explicit_cutoff_function_proved", "rca0_upper_bound_proved"):
        if flags.get(flag) is not True:
            raise ValueError("missing theorem flag " + flag)
    for flag in ("full_state_reconstruction_proved", "causal_support_proved", "new_lorentzian_claim"):
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
            raise ValueError("unexpected v10 status " + coordinate)
        cell["status"] = decision["new_status"]
        cell["evidence"] = list(dict.fromkeys([*cell["evidence"], EVIDENCE_ID]))
        cell["evidence_roles"] = {**cell["evidence_roles"], EVIDENCE_ID: "DIRECT_LOCAL"}
        cell["summary"] = decision["finding"]
        cell["boundary"] = decision["boundary"]
        cell["observable_reconstruction_revision"] = {
            "certificate": EVIDENCE_ID,
            "previous_status": decision["previous_status"],
            "new_status": decision["new_status"],
            "evidence_role": "DIRECT_LOCAL",
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
        "schema_version": "foundational-intersection-cube-v11",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V11",
        "result_kind": "FULL_CARTESIAN_ASSESSMENT_CUBE_WITH_OBSERVABLE_RECONSTRUCTION",
        "lifecycle": "EVIDENCE_AUGMENTED_FULL_CARTESIAN_SURFACE",
        "created": "2026-08-14",
        "repository_base_commit": "af7d497462698fc5c612d8a68bf84f9b72722c02",
        "dependency_tags": old["dependency_tags"],
        "purpose": "Preserve cube v10 while importing the first exact weak-arithmetic finite-approximant theorem for a declared bounded wave observable.",
        "compatibility": {
            **old["compatibility"],
            "v10_full_surface_preserved": True,
            "v10_cells_preserved_except_two_declared_reconstruction_decisions": True,
            "v10_interfaces_preserved": True,
            "coded_observable_reconstruction": EVIDENCE_ID,
        },
        "axes": old["axes"],
        "cell_statuses": old["cell_statuses"],
        "migration_statuses": old["migration_statuses"],
        "evidence_role_vocabulary": old["evidence_role_vocabulary"],
        "evidence_role_rule": old["evidence_role_rule"],
        "dimensions": {
            **old["dimensions"],
            "observable_reconstruction_imported_cells": 2,
            "observable_reconstruction_status_promotions": 2,
            "status_counts": dict(sorted(counts.items())),
            "migration_status_counts": dict(sorted(migrations.items())),
            "evidence_role_counts": dict(sorted(roles.items())),
            "dual_direct_cells": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
        },
        "certified_interfaces": interfaces,
        "certified_carrier_interfaces": carrier_interfaces,
        "cells": cells,
        "provenance": {"inputs": [
            {"path": str(V10.relative_to(ROOT)), "sha256": sha(V10)},
            {"path": str(RECONSTRUCTION.relative_to(ROOT)), "sha256": sha(RECONSTRUCTION)},
        ]},
        "independent_checker": {
            "path": "foundations/check_refined_intersection_cube_v11.py",
            "checks": ["exact 576-cell surface", "574 cube-v10 cells unchanged", "two declared direct-local promotions", "evidence-role closure", "all interfaces preserved", "canonical digest"],
            "expected_digest": digest(cells, interfaces, carrier_interfaces),
        },
        "claim_flags": {
            "v10_surface_preserved": True,
            "all_576_coordinates_assessed": True,
            "declared_wave_observable_imported": True,
            "uniform_observable_reconstruction_imported": True,
            "explicit_cutoff_imported": True,
            "full_state_reconstruction_established": False,
            "representation_invariance_established": False,
            "causal_support_established": False,
            "empirical_agreement_assessed": False,
            "complete_physical_theory_established": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "that RCA_0 is necessary or weakest",
            "a separating observable algebra from one detector profile",
            "full state or field reconstruction from one smeared observable",
            "representation invariance or a general finite-to-continuum theorem",
            "a localized weak spacetime equation or causal Green support",
            "a Weyl, Bateman-Turok, metric-BV, or interacting reconstruction theorem",
            "empirical calibration or observational agreement",
            "that all 576 coordinates are jointly realizable",
            "a complete physical theory or new LORENTZIAN-CAUSAL result",
        ],
        "human_report": "foundations/reports/refined-intersection-cube-v11.md",
    }
    return value


def render(value: dict[str, Any]) -> str:
    counts = value["dimensions"]["status_counts"]
    return "\n".join([
        "# Foundations cube v11: observable reconstruction import", "",
        f"**Result:** `{value['result_id']}`", "", "## Outcome", "",
        "Cube v11 preserves the complete 576-coordinate v10 surface and changes exactly two weak-arithmetic Hilbert/operator coordinates. A declared rational detector is now a direct local kinematics/observable result, and its exact finite dyadic interpolants provide a direct local reconstruction result.", "",
        "The reconstruction theorem is uniform on every rational bounded time interval and supplies the explicit cutoff `N(k)=k+ell(K)+1`. It reconstructs one smeared scalar-wave observable, not the full field, a causal Green operator, or an empirical prediction.", "",
        f"The surface contains **{counts['LOCAL_RESULT']} local results**, **{counts['LITERATURE_RESULT']} literature results**, **{counts['PIECES_ONLY']} pieces-only cells**, **{counts['PRIORITY_GAP']} priority gaps**, **{counts['REVIEWED_GAP']} reviewed gaps**, and **{counts['NOT_MAPPED']} not-mapped cells**.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/refine_intersection_cube_v11.py --check",
        "python3 foundations/check_refined_intersection_cube_v11.py",
        "python3 foundations/verify_refined_intersection_cube_v11.py",
        "python3 -m unittest foundations.tests.test_refined_intersection_cube_v11",
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
        print("FOUNDATIONAL_INTERSECTION_CUBE_V11: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V11: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
