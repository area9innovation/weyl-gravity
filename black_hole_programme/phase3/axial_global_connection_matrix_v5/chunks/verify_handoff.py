#!/usr/bin/env python3
"""Fail-closed verifier for parameter-correlated radial reset handoffs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "phase3-axial-global-affine-reset-handoff-v2"
SHA_KEYS = frozenset("0123456789abcdef")
CELL = {
    "parameter": "Momega",
    "generator": 7315,
    "lower": "1/2",
    "upper": "129/256",
    "center": "257/512",
    "radius": "1/512",
}
STANDARD_ORDER = (
    "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(F)",
    "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(F)",
)
SHEARED_ORDER = (
    "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(rhoF)",
    "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(rhoF)",
)
INFINITY_CHUNKS = {
    f"infinity-{k}": (Fraction(k), Fraction(k + 1))
    for k in range(28)
}
HORIZON_EXPONENT_GROUPS = ((-22, -16), (-16, -10), (-10, -4), (-4, 1))
HORIZON_CHUNKS = {
    f"horizon-{k}": (Fraction(2) ** a, Fraction(2) ** b)
    for k, (a, b) in enumerate(HORIZON_EXPONENT_GROUPS)
}
TOP_KEYS = {
    "schema", "artifact_kind", "chunk_id", "status", "cell", "domain",
    "state", "solver", "frames", "matrix", "integrity", "proof",
}


class HandoffError(ValueError):
    """A typed fail-closed handoff refusal."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HandoffError(message)


def _exact_keys(value: Any, keys: set[str], where: str) -> None:
    _require(isinstance(value, dict), f"{where}: expected object")
    got = set(value)
    _require(got == keys, f"{where}: keys differ: missing={keys-got}, extra={got-keys}")


def _sha(value: Any, where: str) -> str:
    _require(
        isinstance(value, str)
        and len(value) == 64
        and all(c in SHA_KEYS for c in value),
        f"{where}: expected lowercase SHA-256",
    )
    return value


def _rational(value: Any, where: str) -> Fraction:
    _require(isinstance(value, str) and "/" in value, f"{where}: bad rational")
    try:
        numerator, denominator = value.split("/", 1)
        q = Fraction(int(numerator), int(denominator))
    except (ValueError, ZeroDivisionError) as exc:
        raise HandoffError(f"{where}: bad rational") from exc
    _require(str(q.numerator) == numerator, f"{where}: noncanonical numerator")
    _require(str(q.denominator) == denominator, f"{where}: noncanonical denominator")
    return q


def _bits(value: Any, where: str) -> int:
    _require(
        isinstance(value, str)
        and len(value) == 16
        and all(c in SHA_KEYS for c in value),
        f"{where}: expected 16 lowercase hexadecimal digits",
    )
    return int(value, 16)


def _f64_from_bits(value: Any, where: str) -> float:
    n = _bits(value, where)
    x = struct.unpack(">d", struct.pack(">Q", n))[0]
    _require(math.isfinite(x), f"{where}: nonfinite endpoint")
    return x


def _matrix(value: Any, leaf, where: str) -> list[list[Any]]:
    _require(isinstance(value, list) and len(value) == 12, f"{where}: expected 12 rows")
    out = []
    for i, row in enumerate(value):
        _require(isinstance(row, list) and len(row) == 12, f"{where}[{i}]: expected 12 columns")
        out.append([leaf(x, f"{where}[{i}][{j}]") for j, x in enumerate(row)])
    return out


def _interval_matrix(value: Any, where: str) -> list[list[tuple[float, float]]]:
    def interval(x: Any, at: str) -> tuple[float, float]:
        _require(isinstance(x, list) and len(x) == 2, f"{at}: expected [lo_bits,hi_bits]")
        lo = _f64_from_bits(x[0], f"{at}.lo")
        hi = _f64_from_bits(x[1], f"{at}.hi")
        _require(lo <= hi, f"{at}: reversed interval")
        return lo, hi

    return _matrix(value, interval, where)


def _fraction_bounds(q: Fraction) -> tuple[float, float]:
    f = float(q)
    _require(math.isfinite(f), "rational does not fit finite f64")
    fq = Fraction.from_float(f)
    lo = f if fq <= q else math.nextafter(f, -math.inf)
    hi = f if fq >= q else math.nextafter(f, math.inf)
    return lo, hi


def _add_outward(a: float, b: float, direction: float) -> float:
    if a == 0.0:
        return b
    if b == 0.0:
        return a
    return math.nextafter(a + b, direction)


def _verify_affine_hull(data: dict[str, Any]) -> None:
    center = _matrix(data["center"], _rational, "matrix.center")
    linear = _matrix(data["linear"], _rational, "matrix.linear")
    remainder = _interval_matrix(data["remainder"], "matrix.remainder")
    hull = _interval_matrix(data["hull"], "matrix.hull")
    for i in range(12):
        for j in range(12):
            loq = center[i][j] - abs(linear[i][j])
            hiq = center[i][j] + abs(linear[i][j])
            qlo, _ = _fraction_bounds(loq)
            _, qhi = _fraction_bounds(hiq)
            rlo, rhi = remainder[i][j]
            need_lo = _add_outward(qlo, rlo, -math.inf)
            need_hi = _add_outward(qhi, rhi, math.inf)
            hlo, hhi = hull[i][j]
            _require(
                hlo <= need_lo and hhi >= need_hi,
                f"matrix.hull[{i}][{j}]: does not contain affine hull",
            )


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _safe_path(root: Path, relative: Any, where: str) -> Path:
    _require(isinstance(relative, str) and relative, f"{where}: empty path")
    p = Path(relative)
    _require(not p.is_absolute() and ".." not in p.parts, f"{where}: unsafe path")
    resolved_root = root.resolve()
    resolved = (resolved_root / p).resolve()
    _require(
        resolved == resolved_root or resolved_root in resolved.parents,
        f"{where}: path escapes root",
    )
    return resolved


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _verify_path_hash(value: Any, root: Path | None, where: str) -> dict[str, str]:
    _exact_keys(value, {"path", "sha256"}, where)
    digest = _sha(value["sha256"], f"{where}.sha256")
    _require(isinstance(value["path"], str) and value["path"], f"{where}.path")
    _require(not Path(value["path"]).is_absolute() and ".." not in Path(value["path"]).parts,
             f"{where}.path: unsafe")
    if root is not None:
        path = _safe_path(root, value["path"], f"{where}.path")
        _require(path.is_file(), f"{where}.path: missing file")
        _require(_file_sha256(path) == digest, f"{where}: file hash mismatch")
    return {"path": value["path"], "sha256": digest}


def _verify_domain_and_solver(data: dict[str, Any]) -> None:
    kind = data["artifact_kind"]
    chunk_id = data["chunk_id"]
    domain = data["domain"]
    solver = data["solver"]
    _exact_keys(domain, {"coordinate", "orientation", "start", "end"}, "domain")
    _exact_keys(
        solver,
        {
            "panels", "resets", "local_steps", "order", "rank_cells",
            "global_panel_start", "global_panel_end",
        },
        "solver",
    )
    start = _rational(domain["start"], "domain.start")
    end = _rational(domain["end"], "domain.end")
    _require(end > start, "domain: nonpositive orientation")
    _require(solver["order"] == 12 and solver["rank_cells"] == 8, "solver: wrong gates")
    _require(
        all(isinstance(solver[x], int) and not isinstance(solver[x], bool)
            for x in ("panels", "resets", "local_steps",
                      "global_panel_start", "global_panel_end")),
        "solver: integer fields required",
    )
    _require(solver["panels"] == solver["resets"] * solver["local_steps"],
             "solver: panels != resets*local_steps")
    _require(
        solver["global_panel_end"] - solver["global_panel_start"] == solver["panels"],
        "solver: global panel range mismatch",
    )

    if kind == "infinity-standard-fundamental":
        _require(chunk_id in INFINITY_CHUNKS, "infinity: bad chunk id")
        _require((start, end) == INFINITY_CHUNKS[chunk_id], "infinity: bad exact bounds")
        _require(
            domain["coordinate"] == "t=32-r"
            and domain["orientation"] == "increasing-t/inward-r",
            "infinity: wrong coordinate/orientation",
        )
        k = int(chunk_id.split("-")[1])
        _require(
            solver == {
                "panels": 64,
                "resets": 1,
                "local_steps": 64,
                "order": 12,
                "rank_cells": 8,
                "global_panel_start": 64 * k,
                "global_panel_end": 64 * (k + 1),
            },
            "infinity: solver/global-panel contract differs",
        )
    elif kind == "horizon-sheared-fundamental":
        _require(chunk_id in HORIZON_CHUNKS, "horizon: bad chunk id")
        _require((start, end) == HORIZON_CHUNKS[chunk_id], "horizon: bad exact bounds")
        _require(
            domain["coordinate"] == "rho=r-2"
            and domain["orientation"] == "increasing-rho/outward-r",
            "horizon: wrong coordinate/orientation",
        )
        k = int(chunk_id.split("-")[1])
        expected_panels = 96 if k < 3 else 80
        expected_resets = 48 if k < 3 else 40
        panel_start = 96 * k
        _require(
            solver == {
                "panels": expected_panels,
                "resets": expected_resets,
                "local_steps": 2,
                "order": 12,
                "rank_cells": 8,
                "global_panel_start": panel_start,
                "global_panel_end": panel_start + expected_panels,
            },
            "horizon: solver/global-panel contract differs",
        )
    else:
        raise HandoffError("unknown artifact kind")


def verify_handoff(data: Any, repo_root: Path | None = None) -> bool:
    _exact_keys(data, TOP_KEYS, "root")
    _require(data["schema"] == SCHEMA, "root: wrong schema")
    _require(data["status"] == "CERTIFIED", "root: noncertified handoff")
    _exact_keys(data["cell"], set(CELL), "cell")
    _require(data["cell"] == CELL, "cell: wrong shared parameter cell/generator")
    _verify_domain_and_solver(data)

    _exact_keys(data["state"], {"rows", "cols", "chart", "order"}, "state")
    _require(data["state"]["rows"] == data["state"]["cols"] == 12, "state: wrong shape")
    if data["artifact_kind"] == "infinity-standard-fundamental":
        _require(
            data["state"]["chart"] == "standard-real-12"
            and tuple(data["state"]["order"]) == STANDARD_ORDER,
            "state: wrong infinity chart/order",
        )
    else:
        _require(
            data["state"]["chart"] == "horizon-sheared-real-12"
            and tuple(data["state"]["order"]) == SHEARED_ORDER,
            "state: wrong horizon chart/order",
        )

    _exact_keys(
        data["frames"],
        {"table_sha256", "left_boundary_sha256", "right_boundary_sha256", "generation"},
        "frames",
    )
    for key in ("table_sha256", "left_boundary_sha256", "right_boundary_sha256"):
        _sha(data["frames"][key], f"frames.{key}")
    _require(
        data["frames"]["generation"]
        == "single-global-exact-table-sliced-with-byte-identical-overlap",
        "frames: independently generated/rounded boundary frames forbidden",
    )

    _exact_keys(data["matrix"], {"center", "linear", "remainder", "hull"}, "matrix")
    _verify_affine_hull(data["matrix"])

    _exact_keys(
        data["proof"],
        {
            "ok", "refusal_code", "existence_certified", "uniqueness_certified",
            "factor_rank_certified", "outward_remainders",
        },
        "proof",
    )
    _require(
        data["proof"] == {
            "ok": True,
            "refusal_code": 0,
            "existence_certified": True,
            "uniqueness_certified": True,
            "factor_rank_certified": True,
            "outward_remainders": True,
        },
        "proof: incomplete or refused",
    )

    integrity = data["integrity"]
    _exact_keys(
        integrity, {"producer", "inputs", "input_sha256", "output_sha256"}, "integrity"
    )
    _verify_path_hash(integrity["producer"], repo_root, "integrity.producer")
    _require(isinstance(integrity["inputs"], list) and integrity["inputs"],
             "integrity.inputs: expected nonempty list")
    inputs = [
        _verify_path_hash(item, repo_root, f"integrity.inputs[{i}]")
        for i, item in enumerate(integrity["inputs"])
    ]
    _require(
        len({item["path"] for item in inputs}) == len(inputs),
        "integrity.inputs: duplicate paths",
    )
    _require(
        integrity["input_sha256"] == canonical_sha256(inputs),
        "integrity.input_sha256: manifest hash mismatch",
    )
    _require(
        integrity["output_sha256"] == canonical_sha256(data["matrix"]),
        "integrity.output_sha256: matrix payload hash mismatch",
    )
    return True


def verify_chain(handoffs: Iterable[dict[str, Any]], repo_root: Path | None = None) -> bool:
    items = list(handoffs)
    _require(items, "chain: empty")
    for item in items:
        verify_handoff(item, repo_root)
    kind = items[0]["artifact_kind"]
    _require(all(item["artifact_kind"] == kind for item in items), "chain: mixed kinds")
    expected = INFINITY_CHUNKS if kind == "infinity-standard-fundamental" else HORIZON_CHUNKS
    by_id = {item["chunk_id"]: item for item in items}
    _require(len(by_id) == len(items), "chain: duplicate chunk id")
    _require(set(by_id) == set(expected), "chain: incomplete or extra chunk coverage")
    _require(
        [item["chunk_id"] for item in items] == list(expected),
        "chain: reset artifacts are not in exact radial order",
    )
    ordered = items
    for left, right in zip(ordered, ordered[1:]):
        _require(
            _rational(left["domain"]["end"], "chain.left.end")
            == _rational(right["domain"]["start"], "chain.right.start"),
            "chain: boundary gap/overlap",
        )
        _require(
            left["frames"]["table_sha256"] == right["frames"]["table_sha256"],
            "chain: global frame table mismatch",
        )
        _require(
            left["frames"]["right_boundary_sha256"]
            == right["frames"]["left_boundary_sha256"],
            "chain: adjacent boundary frame bytes differ",
        )
        _require(left["cell"] == right["cell"], "chain: parameter cell differs")
        _require(left["state"] == right["state"], "chain: state chart/order differs")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args(argv)
    try:
        payloads = [json.loads(path.read_text()) for path in args.artifacts]
        if args.chain:
            verify_chain(payloads, args.repo_root)
        else:
            for payload in payloads:
                verify_handoff(payload, args.repo_root)
    except (OSError, json.JSONDecodeError, HandoffError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
