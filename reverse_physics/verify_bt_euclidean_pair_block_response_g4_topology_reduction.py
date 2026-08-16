#!/usr/bin/env python3
"""Independent verifier for the BT pair-block g4 topology reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-topology-reduction-v1.schema.json",
)
ROW_DEGREES = ((4, ()), (3, (3,)), (2, (4,)), (2, (3, 3)), (1, (5,)), (1, (3, 4)), (1, (3, 3, 3)))


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def generate_pairings(slots):
    if not slots:
        yield ()
        return
    first, rest = slots[0], slots[1:]
    for index, partner in enumerate(rest):
        for tail in generate_pairings(rest[:index] + rest[index + 1 :]):
            yield ((first, partner),) + tail


def component_count(vertex_count, edges):
    parent = list(range(vertex_count))
    def root(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex
    for left, right in edges:
        if left != right:
            a, b = root(left), root(right)
            if a != b:
                parent[b] = a
    return len({root(vertex) for vertex in range(vertex_count)})


def bridge_by_cut(vertex_count, signature):
    expanded = [edge for edge, multiplicity in signature for _ in range(multiplicity)]
    for index, (left, right) in enumerate(expanded):
        if left == right:
            continue
        if component_count(vertex_count, expanded[:index] + expanded[index + 1 :]) > 1:
            return True
    return False


def independent_counts():
    totals = Counter()
    live_multiplicities = []
    per_row_live = []
    for response_order, actions in ROW_DEGREES:
        topologies = Counter()
        raw = connected = 0
        for response_degree in range(response_order % 2, response_order + 1, 2):
            degrees = (response_degree,) + actions
            slots = tuple((vertex, slot) for vertex, degree in enumerate(degrees) for slot in range(degree))
            for pairing in generate_pairings(slots):
                raw += 1
                edges = [tuple(sorted((left[0], right[0]))) for left, right in pairing]
                if component_count(len(degrees), edges) == 1:
                    connected += 1
                    topologies[(response_degree, tuple(sorted(Counter(edges).items())))] += 1
        live = []
        for key, multiplicity in sorted(topologies.items()):
            if not bridge_by_cut(1 + len(actions), key[1]):
                live.append((key[0], multiplicity))
                live_multiplicities.append(multiplicity)
        per_row_live.append(live)
        totals["raw"] += raw
        totals["connected"] += connected
        totals["topologies"] += len(topologies)
        totals["live"] += len(live)
    return totals, live_multiplicities, per_row_live


def verify(path=DEFAULT_CERT):
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    if list(Draft202012Validator(schema).iter_errors(cert)):
        return False
    if any(file_hash(row["path"]) != row["sha256"] for row in cert["provenance"]["inputs"]):
        return False
    totals, multiplicities, per_row_live = independent_counts()
    if totals != Counter(raw=1226, connected=1046, topologies=27, live=6):
        return False
    if multiplicities != [1, 1, 3, 6, 12, 36]:
        return False
    if [len(row) for row in per_row_live] != [3, 1, 1, 1, 0, 0, 0]:
        return False
    if per_row_live[1] != [(3, 6)] or per_row_live[2] != [(2, 12)] or per_row_live[3] != [(2, 36)]:
        return False
    enumeration = cert["enumeration"]
    if (enumeration["raw_pairings"], enumeration["connected_pairings"], enumeration["connected_topologies"], enumeration["momentum_admissible_topologies"]) != (1226, 1046, 27, 6):
        return False
    live = cert["six_term_fourier_reduction"]["live_topologies"]
    if [row["pairing_multiplicity"] for row in live] != multiplicities:
        return False
    if cert["method_disposition"]["full_gibbs_L6_g4_coefficient"] != "OPEN":
        return False
    if "LORENTZIAN-CAUSAL" in cert["dependency_tags"]:
        return False
    print("[PASS] independent BT pair-block g4 topology verifier (15/15)")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
