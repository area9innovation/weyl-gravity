#!/usr/bin/env python3
"""Independent verifier for the Berger base-wave Hadamard parametrix."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from local_bv.schema_validation import validate_instance

from .berger_base_wave_hadamard_parametrix import HERE, ROOT, validate
from .berger_base_wave_hadamard_parametrix_certificate import OUTPUT


SCHEMA = HERE / "schema/berger-base-wave-hadamard-parametrix-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _independent_flat_sign_checks(signs: dict[str, int]) -> dict[str, bool]:
    covector_time = signs["positive_frequency_covector_time"]
    return {
        "positive_frequency_covector_sharp_is_future": (
            signs["metric_inverse_time"] * covector_time > 0
        ),
        "positive_frequency_covector_is_null": (
            signs["metric_inverse_time"] * covector_time**2
            + signs["spatial_covector_norm_squared"]
            == 0
        ),
        "i0_shift_damps_positive_energy_fourier_modes": (
            signs["epsilon_time_coefficient"] > 0 and covector_time < 0
        ),
        "retarded_minus_advanced_matches_Wightman_antisymmetry": (
            signs["Wightman_antisymmetry_relative_to_standard_wave_E"]
            == signs["E_ret_minus_adv_relative_to_standard_wave_E"]
        ),
        "operator_and_causal_propagator_signs_match": (
            signs["P_relative_to_standard_wave"]
            == signs["E_ret_minus_adv_relative_to_standard_wave_E"]
        ),
    }


def verify_certificate() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    for record in certificate["dependency_refs"].values():
        candidates = list(ROOT.rglob("*.json"))
        matches = [
            path for path in candidates
            if _sha256(path) == record["sha256"]
            and json.loads(path.read_text()).get("result_id") == record["result_id"]
        ]
        if not matches:
            raise ValueError(f"unresolved dependency: {record['result_id']}")

    artifacts = {}
    for name, record in certificate["theorem_instantiation_artifacts"].items():
        path = ROOT / record["path"]
        expected_type = (
            "JSON_FLAT_NORMALIZATION_WITNESS"
            if name == "flat_space_normalization"
            else "JSON_THEOREM_INSTANTIATION_LEDGER"
        )
        if record["artifact_type"] != expected_type or _sha256(path) != record["sha256"]:
            raise ValueError(f"theorem-instantiation artifact mismatch: {name}")
        artifacts[name] = json.loads(path.read_text())

    for name in (
        "operator_inventory",
        "local_hadamard_recursion",
        "microlocal_spectrum",
        "stationarity_zero_modes",
    ):
        if artifacts[name].get("artifact_role") != "THEOREM_INSTANTIATION_LEDGER":
            raise ValueError(f"analytic theorem ledger role drifted: {name}")

    recursion = artifacts["local_hadamard_recursion"]
    if (
        "V_(P,0)(x,x)=I_E" not in recursion.get("hadamard_coefficients", "")
        or "0.5 Box Gamma-4+2k" not in recursion.get("invariant_transport", "")
        or not recursion.get("left_defect", "").startswith("P_x H_P^+ is smooth")
        or not recursion.get("right_defect", "").startswith(
            "P_(x')^sharp H_P^+ is smooth"
        )
    ):
        raise ValueError("Hadamard transport ledger drifted")
    micro = artifacts["microlocal_spectrum"]
    if (
        "k future-directed null" not in micro.get("wavefront_set", "")
        or "P^sharp" not in micro.get("adjoint_reversal", "")
        or "smooth local kernel" not in micro.get("commutator", "")
        or "smooth local bisolution" in micro.get("commutator", "")
    ):
        raise ValueError("microlocal or adjoint theorem drifted")
    zero = artifacts["stationarity_zero_modes"]
    if (
        "no inverse spatial operator" not in zero.get("zero_mode_policy", "")
        or zero.get("positivity_policy") != "not decided by a local parametrix"
    ):
        raise ValueError("zero-mode or positivity boundary drifted")
    flat = artifacts["flat_space_normalization"]
    independent_checks = _independent_flat_sign_checks(
        flat.get("normalized_sign_data", {})
    )
    if (
        flat.get("artifact_role") != "CONVENTION_NORMALIZATION_WITNESS"
        or flat.get("signature") != "(-,+,+,+)"
        or "E=G_ret-G_adv" not in flat.get("green_convention", "")
        or "k=(-|p|,p)" not in flat.get("positive_frequency_covector", "")
        or flat.get("exact_sign_checks") != independent_checks
        or not all(independent_checks.values())
    ):
        raise ValueError("flat Hadamard normalization witness drifted")
    return certificate


def mutation_guards(certificate: dict) -> None:
    mutations = (
        ("global bisolution", "scope_boundary", "global_exact_bisolution", True),
        ("state", "scope_boundary", "quasifree_state", True),
        ("26 rows", "claim_flags", "BERGER_26_ROW_BRST_HADAMARD", True),
        ("quantum", "claim_flags", "QUANTUM_CLAIM", True),
        (
            "global completion",
            "global_completion_obligations",
            "smooth_exact_bisolution_correction",
            "COMPLETE",
        ),
        (
            "flat orientation",
            "verified_checks",
            "flat_space_i0_C_plus_and_CCR_normalization",
            False,
        ),
    )
    for name, group, key, value in mutations:
        mutant = deepcopy(certificate)
        mutant[group][key] = value
        try:
            validate(mutant)
        except ValueError:
            continue
        raise ValueError(f"mutation guard accepted {name}")


def main() -> int:
    certificate = verify_certificate()
    mutation_guards(certificate)
    print("BERGER BASE-WAVE HADAMARD PARAMETRIX independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
