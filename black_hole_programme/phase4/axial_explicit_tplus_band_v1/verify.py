#!/usr/bin/env python3
"""Independent metadata verifier for the correlated successor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    if data.get("status") != "CORRELATED_OUTGOING_SUCCESSOR_PASS_R4_OPEN":
        raise AssertionError("successor is not certified")
    imported = data["imports"]["checkpoint"]
    if sha256(ROOT / imported["path"]) != imported["sha256"]:
        raise AssertionError("predecessor hash drift")
    successor = data["successor"]
    checkpoint_path = ROOT / successor["checkpoint"]
    manifest_path = ROOT / successor["run_manifest"]
    if sha256(checkpoint_path) != successor["checkpoint_sha256"]:
        raise AssertionError("successor checkpoint hash drift")
    if sha256(manifest_path) != successor["run_manifest_sha256"]:
        raise AssertionError("run manifest hash drift")
    checkpoint = json.loads(checkpoint_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    summary = manifest["run"]["summary"]
    if checkpoint["payload_sha256"] != successor["payload_sha256"]:
        raise AssertionError("payload identity drift")
    if checkpoint["payload"]["generator"] != 7315:
        raise AssertionError("frequency generator drift")
    if manifest["selected_candidate"]["final_radius"] != "487/16":
        raise AssertionError("radial endpoint drift")
    if not summary["coefficients"] or not summary["containment"]:
        raise AssertionError("direct/jet boundary gate failed")
    if float(summary["tail"]) >= 0.5 or float(summary["width"]) >= 10.0:
        raise AssertionError("validated tail or width gate failed")
    flags = data["claim_flags"]
    for key in (
        "complete_outgoing_frame_at_r4",
        "explicit_Tplus_certified",
        "reflection_or_stokes_certified",
    ):
        if flags.get(key) is not False:
            raise AssertionError(f"overclaim: {key}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certificate", type=Path, default=HERE / "certificate.json"
    )
    args = parser.parse_args()
    verify(args.certificate)
    print("PASS: correlated outgoing successor")


if __name__ == "__main__":
    main()
