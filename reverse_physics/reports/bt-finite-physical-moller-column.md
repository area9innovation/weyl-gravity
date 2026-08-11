# BT finite physical continuum Møller column

**Certificate:** `REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The completed (75)-mark continuum affiliation can be composed with the
finite Hudson--Parthasarathy evolution.  It gives an exact, normalized
physical continuum **vacuum column** on every channel currently supplied by
the BT amplitudes.

Let (I_Omega) include the incoming hard two-species state with vacuum
noise, let (U_a) be the certified (75)-channel HP unitary, and let

\[
 {cal A}_{\leq3}=I_{\rm vac}\oplus{cal A}_1\oplus{cal A}_2\oplus{cal A}_3
\]

be the direct sum of the certified continuum isometries.  Then

\[
 \boxed{{\cal M}_a={\cal A}_{\leq3}U_aI_\Omega}
\]

obeys

\[
 {cal M}_a^*{\cal M}_a=I_2 .
\]

Its output is the direct sum of the hard range and the physical five-, six-,
and seven-point nested continuum ranges.  This is the first exact operator
that places the finite stochastic dynamics, its survival term, and all
seventy-five physical continuum channels on one column.  It is not a
two-sided spacetime S operator.

## Exact trajectory kernels

The conditional edge rates are

\[
 q_0=\frac1{48},\qquad q_1=\frac5{64},\qquad
 q_2=\frac{27}{400}.
\]

The numbers of children at the three levels are (3,4,5), so the amplitude
drifts are

\[
 d_0=\frac1{32},\qquad d_1=\frac5{32},\qquad
 d_2=\frac{27}{160},\qquad d_3=0.
\]

For one history with (k) emissions at
(0<t_1<\cdots<t_k<a), the vacuum trajectory is

\[
 \psi_k(t_1,\ldots,t_k;a)
 =\sqrt{\prod_{j<k}q_j}\,
 \exp\!\left[-d_0t_1
 -\sum_{j=1}^{k-1}d_j(t_{j+1}-t_j)
 -d_k(a-t_k)\right].
\]

The hard amplitude is (psi_0=e^{-a/32}).  Integrating the squared kernels
over their ordered simplices and summing the (1,3,12,60) histories gives

\[
 p_0=e^{-a/16},
\]

\[
 p_1=\frac14(e^{a/4}-1)e^{-5a/16},
\]

\[
 p_2=\frac{25}{88}
 \left(e^{47a/80}-11e^{27a/80}+10e^{5a/16}\right)e^{-13a/20},
\]

\[
 p_3=-\frac1{88}
 \left(135e^{47a/80}-297e^{27a/80}
 -88e^{13a/20}+250e^{5a/16}\right)e^{-13a/20}.
\]

Their integral representation proves positivity, and exact simplification
gives

\[
 p_0+p_1+p_2+p_3=1
\]

for every (a\geq0).  The first allowed coefficients are

\[
 p_1=\frac a{16}+O(a^2),\qquad
 p_2=\frac{5a^2}{512}+O(a^3),\qquad
 p_3=\frac{9a^3}{8192}+O(a^4),
\]

which are the independently certified five-, six-, and seven-point results.
The physical continuum intertwiners preserve the complete norms, not only
these leading coefficients.

## The hard/dressed term is now on the same finite column

The hard survival probability begins as

\[
 p_0=1-\frac a{16}+O(a^2).
\]

The physical real continuum has the opposite response (+a/16).  Multiplying
by the common Born coefficient (3/32) gives

\[
 \Delta_{\rm hard}=-\frac3{512},\qquad
 \Delta_{\rm real}=+\frac3{512},\qquad
 \Delta_{\rm inclusive}=0.
\]

This closes the hard/real normalization inside the pinned finite
resolution-stochastic model.  The zero response of the public
(R_tP R_t^\dagger) pushforward is not used and is not a physical scattering
summand.

The boundary remains important.  The HP architecture is the exact minimal
unitary dilation of the pinned channel-resolved process, but it has not been
derived from the complete BT loop Hamiltonian.  The displayed cancellation
is therefore a constructed physical completion, not a full BT NLO theorem.

## Minimal typed (R_t) compression

The earlier rank/Jordan obstruction showed that the public quadratic leg and
the physical splitting map cannot be the same operator.  We can now state
exactly what is needed for them to occur in one dilation.

On the cross-metric fibre

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix},
\]

take the concrete public representative

\[
 D=\begin{pmatrix}0&1\\0&1\end{pmatrix}.
\]

Then

\[
 D^TJD=\begin{pmatrix}0&0\\0&2\end{pmatrix},\qquad
 J D^TJD=\begin{pmatrix}0&2\\0&0\end{pmatrix}.
\]

The raised Gram is nonzero, rank one, and nilpotent.  The physical map is

\[
 T=\operatorname{diag}(2Q,2L),\qquad
 T^TJT=-\rho J,qquad \rho=-4LQ>0.
\]

Suppose (D) is retained as the first orthogonal output leg and (C) is the
missing leg.  Equality with the physical pullback forces, rather than merely
suggests,

\[
 C^TJC=-\rho J-D^TJD
 =\begin{pmatrix}0&-\rho\\-\rho&-2\end{pmatrix}.
\]

An exact minimal representative is

\[
 \boxed{C_\rho=
 \begin{pmatrix}-\rho&-1\\0&1\end{pmatrix}}.
\]

Let (F=(D,C_\rho)^T) and (eta=J\oplus J).  Then

\[
 F^T\eta F=-\rho J=T^TJT.
\]

Because (T) is invertible above unequal-mass threshold,

\[
 W=FT^{-1}
\]

satisfies

\[
 W^T\eta W=J,\qquad WT=F,qquad \pi_{\rm public}WT=D.
\]

Thus (W) is a Krein isometry from the physical target fibre into the common
four-dimensional target, and the public map is its first-leg compression.
This is a genuine commuting square, not an equality of the two maps.

## What the missing block must be

The forced missing Gram has

\[
 \det(C_\rho^TJC_\rho)=-\rho^2<0.
\]

It is nondegenerate with inertia ((1,1)).  Consequently:

1. The auxiliary target needs at least two dimensions.
2. A positive-Hilbert noise fibre cannot realize it.
3. Its raised Gram is

   \[
   C_\rho^\sharp C_\rho
   =\begin{pmatrix}-\rho&-2\\0&-\rho\end{pmatrix},
   \]

   with trace (-2\rho\ne0).
4. A trace-null (Q)-remainder of Eq. (19) cannot by itself supply the
   missing physical direction.

The missing block must therefore contain a non-null two-direction component.
All minimal realizations of its forced nondegenerate Gram are equivalent up
to a target Krein isometry.  This fixes the size, inertia, pullback, and trace
of the object that BT zero-mode, vacuum, or higher-composite dynamics would
have to produce.

The construction is measurable pointwise on the same compact continuum core
where (ho>0).  It is not extended through the measure-zero equal-mass
threshold where (T^{-1}) degenerates.

## Eq. (19) boundary and next gate

The two objects remain correctly typed:

- (R_tP_\chi^{(\phi)}R_t^\dagger) is a field/projector pushforward.
- ({\cal M}_a) is a physical vacuum transition column in a pinned
  resolution-stochastic completion.

The public finite-mode, zero-mode-completed quadratic sector still satisfies
the Eq. (19) form through order (lambda), with (Q_1=0).  The new
compression square does not promote that statement to all orders.  Instead,
it converts the former rank mismatch into a precise constructive gate:
derive or obstruct a BT dynamical block with

\[
 C^TJC=-\rho J-\operatorname{diag}(0,2),qquad
 \operatorname{Tr}(C^\sharp C)=-2\rho,
\]

on the same zero-mode, charge, trace, and continuum domain while retaining
the public cross-CCR identities.

The independent all-order discriminator is the eight-point fourth quotient.
The missing-complement calculation is closer to Eq. (19), because another
scalar emission coefficient cannot by itself construct the public-to-physical
operator bridge.

Nothing here constructs a fourth jump, complete BT probability, arbitrary
incoming-noise scattering, a two-sided spacetime Møller/LSZ/S operator, the
all-order Eq. (19), a gravity/BRST lift, a new dimension, or anything
`LORENTZIAN-CAUSAL`.

## Verification receipt

All scientific Python, SymPy, and TeX commands ran sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and work-item/certificate/schema JSON parse | PASS | 0.02 s | 14,828 KB |
| 0 | scoped `git diff --check` | PASS | 0.01 s | 10,956 KB |
| 1 | exact producer and certificate drift check | PASS, 33/33 | 1.35 s | 75,912 KB |
| 1 | method-distinct Laplace-resolvent and Krein-congruence verifier | PASS, 28/28 | 1.25 s | 78,520 KB |
| 1 | producer/verifier plus fourteen falsifying mutations | PASS, 16/16 | 18.89 s | 78,880 KB |
| 1 | Paper V two-pass PDF build | PASS, no new overfull box | 0.43 s + 0.44 s | 50,624 / 50,708 KB |
| 1 | Paper VI two-pass PDF build | PASS, no warning or overfull box | 0.44 s + 0.44 s | 50,748 / 50,600 KB |

Paper V retains its four pre-existing overfull boxes and pre-existing
PDF-string warnings; the new passage introduces none.  Paper VI remains
clean.  The added-line audit finds no changelog prose in either manuscript.

Tier 2 is unnecessary because the mathematical inputs are unchanged and
content-addressed; this result is their new exact operator-level consumer.
Tier 3 is unnecessary because no freeze, release, shared-core change,
all-order Eq. (19), complete BT probability, gravitational transfer, or
Lorentzian theorem is promoted.

The advisory Science Forge import and shadow rails were not run during this
receipt.  Concurrent Forge compilation already occupied more than one
gigabyte in one process plus several compiler workers, so starting another
memory-heavy rail would have violated the session's OOM precaution.  This is
recorded as not run, not as a pass.  No skipped or advisory rail is counted as
scientific evidence.
