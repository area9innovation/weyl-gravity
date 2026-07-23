"""Content-addressed provenance for ephemeral specialized Forge sources.

The 224 global-connection microfactors should not require 224 large generated
source files in Git.  This module defines the deterministic core of the
alternative: hash the committed renderer and one global frame-table manifest,
stream each specialized source through a hash, discard the bytes, and let
each result artifact pin the manifest plus its own micro/source hash.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


SCHEMA = "phase3-axial-ephemeral-source-manifest-v1"
PIN_SCHEMA = "phase3-axial-ephemeral-source-pin-v1"


class ProvenanceError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode()


def build_manifest(
    *,
    renderer_path: str,
    renderer_bytes: bytes,
    frame_table_path: str,
    frame_table_bytes: bytes,
    micro_count: int,
    render_source: Callable[[int], bytes],
) -> dict[str, Any]:
    if micro_count <= 0:
        raise ProvenanceError("micro_count must be positive")
    micros = []
    for micro in range(micro_count):
        source = render_source(micro)
        if not source:
            raise ProvenanceError(f"renderer returned empty source for micro {micro}")
        micros.append(
            {
                "micro": micro,
                "radial_start": f"{micro}/8",
                "radial_end": f"{micro + 1}/8",
                "source_sha256": sha256(source),
                "source_bytes": len(source),
            }
        )
    body = {
        "schema": SCHEMA,
        "renderer": {
            "path": renderer_path,
            "sha256": sha256(renderer_bytes),
            "interface": "render_source(micro)->bytes",
        },
        "frame_table": {
            "path": frame_table_path,
            "sha256": sha256(frame_table_bytes),
            "frame_count": 1793,
            "generation": "single-global-table-with-byte-identical-overlap",
        },
        "micro_count": micro_count,
        "generated_sources_retained": False,
        "micros": micros,
    }
    body["manifest_sha256"] = sha256(canonical_bytes(body))
    return body


def verify_manifest(
    manifest: dict[str, Any],
    *,
    renderer_bytes: bytes,
    frame_table_bytes: bytes,
    render_source: Callable[[int], bytes],
) -> bool:
    if manifest.get("schema") != SCHEMA:
        raise ProvenanceError("wrong manifest schema")
    unsigned = dict(manifest)
    recorded_manifest_sha = unsigned.pop("manifest_sha256", None)
    if recorded_manifest_sha != sha256(canonical_bytes(unsigned)):
        raise ProvenanceError("manifest hash mismatch")
    if manifest.get("generated_sources_retained") is not False:
        raise ProvenanceError("ephemeral-source contract changed")
    renderer = manifest.get("renderer", {})
    frames = manifest.get("frame_table", {})
    if renderer.get("sha256") != sha256(renderer_bytes):
        raise ProvenanceError("renderer hash mismatch")
    if frames.get("sha256") != sha256(frame_table_bytes):
        raise ProvenanceError("frame-table hash mismatch")
    if frames.get("frame_count") != 1793:
        raise ProvenanceError("wrong global frame count")
    micros = manifest.get("micros", [])
    if len(micros) != manifest.get("micro_count"):
        raise ProvenanceError("micro ledger incomplete")
    for expected, record in enumerate(micros):
        if record.get("micro") != expected:
            raise ProvenanceError("micro order is not canonical")
        source = render_source(expected)
        if record.get("source_sha256") != sha256(source):
            raise ProvenanceError(f"source hash mismatch for micro {expected}")
        if record.get("source_bytes") != len(source):
            raise ProvenanceError(f"source length mismatch for micro {expected}")
    return True


def source_pin(manifest: dict[str, Any], micro: int) -> dict[str, Any]:
    micros = manifest.get("micros", [])
    if micro < 0 or micro >= len(micros) or micros[micro].get("micro") != micro:
        raise ProvenanceError("micro is absent from manifest")
    return {
        "schema": PIN_SCHEMA,
        "manifest_sha256": manifest["manifest_sha256"],
        "renderer_sha256": manifest["renderer"]["sha256"],
        "frame_table_sha256": manifest["frame_table"]["sha256"],
        "micro": micro,
        "source_sha256": micros[micro]["source_sha256"],
    }


def verify_source_pin(
    pin: dict[str, Any],
    manifest: dict[str, Any],
    *,
    rendered_source: bytes,
) -> bool:
    if pin.get("schema") != PIN_SCHEMA:
        raise ProvenanceError("wrong pin schema")
    expected = source_pin(manifest, int(pin.get("micro", -1)))
    if pin != expected:
        raise ProvenanceError("artifact source pin differs from manifest")
    if pin.get("source_sha256") != sha256(rendered_source):
        raise ProvenanceError("ephemeral source does not reproduce")
    return True


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(manifest))

