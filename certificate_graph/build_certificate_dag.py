#!/usr/bin/env python3
"""Build reproducible certificate and universe-building dependency DAGs.

The scientific graph is read from a Git tree, never from the ambient working
tree.  This keeps a graph receipt stable while other teams have uncommitted
artifacts in the shared checkout.  Modern certificates are identified by a
``result_id``; legacy top-level JSON files in ``certificates/`` directories
are identified by their repository path.

The full graph is derived.  The public milestone graph is curated in
``universe_milestones.json``, but every evidence reference in that file must
resolve to an actual certificate in the same frozen Git tree.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
MILESTONES_PATH = HERE / "universe_milestones.json"

OUTPUTS = {
    "graph": HERE / "certificate-dag.json",
    "dot": HERE / "certificate-dag.dot",
    "public_dot": HERE / "universe-building-dag.dot",
    "issues": HERE / "unresolved-dependencies.json",
    "receipt": HERE / "certificate-graph-receipt.json",
}

HEX64 = re.compile(r"^[0-9a-f]{64}$")
JSON_REF = re.compile(r"(?P<path>[^\s'\"`]+\.json)(?:#[^\s'\"`]*)?$")
WRAP_AT = 28


@dataclass(frozen=True)
class Certificate:
    key: str
    path: str
    result_id: str | None
    label: str
    family: str
    status: str
    color_state: str
    dependency_tags: tuple[str, ...]
    payload: dict[str, Any]


@dataclass(frozen=True, order=True)
class Edge:
    source: str
    target: str
    relation: str
    evidence: str


@lru_cache(maxsize=1)
def _git_repo() -> Path:
    return Path(
        subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT,
        text=True,
        capture_output=True,
        check=True,
        ).stdout.strip()
    )


def _run_git(args: list[str]) -> str:
    repo = _git_repo()
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    ).stdout


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return PROJECT.relative_to(_git_repo()).as_posix()


def load_git_tree(treeish: str) -> dict[str, bytes]:
    """Return project-relative files from ``treeish``."""

    prefix = _git_prefix()
    listing = _run_git(["ls-tree", "-r", "--name-only", treeish, "--", prefix])
    files: dict[str, bytes] = {}
    for git_path in sorted(line for line in listing.splitlines() if line):
        if not git_path.endswith(".json"):
            continue
        relative = PurePosixPath(git_path).relative_to(prefix).as_posix()
        if relative.startswith("certificate_graph/"):
            continue
        blob = subprocess.run(
            ["git", "show", f"{treeish}:{git_path}"],
            cwd=_git_repo(),
            capture_output=True,
            check=True,
        ).stdout
        files[relative] = blob
    return files


def _json_dict(raw: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _is_certificate(path: str, data: dict[str, Any]) -> bool:
    parts = PurePosixPath(path).parts
    if path.endswith(".schema.json") or "schema" in parts:
        return False
    if "result_id" in data and isinstance(data["result_id"], str):
        return True
    if "certificates" not in parts:
        return False
    certificate_index = parts.index("certificates")
    # Large hash-addressed carrier and bidegree manifests are support data.
    if certificate_index + 2 < len(parts):
        return False
    upper_name = PurePosixPath(path).name.upper()
    if "PAYLOAD" in upper_name or upper_name.endswith("_PROOF.JSON"):
        return False
    return True


def _family(path: str) -> str:
    if path.startswith("d_quotient_classical/"):
        return "Classical / clocks"
    if path.startswith("bridge/"):
        return "Einstein / boundaries"
    if path.startswith("quantum-weyl/transfer/"):
        return "Nonlinear transfer"
    if path.startswith("quantum-weyl/"):
        return "Quantum / microlocal"
    if path.startswith("covariant_completion/"):
        return "Covariant causal complex"
    if path.startswith("field_bv_identification/"):
        return "Residual BV--BFV"
    if path.startswith("analytic_completion/"):
        return "Analytic completion"
    if path.startswith("d_quotient_programme/"):
        return "Programme ledger"
    return "Foundations and other"


LAYOUT_TOPICS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "Classical / clocks": (
        ("Nonlinear brackets and D--Cartan", ("q2", "cartan", "arity", "nonlinear")),
        ("Clocks, light, and redshift", ("clock", "redshift", "maxwell", "observer")),
        ("Charges, Taub fibres, and quotients", ("charge", "quotient", "taub", "moment_map")),
        ("Causal and microlocal propagation", ("green", "causal", "volterra", "biwave", "cone", "microlocal", "hadamard")),
        ("BV operators and contractions", ("bv", "minimal", "nonminimal", "operator", "layout", "witness", "reattached", "shear")),
        ("Scoped obstruction tests", ("no_go", "no-go", "obstruction", "incompatible")),
    ),
    "Covariant causal complex": (
        ("Tractor, BGG, and detour transfer", ("tractor", "bgg", "kostant", "pbw", "detour")),
        ("Green homotopies and support", ("green", "causal", "hyperbolic", "retarded", "advanced", "support")),
        ("Symbols, cones, and factorization tests", ("symbol", "rank", "factor", "no_go", "no-go", "obstruction", "feasibility", "cone", "characteristic", "principal")),
        ("Metric, curvature, and endpoint bridge", ("metric", "curvature", "weyl", "cotton", "bach", "endpoint")),
        ("Cyclicity, currents, and pairings", ("cyclic", "current", "pairing", "adjoint", "hessian", "symplectic")),
        ("Auxiliary systems and deformation retracts", ("auxiliary", "witness", "retract", "projector", "contraction", "saddle", "shift_split")),
        ("Residual endpoint recovery", ("residual", "bfv", "h4", "gram", "ckv", "no_duplication", "quasi_isomorphism")),
        ("Mode and spectrum checks", ("spectrum", "spectra", "multiplicity", "helicity", "frequency", "energy_mode", "sobolev", "residue")),
        ("Operator identities and normal forms", ("operator", "derivative", "curl", "biwave", "intertwiner", "composition", "normal_form")),
        ("Foundations and globalization", ("convention", "gauge_invariance", "jet_basis", "globalization", "status", "final_claim", "closure")),
        ("Complex assembly and chain identities", ("complex", "chain", "nilpot", "homotopy", "differential", "assembly")),
    ),
    "Einstein / boundaries": (
        ("Radiation and Lee--Wald pairings", ("axial", "polar", "radiative", "wave", "lee_wald", "symplectic", "green_pairing", "energy_pairing")),
        ("Taub and nonlinear obstruction tests", ("taub", "obstruction", "linearization", "second_order", "cokernel", "nonlinear")),
        ("Einstein inclusion and branch comparison", ("einstein", "embedding", "inclusion", "chain_map", "branch")),
        ("Maxwell, flux, and charge sectors", ("maxwell", "charge", "flux")),
        ("Boundaries and asymptotic structure", ("asymptotic", "bondi", "adm", "bms", "boundary", "ads", "desitter", "de_sitter")),
        ("Curvature and action identities", ("curvature", "hessian", "generator", "action")),
        ("BV and residual bridge", ("bv", "hpl", "retract", "residual", "metric_to_residual", "bgg", "preimage")),
        ("Linear Bach operators", ("bach_operator", "free_bv_complex", "quadratic")),
    ),
    "Nonlinear transfer": (
        ("Certified classical imports", ("_import", "nonlinear_import")),
        ("Interacting brackets", ("q2", "cubic", "arity", "bracket", "l_infinity", "linfinity")),
        ("Residual D--Cartan structure", ("cartan", "d_derivation", "residual", "d_disposition")),
        ("Causal Green transfer", ("green", "causal", "support", "homotopy")),
        ("Cyclicity and imported pairings", ("cyclic", "pairing", "darboux", "polarization")),
        ("Einstein-sector interaction tests", ("einstein", "taub", "branch", "amplitude", "curvature", "bach_seed")),
        ("Transfer infrastructure", ("pbw", "backend", "bootstrap", "physical_run_contract", "q1")),
    ),
    "Quantum / microlocal": (
        ("Local BV, anomalies, and QME", ("local_bv", "anomaly", "qme", "brst", "counterterm", "cohomology", "descent")),
        ("Local tensor-algebra foundations", ("foundation", "canonicalization", "schouten", "hodge", "specialization")),
        ("Lorentzian Hadamard and microlocal analysis", ("lorentzian", "hadamard", "microlocal", "wavefront", "pauli", "jordan", "moller", "causal")),
        ("Euclidean and reduced spectral tests", ("spectral", "euclidean", "determinant", "heat_kernel", "eigen", "mode")),
        ("Quantum residual transfer", ("residual", "transfer", "cartan", "pairing")),
        ("Classical imports and freeze gates", ("classical", "import", "snapshot", "freeze")),
        ("Measure and coefficient calculations", ("measure", "coefficient", "regularization", "zero_mode", "one_loop")),
    ),
    "Analytic completion": (
        ("Closed operators and domains", ("closed", "operator", "domain", "bound", "finite_total")),
        ("Krein and Hilbert representations", ("krein", "hilbert", "fundamental_symmetry")),
        ("Completed cohomology and pairing", ("h4", "gram", "cohomology", "pairing")),
    ),
    "Residual BV--BFV": (
        ("Residual state complex", ("state", "residual", "bfv", "chain")),
        ("Cohomology and pairing", ("cohomology", "pairing", "gram", "polarized")),
        ("Field-to-residual bridge", ("field", "metric", "bridge", "transfer")),
    ),
}


def _layout_topic(certificate: Certificate) -> str:
    """Return an evidence-neutral navigation box for the technical graph."""

    path_parts = PurePosixPath(certificate.path).parts
    scoped_path = "/".join(path_parts[1:]) if len(path_parts) > 1 else certificate.path
    haystack = (scoped_path + " " + certificate.label).lower()
    if any(
        token in haystack
        for token in (
            "source_manifest",
            "input_manifest",
            "verification_receipt",
            "programme_status",
            "registry",
            "ledger",
        )
    ):
        return "Receipts and provenance"
    for topic, tokens in LAYOUT_TOPICS.get(certificate.family, ()):
        if any(token in haystack for token in tokens):
            return topic
    return "Cross-cutting certificates"


def _status_text(data: dict[str, Any]) -> str:
    for key in (
        "claim_status",
        "result_state",
        "lifecycle_state",
        "lifecycle_layer",
        "lifecycle_status",
        "status",
        "verdict",
        "classification",
    ):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    if data.get("complete") is True:
        return "COMPLETE"
    if data.get("fail_closed") is True:
        return "FAIL_CLOSED"
    return "UNCLASSIFIED"


def _color_state(data: dict[str, Any], status: str) -> str:
    text = status.upper()
    if any(word in text for word in ("NO_GO", "OBSTRUCT", "BLOCKED", "FAIL_CLOSED")):
        return "obstruction"
    if any(
        word in text
        for word in (
            "OPEN",
            "PARTIAL",
            "PREFLIGHT",
            "PENDING",
            "IN_PROGRESS",
            "CANDIDATE",
            "CONTRACT_READY",
            "CLASSIFIED",
            "NOT_REACHED",
        )
    ):
        return "partial"
    if any(word in text for word in ("CERTIFIED", "COMPLETE", "VERIFIED", "PASS", "RESTORED")):
        return "certified"
    flags = data.get("claim_flags")
    if isinstance(flags, dict) and any(value is False for value in flags.values()):
        return "partial"
    return "unclassified"


def collect_certificates(files: dict[str, bytes]) -> tuple[list[Certificate], dict[str, dict[str, Any]]]:
    parsed: dict[str, dict[str, Any]] = {}
    certificates: list[Certificate] = []
    for path, raw in sorted(files.items()):
        if not path.endswith(".json"):
            continue
        data = _json_dict(raw)
        if data is None:
            continue
        parsed[path] = data
        if not _is_certificate(path, data):
            continue
        result_id = data.get("result_id") if isinstance(data.get("result_id"), str) else None
        label = result_id or PurePosixPath(path).stem
        status = _status_text(data)
        raw_tags = data.get("dependency_tags", data.get("dependency_tag", ()))
        if isinstance(raw_tags, str):
            tags = (raw_tags,)
        elif isinstance(raw_tags, list):
            tags = tuple(str(item) for item in raw_tags)
        else:
            tags = ()
        key = "cert:" + hashlib.sha256(path.encode()).hexdigest()[:16]
        certificates.append(
            Certificate(
                key=key,
                path=path,
                result_id=result_id,
                label=label,
                family=_family(path),
                status=status,
                color_state=_color_state(data, status),
                dependency_tags=tags,
                payload=data,
            )
        )
    return certificates, parsed


def _walk(value: Any, context: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_context = (*context, str(key))
            yield child_context, child
            yield from _walk(child, child_context)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_context = (*context, str(index))
            yield child_context, child
            yield from _walk(child, child_context)


def _normalize_ref(source_path: str, reference: str, all_paths: set[str]) -> str | None:
    reference = reference.strip().replace("\\", "/")
    if reference.startswith("https://") or reference.startswith("http://"):
        return None
    project_prefix = _git_prefix() + "/"
    if reference.startswith(project_prefix):
        reference = reference[len(project_prefix) :]
    candidates: list[str] = []
    root_candidate = PurePosixPath(reference).as_posix()
    candidates.append(root_candidate)
    parent_candidate = (PurePosixPath(source_path).parent / reference).as_posix()
    # PurePosixPath does not collapse '..'; use a small lexical normalizer.
    def collapse(path: str) -> str:
        stack: list[str] = []
        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(part)
        return "/".join(stack)

    candidates.append(collapse(parent_candidate))
    for candidate in candidates:
        if candidate in all_paths:
            return candidate
    suffix = reference.lstrip("./")
    matches = [path for path in all_paths if path.endswith(suffix)]
    return matches[0] if len(matches) == 1 else None


def _relation(context: tuple[str, ...]) -> str:
    joined = ".".join(context).lower()
    if "import" in joined:
        return "IMPORTS"
    if "verif" in joined or "independent" in joined:
        return "INDEPENDENTLY_VERIFIES"
    return "DEPENDS_ON"


def _nonordering_relation(
    source_path: str, target_path: str, context: tuple[str, ...]
) -> str | None:
    """Identify provenance cross-links that are not scientific prerequisites.

    Programme registration points both from an aggregate ledger to a team
    receipt and back from the receipt to the ledger.  Verification receipts
    and source manifests likewise authenticate one another.  Keeping these as
    ordinary prerequisite arrows would manufacture cycles in an otherwise
    ordered scientific dependency graph.
    """

    joined = ".".join(context).lower()
    pair = source_path + " " + target_path
    if "D_QUOTIENT_PROGRAMME_STATUS.json" in pair and any(
        token in joined
        for token in (
            "programme_status",
            "programme_registration",
            "team_contributions",
            "team_inputs",
            "source_artifacts",
        )
    ):
        return "REGISTERS"
    if (
        "VERIFICATION_RECEIPT.json" in pair
        and "SOURCE_MANIFEST.json" in pair
        and ("receipt" in joined or "source_manifest" in joined)
    ):
        return "MUTUALLY_AUDITS"
    return None


def _context_is_dependency(context: tuple[str, ...]) -> bool:
    joined = ".".join(context).lower()
    return any(
        token in joined
        for token in (
            "depend",
            "input",
            "import",
            "source",
            "parent",
            "base_",
            "certificate",
            "upstream",
            "proof",
            "classical_commit",
        )
    )


def derive_edges(
    certificates: list[Certificate], files: dict[str, bytes]
) -> tuple[list[Edge], dict[str, Any]]:
    by_path = {certificate.path: certificate for certificate in certificates}
    by_id: dict[str, list[Certificate]] = defaultdict(list)
    for certificate in certificates:
        if certificate.result_id:
            by_id[certificate.result_id].append(certificate)
    all_paths = set(files)
    edges: set[Edge] = set()
    unresolved: list[dict[str, str]] = []
    support_refs: set[tuple[str, str]] = set()
    hash_mismatches: list[dict[str, str]] = []
    cross_links: set[Edge] = set()

    for consumer in certificates:
        for context, value in _walk(consumer.payload):
            if isinstance(value, str):
                match = JSON_REF.search(value)
                if match:
                    reference = match.group("path")
                    target_path = _normalize_ref(consumer.path, reference, all_paths)
                    if target_path == consumer.path:
                        continue
                    if target_path and target_path in by_path and target_path != consumer.path:
                        cross_relation = _nonordering_relation(
                            target_path, consumer.path, context
                        )
                        edge = Edge(
                            source=by_path[target_path].key,
                            target=consumer.key,
                            relation=cross_relation or _relation(context),
                            evidence=".".join(context),
                        )
                        (cross_links if cross_relation else edges).add(edge)
                    elif target_path and target_path != consumer.path:
                        if "/schema/" not in target_path and not target_path.endswith(
                            ".schema.json"
                        ):
                            support_refs.add((consumer.path, target_path))
                    elif _context_is_dependency(context):
                        unresolved.append(
                            {
                                "consumer": consumer.path,
                                "context": ".".join(context),
                                "reference": reference,
                            }
                        )
                if value in by_id and value != consumer.result_id:
                    targets = by_id[value]
                    if len(targets) == 1 and _context_is_dependency(context):
                        edges.add(
                            Edge(
                                source=targets[0].key,
                                target=consumer.key,
                                relation=_relation(context),
                                evidence=".".join(context),
                            )
                        )
            if isinstance(value, dict):
                for reference, expected_hash in value.items():
                    if not isinstance(reference, str) or not reference.endswith(".json"):
                        continue
                    if not isinstance(expected_hash, str) or not HEX64.fullmatch(expected_hash):
                        continue
                    target_path = _normalize_ref(consumer.path, reference, all_paths)
                    if not target_path:
                        continue
                    actual_hash = hashlib.sha256(files[target_path]).hexdigest()
                    if actual_hash != expected_hash:
                        hash_mismatches.append(
                            {
                                "consumer": consumer.path,
                                "reference": target_path,
                                "expected": expected_hash,
                                "actual": actual_hash,
                            }
                        )

    duplicate_ids = {
        result_id: sorted(certificate.path for certificate in values)
        for result_id, values in sorted(by_id.items())
        if len(values) > 1
    }
    issues = {
        "duplicate_result_ids": duplicate_ids,
        "unresolved_declared_json_dependencies": sorted(
            unresolved, key=lambda row: (row["consumer"], row["context"], row["reference"])
        ),
        "support_json_references": [
            {"consumer": consumer, "support": support}
            for consumer, support in sorted(support_refs)
        ],
        "hash_mismatches": sorted(
            hash_mismatches, key=lambda row: (row["consumer"], row["reference"])
        ),
        "nonordering_provenance_cross_links": [
            edge.__dict__ for edge in sorted(cross_links)
        ],
    }
    return sorted(edges), issues


def _cycles(nodes: Iterable[str], edges: Iterable[Edge]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    indegree = {node: 0 for node in nodes}
    for edge in edges:
        if edge.source == edge.target or edge.target in adjacency[edge.source]:
            continue
        adjacency[edge.source].add(edge.target)
        indegree[edge.target] = indegree.get(edge.target, 0) + 1
        indegree.setdefault(edge.source, 0)
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited: set[str] = set()
    while queue:
        node = queue.popleft()
        visited.add(node)
        for target in sorted(adjacency[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    remainder = set(indegree) - visited
    if not remainder:
        return []

    # Tarjan SCCs make a cycle receipt useful instead of returning one opaque set.
    index = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(adjacency[node]):
            if target not in remainder:
                continue
            if target not in indices:
                strongconnect(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == node:
                    break
            if len(component) > 1:
                components.append(sorted(component))

    for node in sorted(remainder):
        if node not in indices:
            strongconnect(node)
    return sorted(components)


def _wrap(label: str, width: int = WRAP_AT) -> str:
    words = re.split(r"([_ /-])", label)
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + len(word) > width:
            lines.append(current.rstrip())
            current = word.lstrip()
        else:
            current += word
    if current:
        lines.append(current.rstrip())
    return "\n".join(lines)


def _dot_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


COLORS = {
    "certified": ("#d9f2df", "#287a3d"),
    "partial": ("#fff0bf", "#9a6a00"),
    "obstruction": ("#ffd8d4", "#a52a2a"),
    "open": ("#eceff3", "#667085"),
    "unclassified": ("#e9e4f5", "#67558c"),
}


def full_dot(certificates: list[Certificate], edges: list[Edge]) -> str:
    lines = [
        "digraph CertificateDAG {",
        "  graph [rankdir=TB, bgcolor=\"white\", pad=0.25, nodesep=0.18, ranksep=0.55, concentrate=true, compound=true, newrank=true, remincross=true, fontname=\"Helvetica\"];",
        "  node [shape=box, style=\"rounded,filled\", fontname=\"Helvetica\", fontsize=8, penwidth=1.0, margin=\"0.07,0.04\"];",
        "  edge [fontname=\"Helvetica\", fontsize=6, color=\"#98a2b3\", arrowsize=0.55];",
        "  label=\"Certified construction graph — generated from repository artifacts\";",
        "  labelloc=t; fontsize=16;",
    ]
    grouped: dict[str, list[Certificate]] = defaultdict(list)
    for certificate in certificates:
        grouped[certificate.family].append(certificate)

    def emit_node(certificate: Certificate, indent: str) -> None:
        fill, border = COLORS[certificate.color_state]
        status = _wrap(certificate.status, 24)
        label = _wrap(certificate.label)
        tooltip = f"{certificate.path} | {certificate.status}"
        lines.append(
            f"{indent}{_dot_quote(certificate.key)} "
            f"[label={_dot_quote(label + chr(10) + status)}, "
            f"fillcolor=\"{fill}\", color=\"{border}\", "
            f"tooltip={_dot_quote(tooltip)}, "
            f"URL={_dot_quote('../' + certificate.path)}];"
        )

    for cluster_index, family in enumerate(sorted(grouped)):
        family_certificates = sorted(grouped[family], key=lambda row: row.path)
        lines.append(f"  subgraph cluster_{cluster_index} {{")
        lines.append(
            f"    label={_dot_quote(family)}; color=\"#98a2b3\"; "
            "style=\"rounded\"; penwidth=1.2;"
        )
        if len(family_certificates) < 12:
            for certificate in family_certificates:
                emit_node(certificate, "    ")
        else:
            topics: dict[str, list[Certificate]] = defaultdict(list)
            for certificate in family_certificates:
                topics[_layout_topic(certificate)].append(certificate)
            singletons = [
                topic
                for topic, topic_certificates in topics.items()
                if len(topic_certificates) == 1 and topic != "Cross-cutting certificates"
            ]
            for topic in singletons:
                topics["Cross-cutting certificates"].extend(topics.pop(topic))
            for topic_index, topic in enumerate(sorted(topics)):
                topic_certificates = topics[topic]
                lines.append(
                    f"    subgraph cluster_{cluster_index}_{topic_index} {{"
                )
                lines.append(
                    f"      label={_dot_quote(topic)}; color=\"#d0d5dd\"; "
                    "bgcolor=\"#f8fafc\"; style=\"rounded,dashed\"; "
                    "penwidth=0.8; fontsize=10;"
                )
                for certificate in topic_certificates:
                    emit_node(certificate, "      ")
                lines.append("    }")
        lines.append("  }")
    relation_style = {
        "DEPENDS_ON": ("#667085", "solid"),
        "IMPORTS": ("#175cd3", "bold"),
        "INDEPENDENTLY_VERIFIES": ("#7a5af8", "dashed"),
    }
    for edge in edges:
        color, style = relation_style.get(edge.relation, ("#667085", "solid"))
        lines.append(
            f"  {_dot_quote(edge.source)} -> {_dot_quote(edge.target)} "
            f"[color=\"{color}\", style=\"{style}\", label={_dot_quote(edge.relation)}];"
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def load_milestones() -> dict[str, Any]:
    value = json.loads(MILESTONES_PATH.read_text())
    if not isinstance(value, dict) or not isinstance(value.get("nodes"), list):
        raise ValueError("universe_milestones.json must contain a nodes list")
    return value


def public_graph(
    manifest: dict[str, Any], certificates: list[Certificate]
) -> tuple[str, dict[str, Any]]:
    by_path = {certificate.path: certificate for certificate in certificates}
    by_id: dict[str, list[Certificate]] = defaultdict(list)
    for certificate in certificates:
        if certificate.result_id:
            by_id[certificate.result_id].append(certificate)
    node_ids: set[str] = set()
    evidence_receipt: dict[str, list[dict[str, str]]] = {}
    missing: list[dict[str, str]] = []
    for node in manifest["nodes"]:
        node_id = node["id"]
        if node_id in node_ids:
            raise ValueError(f"duplicate milestone id: {node_id}")
        node_ids.add(node_id)
        evidence_receipt[node_id] = []
        for reference in node.get("evidence", []):
            certificate: Certificate | None = None
            if reference in by_path:
                certificate = by_path[reference]
            elif len(by_id.get(reference, [])) == 1:
                certificate = by_id[reference][0]
            if certificate is None:
                missing.append({"milestone": node_id, "reference": reference})
            else:
                evidence_receipt[node_id].append(
                    {
                        "reference": reference,
                        "certificate_path": certificate.path,
                        "certificate_status": certificate.status,
                    }
                )
    public_edges: list[tuple[str, str, str]] = []
    for edge in manifest.get("edges", []):
        source, target = edge["from"], edge["to"]
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"milestone edge has unknown endpoint: {source} -> {target}")
        public_edges.append((source, target, edge.get("label", "enables")))
    cycle_edges = [Edge(source, target, "ENABLES", label) for source, target, label in public_edges]
    public_cycles = _cycles(node_ids, cycle_edges)
    if public_cycles:
        raise ValueError(f"public milestone graph is cyclic: {public_cycles}")

    lines = [
        "digraph UniverseBuilding {",
        "  graph [rankdir=TB, bgcolor=\"white\", pad=0.35, nodesep=0.28, ranksep=0.58, splines=polyline, fontname=\"Helvetica\"];",
        "  node [style=\"rounded,filled\", fontname=\"Helvetica\", fontsize=11, penwidth=1.5, margin=\"0.13,0.08\"];",
        "  edge [fontname=\"Helvetica\", fontsize=8, color=\"#667085\", arrowsize=0.7];",
        "  label=\"How the candidate universe is being built\";",
        "  labelloc=t; fontsize=22;",
        "  legend [shape=plaintext, label=\"Arrows show what each result enables\\nGreen = certified | amber = partial | red = obstruction | gray = open\", fontsize=10];",
    ]
    for node in manifest["nodes"]:
        state = node["status"]
        if state not in COLORS:
            raise ValueError(f"unknown milestone status {state!r}")
        fill, border = COLORS[state]
        shape = "diamond" if node.get("kind") == "gate" else "box"
        label = _wrap(node["label"], 24)
        if node.get("detail"):
            label += "\n" + _wrap(node["detail"], 28)
        lines.append(
            f"  {_dot_quote(node['id'])} [shape={shape}, label={_dot_quote(label)}, "
            f"fillcolor=\"{fill}\", color=\"{border}\", tooltip={_dot_quote(node.get('tooltip', label))}];"
        )
    tiers: dict[str, list[str]] = defaultdict(list)
    for node in manifest["nodes"]:
        tiers[str(node.get("tier", "untiered"))].append(node["id"])
    for tier in tiers.values():
        if len(tier) > 1:
            lines.append("  { rank=same; " + "; ".join(_dot_quote(item) for item in tier) + "; }")
    for source, target, label in public_edges:
        lines.append(
            f"  {_dot_quote(source)} -> {_dot_quote(target)} [tooltip={_dot_quote(label)}];"
        )
    lines.append("}")
    receipt = {
        "missing_evidence": missing,
        "evidence": evidence_receipt,
        "cycles": public_cycles,
    }
    return "\n".join(lines) + "\n", receipt


def _canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build(treeish: str) -> dict[Path, str]:
    source_commit = _run_git(["rev-parse", treeish]).strip()
    files = load_git_tree(treeish)
    certificates, _ = collect_certificates(files)
    edges, issues = derive_edges(certificates, files)
    cycles = _cycles((certificate.key for certificate in certificates), edges)
    path_by_key = {certificate.key: certificate.path for certificate in certificates}
    issues["dependency_cycles"] = [
        [path_by_key.get(key, key) for key in component] for component in cycles
    ]
    manifest = load_milestones()
    public_dot_text, public_receipt = public_graph(manifest, certificates)
    issues["public_missing_evidence"] = public_receipt["missing_evidence"]

    graph = {
        "schema": "pure-weyl-certificate-dependency-dag-v1",
        "source_treeish": treeish,
        "source_commit": source_commit,
        "nodes": [
            {
                "key": certificate.key,
                "path": certificate.path,
                "result_id": certificate.result_id,
                "label": certificate.label,
                "family": certificate.family,
                "layout_group": _layout_topic(certificate),
                "status": certificate.status,
                "color_state": certificate.color_state,
                "dependency_tags": list(certificate.dependency_tags),
                "sha256": hashlib.sha256(files[certificate.path]).hexdigest(),
            }
            for certificate in sorted(certificates, key=lambda row: row.path)
        ],
        "edges": [edge.__dict__ for edge in edges],
        "nonordering_provenance_cross_links": issues[
            "nonordering_provenance_cross_links"
        ],
    }
    dot_text = full_dot(certificates, edges)
    issues_text = _canonical_json(issues)
    graph_text = _canonical_json(graph)
    input_digest = hashlib.sha256(
        b"".join(
            path.encode() + b"\0" + hashlib.sha256(files[path]).digest()
            for path in sorted(files)
            if path.endswith(".json") and not path.startswith("certificate_graph/")
        )
    ).hexdigest()
    receipt = {
        "schema": "pure-weyl-certificate-graph-receipt-v1",
        "source_treeish": treeish,
        "source_commit": source_commit,
        "input_json_bundle_sha256": input_digest,
        "milestone_manifest_sha256": hashlib.sha256(MILESTONES_PATH.read_bytes()).hexdigest(),
        "certificate_count": len(certificates),
        "modern_result_id_count": sum(certificate.result_id is not None for certificate in certificates),
        "legacy_path_id_count": sum(certificate.result_id is None for certificate in certificates),
        "dependency_edge_count": len(edges),
        "navigation_group_count": len(
            {(certificate.family, _layout_topic(certificate)) for certificate in certificates}
        ),
        "status_counts": {
            state: sum(certificate.color_state == state for certificate in certificates)
            for state in COLORS
        },
        "issue_counts": {
            "duplicate_result_ids": len(issues["duplicate_result_ids"]),
            "unresolved_declared_json_dependencies": len(
                issues["unresolved_declared_json_dependencies"]
            ),
            "hash_mismatches": len(issues["hash_mismatches"]),
            "dependency_cycles": len(issues["dependency_cycles"]),
            "public_missing_evidence": len(issues["public_missing_evidence"]),
            "nonordering_provenance_cross_links": len(
                issues["nonordering_provenance_cross_links"]
            ),
        },
        "artifacts": {
            "certificate-dag.json": hashlib.sha256(graph_text.encode()).hexdigest(),
            "certificate-dag.dot": hashlib.sha256(dot_text.encode()).hexdigest(),
            "universe-building-dag.dot": hashlib.sha256(public_dot_text.encode()).hexdigest(),
            "unresolved-dependencies.json": hashlib.sha256(issues_text.encode()).hexdigest(),
        },
        "public_evidence": public_receipt["evidence"],
        "claim_boundary": (
            "The full graph records syntactically declared certificate dependencies and imports. "
            "The public graph is a curated evidence-backed milestone view. Neither graph promotes "
            "a certificate beyond its own lifecycle and dependency tags."
        ),
    }
    return {
        OUTPUTS["graph"]: graph_text,
        OUTPUTS["dot"]: dot_text,
        OUTPUTS["public_dot"]: public_dot_text,
        OUTPUTS["issues"]: issues_text,
        OUTPUTS["receipt"]: _canonical_json(receipt),
    }


def _write_or_check(outputs: dict[Path, str], check: bool) -> None:
    drift: list[str] = []
    for path, text in outputs.items():
        if check:
            if not path.exists() or path.read_text() != text:
                drift.append(path.name)
        else:
            path.write_text(text)
    if drift:
        raise AssertionError("certificate graph artifacts drifted: " + ", ".join(drift))


def render() -> None:
    dot = shutil.which("dot")
    if not dot:
        raise RuntimeError("Graphviz 'dot' is required for --render")
    jobs = (
        (OUTPUTS["dot"], HERE / "certificate-dag.svg", "svg"),
        (OUTPUTS["public_dot"], HERE / "universe-building-dag.svg", "svg"),
        (OUTPUTS["public_dot"], HERE / "universe-building-dag.png", "png"),
        (OUTPUTS["public_dot"], HERE / "universe-building-dag.pdf", "pdf"),
    )
    for source, target, output_format in jobs:
        subprocess.run(
            [dot, f"-T{output_format}", str(source), "-o", str(target)], check=True
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-ish", default="HEAD")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument(
        "--strict-unresolved",
        action="store_true",
        help="also fail on unresolved declared JSON references",
    )
    parser.add_argument(
        "--strict-integrity",
        action="store_true",
        help="fail on hash drift, duplicate result IDs, or unresolved references",
    )
    args = parser.parse_args()
    outputs = build(args.tree_ish)
    _write_or_check(outputs, args.check)
    receipt = json.loads(outputs[OUTPUTS["receipt"]])
    issues = receipt["issue_counts"]
    fatal = issues["dependency_cycles"] + issues["public_missing_evidence"]
    if args.strict_unresolved:
        fatal += issues["unresolved_declared_json_dependencies"]
    if args.strict_integrity:
        fatal += (
            issues["hash_mismatches"]
            + issues["duplicate_result_ids"]
            + issues["unresolved_declared_json_dependencies"]
        )
    if fatal:
        print(json.dumps(issues, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    if args.render:
        render()
    print(
        "CERTIFICATE DAG: PASS "
        f"nodes={receipt['certificate_count']} edges={receipt['dependency_edge_count']} "
        f"unresolved={issues['unresolved_declared_json_dependencies']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
