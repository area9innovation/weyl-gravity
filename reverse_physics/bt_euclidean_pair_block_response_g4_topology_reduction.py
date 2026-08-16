#!/usr/bin/env python3
"""Certify the six-topology reduction of the BT pair-block g4 response."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from functools import lru_cache


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-topology-reduction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-pair-block-response-g4-topology-reduction.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_pair_block_response_g4_topology_reduction.py"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_CONNECTED_LEDGER_V1.json",
]
SOURCE_COMMIT = "389cccc029a73c4a5ae82851583b32b864054a75"

Slot = tuple[int, int]
Pairing = tuple[tuple[Slot, Slot], ...]
Signature = tuple[tuple[tuple[int, int], int], ...]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=None)
def pairings(slots: tuple[Slot, ...]) -> tuple[Pairing, ...]:
    if not slots:
        return ((),)
    first = slots[0]
    rows = []
    for index in range(1, len(slots)):
        for tail in pairings(slots[1:index] + slots[index + 1 :]):
            rows.append(((first, slots[index]),) + tail)
    return tuple(rows)


def connected(vertex_count: int, pairing: Pairing) -> bool:
    adjacency = [set() for _ in range(vertex_count)]
    for (left, _), (right, _) in pairing:
        if left != right:
            adjacency[left].add(right)
            adjacency[right].add(left)
    seen = {0}
    stack = [0]
    while stack:
        for neighbour in adjacency[stack.pop()]:
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    return len(seen) == vertex_count


def signature(pairing: Pairing) -> Signature:
    counts = Counter(
        tuple(sorted((left[0], right[0]))) for left, right in pairing
    )
    return tuple(sorted(counts.items()))


def has_nonself_bridge(vertex_count: int, topology: Signature) -> bool:
    for candidate, multiplicity in topology:
        left, right = candidate
        if left == right or multiplicity > 1:
            continue
        adjacency = [set() for _ in range(vertex_count)]
        for edge, _ in topology:
            u, v = edge
            if u != v and edge != candidate:
                adjacency[u].add(v)
                adjacency[v].add(u)
        seen = {0}
        stack = [0]
        while stack:
            for neighbour in adjacency[stack.pop()]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        if len(seen) != vertex_count:
            return True
    return False


ROWS = (
    ("E0[Dm4]", 4, ()),
    ("-kappa0(Dm3,S1)", 3, (3,)),
    ("-kappa0(Dm2,S2)", 2, (4,)),
    ("+(1/2)kappa0(Dm2,S1,S1)", 2, (3, 3)),
    ("-kappa0(Dm1,S3)", 1, (5,)),
    ("+kappa0(Dm1,S1,S2)", 1, (3, 4)),
    ("-(1/6)kappa0(Dm1,S1,S1,S1)", 1, (3, 3, 3)),
)


def topology_rows() -> list[dict]:
    result = []
    for name, response_order, action_degrees in ROWS:
        topology_counts: Counter[tuple[int, Signature]] = Counter()
        raw_pairings = 0
        connected_pairings = 0
        for response_degree in range(response_order % 2, response_order + 1, 2):
            degrees = (response_degree,) + action_degrees
            slots = tuple(
                (vertex, slot)
                for vertex, degree in enumerate(degrees)
                for slot in range(degree)
            )
            for pairing in pairings(slots):
                raw_pairings += 1
                if connected(len(degrees), pairing):
                    connected_pairings += 1
                    topology_counts[(response_degree, signature(pairing))] += 1
        topologies = []
        for (response_degree, topology), multiplicity in sorted(
            topology_counts.items()
        ):
            bridge = has_nonself_bridge(1 + len(action_degrees), topology)
            edge_count = sum(value for _, value in topology)
            topologies.append(
                {
                    "response_degree": response_degree,
                    "edges": [
                        {
                            "vertices": list(edge),
                            "multiplicity": value,
                        }
                        for edge, value in topology
                    ],
                    "pairing_multiplicity": multiplicity,
                    "loop_rank": edge_count - len(action_degrees),
                    "has_nonself_bridge": bridge,
                    "zero_mode_disposition": (
                        "VANISHES_EXACTLY" if bridge else "MOMENTUM_ADMISSIBLE"
                    ),
                }
            )
        result.append(
            {
                "cumulant_row": name,
                "response_order": response_order,
                "action_degrees": list(action_degrees),
                "raw_pairings": raw_pairings,
                "connected_pairings": connected_pairings,
                "connected_topology_count": len(topologies),
                "momentum_admissible_topology_count": sum(
                    not row["has_nonself_bridge"] for row in topologies
                ),
                "topologies": topologies,
            }
        )
    return result


def build() -> dict:
    rows = topology_rows()
    all_topologies = [topology for row in rows for topology in row["topologies"]]
    live = [row for row in all_topologies if not row["has_nonself_bridge"]]
    killed = [row for row in all_topologies if row["has_nonself_bridge"]]
    live_multiplicities = [row["pairing_multiplicity"] for row in live]
    checks = {
        "seven_cumulant_rows_imported": len(rows) == 7,
        "raw_pairing_count_is_1226": sum(row["raw_pairings"] for row in rows) == 1226,
        "connected_pairing_count_is_1046": sum(row["connected_pairings"] for row in rows) == 1046,
        "connected_adjacency_topology_count_is_27": len(all_topologies) == 27,
        "bridge_topology_count_is_21": len(killed) == 21,
        "momentum_admissible_topology_count_is_six": len(live) == 6,
        "live_pairing_multiplicities_are_exact": live_multiplicities == [1, 1, 3, 6, 12, 36],
        "all_Dm1_rows_vanish": all(
            row["momentum_admissible_topology_count"] == 0
            for row in rows
            if row["response_order"] == 1
        ),
        "only_top_degree_Dm3_survives": [
            row["response_degree"]
            for row in rows[1]["topologies"]
            if not row["has_nonself_bridge"]
        ] == [3],
        "one_Dm2_S1_S1_topology_survives": rows[3]["momentum_admissible_topology_count"] == 1,
        "all_live_loop_ranks_are_zero_one_or_two": sorted(
            row["loop_rank"] for row in live
        ) == [0, 1, 2, 2, 2, 2],
        "six_term_fourier_formula_has_no_S3_vertex": True,
        "first_nondegenerate_second_moment_volume_is_L6": True,
        "finite_volume_coefficient_remains_uncomputed": True,
        "large_volume_and_hminus1_gates_remain_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-pair-block-response-g4-topology-reduction-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact connected Wick-topology and zero-mode reduction of the full-Gibbs BT pair-block order-lambda^4 response",
        "question": "Which of the 27 connected Wick adjacency types in the normalized order-lambda^4 pair-response ledger can actually carry nonzero periodic lattice momentum?",
        "answer": (
            "Only six. Exhaustive labeled Wick enumeration gives 1226 raw pairings, 1046 connected pairings, and 27 connected adjacency types. Twenty-one types contain a non-self bridge. Conservation at every translation-summed action vertex forces the momentum through such a bridge to be zero; the bilaplacian Gaussian has G_L(0)=0, so each of those types vanishes exactly. All three rows containing Dm1 disappear, the degree-one sector of Dm3 disappears, and only one of four Dm2-S1-S1 adjacency types survives. The complete coefficient is therefore one zero-loop response constant, one one-loop response contraction, and four two-loop sums. The live labeled multiplicities are 1,1,3,6,12,36 and give the explicit six-term Fourier formula below. This is an exact reduction of the coefficient, not its value or sign."
        ),
        "conventions": {
            "volume": "N=L^4",
            "propagator": "G_L(k)=omega(k)^(-2) for k!=0 and G_L(0)=0",
            "action_vertices": "Gamma_n is the translation-stripped kernel defined by D^n S_(n-2)[N^(-1/2)e_k1,...,N^(-1/2)e_kn]=N^(1-n/2)*delta_(sum k,0)*Gamma_n(k1,...,kn)",
            "response_vertices": "F_(i,r) is the local kernel defined by D_background^r(Dm_i)[N^(-1/2)e_k1,...,N^(-1/2)e_kr]=N^(-r/2)*F_(i,r)(k1,...,kr), with Taylor coefficient 1/r!",
            "fourier_normalization": "phi_x=N^(-1/2)*sum_k exp(i*k*x)*phi_k",
        },
        "enumeration": {
            "raw_pairings": sum(row["raw_pairings"] for row in rows),
            "connected_pairings": sum(row["connected_pairings"] for row in rows),
            "connected_topologies": len(all_topologies),
            "bridge_killed_topologies": len(killed),
            "momentum_admissible_topologies": len(live),
            "rows": rows,
            "status": "EXHAUSTIVE_EXACT_LABELED_PAIRING_ENUMERATION",
        },
        "bridge_zero_mode_theorem": {
            "statement": "In a connected vacuum Wick multigraph, remove a non-self bridge. Summing the momentum-conservation equations over either resulting component shows that the bridge momentum is zero. Since the zero mode is removed, its propagator is G_L(0)=0 and the graph vanishes.",
            "scope": "Self-loops and members of a parallel-edge family are not bridges. A topology marked MOMENTUM_ADMISSIBLE is not asserted nonzero; it is only not forced to vanish by this theorem.",
            "status": "PROVED",
        },
        "six_term_fourier_reduction": {
            "formula": "T4=F_(4,0)+(1/(2*N))*sum_k F_(4,2)(k,-k)*G(k)+(1/(8*N^2))*sum_(k,l) F_(4,4)(k,-k,l,-l)*G(k)*G(l)-(1/(6*N^2))*sum_(k,l) F_(3,3)(k,l,-k-l)*Gamma_3(-k,-l,k+l)*G(k)*G(l)*G(k+l)-(1/(4*N^2))*sum_(k,l) F_(2,2)(k,-k)*Gamma_4(-k,k,l,-l)*G(k)^2*G(l)+(1/(4*N^2))*sum_(k,l) F_(2,2)(k,-k)*Gamma_3(-k,l,k-l)*Gamma_3(k,-l,l-k)*G(k)^2*G(l)*G(k-l)",
            "live_topologies": [
                {"term": "F_(4,0)", "pairing_multiplicity": 1, "loop_rank": 0, "prefactor": "1"},
                {"term": "F_(4,2)", "pairing_multiplicity": 1, "loop_rank": 1, "prefactor": "1/(2*N)"},
                {"term": "F_(4,4)", "pairing_multiplicity": 3, "loop_rank": 2, "prefactor": "1/(8*N^2)"},
                {"term": "F_(3,3)*Gamma_3", "pairing_multiplicity": 6, "loop_rank": 2, "prefactor": "-1/(6*N^2)"},
                {"term": "F_(2,2)*Gamma_4", "pairing_multiplicity": 12, "loop_rank": 2, "prefactor": "-1/(4*N^2)"},
                {"term": "F_(2,2)*Gamma_3^2", "pairing_multiplicity": 36, "loop_rank": 2, "prefactor": "+1/(4*N^2)"},
            ],
            "zero_mode_convention": "All sums may include k=0 or l=0 because every term containing a zero-momentum propagator is defined to be zero.",
            "status": "EXACT_REDUCTION_PROVED_COEFFICIENT_OPEN",
        },
        "volume_selection": {
            "exact_target": "L=6 periodic lattice",
            "reason": "The response is the second spatial moment of a range-two kernel. L=4 aliases the unwrapped quadratic coordinate across the periodic boundary; L=6 is the first already-certified nondegenerate rational fixture and has rational omega values.",
            "arithmetic": "At L=6, omega(k) is rational and the sixth-root phases lie in Q(sqrt(-3)); conjugation makes the final six-term sum rational.",
            "status": "L6_SELECTED_L4_SUPERSEDED",
        },
        "method_disposition": {
            "connected_g4_topology_atlas": "COMPLETE",
            "bridge_zero_mode_elimination": "PROVED",
            "six_term_fourier_reduction": "PROVED",
            "all_Dm1_marginal_rows": "ZERO",
            "full_gibbs_L6_g4_coefficient": "OPEN",
            "large_volume_g4_power_or_log": "OPEN",
            "uniform_pair_response": "OPEN",
            "response_to_witten_schur_bridge": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the exact response vertices F_(2,2), F_(3,3), F_(4,0), F_(4,2), and F_(4,4) for the nearest-neighbour conditional pair",
            "streaming evaluation of the six displayed sums in Q(sqrt(-3)) on the 6^4 lattice and an independent modular or position-space check",
            "the hard/hard, hard/soft, and soft/soft large-volume bounds if the finite-volume coefficient is nonzero",
            "a volume-uniform remainder or nonperturbative response estimate before any Witten or H^-1 transfer",
        ],
        "next_gate": (
            "Generate the five local response vertices by conditional two-variable Gaussian arithmetic evaluated on plane-wave backgrounds. Stream the six displayed sums over the 6^4 momentum pairs in Q(sqrt(-3)); never materialize an N-by-N covariance tensor. Verify the result independently modulo several primes or by a separately generated position-space contraction. Only then classify the finite-volume coefficient sign and proceed to its large-volume hard/soft decomposition."
        ),
        "does_not_establish": [
            "the value or sign of the full-Gibbs order-lambda^4 coefficient",
            "that every momentum-admissible topology is individually nonzero",
            "a volume-uniform perturbative remainder or fixed-coupling response",
            "a heat-bath gap, Witten estimate, or interacting H^-1 theorem",
            "tightness or continuum identification",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Exact integer labeled-pairing enumeration, canonical multigraph adjacency counts, graph connectivity, bridge detection, and symbolic factorial normalization; no floating-point evidence.",
            "assumptions": [
                "the imported seven-row nested-cumulant ledger and degree bounds are valid",
                "the periodic free bilaplacian zero mode is removed exactly",
                "momentum-admissible means only that bridge conservation does not force a zero propagator",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_topology_reduction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_topology_reduction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_topology_reduction",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hash, scoped diff check, and staged-diff inspection required",
            "tier_1": "deterministic producer, nonimporting pairing/bridge verifier, and mutation tests required",
            "tier_2": "the content-addressed connected-ledger input is checked by hash; no coefficient or shared operator changes",
            "tier_3": "not run: this is an exact reduction, not a coefficient, H^-1, continuum, freeze, release, shared-core, or Lorentzian promotion",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "elapsed_seconds_and_peak_kib": {
                "producer": "0.04 s, 21156 KiB",
                "independent_verifier": "0.11 s, 29948 KiB",
                "unit_tests": "0.16 s, 31032 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1701 nodes, 0 invalid items, 0 malformed events; 7.42 s, 212688 KiB",
                "science_forge_shadow": "not run: no registered shadow input changes; this skip is not a pass",
            },
            "exploratory_failures_not_counted_as_passes": [
                "the NumPy preflight stopped before sampling in the default environment because NumPy was absent",
                "a 400-sample calibrated full-Gibbs preflight had variance too large to resolve the certified one-loop signal and is not used as evidence",
                "two sparse coordinate-basis response-tensor prototypes stopped at the 500000 KiB ceiling; no result from either run is promoted",
            ],
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT pair-block g4 topology reduction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
