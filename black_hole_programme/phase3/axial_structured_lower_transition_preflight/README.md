# Structured block-lower transition preflight

This is an isolated fallback for the axial Phase-3 global connection.  It
does not modify the active v5/v6 connection implementation or Forge
`lib/math`.

For

\[
A=\begin{pmatrix}A_c&0\\G&A_k\end{pmatrix},
\]

the Peano--Baker powers retain the same block form.  The polynomial
recurrence is

\[
C_{n+1}=A_cC_n,\qquad
K_{n+1}=A_kK_n,\qquad
L_{n+1}=GC_n+A_kL_n.
\]

If
\(\alpha_c=\|A_c\|_\infty\),
\(\alpha_k=\|A_k\|_\infty\),
\(\beta=\|G\|_\infty\), and
\(\alpha=\max(\alpha_c,\alpha_k)\), the omitted lower block after order
\(N\) is bounded by

\[
\beta h\sum_{m=N}^{\infty}\frac{(\alpha h)^m}{m!}.
\]

The implementation carries the same affine frequency generator through all
blocks, keeps the upper-right block exactly zero, and dyadically rebases
each block after every panel.  Rank is checked only on the carrier and
kernel diagonal factors:

\[
\det\begin{pmatrix}C&0\\L&K\end{pmatrix}=\det(C)\det(K).
\]

## First actual fixture

On the first eight-panel infinity microfactor
\(t\in[0,1/8]\), \(M\omega\in[1/2,129/256]\):

- carrier rank: 8, certified;
- kernel rank: 4, certified;
- exact upper-right block: zero;
- shared generator: 7315;
- Forge runtime: 0.80 seconds after compilation;
- full-matrix rank enclosure: not used.

The resulting maximum entry width is approximately `621.884`.  The method
therefore closes the local raw-rank refusal, but it does **not** yet prove
that composing all 224 factors will retain useful widths.  Moving-frame
lower correction or shorter local resets may still be required.

## Verification

```bash
python3 -m pytest -q \
  black_hole_programme/phase3/axial_structured_lower_transition_preflight/tests

python3 -m \
  black_hole_programme.phase3.axial_structured_lower_transition_preflight.verify \
  --certificate black_hole_programme/phase3/axial_structured_lower_transition_preflight/certificate.json \
  --source black_hole_programme/phase3/axial_structured_lower_transition_preflight/actual_fixture.forge \
  --metadata black_hole_programme/phase3/axial_structured_lower_transition_preflight/source_metadata.json
```

The independent rational oracle compares the structured recurrence with an
exact nilpotent constant block exponential.  Mutation rails reject omission
of the kernel-times-lower term, swapped multiplication order, deletion of
the lower tail, and a changed affine generator.
