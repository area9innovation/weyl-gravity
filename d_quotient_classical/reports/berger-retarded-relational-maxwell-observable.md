# Retarded relational Maxwell observable on the Berger clock

## Result

The earlier `1+z=2` characteristic fixture is now realized by an actual
retarded Maxwell solution.  Let `A_mode=x A_c+y A_s` be the certified
source-free two-phase mode and choose a smooth time switch `chi` which is zero
in the past and one before emission.  Then

```text
A_ret = chi A_mode,
J     = delta d(chi A_mode)
```

has compact source because the switching slab times compact `S3` is compact.
It is Lorenz, `delta J=0`, and uniqueness of the retarded one-form wave problem
gives `A_ret=G_ret J`.  After switching, `F_ret=F_mode`; therefore the emission
at `t=0` and reception at `t=1/2` give the certified exact frequencies

```text
nu_emit    = 2 sqrt(10)/3,
nu_receive = sqrt(10)/3,
1+z        = 2.
```

The observable is a normalized integral of `T[F_ret](u,u)` over the
clock-defined slice.  It depends on `F`, not the potential, and uses the
Weyl-invariant clock metric.  Hence it is Maxwell-gauge and Weyl invariant;
the level-set integral makes its diffeomorphism covariance explicit.  The
retarded Green formula proves causal dependence.

The preparation is spatially global on compact `S3`, although its source is
compact in spacetime.  Its clock-dressed schedule is covariant as a labelled
family:

```text
(L_D + omega partial_tau_source)
  chi((theta-tau_source)/omega) = 0.
```

It is not invariant under raw `D` with `tau_source` artificially held fixed.

## Periodic clock and reduced dynamics

The phase clock is `S1`-valued.  The honest label is

```text
tau_tilde = tau + 2 pi n,  n in Z.
```

At the fixture `mu=beta/omega=8 sqrt(10)/9` is irrational.  Successive clock
crossings therefore rotate the Maxwell quadratures by `2 pi mu`; they do not
give the same reading in general.  The observable is single-valued on the
lifted clock with winding label, and multivalued if that record is discarded.
The specific signal stays within one chart and does not wrap the Hopf fibre.

On the exact two-phase reduced probe block,

```text
Omega=-32*pi**2 dx wedge dy
{x,y}=-1/(32*pi**2)
H_tau=H_t/omega=128*sqrt(10)*pi**2/9*(x^2+y^2)
```

and

```text
d_tau Q = -mu P = {Q,H_tau},
d_tau P =  mu Q = {P,H_tau}.
```

Thus every fixed-`tau_tilde` complete observable is invariant under raw `D`,
while the family varies nontrivially with the physical clock reading.  Gauge
invariance removes the arbitrary orbit parameter; it does not make relational
change vanish.

This is a reduced probe-mode Poisson bracket, not the Dirac bracket of the
open 84-row localized apparatus.

## Exact stopping point

This theorem is spatially averaged and uses the rod-free probe sector.  A
localized two-detector observable requires the rod-defined profiles and memory
transport on the backreacted metric.  Their first missing coefficients occur
at

```text
epsilon_R^2 * kappa.
```

The authoritative 84-row certificate explicitly excludes this bidegree and
its cyclic adjoints.  Accordingly the localized observer morphism, apparatus
bracket, and unqualified 84-row Green theorem remain false.  This is a typed
missing-input obstruction, not a nonexistence theorem.
