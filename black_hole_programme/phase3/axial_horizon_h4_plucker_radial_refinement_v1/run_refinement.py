#!/usr/bin/env python3
"""Run 2x then, only if needed, 4x radial refinement fail-closed."""
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


def compile_attempt(source: Path, binary: Path, log: Path) -> None:
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


def run_attempt(source: Path, binary: Path, log: Path) -> int:
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
        f"PLUCKER_SOURCE_SHA256={produce.sha256(source)}\n"
        + completed.stdout
        + completed.stderr
        + f"PLUCKER_PROCESS_EXIT={completed.returncode}\n"
        + f"PLUCKER_ELAPSED_MILLISECONDS={elapsed}\n"
    )
    return completed.returncode


def heartbeat_hashes(text: str) -> list[str]:
    lines = [
        line for line in text.splitlines()
        if line.startswith("PLUCKER_SEGMENT ")
    ]
    return [
        hashlib.sha256((line + "\n").encode()).hexdigest()
        for line in lines[:19]
    ]


def attempt_entry(factor: int, child: int, metadata: dict) -> dict:
    attempt_paths = produce.paths(factor, child)
    binary = Path(f"/tmp/axial-h4-plucker-radial-{factor}x-{child}-v1")
    compile_attempt(
        attempt_paths["source"], binary, attempt_paths["compile_log"]
    )
    code = run_attempt(
        attempt_paths["source"], binary, attempt_paths["run_log"]
    )
    if code not in (3, 42):
        raise RuntimeError(f"unexpected attempt exit {code}")
    text = attempt_paths["run_log"].read_text()
    refusal = re.findall(
        r"^RADIAL_REFINEMENT_REFUSE factor=(\d+) panel=(\d+) "
        r"raw_code=(\d+) correlated_code=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    defect = re.findall(
        r"^CORRELATED_FUNCTIONAL_DEFECT lo=([^ ]+) hi=([^ ]+) "
        r"norm=([^ ]+)$",
        text,
        flags=re.MULTILINE,
    )
    passes = re.findall(
        r"^RADIAL_REFINEMENT_PASS factor=(\d+) panels=(\d+) "
        r"final_pivot=(\d+) margin=([^ ]+) norm=([^ ]+)$",
        text,
        flags=re.MULTILINE,
    )
    elapsed = re.findall(
        r"^PLUCKER_ELAPSED_MILLISECONDS=(\d+)$",
        text,
        flags=re.MULTILINE,
    )
    if code == 3 and (len(refusal) != 1 or len(defect) != 1):
        raise RuntimeError("refinement refused without typed evidence")
    if code == 42 and len(passes) != 1:
        raise RuntimeError("refinement passed without typed evidence")
    return {
        "factor": factor,
        "child_index": child,
        "frequency_cell": metadata["frequency_cell"],
        "radial_panel_width": produce.RADIAL_WIDTHS[factor],
        "source_path": str(attempt_paths["source"].relative_to(produce.HERE)),
        "source_sha256": metadata["source_sha256"],
        "metadata_path": str(
            attempt_paths["metadata"].relative_to(produce.HERE)
        ),
        "compile_log_path": str(
            attempt_paths["compile_log"].relative_to(produce.HERE)
        ),
        "run_log_path": str(
            attempt_paths["run_log"].relative_to(produce.HERE)
        ),
        "run_log_sha256": produce.sha256(attempt_paths["run_log"]),
        "process_exit": code,
        "status": "PASS" if code == 42 else "REFUSED",
        "prefix_heartbeat_hashes": heartbeat_hashes(text),
        "refusal": (
            None
            if code == 42
            else {
                "panel": int(refusal[0][1]),
                "raw_code": int(refusal[0][2]),
                "correlated_code": int(refusal[0][3]),
            }
        ),
        "defect": (
            None
            if code == 42
            else {
                "lo": defect[0][0],
                "hi": defect[0][1],
                "norm": defect[0][2],
                "interval_width": str(
                    float(defect[0][1]) - float(defect[0][0])
                ),
            }
        ),
        "pass_witness": (
            None
            if code == 3
            else {
                "final_pivot": int(passes[0][2]),
                "margin": passes[0][3],
                "norm": passes[0][4],
            }
        ),
        "elapsed_milliseconds": int(elapsed[0]),
    }


def main() -> int:
    upstream = produce.checked_upstream()
    factor_results = []
    decisive_factor = None
    for factor in produce.FACTORS:
        metadata = produce.write_factor(factor)
        entries = [
            attempt_entry(factor, child, metadata[child])
            for child in (0, 1)
        ]
        cover_pass = all(entry["status"] == "PASS" for entry in entries)
        factor_results.append({
            "factor": factor,
            "radial_panel_width": produce.RADIAL_WIDTHS[factor],
            "cover_pass": cover_pass,
            "children": entries,
        })
        if cover_pass:
            decisive_factor = factor
            break
    status = (
        "CERTIFIED_RADIAL_REFINEMENT_PASS"
        if decisive_factor is not None
        else "CERTIFIED_RADIAL_REFINEMENT_OBSTRUCTION"
    )
    manifest = {
        "schema": "phase3-axial-h4-plucker-radial-refinement-manifest-v1",
        "status": status,
        "scope": {
            "frequency_children": [0, 1],
            "radial_boundary": {"shell": 4, "segment": 3},
            "factors_in_order": [result["factor"] for result in factor_results],
            "stop_on_first_cover_pass": True,
            "no_later_shell": True,
        },
        "upstream_certificate_sha256": (
            produce.EXPECTED_UPSTREAM_CERTIFICATE_SHA256
        ),
        "upstream_manifest_sha256": (
            produce.EXPECTED_UPSTREAM_MANIFEST_SHA256
        ),
        "baseline_prefix_heartbeat_hashes": [
            heartbeat_hashes(
                (correlated_path := (
                    produce.UPSTREAM_MANIFEST.parent
                    / upstream["children"][child]["run_log_path"]
                )).read_text()
            )
            for child in (0, 1)
        ],
        "decisive_factor": decisive_factor,
        "attempts": factor_results,
        "interpretation": (
            "A PASS certifies a nonzero Pluecker witness only at the "
            "declared refined boundary. A refusal means the validated "
            "raw coordinates and midpoint-Hermitian functional still "
            "contain zero; it does not establish rank loss."
        ),
        "does_not_establish": [
            "rank loss when a refined interval still contains zero",
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
        f"{status} factors={manifest['scope']['factors_in_order']} "
        f"manifest={manifest['payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
