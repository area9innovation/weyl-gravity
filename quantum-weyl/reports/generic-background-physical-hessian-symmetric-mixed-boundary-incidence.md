# Symmetric physical-Hessian mixed boundary incidence

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The exact triangle and contact logarithmic rows have now been assembled at
(x_1=x_2=x_3=1).  The isolated obstruction certificate stores one ordered
triangle, while the polarized trace-log contains six orderings.  The contact
certificate already contains its (-1/2) trace-log weight and must be summed
over both endpoints of all three contact cells.

With those incidence multiplicities, the eleven raw five-carrier coordinates
of the combined scale row are

```text
I10_123:                         -787/2
I24_123 = I24_213 = I24_312:   -3661/18
I25_123 = I25_213 = I25_312:     -83
I28_123 = I28_132 = I28_231:       0
I29_123:                          -528
```

The exact equal-box TT carrier evaluates these rows to

\[
 -\frac{1975}{72}+\frac{2704}{27}=\frac{15707}{216}.
\]

Therefore the algebraic (H_2) contact does not cancel the symmetric-point
`M14` logarithm.  The common resolved-boundary Mellin extension instead
renormalizes a nonzero combined scale row.  This is a cancellation verdict,
not a generic form factor: the generic-box triangle corner functions, finite
local rows and full mixed incidence remain open.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_symmetric_mixed_boundary_incidence --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_symmetric_mixed_boundary_incidence
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_symmetric_mixed_boundary_incidence
```

## Verification receipt

On the producing workstation the exact certificate check, independent
consumer and four scoped tests passed in `0.70 s`, `0.75 s` and `0.75 s`.
The generated residual-atlas fragment passed the common-schema validator in
`0.30 s`; the active-frontier and atlas independent verifiers also passed.
Both Paper 12 PDFs were rebuilt without warnings and their generated claim
map replayed independently.

Tier 3 was not run: this change adds one content-addressed coefficient row and
updates only its direct frontier, atlas and paper consumers.  It does not
change a shared algebra implementation, freeze a theorem, or promote a QME,
residual-transfer or Lorentzian lifecycle state.
