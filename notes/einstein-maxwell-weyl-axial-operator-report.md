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

The two extra summands are not certified particles or ghosts.  The later
Lee--Wald completion below supplies the full Einstein/extra matrix and proves
that the extra block is nonradical in the directly varied compact current.
The action-density second variation, final residual quotient,
positive-frequency Hilbert space, causal boundary condition, and scattering
construction remain open.  In particular, the result does not say that an
observer sees two additional gravitons.  It says that the unreduced
fourth-order classical equations possess two additional generic axial
solution polarizations which cannot be identified with the Einstein image by
the declared gauge quotient and do not disappear as a radical of the declared
compact Lee--Wald form.

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

`EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION` now closes the direct-current
part of that gate.  Direct four-dimensional coordinate calculations at
`ell=2,3,4`, retaining independent frequencies for the two arguments, give

```text
integral_(S2) J^t_Lee-Wald
  =N_(ell,m) J^t_reduced-Green
```

on the complete four-coefficient off-shell axial block.  The current has
spectral degree at most two, so the three exact eigenvalues uniquely promote
the identity to every `ell>=2`; `SO(3)` irreducibility promotes the `m=0`
samples to every `m`.  The integrated improvement remainder is zero.

The Einstein and extra primary modules are symplectically orthogonal in both
directions without inverting a frequency difference.  In the convention
`J^t/(-i*omega*N_(ell,m))`, the two Einstein master branches have signature
`(1,1)`, the extra block has `(2,0)`, and the complete generic axial target
block has

```text
signature=(3,1).
```

Thus the two extra directions are genuine nonradical positive directions in
the directly varied compact Lee--Wald current.  The negative direction in
this target convention lies in one Einstein-image master branch, not in the
new extra block.  This remains a classical compact harmonic statement: the
action-density second variation, final residual quotient, causal boundary
admissibility, positive-frequency Hilbert space, and quantum ghost/unitarity
questions remain separate.

Three symplectic objects must not be conflated:

| object | theory and domain | certified statement |
|---|---|---|
| `Omega_EM` | independent Einstein--Maxwell action on its solution tangent | reference source form for the inclusion problem |
| `iota^* Omega_WM` | pullback of the Weyl--Maxwell target form to the Einstein image | differs from `Omega_EM` by branch factors `1 +/- (3/2)sqrt(2lambda)` and has target signature `(1,1)` |
| `Omega_WM` | full generic axial Weyl--Maxwell target, including the extra module | orthogonal Einstein/extra decomposition with signature `(1,1) + (2,0) = (3,1)` |

Consequently the negative target-current direction does not, by itself,
assign a negative Einstein--Maxwell particle norm.  It shows that the identity
solution inclusion is not symplectic for the two independently normalized
actions.  A ghost claim additionally requires residual and boundary descent,
a physical positive-frequency space, and its quantization.

## Reduced Hessian, detector, and first quadratic extension test

`EINSTEIN_MAXWELL_WEYL_AXIAL_REDUCED_ACTION_HESSIAN` reconstructs the exact
reduced quadratic Fourier action with kernel equal to the certified formally
self-adjoint operator. Together with the Green identity and direct Lee--Wald
match, this closes the reduced normalization triangle. The literal second
expansion of the four-dimensional action density remains an independent open
audit and is not silently identified with the reconstruction.

Because the extra Gram block is invertible, its inverse defines exact
symplectic coefficient detectors `O_X^1,O_X^2`. They return the two extra
coordinates and vanish on the complete certified generic axial Einstein
image. This is a `REDUCED-MODE` observable before final residual descent, not
yet a relational or asymptotic detector.

The first nonlinear test is decisive on the complete real `ell=2,k=0` extra
span. For the basis

```text
e_1=(-6,0,6,0),  e_2=(0,-2/3,0,6),
omega^2=16/3,
```

the Hermitian mode-plus-conjugate quadratic source has constant-lapse matrix

```text
T_X=diag(-1728/5,-832/45).
```

It is negative definite. Since fixed `P_N` forces the second-order magnetic
coefficient to vanish, the certified constant-lapse adjoint pairing excludes
every smooth periodic second-order correction for every nonzero real
combination of `e_1,e_2`. Thus these modes are genuine nonradical linear
solutions but are linearization-unstable at this compact fixed-charge
`ell=2,k=0` point. Generic `ell`, nonzero `k`, varying charge fibre, `EE/EX`
channels, residual descent, and causal boundaries remain open. See
`notes/einstein-maxwell-weyl-axial-extra-taub-report.md`.

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
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json
```

The scoped operator seven-test rail passed in about 16 seconds; its generator
and independent verifier passed.  The Green-current and extra-pairing
three-test rails each passed in under one second.
The generic Lee--Wald completion five-test fast rail also passed in under one
second.

Tier 2:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json
python3 -m bridge.einstein_sector.weyl_maxwell_axial_general_lee_wald_fixture \
  --verify bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json
```

The exhaustive direct-tensor `ell=2,3,4` regeneration passed in about 116
seconds.  It is intentionally separated from the fast unit rail.
The direct independent-frequency Lee--Wald `ell=2,3,4` regeneration also
passed; it is retained as a separate slow affected-chain rail.

Tier 3 was not run: this change does not freeze a release, promote a causal or
quantum lifecycle, or alter shared core algebra.
