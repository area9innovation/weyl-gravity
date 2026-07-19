# Generic physical-Hessian triangle corner residues

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The three resolved logarithmic corners of every raw physical `H1^3` channel
are now integrated as exact rational functions of `(x1,x2,x3)`.  The
derivation extracts the `epsilon^2` numerator in each dominant-alpha chart;
the angular numerator has degree at most two, so only the exact moments

```text
(u^2+u*v+v^2)/(3*u^3*v^3)
(2*u+v)/(6*u^2*v^3)
1/(3*u*v^3)
```

are required.  All eleven rows replay their independently stored symmetric
obstruction coefficients, and the `I28` quotient relation vanishes at each
generic corner.  This computes the missing generic triangle residue input;
it does not yet combine it with the contact rows or dispose `M14`.

Replay:

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_triangle_corner_residues --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_triangle_corner_residues
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_triangle_corner_residues
```

The exact regeneration check took `5.41 s` and the independent consumer
`0.38 s` on the producing workstation. Tier 3 was not run because this adds a
content-addressed coefficient layer without changing shared core algebra or
promoting a QME, residual-transfer or Lorentzian lifecycle state.
