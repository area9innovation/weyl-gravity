# Full automatic-face fixed-norm rotation normal form

The generic primary multiplicities close the internal-direction gap.  Each
`q_minus` or `q_plus` scalar node has one axial and one polar current
eigenline, hence complex internal dimension two.  Each `p_extra` node has two
axial and two polar eigenlines, hence dimension four.  All these node current
spaces are definite after branch diagonalization.

At a fixed-node-norm axisymmetric point, let `N` be the number of occupied
scalar nodes and `D` the sum of their internal complex dimensions.  The
complete unquotiented rotation Hessian on
`ker d(mu_J1,mu_J2)` has exact real inertia

```text
(4*D-2, 4*D-2, 2*D-N+2).
```

After quotienting the independent node phases, the inertia is

```text
(4*D-2, 4*D-2, 2*D-2*N+2).
```

The certificate lists the two ray interiors and the two-ray relative
interior separately for every automatic face on candidates 17--21.  The
positive and negative indices always match, so internal polarizations add
hyperbolic blocks rather than a definite obstruction.  The remaining null
directions are explicit `m=0` internal/projective directions plus the
two-dimensional angular radical.

This is the complete quadratic rotation normal form with node norms fixed.
It does not yet resolve the radical into nonlinear local components or apply
to candidate 16 or an active resonance stratum.

## Verification

The exact producer, independent verifier and three focused unit tests pass.
The regenerated fail-closed Einstein atlas passes its independent verifier
and all 96 focused tests.  Paper 13 compiles in three clean `pdflatex` passes
to 24 pages with no warnings or box errors.
