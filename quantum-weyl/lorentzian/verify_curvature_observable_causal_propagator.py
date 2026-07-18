#!/usr/bin/env python3
"""Independent verifier for the curvature observable causal propagator."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .curvature_observable_causal_propagator import (
    transport_identity_replay,
    validate,
)
from .curvature_observable_causal_propagator_certificate import HERE, OUTPUT


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    certificate = json.loads(OUTPUT.read_text())
    validate(certificate)
    if certificate["transport_identity_replay"] != transport_identity_replay():
        raise ValueError("independent curvature transport replay mismatch")
    mapping = {
        "curvature_CCR": "certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json",
        "curvature_graph": "../../covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json",
        "curvature_gauge_map": "../../covariant_completion/certificates/curved_curvature_state_gauge_chain_map.json",
        "full_causal_homotopy": "../../covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json",
        "causal_pairing": "../../covariant_completion/certificates/curved_direct_causal_pairing_transport.json",
    }
    for name, ref in certificate["dependency_refs"].items():
        path = HERE / mapping[name]
        dependency = json.loads(path.read_text())
        if (dependency.get("result_id") or dependency.get("schema")) != ref["artifact_id"]:
            raise ValueError(f"dependency identity mismatch: {name}")
        if _sha256(path) != ref["sha256"]:
            raise ValueError(f"dependency hash mismatch: {name}")
    manifest = certificate["provenance"]["source_manifest"]
    for relative, expected in manifest.items():
        if _sha256(HERE / relative) != expected:
            raise ValueError(f"source manifest hash mismatch: {relative}")
    aggregate = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if aggregate != certificate["provenance"]["source_manifest_sha256"]:
        raise ValueError("source manifest aggregate mismatch")
    for flag in (
        "AUTONOMOUS_CURVATURE_GREEN_OPERATORS_CONSTRUCTED",
        "CURVATURE_PROPAGATOR_WAVEFRONT_SET_CERTIFIED",
        "CURVATURE_HADAMARD_STATE_CONSTRUCTED",
        "PHYSICAL_POSITIVITY_CERTIFIED",
        "LORENTZIAN_QME_RESTORED",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][flag] = True
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation was accepted: {flag}")
    return certificate


def main() -> int:
    verify()
    print("CURVATURE OBSERVABLE CAUSAL PROPAGATOR independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
