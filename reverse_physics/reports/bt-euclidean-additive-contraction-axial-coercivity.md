# BT additive contraction and axial coercivity

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The finite-volume BT landscape has a global monotone contraction, not merely
a unique critical point.  For every positive field on a finite connected
graph, adding the same positive constant to all components of \(\Omega\)
and restoring the geometric-mean gauge strictly lowers the action until the
vacuum is reached.  Consequently every action sublevel is contractible.

The infinitesimal contraction gives the exact actual-Gibbs identity

\[
 \mathbb E_\mu\sum_x{r_x^2\over\Omega_x}
 =\lambda^2\left(1-{1\over N}\right)
  \mathbb E_\mu\sum_x{1\over\Omega_x}.
\]

This is volume-uniform after reciprocal-field size bias.  It is not an
unweighted field or \(H^{-1}\) moment bound.

There is also a sharp positive result for every continuum field depending
on one periodic coordinate.  If \(R=\psi''+(\psi')^2\) and \(E\) is the
Euler gradient of \(\frac12\int R^2\), then on a circle of length \(\ell\),

\[
                  \|E\|_2^2\geq k_1^4\|R\|_2^2,
        \qquad k_1={2\pi\over\ell}.
\]

The coefficient is sharp at infinitesimal lowest Fourier amplitude.  Hence
a volume-uniform failure cannot be produced by a purely axial continuum
profile.  The unresolved mechanism is genuinely multidimensional.

## Explicit contraction of every sublevel

Fix the representative \(\prod_x\Omega_x=1\), and before restoring that
gauge define

\[
                   \widetilde\Omega_x(s)=(1-s)\Omega_x+s,
                   \qquad 0\leq s\leq1.
\]

Common rescaling does not change the residual.  Since the graph Laplacian
annihilates constants,

\[
 r_x(s)={\Delta\widetilde\Omega_x(s)\over
                    \widetilde\Omega_x(s)}
 =r_x(0){(1-s)\Omega_x\over(1-s)\Omega_x+s}.
\]

Every factor lies in \([0,1]\), and differentiation gives

\[
 {dA\over ds}
 =-\sum_x r_x(0)^2
 { (1-s)\Omega_x^2\over((1-s)\Omega_x+s)^3}.
\]

This is strictly negative for \(s<1\) unless \(r=0\).  Connectedness then
makes \(\Omega\) constant.  The homotopy fixes the vacuum and stays inside
the starting action sublevel, proving a strong deformation retraction of
every sublevel to the vacuum.

This is stronger than saying that extra local minima do not exist: there are
no saddle-generated sublevel topology changes anywhere in the finite
landscape.  Negative Hessian directions still occur away from stationary
points, as the earlier exact certificates show.

## Nonlinear reciprocal-field Ward identity

Let \(H=\{\psi:\sum_x\psi_x=0\}\), let \(P_H\) be its Euclidean projector,
and put

\[
                  X(\psi)=P_H e^{-\psi}=P_H\Omega^{-1}.
\]

The restricted divergence is

\[
 \operatorname{div}_H X
 =-\operatorname{tr}_H\operatorname{diag}(\Omega^{-1})
 =-\left(1-{1\over N}\right)\sum_x\Omega_x^{-1}.
\]

The unprojected direction \(e^{-\psi}\) is exactly the logarithmic tangent
to adding a constant to \(\Omega\).  Since the action gradient is mean zero,
projection does not change its pairing, and

\[
       X\mathbin\cdot\nabla A=-\sum_x{r_x^2\over\Omega_x}.
\]

Integration by parts against
\(d\mu=Z^{-1}e^{-A/\lambda^2}d\psi\) gives the displayed Ward identity.
The finite-dimensional boundary term vanishes by the lattice pilot's
already-certified superexponential range coercivity.

Equivalently, if sites and fields are jointly size-biased by
\(\Omega_x^{-1}\), the mean residual square is exactly
\(\lambda^2(1-1/N)\).  This is a new normalized interacting identity, but
the unknown normalization \(\mathbb E\sum_x\Omega_x^{-1}\) prevents it from
being an unweighted moment estimate.

## Sharp one-dimensional continuum theorem

Put \(u=\psi'\), so \(\int u=0\).  Then

\[
 R=u'+u^2,
 \qquad
 \|R\|_2^2=X+Y,
 \qquad
 X=\|u'\|_2^2,quad Y=\|u\|_4^4,
\]

because \(\int u'u^2=\frac13\int(u^3)'=0\).  The Euler gradient factors as

\[
 E=R''-2(Ru)'=j',
 \qquad j=R'-2Ru=u''-2u^3.
\]

Since \(u\) has mean zero,

\[
 -\langle j-\bar j,u\rangle=X+2Y.
\]

Cauchy--Schwarz and the sharp circle Poincare inequality give

\[
 \|j-\bar j\|_2^2
 \geq{(X+2Y)^2\over\|u\|_2^2}
 \geq k_1^2(X+Y).
\]

The last step uses \(X\geq k_1^2\|u\|_2^2\) and
\((X+2Y)^2\geq X(X+Y)\).  Applying Poincare once more to \(j\) proves

\[
                  \|E\|_2^2\geq k_1^4\|R\|_2^2.
\]

For the exact period-\(2\pi\) fixture \(u=\sin x\), normalized full-period
averages give

\[
 \langle R^2\rangle={7\over8},
 \qquad
 \langle E^2\rangle={17\over4},
 \qquad
 \langle E^2-R^2\rangle={27\over8}.
\]

The independent verifier reconstructs these values by exact Laurent--Fourier
arithmetic rather than the producer's beta-moment formula.

## Why higher dimensions are different

For a general periodic continuum field, put

\[
 R=\Delta\psi+|\nabla\psi|^2,
 \qquad
 j=\nabla R-2R\nabla\psi.
\]

The Euler gradient is the divergence of this current,

\[
                         E=\operatorname{div}j,
\]

but its curl is

\[
                  d(j^\flat)=-2\,dR\wedge d\psi.
\]

In one dimension the transverse two-form is absent, so Poincare controls the
mean-zero current by its divergence.  In higher dimensions, Hodge
decomposition allows a transverse current generated by
\(dR\wedge d\psi\).  That component contributes to current size while being
invisible to \(E\).  This is the continuum form of the weighted-current and
corrector barrier found on the lattice.

The remaining deterministic estimate is therefore specific: control the
transverse/curl part by the divergence and residual, or exhibit a sequence
where it dominates.  For the actual continuum problem it is enough instead
to prove that large transverse correctors are uniformly rare under the Gibbs
law.  The additive Ward identity supplies a new weighted input to that
statistical branch, but does not close it.

## Consequence for the remaining barrier

Three explanations are now excluded:

1. tunnelling between distinct finite-volume vacua;
2. a nontrivial finite-volume action-sublevel topology;
3. a purely one-dimensional continuum almost-stationary valley.

The exact predecessor fixture already shows that the sharp free coefficient
can fall in a field depending on two coordinates.  The live problem is
therefore a transverse-current or multidimensional cancellation problem.
The contraction suggests a concrete split: use perturbative stability near
the vacuum and use the reciprocal-weighted Ward identity plus block rarity
away from it.  Neither half has yet been joined into a Witten or Poincare
theorem.

## Boundaries

The `REDUCED-MODE` axial theorem is not evidence for a full
`EUCLIDEAN-SPECTRAL` estimate.  This result does not establish a
multidimensional volume-uniform gradient bound, a Poincare inequality,
Witten one-form coercivity, an unweighted residual or \(H^{-1}\) moment,
tightness, a continuum measure, a Born rule, a Krein reconstruction, or
anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_additive_contraction_axial_coercivity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_additive_contraction_axial_coercivity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_additive_contraction_axial_coercivity
```
