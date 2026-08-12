#!/usr/bin/env python3
"""Independent structural audit of the migration-reviewed explorer v2."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "foundations/site"
DATA = SITE / "data.json"
MANIFEST = SITE / "manifest.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
LADDER = ROOT / "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
STATUSES = {"LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "NOT_MAPPED"}
MIGRATIONS = {"EXACT_PARENT_TRANSFER", "CAPABILITY_QUALIFIED", "REVIEWED_OVERLAY", "REVIEWED_NO_TRANSFER", "REVIEWED_CHILD_GAP", "NOT_REVIEWED"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data: dict[str, Any]) -> str:
    projection = {key: data[key] for key in ("axes", "cells", "evidence", "ladder", "graph")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    data = load(DATA) if data is None else data
    cube, ladder, result, manifest = load(CUBE), load(LADDER), load(RESULT), load(MANIFEST)
    errors: list[str] = []
    axes = {x.get("id"): x for x in data.get("axes", [])}
    keys = {axis_id: [x.get("id") for x in axes.get(axis_id, {}).get("keys", [])] for axis_id in ("FOUNDATION", "CARRIER", "REFINED_OBLIGATION")}
    if [len(keys[x]) for x in keys] != [6, 6, 16]:
        errors.append("axis sizes")
    expected = {(f, c, o) for f in keys["FOUNDATION"] for c in keys["CARRIER"] for o in keys["REFINED_OBLIGATION"]}
    cells = data.get("cells", [])
    coordinates = [(x.get("foundation"), x.get("carrier"), x.get("obligation")) for x in cells]
    if len(cells) != 576 or len(set(coordinates)) != 576 or set(coordinates) != expected:
        errors.append("Cartesian closure")
    if any(x.get("status") not in STATUSES for x in cells) or any(x.get("migration_status") not in MIGRATIONS for x in cells):
        errors.append("coverage/migration status closure")

    emitted = [x for x in cells if x.get("emitted")]
    synthetic = [x for x in cells if not x.get("emitted")]
    if len(emitted) != 452 or len(synthetic) != 124:
        errors.append("emitted/complement partition")
    if any(x.get("status") != "NOT_MAPPED" or x.get("migration_status") != "NOT_REVIEWED" for x in synthetic):
        errors.append("synthetic fail-closed states")
    if any("not a literature-absence claim" not in x.get("boundary", "") for x in synthetic):
        errors.append("synthetic NOT_MAPPED boundary")

    original = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cube["cells"]}
    for cell in emitted:
        source = original.get((cell["foundation"], cell["carrier"], cell["obligation"]))
        if source is None or {key: value for key, value in cell.items() if key != "emitted"} != source:
            errors.append("authoritative emitted-cell copy")
            break
    migration_counts = Counter(x.get("migration_status") for x in emitted)
    if migration_counts.get("REVIEWED_NO_TRANSFER") != 88 or migration_counts.get("REVIEWED_CHILD_GAP") != 24 or "NOT_REVIEWED" in migration_counts:
        errors.append("emitted migration review closure")
    no_transfer = [x for x in emitted if x.get("migration_status") == "REVIEWED_NO_TRANSFER"]
    if any(x.get("status") != "NOT_MAPPED" or x.get("evidence") or not x.get("migration_evidence") for x in no_transfer):
        errors.append("reviewed no-transfer separation")

    evidence = data.get("evidence", {})
    used = {item for cell in emitted for field in ("evidence", "migration_evidence") for item in cell.get(field, [])}
    if set(evidence) != used or len(evidence) != 51:
        errors.append("coverage and migration evidence resolution")
    for item in evidence.values():
        for field in ("result_link", "report_link", "ledger_link"):
            link = item.get(field)
            if link and not (SITE / link).is_file():
                errors.append("bundled evidence link " + link)
    for link in data.get("source_links", {}).values():
        if not (SITE / link).is_file():
            errors.append("bundled source link " + str(link))

    graph = data.get("graph", {})
    nodes = {x.get("id") for x in graph.get("nodes", [])}
    vocabulary = set(graph.get("relation_vocabulary", []))
    if len(nodes) != 12 or len(graph.get("edges", [])) != 10 or any(edge.get("from") not in nodes or edge.get("to") not in nodes or edge.get("relation") not in vocabulary for edge in graph.get("edges", [])):
        errors.append("typed implication graph")
    if data.get("ladder") != ladder.get("ladder") or len(data.get("ladder", [])) != 6:
        errors.append("strength ladder projection")

    calculated_digest = digest(data)
    if calculated_digest != data.get("canonical_digest") or calculated_digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical data digest")
    if (SITE / "data.js").read_bytes() != b"window.MATRIX_EXPLORER_DATA = " + DATA.read_bytes().rstrip() + b";\n":
        errors.append("self-contained data assignment")
    for output in manifest.get("outputs", []):
        path = ROOT / output.get("path", "")
        if not path.is_file() or sha(path) != output.get("sha256") or path.stat().st_size != output.get("bytes"):
            errors.append("manifest output " + str(output.get("path")))
    for source in manifest.get("inputs", []):
        path = ROOT / source.get("path", "")
        if not path.is_file() or sha(path) != source.get("sha256"):
            errors.append("manifest input " + str(source.get("path")))

    html = (SITE / "index.html").read_text()
    app = (SITE / "app.js").read_text() + (SITE / "migration-review.js").read_text()
    if "https://" in html or "http://" in html or '<script src="data.js"></script>' not in html or '<script src="migration-review.js"></script>' not in html:
        errors.append("offline/no-remote-code shell")
    for token in ("matrixGroups", "graphView", "ladderView", "evidenceView", "compareDialog", "exportJson", "exportCsv", "downloadBrief", "column-label", "Migration review", "migration_evidence", "112-decision audit JSON"):
        if token not in html + app:
            errors.append("interface token " + token)

    status_counts = Counter(x.get("status") for x in cells)
    all_migrations = Counter(x.get("migration_status") for x in cells)
    counts = data.get("counts", {})
    if counts.get("status_counts") != dict(sorted(status_counts.items())) or counts.get("migration_status_counts") != dict(sorted(all_migrations.items())):
        errors.append("coverage/migration counts")
    if counts.get("coverage_classified") != 364 or counts.get("migration_reviewed") != 452 or counts.get("migration_pending") != 0 or counts.get("not_mapped") != 212:
        errors.append("review count summary")
    summary = {
        "digest": calculated_digest,
        "cells": len(cells),
        "emitted": len(emitted),
        "synthetic_not_mapped": len(synthetic),
        "total_not_mapped": status_counts["NOT_MAPPED"],
        "coverage_classified": counts.get("coverage_classified"),
        "migration_reviewed": counts.get("migration_reviewed"),
        "migration_pending": counts.get("migration_pending"),
        "reviewed_no_transfer": migration_counts["REVIEWED_NO_TRANSFER"],
        "evidence_records": len(evidence),
        "graph_edges": len(graph.get("edges", [])),
        "ladder_levels": len(data.get("ladder", [])),
    }
    return errors, summary


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
