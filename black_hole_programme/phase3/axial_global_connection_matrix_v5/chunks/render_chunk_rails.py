"""Render the compile-once 224-factor Δt=1/8 microfactor runner."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ..affine_rail import (
    build_microfactor_render_context,
    render_microfactor_adapter,
)

HERE = Path(__file__).resolve().parent
STARTS = tuple(range(224))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--micro", type=int, default=0)
    parser.add_argument(
        "--all-hashes", action="store_true",
        help="render all sources transiently and populate the complete hash manifest",
    )
    args = parser.parse_args()
    if not 0 <= args.micro < 224:
        raise SystemExit("microfactor id must be in [0,223]")
    context = build_microfactor_render_context()
    rendered: dict[int, tuple[str, str]] = {}
    requested = STARTS if args.all_hashes else (args.micro,)
    metadata = None
    for micro in requested:
        text, metadata = render_microfactor_adapter(micro, context=context)
        rendered[micro] = (text, hashlib.sha256(text.encode()).hexdigest())
    assert metadata is not None
    manifest = {"schema": "axial-affine-microfactor-runner-manifest-v3", "chunks": []}
    if not args.all_hashes:
        path = HERE / f"microfactor_{args.micro:03d}.forge"
        path.write_text(rendered[args.micro][0])
    for start in STARTS:
        manifest["chunks"].append({
            "start": start,
            "end": start + 1,
            "exact_t_start": f"{start}/8",
            "exact_t_end": f"{start + 1}/8",
            "panels": 8,
            "global_panel_start": 8 * start,
            "global_panel_end": 8 * (start + 1),
            "structured_panels": 8,
            "structured_order": 12,
            "structured_rebase_bits": 128,
            "structured_global_panel_start": 8 * start,
            "structured_global_panel_end": 8 * (start + 1),
            "rank_argument": "block-lower-determinant",
            "path": f"microfactor_{start:03d}.forge",
            "sha256": rendered[start][1] if start in rendered else None,
            "left_boundary_sha256": metadata["frame_sha256"][8 * start],
            "right_boundary_sha256": metadata["frame_sha256"][8 * (start + 1)],
        })
    manifest["generator"] = metadata["generator"]
    manifest["omega_cell"] = metadata["omega_cell"]
    manifest["frame_table_sha256"] = metadata["frame_table_sha256"]
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
