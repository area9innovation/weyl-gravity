#!/usr/bin/env python3
"""Generate the human-reviewed Phase-1 paper-coverage overlay.

The discovery graph supplies paper inventory only.  Materiality and result-to-paper
routing below are the explicit 2026-07-22 decision of human coordinator Asger
Alstrup Palm; they are deliberately not inferred from filenames or prose.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-07-22"
HUMAN = "Asger Alstrup Palm"
PREFIX = "sf:coverage/result/"

PAPERS = {
    "00": "paper:00-ghosts-geometry-reality",
    "09": "paper:09-relational-clocks-berger-d-cartan",
    "10": "paper:10-compact-einstein-maxwell-weyl-phase-space",
    "11": "paper:11-gravity-light-cyclic-causal-ell3",
    "12": "paper:12-pure-weyl-one-loop-bv-anomaly",
    "13": "paper:13-compact-weyl-maxwell-second-order-tangent-cone",
    "14": "paper:14-pure-weyl-black-hole-radiation",
    "90": "paper:90-cyclic-green-transfer-bridge",
    "91": "paper:91-charge-fibre-taub-bridge",
    "92": "paper:92-extra-axial-lee-wald-bridge",
    "98": "paper:98-physicist-executive-summary",
    "99": "paper:99-how-to-build-a-universe",
}

MARKDOWN_PAPERS = {
    "90": "paper/90-cyclic-green-transfer-bridge.md",
    "91": "paper/91-charge-fibre-taub-bridge.md",
    "92": "paper/92-extra-axial-lee-wald-bridge.md",
    "98": "paper/98-physicist-executive-summary.md",
    "99": "paper/99-how-to-build-a-universe.md",
}

RESULTS: dict[str, dict[str, Any]] = {
    "CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1": {
        "source": "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json",
        "schema": "pure-weyl-classical-phase1-counterflow-claim-map-v1",
        "materiality": "NEGATIVE_RESULT",
        "boundary": "Declared same-field two-phase counterflow Phase-1 classification: selected Berger causal parent, but no robust physically healthy Phase-2 candidate; not a universal no-go for changed architectures.",
        "rationale": "Terminal Phase-1 classification of the first constructive successor and its scoped physical obstruction.",
        "technical": [("09", "NEGATIVE_RESULT")],
        "overview": ["00", "98", "99"],
    },
    "BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1": {
        "source": "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json",
        "schema": "pure-weyl-bridge-phase1-einstein-extra-contribution-v1",
        "materiality": "TECHNICAL",
        "boundary": "Exact compact-carrier Einstein/additional-Weyl structural contribution, including parity completion and charge-fibre dependence; no final residual, causal, particle, or quantum theorem.",
        "rationale": "Authoritative cross-paper structural bridge for the linear and nonlinear Einstein/extra comparison.",
        "technical": [("10", "SUPPORTING_EVIDENCE"), ("13", "SUPPORTING_EVIDENCE"), ("91", "SUPPORTING_EVIDENCE"), ("92", "SUPPORTING_EVIDENCE")],
        "overview": [],
    },
    "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1": {
        "source": "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json",
        "schema": "pure-weyl-nonlinear-phase1-interaction-disposition-v1",
        "materiality": "TECHNICAL",
        "boundary": "Exact retained Berger q2/q3/ell3 representatives and tested cyclic-removability status; the complete deformation class and branch-resolved physical mixing remain open.",
        "rationale": "Current invariant-interaction boundary required to prevent the retained representative from being overinterpreted.",
        "technical": [("11", "PRIMARY_THEOREM")],
        "overview": [],
    },
    "PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1": {
        "source": "paper/09-relational-clocks-berger-d-cartan-claim-map.json",
        "schema": "paper09-publication-claim-map-v1",
        "materiality": "TECHNICAL",
        "boundary": "Paper 09 publication boundary: legacy conditional observables remain typed, while the tested counterflow candidate supplies no promoted operational observable or healthy Phase-2 clock.",
        "rationale": "Publication-current nonactivation boundary for the counterflow health and observer chain.",
        "technical": [("09", "LIMITATION")],
        "overview": [],
    },
    "PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1": {
        "source": "quantum-weyl/phase1/certificates/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1.json",
        "schema": "phase1-quantum-disposition-synthesis-v1",
        "certificate": "sf:quantum-weyl.phase1/certificate/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1",
        "materiality": "HEADLINE",
        "boundary": "Strict local one-loop obstruction, changed formal tau-adic local restoration, and nonactivation of an action-specific successor; no Lorentzian QME, full-BV Hadamard state, particles, positivity, scattering, or unitarity.",
        "rationale": "Phase-1 quantum synthesis fixes the strict-versus-changed-theory distinction and the exact open quantum gates.",
        "technical": [("12", "PRIMARY_THEOREM")],
        "overview": ["00", "98", "99"],
    },
    "PURE_WEYL_BH_ENDPOINT_NONSELECTION_ASSEMBLY": {
        "source": "black_hole_programme/certificates/BH_ENDPOINT_NONSELECTION_ASSEMBLY.json",
        "schema": "pure-weyl-bh-endpoint-nonselection-assembly-v1",
        "certificate": "sf:black_hole_programme/certificate/PURE_WEYL_BH_ENDPOINT_NONSELECTION_ASSEMBLY",
        "materiality": "HEADLINE",
        "boundary": "Scoped Schwarzschild axial endpoint nonselection: future-horizon regularity and tested leading real-frequency asymptotics do not force the additional branch to vanish; no general causal-truncation no-go or complete scattering theorem.",
        "rationale": "The programme's current physically visible black-hole boundary result.",
        "technical": [("14", "PRIMARY_THEOREM")],
        "overview": [],
    },
    "PURE_WEYL_BH2C_SYMBOLIC_FLUX_RADIATION_CLASS": {
        "source": "black_hole_programme/certificates/BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json",
        "schema": "pure-weyl-bh2c-symbolic-flux-radiation-class-v1",
        "certificate": "sf:black_hole_programme/certificate/PURE_WEYL_BH2C_SYMBOLIC_FLUX_RADIATION_CLASS",
        "materiality": "TECHNICAL",
        "boundary": "Symbolic real-frequency flux/radiation-class evidence on the declared Schwarzschild carrier; metric reconstruction, complex frequencies, full exterior phase space, stability, and ringdown remain open.",
        "rationale": "Direct technical support for the scoped Paper 14 radiation-class statement.",
        "technical": [("14", "SUPPORTING_EVIDENCE")],
        "overview": [],
    },
    "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1": {
        "source": "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json",
        "schema": "einstein-maxwell-weyl-polar-direct-lee-wald-completion-v1",
        "certificate": "sf:bridge/certificate/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1",
        "materiality": "TECHNICAL",
        "boundary": "Generic polar direct four-dimensional Lee-Wald completion before final ungauged BV and residual descent; no exceptional-sector, causal, norm, ghost, positivity, or unitarity claim.",
        "rationale": "Closes the polar direct-current gap in the compact Einstein/extra comparison.",
        "technical": [("10", "SUPPORTING_EVIDENCE")],
        "overview": [],
    },
}


def paper_class(title: str) -> str:
    prefix = title.split("-", 1)[0]
    return "overview" if prefix in {"00", "0", "98", "99"} else "technical"


def paper_node(pid: str, title: str, path: str) -> dict[str, Any]:
    return {
        "kind": "paper",
        "id": pid,
        "title": title,
        "source": {"path": path},
        "body": {
            "paper_class": paper_class(title),
            "native": {"source_kind": "paper", "adapter_classified": True},
        },
        "edges": [],
    }


def result_id(raw: str) -> str:
    return PREFIX + raw


def build(discovery: dict[str, Any]) -> dict[str, Any]:
    papers: dict[str, dict[str, Any]] = {}
    for node in discovery.get("nodes", []):
        if node.get("kind") != "paper":
            continue
        pid = node["id"]
        title = node.get("title", pid.removeprefix("paper:"))
        path = node.get("source", {}).get("path", "")
        papers[pid] = paper_node(pid, title, path)
    for number, path in MARKDOWN_PAPERS.items():
        title = Path(path).stem
        papers[PAPERS[number]] = paper_node(PAPERS[number], title, path)

    missing = set(PAPERS.values()) - set(papers)
    if missing:
        raise ValueError(f"paper inventory missing required nodes: {sorted(missing)}")

    nodes: list[dict[str, Any]] = [papers[k] for k in sorted(papers)]
    for raw, spec in RESULTS.items():
        rid = result_id(raw)
        source = ROOT / spec["source"]
        if not source.is_file() or raw not in source.read_text():
            raise ValueError(f"source does not bind result {raw}: {spec['source']}")
        native = {
            "source_kind": "human-reviewed-phase1-result",
            "source_schema": spec["schema"],
            "result_id": raw,
        }
        if "certificate" in spec:
            native["from_certificate"] = spec["certificate"]
        nodes.append({
            "kind": "result",
            "id": rid,
            "title": raw,
            "source": {"path": spec["source"]},
            "body": {
                "lifecycle": "CERTIFIED",
                "boundary": spec["boundary"],
                "stale": False,
                "superseded": False,
                "native": native,
            },
            "edges": ([{"rel": "BRIDGED_FROM", "to": spec["certificate"]}] if "certificate" in spec else []),
        })
        nodes.append({
            "kind": "materiality",
            "id": f"sf:coverage/materiality/{raw}/v1",
            "body": {
                "result_id": rid,
                "materiality": spec["materiality"],
                "version": 1,
                "by": HUMAN,
                "stamp": STAMP,
                "rationale": spec["rationale"],
                "native": {"source_schema": "materiality-v0"},
            },
        })
        for number, edge_kind in spec["technical"]:
            pid = PAPERS[number]
            cid = f"{pid}/claim/{raw.lower()}"
            nodes.append({
                "kind": "paper_claim",
                "id": cid,
                "body": {
                    "paper": pid,
                    "material": True,
                    "asserts_lifecycle": "CERTIFIED",
                    "boundary": spec["boundary"],
                    "cites": [rid],
                },
            })
            nodes.append({
                "kind": "result_paper_edge",
                "id": f"sf:coverage/edge/{raw}/paper-{number}/v1",
                "body": {
                    "from": rid,
                    "to": pid,
                    "claim": cid,
                    "edge_kind": edge_kind,
                    "stale": False,
                    "version": 1,
                    "stamp": STAMP,
                    "native": {"source_schema": "result-paper-edge-v0"},
                },
            })
        for number in spec["overview"]:
            nodes.append({
                "kind": "result_paper_edge",
                "id": f"sf:coverage/edge/{raw}/paper-{number}/overview-v1",
                "body": {
                    "from": rid,
                    "to": PAPERS[number],
                    "edge_kind": "OVERVIEW_MENTION",
                    "stale": False,
                    "version": 1,
                    "stamp": STAMP,
                    "native": {"source_schema": "result-paper-edge-v0"},
                },
            })
    nodes.sort(key=lambda node: (node["kind"], node["id"]))
    return {
        "ir": "science-forge-ir-v0",
        "schema": "phase1-paper-coverage-overlay-v1",
        "human_materiality_decision": {
            "by": HUMAN,
            "stamp": STAMP,
            "version": 1,
            "classified_results": len(RESULTS),
            "policy": "All other discovered results remain explicitly unclassified and visible in REVIEW_QUEUE.",
        },
        "nodes": nodes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = build(json.loads(args.discovery.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(payload['nodes'])} typed overlay nodes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
