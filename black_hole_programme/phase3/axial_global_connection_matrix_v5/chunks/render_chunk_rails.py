"""Render one compile-once Δt=1 reset runner from the authoritative generator."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..affine_rail import render_affine_adapter

HERE = Path(__file__).resolve().parent
STARTS = tuple(range(28))


def main() -> None:
    source, metadata = render_affine_adapter()
    marker = "pub fn main()->i64"
    if marker not in source:
        raise RuntimeError("generated main marker missing")
    prefix = source.rsplit(marker, 1)[0].replace(
        "import prelude;\n", "import prelude;\nimport sys/args;\n", 1
    )
    manifest = {"schema": "axial-affine-reset-runner-manifest-v2", "chunks": []}
    text = prefix + (
        "pub fn main()->i64{"
        "let k:i64=if(args_count()>1){match(parse_i64(bytes(arg(1)),0)){"
        "ok(p)=>p.v,err(e)=>-1}}else{-1};"
        "if(!axial_global_connection_chunk(k,1)){return 3;}return 42;}\n"
    )
    path = HERE / "chunk_runner.forge"
    path.write_text(text)
    runner_hash = hashlib.sha256(text.encode()).hexdigest()
    for start in STARTS:
        manifest["chunks"].append({
            "start": start,
            "end": start + 1,
            "panels": 64,
            "path": path.name,
            "sha256": runner_hash,
        })
    manifest["generator"] = metadata["generator"]
    manifest["omega_cell"] = metadata["omega_cell"]
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
