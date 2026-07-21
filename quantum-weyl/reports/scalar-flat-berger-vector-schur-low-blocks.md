# Scalar-flat Berger vector-Schur low blocks

Date: 2026-07-21

Science Forge work item:
`sf:program/work/quantum-scalar-flat-berger-vector-schur-low-blocks`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The true vector and longitudinal Schur pencils are now computed exactly for
all nine Fourier/representation blocks

```text
n in {-1,0,1},  2j in {0,1,2}.
```

The convention is fixed by the orthonormal coframe

\[
(d\theta,\sigma_1,\sigma_2,2\sigma_3)
\]

and normalized product Haar measure.  On scalar modes,

\[
T_\theta=in,\quad T_1=-iJ_1,\quad T_2=-iJ_2,
\quad T_3=-\frac i2J_3,
\]

with (T_a^\dagger=-T_a) and (delta=d^\dagger).  The one-form basis is
component-major in the displayed coframe.  The exact covector connection is
derived from

\[
[e_1,e_2]=2e_3,\quad [e_2,e_3]=\frac12e_1,
\quad [e_3,e_1]=\frac12e_2.
\]

The stored matrices implement

\[
F=\nabla^*\nabla+\operatorname{Ric},\qquad
W=-2\operatorname{Ric},\qquad A(t)=F+tW,
\]

and

\[
S_L(t)=\frac23 I+\frac13\delta A(t)^{-1}d.
\]

Every block verifies (Fd=d\Delta_0), (F=F^\dagger), and
(A(t)=A(t)^\dagger) for real (t).  The generated oracle records every
matrix entry as an exact rational/algebraic expression in (t), along with
(det A(t)), (det S_L(t)), the paired relative factor and every Schur
denominator root.

## Priming and zero-pole structure

The scalar constant ((n,j)=(0,0)) is removed before using
(Delta_0^{-1}).  In the low oracle, (F) has the single harmonic
(d\theta) mode.

At the physical value (t=1), (A(1)) has five zero modes after left
multiplicities: two in the (n=0,j=0) block and three from the
one-dimensional (n=0,j=1) kernel.  The exact projectors show that all five
are coclosed and orthogonal to the gradient image.  They are Killing
one-forms and require vector priming; they do not create Schur poles.

The other exceptional (A(t)) roots which occur in Schur denominators are
matched zero-pole loci.  In every low block the denominator cancels exactly
from

\[
\frac{\det A(t)}{\det F}\det S_L(t).
\]

The (n=0,j=1/2) denominator has the positive root

\[
t_*=\frac{3(13+\sqrt{817})}{128}\approx0.9746065,
\]

so the vector pencil crosses before (t=1), but its coupled Schur product
has a finite polynomial continuation.  This crossing must be retained in
any Agmon-ray or phase analysis.

## Independent rail

The verifier does not import the producer's ladder construction.  It uses
explicit Pauli matrices for (j=1/2), independently written spin-one
matrices for (j=1), and hard-coded covector connection matrices.  It
reconstructs all six nontrivial (j=1/2,1) vector/Schur blocks, checks the
stored determinant identities, and verifies all nine kernel projectors.
The (n=0,j=1/2) first derivative is independently

\[
S_L'(0)=\operatorname{diag}\left(-\frac{64}{81},-\frac{64}{81}\right).
\]

## Boundary and next gate

This is a finite low-mode oracle.  It does not extrapolate the matrix
formula to arbitrary (j,n), prove uniform high-mode coercivity, construct
the complete primed resolvent, evaluate an infinite determinant or weighted
trace, or compute the five background-specific finite functions.  It makes
no (Gamma_1), (Q_1), QME, Lorentzian, Hadamard, state, particle,
positivity, scattering or unitarity claim.

The next gate is the all-(j,n) representation formula and uniform
high-mode estimate, using this content-addressed oracle as a holdout.

## Verification

```text
python3 quantum-weyl/spectral/euclidean/scalar_flat_berger_vector_schur_low_blocks.py --check
python3 quantum-weyl/spectral/euclidean/verify_scalar_flat_berger_vector_schur_low_blocks.py
python3 -m unittest quantum-weyl/spectral/euclidean/tests/test_scalar_flat_berger_vector_schur_low_blocks.py -v
```

Producer emit/check took 10.68 s and 11.29 s.  The independent exact replay
passed in 13.31 s.  Six tests passed in 14.28 s and reject altered blocks,
kernel counts, high-mode promotion and QME/Lorentzian promotion.

EVIDENCE: `quantum-weyl/spectral/euclidean/certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_LOW_BLOCKS.json`; `quantum-weyl/spectral/euclidean/generated/scalar_flat_berger_vector_schur_low_blocks_v1/blocks.json`

CLOSE-OUT: DONE — all requested low blocks, normalized projectors,
exceptional loci and exact coupled cancellations are exported; the all-mode
and global-sum theorems remain explicitly open.
