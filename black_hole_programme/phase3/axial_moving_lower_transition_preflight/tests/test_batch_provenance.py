from __future__ import annotations

import copy

import pytest

from black_hole_programme.phase3.axial_moving_lower_transition_preflight.batch_provenance import (
    ProvenanceError,
    build_manifest,
    source_pin,
    verify_manifest,
    verify_source_pin,
)


RENDERER = b"renderer-v1"
FRAMES = b"1793-frame-table"


def render(micro: int) -> bytes:
    return f"// micro {micro}\npub fn main()->i64{{return {micro};}}\n".encode()


def fixture() -> dict:
    return build_manifest(
        renderer_path="render.py",
        renderer_bytes=RENDERER,
        frame_table_path="frames.json",
        frame_table_bytes=FRAMES,
        micro_count=4,
        render_source=render,
    )


def test_ephemeral_manifest_and_pin_round_trip() -> None:
    manifest = fixture()
    assert verify_manifest(
        manifest,
        renderer_bytes=RENDERER,
        frame_table_bytes=FRAMES,
        render_source=render,
    )
    pin = source_pin(manifest, 2)
    assert verify_source_pin(pin, manifest, rendered_source=render(2))


def test_renderer_drift_refuses() -> None:
    with pytest.raises(ProvenanceError):
        verify_manifest(
            fixture(),
            renderer_bytes=b"renderer-v2",
            frame_table_bytes=FRAMES,
            render_source=render,
        )


def test_frame_table_drift_refuses() -> None:
    with pytest.raises(ProvenanceError):
        verify_manifest(
            fixture(),
            renderer_bytes=RENDERER,
            frame_table_bytes=b"different frames",
            render_source=render,
        )


def test_one_micro_render_drift_refuses() -> None:
    def drifted(micro: int) -> bytes:
        return render(micro) + (b"// drift\n" if micro == 2 else b"")

    with pytest.raises(ProvenanceError):
        verify_manifest(
            fixture(),
            renderer_bytes=RENDERER,
            frame_table_bytes=FRAMES,
            render_source=drifted,
        )


def test_pin_cannot_be_moved_between_micros() -> None:
    manifest = fixture()
    pin = source_pin(manifest, 1)
    pin = copy.deepcopy(pin)
    pin["micro"] = 2
    with pytest.raises(ProvenanceError):
        verify_source_pin(pin, manifest, rendered_source=render(2))

