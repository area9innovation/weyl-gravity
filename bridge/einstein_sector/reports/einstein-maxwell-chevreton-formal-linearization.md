# Chevreton formal-linearization bridge

The published Bach--Chevreton relation is an Einstein--Maxwell on-shell
identity. Differentiating that identity only along an actual nonlinear family
would cover integrable tangents but would leave a gap for arbitrary Jacobi
fields on the compact background.

The gap is closed over the dual numbers

    D = R[epsilon]/(epsilon^2).

For an arbitrary perturbation `phi=(h,f)`, set
`Phi_epsilon=barPhi+epsilon*phi`. The background is an exact solution and the
coefficient of `epsilon` in each nonlinear residual is its linearization.
Consequently `phi` is a Jacobi field exactly when `Phi_epsilon` solves the
Einstein, Maxwell, and Bianchi equations over `D`. The inverse metric exists
over `D` with

    (g+epsilon*h)^-1 = g^-1-epsilon*g^-1*h*g^-1.

The Bergqvist--Eriksson derivation uses only natural tensor algebra, Leibniz
rules, covariant differentiation, curvature commutators, the differential
Bianchi identity, and the Einstein--Maxwell equations. It therefore repeats
unchanged over `D`. Taking the `epsilon` coefficient proves

    D(B-(2*kappa*Lambda/3)T-C_Ch)[phi] = 0

for every formal Einstein--Maxwell Jacobi field, without requiring an exact
real one-parameter family. Since the background flux is parallel and `C_Ch`
is quadratic in `nabla F`, its first variation vanishes. The incidence tuning
then gives `alpha_B*DB[phi]-DT[phi]=0`.

This is a formal-linearization theorem, not an explicit full off-shell BV
factorization. The latter remains a stronger open result.

## Verification receipt

Date: 2026-07-17. Dependency tag: `LOCAL-ALGEBRAIC`.

Tier 0 passed: the generator, verifier, test, schema, certificate, claim map,
and manuscript parse; scoped `git diff --check` passed; the two-pass paper
build took 1.55 seconds with no undefined citation/reference or overfull-box
warning.

Tier 1 passed with the producer replay, separately implemented verifier, and
five unit tests. Tier 2 also passed: the original Chevreton tangent, this
formal bridge, and the axial operator consumer ran 18 tests in 17.71 seconds.
The physical-ring and paper-claim-map rail passed separately in 8.01 seconds,
including six physical-ring tests. Tier 3 was not run because this commit does
not promote `THEOREM_FROZEN`, alter shared core algebra, or prepare a release.

Exact commands are recorded in the two certificate payloads and the paper
claim map.
