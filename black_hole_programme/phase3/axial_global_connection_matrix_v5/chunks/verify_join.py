#!/usr/bin/env python3
"""Fail-closed verifier for the exact 224-factor moving-frame join."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .factor_cover import factor_id, factor_table_hash, verify_factor_cover
from .verify_handoff import (
    CELL,
    HandoffError,
    _exact_keys,
    _file_sha256,
    _require,
    _sha,
    _verify_affine_hull,
    canonical_sha256,
)
from .verify_microfactor import BLOCK_ORDER


SCHEMA = "phase3-axial-moving-frame-global-join-v1"


def verify_join(data: Any, repo_root: Path | None = None) -> bool:
    _exact_keys(
        data,
        {
            "schema", "artifact_kind", "status", "cell", "domain", "state",
            "composition", "frames", "matrix", "integrity", "proof",
        },
        "root",
    )
    _require(data["schema"] == SCHEMA, "root: wrong schema")
    _require(
        data["artifact_kind"] == "infinity-moving-frame-global-join",
        "root: wrong artifact kind",
    )
    _require(data["status"] == "CERTIFIED", "root: noncertified join")
    _require(data["cell"] == CELL, "cell: wrong parameter cell")
    _require(
        data["domain"] == {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": "0/1",
            "end": "28/1",
        },
        "domain: wrong full infinity-side span",
    )
    _require(
        data["state"] == {
            "rows": 12,
            "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "state: wrong chart/order",
    )
    factor_count = data["composition"].get("factor_count")
    _require(
        isinstance(factor_count, int)
        and factor_count >= 224
        and data["composition"] == {
            "factor_count": factor_count,
            "radial_order": "left-multiply-increasing-exact-radial-leaf",
            "dyadic_rebase_bits_after_each_join": 128,
            "standard_basis_materialized": False,
        },
        "composition: wrong join contract",
    )
    _exact_keys(
        data["frames"],
        {
            "table_sha256", "left_boundary_sha256",
            "right_boundary_sha256", "adjacent_hashes_verified",
        },
        "frames",
    )
    for key in ("table_sha256", "left_boundary_sha256", "right_boundary_sha256"):
        _sha(data["frames"][key], f"frames.{key}")
    _require(
        data["frames"]["adjacent_hashes_verified"] is True,
        "frames: adjacency not verified",
    )

    _exact_keys(data["matrix"], {"center", "linear", "remainder", "hull"}, "matrix")
    _verify_affine_hull(data["matrix"])
    zero_bits = ["0000000000000000", "0000000000000000"]
    for row in range(8):
        for col in range(8, 12):
            _require(
                data["matrix"]["center"][row][col] == "0/1"
                and data["matrix"]["linear"][row][col] == "0/1"
                and data["matrix"]["remainder"][row][col] == zero_bits,
                "matrix: upper-right block is not exactly zero",
            )

    proof = data["proof"]
    _exact_keys(
        proof,
        {
            "ok", "factor_chain_verified", "factor_rank_certified",
            "factor_rank", "rank_argument", "upper_right_exact_zero",
            "shared_generator_preserved", "block_max_width",
        },
        "proof",
    )
    _require(
        proof["ok"] is True
        and proof["factor_chain_verified"] is True
        and proof["factor_rank_certified"] is True
        and proof["factor_rank"] == 12
        and proof["rank_argument"] == "product-of-block-diagonal-determinants"
        and proof["upper_right_exact_zero"] is True
        and proof["shared_generator_preserved"] is True,
        "proof: incomplete or refused",
    )
    _exact_keys(
        proof["block_max_width"], {"carrier", "lower", "kernel"},
        "proof.block_max_width",
    )
    for key, value in proof["block_max_width"].items():
        _require(isinstance(value, str), f"proof.block_max_width.{key}: expected string")
        try:
            width = float(value)
        except ValueError as exc:
            raise HandoffError(f"proof.block_max_width.{key}: malformed") from exc
        _require(
            math.isfinite(width) and width >= 0.0,
            f"proof.block_max_width.{key}: nonfinite/negative",
        )

    integrity = data["integrity"]
    _exact_keys(
        integrity,
        {
            "producer", "join_source", "join_receipt", "factor_artifacts",
            "factor_set_sha256", "output_sha256",
        },
        "integrity",
    )
    for key in ("producer", "join_source", "join_receipt"):
        _exact_keys(integrity[key], {"path", "sha256"}, f"integrity.{key}")
        _sha(integrity[key]["sha256"], f"integrity.{key}.sha256")
    factors = integrity["factor_artifacts"]
    _require(
        isinstance(factors, list) and len(factors) == factor_count,
        "factor set incomplete",
    )
    for expected, item in enumerate(factors):
        _exact_keys(item, {"factor_id", "path", "sha256"}, f"factor[{expected}]")
        _require(isinstance(item["factor_id"], str), "factor id malformed")
        _sha(item["sha256"], f"factor[{expected}].sha256")
    _require(
        integrity["factor_set_sha256"] == canonical_sha256(factors),
        "factor set manifest hash mismatch",
    )
    _require(
        integrity["output_sha256"] == canonical_sha256(data["matrix"]),
        "join matrix hash mismatch",
    )
    if repo_root is not None:
        for key in ("producer", "join_source", "join_receipt"):
            path = repo_root / integrity[key]["path"]
            _require(path.is_file(), f"integrity.{key}: missing")
            _require(
                _file_sha256(path) == integrity[key]["sha256"],
                f"integrity.{key}: hash mismatch",
            )
        payloads = []
        for expected, item in enumerate(factors):
            path = repo_root / item["path"]
            _require(path.is_file(), f"factor[{expected}]: missing")
            _require(
                _file_sha256(path) == item["sha256"],
                f"factor[{expected}]: hash mismatch",
            )
            payloads.append(json.loads(path.read_text()))
        ordered = verify_factor_cover(payloads, repo_root)
        _require(payloads == ordered, "factor set is not in exact radial order")
        _require(
            [item["factor_id"] for item in factors]
            == [factor_id(payload) for payload in payloads],
            "factor ids differ from payloads",
        )
        receipt_path = repo_root / integrity["join_receipt"]["path"]
        receipt = json.loads(receipt_path.read_text())
        _require(
            receipt.get("schema") == "phase3-axial-factor-cover-join-source-v2"
            and receipt.get("layout") == "contiguous-block-lower-v1"
            and receipt.get("factor_count") == factor_count
            and receipt.get("composition")
            == "left-multiply in increasing exact radial leaf order"
            and receipt.get("dyadic_rebase_bits_after_each_join") == 128
            and receipt.get("standard_basis_materialized") is False,
            "join receipt contract mismatch",
        )
        receipt_factors = receipt.get("factor_sha256")
        _require(
            receipt_factors
            == [
                {
                    "factor_id": item["factor_id"],
                    "path": item["path"],
                    "sha256": item["sha256"],
                }
                for item in factors
            ],
            "join receipt factor set/order mismatch",
        )
        from .join_microfactors import render_join_source

        rendered = render_join_source(payloads).encode()
        source_sha256 = hashlib.sha256(rendered).hexdigest()
        _require(
            source_sha256 == integrity["join_source"]["sha256"],
            "join source is not the deterministic ordered factor composition",
        )
        _require(
            receipt.get("source")
            == {
                "path": integrity["join_source"]["path"],
                "sha256": source_sha256,
                "bytes": len(rendered),
            },
            "join receipt source pin mismatch",
        )
        _require(
            data["frames"]["table_sha256"]
            == factor_table_hash(payloads[0]),
            "join frame table differs from factors",
        )
        _require(
            data["frames"]["left_boundary_sha256"]
            == payloads[0]["frames"]["left_boundary_sha256"]
            and data["frames"]["right_boundary_sha256"]
            == payloads[-1]["frames"]["right_boundary_sha256"],
            "join endpoint frame hashes differ",
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args()
    try:
        verify_join(json.loads(args.artifact.read_text()), args.repo_root)
    except (OSError, json.JSONDecodeError, HandoffError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
