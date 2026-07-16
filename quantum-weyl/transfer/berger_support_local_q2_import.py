"""Pinned independent import of the complete Berger support-local q2 payload."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import sympy as sp

TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))

try:
    from . import berger_54_row_q2_arrival as arrival
except ImportError:
    import berger_54_row_q2_arrival as arrival


CLASSICAL_COMMIT = "7b352307eb2adb0dfb8e76b7d24f0bb94a37cc8d"
CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
PAYLOAD_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
)
CERTIFICATE_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-support-local-q2-v1.schema.json"
)
PAYLOAD_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-support-local-q2-payload-v1.schema.json"
)
PRODUCER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/berger_support_local_q2.py"
)
EXPORTER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/berger_support_local_q2_export.py"
)
VERIFIER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/verify_berger_support_local_q2_independent.py"
)
TEST_RELATIVE = (
    "d_quotient_classical/backreacted_clock/tests/test_berger_support_local_q2.py"
)
REPORT_RELATIVE = "d_quotient_classical/reports/berger-support-local-q2.md"
GAUGE_FIXED_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
)
D_RELATIVE = "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"

SQRT10 = sp.sqrt(10)
SPECIALIZATION = {
    arrival.ALPHA_B: sp.Integer(5),
    arrival.U: 3 * SQRT10 / 20,
    arrival.V: 2 * SQRT10 / 3,
}


def _git_prefix() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


@lru_cache(maxsize=None)
def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned support-local q2 artifact: {relative}")
    return result.stdout


@lru_cache(maxsize=None)
def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned support-local q2 JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: object, *, name: str) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if (
        isinstance(value, dict)
        and set(value) == {"numerator", "denominator"}
        and type(value["numerator"]) is int
        and type(value["denominator"]) is int
        and value["denominator"] != 0
    ):
        return Fraction(value["numerator"], value["denominator"])
    raise ValueError(f"{name} is not an exact rational")


def _quadratic_pair(value: object) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict) or set(value) != {"rational", "sqrt10"}:
        raise ValueError("q2 coefficient escaped the declared quadratic field")
    return (
        _fraction(value["rational"], name="rational coefficient"),
        _fraction(value["sqrt10"], name="sqrt10 coefficient"),
    )


def _expression(value: tuple[Fraction, Fraction]) -> sp.Expr:
    rational, radical = value
    return sp.Rational(rational.numerator, rational.denominator) + sp.Rational(
        radical.numerator, radical.denominator
    ) * SQRT10


def _exponents(value: object, *, name: str) -> tuple[int, int, int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 4
        or any(type(item) is not int or item < 0 for item in value)
    ):
        raise ValueError(f"{name} is not a four-axis PBW multiindex")
    return tuple(value)  # type: ignore[return-value]


@dataclass(frozen=True)
class ImportedBergerSupportLocalQ2:
    parsed: arrival.ParsedBergerQ2
    certificate_sha256: str
    payload_file_sha256: str
    payload_canonical_sha256: str
    nonzero_rows: int
    coefficient_field: str
    specialization: dict[sp.Symbol, sp.Expr]


def _validate_schema_identities(
    certificate_schema: dict[str, Any], payload_schema: dict[str, Any]
) -> None:
    if (
        certificate_schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or certificate_schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-support-local-q2-v1.json"
        or certificate_schema.get("additionalProperties") is not False
        or payload_schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or payload_schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-support-local-q2-payload-v1.json"
        or payload_schema.get("additionalProperties") is not False
    ):
        raise ValueError("pinned support-local q2 schema identity drifted")


@lru_cache(maxsize=1)
def import_support_local_q2() -> ImportedBergerSupportLocalQ2:
    certificate = _git_json(CERTIFICATE_RELATIVE)
    payload = _git_json(PAYLOAD_RELATIVE)
    certificate_schema = _git_json(CERTIFICATE_SCHEMA_RELATIVE)
    payload_schema = _git_json(PAYLOAD_SCHEMA_RELATIVE)
    gauge_fixed = _git_json(GAUGE_FIXED_RELATIVE)
    d_action = _git_json(D_RELATIVE)
    _validate_schema_identities(certificate_schema, payload_schema)

    if (
        certificate.get("schema") != "pure-weyl-berger-support-local-q2-v1"
        or certificate.get("result_id") != "BERGER_SUPPORT_LOCAL_Q2"
        or certificate.get("setting_id") != arrival.SETTING_ID
        or certificate.get("claim_status")
        != "CERTIFIED_COMPLETE_SUPPORT_LOCAL_CLASSICAL_Q2"
        or certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("pinned support-local q2 theorem identity drifted")
    if (
        payload.get("schema")
        != "pure-weyl-berger-support-local-q2-payload-v1"
        or payload.get("coefficient_field") != "Q(sqrt(10))"
        or payload.get("shape") != [54, 54, 54]
        or payload.get("factorial_convention") != arrival.CONVENTION
        or payload.get("pbw_basis")
        != "left-invariant Berger frame; words e0^n0 e1^n1 e2^n2 e3^n3"
    ):
        raise ValueError("pinned support-local q2 payload identity drifted")

    dependency = certificate.get("dependency_refs", {})
    expected_dependencies = {
        "gauge_fixed_classical_unary_q1": {
            "result_id": "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
            "sha256": hashlib.sha256(_git_blob(GAUGE_FIXED_RELATIVE)).hexdigest(),
        },
        "local_D_action": {
            "result_id": "BERGER_54_ROW_LOCAL_D_ACTION",
            "sha256": hashlib.sha256(_git_blob(D_RELATIVE)).hexdigest(),
        },
    }
    if dependency != expected_dependencies:
        raise ValueError("pinned support-local q2 dependency binding drifted")
    unary_import, d_import, authoritative_unary = arrival.load_prerequisites()
    arrival_dependencies = arrival.expected_dependency_refs(unary_import, d_import)
    if (
        arrival_dependencies["gauge_fixed_54_row"]["certificate_sha256"]
        != expected_dependencies["gauge_fixed_classical_unary_q1"]["sha256"]
        or arrival_dependencies["local_D_54_row"]["certificate_sha256"]
        != expected_dependencies["local_D_action"]["sha256"]
    ):
        raise ValueError("q2 dependencies do not match the frozen quantum imports")

    summary = certificate.get("classical_binary_q2", {})
    payload_file_hash = hashlib.sha256(_git_blob(PAYLOAD_RELATIVE)).hexdigest()
    payload_canonical_hash = _canonical_hash(payload)
    if (
        summary.get("payload_path") != PAYLOAD_RELATIVE
        or summary.get("payload_file_sha256") != payload_file_hash
        or summary.get("payload_canonical_sha256") != payload_canonical_hash
        or summary.get("total_rows") != 54
        or summary.get("support_local") is not True
        or summary.get("Taylor_convention") != arrival.CONVENTION
    ):
        raise ValueError("pinned support-local q2 payload hash ledger drifted")

    authoritative_rows = authoritative_unary["row_layout"]["component_rows"]
    rows = certificate.get("row_layout", {}).get("component_rows")
    degrees = tuple(row["degree"] for row in authoritative_rows)
    parities = certificate.get("row_layout", {}).get("parities")
    if (
        rows != authoritative_rows
        or parities != [degree & 1 for degree in degrees]
        or certificate.get("row_layout", {}).get("total_rows") != 54
        or certificate.get("row_layout", {}).get("all_rows_ledgered") is not True
    ):
        raise ValueError("support-local q2 row layout or parity bridge drifted")

    payload_rows = payload.get("rows")
    if not isinstance(payload_rows, list) or len(payload_rows) != 54:
        raise ValueError("support-local q2 output-row ledger drifted")
    entries: list[arrival.PBWBilinearEntry] = []
    term_count = 0
    nonzero_rows = 0
    maximum_order = 0
    for expected_output, row in enumerate(payload_rows):
        if (
            not isinstance(row, dict)
            or set(row) != {"output", "terms"}
            or row["output"] != expected_output
            or not isinstance(row["terms"], list)
        ):
            raise ValueError("support-local q2 rows are not canonical")
        raw_table: dict[
            tuple[int, tuple[int, ...], int, tuple[int, ...]],
            tuple[Fraction, Fraction],
        ] = {}
        grouped: dict[tuple[int, int], list[arrival.PBWBilinearTerm]] = defaultdict(list)
        previous: tuple[int, tuple[int, ...], int, tuple[int, ...]] | None = None
        for raw_term in row["terms"]:
            if not isinstance(raw_term, list) or len(raw_term) != 5:
                raise ValueError("support-local q2 term record drifted")
            left, raw_left_word, right, raw_right_word, raw_coefficient = raw_term
            if (
                type(left) is not int
                or type(right) is not int
                or not 0 <= left < 54
                or not 0 <= right < 54
            ):
                raise ValueError("support-local q2 input index drifted")
            left_word = _exponents(raw_left_word, name="left PBW word")
            right_word = _exponents(raw_right_word, name="right PBW word")
            key = (left, left_word, right, right_word)
            if previous is not None and key <= previous:
                raise ValueError("support-local q2 PBW records are not strictly ordered")
            coefficient_pair = _quadratic_pair(raw_coefficient)
            if coefficient_pair == (Fraction(0), Fraction(0)):
                raise ValueError("support-local q2 retains an explicit zero")
            if degrees[expected_output] != degrees[left] + degrees[right] + 1:
                raise ValueError("support-local q2 violates cohomological degree one")
            raw_table[key] = coefficient_pair
            grouped[(left, right)].append(
                arrival.PBWBilinearTerm(
                    left_word, right_word, _expression(coefficient_pair)
                )
            )
            order = sum(left_word) + sum(right_word)
            maximum_order = max(maximum_order, order)
            term_count += 1
            previous = key
        for (left, left_word, right, right_word), coefficient in raw_table.items():
            sign = -1 if parities[left] * parities[right] else 1
            expected = (sign * coefficient[0], sign * coefficient[1])
            if raw_table.get((right, right_word, left, left_word)) != expected:
                raise ValueError("support-local q2 graded Koszul symmetry failed")
        for (left, right), terms in sorted(grouped.items()):
            entries.append(
                arrival.PBWBilinearEntry(
                    expected_output, left, right, tuple(terms)
                )
            )
        nonzero_rows += bool(row["terms"])

    if (
        term_count != summary.get("term_count")
        or nonzero_rows != summary.get("nonzero_rows")
        or maximum_order != summary.get("maximum_total_jet_order")
        or summary.get("maximum_total_jet_order") != 6
    ):
        raise ValueError("support-local q2 exact statistics drifted")
    checks = certificate.get("exact_checks")
    flags = certificate.get("flags")
    if (
        not isinstance(checks, dict)
        or set(checks)
        != {
            "q2_koszul_symmetry_raw_34_rows",
            "q1_q2_arity_two_nilpotency_raw_coefficientwise",
            "canonical_clock_transport_preserves_L_infinity_identity",
            "canonical_gauge_fermion_transport_preserves_L_infinity_identity",
            "q2_koszul_symmetry_gauge_fixed_54_rows",
            "D_q2_derivation_termwise",
            "BV_cyclicity_q2_coefficientwise_and_by_canonical_transport",
            "all_54_output_rows_ledgered",
        }
        or any(value is not True for value in checks.values())
        or flags.get("CLASSICAL_SUPPORT_LOCAL_Q2") is not True
        or flags.get("CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT") is not True
        or flags.get("BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO") is not True
        or flags.get("BERGER_ARITY_TWO_D_CARTAN_FULL_4D") is not False
    ):
        raise ValueError("support-local q2 proof ledger or boundary drifted")

    parsed = arrival.ParsedBergerQ2(
        classical_commit=CLASSICAL_COMMIT,
        row_ids=tuple(row["row_id"] for row in authoritative_rows),
        degrees=degrees,
        maximum_total_jet_order=maximum_order,
        entries=tuple(entries),
        q2_sha256=payload_canonical_hash,
        term_count=term_count,
    )
    return ImportedBergerSupportLocalQ2(
        parsed=parsed,
        certificate_sha256=hashlib.sha256(_git_blob(CERTIFICATE_RELATIVE)).hexdigest(),
        payload_file_sha256=payload_file_hash,
        payload_canonical_sha256=payload_canonical_hash,
        nonzero_rows=nonzero_rows,
        coefficient_field="Q(sqrt(10))",
        specialization=SPECIALIZATION,
    )


def build_import_payload() -> dict[str, Any]:
    imported = import_support_local_q2()
    parsed = imported.parsed
    return {
        "schema": "quantum-weyl-berger-support-local-q2-import-v1",
        "result_id": "BERGER_SUPPORT_LOCAL_Q2_IMPORT",
        "result_state": "COMPLETE_SUPPORT_LOCAL_Q2_IMPORTED_SCIENTIFIC_REPLAY_PENDING",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": arrival.SETTING_ID,
        "classical_result": {
            "result_id": "BERGER_SUPPORT_LOCAL_Q2",
            "commit": CLASSICAL_COMMIT,
            "certificate_sha256": imported.certificate_sha256,
            "payload_file_sha256": imported.payload_file_sha256,
            "payload_canonical_sha256": imported.payload_canonical_sha256,
        },
        "coverage": {
            "total_rows": 54,
            "nonzero_output_rows": imported.nonzero_rows,
            "term_count": parsed.term_count,
            "maximum_total_jet_order": parsed.maximum_total_jet_order,
            "coefficient_field": imported.coefficient_field,
            "specialization": {
                str(symbol): sp.sstr(value)
                for symbol, value in sorted(
                    imported.specialization.items(), key=lambda item: str(item[0])
                )
            },
        },
        "independent_checks": {
            "strict_classical_schema_identities": True,
            "pinned_classical_artifacts": True,
            "dependency_hashes_match_frozen_quantum_imports": True,
            "payload_file_hash": True,
            "payload_canonical_hash": True,
            "all_54_rows_match_authoritative_layout": True,
            "cohomological_degree_one": True,
            "quadratic_field_exactness": True,
            "PBW_record_order_and_jet_bound": True,
            "graded_Koszul_symmetry": True,
            "row_and_term_statistics": True,
        },
        "scientific_replay_gate": {
            "q1_q2_replayed": False,
            "D_q2_replayed": False,
            "BV_cyclicity_replayed": False,
            "status": "REPLAY_PENDING",
        },
        "claim_flags": {
            "CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED": True,
            "SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED": False,
            "TRANSFERRED_ELL2_COMPUTED": False,
            "INTERACTING_CARTAN_VERDICT": False,
            "QUANTUM_CLAIM": False,
        },
        "provenance": {
            name: _artifact(relative)
            for name, relative in (
                ("classical_certificate", CERTIFICATE_RELATIVE),
                ("classical_payload", PAYLOAD_RELATIVE),
                ("classical_certificate_schema", CERTIFICATE_SCHEMA_RELATIVE),
                ("classical_payload_schema", PAYLOAD_SCHEMA_RELATIVE),
                ("classical_geometry_producer", PRODUCER_RELATIVE),
                ("classical_exporter", EXPORTER_RELATIVE),
                ("classical_independent_verifier", VERIFIER_RELATIVE),
                ("classical_test", TEST_RELATIVE),
                ("classical_report", REPORT_RELATIVE),
            )
        },
        "next_gate": "INDEPENDENT_EXACT_Q1_Q2_D_Q2_AND_BV_CYCLICITY_REPLAY",
        "claim_boundary": "This pinned LOCAL-ALGEBRAIC consumer independently validates and imports the complete 150305-term support-local classical q2 payload over Q(sqrt(10)), including its exact row, grading, PBW, hash, and Koszul structure. The producer's arity-two proof ledger is retained as provenance but the quantum consumer has not yet independently replayed q1/q2, D/q2, or BV cyclicity; no transfer, Cartan, causal, anomaly, QME, or quantum claim is authorized.",
    }

