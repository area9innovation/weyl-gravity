#!/usr/bin/env python3
"""Independent structural audit of the generated matrix explorer."""
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
RESULT = ROOT / "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
LADDER = ROOT / "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
STATUSES = {"LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "MIGRATION_UNRESOLVED", "NOT_MAPPED"}


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
    expected_coordinates = {(f, c, o) for f in keys["FOUNDATION"] for c in keys["CARRIER"] for o in keys["REFINED_OBLIGATION"]}
    cells = data.get("cells", [])
    coordinates = [(x.get("foundation"), x.get("carrier"), x.get("obligation")) for x in cells]
    if len(cells) != 576 or len(set(coordinates)) != 576 or set(coordinates) != expected_coordinates:
        errors.append("Cartesian closure")
    if any(x.get("status") not in STATUSES for x in cells):
        errors.append("status closure")
    emitted = [x for x in cells if x.get("emitted")]
    not_mapped = [x for x in cells if not x.get("emitted")]
    if len(emitted) != 452 or len(not_mapped) != 124 or any(x.get("status") != "NOT_MAPPED" for x in not_mapped):
        errors.append("emitted/complement partition")
    if any("not a literature-absence claim" not in x.get("boundary", "") for x in not_mapped):
        errors.append("NOT_MAPPED boundary")
    original = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cube["cells"]}
    for cell in emitted:
        source = original.get((cell["foundation"], cell["carrier"], cell["obligation"]))
        if source is None or {key: value for key, value in cell.items() if key != "emitted"} != source:
            errors.append("authoritative emitted-cell copy")
            break
    evidence = data.get("evidence", {})
    used = {item for cell in emitted for item in cell.get("evidence", [])}
    if set(evidence) != used or len(evidence) != 51:
        errors.append("evidence resolution")
    if any(item.get("kind") not in {"LOCAL_RESULT", "LITERATURE"} for item in evidence.values()):
        errors.append("evidence type closure")
    if any(item.get("kind") == "LITERATURE" and item.get("artifact_status") not in {"CONTENT_PINNED", "METADATA_ONLY"} for item in evidence.values()):
        errors.append("literature artifact status")
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
    if len(nodes) != 12 or len(graph.get("edges", [])) != 10 or any(e.get("from") not in nodes or e.get("to") not in nodes or e.get("relation") not in vocabulary for e in graph.get("edges", [])):
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
    app = (SITE / "app.js").read_text()
    if "https://" in html or "http://" in html or '<script src="data.js"></script>' not in html:
        errors.append("offline/no-remote-code shell")
    for token in ("matrixGroups", "graphView", "ladderView", "evidenceView", "compareDialog", "exportJson", "exportCsv", "downloadBrief", "URLSearchParams", "navigator.clipboard"):
        if token not in html + app:
            errors.append("interface token " + token)
    counts = Counter(x.get("status") for x in cells)
    if data.get("counts", {}).get("status_counts") != dict(sorted(counts.items())):
        errors.append("status counts")
    summary = {
        "digest": calculated_digest,
        "cells": len(cells),
        "emitted": len(emitted),
        "not_mapped": len(not_mapped),
        "evidence_records": len(evidence),
        "graph_nodes": len(nodes),
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
