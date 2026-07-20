#!/usr/bin/env python3
"""Replay and validate the method-distinct active-clock freeze audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from d_quotient_classical.compensator.active_clock_px2_independent_freeze_audit import (
    build,
)


CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-active-clock-px2-independent-freeze-audit-v1.schema.json"
)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload != build():
        raise AssertionError("serialized audit differs from exact replay")
    hashes = payload["content_hashes"]
    for field, section in (
        ("basis_sha256", "action_basis_audit"),
        ("background_sha256", "background_variation_audit"),
        ("locus_sha256", "exact_real_locus_audit"),
        ("coupled_gate_sha256", "coupled_gate_audit"),
        ("singular_sha256", "singular_and_denominator_audit"),
        ("mutations_sha256", "mutation_audit"),
        ("verdict_sha256", "freeze_verdict"),
    ):
        if hashes[field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")
    if (
        payload["independence_boundary"]["producer_module_imported"]
        or payload["independence_boundary"]["producer_invoked"]
        or payload["freeze_verdict"]["all_seven_gate_good_locus"] != "EMPTY"
        or payload["freeze_verdict"]["candidate_C_active_selected"]
        or not payload["freeze_verdict"][
            "scoped_quadratic_active_clock_no_go_theorem_frozen"
        ]
        or payload["claim_flags"]["UNIVERSAL_SCALAR_TENSOR_OR_K_ESSENCE_NO_GO"]
        or payload["claim_flags"]["HADAMARD_ANOMALY_QME_OR_QUANTUM"]
    ):
        raise AssertionError("freeze boundary drifted")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1 "
        "replay: PASS"
    )


if __name__ == "__main__":
    main()
