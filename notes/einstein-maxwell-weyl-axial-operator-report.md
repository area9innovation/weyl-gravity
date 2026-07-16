# Generic axial Weyl--Maxwell operator and extra module

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
Lifecycle state: `CLASSIFIED`

## Result

`EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR` constructs the complete generic
axial `ell>=2` Weyl--Maxwell coefficient operator on the compact
Einstein--Maxwell product, before the final residual quotient.  The calculation
retains symbolic Fourier momentum `k`, frequency `omega`, and spherical
eigenvalue `lambda`.

The independent coordinate fixture inserts
`Y_ell0=P_ell(cos(theta))` directly into the four-dimensional fields and
linearizes

```text
3 delta B_ab-delta T_ab=0,
delta div(F)^b=0.
```

The `ell=2` replay required by the operator-module preflight passes off shell:
all six axial rows separate and every unlisted tensor component vanishes.
The exact `ell=3,4` rows, together with the degree-at-most-two spectral bound
for a fourth-order natural `SO(3)`-equivariant operator, determine the generic
`lambda` coefficients uniquely.  No dispersion relation is substituted in
this reconstruction.

After harmonic-density normalization, the four-by-four reduced operator is
formally self-adjoint.  Lifting it through the previously certified exact
gauge contraction gives a six-by-six ungauged Hessian satisfying

```text
L G=0,
G^dagger L=0,
L^dagger=L
```

coefficientwise, without inverting `D`, `k`, or `omega`.

## Exact module classification

Over `F[omega]`, with `F=Frac(Q(lambda,k))`, the Smith invariant factors are

```text
1,
1,
p,
p q,
```

where

```text
p = omega^2-k^2-lambda+2/3,
q = (omega^2-k^2-lambda)^2-2 lambda.
```

The factor `q` is exactly the certified Einstein--Maxwell axial master factor.
The source-image identity is polynomial:

```text
P_W=(3 lambda-2-3 s) E_EM-6 M_EM,
s=omega^2-k^2.
```

Thus every certified Einstein--Maxwell axial solution remains a target
solution.  Away from the recorded collision `lambda=2/9`, Chinese-remainder
decomposition gives

```text
H_target = (F[omega]/(p))^2 + F[omega]/(q),
Q_extra_ax = H_target / image(H_EM) = (F[omega]/(p))^2.
```

For the physical domain `lambda=ell(ell+1)>=6`, the collision is absent.
Two explicit coefficient representatives are retained in the certificate and
have zero operator image modulo `p`.  Therefore the additional factor is not
a determinant multiplicity artifact: it is a two-polarization algebraic
solution module.

## Interpretation and claim boundary

This is the first explicit strict-inclusion theorem in the generic compact
axial block:

```text
Einstein--Maxwell axial solution module
    is a proper submodule of
Weyl--Maxwell axial solution module.
```

The two extra summands are not yet certified particles or ghosts.  No direct
four-dimensional action-Hessian match, full Einstein/extra Lee--Wald matrix,
presymplectic radical test, positive-frequency Hilbert space, causal boundary
condition, or scattering construction has been supplied.  In particular, the
result does not say that an observer sees two additional gravitons.  It says
that the unreduced fourth-order classical equations possess two additional
generic axial solution polarizations which cannot be identified with the
Einstein image by the declared gauge quotient.

The subsequent `EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT` certificate now
constructs the off-shell local concomitant directly from the polynomial
differential operator.  For arbitrary coefficient jets it proves

```text
partial_t J^t(u,v)+partial_x J^x(u,v)
  =u^T L v-(L u)^T v
```

both on the four invariant fields and on the six-field ungauged lift.  The
reduced current has 26 nonzero terms in each component; the ungauged current
has 54.  No equation of motion, dispersion relation, inverse frequency, or
inverse momentum enters the proof.

This closes the local Green-identity rail, not the Green-function rail.  The
`EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING` certificate then evaluates
that current on the two explicit extra representatives.  In the convention
`N_extra=J^t/(-i omega)` its exact determinant is

```text
det N_extra=lambda^4*(lambda-2)*(9lambda-2)/3.
```

The first principal minor and determinant are positive for every physical
`lambda=ell(ell+1)>=6`, so the extra module is nonradical with signature
`(2,0)` for the reduced-Hessian Green current.  This rules out disappearance
as a radical at that declared layer.

The next load-bearing gate is the direct four-dimensional action-Hessian match
and complete Einstein/extra Lee--Wald matrix.  Until that normalization and
all improvement terms agree, the reduced signature is not a physical norm,
ghost, or particle statement.

## Receipts

Tier 0:

```text
python3 -m py_compile \
  bridge/einstein_sector/einstein_maxwell_weyl_axial_ell2_full_tensor.py \
  bridge/einstein_sector/einstein_maxwell_weyl_axial_operator.py \
  bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_operator.py
git diff --check -- <scoped paths>
```

Tier 1:

```text
python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_operator \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ell2_full_tensor
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_operator.py
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_operator \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_operator.json
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_green_current \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_green_current.json
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_green_pairing \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json
```

The scoped operator seven-test rail passed in about 16 seconds; its generator
and independent verifier passed.  The Green-current and extra-pairing
three-test rails each passed in under one second.

Tier 2:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json
```

The exhaustive direct-tensor `ell=2,3,4` regeneration passed in about 116
seconds.  It is intentionally separated from the fast unit rail.

Tier 3 was not run: this change does not freeze a release, promote a causal or
quantum lifecycle, or alter shared core algebra.
