#!/usr/bin/env python3
"""Compile and execute the bounded q00 continuation chain."""
from __future__ import annotations

import hashlib
import json
import os
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
        raise RuntimeError(f"Forge compile failed for {source.name}")


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


def relative(path: Path) -> str:
    return str(path.relative_to(produce.HERE))


def main() -> int:
    produce.HERE.mkdir(parents=True, exist_ok=True)
    produce.STATE_DIR.mkdir(parents=True, exist_ok=True)
    produce.CHUNK_DIR.mkdir(parents=True, exist_ok=True)

    exporter = produce.render_exporter()
    produce.EXPORTER_SOURCE.write_text(exporter)
    exporter_binary = Path("/tmp/axial-h4-plucker-boundary-exporter-v1")
    compile_log = produce.HERE / "boundary_exporter_compile.txt"
    initial_position = {"shell": 3, "segment": 0}
    current_path = produce.state_path(initial_position)
    reuse_export = False
    if produce.EXPORTER_LOG.exists() and current_path.exists():
        try:
            existing = json.loads(current_path.read_text())
            reuse_export = (
                existing["producer_source_sha256"]
                == hashlib.sha256(
                    produce.EXPORTER_SOURCE.read_bytes()
                ).hexdigest()
                and existing["producer_log_sha256"]
                == hashlib.sha256(
                    produce.EXPORTER_LOG.read_bytes()
                ).hexdigest()
                and existing["rows"]
                == produce.parse_state_lines(
                    produce.EXPORTER_LOG.read_text()
                )
            )
        except (KeyError, ValueError, json.JSONDecodeError, RuntimeError):
            reuse_export = False
    if reuse_export:
        current = json.loads(current_path.read_text())
    else:
        compile_source(produce.EXPORTER_SOURCE, exporter_binary, compile_log)
        if run_source(
            produce.EXPORTER_SOURCE, exporter_binary, produce.EXPORTER_LOG
        ) != 42:
            raise RuntimeError("certified-boundary exporter refused")
        current = produce.write_state(
            produce.EXPORTER_LOG,
            produce.EXPORTER_SOURCE,
            initial_position,
            current_path,
            None,
        )
    entries = []
    terminal = None

    for index, specification in enumerate(produce.CHUNKS):
        label = specification["label"]
        segments = specification["segments"]
        source, metadata_path = produce.write_chunk_source(
            current_path, label, segments
        )
        binary = Path(f"/tmp/axial-h4-plucker-{label}-v1")
        compile_log = produce.CHUNK_DIR / f"{label}_compile.txt"
        run_log = produce.CHUNK_DIR / f"{label}_run.txt"
        compile_source(source, binary, compile_log)
        code = run_source(source, binary, run_log)
        entry = {
            "index": index,
            "label": label,
            "segments": [list(value) for value in segments],
            "input_state_path": relative(current_path),
            "input_state_sha256": current["payload_sha256"],
            "source_path": relative(source),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "metadata_path": relative(metadata_path),
            "compile_log_path": relative(compile_log),
            "run_log_path": relative(run_log),
            "run_log_sha256": hashlib.sha256(
                run_log.read_bytes()
            ).hexdigest(),
            "process_exit": code,
        }
        if code != 42:
            match = __import__("re").search(
                r"^PLCHUNK_REFUSE (.+)$",
                run_log.read_text(),
                flags=__import__("re").MULTILINE,
            )
            if match is None:
                raise RuntimeError("chunk failed without typed refusal")
            terminal = {
                "status": "HONEST_REFUSAL",
                "chunk": label,
                "detail": match.group(1),
            }
            entries.append(entry)
            break

        output_position = specification["output_position"]
        output_path = produce.state_path(output_position)
        output_state = produce.write_state(
            run_log,
            source,
            output_position,
            output_path,
            current["payload_sha256"],
        )
        entry.update(
            {
                "output_state_path": relative(output_path),
                "output_state_sha256": output_state["payload_sha256"],
            }
        )
        entries.append(entry)
        current_path = output_path
        current = output_state

    if terminal is None:
        terminal = {
            "status": "BOUNDED_PASS",
            "reached": produce.CHUNKS[-1]["output_position"],
        }
    manifest = {
        "schema": "phase3-axial-h4-plucker-join-manifest-v1",
        "status": terminal["status"],
        "predecessor_certificate_path": str(
            produce.PREDECESSOR_CERTIFICATE.relative_to(produce.ROOT)
        ),
        "predecessor_certificate_sha256": (
            produce.EXPECTED_PREDECESSOR_CERTIFICATE_SHA256
        ),
        "predecessor_source_sha256": (
            produce.EXPECTED_PREDECESSOR_SOURCE_SHA256
        ),
        "support_prefix_sha256": hashlib.sha256(
            produce.support_prefix().encode()
        ).hexdigest(),
        "exporter": {
            "source_path": relative(produce.EXPORTER_SOURCE),
            "source_sha256": hashlib.sha256(
                produce.EXPORTER_SOURCE.read_bytes()
            ).hexdigest(),
            "log_path": relative(produce.EXPORTER_LOG),
            "log_sha256": hashlib.sha256(
                produce.EXPORTER_LOG.read_bytes()
            ).hexdigest(),
            "output_state_path": relative(
                produce.state_path(initial_position)
            ),
            "output_state_sha256": json.loads(
                produce.state_path(initial_position).read_text()
            )["payload_sha256"],
        },
        "chunks": entries,
        "terminal": terminal,
        "does_not_establish": [
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
        f"{manifest['status']} chunks={len(entries)} "
        f"manifest={manifest['payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
