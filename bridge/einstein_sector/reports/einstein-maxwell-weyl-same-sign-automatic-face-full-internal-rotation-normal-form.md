# Full internal automatic-face rotation normal form

The aligned angular theorem now extends to every axial/polar internal
direction at fixed occupations.  Each `q_minus` or `q_plus` node carries two
current eigenlines, one axial and one polar.  Each `p_extra` node carries
four, two in each parity.  At a section point one eigenline per occupied node
contains the axis amplitude.

Every current-orthogonal internal eigenline is absent from the linear
`J1,J2` equations.  Its five complex angular coefficients see the exact
weighted `J3` diagonal

```text
(-2, -1/4, 0, 1/4, 2),
```

so it adds real inertia `(4,4,2)`.  Combining these blocks with the aligned
inertia gives, for `N` occupied nodes and `M` total current eigenlines over
those nodes,

```text
(positive, negative, null) = (4*M-2, 4*M-2, 2*M-2*N+2).
```

All realized ray and relative-interior strata of the five automatic faces
are enumerated in the certificate.  Their inertias range from `(30,30,10)`
to `(54,54,20)`.  Thus the full internal fixed-occupation rotation kernel is
indefinite everywhere on these faces.

This closes the current-orthogonal normal-space gate.  It does not glue the
different occupation strata or say anything about the active resonance
components, which now form the next independent topology gate.

## Verification

The exact producer, independent verifier and three focused unit tests pass.
The regenerated fail-closed Einstein atlas passes its independent verifier
and all 96 focused tests.  Paper 13 compiles in three clean `pdflatex` passes
to 24 pages with no warnings or box errors.
