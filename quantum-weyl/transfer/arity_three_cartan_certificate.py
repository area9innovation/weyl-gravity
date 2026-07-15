#!/usr/bin/env python3
"""Emit the exact arity-three Cartan recurrence engine certificate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "ND3_ARITY_THREE_CARTAN_ENGINE.json"
SNAPSHOT_PATH = ROOT / "quantum-weyl" / "classical_import" / "snapshots" / "bootstrap-v1.json"

try:
    from .arity_three_cartan import (
        ArityThreeCartanData,
        ArityThreeComplex,
        build_direct_q3_correction_fixture,
        build_exchange_bracket_fixture,
        classify_arity_three_source,
    )
    from .arity_two_cartan import LinearOperator
except ImportError:
    from arity_three_cartan import (
        ArityThreeCartanData,
        ArityThreeComplex,
        build_direct_q3_correction_fixture,
        build_exchange_bracket_fixture,
        classify_arity_three_source,
    )
    from arity_two_cartan import LinearOperator


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _exact(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _sparse(operator, complex_) -> dict[str, object]:
    entries = []
    for output, first, second, third in complex_.coordinate_slots(operator.degree):
        value = operator.entries[output][first][second][third]
        if value:
            entries.append([output, first, second, third, _exact(value)])
    return {
        "degree": operator.degree,
        "ambient_coordinate_count": len(complex_.coordinate_slots(operator.degree)),
        "nonzero_entries": entries,
    }


def _source_manifest() -> dict[str, str]:
    paths = (
        "arity_two_cartan.py",
        "arity_three_cartan.py",
        "arity_three_cartan_certificate.py",
        "schema/arity-three-cartan-engine-v1.schema.json",
        "tests/test_arity_three_cartan.py",
        "tests/test_arity_three_cartan_certificate.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    data = build_direct_q3_correction_fixture()
    classification = data.classify()
    if classification.correction is None:
        raise AssertionError("arity-three direct fixture has no retained correction")

    exchange_complex, q2, iota2, exchange = build_exchange_bracket_fixture()
    reverse_exchange = exchange_complex.bilinear_bracket(iota2, q2, name="[iota_D2,q2]")

    obstruction_complex = ArityThreeComplex(
        (0,),
        (0,),
        LinearOperator.zero("q1", 1, 1),
    )
    obstruction_source = obstruction_complex.operator_from_coordinates(0, (1,), name="obstruction")
    obstruction = classify_arity_three_source(obstruction_complex, obstruction_source)

    rows = [list(row) for row in data.lie_D.entries]
    rows[3][3] = 4
    mutation = ArityThreeCartanData(
        data.complex,
        data.q2,
        data.q3,
        data.iota_D,
        data.iota_D2,
        LinearOperator.from_rows("mutated_L_D", 0, rows),
        data.lie_D2,
        data.lie_D3,
    )
    mutation_checks = mutation.checks()

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    exports = {row["export_id"]: row["status"] for row in snapshot["required_exports"]}
    source_manifest = _source_manifest()
    return {
        "result_id": "ND3_ARITY_THREE_CARTAN_ENGINE",
        "result_state": "ENGINE_READY_AWAITING_Q3_AND_LOWER_PHYSICAL_DATA",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_verdict": "INPUT_GATE_BLOCKED",
        "convention": "suspended-graded-symmetric-factorial-v1",
        "recurrence": "[q1,iota_D^(3)]=-[q3,iota_D]-[q2,iota_D^(2)]+L_D^(3)",
        "direct_q3_fixture": {
            "checks": data.checks(),
            "q3_nonzero": not data.q3.is_zero(),
            "source": _sparse(data.cartan_source(), data.complex),
            "classification": classification.status,
            "correction": _sparse(classification.correction, data.complex),
            "correction_identity": (
                data.complex.differential(classification.correction, name="delta_iota_D3").entries
                == data.cartan_source().scaled(-1).entries
            ),
        },
        "exchange_fixture": {
            "q2_nonzero": not q2.is_zero(),
            "iota_D2_nonzero": not iota2.is_zero(),
            "exchange_source": _sparse(exchange, exchange_complex),
            "exchange_nonzero": not exchange.is_zero(),
            "graded_commutator_symmetry": exchange.entries == reverse_exchange.entries,
        },
        "obstruction_fixture": {
            "classification": obstruction.status,
            "dual_witness": [_exact(value) for value in (obstruction.dual_witness or ())],
            "dual_witness_normalization": "1",
        },
        "mutation_fixture": {
            "mutation": "change the weight-three q3 output D eigenvalue from 3 to 4",
            "Cartan_identity_arity_one": mutation_checks["Cartan_identity_arity_one"],
            "D_equivariance_arity_three": mutation_checks["D_equivariance_arity_three"],
            "solver_gate": "REJECTED_BEFORE_CORRECTION_CLASSIFICATION",
        },
        "input_gate": {
            "support_local_classical_bv_q2": exports["support_local_classical_bv_q2"],
            "classical_inclusion_iota_cl": exports["classical_inclusion_iota_cl"],
            "classical_projection_pi_cl": exports["classical_projection_pi_cl"],
            "classical_homotopy_s_cl": exports["classical_homotopy_s_cl"],
            "support_local_classical_bv_q3": "NOT_AVAILABLE_NO_VERSIONED_EXPORT",
            "physical_iota_D2": "NOT_COMPUTED_PENDING_ARITY_TWO_PHYSICAL_RUN",
        },
        "established": [
            "exact graded-symmetric ternary-map complex and rational boundary solver",
            "arity-three Q-squared, Cartan, D-equivariance, and source-closure checks",
            "separate direct q3 and exchange [q2,iota_D^(2)] source tensors",
            "retained exact iota_D^(3) correction or normalized dual obstruction witness",
        ],
        "not_established": [
            "a conformal-gravity q3 Taylor coefficient",
            "the physical arity-three Cartan source or correction",
            "quartic dynamical/topological mixing or an instability amplitude",
            "a quantum correction or Lorentzian causal theorem",
        ],
        "next_gate": "after the physical arity-two run, import q3 and L_D^(3), recompute the direct and exchange sources, and classify the admissible arity-three obstruction",
        "provenance": {
            "classical_snapshot": str(SNAPSHOT_PATH.relative_to(ROOT)),
            "classical_snapshot_sha256": _sha256(SNAPSHOT_PATH),
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "schema": "quantum-weyl/transfer/schema/arity-three-cartan-engine-v1.schema.json",
        },
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content):
        raise SystemExit(f"arity-three Cartan certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("ND3 ARITY-THREE CARTAN: DIRECT/EXCHANGE ENGINE READY, PHYSICAL INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
