# Berger scalar Hodge block: exact nonclosure obstruction

## Result

The normalized scalar Peter--Weyl carrier is defined exactly on the selected
biaxial Berger sphere, but the proposed round-style scalar exact-one-form
sector is not a subcomplex of the imported gauge-fixed Diff differential.
Consequently no restricted unary, scalar physical quotient, descended pairing
or characteristic/gradient calculation is defined on that proposed carrier.

This is the first exact representation-theoretic obstruction allowed by the
work-package stop condition.  It is not a defect of the complete 70-row BV
parent.

## Normalized scalar carrier

At

\[
 a=1,\qquad c=\frac{3\sqrt{10}}{20},\qquad
 q=c^2=\frac9{40},\qquad
 \operatorname{Vol}(S^3_{\rm Berger})
 =\frac{12\sqrt{10}}5\pi^2,
\]

the orthonormal scalar modes are

\[
 Y_{jmk}=\sqrt{\frac{2j+1}{\operatorname{Vol}}}\,D^j_{mk},
 \qquad
 \overline{Y_{jmk}}=(-1)^{m-k}Y_{j,-m,-k},
\]

where (2j\in\mathbb Z_{\ge0}) and (m,k=-j,-j+1,\ldots,j).  Their
exact scalar Laplacian and right-fibre actions are

\[
 \lambda_{jk}=j(j+1)+\frac{31}{9}k^2,
 \qquad
 e_3Y_{jmk}=-i\frac{2\sqrt{10}}3kY_{jmk}.
\]

For (j>0), the exact-one-form inclusion and projection

\[
 \iota_{\rm ex}(a)=a\,d_hY_{jmk},\qquad
 \pi_{\rm ex}(\alpha)=\lambda_{jk}^{-1}
 \langle d_hY_{jmk},\alpha\rangle_{L^2}
\]

satisfy (pi_{\rm ex}\iota_{\rm ex}=1).  The constant mode (j=0) is
exceptional because (d_hY_{000}=0).

## First closure test

Let (d_0) and (d_1) be the spatial exterior derivatives on scalars and
one-forms.  Closure of the exact-one-form scalar ghost carrier through the
gauge-fixed Diff endpoint requires

\[
 C_{\rm scalar}
 =d_1\,q_{54}[\bar c^*_{\rm diff},c_{\rm spatial}]\,d_0=0.
\]

Direct PBW reduction gives a nonzero three-row two-form operator.  Every term
contains the Berger anisotropy factor (u-v) and ends in the right generator
(e_3), with

\[
 u=\frac{3\sqrt{10}}{20},\qquad
 v=\frac{2\sqrt{10}}3.
\]

The leading temporal term in the
(\theta^1\wedge\theta^2) row is

\[
 3u^2(u-v)e_0^2e_3.
\]

On (Y_{jmk}) its coefficient is

\[
 \boxed{\frac{93}{40}ik},
\]

so (C_{\rm scalar}\ne0) for every (k\ne0).  An independent finite
Wigner-matrix replay for (2j=1,\ldots,6) reproduces this diagonal leading
block exactly: its rank is (2j+1) for odd (2j), and (2j) for even
(2j), with precisely the (k=0) kernel in the latter case.

The round-background mutation (u=v) makes the complete PBW defect vanish.
That negative control confirms that the obstruction is the anisotropic
Berger failure of the round exact/coexact Hodge split, not a fitted deletion
of a gauge row.

## Exceptional labels and fail-closed consequences

- (j=0,m=k=0): (dY=0), so the spatial exact-one-form carrier is absent;
  the homogeneous global sector is handled separately.
- Integer (j\ge1), arbitrary (m), (k=0): this first defect vanishes,
  but full scalar closure and the quotient remain `NOT_COMPUTED`.
- (j\ge\tfrac12), arbitrary (m), (k\ne0): the proposed scalar Hodge
  subcomplex is exactly obstructed.

Because the proposed generic scalar carrier is not closed, the restricted
unary, cocycle/boundary quotient, Lee--Wald Gram/inertia/radical,
characteristic/Jordan data and spatial gradient/cone data are `NOT_DEFINED`
there.  No instability conclusion follows.

## Correct next gate

The old scalar/vector/tensor successor should not be activated under the same
round-style decomposition.  The preferred replacement is to construct full
(SU(2)_L\times U(1)_R) isotypical Berger blocks that include every row mixed
by the gauge-fixed differential, then quotient the complete closed block.
An alternative is a separately certified same-background gauge fixing whose
ghost endpoint preserves the exact/coexact Hodge summands.  Either route must
retain unrestricted (Q_{\rm rel}), physical (D), physical (R_{\rm rel})
and all 70 parent rows.

The evidence is exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` computation.  The
support-local cyclic and causal full parent remains imported and unchanged;
this result does not establish a failure of its nilpotency or Green homotopy,
an all-Hodge theorem, an observer/Hadamard/particle construction, a QME
statement, positivity or unitarity.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1_TIER_RECEIPT
