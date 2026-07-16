# Einstein--Maxwell/Weyl--Maxwell symplectic-restriction preflight

## Established

`EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT` freezes the next compact
calculation as a **linear tangent symplectic restriction**, not a nonlinear
solution-space pullback.  This matters because the complete linear on-shell
Einstein--Maxwell tangent inclusion is certified, while some fixed-flux
tangents have second-order extension obstructions.

The preflight also closes the previously open quotient-injectivity question.
If an Einstein tangent maps to zero modulo target
`Diff x Weyl x U(1)`, subtract the common `Diff x U(1)` transformation.  The
remaining representative must be

```text
(h_ab,a_a)=(2 sigma gbar_ab,0).
```

For the rational product fixture, the conformal variation of the
Einstein--Maxwell metric equation is

```text
delta E_ab/2
 =-nabla_a nabla_b sigma+gbar_ab Box sigma
  +Lambda sigma gbar_ab+kappa sigma T_ab.
```

Here `Lambda=kappa*rho=1/2`.  Its `tt`, `xx`, and sphere-trace rows give

```text
sigma_xx+Delta_S2 sigma=0,
sigma_tt-Delta_S2 sigma=0,
-3 Delta_S2 sigma+2 sigma=0.
```

On `Delta_S2 Y_lm=-ell(ell+1)Y_lm`, the last equation is

```text
[3 ell(ell+1)+2] sigma_lm=0.
```

The coefficient is strictly positive for every `ell>=0`, hence `sigma=0`.
Therefore the induced map

```text
ker(L_EM)/(Diff x U(1)) -> ker(L_WM)/(Diff x Weyl x U(1))
```

is injective on the declared smooth fixed-bundle tangent domain.

## Frozen calculation contract

The restriction must use the exact actions

```text
S_EM=int sqrt(-g)[(R-2 Lambda)/(2 kappa)-F^2/4],
S_WM=int sqrt(-g)[alpha_B C^2/8-F^2/4]
```

at `alpha_B=3`, `kappa=1`, `Lambda=1/2`, `P=1`, `N=2`.  It must retain the
complete curvature terms and background-flux metric/potential mixing in the
Maxwell current.  The generalized global representatives remain at symbolic
time until current conservation has been proved.

The output inventory is exhaustive for the certified standard harmonic
tangent: axial and polar radiative blocks, the physical `ell=1` quotient, the
six-dimensional homogeneous block, and the three axial twist pairs.  Every
block must report its exact matrix, rank, kernel, and comparison with the
Einstein--Maxwell form.

The existing flat theorem is a mandatory control: the pure-Weyl gravitational
current must vanish on flat Einstein TT waves.  Thus any nonzero product
restriction must be carried by curvature or background flux.

## Interpretation

Target Weyl gauge does not remove the ordinary Einstein--Maxwell tangent
classes at this background.  What remains open is whether the Weyl--Maxwell
Lee--Wald form is nondegenerate on them and whether all blocks carry one
common nonzero multiple of the Einstein--Maxwell form.  Degeneration would
mean that Einstein roots require extra fourth-order partners in the full Weyl
phase space; it would not mean that the wave solutions are absent.

This is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.  It is not a nonlinear closure,
final `SO(4,2)` quotient, causal scattering, or quantum theorem.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symplectic_preflight --verify bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symplectic_preflight.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symplectic_preflight
```
