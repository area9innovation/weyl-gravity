#!/usr/bin/env python3
"""Independent fail-closed verifier for the coupled 64-row q2 consumer."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_coupled_64_q2_import import _coefficient, build_payload
from .berger_coupled_64_q2_import_certificate import HERE, OUTPUT, build_certificate


def _rejects(mutant: dict) -> None:
    flags = mutant["claim_flags"]
    if (
        flags["Q1_Q2_IDENTITY_INDEPENDENTLY_REPLAYED"]
        or flags["BV_CYCLICITY_INDEPENDENTLY_REPLAYED"]
        or flags["MAXWELL_UNARY_CONTRACTION_IMPORTED"]
        or flags["MIXED_VERTEX_TRANSFERRED"]
        or flags["RAW_D_EQUIVARIANCE_INDEPENDENTLY_REPLAYED"]
        or flags["RAW_D_CARTAN_CERTIFIED"]
        or flags["QME_RESTORED"]
        or flags["QUANTUM_CLAIM"]
    ):
        raise ValueError("coupled q2 import was over-promoted")


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
    schema = json.loads(
        (HERE / "schema/berger-coupled-64-q2-import-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    if certificate != build_certificate():
        raise ValueError("coupled q2 certificate does not reproduce")
    if build_payload()["independent_replay"]["K_derivation_overlay_terms_replayed"] != 1954:
        raise ValueError("coupled q2 K_Berger replay count drifted")
    for key in (
        "Q1_Q2_IDENTITY_INDEPENDENTLY_REPLAYED",
        "BV_CYCLICITY_INDEPENDENTLY_REPLAYED",
        "MAXWELL_UNARY_CONTRACTION_IMPORTED",
        "MIXED_VERTEX_TRANSFERRED",
        "RAW_D_EQUIVARIANCE_INDEPENDENTLY_REPLAYED",
        "RAW_D_CARTAN_CERTIFIED",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            _rejects(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")
    try:
        _coefficient({"rational": 0.5, "sqrt10": 0})
    except ValueError:
        pass
    else:
        raise ValueError("floating-point coefficient mutation accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER COUPLED 64-ROW Q2 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
