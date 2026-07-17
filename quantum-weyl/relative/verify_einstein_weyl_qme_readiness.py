#!/usr/bin/env python3
"""Independent verifier for quantum relative Einstein--Weyl readiness."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import subprocess

from local_bv.schema_validation import validate_instance

from .einstein_weyl_qme_readiness import (
    GLOBAL_A104,
    LOCAL_CARTAN,
    PLANNING_BRIEF,
    QUADRATIC_PREFLIGHT,
    ROADMAP,
    STANDARD_INCLUSION,
    validate,
)
from .einstein_weyl_qme_readiness_certificate import HERE, OUTPUT


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads((HERE / "schema/einstein-weyl-qme-readiness-v1.schema.json").read_text())
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)
    dependencies = {
        "standard_harmonic_inclusion_contribution": STANDARD_INCLUSION,
        "quadratic_channel_preflight_contribution": QUADRATIC_PREFLIGHT,
        "local_D_Cartan_comparison": LOCAL_CARTAN,
        "Berger_global_A104_partial": GLOBAL_A104,
        "quantum_team_brief": PLANNING_BRIEF,
        "universe_building_roadmap": ROADMAP,
    }
    for name, path in dependencies.items():
        reference = certificate["dependency_refs"][name]
        if reference["sha256"] != _sha256(path):
            raise ValueError(f"dependency hash mismatch: {name}")
    for name, evidence in certificate["pinned_classical_evidence"].items():
        content = subprocess.check_output(
            ["git", "-C", str(HERE.parents[1]), "show", f"{evidence['commit']}:./{evidence['path']}"]
        )
        if hashlib.sha256(content).hexdigest() != evidence["sha256"]:
            raise ValueError(f"pinned classical evidence mismatch: {name}")
    mutations = (
        ("classical_import_gate", "status", "SATISFIED"),
        ("shared_relative_row", "quantum_lift", "QME_RESTORED"),
        ("qme_and_transfer_gate", "residual_quantum_transfer_authorized", True),
        ("claim_flags", "RELATIVE_ANOMALY_CLASS_DEFINED", True),
        ("claim_flags", "RELATIVE_HADAMARD_STATE", True),
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
    print("QUANTUM RELATIVE EINSTEIN-WEYL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
