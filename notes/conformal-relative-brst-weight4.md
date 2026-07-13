# C2g-R: first relative conformal-BRST kernel

## Why weight four is the first target

The residual conformal ghosts are not an independent copy of a global
symmetry pasted onto the local Diff `x` Weyl complex.  They are the
conformal-Killing zero modes of that gauge complex.  In the standard cylinder
polarization their Fock vacuum carries compact energy `-4`.  Relative
ghost-number-zero matter representatives therefore obey

\[
(D-4)|\Psi\rangle=0,
\qquad
R_{MN}|\Psi\rangle=0,
\qquad
K^-_M|\Psi\rangle=0.
\]

The raising conditions are not imposed: a physical state is a conformal
primary, not a vector invariant under the complete noncompact algebra.  This
is the important correction to the naive formula
`H^0(so(4,2),H_local)=H_local^SO(4,2)`.  With the residual-ghost vacuum and
relative antighost conditions included, the cylinder BRST problem selects
weight-four primary scalars.

Hamada derives precisely this relative condition in a broader
Riegert--Weyl conformal-gravity model and identifies the lowest pure-Weyl
state with the Weyl-square bilinear; see
[arXiv:1202.4538](https://arxiv.org/abs/1202.4538).  The present certificate
does not import that model's Riegert sector.  It applies the same residual
zero-mode polarization to the independently normalized pure-Weyl module and
keeps the missing local-BV derivation explicit.

## Complete matter space

The full pure-Weyl matter Fock space at compact weight four consists of

1. every one-particle `E_4/A_4/L_4` mode, of total dimension `82`; and
2. the symmetric square of the ten `E_2^+ + E_2^-` modes, of dimension
   `55`.

Thus

\[
\dim\mathcal F_{D=4}=137.
\]

`symbolic/verify_conformal_relative_brst_weight4.py` constructs all six
compact-rotation constraints and all four proper-conformal lowering maps on
this complete space.  Their stacked exact matrix has rank

\[
135.
\]

The relative kernel is therefore exactly two dimensional.

## The two kernel vectors

For each chirality the lowest `E_2` irrep has spin two.  Its normalized
bosonic scalar is

\[
|W_\pm^2\rangle
=\sqrt{\frac25}|2,-2\rangle_\pm
-\sqrt{\frac25}|1,-1\rangle_\pm
+\frac1{\sqrt5}|0,0\rangle_\pm.
\]

Both are killed separately by every rotation and by every `K^-_M`.  Exact
rank proves that they span the full relative kernel.  Parity exchanges them,
so the combinations

\[
|W^2\rangle={|W_+^2\rangle+|W_-^2\rangle\over\sqrt2},
\qquad
|W\widetilde W\rangle={|W_+^2\rangle-|W_-^2\rangle\over\sqrt2}
\]

are parity even and odd.  Restricting the theory to parity-even observables
leaves the first vector; connected conformal covariance alone permits both.

## Matter-sector pairing

The ambient weight-four form has signature

\[
(97,40).
\]

The forty negative directions are the one-particle `A_4/L_4` modes.  The
relative kernel lies entirely in `Sym^2(E_2)`, so the restriction of the
normalized matter form to the chiral basis is

\[
\boxed{J_{\rm rel}^{(4)}=I_2.}
\]

This is the first concrete instance in which the relative conformal
conditions remove all negative matter directions present in the unreduced
shell and leave a positive pairing on the two weight-four scalar
vertex/deformation candidates.  It is not a positive propagating-particle
space: the one-particle absolute residual cohomology vanishes.  A full BRST
norm also contains the residual-ghost overlap.  Because a BRST differential raises
ghost number, that form pairs complementary ghost degrees rather than being
ghost-number block diagonal.  An explicit centered ghost vacuum/insertion is
therefore required before the displayed matter Gram can be called an
absolute cohomology pairing.  The result does **not** yet prove positivity of
the full interacting conformal theory.

## Acceptance boundary

The result is complete for the matter weight-four **relative primary
kernel**.  It is not yet absolute pure-Weyl BRST cohomology because the
project still has to derive, from the full local Diff `x` Weyl BV complex:

- the conformal-Killing zero-mode split;
- the residual ghost vacuum and its `-4` shift;
- its dual ghost insertion and the centered ghost-number pairing;
- the relative-to-absolute cohomology map;
- the adjoint and pairing on the full ghost complex; and
- interaction descent on the eventual cohomology classes represented by
  these vectors, if they survive the incoming-exact quotient.

Run

```bash
python3 symbolic/verify_conformal_relative_brst_weight4.py
```

The absolute claim must fail:

```bash
python3 symbolic/verify_conformal_relative_brst_weight4.py \
  --claim-absolute-cohomology
```
