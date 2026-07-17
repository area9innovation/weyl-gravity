# Berger momentum-balanced Maxwell fixture

## Outcome

The single traveling mode's homogeneous Hopf-flux obstruction is removable
by an exact configuration in the same Maxwell field.  Add the source-free
counter-propagating solution

\[
A_b=\cos(\beta t)e^1-\sin(\beta t)e^2
\]

to the forward mode.  Their coherent sum is the standing wave

\[
A_{st}=2\cos(\beta t)e^1,
\qquad \beta=2*sqrt(10)/3.
\]

Direct four-form checks give `dF=0=d star F` for the forward, reverse, and
standing fields.  This is one Maxwell field, not two independent photon
species, and the coherent cross-stress is included.

## Normalization hardening

For every symmetric metric component, the verifier differentiates

\[
-\frac14\sqrt{-g(h)}\,F(\epsilon)_{ab}F(\epsilon)^{ab}
\]

once in `h` and twice in the Maxwell amplitude.  The repository metric BV
Euler row is normalized as twice this covariant-metric variational
derivative.  Coefficientwise,

```text
q2_repository - 2 direct_action_cubic = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
```

so the earlier factor of two and the off-diagonal `03` sign are now checked
directly from the action.

## Balanced source and gravity correction

The forward and reverse covariant Hopf fluxes are respectively
`40/9` and `-40/9`; the
standing flux is exactly `0`.  The coherent
standing source in row order `(00,01,02,03,11,12,13,22,23,33)` is

```text
['160/9', '0', '0', '0', '-160/9', '0', '0', '160/9', '0', '160/9']
```

It is `q1` closed, the retained Hessian and augmented matrix both have rank
`7`, and the normalized single-beam witness
pairs to zero.  An exact primitive is

```text
['-10240/567', '0', '0', '0', '4933120/147819', '0', '0', '153410560/4582389', '0', '28160/1953']
```

and the actual order-two correction solving
`q1 h^(2)+1/2 q2(A_st,A_st)=0` is

```text
['5120/567', '0', '0', '0', '-2466560/147819', '0', '0', '-76705280/4582389', '0', '-14080/1953']
```

with identically zero residual.

## Health and scope

The correlated standing-wave phase plane has symplectic pairing
`-64*pi**2` and positive energy coefficient
`64*sqrt(10)*pi**2/3`, hence signature `[2,0,0]`.
No negative physical direction is introduced.

Radiative Einstein-like and extra-Weyl branches are not accessed by this
stationary homogeneous block; no global noncoupling claim is made.  This is
a second-order reduced-mode correction, not an all-orders backreacted
spacetime, localized redshift experiment, or support-local theorem for a
lone traveling beam.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json`.
