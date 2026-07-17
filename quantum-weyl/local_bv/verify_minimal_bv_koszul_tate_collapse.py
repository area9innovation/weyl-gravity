"""Independent verifier for the minimal Koszul--Tate collapse receipt."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .minimal_bv_koszul_tate_collapse_certificate import (
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
    validate,
)


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    validator.validate(value)
    for path, expected in value["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"minimal KT source drifted: {path}")
    if value != build():
        raise ValueError("minimal KT collapse does not reproduce")
    validate(value)
    for flag in (
        "PURE_DIFF_H14_COMPUTED",
        "MIXED_DIFF_WEYL_H14_COMPUTED",
        "FULL_BV_G2_COMPLETE",
        "QME_RESTORED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            continue
        raise ValueError(f"minimal KT overclaim survived: {flag}")
    for mutate in (
        lambda mutant: mutant["lift_ledger"]["exact_rows"][0].update(
            {"minimal_KT_lift_status": "REMAINS_EXACT"}
        ),
        lambda mutant: mutant["checks"].update(
            {"pure_Diff_and_mixed_total_complex": "VERIFIED"}
        ),
    ):
        mutant = deepcopy(value)
        mutate(mutant)
        if not list(validator.iter_errors(mutant)):
            raise ValueError("minimal KT schema accepted a boundary mutation")
    return value


if __name__ == "__main__":
    verify()
    print("MINIMAL BV KOSZUL-TATE COLLAPSE verifier: PASS")
