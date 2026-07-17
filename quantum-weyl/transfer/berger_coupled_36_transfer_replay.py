"""Independent quantum-side replay of the first coupled Berger transfer.

The consumer reads every classical object from the pinned Git commit.  It
does not execute a classical producer.  The portable 64/36 unary, pairing,
and SDR records are parsed into the quantum exact PBW backend; the 1,954-term
Maxwell q2 overlay is then transferred again and compared coefficientwise
with the classical 1,522-term retained payload.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

from local_bv.schema_validation import validate_instance
import sympy as sp

from . import berger_qsqrt10_replay as q10
from .berger_coupled_64_q2_import import _coefficient
from .berger_retained_26_q2_transfer import (
    _cyclicity_defect,
    _transfer_inner,
    _transfer_outer,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "744383f2a21a05a1464f3a25b6569e2b001b4f20"
CARRIER_RELATIVE = (
    "d_quotient_classical/certificates/"
    "BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
)
CARRIER_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/"
    "berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json"
)
COUPLED_Q2_RELATIVE = (
    "d_quotient_classical/certificates/"
    "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json"
)
TRANSFER_CERTIFICATE_RELATIVE = (
    "d_quotient_classical/certificates/"
    "BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json"
)
TRANSFER_PAYLOAD_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD.json"
)
TRANSFER_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-maxwell-unary-contraction-transfer-v1.schema.json"
)
TRANSFER_PAYLOAD_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-first-transferred-mixed-q2-payload-v1.schema.json"
)


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


@lru_cache(maxsize=None)
def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned classical transfer artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _strict_validate(instance: dict, schema: dict, name: str) -> None:
    errors = validate_instance(instance, schema)
    if errors:
        raise ValueError(f"{name} strict schema failure: " + "; ".join(errors))


_Q10_CHARACTERS = re.compile(r"[0-9A-Za-z_+\-*/() ]+")
_Q10_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _q10_string(raw: object) -> q10.Q10:
    if (
        not isinstance(raw, str)
        or not raw
        or _Q10_CHARACTERS.fullmatch(raw) is None
        or set(_Q10_TOKEN.findall(raw)) - {"sqrt"}
    ):
        raise ValueError("operator coefficient escaped exact Q(sqrt(10)) syntax")
    expression = sp.sympify(raw, locals={"sqrt": sp.sqrt})
    if expression.atoms(sp.Float) or expression.free_symbols:
        raise ValueError("operator coefficient is not exact in Q(sqrt(10))")
    return q10.qfrom_expr(expression)


def _parse_operator(
    record: Mapping[str, Any], *, shape: tuple[int, int], name: str
) -> dict[q10.LinearKey, q10.Q10]:
    if record.get("shape") != list(shape) or not isinstance(record.get("entries"), list):
        raise ValueError(f"{name} shape drifted")
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record.get("sha256") != _canonical_hash(body):
        raise ValueError(f"{name} record hash drifted")
    output: dict[tuple[Any, ...], q10.Q10] = {}
    previous = None
    for target, source, terms in record["entries"]:
        if previous is not None and (target, source) <= previous:
            raise ValueError(f"{name} entries are not strictly ordered")
        for exponents, raw in terms:
            coefficient = _q10_string(raw)
            for word, pbw_coefficient in q10.pbw_word(q10._word(exponents)):
                q10._add(
                    output,
                    (target, source, word),
                    q10.qmul(coefficient, pbw_coefficient),
                )
        previous = target, source
    return output  # type: ignore[return-value]


def _parse_overlay(payload: Mapping[str, Any]) -> dict[q10.BilinearKey, q10.Q10]:
    if payload.get("shape") != [64, 64, 64] or payload.get("coefficient_field") != "Q(sqrt(10))":
        raise ValueError("coupled q2 overlay identity drifted")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 64:
        raise ValueError("coupled q2 overlay row ledger drifted")
    output: dict[tuple[Any, ...], q10.Q10] = {}
    for target, row in enumerate(rows):
        body = {"output": target, "terms": row.get("terms")}
        if row.get("output") != target or row.get("canonical_sha256") != _canonical_hash(body):
            raise ValueError(f"coupled q2 overlay row hash drifted: {target}")
        for left, left_raw, right, right_raw, coefficient_raw in row["terms"]:
            coefficient = _coefficient(coefficient_raw)
            for left_word, left_pbw in q10.pbw_word(q10._word(left_raw)):
                for right_word, right_pbw in q10.pbw_word(q10._word(right_raw)):
                    q10._add(
                        output,
                        (target, left, right, left_word, right_word),
                        q10.qmul(coefficient, q10.qmul(left_pbw, right_pbw)),
                    )
    return output  # type: ignore[return-value]


def _parse_transferred(payload: Mapping[str, Any]) -> dict[q10.BilinearKey, q10.Q10]:
    if (
        payload.get("result_id") != "BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD"
        or payload.get("shape") != [36, 36, 36]
        or payload.get("coefficient_field") != "Q(sqrt(10))"
    ):
        raise ValueError("transferred q2 payload identity drifted")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 36:
        raise ValueError("transferred q2 row ledger drifted")
    output: dict[tuple[Any, ...], q10.Q10] = {}
    for target, row in enumerate(rows):
        body = {"output": target, "terms": row.get("terms")}
        if row.get("output") != target or row.get("canonical_sha256") != _canonical_hash(body):
            raise ValueError(f"transferred q2 row hash drifted: {target}")
        for left, left_raw, right, right_raw, raw in row["terms"]:
            coefficient = _q10_string(raw)
            if (
                not isinstance(left_raw, list)
                or not isinstance(right_raw, list)
                or any(type(axis) is not int or not 0 <= axis < 4 for axis in left_raw + right_raw)
            ):
                raise ValueError("transferred q2 contains an invalid PBW word")
            for left_word, left_pbw in q10.pbw_word(tuple(left_raw)):
                for right_word, right_pbw in q10.pbw_word(tuple(right_raw)):
                    q10._add(
                        output,
                        (target, left, right, left_word, right_word),
                        q10.qmul(coefficient, q10.qmul(left_pbw, right_pbw)),
                    )
    body = {key: payload[key] for key in payload if key != "canonical_sha256"}
    if payload.get("canonical_sha256") != _canonical_hash(body):
        raise ValueError("transferred q2 canonical payload hash drifted")
    return output  # type: ignore[return-value]


def _pairing(record: Mapping[str, Any]) -> dict[tuple[int, int], q10.Q10]:
    parsed = _parse_operator(record, shape=(36, 36), name="omega36")
    output: dict[tuple[int, int], q10.Q10] = {}
    for (left, right, word), coefficient in parsed.items():
        if word:
            raise ValueError("retained pairing is not order zero")
        output[left, right] = coefficient
    return output


def _dependency_hashes(carrier: Mapping[str, Any]) -> None:
    for name, dependency in carrier["dependency_refs"].items():
        if _sha256(_git_blob(dependency["path"])) != dependency["sha256"]:
            raise ValueError(f"portable carrier dependency hash drifted: {name}")


@dataclass(frozen=True)
class Replay:
    carrier_sha256: str
    classical_transfer_certificate_sha256: str
    classical_transfer_payload_sha256: str
    q64_terms: int
    omega64_terms: int
    transferred_terms: int
    transferred_nonzero_rows: int
    mixed_input_terms: int
    pure_Maxwell_input_terms: int
    maximum_total_jet_order: int
    inner_contributions: int
    outer_contributions: int
    full_cyclicity_defect_terms: int
    full_cyclicity_defect_sha256: str
    full_cyclicity_first_witness: list[object]
    retained_cyclicity_defect_terms: int
    retained_cyclicity_defect_sha256: str
    retained_cyclicity_first_witness: list[object]


def _defect_ledger(defect: Mapping[q10.TrilinearKey, q10.Q10]) -> list[list[object]]:
    return [
        [first, second, third, list(first_word), list(second_word), q10._coefficient(coefficient)]
        for (first, second, third, first_word, second_word), coefficient in sorted(defect.items())
    ]


@lru_cache(maxsize=1)
def replay() -> Replay:
    carrier = _git_json(CARRIER_RELATIVE)
    carrier_schema = _git_json(CARRIER_SCHEMA_RELATIVE)
    transfer = _git_json(TRANSFER_CERTIFICATE_RELATIVE)
    transfer_payload = _git_json(TRANSFER_PAYLOAD_RELATIVE)
    _strict_validate(carrier, carrier_schema, "portable carrier")
    _strict_validate(transfer, _git_json(TRANSFER_SCHEMA_RELATIVE), "classical transfer")
    _strict_validate(
        transfer_payload,
        _git_json(TRANSFER_PAYLOAD_SCHEMA_RELATIVE),
        "classical transferred payload",
    )
    if (
        carrier.get("result_id") != "BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR"
        or carrier.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or carrier.get("flags", {}).get("CLASSICAL_MAXWELL_CAUSAL_TRANSFER_DEPENDENCY_PINNED") is not True
        or carrier.get("flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("portable carrier theorem boundary drifted")
    _dependency_hashes(carrier)

    full = carrier["full_complex"]
    retained = carrier["retained_complex"]
    contraction = carrier["contraction"]
    degrees = tuple(row["degree"] for row in retained["component_rows"])
    expected_degrees = (
        (-1,) * 3
        + (0,) * 10
        + (1,) * 10
        + (2,) * 3
        + (-1,)
        + (0,) * 4
        + (1,) * 4
        + (2,)
    )
    if degrees != expected_degrees:
        raise ValueError("retained 36-row degree ledger drifted")

    q64 = _parse_operator(full["classical_unary_q1"], shape=(64, 64), name="q64")
    omega64 = _parse_operator(full["cyclic_pairing"], shape=(64, 64), name="omega64")
    q36 = _parse_operator(retained["classical_unary_q1"], shape=(36, 36), name="q36")
    pairing36 = _pairing(retained["cyclic_pairing"])
    iota = _parse_operator(contraction["iota_36_to_64"], shape=(64, 36), name="iota36")
    projection = _parse_operator(contraction["pi_64_to_36"], shape=(36, 64), name="pi36")
    _parse_operator(contraction["S_64"], shape=(64, 64), name="S64")

    overlay = _parse_overlay(_git_json(COUPLED_Q2_RELATIVE))
    expected = _parse_transferred(transfer_payload)
    full_degrees = tuple(row["degree"] for row in full["component_rows"])
    pairing64: dict[tuple[int, int], q10.Q10] = {}
    for (left, right, word), coefficient in omega64.items():
        if word:
            raise ValueError("full cyclic pairing is not order zero")
        pairing64[left, right] = coefficient
    if q10.arity_two_defect(q64, overlay, full_degrees):
        raise ValueError("full q1/q2 overlay arity-two identity failed")
    full_cyclicity_defect = _cyclicity_defect(overlay, pairing64, full_degrees)
    intermediate, inner_contributions = _transfer_inner(overlay, iota)
    computed, outer_contributions = _transfer_outer(intermediate, projection)
    if computed != expected:
        missing = len(set(expected) - set(computed))
        extra = len(set(computed) - set(expected))
        changed = sum(computed.get(key) != expected.get(key) for key in set(computed) & set(expected))
        raise ValueError(
            f"transferred q2 coefficient mismatch: missing={missing}, extra={extra}, changed={changed}"
        )
    if q10.arity_two_defect(q36, expected, degrees):
        raise ValueError("retained q1/q2 arity-two identity failed")
    retained_cyclicity_defect = _cyclicity_defect(expected, pairing36, degrees)

    nonzero_rows = len({target for target, *_ in expected})
    mixed = sum((left < 26) != (right < 26) for _, left, right, _, _ in expected)
    pure_Maxwell = sum(left >= 26 and right >= 26 for _, left, right, _, _ in expected)
    maximum_order = max(len(left_word) + len(right_word) for *_, left_word, right_word in expected)
    summary = transfer["first_transferred_mixed_vertex"]
    if (
        len(expected) != 1522
        or nonzero_rows != 23
        or len(expected) != summary["term_count"]
        or mixed != summary["mixed_gravity_Maxwell_input_term_count"]
        or pure_Maxwell != summary["pure_Maxwell_input_term_count"]
        or maximum_order != summary["maximum_total_jet_order"]
        or _sha256(_git_blob(TRANSFER_PAYLOAD_RELATIVE)) != summary["payload_file_sha256"]
    ):
        raise ValueError("transferred mixed-vertex summary drifted")
    full_ledger = _defect_ledger(full_cyclicity_defect)
    retained_ledger = _defect_ledger(retained_cyclicity_defect)
    if len(full_ledger) != 1234 or len(retained_ledger) != 953:
        raise ValueError("cyclicity obstruction ledger drifted")

    return Replay(
        carrier_sha256=_sha256(_git_blob(CARRIER_RELATIVE)),
        classical_transfer_certificate_sha256=_sha256(_git_blob(TRANSFER_CERTIFICATE_RELATIVE)),
        classical_transfer_payload_sha256=_sha256(_git_blob(TRANSFER_PAYLOAD_RELATIVE)),
        q64_terms=len(q64),
        omega64_terms=len(omega64),
        transferred_terms=len(expected),
        transferred_nonzero_rows=nonzero_rows,
        mixed_input_terms=mixed,
        pure_Maxwell_input_terms=pure_Maxwell,
        maximum_total_jet_order=maximum_order,
        inner_contributions=inner_contributions,
        outer_contributions=outer_contributions,
        full_cyclicity_defect_terms=len(full_ledger),
        full_cyclicity_defect_sha256=_canonical_hash(full_ledger),
        full_cyclicity_first_witness=full_ledger[0],
        retained_cyclicity_defect_terms=len(retained_ledger),
        retained_cyclicity_defect_sha256=_canonical_hash(retained_ledger),
        retained_cyclicity_first_witness=retained_ledger[0],
    )


def build_payload() -> dict[str, Any]:
    result = replay()
    return {
        "schema": "quantum-weyl-berger-coupled-36-transfer-replay-v1",
        "result_id": "BERGER_COUPLED_36_TRANSFER_INDEPENDENT_REPLAY",
        "result_state": "TRANSFER_AND_Q1Q2_REPLAYED_CYCLICITY_OBSTRUCTION_FOUND",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_commit": CLASSICAL_COMMIT,
        "pinned_inputs": {
            "portable_carrier_sha256": result.carrier_sha256,
            "classical_transfer_certificate_sha256": result.classical_transfer_certificate_sha256,
            "classical_transfer_payload_sha256": result.classical_transfer_payload_sha256,
        },
        "coverage": {
            "full_rows": 64,
            "retained_rows": 36,
            "q64_canonical_coefficients": result.q64_terms,
            "omega64_canonical_coefficients": result.omega64_terms,
            "transferred_q2_canonical_coefficients": result.transferred_terms,
            "transferred_nonzero_output_rows": result.transferred_nonzero_rows,
            "mixed_gravity_Maxwell_input_coefficients": result.mixed_input_terms,
            "pure_Maxwell_input_coefficients": result.pure_Maxwell_input_terms,
            "maximum_total_jet_order": result.maximum_total_jet_order,
        },
        "work_ledger": {
            "formula": "ell2_mixed=pi64 q2_Maxwell-overlay(iota36,iota36)",
            "inner_raw_contributions": result.inner_contributions,
            "outer_Leibniz_contributions": result.outer_contributions,
        },
        "independent_replay": {
            "strict_schemas_and_content_hashes": "VERIFIED",
            "portable_q1_pairing_and_SDR_records": "VERIFIED",
            "transfer_formula_all_1522_coefficients": "VERIFIED",
            "retained_q1_q2_arity_two_identity": "VERIFIED",
            "full_q1_q2_arity_two_identity": "VERIFIED",
            "full_odd_pairing_cyclicity": "FAILED_WITH_EXACT_WITNESS",
            "retained_odd_pairing_cyclicity": "FAILED_WITH_EXACT_WITNESS",
            "exact_Q_sqrt10_no_floating_point": "VERIFIED",
        },
        "cyclicity_obstruction": {
            "full_64_defect_coefficient_count": result.full_cyclicity_defect_terms,
            "full_64_defect_sha256": result.full_cyclicity_defect_sha256,
            "full_64_first_normalized_witness": result.full_cyclicity_first_witness,
            "retained_36_defect_coefficient_count": result.retained_cyclicity_defect_terms,
            "retained_36_defect_sha256": result.retained_cyclicity_defect_sha256,
            "retained_36_first_normalized_witness": result.retained_cyclicity_first_witness,
            "interpretation": (
                "the action-derived cyclicity boolean in the classical transfer certificate "
                "was not coefficientwise replayed there and is not reproduced by the exported tensor/pairing"
            ),
        },
        "claim_flags": {
            "PORTABLE_64_36_CARRIER_IMPORTED": True,
            "CLASSICAL_MIXED_Q2_TRANSFER_INDEPENDENTLY_REPLAYED": True,
            "RETAINED_Q1_Q2_IDENTITY_INDEPENDENTLY_REPLAYED": True,
            "RETAINED_BV_CYCLICITY_INDEPENDENTLY_REPLAYED": False,
            "EXACT_CYCLICITY_OBSTRUCTION_WITNESS": True,
            "CLASSICAL_MAXWELL_CAUSAL_CONTRACTION_HASH_PINNED": True,
            "CAUSAL_GREEN_IDENTITIES_INDEPENDENTLY_REPLAYED_HERE": False,
            "MIXED_Q3_TRANSFERRED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPAIR_CLASSICAL_COUPLED_Q2_OR_PAIRING_UNTIL_CYCLICITY_REPLAYS",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC quantum-side consumer independently parses the committed "
            "portable 64-row unary and pairing, 64-to-36 cyclic SDR, original 1,954-term "
            "Maxwell q2 overlay and classical 1,522-term retained payload over Q(sqrt(10)). "
            "It recomputes ell2_mixed=pi64 q2(iota36,iota36) coefficientwise and independently "
            "replays the full and retained arity-two identities. The odd-pairing cyclicity claim "
            "does not replay: the normalized defect has 1,234 full and 953 retained exact "
            "coefficients, recorded with hashes and explicit first witnesses. The separate "
            "classical causal Maxwell certificate is hash-pinned but its Green-support theorem "
            "is not analytically re-proved here. This is a classical BV import/replay result, "
            "and it blocks promotion of the mixed vertex until the classical tensor or convention "
            "is repaired. This is not a mixed-q3, localized apparatus, Hadamard, renormalized-product, QME, particle, "
            "unitarity, or quantum theorem."
        ),
    }
