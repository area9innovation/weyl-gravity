#!/usr/bin/env python3
"""Emit the ND2 exact arity-two consumer and Cartan-solver certificate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_IMPORT_ROOT = TRANSFER_ROOT.parent / "classical_import"
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "ND2_ARITY_TWO_CARTAN_ENGINE.json"
SNAPSHOT_PATH = CLASSICAL_IMPORT_ROOT / "snapshots" / "bootstrap-v1.json"

try:
    from .arity_two_cartan import (
        AdmissibleArityTwoComplex,
        ArityTwoComplex,
        BilinearConstraint,
        LinearOperator,
        build_exact_correction_fixture,
        classify_cartan_source,
    )
    from .support_local_q2_consumer import (
        evaluate_identity_fixture,
        parse_support_local_export,
    )
except ImportError:  # direct script execution
    from arity_two_cartan import (
        AdmissibleArityTwoComplex,
        ArityTwoComplex,
        BilinearConstraint,
        LinearOperator,
        build_exact_correction_fixture,
        classify_cartan_source,
    )
    from support_local_q2_consumer import (
        evaluate_identity_fixture,
        parse_support_local_export,
    )


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_payload(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _sparse_bilinear(operator, complex_) -> dict[str, object]:
    entries = []
    for output, left, right in complex_.coordinate_slots(operator.degree):
        value = operator.entries[output][left][right]
        if value:
            entries.append([output, left, right, _fraction_payload(value)])
    return {
        "degree": operator.degree,
        "coordinate_convention": "graded-symmetric i<=j; odd diagonal omitted",
        "ambient_coordinate_count": len(complex_.coordinate_slots(operator.degree)),
        "nonzero_entries": entries,
    }


def _identity_monomial(arity: int) -> dict[str, object]:
    return {
        "operator_id": "scalar_identity",
        "input_jets": [[0, 0, 0, 0] for _ in range(arity)],
        "free_indices": [],
        "contractions": [],
    }


def _operator(
    arity: int,
    degree: int,
    components: list[dict[str, object]],
    symbols: list[str],
) -> dict[str, object]:
    return {
        "arity": arity,
        "degree": degree,
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "components": components,
        "row_completeness": [
            {
                "output": symbol,
                "status": "COMPLETE",
                "component_ids": [
                    component["component_id"]
                    for component in components
                    if component["output"] == symbol
                ],
            }
            for symbol in symbols
        ],
    }


def _consumer_fixture_payload() -> dict[str, object]:
    roles = (
        ("h", "metric", 0, 0, 0),
        ("xi", "diffeomorphism_ghost", 1, 0, 1),
        ("omega", "weyl_ghost", 1, 0, 1),
        ("h_star", "metric_antifield", -1, 1, 1),
        ("xi_star", "diffeomorphism_ghost_antifield", -2, 2, 0),
        ("omega_star", "weyl_ghost_antifield", -2, 2, 0),
    )
    generators = [
        {
            "symbol": symbol,
            "role": role,
            "sector": "minimal",
            "tensor_type": {"bundle": role},
            "ghost_number": ghost,
            "antifield_number": antifield,
            "form_degree": 0 if antifield == 0 else 4,
            "Grassmann_parity": parity,
            "mass_dimension": 0,
            "Weyl_weight": 0,
            "canonical_index_symmetry": {"kind": "fixture"},
        }
        for symbol, role, ghost, antifield, parity in roles
    ]
    symbols = [generator["symbol"] for generator in generators]
    q2_component = {
        "component_id": "q2_xi_h_h",
        "output": "xi",
        "inputs": ["h", "h"],
        "max_jet_orders": [0, 0],
        "expression": {
            "terms": [
                {
                    "coefficient": {"numerator": 1, "denominator": 2},
                    "monomial": _identity_monomial(2),
                },
                {
                    "coefficient": {"numerator": 1, "denominator": 2},
                    "monomial": _identity_monomial(2),
                },
            ]
        },
    }
    D_component = {
        "component_id": "D_h_h",
        "output": "h",
        "inputs": ["h"],
        "max_jet_orders": [0],
        "expression": {
            "terms": [{"coefficient": 0, "monomial": _identity_monomial(1)}]
        },
    }
    proof_checks = [
        {
            "check_id": check_id,
            "status": "VERIFIED",
            "proof_artifact": {"path": f"fixture/{check_id}.json", "sha256": "0" * 64},
        }
        for check_id in sorted(
            {
                "q1_squared_zero",
                "q1_q2_arity_two_nilpotency",
                "q2_koszul_symmetry",
                "q2_row_completeness",
                "D_q1_commutator_zero",
                "D_q2_derivation",
                "BV_cyclicity_q2",
            }
        )
    ]
    payload: dict[str, object] = {
        "schema": "quantum-weyl-support-local-q2-export-v1",
        "classical_commit": "0" * 40,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "convention": "suspended-graded-symmetric-factorial-v1",
        "expression_schema_version": "quantum-weyl-canonical-local-expression-v1",
        "support_category": {
            "spacetime_dimension": 4,
            "background_id": "ND2_fixture",
            "boundary_conditions": "compact support fixture",
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "test_function_space": "fixture_C_c_infinity",
            "integration_by_parts_quotient": False,
            "maximum_jet_order": 0,
        },
        "generators": generators,
        "q1": _operator(1, 1, [], symbols),
        "q2": _operator(2, 1, [q2_component], symbols),
        "D_action": _operator(1, 0, [D_component], symbols),
        "proof_checks": proof_checks,
    }
    payload["canonical_hashes"] = {
        "support_metadata_hash": _canonical_hash(
            {
                "convention": payload["convention"],
                "expression_schema_version": payload["expression_schema_version"],
                "support_category": payload["support_category"],
            }
        ),
        "generator_dictionary_hash": _canonical_hash(payload["generators"]),
        "q1_hash": _canonical_hash(payload["q1"]),
        "q2_hash": _canonical_hash(payload["q2"]),
        "D_action_hash": _canonical_hash(payload["D_action"]),
        "proof_checks_hash": _canonical_hash(payload["proof_checks"]),
    }
    return payload


def _source_manifest() -> dict[str, str]:
    paths = (
        "arity_two_cartan.py",
        "local_expression_ast.py",
        "support_local_q2_consumer.py",
        "nd2_arity_two_certificate.py",
        "schema/nd2-arity-two-cartan-engine-v1.schema.json",
        "tests/test_arity_two_cartan.py",
        "tests/test_local_expression_ast.py",
        "tests/test_support_local_q2_consumer.py",
        "tests/test_nd2_arity_two_certificate.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    parsed = parse_support_local_export(_consumer_fixture_payload())
    evaluated = evaluate_identity_fixture(parsed)

    data = build_exact_correction_fixture()
    checks = data.checks()
    classification = data.classify()
    if classification.correction is None:
        raise AssertionError("ND2 exact fixture did not produce a correction")
    correction = classification.correction

    mutated_rows = [list(row) for row in data.lie_D.entries]
    mutated_rows[5][5] = 3
    mutated_D = LinearOperator.from_rows("mutated_L_D", 0, mutated_rows)
    mutation_defect = data.complex.linear_bracket(mutated_D, data.q2, name="mutation_[D,q2]")

    obstruction_complex = ArityTwoComplex(
        (0,),
        (0,),
        LinearOperator.zero("q1", 1, 1),
    )
    obstruction_source = obstruction_complex.operator_from_coordinates(
        0,
        (1,),
        name="normalized_obstruction",
    )
    obstruction = classify_cartan_source(obstruction_complex, obstruction_source)

    primitive_slots = data.complex.coordinate_slots(-1)
    constraints = tuple(
        BilinearConstraint.from_row(
            f"forbid_iota2_{index}",
            -1,
            [int(column == index) for column in range(len(primitive_slots))],
        )
        for index in range(len(primitive_slots))
    )
    admissible = AdmissibleArityTwoComplex(data.complex, constraints, (-1,))
    restricted = classify_cartan_source(admissible, data.cartan_source())

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    exports = {row["export_id"]: row["status"] for row in snapshot["required_exports"]}
    source_manifest = _source_manifest()
    return {
        "result_id": "ND2_ARITY_TWO_CARTAN_ENGINE",
        "result_state": "ENGINE_READY_AWAITING_SUPPORT_LOCAL_CLASSICAL_EXPORT",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_verdict": "INPUT_GATE_BLOCKED",
        "convention": "suspended-graded-symmetric-factorial-v1",
        "consumer_fixture": {
            "schema_version": parsed.expression_schema_version,
            "generator_count": len(parsed.symbols),
            "canonical_expression_sha256": parsed.canonical_expression_sha256,
            "q2_nonzero": not evaluated.q2.is_zero(),
            "q1_q2_nilpotency": evaluated.complex.linear_bracket(
                evaluated.complex.q1,
                evaluated.q2,
                name="[q1,q2]",
            ).is_zero(),
            "unknown_expression_languages": "REJECTED",
            "nonidentity_fixture_evaluation": "REJECTED",
        },
        "exact_correction_fixture": {
            "basis_dimension": data.complex.dimension,
            "checks": checks,
            "cartan_source": _sparse_bilinear(data.cartan_source(), data.complex),
            "classification": classification.status,
            "iota_D2": _sparse_bilinear(correction, data.complex),
            "correction_identity": data.complex.differential(
                correction,
                name="[q1,iota_D2]",
            ).entries
            == data.cartan_source().scaled(-1).entries,
        },
        "mutation_fixture": {
            "mutation": "change weight-two output D eigenvalue from 2 to 3",
            "D_derivation_defect": _sparse_bilinear(mutation_defect, data.complex),
            "nonzero_defect_detected": not mutation_defect.is_zero(),
            "solver_gate": "REJECTED_BEFORE_CORRECTION_CLASSIFICATION",
        },
        "obstruction_fixture": {
            "classification": obstruction.status,
            "source": _sparse_bilinear(obstruction_source, obstruction_complex),
            "dual_witness": [
                _fraction_payload(value) for value in (obstruction.dual_witness or ())
            ],
            "dual_witness_normalization": "1",
        },
        "admissibility_fixture": {
            "ambient_classification": classification.status,
            "admissible_classification": restricted.status,
            "forbidden_primitive_coordinate_count": len(primitive_slots),
            "dual_witness_present": restricted.dual_witness is not None,
        },
        "input_gate": {
            "support_local_classical_bv_q2": exports["support_local_classical_bv_q2"],
            "local_D_action_on_bv_generators": exports["local_D_action_on_bv_generators"],
            "classical_inclusion_iota_cl": exports["classical_inclusion_iota_cl"],
            "classical_projection_pi_cl": exports["classical_projection_pi_cl"],
            "classical_homotopy_s_cl": exports["classical_homotopy_s_cl"],
            "physical_evaluator": "NOT_REGISTERED_PENDING_EXPRESSION_SCHEMA",
        },
        "established": [
            "canonical exact local-expression AST with duplicate-term reduction and jet-bound checks",
            "independent support-local export consumer with fail-closed evaluator dispatch",
            "full finite arity-two q1/q2/D derivation and Cartan-source tensors",
            "exact iota_D^(2) boundary solver with retained rational primitive",
            "normalized dual witness for nontrivial obstruction",
            "admissibility constraints can reject an ambient but forbidden primitive",
        ],
        "not_established": [
            "a support-local conformal-gravity q2 coefficient",
            "a physical expression evaluator for the pending classical schema",
            "the conformal-gravity arity-two Cartan source or iota_D^(2)",
            "cyclic, real, boundary-compatible, or causal admissibility of a physical correction",
            "q3, higher transferred brackets, quantum corrections, or a Lorentzian theorem",
        ],
        "next_gate": "import the pinned classical q1/q2/D action and contraction, register its exact expression evaluator, compute the physical Cartan source, then retain either iota_D^(2) or its normalized admissible obstruction witness",
        "provenance": {
            "classical_snapshot": str(SNAPSHOT_PATH.relative_to(ROOT)),
            "classical_snapshot_sha256": _sha256(SNAPSHOT_PATH),
            "support_local_contract": "quantum-weyl/classical_import/certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json",
            "support_local_contract_sha256": _sha256(
                CLASSICAL_IMPORT_ROOT / "certificates" / "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json"
            ),
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "schema": "quantum-weyl/transfer/schema/nd2-arity-two-cartan-engine-v1.schema.json",
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
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"ND2 arity-two engine certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("ND2 ARITY-TWO CARTAN ENGINE: PRIMITIVE/OBSTRUCTION SOLVER READY, PHYSICAL INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
