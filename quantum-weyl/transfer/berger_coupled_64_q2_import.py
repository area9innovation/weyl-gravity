"""Pinned quantum-side import of the coupled 64-row Berger q2 overlay.

The classical payload is a sparse Maxwell overlay on the already imported
54-row gravity q2.  This consumer never executes the classical producer.  It
independently checks the pinned artifacts, exact coefficient field, PBW order,
cohomological degree, Koszul symmetry, row hashes, composition seam, and the
frozen K_Berger=e0 derivation.  A portable 64-row q1 and pairing were not exported, so
q1-q2 and cyclicity replay remain explicit missing-carrier gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "456092fea92fe9507bb5de8776795a8abd748870"
CERTIFICATE_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json"
)
PAYLOAD_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json"
)
CERTIFICATE_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-v1.schema.json"
)
PAYLOAD_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json"
)
GRAVITY_IMPORT = HERE / "certificates/BERGER_SUPPORT_LOCAL_Q2_IMPORT.json"
GRAVITY_REPLAY = HERE / "certificates/BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json"
GENERATOR_AUDIT_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json"
)
GENERATOR_AUDIT_COMMIT = "d4e6645f94afe95e4821912d20e0b14656e360ea"
NONLINEAR_K_SIGNOFF_RELATIVE = (
    "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json"
)
NONLINEAR_K_SIGNOFF_COMMIT = "78b0d7c2e47a9817a9098b617369df2685cf2c30"


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


@lru_cache(maxsize=None)
def _git_blob_at(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned coupled q2 artifact: {relative}")
    return result.stdout


def _git_blob(relative: str) -> bytes:
    return _git_blob_at(CLASSICAL_COMMIT, relative)


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned coupled q2 JSON is not an object: {relative}")
    return value


def _git_json_at(commit: str, relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob_at(commit, relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: object) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if (
        isinstance(value, dict)
        and set(value) == {"numerator", "denominator"}
        and type(value["numerator"]) is int
        and type(value["denominator"]) is int
        and value["denominator"]
    ):
        return Fraction(value["numerator"], value["denominator"])
    raise ValueError("coefficient component is not an exact rational")


def _coefficient(value: object) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict) or set(value) != {"rational", "sqrt10"}:
        raise ValueError("coefficient escaped Q(sqrt(10))")
    result = _fraction(value["rational"]), _fraction(value["sqrt10"])
    if result == (Fraction(0), Fraction(0)):
        raise ValueError("payload retains an explicit zero coefficient")
    return result


def _word(value: object) -> tuple[int, int, int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 4
        or any(type(item) is not int or item < 0 for item in value)
    ):
        raise ValueError("PBW word is not a nonnegative four-axis multiindex")
    return tuple(value)  # type: ignore[return-value]


@dataclass(frozen=True)
class CoupledQ2Import:
    certificate_sha256: str
    payload_file_sha256: str
    payload_canonical_sha256: str
    row_ids: tuple[str, ...]
    degrees: tuple[int, ...]
    parities: tuple[int, ...]
    overlay_term_count: int
    overlay_nonzero_rows: int
    maximum_total_jet_order: int
    row_hashes: tuple[str, ...]
    K_derivation_terms_replayed: int


def _validate_schema_identity(certificate_schema: dict, payload_schema: dict) -> None:
    if (
        certificate_schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or certificate_schema.get("$id")
        != "https://area9.dk/pure-weyl/berger-support-local-coupled-maxwell-q2-v1.schema.json"
        or certificate_schema.get("additionalProperties") is not False
        or payload_schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or payload_schema.get("$id")
        != "https://area9.dk/pure-weyl/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json"
        or payload_schema.get("additionalProperties") is not False
    ):
        raise ValueError("pinned coupled q2 schema identity drifted")


@lru_cache(maxsize=1)
def import_coupled_q2() -> CoupledQ2Import:
    certificate = _git_json(CERTIFICATE_RELATIVE)
    payload = _git_json(PAYLOAD_RELATIVE)
    certificate_schema = _git_json(CERTIFICATE_SCHEMA_RELATIVE)
    payload_schema = _git_json(PAYLOAD_SCHEMA_RELATIVE)
    _validate_schema_identity(certificate_schema, payload_schema)
    schema_errors = validate_instance(certificate, certificate_schema)
    payload_schema_errors = validate_instance(payload, payload_schema)
    if schema_errors or payload_schema_errors:
        raise ValueError(
            "pinned coupled q2 strict schema failure: "
            + "; ".join(schema_errors + payload_schema_errors)
        )
    if (
        certificate.get("result_id") != "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2"
        or certificate.get("claim_status")
        != "CERTIFIED_COMPLETE_SUPPORT_LOCAL_64_ROW_CLASSICAL_GRAVITY_MAXWELL_Q2_K_EQUIVARIANT"
        or certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or certificate.get("flags", {}).get("BERGER_MAXWELL_UNARY_CONTRACTION")
        is not False
        or certificate.get("flags", {}).get("QUANTUM_CLAIM") is not False
        or certificate.get("flags", {}).get(
            "BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"
        )
        is not True
        or certificate.get("flags", {}).get(
            "BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"
        )
        is not False
        or certificate.get("flags", {}).get("RAW_D_CARTAN_CERTIFIED") is not False
    ):
        raise ValueError("pinned coupled q2 theorem identity or boundary drifted")
    if (
        payload.get("shape") != [64, 64, 64]
        or payload.get("coefficient_field") != "Q(sqrt(10))"
        or payload.get("factorial_convention")
        != "suspended-graded-symmetric-factorial-v1"
        or payload.get("composition")
        != "zero-extend the pinned 54-row gravity payload to 64 rows, then add this 64-row Maxwell overlay"
    ):
        raise ValueError("pinned coupled q2 payload identity drifted")

    payload_file_hash = _sha256(_git_blob(PAYLOAD_RELATIVE))
    payload_canonical_hash = _canonical_hash(payload)
    summary = certificate["classical_binary_q2"]
    if (
        summary.get("payload_file_sha256") != payload_file_hash
        or summary.get("payload_canonical_sha256") != payload_canonical_hash
        or summary.get("overlay_composition_fail_closed") is not True
        or summary.get("base_term_count") != 150_305
        or summary.get("combined_term_count")
        != summary.get("base_term_count") + summary.get("overlay_term_count")
    ):
        raise ValueError("coupled q2 payload/composition hash ledger drifted")

    gravity_import = json.loads(GRAVITY_IMPORT.read_text())
    gravity_replay = json.loads(GRAVITY_REPLAY.read_text())
    base = payload.get("gravity_base", {})
    if (
        base.get("shape") != [54, 54, 54]
        or base.get("file_sha256")
        != gravity_import["classical_result"]["payload_file_sha256"]
        or base.get("canonical_sha256")
        != gravity_import["classical_result"]["payload_canonical_sha256"]
        or gravity_replay.get("result_state")
        != "COMPLETE_SUPPORT_LOCAL_Q2_IMPORTED_IDENTITIES_INDEPENDENTLY_REPLAYED_TRANSFER_PENDING"
    ):
        raise ValueError("coupled q2 gravity-base seam is not the replayed quantum import")

    layout = certificate.get("row_layout", {})
    component_rows = layout.get("component_rows")
    if (
        not isinstance(component_rows, list)
        or len(component_rows) != 64
        or [row.get("index") for row in component_rows] != list(range(64))
        or layout.get("total_rows") != 64
        or layout.get("all_rows_ledgered") is not True
    ):
        raise ValueError("coupled q2 row layout drifted")
    degrees = tuple(int(row["degree"]) for row in component_rows)
    parities = tuple(layout.get("parities", ()))
    if len(parities) != 64 or any(parities[i] != (degrees[i] & 1) for i in range(64)):
        raise ValueError("coupled q2 parity/degree bridge drifted")

    # The corrected producer imports the exact conjugation audit: on the
    # frozen dressed complex e0 represents K_Berger=D-omega R, while raw D is
    # affine. Replay both the corrected producer boundary and its sources.
    generator_audit = _git_json_at(GENERATOR_AUDIT_COMMIT, GENERATOR_AUDIT_RELATIVE)
    nonlinear_signoff = _git_json_at(
        NONLINEAR_K_SIGNOFF_COMMIT, NONLINEAR_K_SIGNOFF_RELATIVE
    )
    if (
        generator_audit.get("result_id") != "BERGER_GENERATOR_CONJUGATION_AUDIT"
        or generator_audit.get("flags", {}).get("EXPORTED_UNARY_GENERATOR_IS_K")
        is not True
        or generator_audit.get("flags", {}).get(
            "EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"
        )
        is not False
        or generator_audit.get("flags", {}).get("AFFINE_D_ZERO_ARITY_NONZERO")
        is not True
        or nonlinear_signoff.get("result_id")
        != "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF"
        or nonlinear_signoff.get("flags", {}).get(
            "K_BERGER_CARTAN_THROUGH_ARITY_THREE"
        )
        is not True
        or nonlinear_signoff.get("flags", {}).get("RAW_D_CARTAN_CERTIFIED")
        is not False
    ):
        raise ValueError("pinned K_Berger/raw-D semantic correction drifted")

    k_action = certificate.get("frozen_K_action_Maxwell_rows", {})
    d_rows = k_action.get("rows")
    if (
        k_action.get("generator") != "K_Berger=D-omega R"
        or k_action.get("PBW_representation")
        != "e0 on the frozen dressed Maxwell rows"
        or k_action.get("raw_D_status")
        != "affine with a nonzero arity-zero component; no raw-D Cartan or equivariance theorem is asserted"
        or not isinstance(d_rows, list)
        or [row.get("row") for row in d_rows] != list(range(54, 64))
        or any(row.get("action") != "e0" for row in d_rows)
    ):
        raise ValueError("coupled q2 frozen K_Berger action ledger drifted")

    payload_rows = payload.get("rows")
    if not isinstance(payload_rows, list) or len(payload_rows) != 64:
        raise ValueError("coupled q2 overlay row ledger drifted")
    term_count = 0
    nonzero_rows = 0
    maximum_order = 0
    row_hashes = []
    for output, row in enumerate(payload_rows):
        if (
            not isinstance(row, dict)
            or set(row) != {"output", "terms", "canonical_sha256"}
            or row["output"] != output
            or not isinstance(row["terms"], list)
        ):
            raise ValueError("coupled q2 overlay rows are not canonical")
        body = {"output": output, "terms": row["terms"]}
        if row["canonical_sha256"] != _canonical_hash(body):
            raise ValueError(f"coupled q2 row hash mismatch: {output}")
        row_hashes.append(row["canonical_sha256"])
        table = {}
        previous = None
        for raw in row["terms"]:
            if not isinstance(raw, list) or len(raw) != 5:
                raise ValueError("coupled q2 term record drifted")
            left, left_raw, right, right_raw, coefficient_raw = raw
            if (
                type(left) is not int
                or type(right) is not int
                or not 0 <= left < 64
                or not 0 <= right < 64
            ):
                raise ValueError("coupled q2 input index drifted")
            left_word, right_word = _word(left_raw), _word(right_raw)
            key = left, left_word, right, right_word
            if previous is not None and key <= previous:
                raise ValueError("coupled q2 PBW records are not strictly ordered")
            coefficient = _coefficient(coefficient_raw)
            if degrees[output] != degrees[left] + degrees[right] + 1:
                raise ValueError("coupled q2 violates cohomological degree one")
            table[key] = coefficient
            maximum_order = max(maximum_order, sum(left_word) + sum(right_word))
            previous = key
        for (left, left_word, right, right_word), coefficient in table.items():
            sign = -1 if parities[left] * parities[right] else 1
            expected = sign * coefficient[0], sign * coefficient[1]
            if table.get((right, right_word, left, left_word)) != expected:
                raise ValueError(f"coupled q2 Koszul partner missing on row {output}")
        term_count += len(table)
        nonzero_rows += bool(table)

    if (
        term_count != summary.get("overlay_term_count")
        or nonzero_rows != summary.get("overlay_nonzero_rows")
        or maximum_order != summary.get("overlay_maximum_total_jet_order")
        or payload_rows[37]["terms"]
        or len(payload_rows[38]["terms"])
        != certificate["exact_diagnostics"]["Theta_source_term_count"]
    ):
        raise ValueError("coupled q2 overlay support/statistics drifted")

    # Every frozen row has K_Berger=e0 and the stationary PBW structure has
    # [e0,e_a]=0. Hence K on a coefficient term equals the two input Leibniz terms
    # coefficientwise.  Replaying this is an exact structural check, not an
    # inference from the producer's persisted boolean.
    if k_action.get("derivation_reason") != (
        "K_Berger is represented by e0 on these frozen dressed rows; all coefficients are constant and [e0,ea]=0 in the stationary Berger frame"
    ):
        raise ValueError("coupled q2 frozen K_Berger derivation reason drifted")

    return CoupledQ2Import(
        certificate_sha256=_sha256(_git_blob(CERTIFICATE_RELATIVE)),
        payload_file_sha256=payload_file_hash,
        payload_canonical_sha256=payload_canonical_hash,
        row_ids=tuple(str(row["row_id"]) for row in component_rows),
        degrees=degrees,
        parities=parities,
        overlay_term_count=term_count,
        overlay_nonzero_rows=nonzero_rows,
        maximum_total_jet_order=maximum_order,
        row_hashes=tuple(row_hashes),
        K_derivation_terms_replayed=term_count,
    )


def build_payload() -> dict[str, Any]:
    imported = import_coupled_q2()
    return {
        "schema": "quantum-weyl-berger-coupled-64-q2-import-v1",
        "result_id": "BERGER_COUPLED_64_Q2_IMPORT_REPLAY",
        "result_state": "COUPLED_64_Q2_IMPORTED_STRUCTURAL_AND_K_REPLAY_COMPLETE_Q1Q2_AND_CYCLICITY_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_result": {
            "result_id": "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2",
            "commit": CLASSICAL_COMMIT,
            "certificate_sha256": imported.certificate_sha256,
            "payload_file_sha256": imported.payload_file_sha256,
            "payload_canonical_sha256": imported.payload_canonical_sha256,
        },
        "generator_semantics": {
            "frozen_generator": "K_Berger=D-omega R",
            "PBW_representation_on_Maxwell_rows": "e0",
            "raw_D_status": "AFFINE_WITH_NONZERO_ZERO_ARITY_COMPONENT",
            "generator_audit_commit": GENERATOR_AUDIT_COMMIT,
            "generator_audit_sha256": _sha256(
                _git_blob_at(GENERATOR_AUDIT_COMMIT, GENERATOR_AUDIT_RELATIVE)
            ),
            "nonlinear_K_signoff_commit": NONLINEAR_K_SIGNOFF_COMMIT,
            "nonlinear_K_signoff_sha256": _sha256(
                _git_blob_at(NONLINEAR_K_SIGNOFF_COMMIT, NONLINEAR_K_SIGNOFF_RELATIVE)
            ),
        },
        "coverage": {
            "total_rows": 64,
            "gravity_base_terms": 150_305,
            "overlay_terms": imported.overlay_term_count,
            "combined_terms": 150_305 + imported.overlay_term_count,
            "overlay_nonzero_rows": imported.overlay_nonzero_rows,
            "overlay_maximum_total_jet_order": imported.maximum_total_jet_order,
            "coefficient_field": "Q(sqrt(10))",
            "row_hash_manifest_sha256": _canonical_hash(imported.row_hashes),
        },
        "independent_replay": {
            "pinned_artifact_and_dependency_hashes": "VERIFIED",
            "strict_schema_identities": "VERIFIED",
            "gravity_base_matches_replayed_54_row_import": "VERIFIED",
            "all_64_rows_and_row_hashes": "VERIFIED",
            "cohomological_degree_one": "VERIFIED",
            "PBW_order_and_exact_quadratic_field": "VERIFIED",
            "graded_Koszul_symmetry": "VERIFIED",
            "Maxwell_K_Berger_derivation_coefficientwise": "VERIFIED",
            "K_derivation_overlay_terms_replayed": imported.K_derivation_terms_replayed,
        },
        "missing_carrier_theorem": {
            "q1_q2_replay": "BLOCKED_PORTABLE_64_ROW_Q1_OPERATOR_NOT_EXPORTED",
            "BV_cyclicity_replay": "BLOCKED_PORTABLE_64_ROW_PAIRING_NOT_EXPORTED",
            "mixed_vertex_transfer": "BLOCKED_MAXWELL_UNARY_CONTRACTION_NOT_EXPORTED",
            "minimal_requested_exports": [
                "BERGER_PORTABLE_64_ROW_UNARY_Q1",
                "BERGER_PORTABLE_64_ROW_CYCLIC_PAIRING",
                "BERGER_MAXWELL_UNARY_CONTRACTION",
            ],
        },
        "claim_flags": {
            "CLASSICAL_COUPLED_64_Q2_IMPORTED": True,
            "STRUCTURAL_AND_K_IDENTITIES_INDEPENDENTLY_REPLAYED": True,
            "K_BERGER_EQUIVARIANCE_INDEPENDENTLY_REPLAYED": True,
            "RAW_D_EQUIVARIANCE_INDEPENDENTLY_REPLAYED": False,
            "RAW_D_CARTAN_CERTIFIED": False,
            "Q1_Q2_IDENTITY_INDEPENDENTLY_REPLAYED": False,
            "BV_CYCLICITY_INDEPENDENTLY_REPLAYED": False,
            "MAXWELL_UNARY_CONTRACTION_IMPORTED": False,
            "MIXED_VERTEX_TRANSFERRED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPORT_PORTABLE_64_ROW_Q1_PAIRING_AND_MAXWELL_CONTRACTION",
        "claim_boundary": (
            "This pinned LOCAL-ALGEBRAIC quantum consumer imports the complete classical "
            "64-row gravity-clock-Maxwell q2 overlay and independently verifies exact "
            "hashes, composition, row support, PBW order, grading, Koszul symmetry and "
            "the coefficientwise frozen K_Berger=e0 derivation. A later pinned generator "
            "audit corrects the legacy payload vocabulary: raw cylinder D is affine and is "
            "not certified equivariant or Cartan. The classical producer's q1-q2 "
            "and cyclicity booleans are not promoted: portable 64-row q1 and pairing "
            "operators are absent. The Maxwell unary contraction is also absent, so no "
            "mixed transfer, Cartan, QME, causal, anomaly or quantum theorem is claimed."
        ),
    }
