# Axial physical coefficient-ring audit

The fraction-field Smith calculation in
EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR is generic in lambda and k and does not
by itself justify specialization to zero momentum. The physical-ring
certificate repairs that gap without changing the operator.

The ring is

    R_phys = Q[lambda,k,lambda^-1,(lambda-2)^-1,(9lambda-2)^-1].

The gauge-fixed Hessian has a two-by-two minor equal to minus lambda squared,
hence two unit invariant directions. Exact block elimination gives a Schur
complement p times T, where

    p = omega^2-k^2-lambda+2/3.

After removing the common factor minus three quarters, write the symmetric
entries of T as a, b, and d. The exact identity

    omega^2*(k^2+2lambda-omega^2)*a
    - k*omega*(k^2+2lambda-omega^2)*b
    - lambda*(lambda-2)*d
    = lambda^2*(lambda-2)^2

shows that these entries generate the unit ideal in R_phys[omega].
Consequently the determinantal ideals are

    I1=(1), I2=(1), I3=(p), I4=(p^2*q),

where q=(omega^2-k^2-lambda)^2-2lambda.

No k, omega, p, or q is inverted. Every physical specialization
lambda=ell(ell+1), ell at least two, and every compact momentum
k=2*pi*n/L, including n=0, therefore has fiberwise Smith factors
1,1,p,p*q. Since the p,q resultant is nonzero for every physical lambda, the
extra quotient on each fiber is two copies of K[omega]/(p).

This proves the all-momentum specialization theorem. It does not assert that
explicit global unimodular Smith transformations over the multivariate ring
have been constructed.

## Verification receipt

Date: 2026-07-17. Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Tier 0 passed: Python compilation, JSON parsing, scoped `git diff --check`,
and two-pass LaTeX compilation. The final two-pass paper compilation took
1.13 seconds and reported no undefined citation/reference or overfull-box
warning.

Tier 1 passed in 9.36 seconds with:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_physical_ring --verify bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_physical_ring.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_physical_ring
python3 bridge/einstein_sector/verify_compact_linear_paper_claim_map.py
```

The five unit tests took 5.092 seconds inside that run. Tier 2 was not run:
the imported operator certificate is unchanged and content-addressed, while
this audit adds a specialization theorem without changing the shared
operator. Tier 3 was not run because this change neither freezes a theorem
nor changes shared core algebra or prepares a release.
