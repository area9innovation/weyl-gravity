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

    proofs = {}
    for name, record in certificate["proof_artifacts"].items():
        path = ROOT / record["path"]
        if record["artifact_type"] != "JSON_ANALYTIC_PROOF" or _sha256(path) != record["sha256"]:
            raise ValueError(f"proof artifact mismatch: {name}")
        proofs[name] = json.loads(path.read_text())

    recursion = proofs["local_hadamard_recursion"]
    if (
        "V_(P,0)(x,x)=I_E" not in recursion.get("hadamard_coefficients", "")
        or "0.5 Box Gamma-4+2k" not in recursion.get("invariant_transport", "")
        or not recursion.get("left_defect", "").startswith("P_x H_P^+ is smooth")
        or not recursion.get("right_defect", "").startswith(
            "P_(x')^sharp H_P^+ is smooth"
        )
    ):
        raise ValueError("Hadamard transport ledger drifted")
    micro = proofs["microlocal_spectrum"]
    if (
        "k future-directed null" not in micro.get("wavefront_set", "")
        or "P^sharp" not in micro.get("adjoint_reversal", "")
    ):
        raise ValueError("microlocal or adjoint theorem drifted")
    zero = proofs["stationarity_zero_modes"]
    if (
        "no inverse spatial operator" not in zero.get("zero_mode_policy", "")
        or zero.get("positivity_policy") != "not decided by a local parametrix"
    ):
        raise ValueError("zero-mode or positivity boundary drifted")
    return certificate


def mutation_guards(certificate: dict) -> None:
    mutations = (
        ("global bisolution", "scope_boundary", "global_exact_bisolution", True),
        ("state", "scope_boundary", "quasifree_state", True),
        ("26 rows", "claim_flags", "BERGER_26_ROW_BRST_HADAMARD", True),
        ("quantum", "claim_flags", "QUANTUM_CLAIM", True),
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
