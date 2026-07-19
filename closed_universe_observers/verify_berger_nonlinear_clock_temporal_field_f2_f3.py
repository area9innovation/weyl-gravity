#!/usr/bin/env python3
"""Independently verify the temporal nonlinear clock field retraction."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_nonlinear_clock_temporal_field_f2_f3 import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    TemporalJetChart,
    canonical_sha256,
    field_chart_audit,
    phase_inverse_audit,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    phase = phase_inverse_audit()
    audit = field_chart_audit()
    payload = TemporalJetChart().payload()
    assert value["phase_inverse"] == phase
    assert value["temporal_field_chart"] == audit
    assert value["taylor_payload"]["F2"] == payload["F2"]
    assert value["taylor_payload"]["F3"] == payload["F3"]
    assert value["taylor_payload"]["canonical_sha256"] == canonical_sha256(payload)
    assert value["taylor_payload"]["reconstruction_audit"] == TemporalJetChart().payload_reconstruction_audit()
    assert value["taylor_payload"]["reconstruction_audit"]["defect_component_count"] == 0
    assert TemporalJetChart().payload_reconstruction_audit(use_full_arity_factorial=True)["defect_component_count"] > 0
    assert phase["residual_term_count"] == 0
    assert phase_inverse_audit(omit_cubic_terms=True)["residual_term_count"] > 0
    assert audit["linear_metric_defect_count"] == 0
    assert audit["quadratic_monomial_count"] == 36
    assert audit["cubic_monomial_count"] == 96
    assert field_chart_audit(omit_quadratic_inverse_shift=True)["correction_expressions"] != audit["correction_expressions"]
    assert field_chart_audit(flip_inverse_jacobian_sign=True)["linear_metric_defect_count"] > 0
    print("BERGER_NONLINEAR_CLOCK_TEMPORAL_FIELD_F2_F3 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
