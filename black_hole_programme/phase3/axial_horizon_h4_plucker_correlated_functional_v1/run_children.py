#!/usr/bin/env python3
"""Compile and run both one-boundary correlated replays."""
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


def compile_source(source: Path, binary: Path, log: Path) -> None:
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
        raise RuntimeError(f"compile failed: {source.name}")


def run_source(source: Path, binary: Path, log: Path) -> int:
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
    metadata = produce.write_sources()
    entries = []
    for index, child_metadata in enumerate(metadata):
        child_paths = produce.paths(index)
        binary = Path(f"/tmp/axial-h4-plucker-correlated-{index}-v1")
        compile_source(
            child_paths["source"], binary, child_paths["compile_log"]
        )
        code = run_source(
            child_paths["source"], binary, child_paths["run_log"]
        )
        text = child_paths["run_log"].read_text()
        refusals = re.findall(
            r"^(?:PLUCKER_REFUSE|CORRELATED_FUNCTIONAL_DEFECT).*$",
            text,
            flags=re.MULTILINE,
        )
        if code not in (3, 42):
            raise RuntimeError(f"unexpected replay exit {code}")
        if code == 3 and not refusals:
            raise RuntimeError("replay failed without typed evidence")
        entries.append(
            {
                "child_index": index,
                "frequency_cell": child_metadata["frequency_cell"],
                "source_path": str(
                    child_paths["source"].relative_to(produce.HERE)
                ),
                "source_sha256": child_metadata["source_sha256"],
                "metadata_path": str(
                    child_paths["metadata"].relative_to(produce.HERE)
                ),
                "compile_log_path": str(
                    child_paths["compile_log"].relative_to(produce.HERE)
                ),
                "run_log_path": str(
                    child_paths["run_log"].relative_to(produce.HERE)
                ),
                "run_log_sha256": hashlib.sha256(
                    child_paths["run_log"].read_bytes()
                ).hexdigest(),
                "process_exit": code,
                "terminal_evidence": refusals,
            }
        )
    passed = all(entry["process_exit"] == 42 for entry in entries)
    manifest = {
        "schema": (
            "phase3-axial-h4-plucker-correlated-functional-manifest-v1"
        ),
        "status": "CORRELATED_PASS" if passed else "CORRELATED_REFUSED",
        "scope": {
            "children": [0, 1],
            "replayed_boundary": {"shell": 4, "segment": 3},
            "no_later_shell": True,
        },
        "split_certificate_sha256": (
            produce.EXPECTED_SPLIT_CERTIFICATE_SHA256
        ),
        "split_manifest_sha256": produce.EXPECTED_SPLIT_MANIFEST_SHA256,
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
        f"{manifest['status']} children=2 "
        f"manifest={manifest['payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
