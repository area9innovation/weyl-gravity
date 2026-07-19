# Generic physical-Hessian finite H1-H2 contact rows

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The three mixed `H1-H2` contact cells are quadratic in their normalized
Feynman parameter.  Write the loop-independent numerator as

```text
C(t) = C(-p)(1-t) + C(0)t + c2 t(1-t),
c2   = 4 C(-p/2) - 2 C(-p) - 2 C(0).
```

After the four-dimensional Wick contraction their density is

```text
-C(t)/(2 t(1-t) p^4) - P/(4 p^2).
```

The two pole coefficients are the already-certified endpoint rows.  In the
declared common Mellin minimal-subtraction convention,
`FP B(s,s+1)|_(s=0)=0`, so the finite contact contribution at unit
dimensionless scale is exactly

```text
-c2/(2 p^4) - P/(4 p^2).
```

The tensor calculation was performed at 28 exact box-unisolvent momentum
fixtures and projected to all 33 raw contact/carrier rows.  Two unseen tensor
fixtures replay with zero defects.  Every row is a homogeneous exact rational
box function, and the symmetric `I28` relation vanishes coefficientwise in
each contact block.  On the certified equal-box TT fixture the three finite
contact contributions sum to

```text
3188/27
```

before the common `(4*pi)^-2` loop prefactor.

This fixes only the finite contact contribution selected by the declared
Mellin minimal subtraction.  It does not fix an arbitrary mu-independent
finite local counterterm, reduce the renormalized `H1^3` triangle bulk,
complete the physical form factors, change the anomaly/QME disposition, or
certify a Lorentzian theory.

Replay:

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_h1_h2_contact_finite_rows --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_h1_h2_contact_finite_rows
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_h1_h2_contact_finite_rows
```

On the producing workstation the exact regeneration check took `10.50 s`,
the independent unseen-tensor consumer `10.05 s`, and the five scoped tests
`9.83 s`.  The affected frontier chain took `0.82 s`, the atlas plus common
fragment validator `3.18 s`, and the Paper 12 claim-map chain `0.16 s`.
The main manuscript was rebuilt in two passes and the supplement in three;
both final logs were warning-free. Tier 3 was not run because this slice does
not change shared core algebra, the anomaly/QME lifecycle, residual transfer,
or any Lorentzian claim.
