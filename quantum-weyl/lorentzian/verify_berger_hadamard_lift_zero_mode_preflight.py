#!/usr/bin/env python3
"""Independent verifier for the Hadamard lift and zero-mode preflight."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_hadamard_lift_zero_mode_preflight import (
    BASE,
    CAUSAL_26,
    CAUSAL_54,
    D_CARTAN,
    GAUGE_FIXED,
    GRADED_CONTRACT,
    Q2,
    REDUCTION,
    TYPED_COMPANION,
    covariance_lift_replay,
    koszul_pairing_replay,
    validate,
)
from .berger_hadamard_lift_zero_mode_preflight_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-hadamard-lift-zero-mode-preflight-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    dependency_paths = {
        "graded_state_space_contract": GRADED_CONTRACT,
        "base_wave_parametrix": BASE,
        "typed_companion_preflight": TYPED_COMPANION,
        "gauge_fixed_54_contraction": GAUGE_FIXED,
        "causal_54_to_26_reduction": REDUCTION,
        "causal_26": CAUSAL_26,
        "causal_54": CAUSAL_54,
        "causal_D_Cartan_v2": D_CARTAN,
        "support_local_q2": Q2,
    }
    for name, path in dependency_paths.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if certificate["dependency_refs"][name]["sha256"] != actual:
            raise ValueError(f"dependency hash mismatch: {name}")

    gauge_fixed = json.loads(GAUGE_FIXED.read_text())
    if koszul_pairing_replay(gauge_fixed) != certificate["rowwise_Koszul_audit"]:
        raise ValueError("independent rowwise Koszul replay mismatch")
    if covariance_lift_replay() != certificate["covariance_lift_26_to_54"]:
        raise ValueError("independent covariance-lift replay mismatch")

    mutations = (
        ("claim_flags", "BERGER_54_ROW_BRST_HADAMARD", True),
        ("claim_flags", "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY", True),
        ("claim_flags", "QUANTUM_CLAIM", True),
        ("zero_frequency_carrier_theorem", "status", "COMPLETE"),
        (
            "retained_26_construction_boundary",
            "exact_global_omega2_plus_26",
            "CONSTRUCTED",
        ),
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
    print("BERGER HADAMARD LIFT/ZERO-MODE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
