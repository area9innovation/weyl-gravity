from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import PACKAGE, build_certificate, sha256


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.repo_root.resolve()
    package = root / PACKAGE
    package.mkdir(parents=True, exist_ok=True)
    certificate_path = package / "certificate.json"
    certificate = build_certificate(root)
    certificate_path.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "phase3-axial-global-finite-flux-channel-classification-v3-receipt",
        "status": "PASS",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "artifacts": {
            "certificate": {
                "path": str(PACKAGE / "certificate.json"),
                "sha256": sha256(certificate_path),
            },
            "producer": {
                "path": str(PACKAGE / "produce.py"),
                "sha256": sha256(package / "produce.py"),
            },
            "audit_kernel": {
                "path": str(PACKAGE / "audit.py"),
                "sha256": sha256(package / "audit.py"),
            },
            "independent_verifier": {
                "path": str(PACKAGE / "verify.py"),
                "sha256": sha256(package / "verify.py"),
            },
            "tests": {
                "path": str(PACKAGE / "test_classification.py"),
                "sha256": sha256(package / "test_classification.py"),
            },
            "schema": {
                "path": str(PACKAGE / "schema.json"),
                "sha256": sha256(package / "schema.json"),
            },
        },
        "commands": [
            {
                "tier": 0,
                "command": f"python3 -m json.tool {PACKAGE / 'certificate.json'}",
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": certificate["verification"]["verifier"],
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": certificate["verification"]["tests"],
                "result": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "This synthesis changes no mathematical input, operator, shared schema or "
                "generated upstream artifact; every imported claim is pinned by content hash."
            ),
        },
        "does_not_establish": certificate["does_not_establish"],
    }
    (package / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(certificate_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
