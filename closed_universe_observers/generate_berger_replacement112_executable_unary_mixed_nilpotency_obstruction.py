#!/usr/bin/env python3
"""Produce the exact replacement-112 mixed-nilpotency obstruction witness."""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator

from closed_universe_observers import berger_replacement112_executable_unary_engine as engine


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION.json"
X = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-executable-unary-mixed-nilpotency-obstruction-v1.schema.json"
REPORT = P / "reports/berger-replacement112-executable-unary-mixed-nilpotency-obstruction.md"
DEPS = {
    "complete_108_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_108_unary_payload": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json",
    "positive_phi2_map": P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT.json",
    "positive_phi2_payload": P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT_PAYLOAD.json",
    "mixed_hessian_interface": P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE.json",
    "mixed_hessian_payload": P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE_PAYLOAD.json",
    "positive_action": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "positive_action_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
}
FIXTURE = {
    engine.SA: sp.Rational(3, 5),
    engine.CA: sp.Rational(4, 5),
    engine.SU: sp.Rational(5, 13),
    engine.CU: sp.Rational(12, 13),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def specialize(operator: engine.Operator) -> engine.Operator:
    result = {}
    for key, polynomial in operator.items():
        specialized = {}
        for monomial, coefficient in polynomial.items():
            value = sp.cancel(coefficient.subs(FIXTURE))
            if value != 0:
                specialized[monomial] = value
        if specialized:
            result[key] = specialized
    return result


def defect_record(key: tuple[int, int, tuple[int, ...], int], value: sp.Expr, rows: list[dict[str, Any]]) -> dict[str, Any]:
    row, column, word, mode = key
    return {
        "output_index": row,
        "output_row_id": rows[row]["row_id"],
        "input_index": column,
        "input_row_id": rows[column]["row_id"],
        "input_pbw_word": list(word),
        "time_mode": mode,
        "coefficient": sp.sstr(value),
    }


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    for certificate_name, payload_name in (
        ("complete_108_unary", "complete_108_unary_payload"),
        ("positive_phi2_map", "positive_phi2_payload"),
        ("mixed_hessian_interface", "mixed_hessian_payload"),
        ("positive_action", "positive_action_payload"),
    ):
        if sha(DEPS[payload_name]) != dependencies[certificate_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{certificate_name} payload hash mismatch")

    q1, assembly = engine.assemble()
    q00 = specialize(q1[(0, 0)])
    q10 = specialize(q1[(1, 0)])
    mixed_square = engine.add_operators(engine.compose(q10, q00), engine.compose(q00, q10))
    reduced, quotient = engine.background_quotient_defect(mixed_square, FIXTURE)
    if not reduced:
        raise AssertionError("expected exact mixed-nilpotency fixture obstruction disappeared")

    action_payload = dependencies["positive_action_payload"]
    rows = action_payload["carrier"]["rows"]
    ordered = sorted(reduced.items(), key=lambda item: item[0])
    records = [defect_record(key, value, rows) for key, value in ordered]
    first = records[0]
    first_expression = ordered[0][1]
    point = {engine.rods.X[0]: sp.Rational(3, 5), engine.rods.X[1]: sp.Rational(4, 5), engine.rods.X[2]: 0, engine.rods.X[3]: 0}
    point_value = engine.background_reduce_expr(first_expression.subs(point))
    if point_value == 0:
        raise AssertionError("declared first-witness point unexpectedly vanishes")

    positions = sorted({(record["output_index"], record["input_index"]) for record in records})
    typed_positions = [
        {
            "output_index": row,
            "output_row_id": rows[row]["row_id"],
            "input_index": column,
            "input_row_id": rows[column]["row_id"],
        }
        for row, column in positions
    ]
    return {
        "schema": "closed-universe-berger-replacement112-executable-unary-mixed-nilpotency-obstruction-payload-v1",
        "result_id": "BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION_PAYLOAD",
        "carrier": {
            "row_count": len(rows),
            "rows": rows,
            "pairing_rank": action_payload["carrier"]["pairing_rank"],
            "pairing_entry_count": len(action_payload["carrier"]["pairing_entries"]),
        },
        "assembly": assembly,
        "exact_fixture": {
            "parameter_values": {str(symbol): str(value) for symbol, value in FIXTURE.items()},
            "unit_circle_checks": {
                "ca_squared_plus_sa_squared": str(FIXTURE[engine.CA] ** 2 + FIXTURE[engine.SA] ** 2),
                "cu_squared_plus_su_squared": str(FIXTURE[engine.CU] ** 2 + FIXTURE[engine.SU] ** 2),
            },
            "nonzero_parameter_product": str(sp.prod(FIXTURE.values())),
            "specialized_q00_summary": engine.summary(q00),
            "specialized_q10_summary": engine.summary(q10),
            "mixed_square_before_background_quotient": engine.summary(mixed_square),
        },
        "mixed_nilpotency_obstruction": {
            **quotient,
            "coefficient_identity": "q10*q00+q00*q10",
            "typed_defect_positions": typed_positions,
            "defect_entries": records,
            "first_exact_witness": first,
            "first_witness_sphere_point": {str(symbol): str(value) for symbol, value in point.items()},
            "first_witness_point_value": sp.sstr(point_value),
            "first_witness_nonzero": True,
        },
        "gate_disposition": {
            "complete_112_row_diagnostic_assembly": "CERTIFIED",
            "signed_pairing_rank_112": "CERTIFIED",
            "rod_wave_background_equations_at_fixture": "CERTIFIED",
            "mixed_epsilon_R_squared_nilpotency_at_fixture": "OBSTRUCTED",
            "complete_executable_replacement112_q1": "NO_CERTIFIED_MAP",
            "generic_parameter_nilpotency": "OPEN",
            "full_K_Berger_compatibility": "NOT_REACHED",
            "reality_and_mutation_suite": "NOT_REACHED",
            "combined_160_cohomology_memory_redshift": "NOT_REACHED",
        },
        "does_not_establish": [
            "a generic-parameter classification of every mixed-square defect",
            "a complete executable replacement-112 unary export",
            "cohomology, gauge reduction, detector response, memory, redshift or recoil",
            "a causal metric-BV propagator or any quantum observer algebra",
        ],
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    obstruction = payload["mixed_nilpotency_obstruction"]
    return {
        "schema": "closed-universe-berger-replacement112-executable-unary-mixed-nilpotency-obstruction-v1",
        "result_id": "BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION",
        "setting_id": dependencies["positive_action"]["setting_id"],
        "claim_status": "OBSTRUCTED_EXACT_NONDEGENERATE_FIXTURE_MIXED_NILPOTENCY",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": dependencies[name]["result_id"], "sha256": sha(path)}
            for name, path in DEPS.items()
        },
        "payload_ref": {
            "path": str(X.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical(payload),
        },
        "gate_results": payload["gate_disposition"],
        "first_obstruction": obstruction["first_exact_witness"],
        "next_gate": "RECONCILE_THE_H_HAT_STAR_00_FROM_SIGMA_MIXED_NOETHER_ROW_BEFORE_ANY_EXECUTABLE_EXPORT",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE diagnostic imports the certified 108-row q1, the complete positive-mixed Phi2 component map, the action-derived mixed metric--rod Hessian interface and the 112-row positive action by content hash. It assembles all four epsilon bidegrees on the frozen 112-row carrier, including the six-rod subtraction, H-weighted eight-rod addition, Diff-BV adjoints, metric Hessian delta, support rows and the two new rod/cotangent pairs. At the exact nondegenerate unit-circle fixture (sa,ca)=(3/5,4/5), (su,cu)=(5/13,12/13), the mixed coefficient q10 q00+q00 q10 has 132 nonzero Fourier-mode entries in 28 matrix positions after the declared R=B psi Berger background and sphere quotient; all eight rod wave equations vanish. The lexicographically first witness is row 27 h_hat_star_00 from column 4 sigma, empty input word and time mode -2, and remains nonzero at the exact sphere point (3/5,4/5,0,0). A single exact nonzero fixture value disproves the requested generic executable nilpotency identity. Therefore this assembly is a diagnostic obstruction, not a complete executable q1. Full K compatibility, reality mutations and downstream 160-row, cohomology, detector, memory, redshift, recoil and quantum gates are not reached. The independent verifier validates hashes, carrier typing, fixture nondegeneracy, the quotient relations and the serialized nonzero witness without importing the producer or assembly engine; it does not claim an independent full 112-row reassembly."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_replacement112_executable_unary_mixed_nilpotency_obstruction --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_replacement112_executable_unary_mixed_nilpotency_obstruction",
            "producer_source_sha256": sha(Path(__file__)),
            "assembly_engine_sha256": sha(P / "berger_replacement112_executable_unary_engine.py"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        X.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        C.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(
            "# Replacement-112 executable unary mixed-nilpotency obstruction\n\n"
            "The complete 112-row diagnostic assembly fails the exact mixed nilpotency gate at a nondegenerate unit-circle fixture. "
            "There are 132 reduced Fourier-mode defects in 28 matrix positions. The canonical first is `h_hat_star_00 <- sigma` with empty input word and time mode `-2`. "
            "The rod wave equations vanish, so this is not a failed background-wave fixture. No executable unary or downstream observer claim is promoted.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
