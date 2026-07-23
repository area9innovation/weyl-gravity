# Phase 3 horizon Grassmann transport design

**Date:** 23 July 2026

**Status:** unvalidated design input; no scientific claim

**Scope:** axial \(\ell=2\) Schwarzschild horizon transport on
\(\widehat\omega=M\omega\in[1/2,3/4]\)

## Purpose

The current horizon-to-\(r=4M\) preflight transports a \(12\times6\) real
matrix whose six columns represent three complex future-horizon-regular
solutions.  This transports a chosen basis, although the scientific object
needed for matching is initially only the three-complex-dimensional regular
subspace.  Artificial complementary contamination is amplified under the
existing fixed-frame composition and the validated interval calculation
stops before \(r=4M\).

This memo proposes an exact-affine Grassmann-chart transport for that
subspace.  It is an implementation design and falsification plan, not a
repair or certificate for the active horizon package.

The design reuses the existing action-derived first-order system, horizon
initializer, exact dyadic shell partition, and certified local transition
factors.  It changes only the transported object:

\[
  \text{basis }Y\in\mathbb C^{6\times3}
  \quad\longrightarrow\quad
  \text{plane }[Y]\in \mathrm{Gr}(3,6).
\]

## State ordering and row crosswalk

The complex sheared state is

\[
  X=(P,P',Q,Q',H_1,\rho F)^T,
  \qquad \rho=r-2M .
\]

The active local transition factors use the consumer's block-real ordering,

\[
(\Re P,\Re P',\Re Q,\Re Q',
  \Im P,\Im P',\Im Q,\Im Q',
  \Re H_1,\Re\rho F,\Im H_1,\Im\rho F)^T.
\]

The proposed initial complex pivot rows are

\[
 I=(P',Q,H_1)=(1,2,4),\qquad
 J=(P,Q',\rho F)=(0,3,5).
\]

In block-real row order the corresponding selectors are

\[
 I_{\mathbb R}=[1,2,8,5,6,10],\qquad
 J_{\mathbb R}=[0,3,9,4,7,11].
\]

Equivalently, if the implementation continues to use the existing
consumer-specific ordering in which the six real and imaginary components
are grouped after the standard-to-block conversion, it must derive these
selectors from the named complex rows rather than copy numeric indices.
This is a mandatory guard against the standard/interleaved-versus-contiguous
row bug already found in an earlier lower-transition composer.

For avoidance of ambiguity, the implementation must print its resolved
row-name table in the certificate and independently verify that selecting a
complex row selects both its real and imaginary components.

Exploratory midpoint arithmetic on the exact horizon initializer gives

\[
\sigma_{\min}(P_IY_0)\simeq0.7346637523,\qquad
\kappa(P_IY_0)\simeq2.6253426974,\qquad
\|Z_0\|_\infty\simeq1.4953712992.
\]

These decimal values are diagnostics only.  They are not certified bounds.
The superficially better-conditioned chart
\(I=(Q,Q',H_1)\) has exploratory graph norm about \(2.7747930453\), so the
selected chart trades some pivot conditioning for a materially smaller
graph coordinate.

## Exact Grassmann update

For a chart \(I\sqcup J=\{0,\ldots,5\}\), write a representative of the
plane as

\[
  G_I(Z)=
  \begin{pmatrix}I_3\\ Z\end{pmatrix}_I ,
\]

where the subscript means that the identity and graph rows are restored to
their named positions.  Partition a certified local transition factor
\(\Phi\) in the same chart:

\[
\Phi=
\begin{pmatrix}
\Phi_{II}&\Phi_{IJ}\\
\Phi_{JI}&\Phi_{JJ}
\end{pmatrix}.
\]

Then

\[
  \Phi G_I(Z)=
  \begin{pmatrix}M\\N\end{pmatrix}_I,\qquad
  M=\Phi_{II}+\Phi_{IJ}Z,\qquad
  N=\Phi_{JI}+\Phi_{JJ}Z,
\]

and, when \(M\) is certified invertible,

\[
  Z_{\mathrm{next}}=NM^{-1}.
\]

The right solve must not be implemented as a left solve.  With the current
Forge math API, \(XA=B\) is obtained through

```text
Xt = ivam_solve_rect(ivam_transpose(A), ivam_transpose(B))
X  = ivam_transpose(Xt.value)
```

so the update uses \(A=M\) and \(B=N\).  A small named wrapper should expose
the invariant directly, for example

```text
ivam_right_solve(B, A) -> X with X*A = B
```

and should verify its residual before returning.

All matrix products and solves remain exact-affine interval operations with
the shared \(\widehat\omega\) generator.  Non-affine dependence generated
by products and inversion is enclosed in the remainder by the existing
checked multiplication and Krawczyk/Neumann solve machinery.  Rebase to a
dyadic denominator of \(2^{128}\) after every panel.

The continuous Riccati equation is an independent numerical oracle:

\[
 Z'
 =
 A_{JI}+A_{JJ}Z-ZA_{II}-ZA_{IJ}Z.
\]

On a shell \(\rho\in[\rho_0,\rho_1]\), use

\[
 s=\frac{\rho-\rho_0}{\rho_1-\rho_0},\qquad
 \frac{dZ}{ds}=(\rho_1-\rho_0)\frac{dZ}{d\rho}.
\]

For the doubling shells, \(\rho_1-\rho_0=\rho_0\), which removes the
leading near-horizon \(1/\rho\) scale from the normalized coefficient.
The Riccati integration is not a verification rail unless separately
enclosed; its initial role is mutation-sensitive comparison only.

## Recharting

Recharting must be based on certified pivots, never midpoint rank.
Given \(G_I(Z)\), enumerate the twenty complex row triples
\(K\subset\{0,\ldots,5\}\).  For each \(K\), form

\[
 B_K=P_KG_I(Z).
\]

Accept \(K\) only if the corresponding \(6\times6\) block-real pivot has
certified full rank and a certified inverse.  The new graph is

\[
 Z_K=P_{K^c}G_I(Z)\,B_K^{-1}.
\]

Among accepted charts, choose the one with the smallest certified upper
bound on \(\|Z_K\|_\infty\), using lexicographic order only as a deterministic
tie breaker.  Rechart when the current certified upper bound exceeds \(2\)
or when the next Möbius solve refuses.  If no candidate has upper bound at
most \(2\), split the radial panel or frequency cell and fail closed if the
split does not restore a certified chart.

### Unvalidated numerical chart schedule

The following schedule comes from an ordinary floating-point RK4
exploration.  It is **UNVALIDATED DESIGN INPUT**, included only to guide
test placement:

* \(I=(P',Q,H_1)\) appears to remain usable with
  \(\|Z\|_\infty\approx1.495\) through shell 19;
* near the shell taking \(\rho\) from \(1/4\) to \(1/2\), the preferred
  chart appears to change to
  \(I=(Q,H_1,\rho F)=(2,4,5)\);
* exploratory graph norms after that switch are approximately
  \(1.4197\), \(1.0498\), and \(0.8692\) on the remaining macroscopic
  shells to \(r=4M\).

None of these values proves that the certified affine calculation will
accept the same charts.

## Why Grassmann coordinates are the first design

The plane has nine complex graph coordinates, or eighteen real coordinates.
The third exterior power has twenty complex coordinates and introduces a
larger interval system.  Continuous QR or Drury--Oja transport is attractive
numerically but introduces square-root, orthogonalization, and phase choices
that are less mature in the exact-affine backend.  Grassmann charts therefore
give the smallest exact transport object while retaining an explicit rank
gate.

The plane transport discards the internal normalization of the three
horizon-regular columns.  If a later connection theorem needs
horizon-labelled amplitudes, propagate a separate \(3\times3\) factor \(R\):

\[
  Y=G_I(Z)R,\qquad R_{\mathrm{next}}=MR.
\]

That amplitude rail is deliberately excluded from the first one-shell
preflight.

## Proposed implementation surface

The first implementation should remain consumer-local until the one-shell
experiment passes.  A minimal interface is:

```text
IvGrassmannChart {
  generator
  complex_pivots
  z
}

ivam_select_complex_rows(matrix, row_names, pivots, layout)
ivam_right_solve(B, A)
ivgrass_from_basis(Y, pivots, rank_cells, rebase_bits)
ivgrass_step(Phi, chart, rank_cells, rebase_bits)
ivgrass_rechart(chart, new_pivots, rank_cells, rebase_bits)
ivgrass_choose_chart(chart, norm_limit, rank_cells, rebase_bits)
```

Only after the consumer-local experiment passes, including the row-layout
mutations, should generic selectors, right solves, and chart transport be
requested for `forge/lib/math`.

## Exact one-shell preflight

The first falsification target is shell zero,

\[
  \rho\in[2^{-22},2^{-21}],
\]

using the existing sixteen certified local factors on each of the four exact
frequency subcells covering the lower pilot interval.

### Producer gates

1. Construct the exact-affine horizon initializer \(Y_0\).
2. Form \(M_0=P_IY_0\) and \(N_0=P_JY_0\).
3. Certify that the block-real \(M_0\) has rank six and solve
   \(Z_0=N_0M_0^{-1}\).
4. For every panel, form \(M,N\), certify the right solve, update \(Z\), and
   rebase at 128 bits.
5. Require generator ID `7315` to survive every extraction, product, solve,
   and rebase.
6. Require a certified chart-norm upper bound below \(2\) throughout the
   shell.
7. Require no rank, Krawczyk, or chart-selection refusal.

### Independent rails

The existing direct basis rail is still numerically manageable through the
first shell.  Rechart its terminal interval basis only at the endpoint and
require entrywise interval intersection with the terminal Grassmann chart.
This is comparison with a distinct state representation, not a rerun of the
same producer.

Apply a nontrivial exact invertible complex rational column gauge

\[
  Y_0\longmapsto Y_0S,\qquad S\in GL(3,\mathbb Q(i)).
\]

Both the initial and terminal Grassmann coordinates must be invariant:
their interval enclosures must intersect the ungauged result entrywise.
This is the principal test that the new rail transports a plane rather than
a preferred basis.

Record the width of the direct basis after endpoint recharting and the width
of the incrementally transported Grassmann chart.  Before execution, freeze
a material improvement threshold; a factor of at least two in the maximum
entry width is the proposed minimum.  Failure to meet it is a failed
preflight even if both enclosures overlap.

The noncertifying Riccati oracle predicts that the graph norm remains close
to \(1.4953713\) on this shell.  It may be used as a diagnostic but not as a
pass condition.

### Mandatory mutations

The verifier must reject at least:

1. the wrong left solve \(M^{-1}N\);
2. deletion of the \(\Phi_{IJ}Z\) term in \(M\);
3. a standard/interleaved row selector applied to block-real factors;
4. a changed or dropped generator ID;
5. a column-gauge transformation that changes the reported plane;
6. omission of rebase or of an affine remainder tail when it changes the
   enclosure.

The certificate must record mutation names, expected failure gates, exact
commands, elapsed times, input hashes, and whether higher test tiers were
run.

## Promotion sequence

If and only if the one-shell preflight passes:

1. extend through the near-horizon shells without dynamic recharting;
2. activate certified chart selection and radial splitting;
3. reach \(r=4M\) on the lower frequency pilot interval;
4. repeat independently on the upper pilot interval;
5. add the internal amplitude rail;
6. only then construct a horizon-to-infinity connection determinant and
   pull back the endpoint flux Gram.

Every step is a separate certificate.  A failure or timeout at one step is
not evidence for the next.

## `does_not_establish`

This memo does **not** establish:

* a certified one-shell Grassmann transport;
* a repair or certification of the active horizon transport package;
* a horizon-regular basis or connection at \(r=4M\);
* the internal amplitude or normalization map from horizon-labelled modes;
* a horizon-to-infinity connection matrix;
* a global scattering space, flux-conservation theorem, physical ghost,
  stability, or CPT result;
* any result outside the declared axial \(\ell=2\) pilot;
* any result for frequencies outside the named pilot interval;
* any result for polar perturbations;
* rigor for the floating-point chart schedule or quoted midpoint
  diagnostics.

The memo is a typed design input for the next exact preflight.  Scientific
claims remain governed by the resulting producer, independent verifier,
mutation tests, and machine-readable certificate.
