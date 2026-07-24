# Panel-30 supersession and bounded retry

Dependency tag: `REDUCED-MODE`.

## Append-only correction

The earlier continuation checked that the raw Taylor state was finite and
that the projective pivot excluded zero.  It did not re-check finiteness
after the correlated projective division.  At panel 31 the raw state is
finite and the \(e_2\) pivot lower bound is \(0.42120\ldots\), but the
normalized tangent contains non-finite balls.

The old two-gate predicate therefore accepts while the corrected three-gate
predicate refuses.  Panel 31 is demoted.  The last valid normalized
checkpoint is panel 30 at

\[
\rho=\frac{95}{268435456}.
\]

The prior artifact is retained as history and named explicitly by the
supersession certificate.

## Bounded subdivision/order audit

Starting from the corrected panel-30 checkpoint, the rail tests every pair

\[
\text{Taylor order}\in\{16,20,24,32,40\},\qquad
\text{subdivisions}\in\{2,4,8,16,32,64\},
\]

using the only admissible \(e_2\) chart and retaining the exact dual
base/tangent pivot identities.  None of the 30 attempts completes the next
base panel.  The only terminal gates are:

- `NONFINITE_PROJECTIVE_NORMALIZATION`;
- `E2_PIVOT_CONTAINS_ZERO`.

This exhausts only the declared step-halving/higher-order grid.  It does not
exclude a future affine, Taylor-model, or other correlated reconditioning
repair.  The next dyadic shell, \(r=4\), \(H_4\), \(T_+\), and the global
Stokes identity remain open.
