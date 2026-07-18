# Local SU(2) profile-coefficient enclosures

The unit-quaternion convention is

```text
D_1(y) = [[y0+i y3,  y2-i y1],
          [-y2-i y1, y0-i y3]].
```

Its normalized symmetric powers are ordered by `m=-j,...,j`.
Differentiation along `y_a=s/2` reproduces the exact skew-Hermitian
generators used by the Berger Peter--Weyl Laplacian engine, including the
separate `e3=xi3/c` metric scaling.

The rod bump becomes anisotropic in these coordinates, but its `y1` and
`y2` scales remain equal.  Coordinate sign parity and `y1`--`y2` exchange
symmetry therefore make its local Fourier matrix diagonal.  The validated
radial moments evaluate every polynomial term through `two_j=4`.  For odd
representations, powers of `y0=sqrt(1-|y|^2)` are expanded only through the
available twelfth moment and carry an exact uniform Taylor remainder below
`10^-24`.

The two detector centers are diagonal Hopf elements, so exact phase factors
convert the local diagonal matrices to global scalar-profile coefficients.
The result is uniform over both detector windows.  It does not yet include
the clock integral, polarization, coderivative, form components, modes above
`two_j=4`, or the infinite spectral tail.
