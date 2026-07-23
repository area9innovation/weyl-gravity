# Axial normalized-plane channel classification

This package freezes the evidence boundary for joining the independently
normalized horizon and infinity planes at \(r=4M\).  It deliberately accepts
chart-identity plane frames without pretending that their discarded endpoint
amplitudes have been recovered.

For the declared phase convention,

\[
  F^r(y,\bar z)=\pi\alpha_{\rm W}\,z^\dagger\widehat J(r,\omega)y ,
  \qquad K_4=+i\widehat J(4,\omega).
\]

The Hermitian matrix used by the join is therefore the standard realification

\[
 {\cal R}(K_4)=
 \begin{pmatrix}\Re K_4&-\Im K_4\\
                 \Im K_4& \Re K_4\end{pmatrix}.
\]

Let \(H,B_-,B_+\) be the normalized complex \(6\times3\) frames at \(r=4M\)
and \(W=[B_-\ B_+]\).  A certified join must solve

\[
 WC=H,\qquad C=\binom{C_-}{C_+},
\]

on the complete frequency cell.  It must independently pull back \(K_4\),
certify \(B_-^\dagger K_4B_+=0\), and verify

\[
G_{\mathcal H^+}+C_+^\dagger G_+C_+
-C_-^\dagger G_-C_-=0,
\]

with

\[
G_{\mathcal H^+}=-H^\dagger K_4H,\qquad
G_-=-B_-^\dagger K_4B_-,\qquad
G_+=B_+^\dagger K_4B_+.
\]

These statements are invariant under independent right changes of frame
\(H\mapsto HA_H\), \(B_\pm\mapsto B_\pm A_\pm\).  The connection matrices
transform as \(C_\pm\mapsto A_\pm^{-1}C_\pm A_H\), while every Gram transforms
by congruence.

## Index-pullback activation theorem

The exact outgoing endpoint Gram has inertia \((1,2,0)\) for
\(\alpha_{\rm W}>0\).  If the populated image of \(C_+\) has complex
dimension \(r\), the restriction of that Gram to the image obeys

\[
 n_-\!\left(C_+^\dagger G_+C_+\right)\geq \max(0,r-1).
\]

Indeed, a nonnegative subspace of a Hermitian space with positive index one
and zero radical has dimension at most one.  Hence every rank-two populated
image contains a negative direction, while a full-rank image contains at
least two.

Consequently, on any certified open frequency cell where \(G_+\) and \(C_+\)
vary continuously, `rank_Cplus >= 2` is enough to construct a nonzero
compactly supported frequency profile with strictly negative
**endpoint flux**.  This is the first activation branch.  It does not require
full rank on the complete pilot interval.

The conclusion is not merely one-dimensional.  Choose countably many such
profiles with pairwise disjoint frequency supports inside the certified open
cell.  Because the endpoint form is frequency diagonal, their cross pairings
vanish and every diagonal pairing is negative.  Their span is therefore an
infinite-dimensional negative endpoint-flux subspace.

The stronger branch remains separate: if \(C_-\) is uniformly invertible,
the join may also certify the normalized one-sided \(J\)-isometry.  Neither
branch supplies the missing \(\mathcal H^-\) data or canonical endpoint
amplitudes.

## Current disposition

`preactivation-certificate.json` is intentionally `NOT_ACTIVATED`.  It
certifies the contract and the exact algebraic reference checks only.  It
does not contain propagated horizon or infinity data.

The normalized join may establish plane dimensions, connection projection
ranks, current-form ranks/radicals/inertias, Stokes conservation, and a
normalized one-sided \(J\)-isometry.  It may not establish:

- canonical endpoint or scattering amplitudes;
- the original `XI*`, `EI*`, `XH*` column normalization;
- Einstein/additional origin restrictions after unrestricted plane mixing;
- equivalence with the frozen endpoint \(L^2\) normalization;
- a two-ended scattering matrix, because \(\mathcal H^-\) is absent;
- negative total conserved energy or a horizon-completed energy sign;
- stability, CPT positivity, a quantum ghost, particles, or unitarity.

In particular, a negative \(\mathscr I^+\) endpoint-flux wave packet is not
by itself a negative conserved-energy state: the horizon contribution is a
separate term in the Stokes identity.  It is also not a quantum-ghost claim.

## Verification

```bash
python3 -m \
  black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.verify
python3 -m \
  black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.mutations
python3 -m unittest -v \
  black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.tests.test_contract
```
