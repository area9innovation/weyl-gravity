#!/usr/bin/env python3
"""Independent verifier for the retained stationary spectral preflight."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_retained_stationary_spectral_preflight import (
    CAUSAL_26,
    CAUSAL_WITNESS,
    COMPANION,
    D_ACTION,
    DECOMPOSABILITY,
    GAUGE_FIXED,
    LIFT_PREFLIGHT,
    REDUCED_KREIN,
    VOLTERRA,
    D_action_replay,
    stationary_pencil_replay,
    two_slot_lift_replay,
    validate,
)
from .berger_retained_stationary_spectral_preflight_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-retained-stationary-spectral-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    dependency_paths = {
        "Hadamard_lift_preflight": LIFT_PREFLIGHT,
        "retained_companion": COMPANION,
        "stationary_decomposability": DECOMPOSABILITY,
        "causal_witness": CAUSAL_WITNESS,
        "typed_Volterra": VOLTERRA,
        "causal_26": CAUSAL_26,
        "local_D_action": D_ACTION,
        "gauge_fixed_contraction": GAUGE_FIXED,
        "reduced_Krein": REDUCED_KREIN,
    }
    for name, path in dependency_paths.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if certificate["dependency_refs"][name]["sha256"] != actual:
            raise ValueError(f"dependency hash mismatch: {name}")

    witness = json.loads(CAUSAL_WITNESS.read_text())
    D_action = json.loads(D_ACTION.read_text())
    gauge_fixed = json.loads(GAUGE_FIXED.read_text())
    if stationary_pencil_replay(witness) != certificate["stationary_pencil_inventory"]:
        raise ValueError("independent stationary pencil replay mismatch")
    if D_action_replay(D_action) != certificate["stationary_action_replay"]:
        raise ValueError("independent stationary action replay mismatch")
    if two_slot_lift_replay(gauge_fixed) != certificate["two_slot_covariance_lift"]:
        raise ValueError("independent two-slot lift replay mismatch")

    mutations = (
        ("claim_flags", "BERGER_RETAINED_CLOSED_STATIONARY_GENERATOR", True),
        ("claim_flags", "BERGER_RETAINED_ZERO_ISOLATED", True),
        ("claim_flags", "BERGER_26_ROW_BRST_HADAMARD", True),
        ("closed_generator_contract", "closed_realization_status", "CERTIFIED"),
        ("spectral_isolation_contract", "zero_isolated", "CERTIFIED"),
        ("generalized_zero_and_Riesz_policy", "Riesz_projector_status", "DEFINED"),
    )
    for section, key, value in mutations:
        mutant = deepcopy(certificate)
        mutant[section][key] = value
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation was accepted: {section}.{key}")
    return certificate


def main() -> int:
    verify()
    print("BERGER RETAINED STATIONARY SPECTRAL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
