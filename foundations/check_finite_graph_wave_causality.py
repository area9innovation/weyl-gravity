#!/usr/bin/env python3
"""Independent exact checker for finite-graph wave kernels."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def decode(value: list[int]) -> Fraction:
    return Fraction(value[0], value[1])


def mul(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction()) for j in range(len(b))] for i in range(len(a))]


def sub(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def digest(fixtures: list[dict[str, Any]]) -> str:
    payload = [(x["id"], x["update_matrix"], x["retarded_kernels"], x["advanced_kernels"]) for x in fixtures]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if result is None else result
    errors: list[str] = []
    fixtures = result.get("fixtures", [])
    if [x.get("id") for x in fixtures] != ["PATH_5", "CYCLE_6", "STAR_5"]:
        errors.append("fixture closure")
    total_recurrence = total_adjoint = violations = 0
    for fixture in fixtures:
        n = fixture["vertices"]
        a = [[decode(x) for x in row] for row in fixture["update_matrix"]]
        kernels = [[[decode(x) for x in row] for row in kernel] for kernel in fixture["retarded_kernels"]]
        advanced = [[[decode(x) for x in row] for row in kernel] for kernel in fixture["advanced_kernels"]]
        adjacency = [[] for _ in range(n)]
        for i, j in fixture["edges"]:
            adjacency[i].append(j); adjacency[j].append(i)
        distances = []
        for source in range(n):
            d = [n + 1] * n; d[source] = 0; queue = [source]
            for v in queue:
                for w in adjacency[v]:
                    if d[w] > d[v] + 1:
                        d[w] = d[v] + 1; queue.append(w)
            distances.append(d)
        for step in range(2, len(kernels)):
            if kernels[step] != sub(mul(a, kernels[step - 1]), kernels[step - 2]):
                errors.append("recurrence " + fixture["id"] + ":" + str(step))
            total_recurrence += n * n
        for step, kernel in enumerate(kernels):
            for target in range(n):
                for source in range(n):
                    if kernel[target][source] and distances[source][target] > step - 1:
                        violations += 1
                    if advanced[step][source][target] != kernel[target][source]:
                        errors.append("advanced transpose " + fixture["id"] + ":" + str(step))
            total_adjoint += n * n
    summary = result.get("summary", {})
    if violations or summary.get("support_violations") != 0:
        errors.append("support violations")
    if summary.get("recurrence_entry_checks") != total_recurrence or summary.get("adjoint_entry_checks") != total_adjoint:
        errors.append("check counts")
    calculated = digest(fixtures)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": calculated, "fixtures": len(fixtures), "recurrence_checks": total_recurrence, "adjoint_checks": total_adjoint, "support_violations": violations}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
