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
    RELATIVE_FUNCTOR_PREFLIGHT,
    ROADMAP,
    STANDARD_INCLUSION,
    TRIANGLE_PREFLIGHT,
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
        "relative_linear_triangle_preflight": TRIANGLE_PREFLIGHT,
        "relative_functor_preflight": RELATIVE_FUNCTOR_PREFLIGHT,
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
        working = HERE.parents[1] / evidence["path"]
        if not working.is_file() or working.read_bytes() != content:
            raise ValueError(f"working/pinned classical evidence mismatch: {name}")
    evidence_dependencies = {
        "relative_linear_triangle_preflight": "relative_linear_triangle_preflight",
        "relative_functor_preflight": "relative_functor_preflight",
    }
    for evidence_name, dependency_name in evidence_dependencies.items():
        evidence = certificate["pinned_classical_evidence"][evidence_name]
        dependency = certificate["dependency_refs"][dependency_name]
        if (
            evidence["path"] != dependency["path"]
            or evidence["sha256"] != dependency["sha256"]
        ):
            raise ValueError(f"working/pinned seam mismatch: {evidence_name}")
    triangle = json.loads(TRIANGLE_PREFLIGHT.read_text())
    classification = triangle.get("classification", {})
    if (
        classification.get("principal_BV_chain_map_and_cone_certified") is not True
        or classification.get("generic_axial_offshell_chain_map_certified") is not True
        or classification.get("relative_linear_triangle_V1_certified") is not False
        or classification.get("quantum_import_gate_satisfied") is not False
    ):
        raise ValueError("partial triangle was over-promoted or weakened")
    functor = json.loads(RELATIVE_FUNCTOR_PREFLIGHT.read_text())
    if (
        functor.get("flags", {}).get("RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1")
        is not False
        or functor.get("flags", {}).get("EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED")
        is not False
    ):
        raise ValueError("relative functor preflight was over-promoted")
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
