# Phase 3 axial global connection: moving-frame microfactor v6

Date: 23 July 2026

Dependency tags: `LORENTZIAN-CAUSAL`, `LOCAL-ALGEBRAIC`

## Result

The first final-frequency child now has a complete exact
\(r=32\)-to-\(r=4\) radial transport map on

\[
  \ell=2,\qquad M=1,\qquad
  M\omega\in[1/2,2049/4096],\qquad
  t=32-r\in[0,28].
\]

It is assembled from a certified prefix, an exact inherited-boundary
crosswalk, and 66 child-specialized tail factors.  Every factor is rank
twelve.  The exact block-to-standard state permutation is applied only after
radial composition and before the six-state complex infinity projection.  A
separate exact rank witness certifies the boundary crosswalk; the wide final
interval hull is not misused as a direct numerical rank test.

This advances the earlier first-factor result described below.  The
canonical child-global artifact is
`black_hole_programme/phase3/axial_global_connection_matrix_v5/chunks/artifacts/global_maps/global_map_q00.json`.
The remaining fifteen frequency children are being evaluated by the same
frozen rail.

The original first exact infinity-side radial microfactor was on

\[
  \ell=2,\qquad M=1,\qquad
  M\omega\in[1/2,129/256],\qquad
  t=32-r\in[0,1/8]
\]

is certified in a shared-generator affine moving frame.  The transition is
stored in the explicit contiguous block-lower layout

\[
  W_0=\begin{pmatrix}W_c&0\\W_l&W_k\end{pmatrix},
  \qquad \dim W_c=8,\quad \dim W_k=4.
\]

The carrier and Einstein-kernel flows both pass their existence and
uniqueness gates.  The diagonal blocks have independently certified ranks
eight and four, so the block determinant proves rank twelve without an
ill-conditioned full-matrix interval rank test.  The upper-right block is
exactly zero in its rational center, affine coefficient and interval
remainder.

The maximum interval widths are:

| Block | Maximum width |
| --- | ---: |
| \(W_c\) | `5.25130026437122e-06` |
| \(W_l\) | `0.0703247032992677` |
| \(W_k\) | `4.357247492393983e-06` |

The runner exits with the declared success code 42, emits all 144 affine
entries, and closes its `BEGIN`/`END` envelope.  The canonical artifact is
`black_hole_programme/phase3/axial_global_connection_matrix_v5/chunks/artifacts/microfactor_000.json`.

## Layout defect caught before promotion

The first structured fallback package composed an
`ivam_block_lower` matrix, whose storage is contiguous \(8+4\), using an
extractor for the original interleaved ODE ordering.  Its multi-panel
certificate is therefore withdrawn and is not used as evidence here.  The
v6 rail:

1. uses the interleaved extractor only on the differential coefficient and
   frame inputs;
2. uses a separate contiguous extractor on every structured transition;
3. prints and verifies the layout tag
   `contiguous-block-lower-v1`;
4. rejects an interleaved-extractor mutation;
5. rejects any nonzero upper-right block.

Only the fallback package's one-panel exponential/tail kernel is imported by
source hash.  Its defective composition function and certificate are
excluded.

## Runtime disposition

The raw \(12\times12\) affine formulation did not return after 16 minutes
19 seconds for this single interval and was terminated as a runtime
shortfall.  A first moving-frame implementation that materialized the
standard chart reduced runtime but produced an enclosure width above
\(10^6\) and did not certify full rank.  Keeping the factor in its natural
moving block frame takes about one minute on the present machine and yields
the narrow widths printed above.

All 224 specialized runner source hashes are derived from one global table of
1,793 exact affine boundary frames.  Adjacent factors therefore share
byte-identical boundary-frame hashes.  The complete manifest was rendered in
8.94 seconds after caching the common exact Taylor source.

The scale runner keeps specialized Forge sources ephemeral.  Each artifact
pins the committed renderer, complete source-hash manifest, global frame-table
hash, microfactor id and specialized source hash.  A clean clone can therefore
re-render any requested source without storing roughly 57 MB of mechanical
generated text.  Bounded parallel execution retains the complete runner logs,
which are converted to canonical artifacts only after their source hashes and
trace envelopes pass.

## Verification

```text
python -m black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.emit_microfactor \
  --micro 0 --log /tmp/axial_microfactor_000_frozen.log \
  --output black_hole_programme/phase3/axial_global_connection_matrix_v5/chunks/artifacts/microfactor_000.json \
  --repo-root .

python -m black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_microfactor \
  black_hole_programme/phase3/axial_global_connection_matrix_v5/chunks/artifacts/microfactor_000.json \
  --repo-root .

python -m unittest \
  black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.tests.test_microfactor \
  black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.tests.test_handoff
```

The artifact and provenance verifiers pass.  Fifty-five scoped chunk tests
pass, including layout, exact-boundary, affine-hull, source-hash,
upper-right-zero, false-restart, state-permutation, projection-order and
prefix/tail provenance mutation tests.

## Next gate

This result certifies the complete \(r=32\)-to-\(r=4\) radial transport only
on the first of sixteen final frequency cells.  It does not establish a
horizon-to-infinity connection, endpoint flux, a populated additional
channel, stability, CPT positivity, scattering or unitarity.

The next steps are:

1. complete and emit the other fifteen child-specialized tails;
2. compose and replay all sixteen \(r=32\)-to-\(r=4\) global maps;
3. attach a separately certified future-horizon-regular map at \(r=4\);
4. materialize endpoint action once, with the radial/outward orientation
   recorded explicitly;
5. compute the populated pullback
   \(C_{\rm reg}^{\dagger}G_{\rm endpoint}C_{\rm reg}\).

No physical-ghost or scattering-channel statement is licensed before that
populated endpoint pullback exists.
