#!/usr/bin/env python3
"""Verify the complete spatial-R6# aligned Jordan-chain obstruction."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_r6_chain_obstruction import (  # noqa: E402
    ExpandedRelativeR6ChainObstruction,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_expanded_relative_witness_r6_chain_obstruction.json"
)


def _rejects(candidate: ExpandedRelativeR6ChainObstruction) -> bool:
    try:
        candidate.verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-chain-break", action="store_true")
    parser.add_argument("--claim-semisimple", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()

    obstruction = ExpandedRelativeR6ChainObstruction.build()
    certificate = obstruction.certificate()

    checks = {
        "direct_intrinsic_condition_map_is_232_by_46": (
            obstruction.chain_sensitivity.shape == (232, 46)
        ),
        "direct_intrinsic_condition_map_rank_is_zero": (
            obstruction.chain_sensitivity.rank() == 0
        ),
        "all_first_direction_intertwiners_annihilate_f23": (
            obstruction.aligned_first_column_eigenvector == sp.zeros(14, 46)
        ),
        "all_first_direction_intertwiners_annihilate_h23": (
            obstruction.aligned_first_column_generalized == sp.zeros(14, 46)
        ),
        "all_139_sparse_samples_are_regular": (
            min(obstruction.sparse_regularity_ranks) == 116
        ),
        "all_139_sparse_samples_retain_chain": (
            sum(obstruction.sparse_chain_defects) == 0
        ),
        "mutated_intrinsic_sensitivity_rejected": _rejects(
            replace(
                obstruction,
                chain_sensitivity=(
                    obstruction.chain_sensitivity
                    + sp.SparseMatrix(232, 46, {(0, 0): 1})
                ),
            )
        ),
        "no_green_flag_promoted": (
            certificate["warranted_atomic_flags"] == []
            and certificate["status_flags_promoted"] == []
            and not certificate["prolonged_green_witness"]
            and not certificate["curvature_causal_green_operators"]
            and not certificate["causal_green_homotopy"]
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"R6# chain-obstruction checks failed: {failed}")

    if args.emit:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.claim_chain_break:
        raise SystemExit(
            "REFUSED: every member of the complete fixed-temporal 46-parameter "
            "spatial R6# family retains the intrinsic +1 polynomial chain"
        )
    if args.claim_semisimple:
        raise SystemExit(
            "REFUSED: the universal length-two chain rules out semisimplicity "
            "at all nonzero characteristic roots"
        )
    if args.promote_flag:
        raise SystemExit(
            "REFUSED: this scoped obstruction promotes no Green-theoretic flag"
        )

    print("=== Expanded relative R6# chain obstruction ===")
    for name, value in checks.items():
        print(f"  {'PASS' if value else 'FAIL'} {name}")
    print(
        "  exact result: 232x46 intrinsic chain-condition map has rank 0; "
        "the +1 chain persists for all 46 parameters"
    )
    print(
        "  sparse screen: 139 regular rational samples, 0 semisimple-at-all-"
        "nonzero-roots candidates"
    )
    print("  no Green-theoretic project flag promoted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
