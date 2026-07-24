from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import AuditError, PACKAGE, build_certificate, sha256


def verify_certificate(root: Path, certificate_path: Path | None = None) -> None:
    path = certificate_path or (root / PACKAGE / "certificate.json")
    actual = json.loads(path.read_text(encoding="utf-8"))
    expected = build_certificate(root)
    if actual != expected:
        raise AuditError("certificate differs from independently reconstructed theorem")
    receipt_path = root / PACKAGE / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["status"] != "PASS":
        raise AuditError("receipt status is not PASS")
    if receipt["artifacts"]["certificate"]["sha256"] != sha256(path):
        raise AuditError("certificate hash in receipt is stale")
    for name, artifact in receipt["artifacts"].items():
        if name == "certificate":
            continue
        artifact_path = root / artifact["path"]
        if artifact["sha256"] != sha256(artifact_path):
            raise AuditError(f"{name} hash in receipt is stale")
    if receipt["does_not_establish"] != actual["does_not_establish"]:
        raise AuditError("claim boundary differs between certificate and receipt")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        verify_certificate(root, args.certificate)
    except (AuditError, KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print("PASS: transport-free axial finite-flux channel classification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
