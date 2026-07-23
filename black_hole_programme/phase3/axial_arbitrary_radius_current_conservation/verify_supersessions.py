"""Independent fail-closed checks for superseded interpolation shortfalls."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SHORTFALLS = [
    HERE / "superseded-26-node-shortfall.json",
    HERE / "superseded-27-node-shortfall.json",
]


class SupersessionError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_superseded_shortfall(payload: dict[str, Any]) -> None:
    if payload.get("disposition") != "SUPERSEDED_SHORTFALL_NOT_ACCEPTED_AS_PROOF":
        raise SupersessionError("superseded interpolation artifact was promoted")
    flags = payload.get("claim_flags", {})
    if flags.get("arbitrary_radius_literal_current_reconstructed"):
        raise SupersessionError("shortfall claims arbitrary-radius reconstruction")
    if flags.get("conservation_identity_established"):
        raise SupersessionError("shortfall claims conservation")
    for key in ("superseded_artifact", "superseded_receipt"):
        item = payload[key]
        path = ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise SupersessionError(f"shortfall provenance drift: {item['path']}")


def main() -> None:
    for path in SHORTFALLS:
        verify_superseded_shortfall(json.loads(path.read_text()))
    print("PASS: superseded interpolation artifacts remain fail-closed")


if __name__ == "__main__":
    main()
