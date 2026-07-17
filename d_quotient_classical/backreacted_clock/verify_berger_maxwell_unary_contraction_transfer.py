#!/usr/bin/env python3
"""Independent replay of the Maxwell contraction and transferred q2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _embed, _identity_matrix, _is_zero, _matrix_add, _negative, _one,
    _sparse_multiply, _subtract, _zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import _adjoint_matrix
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q2 import (
    COMBINED_PARITIES, ETA_DIAGONAL, build_maxwell_q2_overlay,
    maxwell_unary_blocks, _scalar_operator,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    BZERO, BilinearOperator, U, U0, V, V0, _apply_output_linear,
    _fixture_bilinear, _fixture_linear, _precompose_bilinear,
    _precompose_bilinear_slot,
)


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json"
PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-maxwell-unary-contraction-transfer-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/berger-first-transferred-mixed-q2-payload-v1.schema.json"
GRAVITY = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fixture_matrix(matrix):
    return [[_fixture_linear(entry) for entry in row] for row in matrix]


def _maxwell_q1():
    blocks = maxwell_unary_blocks()
    q = _zero(10, 10)
    for mu in range(4):
        q[1 + mu][0] = blocks["gradient"][mu][0]
        q[9][5 + mu] = blocks["divergence"][0][mu]
        for nu in range(4):
            q[5 + mu][1 + nu] = blocks["hessian"][mu][nu]
    return q


def _audit_witness(certificate: dict) -> None:
    q = _maxwell_q1()
    witness = _zero(10, 10)
    for mu, eta in enumerate(ETA_DIAGONAL):
        witness[0][1 + mu] = _scalar_operator(((mu,), eta))
        witness[1 + mu][5 + mu] = _scalar_operator(((), eta))
        witness[5 + mu][9] = _scalar_operator(((mu,), -eta))
    wave = _fixture_matrix(
        _matrix_add(_sparse_multiply(q, witness), _sparse_multiply(witness, q))
    )
    canonical = {(0, 0): -sp.S.One, (1, 1): sp.S.One, (2, 2): sp.S.One, (3, 3): sp.S.One}
    for row, entries in enumerate(wave):
        for column, entry in enumerate(entries):
            principal = {word: coefficient for _, word, coefficient in entry.terms if len(word) == 2}
            if principal != (canonical if row == column else {}):
                raise AssertionError(f"independent Maxwell principal defect at {row},{column}")
    if not _is_zero(
        _fixture_matrix(
            _subtract(_sparse_multiply(q, wave), _sparse_multiply(wave, q))
        )
    ):
        raise AssertionError("independent q-wave commutator failed")
    if not _is_zero(_subtract(_adjoint_matrix([[wave[0][0]]]), [[wave[9][9]]])):
        raise AssertionError("independent ghost/identity adjoint check failed")
    if not _is_zero(
        _subtract(_adjoint_matrix([row[1:5] for row in wave[1:5]]), [row[5:9] for row in wave[5:9]])
    ):
        raise AssertionError("independent field/antifield adjoint check failed")
    record = certificate["maxwell_unary_contraction"]
    if record["principal_symbol"] != "g^{mu nu} zeta_mu zeta_nu I10":
        raise AssertionError("declared Maxwell symbol drifted")


def _combined_maps():
    gravity = json.loads(GRAVITY.read_text())
    q54 = _matrix_from_record(gravity["classical_unary_q1"]["matrix"])
    i54 = _matrix_from_record(gravity["contraction"]["iota_cl"])
    p54 = _matrix_from_record(gravity["contraction"]["pi_cl"])
    q64 = _zero(64, 64)
    i64 = _zero(64, 36)
    p64 = _zero(36, 64)
    _embed(q64, q54, 0, 0)
    _embed(q64, _maxwell_q1(), 54, 54)
    _embed(i64, i54, 0, 0)
    _embed(p64, p54, 0, 0)
    for index in range(10):
        i64[54 + index][26 + index] = _one()
        p64[26 + index][54 + index] = _one()
    if not _is_zero(_subtract(_sparse_multiply(p64, i64), _identity_matrix(36))):
        raise AssertionError("independent combined pi-iota check failed")
    q36 = _fixture_matrix(_sparse_multiply(_sparse_multiply(p64, q64), i64))
    return i64, p64, q36


def _parse_payload_rows(payload: dict) -> list[BilinearOperator]:
    rows = []
    if [entry["output"] for entry in payload["rows"]] != list(range(36)):
        raise AssertionError("transferred output ordering drifted")
    for entry in payload["rows"]:
        body = {"output": entry["output"], "terms": entry["terms"]}
        if _digest(body) != entry["canonical_sha256"]:
            raise AssertionError(f"row digest mismatch: {entry['output']}")
        rows.append(
            BilinearOperator.from_terms(
                (
                    left,
                    tuple(left_word),
                    right,
                    tuple(right_word),
                    sp.sympify(coefficient, locals={"u": U, "v": V}),
                )
                for left, left_word, right, right_word, coefficient in entry["terms"]
            )
        )
    canonical_body = dict(payload)
    expected = canonical_body.pop("canonical_sha256")
    if _digest(canonical_body) != expected:
        raise AssertionError("payload canonical digest mismatch")
    return rows


def _replay_transfer(certificate: dict, payload: dict) -> None:
    i64, p64, q36 = _combined_maps()
    pulled = [
        _precompose_bilinear(operator, i64) if operator.terms else operator
        for operator in build_maxwell_q2_overlay()
    ]
    replay = []
    for output in range(36):
        terms = []
        for old_output in range(64):
            if p64[output][old_output].terms and pulled[old_output].terms:
                terms.extend(_apply_output_linear(p64[output][old_output], pulled[old_output]).terms)
        replay.append(_fixture_bilinear(BilinearOperator.from_terms(terms)))
    frozen = _parse_payload_rows(payload)
    if replay != frozen:
        raise AssertionError("independent transferred q2 replay differs from payload")
    layout = json.loads(LAYOUT.read_text())
    parities = tuple(row["degree"] % 2 for row in layout["component_rows"]) + COMBINED_PARITIES[54:]
    for target, operator in enumerate(replay):
        defect = BZERO
        for middle, outer in enumerate(q36[target]):
            if outer.terms and replay[middle].terms:
                defect = defect + _apply_output_linear(outer, replay[middle])
        if operator.terms:
            defect = defect + _precompose_bilinear_slot(operator, q36, slot=0, parities=parities)
            defect = defect + _precompose_bilinear_slot(
                operator, q36, slot=1, parities=parities, second_slot_q1_sign=True
            )
        if _fixture_bilinear(defect).terms:
            raise AssertionError(f"independent endpoint q1/q2 defect at row {target}")
    terms = sum(len(operator.terms) for operator in replay)
    mixed = sum(
        1 for operator in replay for left, _, right, _, _ in operator.terms
        if (left < 26) != (right < 26)
    )
    if terms != 1474 or mixed != certificate["first_transferred_mixed_vertex"]["mixed_gravity_Maxwell_input_term_count"]:
        raise AssertionError("independent transferred term ledger failed")


def _audit_cyclicity_repair_boundary(certificate: dict) -> None:
    dependency = certificate["dependency_refs"]["independent_cyclicity_audit"]
    audit = json.loads((ROOT / dependency["path"]).read_text())
    transfer = certificate["first_transferred_mixed_vertex"]
    if audit["claim_flags"]["EXACT_CYCLICITY_OBSTRUCTION_WITNESS"] is not True:
        raise AssertionError("historical obstruction dependency is unavailable")
    if transfer["historical_obstruction_dependency"] != audit["result_id"]:
        raise AssertionError("historical obstruction identity drifted")
    if transfer["full_64_cyclicity_defect_count"] or transfer["retained_36_cyclicity_defect_count"]:
        raise AssertionError("repaired cyclicity count is nonzero")
    if certificate["flags"]["BERGER_MIXED_Q2_CYCLICITY"] is not True:
        raise AssertionError("repaired cyclicity was not promoted classically")
    if certificate["flags"]["BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING"] is not True:
        raise AssertionError("repaired mixed dressing was not promoted classically")


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator.check_schema(payload_schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    jsonschema.Draft202012Validator(payload_schema).validate(payload)
    if _sha256(PAYLOAD) != certificate["first_transferred_mixed_vertex"]["payload_file_sha256"]:
        raise AssertionError("transferred payload file hash mismatch")
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {dependency['path']}")
    _audit_witness(certificate)
    _replay_transfer(certificate, payload)
    _audit_cyclicity_repair_boundary(certificate)
    print("BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
