# Coefficient-explicit aligned twist--extra smooth correction

The direct four-dimensional source fixture has now been inverted in every
aligned twist-position/velocity times generic \(\ell=2\) extra-primary
channel.  The tensor product has only \(L=1,3\) outputs.  Of the sixteen
declared combinations, thirteen have a nonzero source and three vanish
identically.

For a correction

\[
 e^{-i\omega_e t}v(t),\qquad \omega_e=4/\sqrt3,
\]

the action symbol acts as \(H(\omega_e+i\partial_t)v(t)\).  Every nonzero
source has polynomial degree at most one.  The exceptional \(L=1\) sources
were solved on the complete slices \(h_t=0\) (axial) and \(U=0\) (polar),
and all four unreduced action rows were then checked exactly.  The generic
\(L=3\) action blocks are directly invertible.  All thirteen printed
corrections have zero exact remainder.

This closes the coefficient-level aligned twist--extra mixed block in the
smooth exponential-polynomial correction class.  It does not make the full
global--extra orbit correction coefficient-explicit: the remaining
zero-frequency global/global and extra/extra self coefficients still have
to be assembled.  It also does not certify a bounded, causal/retarded, or
all-orders extension.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction
```
