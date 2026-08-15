# BT normalized additive Ward frame

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle: `NORMALIZED_WEIGHTED_RESIDUAL_ESTIMATE_PROVED`

## Result

The additive BT contraction can be normalized inside each field. This removes
the unknown reciprocal-field normalization from the earlier Ward identity and
gives an estimate under the actual normalized Gibbs measure.

Write

\[
 q_x=e^{-\psi_x},\qquad W=\sum_xq_x,\qquad
 \pi_x={q_x\over W}.
\]

Thus \(\pi\) is a probability vector determined by the field. For the BT
residual \(r_x=(\Delta\Omega)_x/\Omega_x\), the new identity is

\[
 \boxed{
 \mathbb E_{\mu_\lambda}\sum_x\pi_xr_x^2
 =\lambda^2\mathbb E_{\mu_\lambda}
       \left(1-\sum_x\pi_x^2\right).}
\]

Since \(\sum_x\pi_x^2\geq1/N\), this proves the actual volume-uniform
estimate

\[
 \mathbb E_{\mu_\lambda}\sum_x\pi_xr_x^2
 \leq\lambda^2\left(1-{1\over N}\right).
\]

At \(\lambda=2/5\), the right side is strictly below \(4/25\). On a periodic
vertex-transitive lattice, translation invariance also gives the sitewise
identity

\[
 \mathbb E[\pi_xr_x^2]
 =\lambda^2\left({1\over N}-\mathbb E[\pi_x^2]\right).
\]

This is the first result in this route that controls the reciprocal-weighted
residual by an ordinary normalized expectation rather than by a ratio of two
unknown extensive expectations.

The result does not yet bound the field. The same construction supplies a
full modulated Stein/Ward frame and identifies the exact conjugate score of a
lowest Fourier source. A coercive estimate for that score is now the missing
one-mode theorem.

## The normalized additive vector field

Let

\[
 H=\{\psi:\sum_x\psi_x=0\},\qquad
 P_H=I-{1\over N}{\bf1}{\bf1}^T.
\]

For a fixed real site function \(a\), define

\[
 X_a(\psi)=P_H(a\pi).
\]

Every component of \(X_a\) is bounded by a constant depending only on \(a\),
even when the field runs to infinity. Its restricted divergence is

\[
 \boxed{
 \operatorname{div}_H X_a
 =-\sum_xa_x\pi_x(1-\pi_x).}
\]

To compute the action derivative, note that the unprojected logarithmic
variation \(a_xq_x/W\) induces

\[
 \delta\Omega_x={a_x\over W}.
\]

The projection subtracts only a common infinitesimal rescaling of \(\Omega\),
which leaves every residual unchanged. Differentiating
\(r_x=(\Delta\Omega)_x/\Omega_x\) therefore gives

\[
 \delta r_x={1\over W\Omega_x}
       \left((\Delta a)_x-a_xr_x\right).
\]

Consequently,

\[
 \boxed{
 X_a\mathbin\cdot\nabla A
 =\sum_x\pi_x\left[r_x(\Delta a)_x-a_xr_x^2\right].}
\]

Both formulas are pointwise finite-graph identities.

## Full normalized Stein identity

For

\[
 d\mu_\lambda(\psi)=Z^{-1}e^{-A(\psi)/\lambda^2}\,d\psi,
\]

integration by parts gives

\[
 \mathbb E[X_a\mathbin\cdot\nabla f]
 =\mathbb E[fY_a],
\]

where

\[
 Y_a={1\over\lambda^2}\sum_x\pi_x
       \left[r_x(\Delta a)_x-a_xr_x^2\right]
       +\sum_xa_x\pi_x(1-\pi_x).
\]

In particular, \(\mathbb E[Y_a]=0\). The identity is first proved for compactly
supported smooth \(f\). The certified finite-volume coercive tails and the
boundedness of \(X_a\) extend it to the polynomial observables used here.

Putting \(a=1\) gives

\[
 X_1=\pi-N^{-1}{\bf1},\qquad
 \operatorname{div}_H X_1=-D(\pi),\qquad
 X_1\cdot\nabla A=-\sum_x\pi_xr_x^2,
\]

with \(D(\pi)=1-\sum_x\pi_x^2\). Taking \(f=1\) proves the boxed normalized
residual identity.

## Fourier source normalization

For a mean-zero deterministic vector \(b\), put

\[
 F_b(\psi)=\sum_xb_x\psi_x.
\]

Since \(X_a\cdot\nabla F_b=\sum_x\pi_xa_xb_x\), translation invariance on a
periodic lattice gives

\[
 \boxed{
 \mathbb E[F_bY_a]={1\over N}\sum_xa_xb_x.}
\]

On the periodic \(L^4\) lattice with integer \(L\geq4\), take a lowest real
Fourier phase

\[
 a_x=b_x=h_x=\cos(2\pi x_\mu/L+\alpha),
\]

one has \(\sum_xh_x^2=N/2\), and hence

\[
                         \mathbb E[F_hY_h]={1\over2}.
\]

This fixes the source normalization exactly. It does not give the desired
upper bound on \(\mathbb E[F_h^2]\): Cauchy--Schwarz applied to this identity
points in the opposite direction unless a separate coercive or inverse-Witten
estimate for \(Y_h\) is supplied.

## The complete cosine--sine phase matrix

Keeping both real phases removes an artificial scalar degeneracy. On the same
periodic \(L^4\) lattice with integer \(L\geq4\), let

\[
 h_c(x)=\cos(2\pi x_\mu/L+\alpha),\qquad
 h_s(x)=\sin(2\pi x_\mu/L+\alpha),
\]

and write \(F=(F_c,F_s)\), \(Y=(Y_c,Y_s)\). For any smooth function
\(g:\mathbb R^2\to\mathbb R\), the two modulated frames give

\[
 \mathbb E\left[\sum_jG_{ij}\partial_jg(F)\right]
 =\mathbb E[Y_i g(F)],
 \qquad
 G_{ij}=\sum_x\pi_xh_i(x)h_j(x).
\]

This random \(2\times2\) matrix has the exact trace

\[
 \operatorname{tr}G=\sum_x\pi_x(h_c^2+h_s^2)=1.
\]

If

\[
 z_2=\sum_x\pi_xe^{2i(2\pi x_\mu/L+\alpha)},
\]

then

\[
 \operatorname{spec}G=\left\{{1+|z_2|\over2},
                              {1-|z_2|\over2}\right\}.
\]

Thus the total two-phase diffusion never disappears. Its smaller direction
can degenerate only if the reciprocal probability \(\pi\) localizes in the
second harmonic. Translation invariance gives

\[
 \mathbb E[G]={1\over2}I_2,
 \qquad
 \mathbb E[F_jY_i]={1\over2}\delta_{ij}.
\]

This identifies a sharper next target than a scalar score bound: control the
conditional second-harmonic localization together with the two-phase
conjugate score. It remains a normalized marginal problem, not yet its
solution.

## Diversity monotonicity

The constant frame also makes the geometry of the additive flow explicit:

\[
 D_{X_1}\pi_x=\pi_x
 \left(\sum_y\pi_y^2-\pi_x\right).
\]

Therefore

\[
 D_{X_1}D(\pi)
 =2\left[\sum_x\pi_x^3-\left(\sum_x\pi_x^2\right)^2\right]\geq0.
\]

The bracket is the variance of the value \(\pi_x\) when \(x\) itself is
sampled from \(\pi\). Thus the same bounded flow decreases the BT action and
increases reciprocal-field diversity. This makes precise why normalizing the
old contraction removes rather than adds an unknown size bias.

## Exact four-cycle fixture

On \(C_4\), take

\[
 \Omega=(1,2,1,1/2),\qquad
 \pi=(2/9,1/9,2/9,4/9),\qquad
 r=(1/2,-1,1/2,2).
\]

Then

\[
 \sum_x\pi_x^2={25\over81},\qquad
 D(\pi)={56\over81},\qquad
 \sum_x\pi_xr_x^2=2.
\]

The constant frame is

\[
 X_1=(-1,-5,-1,7)/36,
\]

and its divergence and action pairing are exactly \(-56/81\) and \(-2\).

For the nonconstant modulation and source

\[
 a=(1,-1,2,-2),\qquad b=(1,0,-1,0),
\]

the independently reconstructed values are

\[
 \Delta a=(-5,5,-7,7),qquad
 X_a=(11,-1,19,-29)/36,
\]

\[
 \operatorname{div}_H X_a={2\over27},qquad
 X_a\cdot\nabla A={47\over6},qquad
 X_a\cdot\nabla F_b=-{2\over9}.
\]

Finally,

\[
 D_{X_1}D(\pi)={208\over6561}>0.
\]

For the lowest \(C_4\) cosine--sine pair, the same probability gives

\[
 G=\begin{pmatrix}4/9&0\\0&5/9\end{pmatrix},
 \qquad z_2=-1/9,
\]

so its two eigenvalues agree exactly with the general second-harmonic formula.

The fixture checks the signs and projection terms in a field where neither
the normalized probability nor the modulation is uniform. It is a pointwise
check of the differential formulas; the Gibbs expectation identity follows
from the displayed integration-by-parts theorem, not from the fixture.

## Meaning for the reconstruction programme

The earlier additive Ward theorem said that a reciprocal-field-size-biased
mean residual square was fixed, but both its numerator and denominator were
unknown. The normalized vector field replaces that statement with an actual
expectation bounded uniformly in volume. It also supplies an exact family of
normalized conjugate scores, including the physical lowest Fourier source.

The remaining barrier is now operator-theoretic rather than a missing
normalization. The next calculation is the quadratic form of \(Y_h\) with its
\(\pi\)-weights and signed lattice Laplacian retained. A successful inverse
estimate must upper-bound \(\mathbb E[F_h^2]\) at the scale
\((N\omega_L^2)^{-1}\). A negative result must be an actual normalized BT
volume sequence. Only after this one-mode gate should the calculation pass to
dyadic shells and the interacting \(H^{-1}\) moment.

## Boundary

This result does not establish an unweighted site residual estimate, a
normalized field or lowest-mode second moment, the interacting \(H^{-1}\)
bound or its divergence, tightness, or continuum identification. It does not
change the finite-volume ordinary-OS obstruction and has no Born, Krein, or
`LORENTZIAN-CAUSAL` consequence. No literature-priority claim is made.

## Verification

Run sequentially under the 500 MB cap:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_normalized_additive_ward_frame.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_normalized_additive_ward_frame.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_normalized_additive_ward_frame

## Verification receipt

The final producer byte check passed in 0.04 seconds with peak RSS 20568 KiB.
The independent verifier passed all 17 checks in 0.12 seconds with peak RSS
30500 KiB. All 11 focused tests passed in 0.14 seconds with peak RSS 30420
KiB, including seven adversarial certificate mutations. Python compilation
passed in 0.05 seconds with peak RSS 16312 KiB. Every Python command ran under
the 500 MB virtual-memory cap.

The Science Forge planning import passed with 1669 nodes, zero invalid items,
and zero malformed events in 7.62 seconds with peak RSS 214992 KiB under
`GOMEMLIMIT=300MiB` and `GOGC=50`. Tier 2 uses unchanged, content-addressed
predecessor certificates. Tier 3 was not run because the normalized field
moment and continuum lifecycle states remain open. The Science Forge shadow
rail was skipped because no registered shadow input changed; that skip is not
recorded as a pass.
