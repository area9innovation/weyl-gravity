# Phase 3 axial normalized-plane classification contract

Date: 23 July 2026

## Result

A fail-closed contract now exists for the proposed plane-only join at
\(r=4M\).  It separates basis-invariant channel information from the
canonical endpoint amplitudes discarded by the Grassmann chart
normalization.

The contract permits a later certified handoff to establish:

- the horizon and endpoint subspaces and their dimensions;
- the normalized connection \(C=(C_-,C_+)^T\);
- ranks and kernels of its endpoint projections;
- rank, radical and inertia of current pullbacks;
- endpoint \(J\)-orthogonality and the Stokes identity;
- a compact-frequency negative endpoint-flux wave packet as soon as the
  populated \(I^+\) image has rank at least two on one certified open cell;
- a normalized one-sided \(J\)-isometry when \(C_-\) is uniformly invertible.

It forbids promotion to canonical amplitudes, named Einstein/additional
origin columns, the frozen endpoint \(L^2\) normalization, a two-ended
scattering matrix, stability, CPT positivity, a physical quantum ghost, or
unitarity.

## Current-sign audit

The exact current certificate declares

\[
F^r(y,\bar z)/(\pi\alpha_{\rm W})
=z^\dagger\widehat J(r,\omega)y.
\]

The action-derived endpoint Gram producer explicitly computes \(+iF^r\), and
the public handoff convention also declares \(iF^r\).  The required
Hermitian matrix is therefore

\[
K_4=+i\widehat J(4,\omega).
\]

An older unactivated affine rail realifies \(-i\widehat J\).  A conservation
defect cannot detect this overall sign because both sides flip together, but
the reported inertia does change.  The new contract therefore requires an
independent congruence crosscheck against the exact endpoint Gram.  Replacing
\(+i\) by \(-i\) is a mandatory rejecting mutation.

## Algebraic join

For normalized frames \(H,B_-,B_+\), set \(W=[B_-\ B_+]\) and solve

\[
WC=H,\qquad C=\binom{C_-}{C_+}.
\]

The complete pulled current \(W^\dagger K_4W\) must be computed.  In
particular, the cross block \(B_-^\dagger K_4B_+\) must be certified as zero;
it may not be silently omitted.  With that gate,

\[
\begin{aligned}
G_{\mathcal H^+}&=-H^\dagger K_4H,\\
G_-&=-B_-^\dagger K_4B_-,\\
G_+&= B_+^\dagger K_4B_+,
\end{aligned}
\qquad
G_{\mathcal H^+}+C_+^\dagger G_+C_+
-C_-^\dagger G_-C_-=0.
\]

The verifier contains an exact rational reference calculation, including a
nonunitary basis-change test.

## Index-pullback theorem

The exact outgoing endpoint form has inertia \((1,2,0)\) for
\(\alpha_{\rm W}>0\).  If \(r=\operatorname{rank}C_+\), the populated
pullback satisfies

\[
n_-\!\left(C_+^\dagger G_+C_+\right)\geq\max(0,r-1).
\]

This is the dimension inequality for the intersection of an
\(r\)-dimensional image with the two-dimensional negative subspace.  Thus
rank two already forces a negative outgoing endpoint direction.  On a
certified open frequency cell, continuity supplies a local continuous
negative direction; multiplying it by a nonzero compactly supported
frequency profile gives a strictly negative endpoint-flux wave packet.
Taking countably many profiles with pairwise disjoint frequency supports
makes their cross pairings vanish and yields an infinite-dimensional
negative endpoint-flux subspace.

This lower-rank activation is distinct from the stronger full-rank branch.
Uniform invertibility of \(C_-\) may additionally certify a normalized
one-sided \(J\)-isometry, but is not needed for the first negative
endpoint-flux result.

The conclusion concerns the \(\mathscr I^+\) endpoint term only.  The future
horizon contribution remains separate in the Stokes identity, so the
theorem establishes neither negative total conserved energy nor a physical
quantum ghost.

## Disposition

`NOT_ACTIVATED`.

No propagated normalized frame is imported here.  The future data join is a
separate Science Forge work item and depends on the landed horizon and
infinity plane transports.

## Verification

```bash
python3 -m \
  black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.verify
python3 -m \
  black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.mutations
python3 -m unittest -v \
  black_hole_programme.phase3.axial_global_normalized_plane_channel_classification.tests.test_contract
```
