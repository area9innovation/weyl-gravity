# Moving-frame lower-transition preflight

This isolated preflight addresses the width obstruction in the first axial
Schwarzschild infinity microfactor without editing the active global
connection implementation.

## Layout correction

The superseded structured preflight mixed two matrix layouts:

- coefficients and numerical frames use the original interleaved real
  12-state order;
- `ivam_block_lower` produces a contiguous `8+4` block layout.

Its multi-panel composer applied the interleaved extractor to a contiguous
matrix.  This package does **not** import that composition or its
certificate.  It imports only the coefficient/frame table bytes as data,
then deletes the predecessor tail at render time.  The new implementation
uses separate, explicit extractors and an exact rational mutation fixture
that rejects the predecessor mapping.

## Moving-frame identity

For

\[
U=\begin{pmatrix}U_c&0\\L&U_k\end{pmatrix},
\qquad
B_i=\begin{pmatrix}C_{c,i}&0\\D_i&C_{k,i}\end{pmatrix},
\]

the local transition in moving coordinates is

\[
W=B_1^{-1}UB_0
 =\begin{pmatrix}W_c&0\\W_l&W_k\end{pmatrix},
\]

where

\[
W_c=C_{c,1}^{-1}U_cC_{c,0},\qquad
W_k=C_{k,1}^{-1}U_kC_{k,0},
\]

\[
W_l=C_{k,1}^{-1}
\left(LC_{c,0}+U_kD_0-D_1W_c\right).
\]

The calculation retains affine generator `7315`, exact zero upper-right
blocks, the action-derived outward local Taylor tails, and 128-bit dyadic
rebasing after every structured composition.

## Result

On the first radial microinterval \(t\in[0,1/8]\) and the full pilot
frequency cell \(M\omega\in[1/2,129/256]\), split into four exact dyadic
subcells:

- every carrier diagonal block has certified rank 8;
- every kernel diagonal block has certified rank 4;
- the upper-right block is identically zero;
- maximum local moving-lower width: `0.00887141066029161`;
- maximum composed piecewise moving-lower width:
  `0.07027467354990395`;
- Forge runtime: about 50 seconds after compilation.

The older `621.8840812306481` figure is retained only as a **superseded
unframed benchmark**.  It is not used as mathematical evidence because its
predecessor certificate had the layout defect above.  Relative to that
benchmark, the new piecewise moving representation is about 8,849 times
narrower.

This is a `PREFLIGHT_PASS`, but it proves neither all 224 infinity factors
nor the horizon-to-infinity connection.

## Verification

```bash
python3 -m pytest -q \
  black_hole_programme/phase3/axial_moving_lower_transition_preflight/tests

python3 -m \
  black_hole_programme.phase3.axial_moving_lower_transition_preflight.verify \
  --certificate \
    black_hole_programme/phase3/axial_moving_lower_transition_preflight/certificate.json \
  --source \
    black_hole_programme/phase3/axial_moving_lower_transition_preflight/moving_fixture.forge \
  --metadata \
    black_hole_programme/phase3/axial_moving_lower_transition_preflight/source_metadata.json
```

To reproduce the Forge certificate:

```bash
python3 -m \
  black_hole_programme.phase3.axial_moving_lower_transition_preflight.run_preflight
```

The ephemeral-source provenance design for scaling to 224 factors is in
`EPHEMERAL-SOURCE-DESIGN.md`.

