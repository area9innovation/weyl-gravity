# Physical triangle relative-IBP boundary flux

## Result

All eleven generic physical three-`H1` triangle channels now have exact
punctured-simplex boundary fluxes and complete structured decompositions in
the seven-function basis

```text
J_triangle
log(x2/x1)
log(x3/x1)
rational_corner
M14_singlet
M15_standard_u
M16_standard_v
```

The calculation is tagged `LOCAL-ALGEBRAIC` and `EUCLIDEAN-SPECTRAL`.  It
does not assemble the eleven raw channel functions and finite `H1-H2`
contact rows into the five repository third-curvature form factors.

## Exact construction

The six-master coordinates are subtracted first.  The remainder lies in the
46-dimensional relative-IBP tangent image.  A fraction-free solve supplies a
primitive, but its 46 entries retain one common polynomial denominator until
after contraction with the three corner functionals.  This avoids symbolic
expression blowup without changing the exact identity.

The three corner numerators are at most quadratic in the angular parameter.
Their moments are evaluated in the basis

```text
I0 = (a+b)/(2*a^2*b^2)
I1 = 1/(2*a*b^2)
I2 = (log(b/a)+2*a/b-a^2/(2*b^2)-3/2)/(b-a)^3
```

and then rewritten in the global logarithm basis `log(x2/x1)`,
`log(x3/x1)`.  The exact ledger contains 11 tangent identities, 33 corner
integrals, 77 integrated-basis coordinates and 11 symmetric scale-row
regressions.

The scale response is stored as a sparse exact recipe over the certified
`M14/M15/M16` coordinate functions and master scale rows, rather than as an
artificially expanded common fraction.  Canonicalizing the three master
scale rows separately removes their sectorwise removable singularities:

```text
M14 scale = (x1^2+x2^2+x3^2)/(6*x1^2*x2^2*x3^2)
M15 scale = -(x1^2-x3^2)/(6*x1^2*x2^2*x3^2)
M16 scale =  (x1^2-x2^2)/(6*x1^2*x2^2*x3^2)
```

At `x1=x2=x3=1`, this reproduces the previously certified obstruction rows
channel by channel, including `I10: (15/2)(1/2)=15/4`.

## Independent verification

The verifier does not replay the polynomial-ring producer.  At the exact
holdout points `(2,3,5)` and `(3,5,7)` it reconstructs the 46-dimensional
tangent primitive over the rationals, checks the full residual identity,
reconstructs every corner numerator, evaluates the angular moments, combines
the seven-function basis and independently checks the scale recipes.  It also
repeats the symmetric removable-singularity reduction.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_triangle_relative_ibp_boundary_flux --emit --jobs 4
# PASS; exhaustive generation 315.61 s, peak RSS 278852 KiB

PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_triangle_relative_ibp_boundary_flux --fast
# PASS; 1.74 s, peak RSS 106576 KiB

PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_triangle_relative_ibp_boundary_flux
# PASS; 57.80 s, peak RSS 118972 KiB

PYTHONPATH=quantum-weyl pytest -q quantum-weyl/spectral/euclidean/tests/test_generic_background_physical_hessian_triangle_relative_ibp_boundary_flux.py
# 4 passed; 43.42 s, peak RSS 136972 KiB
```

The 315-second producer is an affected-certificate regeneration rail.  Normal
commit checks use the emitted-artifact validation and independent exact
holdout replay.  No higher-tier full repository suite is required because no
shared core algebra, release state or theorem freeze changed.

## Artifacts

- `quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json`
- `quantum-weyl/spectral/euclidean/generic_background_physical_hessian_triangle_relative_ibp_boundary_flux.py`
- `quantum-weyl/spectral/euclidean/verify_generic_background_physical_hessian_triangle_relative_ibp_boundary_flux.py`
- `quantum-weyl/spectral/euclidean/schema/generic-background-physical-hessian-triangle-relative-ibp-boundary-flux-v1.schema.json`

## Next gate

Assemble the eleven integrated physical triangle functions and the already
certified finite `H1-H2` contact rows into the five repository
third-curvature form factors.  Complete `Gamma_1`, `Q_1`, residual transfer
and Lorentzian claims remain fail-closed.
