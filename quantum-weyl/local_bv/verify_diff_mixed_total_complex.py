"""Independent verifier for the Diff/mixed minimal-BV H14 receipt."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .diff_mixed_total_complex_certificate import OUTPUT, ROOT, SCHEMA, build, validate


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    validator.validate(value)
    for path, expected in value["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Diff/mixed H14 source drifted: {path}")
    if value != build():
        raise ValueError("Diff/mixed H14 certificate does not reproduce")
    validate(value)
    for flag in (
        "GENERAL_NONMINIMAL_GAUGE_FIXED_H14_COMPLETE",
        "FULL_G2_PROMOTED",
        "ANOMALY_COEFFICIENTS_COMPUTED_HERE",
        "QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"Diff/mixed H14 overclaim survived: {flag}")
    for mutate in (
        lambda mutant: mutant["small_algebra"]["symmetric_invariant_spaces"][2].update(
            {"invariant_dimension": 1}
        ),
        lambda mutant: mutant["checks"].update(
            {"general_nonminimal_gauge_fixed_sector": "VERIFIED"}
        ),
    ):
        mutant = deepcopy(value)
        mutate(mutant)
        if not list(validator.iter_errors(mutant)):
            raise ValueError("Diff/mixed H14 schema accepted a boundary mutation")
    return value


if __name__ == "__main__":
    verify()
    print("AFN0 Diff/mixed minimal-BV H14 verifier: PASS")
