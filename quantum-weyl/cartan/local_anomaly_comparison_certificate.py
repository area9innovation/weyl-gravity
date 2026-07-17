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
    "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json",
    "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json",
    "quantum-weyl/cartan/certificates/RENORMALIZED_D_WARD_INSERTION_CONTRACT.json",
    "quantum-weyl/lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
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
    g2 = _load(DEPENDENCIES[0])
    h14 = _load(DEPENDENCIES[1])
    coefficients = _load(DEPENDENCIES[2])
    cartan = _load(DEPENDENCIES[3])
    ward_contract = _load(DEPENDENCIES[4])
    causal_chain = _load(DEPENDENCIES[5])
    berger = _load(DEPENDENCIES[6])
    generators = _load(DEPENDENCIES[7], commit=registry_commit)["generators"]
    phase_spaces = _load(DEPENDENCIES[8], commit=registry_commit)["phase_spaces"]
    if (
        g2["result_state"]
        != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN"
        or g2["claim_flags"]["FULL_BV_G2_COMPLETE"] is not True
    ):
        raise ValueError("full local BV G2 input is not complete")
    if (
        h14["result_state"] != "GAUGE_FIXED_BV_LOCAL_COHOMOLOGY_COMPLETE"
        or h14["parity_dimensions"] != {"even": 2, "odd": 1}
        or h14["claim_flags"]["COHOMOLOGY_COMPLETE"] is not True
    ):
        raise ValueError("gauge-fixed H14 quotient input is not complete")
    if not coefficients["claim_flags"]["CYLINDER_D_LOCAL_ANOMALY_PULLBACK_ZERO"]:
        raise ValueError("coefficient input does not certify the cylinder pullback")
    if cartan["result_state"] != "ALGEBRAIC_ENGINE_READY_PHYSICAL_CANDIDATES_INPUT_BLOCKED":
        raise ValueError("Cartan input no longer has the expected fail-closed state")
    if (
        ward_contract.get("result_state")
        != "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED"
        or ward_contract.get("qme_status") != "NOT_COMPUTED"
        or ward_contract.get("quantum_cartan_status") != "NO_VERDICT"
    ):
        raise ValueError("Ward insertion contract crossed its input boundary")
    causal_flags = causal_chain.get("claim_flags", {})
    if (
        causal_chain.get("result_state")
        != "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN"
        or causal_flags.get("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED")
        is not True
        or causal_flags.get("BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED")
        is not True
        or causal_flags.get("BERGER_HADAMARD_DATA") is not False
        or causal_flags.get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("causal-chain/Hadamard boundary drifted")
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
