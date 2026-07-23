#!/usr/bin/env python3
"""Independent structural and log verifier for the Taylor2 q0 sentinel."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "transport_c00_taylor2.forge"
LOG = HERE / "sentinel_q00.log"
METADATA = HERE / "source_metadata.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_log(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("BEGIN q=0\n"):
        errors.append("missing q0 begin")
    shells = re.findall(
        r"^SHELL q=0 shell=(\d+) chart=(\d+) rank=(\d+).*"
        r"direct=true overlap=true switches=(\d+)$",
        text,
        re.MULTILINE,
    )
    if shells != [("0", "11", "6", "0"), ("1", "11", "6", "0")]:
        errors.append(f"unexpected certified shell prefix: {shells}")
    if len(re.findall(r"^HEARTBEAT q=0 ", text, re.MULTILINE)) != 12:
        errors.append("expected twelve q0 heartbeats through shell 2")
    refusal = "REFUSE amplitude-rank q=0 shell=2"
    if text.count(refusal) != 1:
        errors.append("missing unique shell-2 amplitude-rank refusal")
    if re.search(r"^PASS ", text, re.MULTILINE):
        errors.append("refused run contains PASS")
    if re.search(r"q=(?!0(?:\D|$))", text):
        errors.append("non-q0 execution found")
    if "AMPLITUDE_CENTER_RANK 6" not in text:
        errors.append("missing diagnostic center-rank separation")
    return errors


def verify() -> list[str]:
    errors = verify_log(LOG.read_text())
    metadata = json.loads(METADATA.read_text())
    if metadata["frozen_affine_source_sha256"] != (
        "6978e7532e7f30944b746db91fb58d2254bd3267607947b2c3e7ea5e9ed527c3"
    ):
        errors.append("frozen affine hash drift")
    if metadata["frozen_affine_source_commit"] != (
        "630880a6cb8d83efa286c585ffe68c52898e7f04"
    ):
        errors.append("frozen affine commit drift")
    if metadata["tango_commit"] != (
        "972aa4337b73cc0f632d9599fb345098bc8ccce8"
    ):
        errors.append("Tango pin drift")
    if metadata["source_sha256"] != sha256(SOURCE):
        errors.append("rendered source hash drift")
    source = SOURCE.read_text()
    required = {
        "degree-two import": "import math/ivtaylor;",
        "initializer lift": "ivtm_from_affine(hc_initial_model(cell))",
        "transition lift": "ivtm_from_affine(phi0)",
        "right action": "ivtm_solve_right(b,a)",
        "twenty charts": "while(c<20)",
        "shell count": "while(shell<23)",
        "panel count": "while(panel<256)",
        "rank cover": "ivtm_full_column_rank_cells(state.amplitude,64)",
        "separate amplitude": "pub amplitude: IvTaylorMat",
        "q0 only": "if(!hr_run(0))",
    }
    for label, marker in required.items():
        if marker not in source:
            errors.append(f"missing source invariant: {label}")
    return errors


if __name__ == "__main__":
    found = verify()
    if found:
        for item in found:
            print(f"FAIL {item}")
        raise SystemExit(1)
    print("verified=true status=TAYLOR2_AMPLITUDE_RANK_SHORTFALL q=0 shell=2")
