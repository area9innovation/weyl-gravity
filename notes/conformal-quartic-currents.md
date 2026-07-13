# P4 cubic currents and the t-channel conformal constraint

## Scope

`symbolic/verify_conformal_quartic_currents.py` evaluates exact three-wave
coefficients of the reduced Weyl action for the scalar internal blocks in the
energy-six `AA <-> EL` calculation.  The entries reported here are raw chiral
`A_+A_- <-> E_+L_-` seeds.  The `E_+L_-` PairTerm coefficient `1/sqrt(2)` is
not hidden inside them, and no parity-projected result is formed until the
parity partner is independently evaluated.

These are stationary covariant-action currents.  They are not yet Born or
effective-Hamiltonian currents.

The fast command

```bash
python3 symbolic/verify_conformal_quartic_currents.py \
  t negative slice --audit-only
```

checks the stored normalization, generalized-CK, parity, and physical-adjoint
relations without rerunning the multi-minute curvature jobs.  Omitting
`--audit-only` regenerates the selected exact coefficient and checks it
against the frozen regression data.

## Exact t slice currents

For the forward raw chiral seed, the negative-frequency pair gives

\[
\mathcal D_{t,-}(t)=
\frac{i\sqrt5\,t(11-7t^2)}{80\pi^3(1+t^2)^2},
\]

\[
C_{t,-}=\frac{i\sqrt5}{5\pi},\qquad
a_{t,-}=\frac{i\sqrt5}{10\pi}.
\]

The positive-frequency pair gives

\[
\mathcal D_{t,+}(t)=
\frac{i\sqrt{10}\,t(11t^2-3)}{160\pi^3(1+t^2)^2},
\]

\[
C_{t,+}=\frac{i\sqrt{10}}{5\pi},\qquad
a_{t,+}=\frac{i\sqrt{10}}{10\pi}.
\]

Here `C` is the integrated slice coefficient and `a` is the coefficient of
the one-dimensional Ward covector.  Explicitly,

\[
j_{t,-}=a_{t,-}(1,-2i,1)^T,
\qquad
j_{t,+}=a_{t,+}(1,2i,1)^T,
\]

in the bra/ket convention of the Hessian rail.

For every entry in this note the measured stereographic integrand is kept
separate from the local density:

\[
\mathcal I(t)=\frac{2}{1+t^2}\,\mathcal D(t),\qquad
C=8\pi^2\int_0^\infty \mathcal I(t)\,dt.
\]

The script prints both objects independently.

## Independent Ward probes

Every reduced diffeomorphism/Weyl generator was inserted as an independent
third wave, rather than inferred from the slice result.  The four local
radial densities below are nonzero; after multiplication by the
stereographic measure their exact coefficients vanish:

\[
\begin{aligned}
\mathcal D_{-,0}&=
\frac{7\sqrt5\,t(t^2-1)}{120\pi^3(1+t^2)^2},
&C_{-,0}=0,\\
\mathcal D_{-,1}&=
\frac{3i\sqrt5\,t(t^2-1)}{20\pi^3(1+t^2)^2},
&C_{-,1}=0,\\
\mathcal D_{+,0}&=
\frac{\sqrt{10}\,t(t^2-1)}{120\pi^3(1+t^2)^2},
&C_{+,0}=0,\\
\mathcal D_{+,1}&=
\frac{i\sqrt{10}\,t(t^2-1)}{40\pi^3(1+t^2)^2},
&C_{+,1}=0.
\end{aligned}
\]

Thus the nonzero slice result is a genuine Ward current, not leakage from a
bad internal gauge representative.

## Why no ordinary t propagator is defined

The exact quadratic rail gives

\[
\kappa_t=0.
\]

The t block is the `ell=omega=1` conformal-Killing reducibility block:

\[
G_+(i,1,1)^T=0,\qquad G_-(-i,1,1)^T=0.
\]

Its transverse representatives

\[
p_+=(3,i,1)^T,\qquad p_-=(3,-i,1)^T
\]

are frequency derivatives of those reducibilities modulo ordinary gauge:

\[
\partial_\omega G_+r_+-2p_+=B_+(-2i,1)^T,
\]

\[
\partial_\omega G_-r_--2p_-=B_-(2i,1)^T.
\]

The nonzero currents therefore lie in the adjoint cokernel of a generalized
conformal-Killing zero mode.  Dividing by `kappa_t` is forbidden.  The
companion action-normalized certificate
`symbolic/verify_conformal_taub_charge.py` now proves for the selected mixed
components that `Q_s=-i s C_s`, giving
`Q_xi-[E_+^dagger,A_+]=-sqrt(5)/(5 pi)` and
`Q_xi+[L_-^dagger,A_-]=sqrt(10)/(5 pi)`.  The full fifteen-component charge
matrix and global state-space reduction remain open; this is still not a
scattering exchange coefficient.

## Physical-state caveat

This result blocks the naive energy-six oscillator calculation before it
establishes a physical obstruction.  The compact-cylinder BRST audit must
determine whether the `E/A/L` oscillator towers survive the global conformal
constraints as individual states or only through charge-neutral, dressed, or
singlet combinations.  See `notes/conformal-linearization-stability.md`.

## Parity and physical reverse

Both parity-related raw chiral seeds were assembled independently.  Their
reduced amplitudes agree exactly:

\[
a_{t,-}^{\mathcal P}=a_{t,-}
=\frac{i\sqrt5}{10\pi},\qquad
a_{t,+}^{\mathcal P}=a_{t,+}
=\frac{i\sqrt{10}}{10\pi}.
\]

Hence parity does not cancel the generalized conformal-charge current.  The
uncontracted parity current must be kept as the direct sum

\[
\frac1{\sqrt2}(j,j^{\mathcal P});
\]

it has a nonzero parity-even component and zero parity-odd component.  Only
after an internal contraction may the two equal scalar transition seeds be
combined as `(X + X^P)/sqrt(2) = sqrt(2) X`.

The physical reverse was also assembled from independently reversed external
waves, rather than assigned by conjugation.  It gives

\[
a_{t,-}^{\rm rev}=-\frac{i\sqrt{10}}{10\pi}
=\overline{a_{t,+}},\qquad
a_{t,+}^{\rm rev}=-\frac{i\sqrt5}{10\pi}
=\overline{a_{t,-}}.
\]

Its parity partners agree separately with the corresponding reverse seeds.
Thus the raw current rail passes both the parity normalization and physical
adjoint tests; neither removes the nonzero generalized-CK constraint
projection.

No ordinary t-channel propagator, exchange number, or obstruction follows
from these completed local rails.

Recorded exact runtimes in seconds were:

| probe | negative | positive |
|---|---:|---:|
| forward seed | 366.58 | 347.64 |
| forward parity | 486.30 | 459.64 |
| physical reverse | 461.90 | 486.38 |
| reverse parity | 462.89 | 486.47 |
