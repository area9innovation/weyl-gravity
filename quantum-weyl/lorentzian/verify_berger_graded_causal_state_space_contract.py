#!/usr/bin/env python3
"""Independent verifier for the graded causal state-space contract."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_graded_causal_state_space_contract import (
    BASE,
    CAUSAL_IMPORT,
    DECOMPOSABILITY,
    FLAT,
    FULL_CAUSAL,
    GAUGE_FIXED,
    KREIN,
    POLARIZED,
    RETAINED_LAYOUT,
    ZERO_MODE_TRANS,
    causal_algebra_replay,
    row_pairing_replay,
    validate,
)
from .berger_graded_causal_state_space_contract_certificate import HERE, OUTPUT


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-graded-causal-state-space-contract-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    dependency_paths = {
        "causal_chain_v2": CAUSAL_IMPORT,
        "stationary_decomposability": DECOMPOSABILITY,
        "base_hadamard_parametrix": BASE,
        "flat_CCR_normalization": FLAT,
        "full_54_causal_chain": FULL_CAUSAL,
        "gauge_fixed_pairing": GAUGE_FIXED,
        "retained_layout": RETAINED_LAYOUT,
        "reduced_polarization": POLARIZED,
        "reduced_Krein": KREIN,
        "zero_mode_transgression": ZERO_MODE_TRANS,
    }
    for name, path in dependency_paths.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if certificate["dependency_refs"][name]["sha256"] != actual:
            raise ValueError(f"dependency hash mismatch: {name}")

    gauge_fixed = json.loads(GAUGE_FIXED.read_text())
    if row_pairing_replay(gauge_fixed["row_layout"]["component_rows"]) != certificate[
        "row_pairing_replay"
    ]:
        raise ValueError("independent 54-row pairing replay mismatch")
    if causal_algebra_replay() != certificate["causal_commutator_contract"]:
        raise ValueError("independent causal algebra replay mismatch")
    for flag in (
        "BERGER_54_ROW_BRST_HADAMARD",
        "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation was accepted: {flag}")
    for section, key, promoted in (
        ("two_point_target", "status", "CONSTRUCTED"),
        (
            "brst_descent",
            "distributional_quotient_weak_nondegeneracy",
            "CERTIFIED",
        ),
        ("positivity_and_krein_policy", "full_BV_positive_state", "CERTIFIED"),
    ):
        mutant = deepcopy(certificate)
        mutant[section][key] = promoted
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"analytic promotion was accepted: {section}.{key}")
    return certificate


def main() -> int:
    verify()
    print("BERGER GRADED CAUSAL STATE SPACE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
