#!/usr/bin/env python3
"""Generate the committed-snapshot residual branch manifest and trace view."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = "physics/symplectic-reconstruction/"
SOURCE_COMMIT = "ba746d608a86ffb8ce7d8d1adf8503e29e8db9b1"
OUTPUT = ROOT / "residual_atlas/residual-branch-manifest-v1.json"
REPORT = ROOT / "reports/residual-branch-manifest-v1.md"
SCHEMA = ROOT / "residual_atlas/schema/residual-branch-manifest-v1.schema.json"
FRAGMENT_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
CELL_AXES = [
    "linear_operator",
    "causal_carrier",
    "lee_wald_pairing",
    "taub_map",
    "second_order",
    "interaction_readiness",
    "observer_coupling",
    "quantum_status",
]
FRAGMENT_PATHS = {
    "einstein": "bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json",
    "classical": "d_quotient_classical/atlas/classical-causal-atlas-fragment.json",
    "nonlinear": "d_quotient_classical/atlas/nonlinear-atlas-fragment.json",
    "observer": "closed_universe_observers/atlas/observer-atlas-fragment.json",
    "quantum": "quantum-weyl/atlas/quantum-atlas-fragment.json",
    "black_hole": "black_hole_programme/atlas/black-hole-atlas-fragment.json",
}


class BranchManifestError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BranchManifestError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_bytes(relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{SOURCE_COMMIT}:{PREFIX}{relative}"],
        cwd=REPO,
    )


def _load_fragments() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    fragment_schema = json.loads(FRAGMENT_SCHEMA.read_text(encoding="utf-8"))
    loaded: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for key, relative in FRAGMENT_PATHS.items():
        raw = _git_bytes(relative)
        payload = json.loads(raw)
        Draft202012Validator(fragment_schema).validate(payload)
        ids = [entry["id"] for entry in payload["entries"]]
        _require(len(ids) == len(set(ids)), f"duplicate entry in {key}")
        loaded[key] = {"payload": payload, "by_id": {entry["id"]: entry for entry in payload["entries"]}}
        id_bytes = ("\n".join(ids) + "\n").encode()
        records.append(
            {
                "key": key,
                "path": relative,
                "team": payload["team"],
                "sha256": _sha256(raw),
                "entry_count": len(ids),
                "entry_ids": ids,
                "entry_ids_sha256": _sha256(id_bytes),
            }
        )
    return loaded, records


def _get(value: Any, path: str) -> Any:
    for part in path.split("."):
        value = value[part]
    return value


def _source_ref(fragments: dict[str, dict[str, Any]], fragment: str, entry_id: str, field_path: str) -> dict[str, str]:
    entry = fragments[fragment]["by_id"][entry_id]
    value = _get(entry, field_path)
    if isinstance(value, dict):
        status = value["status"]
        statement = value["statement"]
    else:
        status = value
        statement = f"source status field {field_path}={value}"
    _require(status in STATUSES, f"bad status at {fragment}:{entry_id}:{field_path}")
    return {
        "fragment": fragment,
        "entry_id": entry_id,
        "field_path": field_path,
        "observed_status": status,
        "observed_statement": statement,
    }


def _cell(
    fragments: dict[str, dict[str, Any]],
    refs: list[tuple[str, str, str]],
    *,
    status: str | None = None,
    statement: str | None = None,
) -> dict[str, Any]:
    sources = [_source_ref(fragments, *ref) for ref in refs]
    statuses = {source["observed_status"] for source in sources}
    selected = status or (next(iter(statuses)) if len(statuses) == 1 else "OPEN")
    _require(selected in STATUSES, "invalid selected cell status")
    text = statement or " | ".join(source["observed_statement"] for source in sources)
    return {"status": selected, "statement": text, "sources": sources}


def _scope(entry: dict[str, Any], **updates: Any) -> dict[str, Any]:
    scope = deepcopy(entry["scope"])
    scope.update(updates)
    return scope


def _source_rows(*rows: tuple[str, str, str]) -> list[dict[str, str]]:
    return [{"fragment": fragment, "entry_id": entry_id, "map_role": role} for fragment, entry_id, role in rows]


def _direct_branch(
    fragments: dict[str, dict[str, Any]],
    *,
    branch_id: str,
    kind: str,
    fragment: str,
    entry_id: str,
    source_rows: list[dict[str, str]] | None = None,
    scope: dict[str, Any] | None = None,
    overrides: dict[str, dict[str, Any]] | None = None,
    boundary: str | None = None,
) -> dict[str, Any]:
    entry = fragments[fragment]["by_id"][entry_id]
    refs = {
        "linear_operator": [(fragment, entry_id, "mode_data.dispersion")],
        "causal_carrier": [(fragment, entry_id, "descriptions.causal")],
        "lee_wald_pairing": [(fragment, entry_id, "mode_data.lee_wald")],
        "taub_map": [(fragment, entry_id, "mode_data.taub_maps")],
        "second_order": [(fragment, entry_id, "mode_data.second_order.bounded_or_finite_quasiperiodic")],
        "interaction_readiness": [(fragment, entry_id, "mode_data.resonance")],
        "observer_coupling": [(fragment, entry_id, "descriptions.observational")],
        "quantum_status": [(fragment, entry_id, "descriptions.quantum")],
    }
    cells = {axis: _cell(fragments, axis_refs) for axis, axis_refs in refs.items()}
    for axis, replacement in (overrides or {}).items():
        cells[axis] = _cell(
            fragments,
            replacement["refs"],
            status=replacement.get("status"),
            statement=replacement.get("statement"),
        )
    return {
        "id": branch_id,
        "kind": kind,
        "scope": scope or deepcopy(entry["scope"]),
        "source_rows": source_rows or _source_rows((fragment, entry_id, "IDENTICAL_CARRIER")),
        "cells": cells,
        "claim_boundary": boundary or entry["claim_boundary"],
    }


def _branches(fragments: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    E = fragments["einstein"]["by_id"]
    branches: list[dict[str, Any]] = []
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.em.q.generic", kind="EINSTEIN_IMAGE",
        fragment="einstein", entry_id="einstein.ph.em_wm.standard.generic_radiative",
        boundary="Same-background compact q-primary Einstein image only; no cylinder, black-hole, observer or quantum identification."
    ))
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.wm.p.generic", kind="ADDITIONAL_WEYL",
        fragment="einstein", entry_id="einstein.ph.wm.extra.generic_p_primary",
        boundary="Compact additional-Weyl p-primary cofiber before final residual quotient; the current sign is not a quantum norm."
    ))
    sign_id = "einstein.ph.wm.taub.harmonic_sign_stratification"
    dictionary_id = "einstein.ph.bridge.relative_branch_dictionary_v1"
    ell1_scope = _scope(
        E[dictionary_id],
        carrier="physical exceptional ell=1 Einstein-image standard shell",
        degree=1, ell=1, m="-1,0,1", k="every allowed compact momentum",
        omega="omega^2=k^2+4", parity="axial and polar",
    )
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.em.ell1.standard", kind="EINSTEIN_IMAGE",
        fragment="einstein", entry_id=dictionary_id, scope=ell1_scope,
        source_rows=_source_rows(
            ("einstein", dictionary_id, "DECLARED_SUBBRANCH"),
            ("einstein", sign_id, "DECLARED_SUBBRANCH"),
        ),
        overrides={
            "lee_wald_pairing": {"refs": [("einstein", sign_id, "mode_data.lee_wald")]},
            "taub_map": {"refs": [("einstein", sign_id, "mode_data.taub_maps")]},
            "second_order": {"refs": [("einstein", sign_id, "mode_data.second_order.bounded_or_finite_quasiperiodic")]},
        },
        boundary="The stable identifier records the declared ell=1 Einstein-image subbranch; no separate causal, observer or quantum carrier is inferred."
    ))
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.wm.ell1.extra.k0", kind="ADDITIONAL_WEYL",
        fragment="einstein", entry_id="einstein.ph.wm.extra.exceptional_ell1_k0",
    ))
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.wm.ell1.extra.knonzero", kind="ADDITIONAL_WEYL",
        fragment="einstein", entry_id="einstein.ph.wm.extra.exceptional_ell1_nonzero_k",
        overrides={
            "taub_map": {"refs": [("einstein", sign_id, "mode_data.taub_maps")], "status": "CERTIFIED",
                         "statement": "The harmonic sign theorem certifies the exceptional extra cofiber sign for every allowed nonzero compact momentum."},
            "second_order": {"refs": [("einstein", sign_id, "mode_data.second_order.bounded_or_finite_quasiperiodic")],
                             "status": "OBSTRUCTED",
                             "statement": "The fixed-bundle Hamiltonian Taub pairing obstructs every nonzero pure-extra tangent, including nonzero-k exceptional modes."},
        },
    ))
    global_id = "einstein.ph.wm.standard.global_bounded_cone"
    global_entry = E[global_id]
    common_global_rows = _source_rows(
        ("einstein", global_id, "DECLARED_SUBBRANCH"),
        ("einstein", sign_id, "DECLARED_SUBBRANCH"),
    )
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.global.homogeneous", kind="GLOBAL_GENERALIZED_ZERO",
        fragment="einstein", entry_id=global_id,
        scope=_scope(global_entry, carrier="homogeneous generalized-zero coordinates (a,b,c,d,Q_e,W_x)",
                     ell=0, m=0, k=0, omega="generalized zero", parity="homogeneous scalar/global"),
        source_rows=common_global_rows,
        boundary="Homogeneous Einstein-image block with zero solution cofiber; no extra-Weyl or particle identification."
    ))
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.global.twist", kind="GLOBAL_GENERALIZED_ZERO",
        fragment="einstein", entry_id=global_id,
        scope=_scope(global_entry, carrier="axial twist position/velocity vectors (A,B)",
                     ell=1, m="three real SO3 components", k=0, omega="generalized zero A+B*t", parity="axial"),
        source_rows=common_global_rows,
        boundary="Twist Einstein-image block with zero solution cofiber; finite holonomy and final residual quotients remain separate."
    ))
    electric_id = "einstein.ph.wm.interaction.electric_wilson_complete_oscillator_transport"
    branches.append(_direct_branch(
        fragments, branch_id="branch.ph.maxwell.electric_wilson", kind="MAXWELL_GLOBAL",
        fragment="einstein", entry_id=global_id,
        scope=_scope(global_entry, carrier="homogeneous electric charge Q_e and flat Wilson line W_x",
                     ell=0, m=0, k=0, omega="generalized zero Q_e*t+W_x", parity="Maxwell global"),
        source_rows=_source_rows(
            ("einstein", global_id, "DECLARED_SUBBRANCH"),
            ("einstein", electric_id, "INTERACTION_INPUT"),
        ),
        overrides={
            "interaction_readiness": {"refs": [("einstein", electric_id, "mode_data.resonance")]},
            "second_order": {"refs": [("einstein", electric_id, "mode_data.second_order.bounded_or_finite_quasiperiodic")]},
        },
        boundary="Fixed magnetic bundle with electric and Wilson-line tangents retained; uniform magnetic-flux variation is not identified with this branch."
    ))

    for short, label in (("e", "E"), ("a", "A"), ("l", "L")):
        classical_id = f"classical.vacuum_cylinder.one_particle.{short}"
        qplus = f"quantum.cylinder.mode_family.{short}.chirality_plus"
        qminus = f"quantum.cylinder.mode_family.{short}.chirality_minus"
        branches.append(_direct_branch(
            fragments, branch_id=f"branch.cylinder.{short}", kind="ONE_PARTICLE_FAMILY",
            fragment="classical", entry_id=classical_id,
            source_rows=_source_rows(
                ("classical", classical_id, "IDENTICAL_CARRIER"),
                ("quantum", qplus, "CHIRAL_SPLIT"),
                ("quantum", qminus, "CHIRAL_SPLIT"),
            ),
            overrides={
                "quantum_status": {"refs": [
                    ("quantum", qplus, "quantum_data.lifecycle_state"),
                    ("quantum", qminus, "quantum_data.lifecycle_state"),
                ], "status": "CERTIFIED", "statement": f"Both chiral {label} quantum carrier rows are certified on the reduced vacuum-cylinder complex."},
                "interaction_readiness": {"refs": [
                    ("quantum", qplus, "mode_data.resonance"),
                    ("quantum", qminus, "mode_data.resonance"),
                ], "status": "OPEN", "statement": "The free spectral carriers are certified; nonlinear interaction readiness remains open."},
            },
            boundary="Vacuum-cylinder E/A/L family only. No compact-product or black-hole mode identification is made."
        ))
    for chirality, short in (("plus", "plus"), ("minus", "minus")):
        classical_id = f"classical.vacuum_cylinder.deformation.w_{short}_squared"
        quantum_id = f"quantum.cylinder.residual_deformation.w_{short}_2"
        branches.append(_direct_branch(
            fragments, branch_id=f"branch.cylinder.w_{short}_squared", kind="NONPARTICLE_RESIDUAL_CLASS",
            fragment="classical", entry_id=classical_id,
            source_rows=_source_rows(
                ("classical", classical_id, "IDENTICAL_CARRIER"),
                ("quantum", quantum_id, "QUANTUM_CROSSWALK"),
            ),
            overrides={
                "quantum_status": {"refs": [("quantum", quantum_id, "quantum_data.lifecycle_state")]},
            },
            boundary=f"Centered W_{chirality}^2 deformation class, not a one-particle graviton state."
        ))

    berger_id = "classical.berger.retained_gravity_clock_maxwell"
    nonlinear_berger = "nonlinear.berger.retained_mixed_ell3.filtered_cyclic_obstruction"
    observer_berger = "observer.crosswalk.berger_physical_branch_to_detector"
    branches.append(_direct_branch(
        fragments, branch_id="branch.berger.retained.unsplit", kind="UNSPLIT_MIXED",
        fragment="classical", entry_id=berger_id,
        source_rows=_source_rows(
            ("classical", berger_id, "IDENTICAL_CARRIER"),
            ("nonlinear", nonlinear_berger, "INTERACTION_INPUT"),
            ("observer", observer_berger, "OBSERVER_CROSSWALK"),
        ),
        overrides={
            "interaction_readiness": {"refs": [("nonlinear", nonlinear_berger, "mode_data.resonance")]},
            "observer_coupling": {"refs": [("observer", observer_berger, "mode_data.dispersion")]},
        },
        boundary="Unsplit Berger retained carrier. The obstructed branch projector forbids identifying its rows as Einstein, extra-Weyl or Maxwell branches."
    ))

    for branch_id, entry_id in (
        ("branch.black_hole.axial.einstein", "bh.mode.axial.einstein-branch"),
        ("branch.black_hole.axial.extra", "bh.mode.axial.extra-fourth-order-branch"),
        ("branch.black_hole.polar.einstein", "bh.mode.polar"),
        ("branch.black_hole.polar.extra", "bh.mode.polar.extra-fourth-order-branch"),
    ):
        branches.append(_direct_branch(
            fragments, branch_id=branch_id, kind="BLACK_HOLE_BRANCH",
            fragment="black_hole", entry_id=entry_id,
            boundary="Native black-hole exterior branch only; compact-product and cylinder branch names do not define a cross-background map."
        ))
    return branches


def _crosswalk(
    fragments: dict[str, dict[str, Any]],
    *,
    crosswalk_id: str,
    from_branches: list[str],
    to_branches: list[str],
    fragment: str,
    entry_id: str,
    field_path: str,
) -> dict[str, Any]:
    source = _source_ref(fragments, fragment, entry_id, field_path)
    return {
        "id": crosswalk_id,
        "from_branches": from_branches,
        "to_branches": to_branches,
        "status": source["observed_status"],
        "statement": source["observed_statement"],
        "source": source,
    }


def build_manifest() -> dict[str, Any]:
    fragments, fragment_records = _load_fragments()
    branches = _branches(fragments)
    branch_ids = {branch["id"] for branch in branches}
    _require(len(branch_ids) == len(branches), "duplicate stable branch id")
    ph = sorted(branch for branch in branch_ids if branch.startswith("branch.ph."))
    cylinder = sorted(branch for branch in branch_ids if branch.startswith("branch.cylinder."))
    black_hole = sorted(branch for branch in branch_ids if branch.startswith("branch.black_hole."))
    crosswalks = [
        _crosswalk(
            fragments,
            crosswalk_id="crosswalk.ph_to_vacuum_cylinder",
            from_branches=ph,
            to_branches=cylinder,
            fragment="einstein",
            entry_id="einstein.crosswalk.compact_product_to_asymptotic_or_vacuum_cylinder",
            field_path="mode_data.dispersion",
        ),
        _crosswalk(
            fragments,
            crosswalk_id="crosswalk.ph_to_black_hole",
            from_branches=ph,
            to_branches=black_hole,
            fragment="black_hole",
            entry_id="bh.bridge.compact-branch-comparison",
            field_path="mode_data.dispersion",
        ),
        _crosswalk(
            fragments,
            crosswalk_id="crosswalk.berger_unsplit_to_ph_branches",
            from_branches=["branch.berger.retained.unsplit"],
            to_branches=ph,
            fragment="classical",
            entry_id="classical.berger.crosswalk.retained36_to_einstein_extra",
            field_path="mode_data.resonance",
        ),
        _crosswalk(
            fragments,
            crosswalk_id="crosswalk.ph_exceptional_to_berger_observer",
            from_branches=["branch.ph.wm.ell1.extra.k0"],
            to_branches=["branch.berger.retained.unsplit"],
            fragment="observer",
            entry_id="observer.crosswalk.compact_product_exceptional_resonance_to_berger",
            field_path="mode_data.dispersion",
        ),
        _crosswalk(
            fragments,
            crosswalk_id="crosswalk.berger_branch_to_detector",
            from_branches=["branch.berger.retained.unsplit"],
            to_branches=["branch.berger.retained.unsplit"],
            fragment="observer",
            entry_id="observer.crosswalk.berger_physical_branch_to_detector",
            field_path="mode_data.dispersion",
        ),
    ]
    all_ids = [f"{record['key']}:{entry_id}" for record in fragment_records for entry_id in record["entry_ids"]]
    inventory_hash = _sha256(("\n".join(all_ids) + "\n").encode())
    return {
        "schema": "pure-weyl-residual-branch-manifest-v1",
        "schema_version": "1.0.0",
        "source_snapshot_commit": SOURCE_COMMIT,
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__).read_bytes()),
        "status_vocabulary": STATUSES,
        "cell_axes": CELL_AXES,
        "fragments": fragment_records,
        "branches": branches,
        "crosswalks": crosswalks,
        "coverage": {
            "fragment_count": len(fragment_records),
            "total_source_rows": len(all_ids),
            "stable_branch_count": len(branches),
            "crosswalk_count": len(crosswalks),
            "row_inventory_sha256": inventory_hash,
        },
        "claim_boundary": "This generated ledger traces only explicit committed same-carrier rows and explicit crosswalk/no-crosswalk witnesses. It does not identify similarly named modes across backgrounds, infer empty cells as zero, turn reduced current signs into quantum norms, or promote absent causal, observer, interaction or quantum maps.",
        "verification_commands": [
            "python3 residual_atlas/generate_branch_manifest.py --check",
            "python3 residual_atlas/verify_branch_manifest.py",
            "python3 -m unittest residual_atlas.tests.test_branch_manifest",
        ],
    }


def render_report(manifest: dict[str, Any]) -> str:
    lines = [
        "# Residual branch manifest v1",
        "",
        f"Pinned source snapshot: `{manifest['source_snapshot_commit']}`.",
        "",
        "| Stable branch | Kind | Linear | Causal | Lee–Wald | Taub | Second order | Interaction | Observer | Quantum |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for branch in manifest["branches"]:
        cells = branch["cells"]
        lines.append(
            "| " + " | ".join([
                f"`{branch['id']}`",
                branch["kind"],
                cells["linear_operator"]["status"],
                cells["causal_carrier"]["status"],
                cells["lee_wald_pairing"]["status"],
                cells["taub_map"]["status"],
                cells["second_order"]["status"],
                cells["interaction_readiness"]["status"],
                cells["observer_coupling"]["status"],
                cells["quantum_status"]["status"],
            ]) + " |"
        )
    lines.extend(["", "## Explicit crosswalk boundary", ""])
    for crosswalk in manifest["crosswalks"]:
        lines.append(f"- `{crosswalk['id']}` — **{crosswalk['status']}**: {crosswalk['statement']}")
    lines.extend([
        "",
        "The JSON manifest retains the full scope tuple, exact source rows and field paths, observed source statuses and statements, committed fragment hashes, and complete source-row inventory digest.",
        "",
        manifest["claim_boundary"],
        "",
        "CLOSE-OUT: DONE — the complete stop condition is met",
        "EVIDENCE: residual_atlas/residual-branch-manifest-v1.json",
        "",
    ])
    return "\n".join(lines)


def _validate(manifest: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    _validate(manifest)
    report = render_report(manifest)
    if args.write:
        OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT.write_text(report, encoding="utf-8")
    else:
        _require(json.loads(OUTPUT.read_text(encoding="utf-8")) == manifest, "branch manifest is stale")
        _require(REPORT.read_text(encoding="utf-8") == report, "branch report is stale")
    print("RESIDUAL_BRANCH_MANIFEST_V1: PASS")


if __name__ == "__main__":
    main()
