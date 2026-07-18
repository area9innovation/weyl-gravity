#!/usr/bin/env python3
"""Build public and technical views of the machine-readable residual atlas.

The scientific inputs are the team-owned ``*-atlas-fragment.json`` files.
This module changes no status and performs no inference across backgrounds.
It supplies presentation labels, a landscape Graphviz census, a searchable
HTML passport view, and a content-addressed build receipt.

By default only Git-tracked fragments are publishable inputs.  The optional
``--include-working-tree`` flag is for local previews and marks the receipt as
non-publishable when an untracked fragment is consumed.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LABELS_PATH = HERE / "residual_atlas_labels.json"

OUTPUTS = {
    "json": HERE / "residual-atlas-overview.json",
    "dot": HERE / "residual-atlas-overview.dot",
    "html": HERE / "residual-atlas-passports.html",
    "svg": HERE / "residual-atlas-overview.svg",
    "png": HERE / "residual-atlas-overview.png",
    "pdf": HERE / "residual-atlas-overview.pdf",
    "receipt": HERE / "residual-atlas-visualization-receipt.json",
}

AXES = ("causal", "symplectic", "nonlinear", "observational", "quantum")
STATUSES = (
    "CERTIFIED",
    "OBSTRUCTED",
    "OPEN",
    "NOT_APPLICABLE",
    "NO_CERTIFIED_MAP",
)
STATUS_DISPLAY = {
    "CERTIFIED": ("Demonstrated", "#DDF3E4", "#14532D"),
    "OBSTRUCTED": ("Limit found", "#FBE1E3", "#8B1E2D"),
    "OPEN": ("Next frontier", "#FFF1C7", "#7A4B00"),
    "NOT_APPLICABLE": ("Not part of this test", "#ECEFF3", "#475467"),
    "NO_CERTIFIED_MAP": ("Bridge not built", "#DDEAF7", "#184E77"),
}
AXIS_DISPLAY = {
    "causal": "Causal travel",
    "symplectic": "Classical pairing",
    "nonlinear": "Nonlinear survival",
    "observational": "Observer response",
    "quantum": "Quantum status",
}


@dataclass(frozen=True)
class AtlasEntry:
    id: str
    label: str
    group: str
    source: str
    team: str
    descriptions: dict[str, str]
    scope: dict[str, Any]
    details: dict[str, Any]
    evidence: list[dict[str, Any]]
    boundary: str


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _tracked_fragment_paths() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return sorted(
        ROOT / line
        for line in proc.stdout.splitlines()
        if line.endswith("atlas-fragment.json")
    )


def discover_fragments(include_working_tree: bool = False) -> tuple[list[Path], set[Path]]:
    tracked = set(_tracked_fragment_paths())
    paths = set(tracked)
    if include_working_tree:
        paths.update(ROOT.rglob("*atlas-fragment.json"))
    paths = {
        path
        for path in paths
        if "schema" not in path.parts and path.is_file()
    }
    return sorted(paths), tracked


def _fallback_label(identifier: str) -> str:
    words = identifier.replace("_", " ").replace(".", " / ").split()
    return " ".join(words).strip().capitalize()


def _group_for(identifier: str) -> str:
    if ".crosswalk." in identifier or identifier.startswith(("observer.crosswalk", "bh.crosswalk")):
        return "bridges"
    if identifier.startswith("einstein.ph."):
        return "compact_product"
    if identifier.startswith("observer.berger.") or identifier.startswith("quantum.berger."):
        return "berger_clock"
    if identifier.startswith("quantum.cylinder."):
        return "vacuum_cylinder"
    if identifier.startswith("bh."):
        return "black_hole"
    return "other"


def _validate_descriptions(identifier: str, descriptions: Any) -> dict[str, str]:
    if not isinstance(descriptions, dict):
        raise ValueError(f"{identifier}: descriptions must be an object")
    missing = [axis for axis in AXES if axis not in descriptions]
    if missing:
        raise ValueError(f"{identifier}: missing description axes {missing}")
    result = {}
    for axis in AXES:
        status = descriptions[axis]
        if status not in STATUSES:
            raise ValueError(f"{identifier}: invalid {axis} status {status!r}")
        result[axis] = status
    return result


def _normalise_evidence(evidence: Any) -> list[dict[str, Any]]:
    if not isinstance(evidence, list):
        return []
    normalised = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        path = item.get("path") or item.get("certificate") or item.get("source")
        normalised.append(
            {
                "path": str(path) if path else "",
                "result_id": str(item.get("result_id", "")),
                "sha256": str(item.get("sha256", "")),
            }
        )
    return normalised


def load_entries(paths: Iterable[Path], labels: dict[str, Any]) -> list[AtlasEntry]:
    entries: list[AtlasEntry] = []
    seen: dict[str, str] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "pure-weyl-residual-atlas-fragment-v1":
            raise ValueError(f"{path}: unsupported atlas schema {payload.get('schema')!r}")
        team = str(payload.get("team", "unknown"))
        raw_entries = payload.get("entries")
        if not isinstance(raw_entries, list):
            raise ValueError(f"{path}: entries must be an array")
        source = _repo_path(path)
        for raw in raw_entries:
            if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
                raise ValueError(f"{path}: every atlas entry requires a string id")
            identifier = raw["id"]
            if identifier in seen:
                raise ValueError(
                    f"duplicate atlas id {identifier!r} in {source} and {seen[identifier]}"
                )
            seen[identifier] = source
            descriptions = _validate_descriptions(identifier, raw.get("descriptions"))
            scope = raw.get("scope") if isinstance(raw.get("scope"), dict) else {}
            boundary = str(raw.get("claim_boundary") or raw.get("caveats") or "Scope boundary not supplied.")
            detail_keys = (
                "mode_data", "quantum_data", "quantum_status", "claim", "carrier_crosswalk"
            )
            details = {key: raw[key] for key in detail_keys if key in raw}
            entries.append(
                AtlasEntry(
                    id=identifier,
                    label=labels.get("labels", {}).get(identifier, _fallback_label(identifier)),
                    group=_group_for(identifier),
                    source=source,
                    team=team,
                    descriptions=descriptions,
                    scope=scope,
                    details=details,
                    evidence=_normalise_evidence(raw.get("evidence")),
                    boundary=boundary,
                )
            )
    order = {name: index for index, name in enumerate(labels.get("group_order", []))}
    return sorted(entries, key=lambda entry: (order.get(entry.group, 999), entry.label, entry.id))


def public_payload(entries: list[AtlasEntry], inputs: list[Path], publishable: bool) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-overview-v1",
        "publishable_inputs_only": publishable,
        "status_vocabulary": list(STATUSES),
        "axes": list(AXES),
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": _sha256_path(path)}
            for path in inputs
        ],
        "entries": [
            {
                "id": entry.id,
                "label": entry.label,
                "group": entry.group,
                "source": entry.source,
                "team": entry.team,
                "descriptions": entry.descriptions,
                "scope": entry.scope,
                "details": entry.details,
                "evidence": entry.evidence,
                "claim_boundary": entry.boundary,
            }
            for entry in entries
        ],
        "claim_boundary": (
            "This is a generated index of scoped atlas claims. Demonstrated means demonstrated "
            "only in the entry's declared theory, background, carrier, charge sector and lifecycle. "
            "The visualization creates no cross-background identification and no particle claim."
        ),
    }


def _dot_text(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _dot_cell(status: str) -> str:
    label, fill, foreground = STATUS_DISPLAY[status]
    return (
        f'<TD BGCOLOR="{fill}" COLOR="#FFFFFF" CELLPADDING="7">'
        f'<FONT COLOR="{foreground}" POINT-SIZE="10"><B>{_dot_text(label)}</B></FONT></TD>'
    )


def build_dot(entries: list[AtlasEntry], labels: dict[str, Any], publishable: bool) -> str:
    by_group: dict[str, list[AtlasEntry]] = {}
    for entry in entries:
        by_group.setdefault(entry.group, []).append(entry)
    order = labels.get("group_order", [])
    panel_nodes = []
    panel_ids = []
    for group in order + sorted(set(by_group) - set(order)):
        group_entries = by_group.get(group, [])
        if not group_entries:
            continue
        meta = labels.get("groups", {}).get(group, {"label": group, "description": ""})
        rows = [
            '<TR><TD COLSPAN="6" ALIGN="LEFT" BGCOLOR="#172B4D" CELLPADDING="9">'
            f'<FONT COLOR="white" POINT-SIZE="14"><B>{_dot_text(meta["label"])}</B></FONT>'
            f'<BR/><FONT COLOR="#DCE6F2" POINT-SIZE="9">{_dot_text(meta.get("description", ""))}</FONT>'
            "</TD></TR>"
        ]
        headers = "".join(
            f'<TD BGCOLOR="#E8EEF5" CELLPADDING="6"><FONT COLOR="#172B4D" POINT-SIZE="8"><B>{_dot_text(AXIS_DISPLAY[axis])}</B></FONT></TD>'
            for axis in AXES
        )
        rows.append(
            '<TR><TD ALIGN="LEFT" BGCOLOR="#E8EEF5" CELLPADDING="6">'
            '<FONT COLOR="#172B4D" POINT-SIZE="8"><B>Inhabitant</B></FONT></TD>'
            + headers
            + "</TR>"
        )
        for entry in group_entries:
            rows.append(
                '<TR><TD ALIGN="LEFT" BGCOLOR="#F8FAFC" CELLPADDING="7">'
                f'<FONT COLOR="#172B4D" POINT-SIZE="10"><B>{_dot_text(entry.label)}</B></FONT></TD>'
                + "".join(_dot_cell(entry.descriptions[axis]) for axis in AXES)
                + "</TR>"
            )
        panel_id = f"panel_{group}"
        panel_ids.append(panel_id)
        panel_nodes.append(
            f'  {panel_id} [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" COLOR="#CBD5E1" BGCOLOR="white">'
            + "".join(rows)
            + "</TABLE>>];"
        )
    preview = "" if publishable else "WORKING-TREE PREVIEW - contains uncommitted team fragments"
    legend = "".join(
        f'<TD BGCOLOR="{fill}" CELLPADDING="6"><FONT COLOR="{foreground}" POINT-SIZE="9"><B>{_dot_text(label)}</B></FONT></TD>'
        for label, fill, foreground in STATUS_DISPLAY.values()
    )
    ranks = []
    for index in range(0, len(panel_ids), 2):
        pair = panel_ids[index:index + 2]
        ranks.append("  { rank=same; " + "; ".join(pair) + "; }")
        if len(pair) == 2:
            ranks.append(f"  {pair[0]} -> {pair[1]} [style=invis, weight=20];")
    vertical = []
    for index in range(len(panel_ids) - 2):
        vertical.append(f"  {panel_ids[index]} -> {panel_ids[index + 2]} [style=invis, weight=10];")
    if panel_ids:
        vertical.append(f"  {panel_ids[-1]} -> legend [style=invis, weight=5];")
    preview_row = (
        '<TR><TD COLSPAN="5"><FONT COLOR="#8B1E2D" POINT-SIZE="9"><B>'
        + _dot_text(preview)
        + "</B></FONT></TD></TR>"
        if preview
        else ""
    )
    legend_rows = (
        f'<TR>{legend}</TR>'
        '<TR><TD COLSPAN="5"><FONT COLOR="#667085" POINT-SIZE="9">'
        "Each verdict is restricted to its declared background, carrier, boundaries and charge sector."
        "</FONT></TD></TR>"
        + preview_row
    )
    return f'''digraph residual_atlas {{
  graph [rankdir=TB, bgcolor="#F5F7FA", pad="0.25", nodesep="0.25", ranksep="0.35",
         fontname="Helvetica", label="THE RESIDUAL ATLAS\\nA field guide to the inhabitants of the model universe",
         labelloc="t", fontsize=24, fontcolor="#172B4D"];
  node [shape=plain, fontname="Helvetica"];
{chr(10).join(panel_nodes)}
{chr(10).join(ranks)}
  legend [label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">{legend_rows}</TABLE>>];
{chr(10).join(vertical)}
}}
'''


def _flatten_details(value: Any, prefix: str = "") -> list[tuple[str, str, str | None]]:
    rows: list[tuple[str, str, str | None]] = []
    if isinstance(value, dict):
        if "status" in value and any(key in value for key in ("statement", "value")):
            text = value.get("statement", value.get("value", ""))
            rows.append((prefix, str(text), str(value["status"])))
        else:
            for key, child in value.items():
                child_prefix = f"{prefix} / {key}" if prefix else key
                rows.extend(_flatten_details(child, child_prefix))
    elif isinstance(value, list):
        rows.append((prefix, ", ".join(map(str, value)), None))
    elif value is not None:
        rows.append((prefix, str(value), None))
    return rows


def _h(value: Any) -> str:
    return html.escape(str(value), quote=True)


def build_html(entries: list[AtlasEntry], labels: dict[str, Any], publishable: bool) -> str:
    cards = []
    for entry in entries:
        badges = "".join(
            f'<div class="badge {_h(entry.descriptions[axis].lower())}"><span>{_h(AXIS_DISPLAY[axis])}</span><b>{_h(STATUS_DISPLAY[entry.descriptions[axis]][0])}</b></div>'
            for axis in AXES
        )
        scope_rows = "".join(
            f"<tr><th>{_h(key.replace('_', ' '))}</th><td>{_h(value)}</td></tr>"
            for key, value in entry.scope.items()
        )
        detail_rows = "".join(
            f'<tr><th>{_h(key.replace("_", " "))}</th><td>{_h(text)}'
            + (f' <span class="mini {_h(status.lower())}">{_h(STATUS_DISPLAY[status][0])}</span>' if status in STATUS_DISPLAY else "")
            + "</td></tr>"
            for key, text, status in _flatten_details(entry.details)
        )
        evidence = "".join(
            f'<li><a href="../{_h(item["path"])}">{_h(item["result_id"] or item["path"] or "Evidence")}</a>'
            f'<code>{_h(item["sha256"][:12])}</code></li>'
            for item in entry.evidence
            if item.get("path")
        ) or "<li>No evidence link supplied for this explicitly open or unmapped entry.</li>"
        search = " ".join(
            [entry.id, entry.label, entry.group, entry.team]
            + [str(value) for value in entry.scope.values()]
            + list(entry.descriptions.values())
        ).lower()
        group_meta = labels.get("groups", {}).get(entry.group, {})
        cards.append(f'''
<article class="card" data-group="{_h(entry.group)}" data-search="{_h(search)}">
  <div class="card-head"><div><p class="eyebrow">{_h(group_meta.get("label", entry.group))}</p><h2>{_h(entry.label)}</h2><code>{_h(entry.id)}</code></div><p class="team">{_h(entry.team)}</p></div>
  <div class="badges">{badges}</div>
  <details><summary>Scope passport</summary><table>{scope_rows}</table></details>
  <details><summary>Certified statements and open gates</summary><table>{detail_rows or '<tr><td>No structured detail supplied.</td></tr>'}</table></details>
  <details><summary>Evidence</summary><ul>{evidence}</ul></details>
  <p class="boundary"><b>Claim boundary:</b> {_h(entry.boundary)}</p>
  <p class="source">Atlas fragment: <code>{_h(entry.source)}</code></p>
</article>''')
    group_options = "".join(
        f'<option value="{_h(group)}">{_h(meta["label"])}</option>'
        for group, meta in labels.get("groups", {}).items()
        if any(entry.group == group for entry in entries)
    )
    preview = "" if publishable else '<div class="preview">Working-tree preview: uncommitted team fragments are included.</div>'
    counts = Counter(status for entry in entries for status in entry.descriptions.values())
    stats = "".join(
        f'<div><b>{counts[status]}</b><span>{_h(label)}</span></div>'
        for status, (label, _, _) in STATUS_DISPLAY.items()
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Residual Atlas</title>
<style>
:root{{--ink:#172b4d;--muted:#667085;--line:#d0d5dd;--paper:#fff;--ground:#f4f7fb}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{padding:3rem max(5vw,2rem) 2rem;background:linear-gradient(120deg,#132640,#234b72);color:white}} header h1{{font-size:clamp(2.4rem,6vw,5rem);line-height:1;margin:.2rem 0}} header p{{max-width:70rem;color:#dce6f2;font-size:1.1rem}}
.preview{{background:#8b1e2d;color:white;padding:.65rem 5vw;font-weight:700}} .controls{{position:sticky;top:0;z-index:2;display:flex;gap:1rem;padding:1rem 5vw;background:#edf2f7eF;backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}
input,select{{font:inherit;padding:.7rem;border:1px solid #98a2b3;border-radius:.5rem;background:white}} input{{flex:1}} main{{padding:2rem 5vw 5rem}} .stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:.7rem;margin-bottom:2rem}} .stats div{{background:white;border:1px solid var(--line);border-radius:.7rem;padding:1rem}} .stats b{{display:block;font-size:1.7rem}} .stats span{{color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,34rem),1fr));gap:1.2rem}} .card{{background:var(--paper);border:1px solid var(--line);border-radius:1rem;padding:1.2rem;box-shadow:0 8px 25px #172b4d10}} .card-head{{display:flex;justify-content:space-between;gap:1rem}} .card h2{{margin:.1rem 0 .3rem;font-size:1.35rem}} .eyebrow,.team,.source{{color:var(--muted);font-size:.82rem;margin:0;text-transform:uppercase;letter-spacing:.05em}} code{{font-size:.78rem;overflow-wrap:anywhere}}
.badges{{display:grid;grid-template-columns:repeat(5,1fr);gap:.35rem;margin:1rem 0}} .badge{{padding:.55rem;border-radius:.5rem;min-height:4rem}} .badge span,.badge b{{display:block;font-size:.75rem}} .badge span{{opacity:.8}} .certified{{background:#ddf3e4;color:#14532d}} .obstructed{{background:#fbe1e3;color:#8b1e2d}} .open{{background:#fff1c7;color:#7a4b00}} .not_applicable{{background:#eceff3;color:#475467}} .no_certified_map{{background:#ddeaf7;color:#184e77}}
details{{border-top:1px solid #eaecf0;padding:.65rem 0}} summary{{cursor:pointer;font-weight:700}} table{{width:100%;border-collapse:collapse;margin-top:.5rem}} th,td{{vertical-align:top;text-align:left;border-top:1px solid #eaecf0;padding:.45rem}} th{{width:34%;color:var(--muted);font-size:.82rem}} .mini{{display:inline-block;padding:.1rem .35rem;border-radius:.3rem;font-size:.7rem;font-weight:700}} li{{margin:.3rem 0}} li code{{float:right;color:var(--muted)}} .boundary{{background:#f8fafc;border-left:4px solid #98a2b3;padding:.75rem;font-size:.9rem}} .hidden{{display:none}}
@media(max-width:760px){{.badges,.stats{{grid-template-columns:1fr 1fr}}.controls{{position:static;flex-direction:column}}}}
</style></head><body>
<header><p class="eyebrow">A machine-checked field guide</p><h1>The Residual Atlas</h1><p>Select an inhabitant of the model universe and follow what is known about its causal propagation, classical pairing, nonlinear survival, observable response and quantum status. Every verdict remains restricted to its declared laboratory and links back to its evidence.</p></header>
{preview}
<div class="controls"><input id="search" type="search" placeholder="Search modes, backgrounds, teams or statuses"><select id="group"><option value="">All laboratories</option>{group_options}</select></div>
<main><section class="stats">{stats}</section><section class="grid" id="grid">{''.join(cards)}</section></main>
<script>
const q=document.querySelector('#search'),g=document.querySelector('#group'),cards=[...document.querySelectorAll('.card')];
function filter(){{const term=q.value.trim().toLowerCase(),group=g.value;for(const card of cards){{card.classList.toggle('hidden',!!((term&&!card.dataset.search.includes(term))||(group&&card.dataset.group!==group)))}}}}
q.addEventListener('input',filter);g.addEventListener('change',filter);
</script></body></html>
'''


def build_receipt(
    entries: list[AtlasEntry], inputs: list[Path], publishable: bool, output_bytes: dict[str, bytes]
) -> dict[str, Any]:
    by_status = Counter(status for entry in entries for status in entry.descriptions.values())
    by_group = Counter(entry.group for entry in entries)
    return {
        "schema": "pure-weyl-residual-atlas-visualization-receipt-v1",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256_path(Path(__file__)),
        "presentation_manifest": str(LABELS_PATH.relative_to(ROOT)),
        "presentation_manifest_sha256": _sha256_path(LABELS_PATH),
        "publishable_inputs_only": publishable,
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": _sha256_path(path)}
            for path in inputs
        ],
        "entry_count": len(entries),
        "counts_by_group": dict(sorted(by_group.items())),
        "counts_by_status": {status: by_status[status] for status in STATUSES},
        "outputs": {name: _sha256_bytes(data) for name, data in sorted(output_bytes.items())},
        "claim_boundary": (
            "The renderer copies scoped statuses from team atlas fragments. Presentation labels "
            "and grouping create no scientific inference, carrier map, particle interpretation, "
            "or lifecycle promotion."
        ),
    }


def render_dot(dot_path: Path, targets: dict[str, Path]) -> None:
    dot = shutil.which("dot")
    if not dot:
        raise RuntimeError("Graphviz 'dot' is required for --render")
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "0"
    for fmt, target in targets.items():
        subprocess.run(
            [dot, f"-T{fmt}", str(dot_path), "-o", str(target)],
            check=True,
            env=environment,
        )


def generate(include_working_tree: bool = False, render: bool = False) -> dict[str, Any]:
    labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    inputs, tracked = discover_fragments(include_working_tree=include_working_tree)
    if not inputs:
        raise ValueError("no tracked residual-atlas fragments found")
    publishable = all(path in tracked for path in inputs)
    entries = load_entries(inputs, labels)
    payload = public_payload(entries, inputs, publishable)
    output_bytes = {
        "residual-atlas-overview.json": _json_bytes(payload),
        "residual-atlas-overview.dot": build_dot(entries, labels, publishable).encode("utf-8"),
        "residual-atlas-passports.html": build_html(entries, labels, publishable).encode("utf-8"),
    }
    for name, data in output_bytes.items():
        (HERE / name).write_bytes(data)
    if render:
        render_dot(
            OUTPUTS["dot"],
            {"svg": OUTPUTS["svg"], "png": OUTPUTS["png"], "pdf": OUTPUTS["pdf"]},
        )
        for key in ("svg", "png", "pdf"):
            output_bytes[OUTPUTS[key].name] = OUTPUTS[key].read_bytes()
    else:
        for key in ("svg", "png", "pdf"):
            if OUTPUTS[key].exists():
                output_bytes[OUTPUTS[key].name] = OUTPUTS[key].read_bytes()
    receipt = build_receipt(entries, inputs, publishable, output_bytes)
    OUTPUTS["receipt"].write_bytes(_json_bytes(receipt))
    return receipt


def check(include_working_tree: bool = False, render: bool = False) -> None:
    expected = {key: path.read_bytes() for key, path in OUTPUTS.items() if path.exists()}
    receipt = generate(include_working_tree=include_working_tree, render=render)
    changed = [key for key, data in expected.items() if OUTPUTS[key].read_bytes() != data]
    if changed:
        raise SystemExit(f"residual atlas visualization is stale: {changed}")
    if not receipt["publishable_inputs_only"] and not include_working_tree:
        raise SystemExit("publishable build unexpectedly consumed an untracked fragment")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-working-tree", action="store_true", help="include untracked team fragments in a preview")
    parser.add_argument("--render", action="store_true", help="render SVG, PNG and PDF with Graphviz")
    parser.add_argument("--check", action="store_true", help="verify that committed outputs are current")
    args = parser.parse_args()
    if args.check:
        check(include_working_tree=args.include_working_tree, render=args.render)
    else:
        receipt = generate(include_working_tree=args.include_working_tree, render=args.render)
        print(
            f"wrote residual atlas visualization: {receipt['entry_count']} entries, "
            f"publishable_inputs_only={receipt['publishable_inputs_only']}"
        )


if __name__ == "__main__":
    main()
