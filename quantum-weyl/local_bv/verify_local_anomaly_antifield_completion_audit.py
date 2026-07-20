#!/usr/bin/env python3
"""Independent verifier for the local anomaly completion audit."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance

try:
    from .local_anomaly_antifield_completion_audit import (
        DEPENDENCIES,
        EXPECTED_VECTOR,
        validate,
    )
    from .local_anomaly_antifield_completion_audit_certificate import (
        HERE,
        OUTPUT,
        SOURCE_PATHS,
    )
except ImportError:
    from local_anomaly_antifield_completion_audit import (
        DEPENDENCIES,
        EXPECTED_VECTOR,
        validate,
    )
    from local_anomaly_antifield_completion_audit_certificate import (
        HERE,
        OUTPUT,
        SOURCE_PATHS,
    )


SCHEMA = HERE / "schema/local-anomaly-antifield-completion-audit-v1.schema.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: str | dict[str, int]) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"completion audit schema failed: {errors}")
    validate(value)

    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != _sha256(path):
            raise ValueError(f"completion audit dependency drift: {name}")

    h14 = dependencies["H14_gauge_fixed"]
    if (
        h14["parity_dimensions"] != {"even": 2, "odd": 1}
        or h14["regularity_scope"] != "REGULAR_BACH_LOCUS"
        or {row["representative_id"] for row in h14["classes"]}
        != {"ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C"}
    ):
        raise ValueError("independent H14 quotient replay failed")

    standard = dependencies["standard_coefficients"]["coefficient_calculation"]
    a_rows = [
        _q(row["signed_a_contribution"])
        for row in standard["constant_curvature_factor_ledger"]
    ]
    a_factor = sum(a_rows, Fraction(0))
    a_closed = _q(standard["closed_form_a"])
    c_ricci = a_factor + _q(
        standard["ricci_flat_sum_beta1_equals_c_minus_a"]
    )
    c_conical = _q(standard["independent_conical_sphere_c"])
    if not (
        a_factor == a_closed == Fraction(87, 20)
        and c_ricci == c_conical == Fraction(199, 30)
    ):
        raise ValueError("independent two-method coefficient replay failed")

    strict = dependencies["strict_Slavnov"]
    strict_vector = {
        key: _q(coefficient)
        for key, coefficient in strict["coefficients"].items()
    }
    if (
        strict_vector != EXPECTED_VECTOR
        or strict["qme_disposition"]["status"]
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
    ):
        raise ValueError("independent strict-QME replay failed")

    extended = dependencies["WZ_extended_cohomology"]
    boundary = [
        [_q(item) for item in row] for row in extended["H14"]["boundary_matrix"]
    ]
    if (
        boundary
        != [
            [Fraction(1 if row == column else 0) for column in range(4)]
            for row in range(4)
        ]
        or extended["one_loop_QME"]["status"]
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
    ):
        raise ValueError("independent extended-QME replay failed")

    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("completion audit source manifest drift")

    mutant = deepcopy(value)
    mutant["claim_flags"]["STRICT_THEORY_ANOMALY_FREE"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("strict anomaly-freedom mutant was accepted")
    return value


if __name__ == "__main__":
    verify()
    print("LOCAL ANOMALY ANTIFIELD COMPLETION independent verification: PASS")
