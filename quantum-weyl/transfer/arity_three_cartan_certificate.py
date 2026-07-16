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
Q2_REPLAY_PATH = TRANSFER_ROOT / "certificates" / "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json"
RETAINED_Q2_PATH = TRANSFER_ROOT / "certificates" / "BERGER_RETAINED_26_Q2_TRANSFER.json"
CAUSAL_CHAIN_PATH = (
    ROOT / "quantum-weyl" / "lorentzian" / "certificates" / "BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
)

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
        "../reports/nd3-current-input-consolidation.md",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def _load_current_inputs() -> dict[str, dict[str, Any]]:
    return {
        "support_local_q2_replay": json.loads(Q2_REPLAY_PATH.read_text(encoding="utf-8")),
        "retained_q2_transfer": json.loads(RETAINED_Q2_PATH.read_text(encoding="utf-8")),
        "causal_chain_v2": json.loads(CAUSAL_CHAIN_PATH.read_text(encoding="utf-8")),
    }


def _validate_current_inputs(inputs: dict[str, dict[str, Any]]) -> None:
    if set(inputs) != {
        "support_local_q2_replay",
        "retained_q2_transfer",
        "causal_chain_v2",
    }:
        raise ValueError("ND3 current-input set drifted")
    q2 = inputs["support_local_q2_replay"]
    retained = inputs["retained_q2_transfer"]
    causal = inputs["causal_chain_v2"]
    if (
        q2.get("result_id") != "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"
        or q2.get("result_state")
        != "COMPLETE_SUPPORT_LOCAL_Q2_IMPORTED_IDENTITIES_INDEPENDENTLY_REPLAYED_TRANSFER_PENDING"
        or q2.get("claim_flags", {}).get("CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED") is not True
        or q2.get("claim_flags", {}).get(
            "SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED"
        )
        is not True
        or q2.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("ND3 support-local q2 prerequisite drifted")
    if (
        retained.get("result_id") != "BERGER_RETAINED_26_Q2_TRANSFER"
        or retained.get("result_state")
        != "RETAINED_26_ROW_Q2_TRANSFERRED_IDENTITIES_VERIFIED_FURTHER_RESIDUAL_TRANSFER_PENDING"
        or retained.get("claim_flags", {}).get("CLASSICAL_RETAINED_26_Q2_TRANSFERRED")
        is not True
        or retained.get("claim_flags", {}).get("RETAINED_Q1_Q2_IDENTITIES_VERIFIED")
        is not True
        or retained.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("ND3 retained q2/SDR prerequisite drifted")
    causal_checks = causal.get("coverage", {}).get("checks", {})
    if (
        causal.get("result_id") != "BERGER_CAUSAL_CHAIN_V2_IMPORT"
        or causal.get("result_state")
        != "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN"
        or causal.get("coverage", {}).get("D_Cartan_arities") != [1, 2]
        or causal_checks.get("causal_D_Cartan", {}).get("arity_two_cyclic_primitive")
        is not True
        or causal_checks.get("causal_D_Cartan", {}).get("arity_two_source_closed")
        is not True
        or causal_checks.get("full_54", {}).get("support_local_SDR_lift") is not True
        or causal.get("claim_flags", {}).get("BERGER_CAUSAL_D_CARTAN_V2_IMPORTED")
        is not True
        or causal.get("claim_flags", {}).get("BERGER_ARITY_THREE_D_CARTAN")
        is not False
        or causal.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("ND3 causal arity-two prerequisite drifted")


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

    current_inputs = _load_current_inputs()
    _validate_current_inputs(current_inputs)
    source_manifest = _source_manifest()
    return {
        "result_id": "ND3_ARITY_THREE_CARTAN_ENGINE",
        "result_state": "ENGINE_READY_LOWER_PHYSICAL_CHAIN_CERTIFIED_Q3_INPUT_BLOCKED",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
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
            "status": "LOWER_ARITY_CHAIN_READY_Q3_AND_L_D3_EXPORT_BLOCKED",
            "support_local_classical_bv_q2": "IMPORTED_AND_INDEPENDENTLY_REPLAYED_54_ROWS",
            "retained_q2_26": "TRANSFERRED_WITH_Q1_Q2_AND_CYCLIC_IDENTITIES_VERIFIED",
            "classical_inclusion_iota_cl": "IMPORTED_EXACT_IN_RETAINED_Q2_TRANSFER",
            "classical_projection_pi_cl": "IMPORTED_EXACT_IN_RETAINED_Q2_TRANSFER",
            "classical_homotopy_s_cl": "IMPORTED_IN_CAUSAL_54_TO_26_SDR_LIFT",
            "physical_iota_D2": "CERTIFIED_CAUSAL_CYCLIC_TWO_SIDED_54_ROWS",
            "support_local_classical_bv_q3": "NOT_AVAILABLE_NO_VERSIONED_EXPORT",
            "L_D3": "NOT_DECLARED_BY_VERSIONED_Q3_EXPORT",
            "physical_arity_three_execution_authorized": False,
        },
        "required_q3_export": {
            "support_category": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "required_objects": ["q3", "L_D3"],
            "required_checks": [
                "complete_54_row_field_ghost_antifield_coverage",
                "arity_three_Q_squared_identity",
                "D_equivariance_arity_three",
                "odd_Darboux_cyclicity",
                "exact_coefficient_domain",
                "content_hashes_and_classical_provenance",
            ],
            "zero_L_D3_is_allowed_only_if_explicitly_certified": True,
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
        "next_gate": "import a versioned support-local q3 and explicit L_D^(3) declaration, assemble them with the certified q2 and causal iota_D^(2), then classify the admissible arity-three obstruction",
        "provenance": {
            "current_inputs": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": _sha256(path),
                }
                for name, path in {
                    "support_local_q2_replay": Q2_REPLAY_PATH,
                    "retained_q2_transfer": RETAINED_Q2_PATH,
                    "causal_chain_v2": CAUSAL_CHAIN_PATH,
                }.items()
            },
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
        print("ND3 ARITY-THREE CARTAN: LOWER CHAIN READY, Q3/L_D3 INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
