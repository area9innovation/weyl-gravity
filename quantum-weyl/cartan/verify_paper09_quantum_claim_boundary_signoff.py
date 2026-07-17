"""Independent verifier for the Paper IX quantum claim-boundary signoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/cartan/certificates/PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF.json"
SCHEMA = ROOT / "quantum-weyl/cartan/schema/paper09-quantum-claim-boundary-signoff-v1.schema.json"


def _git_blob(commit: str, relpath: str) -> bytes:
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    return subprocess.check_output(
        ["git", "show", f"{commit}:{prefix}{relpath}"], cwd=ROOT
    )


def _at(obj: object, path: str) -> object:
    cur = obj
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            raise AssertionError(f"missing semantic path {path}")
        cur = cur[key]
    return cur


def main() -> None:
    cert = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(cert, schema, cls=jsonschema.Draft202012Validator)

    for key, item in cert["source_manifest"].items():
        path = ROOT / item["path"]
        blob = _git_blob(item["commit"], item["path"])
        if hashlib.sha256(blob).hexdigest() != item["sha256"]:
            raise AssertionError(f"pinned source hash mismatch: {item['path']}")
        if key != "claim_table" and hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise AssertionError(f"live source hash mismatch: {item['path']}")

    manifest = cert["source_manifest"]
    loaded = {}
    for key, item in manifest.items():
        if not item["path"].endswith(".json"):
            continue
        if key == "claim_table":
            raw = _git_blob(item["commit"], item["path"])
            loaded[key] = json.loads(raw)
        else:
            loaded[key] = json.loads((ROOT / item["path"]).read_text())
    generator = loaded["generator_audit"]
    arity3 = loaded["causal_k_cartan_arity_three"]
    qboundary = loaded["quantum_cartan_boundary"]
    paper = (ROOT / manifest["paper"]["path"]).read_text()
    paper_flat = " ".join(paper.split())

    assertions = {
        "generator corrected to K": _at(generator, "flags.EXPORTED_UNARY_GENERATOR_IS_K") is True,
        "raw D rejected": _at(generator, "flags.EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D") is False,
        "raw D affine": _at(generator, "flags.AFFINE_D_ZERO_ARITY_NONZERO") is True,
        "no affine D primitive": _at(generator, "flags.AFFINE_D_CARTAN_CONSTRUCTED") is False,
        "arity three classical complete": _at(arity3, "flags.BERGER_ARITY_THREE_D_CARTAN_FULL_4D")
        is True,
        "arity three nonquantum": _at(arity3, "flags.QUANTUM_CLAIM") is False,
        "arity three no Hadamard": _at(arity3, "flags.BERGER_HADAMARD_DATA") is False,
        "quantum boundary blocked": qboundary["claim_status"] == "BLOCKED",
        "paper theorem is K": "[Q,\\iota_K]-L_K" in paper,
        "paper rejects affine D": "No affine $D$-Cartan theorem is claimed" in paper_flat
        and "L_D^{(0)}=\\omega R(\\rho,0)" in paper,
        "paper rejects quantum theorem": "quantum-master-equation result" in paper,
        "signoff accepts classical K": cert["theorem_flags"][
            "PAPER09_CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_ACCEPTED"
        ]
        is True,
        "signoff blocks affine D": cert["theorem_flags"]["PAPER09_AFFINE_D_CARTAN_ACCEPTED"]
        is False,
        "signoff blocks Hadamard": cert["theorem_flags"]["PAPER09_HADAMARD_ACCEPTED"]
        is False,
        "signoff blocks QME": cert["theorem_flags"]["PAPER09_QME_ACCEPTED"] is False,
        "signoff blocks anomaly": cert["theorem_flags"][
            "PAPER09_ANOMALY_CANCELLATION_ACCEPTED"
        ]
        is False,
        "signoff blocks quantum": cert["theorem_flags"]["PAPER09_QUANTUM_PROMOTION_ACCEPTED"]
        is False,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise AssertionError(f"independent signoff verification failed: {failed}")
    print("Paper IX quantum claim-boundary signoff: PASS")


if __name__ == "__main__":
    main()
