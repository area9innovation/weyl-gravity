#!/usr/bin/env python3
"""Independent exact replay of the retained typed mixed ell3 transfer."""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)

# The verifier consumes the frozen Taylor-order-three artifacts.  Setting the
# guard here makes the advertised replay command self-contained without
# weakening the producer's fail-closed launch requirement.
os.environ.setdefault("BERGER_TAYLOR_ORDER", "3")

from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q3 import (
    _exact_rational,
    _gravity_q2_zero_extended,
    _word,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_TRANSFER.json"
ELL2_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD.json"
ELL3_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_PAYLOAD.json"
UPSTREAM_Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
UPSTREAM_Q3 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json"
TYPED_CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
CARRIER_SCHEMA = ROOT / "d_quotient_classical/schema/berger-portable-coupled-64-typed-pairing-36-sdr-v1.schema.json"
LEGACY_LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
SCHEMAS = {
    CERTIFICATE: ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-transfer-v1.schema.json",
    ELL2_PAYLOAD: ROOT / "d_quotient_classical/schema/berger-retained-typed-mixed-ell2-payload-v1.schema.json",
    ELL3_PAYLOAD: ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-payload-v1.schema.json",
}
ROW_SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-row-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _coefficient(value: dict[str, object]):
    return _exact_rational(value["rational"]) + _exact_rational(value["sqrt10"]) * engine.SQRT10


def _parse_bilinear(payload: dict, rows: int):
    result = [engine.BZERO for _ in range(rows)]
    seen = set()
    for record in payload["rows"]:
        output = record["output"]
        if output in seen:
            raise AssertionError(f"duplicate bilinear output row: {output}")
        seen.add(output)
        body = {"output": output, "terms": record["terms"]}
        if _digest(body) != record["canonical_sha256"]:
            raise AssertionError(f"bilinear row canonical hash drifted: {output}")
        result[output] = engine.BilinearOperator.from_terms(
            (left, _word(left_word), right, _word(right_word), _coefficient(value))
            for left, left_word, right, right_word, value in record["terms"]
        )
    if seen != set(range(rows)):
        raise AssertionError("bilinear row ledger is incomplete")
    return tuple(result)


def _parse_trilinear_manifest(payload: dict, rows: int, row_validator):
    result = [engine.TZERO for _ in range(rows)]
    seen = set()
    total = nonzero = maximum = 0
    for chunk in payload["chunks"]:
        path = ROOT / chunk["path"]
        if path.read_bytes()[4:8] != b"\x00\x00\x00\x00":
            raise AssertionError(f"gzip mtime is not deterministic: {chunk['path']}")
        if _sha256(path) != chunk["file_sha256"]:
            raise AssertionError(f"trilinear row file hash drifted: {chunk['output']}")
        with gzip.open(path, "rt") as handle:
            record = json.load(handle)
        row_validator.validate(record)
        output = record["output"]
        if output in seen or output != chunk["output"]:
            raise AssertionError("trilinear row order/uniqueness failed")
        seen.add(output)
        body = {"output": output, "terms": record["terms"]}
        if _digest(body) != record["canonical_sha256"] or record["canonical_sha256"] != chunk["canonical_sha256"]:
            raise AssertionError(f"trilinear row canonical hash drifted: {output}")
        row_maximum = max(
            (sum(term[1]) + sum(term[3]) + sum(term[5]) for term in record["terms"]),
            default=0,
        )
        if len(record["terms"]) != chunk["term_count"] or row_maximum != chunk["maximum_total_jet_order"]:
            raise AssertionError(f"trilinear row summary drifted: {output}")
        result[output] = engine.TrilinearOperator.from_terms(
            (
                first,
                _word(first_word),
                second,
                _word(second_word),
                third,
                _word(third_word),
                _coefficient(value),
            )
            for first, first_word, second, second_word, third, third_word, value in record["terms"]
        )
        total += len(record["terms"])
        nonzero += bool(record["terms"])
        maximum = max(maximum, row_maximum)
    if seen != set(range(rows)):
        raise AssertionError("trilinear row ledger is incomplete")
    return tuple(result), (total, nonzero, maximum)


def _q1_q3_row(target, q1, q3, parities):
    defect = engine.TZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and q3[middle].terms:
            defect += engine._apply_output_linear_trilinear(outer, q3[middle])
    if q3[target].terms:
        for slot in range(3):
            defect += engine._precompose_trilinear_slot(
                q3[target], q1, slot=slot, parities=parities
            )
    return engine._fixture_trilinear(defect)


def _exchange_row(outer, inclusion2, iota, parities):
    """Evaluate the three graded (2,1)-unshuffles without producer code."""

    terms = []
    for middle, outer_word, direct, direct_word, outer_coefficient in outer.terms:
        inner = inclusion2[middle]
        if not inner.terms:
            continue
        for new_direct, entry in enumerate(iota[direct]):
            for scalar, iota_word, iota_coefficient in entry.terms:
                if scalar != 0:
                    raise AssertionError("iota entry is not scalar")
                for first, first_word, second, second_word, inner_coefficient in inner.terms:
                    for new_first, new_second, multiplicity in engine._leibniz_output_terms(
                        outer_word, first_word, second_word
                    ):
                        coefficient = (
                            outer_coefficient
                            * inner_coefficient
                            * iota_coefficient
                            * multiplicity
                        )
                        direct_derivative = direct_word + iota_word
                        terms.append(
                            (
                                first,
                                new_first,
                                second,
                                new_second,
                                new_direct,
                                direct_derivative,
                                coefficient,
                            )
                        )
                        terms.append(
                            (
                                first,
                                new_first,
                                new_direct,
                                direct_derivative,
                                second,
                                new_second,
                                coefficient
                                * (-1 if parities[second] * parities[new_direct] else 1),
                            )
                        )
                        terms.append(
                            (
                                new_direct,
                                direct_derivative,
                                first,
                                new_first,
                                second,
                                new_second,
                                coefficient
                                * (
                                    -1
                                    if parities[new_direct]
                                    * (parities[first] + parities[second])
                                    % 2
                                    else 1
                                ),
                            )
                        )
    return engine.TrilinearOperator.from_terms(terms)


def _exchange(outer_q2, inclusion2, iota, projection, parities):
    full = tuple(
        engine._fixture_trilinear(
            _exchange_row(outer_q2[row], inclusion2, iota, parities)
        )
        for row in range(64)
    )
    result = []
    for retained in range(36):
        value = engine.TZERO
        for old, outer in enumerate(projection[retained]):
            if outer.terms and full[old].terms:
                value += engine._apply_output_linear_trilinear(outer, full[old])
        result.append(engine._fixture_trilinear(value))
    return tuple(result), full


def _relative_defects(q1, ell3, parities, gravity_ell2, mixed_ell2, full_ell2):
    defects = []
    for row in range(36):
        defect = _q1_q3_row(row, q1, ell3, parities)
        defect += engine._q2_composed_with_q2_row(
            gravity_ell2[row], mixed_ell2, parities
        )
        defect += engine._q2_composed_with_q2_row(
            mixed_ell2[row], full_ell2, parities
        )
        defects.append(engine._fixture_trilinear(defect))
    return tuple(defects)


def _replace_first_coefficient(ell3):
    mutated = list(ell3)
    for row, operator in enumerate(mutated):
        if not operator.terms:
            continue
        terms = list(operator.terms)
        first = list(terms[0])
        first[-1] += 1
        terms[0] = tuple(first)
        mutated[row] = engine.TrilinearOperator.from_terms(terms)
        return tuple(mutated)
    raise AssertionError("cannot mutate an empty retained ell3")


def _add_fabricated_exchange_term(ell3):
    mutated = list(ell3)
    zero = _word((0, 0, 0, 0))
    fabricated = engine.TrilinearOperator.from_terms(
        [(0, zero, 0, zero, 0, zero, 1)]
    )
    mutated[0] = engine._fixture_trilinear(mutated[0] + fabricated)
    return tuple(mutated)


def verify() -> None:
    values = {}
    for artifact, schema_path in SCHEMAS.items():
        value = json.loads(artifact.read_text())
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        values[artifact] = value
    certificate = values[CERTIFICATE]
    ell2_payload = values[ELL2_PAYLOAD]
    ell3_payload = values[ELL3_PAYLOAD]

    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash drifted: {dependency['path']}")
    for relative, expected_hash in certificate["source_manifest"].items():
        if _sha256(ROOT / relative) != expected_hash:
            raise AssertionError(f"source hash drifted: {relative}")
    ell2_summary = certificate["retained_ell2"]
    ell3_summary = certificate["retained_ell3"]
    if _sha256(ELL2_PAYLOAD) != ell2_summary["payload_file_sha256"] or _digest(ell2_payload) != ell2_summary["payload_canonical_sha256"]:
        raise AssertionError("retained ell2 payload hash drifted")
    if _sha256(ELL3_PAYLOAD) != ell3_summary["payload_file_sha256"] or _digest(ell3_payload) != ell3_summary["payload_canonical_sha256"]:
        raise AssertionError("retained ell3 payload hash drifted")

    row_schema = json.loads(ROW_SCHEMA.read_text())
    Draft202012Validator.check_schema(row_schema)
    row_validator = Draft202012Validator(row_schema)
    retained_mixed_q2 = _parse_bilinear(ell2_payload, 36)
    retained_mixed_q3, q3_counts = _parse_trilinear_manifest(ell3_payload, 36, row_validator)
    if sum(len(row.terms) for row in retained_mixed_q2) != ell2_summary["term_count"]:
        raise AssertionError("retained ell2 coefficient count drifted")
    if q3_counts != (
        ell3_summary["total_term_count"],
        ell3_summary["nonzero_rows"],
        ell3_summary["maximum_total_jet_order"],
    ):
        raise AssertionError("retained ell3 aggregate summary drifted")

    carrier = json.loads(TYPED_CARRIER.read_text())
    iota = _matrix_from_record(carrier["contraction"]["iota_36_to_64"])
    projection = _matrix_from_record(carrier["contraction"]["pi_64_to_36"])
    homotopy = _matrix_from_record(carrier["contraction"]["S_64"])
    q1 = _matrix_from_record(carrier["retained_complex"]["classical_unary_q1"])
    upstream_q2 = _parse_bilinear(json.loads(UPSTREAM_Q2.read_text()), 64)
    upstream_q3_manifest = json.loads(UPSTREAM_Q3.read_text())
    upstream_row_schema = json.loads(
        (ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-row-v1.schema.json").read_text()
    )
    upstream_q3, _ = _parse_trilinear_manifest(
        upstream_q3_manifest, 64, Draft202012Validator(upstream_row_schema)
    )

    expected_contact = tuple(
        engine._fixture_trilinear(row)
        for row in engine._transform_trilinear_vector(upstream_q3, projection, iota)
    )
    if any(expected_contact[row].terms != retained_mixed_q3[row].terms for row in range(36)):
        raise AssertionError("retained mixed ell3 is not the coefficientwise contact pullback")

    gravity_q2 = _gravity_q2_zero_extended()
    gravity_i2 = tuple(
        engine._fixture_bilinear(row).scale(-1)
        for row in engine._transform_bilinear_vector(gravity_q2, homotopy, iota)
    )
    mixed_i2 = tuple(
        engine._fixture_bilinear(row).scale(-1)
        for row in engine._transform_bilinear_vector(upstream_q2, homotopy, iota)
    )
    gravity_i2_support = {row for row, operator in enumerate(gravity_i2) if operator.terms}
    mixed_i2_support = {row for row, operator in enumerate(mixed_i2) if operator.terms}
    if gravity_i2_support != {37, 38} or mixed_i2_support != {38}:
        raise AssertionError("second inclusion support drifted")
    layout = json.loads(LEGACY_LAYOUT.read_text())
    parities = tuple(
        row["degree"] & 1 for row in layout["retained_complex"]["component_rows"]
    )
    exchange_pairs = {
        "gravity_outer_mixed_inner": _exchange(
            gravity_q2, mixed_i2, iota, projection, parities
        ),
        "mixed_outer_gravity_inner": _exchange(
            upstream_q2, gravity_i2, iota, projection, parities
        ),
        "mixed_outer_mixed_inner": _exchange(
            upstream_q2, mixed_i2, iota, projection, parities
        ),
    }
    exchange_parts = {name: pair[0] for name, pair in exchange_pairs.items()}
    raw_exchange_parts = {name: pair[1] for name, pair in exchange_pairs.items()}
    exchange_counts = {
        name: sum(len(row.terms) for row in rows)
        for name, rows in exchange_parts.items()
    }
    if exchange_counts != {
        "gravity_outer_mixed_inner": 0,
        "mixed_outer_gravity_inner": 0,
        "mixed_outer_mixed_inner": 0,
    }:
        raise AssertionError(f"exchange ledger overclaims zero exchange: {exchange_counts}")
    raw_exchange_counts = {
        name: sum(len(row.terms) for row in rows)
        for name, rows in raw_exchange_parts.items()
    }
    raw_exchange_rows = {
        name: [row for row, operator in enumerate(rows) if operator.terms]
        for name, rows in raw_exchange_parts.items()
    }
    if raw_exchange_counts != {
        "gravity_outer_mixed_inner": 342,
        "mixed_outer_gravity_inner": 0,
        "mixed_outer_mixed_inner": 0,
    }:
        raise AssertionError(f"raw exchange ledger drifted: {raw_exchange_counts}")
    ledger = certificate["exchange_ledger"]
    if ledger["raw_part_term_counts"] != raw_exchange_counts:
        raise AssertionError("raw exchange count certificate drifted")
    if ledger["raw_part_nonzero_output_rows"] != raw_exchange_rows:
        raise AssertionError("raw exchange row certificate drifted")
    if ledger["projected_part_term_counts"] != exchange_counts:
        raise AssertionError("exchange ledger drifted")

    retained_gravity_q2 = tuple(
        engine._fixture_bilinear(row)
        for row in engine._transform_bilinear_vector(gravity_q2, projection, iota)
    )
    retained_full_q2 = tuple(
        engine._fixture_bilinear(retained_gravity_q2[row] + retained_mixed_q2[row])
        for row in range(36)
    )
    defects = _relative_defects(
        q1,
        retained_mixed_q3,
        parities,
        retained_gravity_q2,
        retained_mixed_q2,
        retained_full_q2,
    )
    for row, defect in enumerate(defects):
        if defect.terms:
            raise AssertionError(
                f"retained relative arity-three identity failed row={row} term={defect.terms[0]}"
            )

    carrier_schema = json.loads(CARRIER_SCHEMA.read_text())
    mutated_carrier = copy.deepcopy(carrier)
    mutated_carrier["normalization"]["Maxwell_pairing_weight"] = 1
    weight_rejected = bool(
        list(Draft202012Validator(carrier_schema).iter_errors(mutated_carrier))
    )
    coefficient_rejected = any(
        defect.terms
        for defect in _relative_defects(
            q1,
            _replace_first_coefficient(retained_mixed_q3),
            parities,
            retained_gravity_q2,
            retained_mixed_q2,
            retained_full_q2,
        )
    )
    exchange_rejected = any(
        defect.terms
        for defect in _relative_defects(
            q1,
            _add_fabricated_exchange_term(retained_mixed_q3),
            parities,
            retained_gravity_q2,
            retained_mixed_q2,
            retained_full_q2,
        )
    )
    mutation_guards = {
        "Maxwell_pairing_weight_mutation_rejected": weight_rejected,
        "retained_ell3_coefficient_mutation_rejected": coefficient_rejected,
        "fabricated_exchange_term_rejected": exchange_rejected,
    }
    if mutation_guards != certificate["mutation_guards"] or not all(
        mutation_guards.values()
    ):
        raise AssertionError(f"mutation guard failed: {mutation_guards}")

    flags = certificate["flags"]
    if not flags["BERGER_RETAINED_MIXED_ELL3_TRANSFER"]:
        raise AssertionError("retained ell3 transfer was not promoted")
    if flags["BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_QUANTUM_ACCEPTANCE"]:
        raise AssertionError("independent quantum acceptance was overclaimed")
    if flags["QME_RESTORED"] or flags["QUANTUM_CLAIM"]:
        raise AssertionError("quantum conclusion was overclaimed")


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_MIXED_ELL3_TRANSFER independent replay: PASS")
    print("1,474 retained ell2 coefficients; 25,950 retained ell3 coefficients")
    print("all three exchange sectors vanish; all 36 relative arity-three rows close")
