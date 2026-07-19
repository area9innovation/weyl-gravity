#!/usr/bin/env python3
"""Independent replay of the physical-Hessian n=3 carrier projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from spectral.euclidean.generic_background_physical_hessian_n3_five_carrier_projection import (
    DEPENDENCIES,
    OUTPUT,
    PHYSICAL_MOMENTUM_FIXTURES,
    ROOT,
    UNISOLVENCE_PRIME,
    UNSEEN_MOMENTUM_FIXTURES,
    _evaluate_projection_row,
    _fixture_coordinate_polynomials,
    _modular_rank,
    _validate_projection_rows,
    validate,
)
from spectral.euclidean.generic_background_ghost_n3_five_carrier_projection import (
    _fixture_momenta,
    _homogeneous_monomials,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_dependencies(payload: dict[str, Any]) -> None:
    for name, expected_path in DEPENDENCIES.items():
        reference = payload["dependencies"][name]
        path = ROOT / reference["path"]
        if (
            path.resolve() != expected_path.resolve()
            or not path.is_file()
            or _sha256(path) != reference["sha256"]
            or json.loads(path.read_text()).get("result_id")
            != reference["result_id"]
        ):
            raise ValueError(f"{name} dependency path, identity, or hash drifted")


def _check_unisolvence(payload: dict[str, Any]) -> None:
    declared = payload["interpolation_certificate"]
    boxes = [
        tuple(int(momentum.dot(momentum)) for momentum in _fixture_momenta(fixture))
        for fixture in PHYSICAL_MOMENTUM_FIXTURES
    ]
    monomials = _homogeneous_monomials(6, 3)
    rows = [
        [
            int(sp.prod(box[index] ** exponent[index] for index in range(3)))
            for exponent in monomials
        ]
        for box in boxes
    ]
    if (
        declared["training_fixture_count"] != len(boxes)
        or len(boxes) != 28
        or declared["maximum_box_monomial_count"] != len(monomials)
        or len(monomials) != 28
        or declared["unisolvence_modulus"] != UNISOLVENCE_PRIME
        or _modular_rank(rows, UNISOLVENCE_PRIME) != 28
        or declared["degree_six_box_evaluation_rank_mod_prime"] != 28
    ):
        raise ValueError("degree-six physical box unisolvence drifted")


def _check_fresh_unseen(payload: dict[str, Any], fixture_index: int) -> None:
    fixture = UNSEEN_MOMENTUM_FIXTURES[fixture_index]
    boxes, coordinates, ledger = _fixture_coordinate_polynomials(
        fixture, use_cache=False
    )
    if ledger["carrier_matrix_rank"] != 10 or ledger["gauge_completed_rank"] != 11:
        raise ValueError("fresh unseen carrier rank drifted")
    defects = []
    for row, coordinate in zip(payload["projection_rows"], coordinates):
        predicted = _evaluate_projection_row(row, boxes)
        if predicted != coordinate:
            defects.append(
                {
                    "channel_id": row["channel_id"],
                    "defect": str(sp.expand(predicted.as_expr() - coordinate.as_expr())),
                }
            )
    if defects:
        raise ValueError(f"fresh unseen physical projection defects: {defects}")


def verify(
    payload: dict[str, Any] | None = None,
    *,
    replay_unseen: bool = True,
    fixture_index: int = 0,
) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if payload is None else payload
    validate(stored)
    _check_dependencies(stored)
    _validate_projection_rows(stored["projection_rows"])
    _check_unisolvence(stored)
    if replay_unseen:
        _check_fresh_unseen(stored, fixture_index)
    print(
        "physical Hessian n=3 five-carrier independent verification: PASS "
        f"(fresh_unseen={replay_unseen})"
    )
    return stored


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-fresh-unseen", action="store_true")
    parser.add_argument("--fixture-index", type=int, choices=range(2), default=0)
    args = parser.parse_args()
    verify(
        replay_unseen=not args.skip_fresh_unseen,
        fixture_index=args.fixture_index,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
