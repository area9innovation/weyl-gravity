"""Emit the local-anomaly to D-Cartan comparison certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from local_bv.algebra import canonical_sha256

from .local_anomaly_comparison import comparison_payload


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "local_anomaly_to_d_cartan_comparison.schema.json"

DEPENDENCIES = (
    "quantum-weyl/local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "quantum-weyl/local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json",
    "quantum-weyl/transfer/certificates/BERGER_54_ROW_D_CAUSAL_INPUT_IMPORT.json",
    "d_quotient_programme/registry/generators.json",
    "d_quotient_programme/registry/phase_spaces.json",
)
REGISTRY_DEPENDENCIES = DEPENDENCIES[-2:]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _registry_commit() -> str:
    return subprocess.check_output(
        [
            "git", "-C", str(REPOSITORY_ROOT), "log", "-1", "--format=%H", "--",
            *REGISTRY_DEPENDENCIES,
        ],
        text=True,
    ).strip()


def _committed_bytes(path: str, commit: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(REPOSITORY_ROOT), "show", f"{commit}:./{path}"]
    )


def _load(path: str, *, commit: str | None = None) -> dict[str, object]:
    payload = _committed_bytes(path, commit) if commit else (REPOSITORY_ROOT / path).read_bytes()
    return json.loads(payload)


def _semantic_input_checks() -> tuple[dict[str, str], str]:
    registry_commit = _registry_commit()
    even = _load(DEPENDENCIES[0])
    odd = _load(DEPENDENCIES[1])
    coefficients = _load(DEPENDENCIES[2])
    cartan = _load(DEPENDENCIES[3])
    berger = _load(DEPENDENCIES[4])
    generators = _load(DEPENDENCIES[5], commit=registry_commit)["generators"]
    phase_spaces = _load(DEPENDENCIES[6], commit=registry_commit)["phase_spaces"]
    if even["result_state"] != "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT":
        raise ValueError("even AFN0 quotient input is not complete")
    if odd["result_state"] != "COMPLETE_AFN0_ODD_CANDIDATE_QUOTIENT":
        raise ValueError("odd AFN0 quotient input is not complete")
    if not coefficients["claim_flags"]["CYLINDER_D_LOCAL_ANOMALY_PULLBACK_ZERO"]:
        raise ValueError("coefficient input does not certify the cylinder pullback")
    if cartan["result_state"] != "ALGEBRAIC_ENGINE_READY_PHYSICAL_CANDIDATES_INPUT_BLOCKED":
        raise ValueError("Cartan input no longer has the expected fail-closed state")
    if (
        berger.get("result_state")
        != "CLASSICAL_D_ACTION_IMPORTED_CAUSAL_ENDPOINT_REDUCED"
        or berger.get("quantum_execution_authorized") is not False
        or berger.get("conditional_causal_lift", {}).get("endpoint_status")
        != "NOT_CONSTRUCTED"
    ):
        raise ValueError("Berger D/causal input crossed its setting-specific boundary")
    if sum(row["generator_id"] == "D_compact" for row in generators) != 1:
        raise ValueError("D_compact registry entry is not unique")
    if sum(row["phase_space_id"] == "compact_quantum" for row in phase_spaces) != 1:
        raise ValueError("compact_quantum registry entry is not unique")
    sources = {
        path: (
            hashlib.sha256(_committed_bytes(path, registry_commit)).hexdigest()
            if path in REGISTRY_DEPENDENCIES
            else _sha256(REPOSITORY_ROOT / path)
        )
        for path in DEPENDENCIES
    }
    return sources, registry_commit


def build_certificate() -> dict[str, object]:
    sources, registry_commit = _semantic_input_checks()
    payload = {
        **comparison_payload(),
        "provenance": {
            "source_sha256": sources,
            "source_manifest_sha256": canonical_sha256(sources),
            "registry_commit": registry_commit,
            "implementation": "quantum-weyl/cartan/local_anomaly_comparison.py",
            "schema": "quantum-weyl/cartan/schema/local_anomaly_to_d_cartan_comparison.schema.json",
        },
    }
    return {**payload, "certificate_hash": canonical_sha256(payload)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"local anomaly comparison certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("LOCAL ANOMALY -> D CARTAN: CYLINDER PULLBACK ZERO; TARGET MAP UNDEFINED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
