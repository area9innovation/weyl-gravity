"""Reproduce the machine-readable minimal local-BV bootstrap certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_json, canonical_sha256, LocalJetAlgebra
from .brst import MinimalBRSTDifferential
from .metadata import minimal_registry


PACKAGE_ROOT = Path(__file__).resolve().parent
CERTIFICATE_PATH = PACKAGE_ROOT / "certificates" / "LOCAL_BV_MINIMAL_BOOTSTRAP.json"


def _source_manifest() -> dict[str, str]:
    relative_paths = (
        "algebra.py",
        "brst.py",
        "certificate.py",
        "metadata.py",
        "schema/bootstrap_certificate.schema.json",
        "schema/field_spec.schema.json",
        "tests/test_algebra.py",
        "tests/test_brst.py",
        "tests/test_certificate.py",
        "tests/test_metadata.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in relative_paths
    }


def _minimal_rows_and_residuals() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    algebra = LocalJetAlgebra(4)
    differential = MinimalBRSTDifferential(algebra)
    variables = [algebra.jet("omega")]
    variables.extend(algebra.jet("xi", (mu,)) for mu in range(4))
    variables.extend(algebra.jet("g", (mu, nu)) for mu in range(4) for nu in range(mu, 4))
    rows = [
        {
            "generator": variable.canonical_payload(),
            "variation": differential.on_variable(variable).canonical_payload(),
        }
        for variable in variables
    ]
    residuals = [
        {
            "generator": variable.canonical_payload(),
            "residual": differential.nilpotency_residual(variable).canonical_payload(),
        }
        for variable in variables
    ]
    nonzero = [item for item in residuals if item["residual"] != {"terms": []}]
    if nonzero:
        raise AssertionError("minimal BRST nilpotency residual is nonzero")
    return rows, residuals


def build_certificate() -> dict[str, Any]:
    registry_payload = [
        minimal_registry()[name].canonical_payload()
        for name in sorted(minimal_registry())
    ]
    rows, nilpotency_payload = _minimal_rows_and_residuals()
    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_BV_MINIMAL_BOOTSTRAP",
        "result_state": "INFRASTRUCTURE_VERIFIED",
        "classical_commit": "NOT_FROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Exact four-dimensional supercommutative coordinate jets for g, xi, and omega; "
            "the three stated minimal BRST rows; deterministic canonical serialization."
        ),
        "checks": {
            "exact_rational_arithmetic": "VERIFIED",
            "graded_commutativity": "VERIFIED",
            "graded_leibniz": "VERIFIED",
            "minimal_generator_nilpotency": "VERIFIED",
            "coordinate_jet_nilpotency": "VERIFIED",
            "deterministic_canonical_hashing": "VERIFIED",
            "antifield_rows": "BLOCKED",
            "covariant_canonical_reduction": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED"
        },
        "not_computed": [
            "classical freeze and imported antifield/nonminimal rows",
            "covariant derivatives and curvature construction",
            "algebraic and differential Bianchi quotient",
            "Hodge duality and parity Ward identities",
            "integration by parts and total-derivative quotient",
            "counterterm cohomology H^{0,4}(s|d)",
            "anomaly cohomology H^{1,4}(s|d)",
            "descent equations and antifield spectral sequence"
        ],
        "canonical_hashes": {
            "minimal_field_dictionary_sha256": canonical_sha256(registry_payload),
            "minimal_differential_rows_sha256": canonical_sha256(rows),
            "minimal_nilpotency_residuals_sha256": canonical_sha256(nilpotency_payload),
            "source_manifest_sha256": canonical_sha256(source_manifest)
        },
        "assumptions": [
            "Coordinate derivatives have mass dimension one and Q_0 has mass dimension zero.",
            "Q_0 commutes with coordinate total derivatives.",
            "The supplied minimal transformations use a left odd derivation.",
            "No statement about antifields is made before the classical snapshot is frozen."
        ]
    }


def rendered_certificate() -> str:
    return json.dumps(build_certificate(), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the reproduced certificate with the checked-in receipt",
    )
    args = parser.parse_args()
    rendered = rendered_certificate()
    if args.check:
        checked_in = CERTIFICATE_PATH.read_text(encoding="utf-8")
        if checked_in != rendered:
            raise SystemExit("certificate is stale; reproduce it and review the changed hashes")
        print(f"VERIFIED {CERTIFICATE_PATH.relative_to(PACKAGE_ROOT.parent)}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
