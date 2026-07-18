# Repository full-BV multiplicity preflight

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The standard four-factor conformal-spin-two determinant uses transverse
traceless bundles of spins (2,0,2,1). In four dimensions,

\[
\operatorname{rank}(TT_s)=(s+1)^2-s^2=2s+1,
\]

so the exact bundle ranks are

\[
(5,1,5,3).
\]

With the standard determinant signs, their signed effective rank is
(5-1+5-3=6), reproducing the independently certified effective degree count.

The imported covariant minimal BV dictionary gives component ranks

\[
\operatorname{rank}(g)=10,\qquad
\operatorname{rank}(\xi)=4,\qquad
\operatorname{rank}(\omega)=1.
\]

The generic York/Hodge decompositions read

\[
10=5_{TT}+4_{\mathrm{Diff\ orbit}}+1_{\mathrm{Weyl\ trace}},
\qquad
4=3_{\mathrm{transverse}}+1_{\mathrm{longitudinal}}.
\]

Thus the covariant minimal scalar-ghost candidate sector has rank two: the
longitudinal diffeomorphism ghost and the Weyl ghost. The standard scalar
ghost determinant has rank one. The remaining multiplicity question is
therefore localized exactly to a rank-one scalar cancellation, together with
the analytic row/operator and Berezinian map that proves it.

The 54-row Berger gauge-fixed classical carrier is not that map. It contains
34 minimal and 20 nonminimal component rows, including antifields and
contractible pairs, and its producer explicitly marks it as not a quantum
loop operator. Treating those row counts as determinant multiplicities would
silently integrate antifields and count contractible rows incorrectly.

## Receiver contract

The strict export schema requires a gauge-fixed Lagrangian integration slice,
the repository kinetic factors and exact determinant exponents, a four-row
map to the standard factors, all zero-mode policies, and verified
contractible/scalar/nonminimal cancellations. Antifields must not be listed as
independent integration variables. Every proof artifact is content-addressed.

The executable semantic receiver goes beyond schema validation. It verifies
the target rank/sign ledger `(5,+1),(1,-1),(5,+1),(3,-1)`, requires every
repository factor to be mapped exactly once or explicitly cancelled, and
requires every integration row to source a factor or be explicitly
cancelled. It also checks that the scalar output is a rank-one fermionic
factor in the standard scalar-ghost row and that both rank-one scalar ghost
inputs source it. Nested proof hashes, the frozen classical commit, and the
analytic route are checked recursively. Synthetic mutations with orphan
rows/factors, duplicate maps, wrong target or repository-factor ranks and
statistics, scalar-output drift, route drift, and bad hashes are rejected.

## Claim boundary

This preflight proves the standard factor ranks, covariant component ranks,
and the rank-one location of the missing scalar cancellation. It does not
supply a repository Euclidean Hessian, ellipticity proof, nonminimal
Berezinian, determinant measure, contour, zero-mode treatment, anomaly
coefficient, regulated Slavnov breaking, QME disposition, residual transfer,
or Lorentzian construction.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.full_bv_multiplicity_preflight --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_full_bv_multiplicity_preflight
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_full_bv_multiplicity_preflight -v
```
