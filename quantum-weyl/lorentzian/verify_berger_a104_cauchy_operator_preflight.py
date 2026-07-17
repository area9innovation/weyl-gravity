#!/usr/bin/env python3
"""Independent verifier for the Berger A104 Cauchy-operator preflight."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_a104_cauchy_operator_preflight import (
    ENDPOINT_CONTRACT,
    ENDPOINT_IMPORT,
    GENERATED,
    LAYOUT,
    LOWER_IMPORT,
    STATIONARY,
    cauchy_row_ledger,
    metric_cauchy_replay,
    validate,
)
from .berger_a104_cauchy_operator_preflight_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-a104-cauchy-operator-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    paths = {
        "stationary_spectral_preflight": STATIONARY,
        "metric_lower_by_two_import": LOWER_IMPORT,
        "endpoint_factor_import": ENDPOINT_IMPORT,
        "endpoint_contract": ENDPOINT_CONTRACT,
        "retained_layout": LAYOUT,
    }
    for name, path in paths.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if certificate["dependency_refs"][name]["sha256"] != actual:
            raise ValueError(f"dependency hash mismatch: {name}")

    metric, artifacts = metric_cauchy_replay()
    if metric != certificate["metric_Cauchy_operators"]:
        raise ValueError("independent metric Cauchy replay mismatch")
    layout = json.loads(LAYOUT.read_text())
    if cauchy_row_ledger(layout) != certificate["Cauchy_row_ledger"]:
        raise ValueError("independent Cauchy row replay mismatch")
    seen = set()
    for sector, ledger in metric.items():
        for label, reference in ledger["artifacts"].items():
            name = f"{sector}_{label}"
            seen.add(name)
            path = GENERATED / f"{name}.json"
            if json.loads(path.read_text()) != artifacts[name]:
                raise ValueError(f"exact operator artifact replay mismatch: {name}")
            if reference["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError(f"exact operator artifact hash mismatch: {name}")
    if seen != set(artifacts):
        raise ValueError("exact operator artifact inventory mismatch")

    mutations = (
        ("partial_A104_assembly", "full_A104_status", "ASSEMBLED"),
        ("BRST_and_pairing_gate", "q_Cauchy_104", "CONSTRUCTED"),
        ("analytic_gate", "closed_generator_theorem_authorized", True),
        ("claim_flags", "BERGER_FULL_A104_CAUCHY_OPERATOR", True),
        ("claim_flags", "BERGER_HADAMARD_DATA", True),
    )
    for section, key, value in mutations:
        mutant = deepcopy(certificate)
        mutant[section][key] = value
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {section}.{key}")
    return certificate


def main() -> int:
    verify()
    print("BERGER A104 CAUCHY PREFLIGHT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
