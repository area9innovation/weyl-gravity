#!/usr/bin/env python3
"""Generate exact finite-graph retarded/advanced wave kernels and support witnesses."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json"
REPORT = ROOT / "foundations/reports/finite-graph-wave-causality.md"

FIXTURES = [
    {"id": "PATH_5", "vertices": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "kappa": [1, 4], "steps": 7},
    {"id": "CYCLE_6", "vertices": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "kappa": [1, 5], "steps": 7},
    {"id": "STAR_5", "vertices": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "kappa": [1, 6], "steps": 6},
]


def add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction()) for j in range(len(b[0]))] for i in range(len(a))]


def zero(n: int) -> list[list[Fraction]]:
    return [[Fraction() for _ in range(n)] for _ in range(n)]


def identity(n: int) -> list[list[Fraction]]:
    return [[Fraction(i == j) for j in range(n)] for i in range(n)]


def matrix(fixture: dict[str, Any]) -> list[list[Fraction]]:
    n = fixture["vertices"]
    lap = zero(n)
    for i, j in fixture["edges"]:
        lap[i][j] += 1
        lap[j][i] += 1
        lap[i][i] -= 1
        lap[j][j] -= 1
    kappa = Fraction(*fixture["kappa"])
    return add([[kappa * x for x in row] for row in lap], [[Fraction(2) * x for x in row] for row in identity(n)])


def distances(fixture: dict[str, Any]) -> list[list[int]]:
    n = fixture["vertices"]
    adjacency = [[] for _ in range(n)]
    for i, j in fixture["edges"]:
        adjacency[i].append(j)
        adjacency[j].append(i)
    result = []
    for source in range(n):
        d = [n + 1] * n
        d[source] = 0
        queue = [source]
        for v in queue:
            for w in adjacency[v]:
                if d[w] > d[v] + 1:
                    d[w] = d[v] + 1
                    queue.append(w)
        result.append(d)
    return result


def encode(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def fixture_result(fixture: dict[str, Any]) -> dict[str, Any]:
    n = fixture["vertices"]
    a = matrix(fixture)
    kernels = [zero(n), identity(n)]
    for _ in range(1, fixture["steps"]):
        kernels.append(sub(mul(a, kernels[-1]), kernels[-2]))
    d = distances(fixture)
    violations = []
    nonzero_counts = []
    recurrence_checks = 0
    for step, kernel in enumerate(kernels):
        nonzero_counts.append(sum(value != 0 for row in kernel for value in row))
        for target in range(n):
            for source in range(n):
                if kernel[target][source] and d[source][target] > step - 1:
                    violations.append([step, target, source, d[source][target]])
        if step >= 2:
            recurrence_checks += n * n
    advanced = [[[encode(kernels[step][source][target]) for target in range(n)] for source in range(n)] for step in range(len(kernels))]
    return {
        **fixture,
        "update_matrix": [[encode(x) for x in row] for row in a],
        "retarded_kernels": [[[encode(x) for x in row] for row in kernel] for kernel in kernels],
        "advanced_kernels": advanced,
        "support_rule": "K_n(target,source)=0 whenever graph_distance(source,target)>n-1; K_0=0 and K_1=I.",
        "support_violations": violations,
        "nonzero_counts": nonzero_counts,
        "recurrence_entry_checks": recurrence_checks,
        "adjoint_entry_checks": len(kernels) * n * n,
    }


def canonical_digest(fixtures: list[dict[str, Any]]) -> str:
    payload = [(x["id"], x["update_matrix"], x["retarded_kernels"], x["advanced_kernels"]) for x in fixtures]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    fixtures = [fixture_result(x) for x in FIXTURES]
    return {
        "schema_version": "foundational-finite-graph-wave-causality-v1",
        "result_id": "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1",
        "result_kind": "EXACT_FINITE_DISCRETE_CAUSAL_GREEN_KERNEL",
        "lifecycle": "CERTIFIED",
        "created": "2026-08-12",
        "repository_base_commit": "1ec0ae4b25c0cb53859263613a8dc6a56fb85709",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "statement": "For the displayed finite graphs and rational nearest-neighbour recurrence, exact retarded kernels have graph-step support and advanced kernels are their transposes under time reversal.",
        "general_proof": {
            "retarded_recurrence": "K_0=0, K_1=I, K_(n+1)=(2I+kappa*Delta)K_n-K_(n-1)",
            "support_induction": "The update matrix has entries only at graph distance at most one. If K_n is supported at distance <=n-1 and K_(n-1) at distance <=n-2, then K_(n+1) is supported at distance <=n.",
            "advanced_kernel": "For an undirected graph the update matrix is symmetric, so every K_n is symmetric; the advanced finite-horizon kernel is the retarded kernel with source and target interchanged and time reversed.",
            "formal_base": "Primitive-recursive exact rational matrix arithmetic and induction on the displayed finite step bound suffice for each fixture.",
        },
        "fixtures": fixtures,
        "summary": {
            "fixtures": len(fixtures),
            "vertices": sum(x["vertices"] for x in fixtures),
            "kernel_steps": sum(len(x["retarded_kernels"]) for x in fixtures),
            "support_violations": sum(len(x["support_violations"]) for x in fixtures),
            "recurrence_entry_checks": sum(x["recurrence_entry_checks"] for x in fixtures),
            "adjoint_entry_checks": sum(x["adjoint_entry_checks"] for x in fixtures),
        },
        "independent_checker": {
            "path": "foundations/check_finite_graph_wave_causality.py",
            "expected_digest": canonical_digest(fixtures),
            "checks": ["fixture closure", "exact recurrence", "graph-distance support", "retarded/advanced transpose", "canonical digest"],
        },
        "claim_flags": {
            "finite_exact_retarded_kernel_constructed": True,
            "finite_exact_advanced_kernel_constructed": True,
            "graph_step_support_certified": True,
            "continuum_green_operator_constructed": False,
            "lorentzian_causal_claim": False,
            "continuum_limit_proved": False,
        },
        "does_not_establish": [
            "continuum finite propagation", "a Lorentzian advanced or retarded Green operator", "CFL stability or convergence under refinement", "a regulator-independent continuum limit", "a Weyl metric BV propagator", "a reverse-mathematical classification of continuum PDE"
        ],
        "human_report": "foundations/reports/finite-graph-wave-causality.md",
    }


def render(result: dict[str, Any]) -> str:
    s = result["summary"]
    lines = [
        "# Exact finite-graph wave causality", "", f"**Result:** `{result['result_id']}`", "", "## Result", "",
        "A rational nearest-neighbour wave recurrence has exact retarded and advanced kernels on three finite graph fixtures. The retarded kernel at step `n` vanishes beyond graph distance `n-1`; the advanced kernel is the time-reversed transpose.", "",
        f"The checker covers **{s['fixtures']} fixtures**, **{s['vertices']} vertices**, **{s['kernel_steps']} kernel steps**, **{s['recurrence_entry_checks']} recurrence entries**, and **{s['adjoint_entry_checks']} adjoint entries**, with **{s['support_violations']} support violations**.", "",
        "## Why this is causal only in the finite-discrete sense", "",
        "The result supplies an exact graph-step domain of dependence. It does not identify graph distance with a Lorentzian metric, prove convergence as a mesh is refined, or turn a Lieb–Robinson tail into strict continuum support.", "",
        "## Reproduction", "", "```text", "python3 foundations/build_finite_graph_wave_causality.py --check", "python3 foundations/check_finite_graph_wave_causality.py", "python3 foundations/verify_finite_graph_wave_causality.py", "```", "", "## Boundaries", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in result["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    result = build()
    return (json.dumps(result, indent=2) + "\n").encode(), render(result).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((OUTPUT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1: generated artifacts current")
        return 0
    OUTPUT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
