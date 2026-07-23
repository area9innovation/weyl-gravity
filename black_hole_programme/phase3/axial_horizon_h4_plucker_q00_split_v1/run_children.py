#!/usr/bin/env python3
"""Compile and run both exact q00 Plücker children fail-closed."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from . import produce

FORGE = Path("/home/alstrup/area9/tango/forge/forge")
FORGE_LIB = Path("/home/alstrup/area9/tango/forge/lib")


def compile_child(source: Path, binary: Path, log: Path) -> None:
    started = time.monotonic()
    completed = subprocess.run(
        [str(FORGE), "-o", str(binary), str(source)],
        cwd=produce.ROOT,
        env={**os.environ, "FORGE_LIB": str(FORGE_LIB)},
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = int((time.monotonic() - started) * 1000)
    log.write_text(
        completed.stdout
        + completed.stderr
        + f"COMPILE_PROCESS_EXIT={completed.returncode}\n"
        + f"COMPILE_ELAPSED_MILLISECONDS={elapsed}\n"
    )
    if completed.returncode != 0 or not binary.exists():
        raise RuntimeError(f"child compile failed: {source.name}")


def run_child(source: Path, binary: Path, log: Path) -> int:
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    started = time.monotonic()
    completed = subprocess.run(
        [str(binary)],
        cwd=produce.ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = int((time.monotonic() - started) * 1000)
    log.write_text(
        f"PLUCKER_SOURCE_SHA256={source_sha}\n"
        + completed.stdout
        + completed.stderr
        + f"PLUCKER_PROCESS_EXIT={completed.returncode}\n"
        + f"PLUCKER_ELAPSED_MILLISECONDS={elapsed}\n"
    )
    return completed.returncode


def main() -> int:
    children_metadata = produce.write_sources()
    entries = []
    for index, metadata in enumerate(children_metadata):
        paths = produce.paths(index)
        binary = Path(f"/tmp/axial-h4-plucker-q00-split-{index}-v1")
        compile_child(paths["source"], binary, paths["compile_log"])
        code = run_child(paths["source"], binary, paths["run_log"])
        text = paths["run_log"].read_text()
        refusal = re.findall(
            r"^PLUCKER_REFUSE .*$", text, flags=re.MULTILINE
        )
        if code not in (3, 42):
            raise RuntimeError(f"unexpected child exit {code}")
        if code == 3 and len(refusal) != 1:
            raise RuntimeError("child failed without one typed refusal")
        entries.append(
            {
                "child_index": index,
                "frequency_cell": metadata["frequency_cell"],
                "source_path": str(
                    paths["source"].relative_to(produce.HERE)
                ),
                "source_sha256": metadata["source_sha256"],
                "metadata_path": str(
                    paths["metadata"].relative_to(produce.HERE)
                ),
                "compile_log_path": str(
                    paths["compile_log"].relative_to(produce.HERE)
                ),
                "run_log_path": str(
                    paths["run_log"].relative_to(produce.HERE)
                ),
                "run_log_sha256": hashlib.sha256(
                    paths["run_log"].read_bytes()
                ).hexdigest(),
                "process_exit": code,
                "terminal_refusal": refusal[0] if refusal else None,
            }
        )
    passed = all(entry["process_exit"] == 42 for entry in entries)
    manifest = {
        "schema": "phase3-axial-h4-plucker-q00-split-cover-v1",
        "status": "COVER_PASS" if passed else "COVER_REFUSED",
        "parent_cell": [
            produce.rational_text(value) for value in produce.Q00
        ],
        "split_point": produce.rational_text(produce.MIDPOINT),
        "child_cells": [
            [produce.rational_text(value) for value in cell]
            for cell in produce.CHILD_CELLS
        ],
        "target": {"shell": 4, "segment": 3},
        "parent_certificate_sha256": (
            produce.EXPECTED_PARENT_CERTIFICATE_SHA256
        ),
        "shortfall_certificate_sha256": (
            produce.EXPECTED_SHORTFALL_CERTIFICATE_SHA256
        ),
        "children": entries,
        "does_not_establish": [
            "transport beyond shell 4 segment 3",
            "the complete 23-shell horizon transport",
            "canonical endpoint amplitudes",
            "a horizon-to-infinity scattering theorem",
        ],
    }
    manifest["payload_sha256"] = produce.canonical_hash(manifest)
    produce.MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(
        f"{manifest['status']} children={len(entries)} "
        f"manifest={manifest['payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
