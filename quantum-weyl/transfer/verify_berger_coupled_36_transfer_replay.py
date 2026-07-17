#!/usr/bin/env python3
"""Independent fail-closed verifier for the coupled transfer replay."""

from __future__ import annotations

from copy import deepcopy
import json

from local_bv.schema_validation import validate_instance

from .berger_coupled_36_transfer_replay import _q10_string, build_payload
from .berger_coupled_36_transfer_replay_certificate import HERE, OUTPUT, build_certificate


def _rejects_overclaim(value: dict) -> None:
    flags = value["claim_flags"]
    obstruction = value["cyclicity_obstruction"]
    if (
        flags["RETAINED_BV_CYCLICITY_INDEPENDENTLY_REPLAYED"]
        or not flags["EXACT_CYCLICITY_OBSTRUCTION_WITNESS"]
        or flags["CAUSAL_GREEN_IDENTITIES_INDEPENDENTLY_REPLAYED_HERE"]
        or flags["MIXED_Q3_TRANSFERRED"]
        or flags["QME_RESTORED"]
        or flags["QUANTUM_CLAIM"]
        or obstruction["full_64_defect_coefficient_count"] != 1234
        or obstruction["retained_36_defect_coefficient_count"] != 953
    ):
        raise ValueError("coupled transfer replay was over-promoted or its witness drifted")


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
    schema = json.loads(
        (HERE / "schema/berger-coupled-36-transfer-replay-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    if certificate != build_certificate() or build_payload()["coverage"]["transferred_q2_canonical_coefficients"] != 1522:
        raise ValueError("coupled transfer replay does not reproduce")
    _rejects_overclaim(certificate)
    for key, value in (
        ("RETAINED_BV_CYCLICITY_INDEPENDENTLY_REPLAYED", True),
        ("EXACT_CYCLICITY_OBSTRUCTION_WITNESS", False),
        ("CAUSAL_GREEN_IDENTITIES_INDEPENDENTLY_REPLAYED_HERE", True),
        ("MIXED_Q3_TRANSFERRED", True),
        ("QME_RESTORED", True),
        ("QUANTUM_CLAIM", True),
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = value
        try:
            _rejects_overclaim(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")
    try:
        _q10_string("0.5")
    except ValueError:
        pass
    else:
        raise ValueError("floating-point coefficient mutation accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER COUPLED 36 TRANSFER independent verification: PASS (cyclicity obstruction retained)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
