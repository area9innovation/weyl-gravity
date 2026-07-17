"""Fail-closed acceptance evaluator for a corrected coupled Berger q2."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from local_bv.schema_validation import validate_instance

from . import berger_coupled_36_transfer_replay as replay_engine
from . import berger_qsqrt10_replay as q10
from .berger_retained_26_q2_transfer import (
    _cyclicity_defect,
    _transfer_inner,
    _transfer_outer,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_SCHEMA = HERE / "schema/berger-coupled-cyclicity-repair-input-v1.schema.json"
BASELINE_COMMIT = "744383f2a21a05a1464f3a25b6569e2b001b4f20"

ARTIFACT_PATHS = {
    "carrier": "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "carrier_schema": "d_quotient_classical/schema/berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json",
    "coupled_q2_payload": "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
    "coupled_q2_payload_schema": "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json",
    "transfer_certificate": "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "transfer_certificate_schema": "d_quotient_classical/schema/berger-maxwell-unary-contraction-transfer-v1.schema.json",
    "transferred_q2_payload": "d_quotient_classical/certificates/BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD.json",
    "transferred_q2_payload_schema": "d_quotient_classical/schema/berger-first-transferred-mixed-q2-payload-v1.schema.json",
}

SCHEMA_IDS = {
    "carrier_schema": "https://area9.dk/pure-weyl/berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json",
    "coupled_q2_payload_schema": "https://area9.dk/pure-weyl/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json",
    "transfer_certificate_schema": "https://pure-weyl.example/schema/berger-maxwell-unary-contraction-transfer-v1.json",
    "transferred_q2_payload_schema": "https://pure-weyl.example/schema/berger-first-transferred-mixed-q2-payload-v1.json",
}


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


@lru_cache(maxsize=None)
def _git_blob(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing candidate artifact at {commit}: {relative}")
    return result.stdout


def _git_json(commit: str, relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(commit, relative))
    if not isinstance(value, dict):
        raise ValueError(f"candidate JSON is not an object: {relative}")
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def baseline_manifest() -> dict[str, Any]:
    return {
        "schema": "quantum-weyl-berger-coupled-cyclicity-repair-input-v1",
        "result_id": "BERGER_COUPLED_CYCLICITY_REPAIR_INPUT",
        "classical_commit": BASELINE_COMMIT,
        "artifacts": {
            name: {"path": path, "sha256": _sha256(_git_blob(BASELINE_COMMIT, path))}
            for name, path in ARTIFACT_PATHS.items()
        },
        "declared_scope": {
            "setting_id": "compact_positive_berger_clock_fixed_coupling",
            "coefficient_field": "Q(sqrt(10))",
            "full_rows": 64,
            "retained_rows": 36,
            "required_dependency_tags": ["LOCAL-ALGEBRAIC"],
        },
        "claim_boundary": (
            "Pinned obstructed baseline used only to prove that the acceptance rail rejects "
            "noncyclic coupled q2 data. It is not a corrected candidate or scientific repair."
        ),
    }


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    commit = manifest["classical_commit"]
    for name, expected_path in ARTIFACT_PATHS.items():
        artifact = manifest["artifacts"][name]
        if artifact["path"] != expected_path:
            raise ValueError(f"candidate artifact path drifted: {name}")
        if _sha256(_git_blob(commit, expected_path)) != artifact["sha256"]:
            raise ValueError(f"candidate artifact hash drifted: {name}")


def _pairing64(record: Mapping[str, Any]) -> dict[tuple[int, int], q10.Q10]:
    parsed = replay_engine._parse_operator(record, shape=(64, 64), name="omega64")
    output: dict[tuple[int, int], q10.Q10] = {}
    for (left, right, word), coefficient in parsed.items():
        if word:
            raise ValueError("candidate full pairing is not order zero")
        output[left, right] = coefficient
    return output


def _strict_artifact_validation(
    manifest: Mapping[str, Any], artifacts: Mapping[str, dict[str, Any]]
) -> None:
    del manifest
    pairs = (
        ("carrier", "carrier_schema"),
        ("coupled_q2_payload", "coupled_q2_payload_schema"),
        ("transfer_certificate", "transfer_certificate_schema"),
        ("transferred_q2_payload", "transferred_q2_payload_schema"),
    )
    for instance_name, schema_name in pairs:
        schema = artifacts[schema_name]
        Draft202012Validator.check_schema(schema)
        if (
            schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("$id") != SCHEMA_IDS[schema_name]
            or schema.get("additionalProperties") is not False
        ):
            raise ValueError(f"candidate schema identity or strictness drifted: {schema_name}")
        errors = validate_instance(artifacts[instance_name], artifacts[schema_name])
        if errors:
            raise ValueError(
                f"candidate strict schema failure ({instance_name}): " + "; ".join(errors)
            )


def _classify(diagnostics: Mapping[str, Any]) -> str:
    algebraic_counts = (
        diagnostics["full_q1_q2_defect_count"],
        diagnostics["full_cyclicity_defect_count"],
        diagnostics["transfer_missing_coefficient_count"],
        diagnostics["transfer_extra_coefficient_count"],
        diagnostics["transfer_changed_coefficient_count"],
        diagnostics["retained_q1_q2_defect_count"],
        diagnostics["retained_cyclicity_defect_count"],
    )
    if any(algebraic_counts):
        return "REJECTED_EXACT_ALGEBRAIC_DEFECT"
    if not diagnostics["causal_unary_flags_preserved"]:
        return "REJECTED_CAUSAL_UNARY_REGRESSION"
    if not diagnostics["producer_cyclicity_claim_consistent"]:
        return "REJECTED_PRODUCER_CLAIM_BOUNDARY"
    return "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR"


def evaluate(manifest: Mapping[str, Any]) -> dict[str, Any]:
    _validate_manifest(manifest)
    commit = manifest["classical_commit"]
    artifacts = {
        name: _git_json(commit, artifact["path"])
        for name, artifact in manifest["artifacts"].items()
    }
    _strict_artifact_validation(manifest, artifacts)

    carrier = artifacts["carrier"]
    full = carrier["full_complex"]
    retained = carrier["retained_complex"]
    contraction = carrier["contraction"]
    full_degrees = tuple(row["degree"] for row in full["component_rows"])
    retained_degrees = tuple(row["degree"] for row in retained["component_rows"])
    q64 = replay_engine._parse_operator(
        full["classical_unary_q1"], shape=(64, 64), name="q64"
    )
    q36 = replay_engine._parse_operator(
        retained["classical_unary_q1"], shape=(36, 36), name="q36"
    )
    pairing64 = _pairing64(full["cyclic_pairing"])
    pairing36 = replay_engine._pairing(retained["cyclic_pairing"])
    iota = replay_engine._parse_operator(
        contraction["iota_36_to_64"], shape=(64, 36), name="iota36"
    )
    projection = replay_engine._parse_operator(
        contraction["pi_64_to_36"], shape=(36, 64), name="pi36"
    )
    overlay = replay_engine._parse_overlay(artifacts["coupled_q2_payload"])
    transferred = replay_engine._parse_transferred(artifacts["transferred_q2_payload"])
    intermediate, inner_contributions = _transfer_inner(overlay, iota)
    computed, outer_contributions = _transfer_outer(intermediate, projection)
    common = set(computed) & set(transferred)

    transfer_flags = artifacts["transfer_certificate"].get("flags", {})
    diagnostics = {
        "full_q1_q2_defect_count": len(
            q10.arity_two_defect(q64, overlay, full_degrees)
        ),
        "full_cyclicity_defect_count": len(
            _cyclicity_defect(overlay, pairing64, full_degrees)
        ),
        "transfer_missing_coefficient_count": len(set(transferred) - set(computed)),
        "transfer_extra_coefficient_count": len(set(computed) - set(transferred)),
        "transfer_changed_coefficient_count": sum(
            computed[key] != transferred[key] for key in common
        ),
        "retained_q1_q2_defect_count": len(
            q10.arity_two_defect(q36, transferred, retained_degrees)
        ),
        "retained_cyclicity_defect_count": len(
            _cyclicity_defect(transferred, pairing36, retained_degrees)
        ),
        "causal_unary_flags_preserved": (
            transfer_flags.get("BERGER_MAXWELL_UNARY_CONTRACTION") is True
            and transfer_flags.get("BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY") is True
            and transfer_flags.get("BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY")
            is True
        ),
        "producer_cyclicity_claim_consistent": (
            transfer_flags.get("BERGER_MIXED_Q2_CYCLICITY") is True
            and transfer_flags.get("BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING")
            is True
        ),
        "full_overlay_coefficient_count": len(overlay),
        "retained_transfer_coefficient_count": len(transferred),
        "inner_raw_contributions": inner_contributions,
        "outer_Leibniz_contributions": outer_contributions,
    }
    return {
        "manifest_canonical_sha256": _canonical_hash(manifest),
        "classical_commit": commit,
        "diagnostics": diagnostics,
        "verdict": _classify(diagnostics),
    }
