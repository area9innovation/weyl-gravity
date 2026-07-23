# Ephemeral specialized-source provenance

The global axial connection needs 224 specialized Forge runners, but keeping
all rendered sources would add roughly 57 MB of derived text.  The source is
still part of the proof provenance and therefore cannot simply disappear.

Use this content-addressed pattern:

1. Commit one deterministic renderer and one 1,793-frame global table.
2. Stream `render_source(micro)` for each `micro=0,...,223` into SHA-256 and
   immediately discard the bytes.
3. Commit one canonical manifest containing the renderer hash, global-frame
   hash and the `(micro, radial-domain, source-hash, byte-count)` ledger.
4. Each handoff artifact pins exactly:

   ```text
   manifest_sha256
   renderer_sha256
   frame_table_sha256
   micro
   source_sha256
   ```

5. A clean-clone verifier re-renders only the requested microfactor into a
   temporary file, checks its source hash against both the artifact pin and
   manifest, compiles it, and deletes it after verification.

This retains the scientific guarantee—every binary is attributable to exact
source bytes—without treating mechanically generated text as an archival
source file.  Renderer or frame drift invalidates the entire manifest;
micro-specific drift invalidates only the corresponding pin before
compilation.

`batch_provenance.py` implements the manifest, source-pin and fail-closed
verification core.  Its tests cover renderer drift, frame drift,
micro-specific source drift and attempts to move a pin between microfactors.

The active v5/v6 implementation should expose a pure deterministic
`render_source(micro) -> bytes` entry point.  A batch driver should compute
the 1,793-frame table once, close over it, render/hash all 224 sources in one
process, and then schedule temporary compilation with bounded concurrency.
No active global-connection file is modified by this preflight.
