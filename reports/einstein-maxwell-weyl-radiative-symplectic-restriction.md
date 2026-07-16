# Combined Weyl--Maxwell restriction on standard Einstein--Maxwell radiation

## Theorem

`EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION` combines the direct
axial and polar current certificates on every standard radiative harmonic
with `lambda=ell(ell+1)>=6`, every periodic `S1` momentum, every spherical
multiplicity, and both physical master branches.  It applies before the final
residual `SO(4,2)` quotient.

Let `M_A` and `M_P` be the certified Einstein--Maxwell master operators and
let `M_rad=M_A direct_sum M_P`.  On the radiative solution space the pullback
of the Weyl--Maxwell Lee--Wald form obeys

```text
Omega_WM(u,v) = Omega_EM(u, R_rad v),
R_rad = p_lambda(M_rad),
p_lambda(x) = 1 + (3/2)(x-lambda).
```

This is one parity-independent spectral polynomial.  Its coordinate matrices
differ between the axial and polar master bases, just as the direct off-shell
current matrices differ.

The master eigenvalues and relative symplectic weights are

```text
mu_+ = lambda+sqrt(2lambda),  r_+ = 1+(3/2)sqrt(2lambda),
mu_- = lambda-sqrt(2lambda),  r_- = 1-(3/2)sqrt(2lambda).
```

For `lambda>=6`, `r_+>0` and `r_-<0`.  Each real spatial harmonic therefore
has four oscillator blocks—two parities times two branches—with relative
coefficient signature `(2,2)` and no zero block.  The identity tangent
inclusion is target-nondegenerate but does not preserve the Einstein--Maxwell
symplectic form.

## Orthogonality

The direct-sum claim includes the selection rules rather than assuming them.

- Different spherical or Fourier labels vanish by `SO(3)` and `S1`
  orthogonality, with complex `(n,ell,m)` paired with `(-n,ell,-m)`.
- Axial and polar representatives have opposite spatial parity, so invariance
  of the Lee--Wald form makes their cross-pairing equal to its negative.
- Within a parity, the master operator is self-adjoint for the positive
  Einstein coefficient form.  Its distinct branch eigenspaces are therefore
  orthogonal for both `E` and `E p_lambda(M)`.  Equivalently, conservation and
  time-translation covariance kill the unequal-frequency phase because
  `omega_+^2-omega_-^2=2sqrt(2lambda)>0`.

These statements promote the matching diagonal branch weights to the full
solution-space operator identity above.

## Reality and multiplicity convention

A complex coefficient labelled `(n,ell,m)` is bookkeeping: reality pairs it
with `(-n,ell,-m)`, so it is not a second independent real oscillator.  In a
real basis there are `2ell+1` spherical harmonics, together with one constant
`S1` harmonic at `n=0` or a cosine/sine pair at each `n>0`.

Writing `q=2ell+1` for `n=0` and `q=2(2ell+1)` for `n>0`, the sector contains
`4q` real oscillator/Darboux blocks and has real phase-space dimension `8q`.
There are `2q` relative-positive and `2q` relative-negative blocks.  On full
real Cauchy data, the corresponding relative-operator eigenspaces have
dimensions `4q` and `4q`.

## Interpretation and boundary

This is a classical `LOCAL-ALGEBRAIC`/`REDUCED-MODE` comparison theorem.  The
negative relative coefficient does not by itself certify a negative-norm
particle, a quantum ghost, or a unitarity failure.  No positive-frequency
complex structure or one-particle Hilbert norm has been constructed here.

The theorem establishes that ordinary `ell>=2` Einstein--Maxwell radiation is
not removed by target Weyl gauge before the final residual quotient.  It does
not cover physical `ell=1`, homogeneous `ell=0`, axial twist, extra
fourth-order Weyl--Maxwell solutions, nonlinear closure, causal scattering,
the final residual quotient, or quantum theory.

The next gate is the physical `ell=1` restriction using its certified quotient
representatives, followed by direct-current calculations on the homogeneous
and twist generalized global solutions.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_radiative_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_radiative_symplectic_restriction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_radiative_symplectic_restriction
```

Tier 2 is satisfied by the content hashes of the imported direct-current axial
and polar certificates.  Their expensive arbitrary-harmonic fixtures were not
replayed because neither fixture nor either current engine changed.  Tier 3 is
not required because this does not freeze shared core algebra or promote a
Lorentzian or quantum lifecycle state.
