"""Independent verifier for the nonminimal/gauge-fixed G2 receipt."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .nonminimal_gauge_fixed_contraction_certificate import (
    H04_OUTPUT,
    H14_OUTPUT,
    OUTPUT,
    RESULT_SCHEMA,
    ROOT,
    SCHEMA,
    build_outputs,
    validate,
)


def verify() -> dict:
    checked = {path: json.loads(path.read_text()) for path in (OUTPUT, H04_OUTPUT, H14_OUTPUT)}
    schemas = {
        OUTPUT: json.loads(SCHEMA.read_text()),
        H04_OUTPUT: json.loads(RESULT_SCHEMA.read_text()),
        H14_OUTPUT: json.loads(RESULT_SCHEMA.read_text()),
    }
    for path, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(checked[path])
    for path, expected in checked[OUTPUT]["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"nonminimal/gauge-fixed source drifted: {path}")
    if checked != build_outputs():
        raise ValueError("nonminimal/gauge-fixed outputs do not reproduce")
    validate(checked[OUTPUT])
    for flag in (
        "ANOMALY_COEFFICIENTS_COMPUTED_HERE",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
    ):
        mutant = deepcopy(checked[OUTPUT])
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"nonminimal/gauge-fixed overclaim survived: {flag}")
    return checked[OUTPUT]


if __name__ == "__main__":
    verify()
    print("general nonminimal/gauge-fixed G2 verifier: PASS")
