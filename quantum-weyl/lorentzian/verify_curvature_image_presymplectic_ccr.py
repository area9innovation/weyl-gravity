#!/usr/bin/env python3
"""Independent verifier for the curvature-image presymplectic CCR algebra."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .curvature_image_presymplectic_ccr import (
    algebraic_well_definedness_replay,
    validate,
)
from .curvature_image_presymplectic_ccr_certificate import HERE, OUTPUT


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    certificate = json.loads(OUTPUT.read_text())
    validate(certificate)
    if certificate["well_definedness_replay"] != algebraic_well_definedness_replay():
        raise ValueError("independent CCR well-definedness replay mismatch")
    for name, ref in certificate["dependency_refs"].items():
        mapping = {
            "curvature_status": "../../covariant_completion/certificates/curved_curvature_prolongation_status.json",
            "curvature_graph": "../../covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json",
            "core_chain_map": "../../covariant_completion/certificates/curved_core_curvature_chain_map.json",
            "causal_quasi_isomorphism": "../../covariant_completion/certificates/covariant_causal_quasi_isomorphism.json",
            "causal_pairing": "../../covariant_completion/certificates/curved_direct_causal_pairing_transport.json",
            "final_status": "../../covariant_completion/certificates/completed_covariant_status.json",
        }
        dependency_path = HERE / mapping[name]
        dependency = json.loads(dependency_path.read_text())
        artifact_id = dependency.get("result_id") or dependency.get("schema")
        if artifact_id != ref["artifact_id"]:
            raise ValueError(f"dependency identity mismatch: {name}")
        if _sha256(dependency_path) != ref["sha256"]:
            raise ValueError(f"dependency hash mismatch: {name}")
    manifest = certificate["provenance"]["source_manifest"]
    for relative, expected in manifest.items():
        if _sha256(HERE / relative) != expected:
            raise ValueError(f"source manifest hash mismatch: {relative}")
    manifest_hash = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if manifest_hash != certificate["provenance"]["source_manifest_sha256"]:
        raise ValueError("source manifest aggregate hash mismatch")
    for flag in (
        "DIRECT_CURVATURE_CAUSAL_PROPAGATOR_CONSTRUCTED",
        "CURVATURE_HADAMARD_STATE_CONSTRUCTED",
        "PHYSICAL_POSITIVITY_CERTIFIED",
        "LORENTZIAN_QME_RESTORED",
        "INTERACTING_QUANTUM_THEORY",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation was accepted: {flag}")
    mutant = deepcopy(certificate)
    mutant["analytic_boundary"]["Hadamard_two_point_function"] = "CONSTRUCTED"
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("Hadamard boundary mutation was accepted")
    return certificate


def main() -> int:
    verify()
    print("CURVATURE IMAGE PRESYMPLECTIC CCR independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
