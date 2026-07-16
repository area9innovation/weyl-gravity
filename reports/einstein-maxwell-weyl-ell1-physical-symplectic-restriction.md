# Weyl--Maxwell restriction on the physical `ell=1` quotient

## Result

`EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_SYMPLECTIC_RESTRICTION` computes the
literal Weyl--Maxwell Lee--Wald pullback on every physical axial and polar
`ell=1` Einstein--Maxwell quotient mode, for all three spherical harmonics and
every periodic `S1` momentum.  These modes obey

```text
omega^2=k_n^2+4.
```

The calculation uses the exceptional representatives themselves.  In the
polar parity this is

```text
K=0: (A,B,C,U)=(-2 Psi_P,0,2 Psi_P,Psi_P),
```

not the singular continuation of the generic `ell>=2` reconstruction.  In the
axial parity it uses `(H,Q)=(p_A,p_A)` and the normalized coordinate
`Psi_A=2p_A`.

For `Y_10=cos(theta)`, `N_10=4pi/3`, the direct on-shell target current matrices
in `(physical,residual gauge)` order are

```text
axial raw = [[-256 I pi omega/3, 0], [0,0]],
polar     = [[ -64 I pi omega/3, 0], [0,0]].
```

The complete gauge rows and columns vanish, so the target current descends to
both exceptional quotients.  The difference between the two raw physical
entries is only the certified reconstruction-coordinate normalization.  After
using `Psi_A=2p_A`, both parities give

```text
Omega_EM = -16 I pi omega/3,
Omega_WM = -64 I pi omega/3,
Omega_WM = 4 Omega_EM.
```

Thus each independent real spatial harmonic has two nonnull oscillator blocks
and relative coefficient signature `(2,0)`.  Both physical `ell=1` parities
survive target Weyl gauge before the final residual quotient.

## Why the exceptional calculation is necessary

Substitution of `lambda=2, mu=4` into the generic polar matrix gives

```text
[[8,-6],[-6,8]].
```

For the certified residual diffeomorphism `g=(2,1)`, its Einstein norm is zero,
but this continued target matrix gives `g^T G g=16` and a cross-pairing `-24`
with the physical eigenvector.  It therefore does not descend to the quotient;
it gives ratio 4 on one representative and the spurious ratio 2 on the
gauge-equivalent `K=0` representative.  The direct exceptional fixture removes
this ambiguity and independently recovers ratio 4.

## Interpretation and boundary

The physical `ell=1` triplets are massive radiative oscillators in the compact
harmonic decomposition.  They are not the `n=0` zero-frequency axial twist,
which belongs to a separate generalized global Darboux block.

This is a classical `LOCAL-ALGEBRAIC`/`REDUCED-MODE` theorem.  A positive
relative factor does not construct a positive-frequency complex structure,
one-particle Hilbert norm, causal scattering sector, or quantum unitarity
theorem.  Homogeneous, twist, extra fourth-order, nonlinear, final-quotient,
causal, scattering, and quantum claims remain open.

The next gate is to compute the six-dimensional homogeneous target matrix and
the axial-twist target matrix separately by direct currents.

## Verification

Fast Tier 1:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell1_physical_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell1_physical_symplectic_restriction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell1_physical_symplectic_restriction
```

Slow direct-current rail:

```text
python3 -m bridge.einstein_sector.weyl_maxwell_ell1_exceptional_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_ell1_exceptional_lee_wald_fixture.json
```

The initial exact slow build passed in `161.44 s`, and the frozen-fixture replay
passed in `188.80 s`.  The fast theorem imports the direct fixture and all
classical quotient inputs by content hash.  Tier 3 is not required because no
shared algebra, freeze, Lorentzian, or quantum lifecycle state is promoted.
