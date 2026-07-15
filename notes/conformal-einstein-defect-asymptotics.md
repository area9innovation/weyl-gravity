# Einstein-defect asymptotics

## Exact reduced theorem

For each Cartesian transverse-traceless polarization on flat space, define

```text
chi_mn = Box h_mn^TT.
```

The imported curvature calculation gives

```text
Ric_1_mn = -chi_mn/2,
R_1 = 0,
B_1_mn = -(1/4) Box chi_mn.
```

Consequently the reduced equations are

```text
Einstein:  chi=0,
Weyl:      Box chi=0.
```

Thus the linearized Einstein sector is the zero-defect subspace inside the
larger Bach solution space:

```text
ker(chi) is contained in ker(Box chi).
```

This is certified in
`bridge/certificates/einstein_defect_asymptotics.json` with dependency tag
`REDUCED-MODE`.

## Exact radial coefficient map

For

```text
phi = sum_(j>=0) r^(-p-j) f_j(u)Y_L,
chi = sum_(j>=0) r^(-p-j-1) g_j(u)Y_L,
Delta_S2 Y_L=-L Y_L,
```

direct application of the retarded wave operator gives

```text
g_j = 2(p+j-1) d_u f_j
      + [(p+j-1)(p+j-2)-L] f_(j-1),
```

with `f_j=g_j=0` for negative indices.  Einstein is therefore the complete
set of constraints

```text
g_j=0 for every j,
```

not merely a falloff condition or one leading constraint.

Applying `Box` again gives the exact defect-wave recursion

```text
2(p+j) d_u g_j
  + [(p+j)(p+j-1)-L] g_(j-1)=0.
```

The certificate proves symbolically that composing the defect map with this
wave recursion reproduces every coefficient of the previously certified
biwave recursion.  It independently extracts both maps from finite radial
series at `p=0,1,2`.

## The two metric falloffs

For `p=0`,

```text
g_0=-2 d_u f_0,
g_1=-L f_0,

chi=-2r^-1 d_u f_0-r^-2 Lf_0+O(r^-3).
```

This metric branch changes the leading unphysical boundary metric.  Fixing
that boundary metric removes the branch and hence this leading source-like
defect family.

For `p=1`, the nominal first defect coefficient vanishes identically and

```text
g_0=0,
g_1=kappa=2 d_u f_1-Lf_0,
g_2=rho=4 d_u f_2+(2-L)f_1.
```

The first two defect-wave rows are

```text
4 d_u kappa=0,
6 d_u rho+(6-L)kappa=0.
```

Therefore

```text
kappa=0  =>  d_u rho=0,
```

but it does not imply `rho=0`.  Higher defect coefficients can likewise
remain.  In particular, in the scalar channel

```text
chi=r^-3 kappa Y_L,
d_u kappa=0,
L=6
```

is already an exact single-term solution of `Box chi=0`.  This is a
stationary quadrupole-like scalar defect, not a certified tensor particle or
charge.  As an exterior radial mode it may be singular in the interior;
global regularity and spatial-infinity matching are not established.

## Correct boundary-selection target

The following are each insufficient to isolate Einstein gravity:

- `p=1` metric falloff;
- fixing the unphysical boundary metric;
- setting only `kappa=0`.

The actual target is

```text
all admissible characteristic and corner data of chi_mn vanish.
```

On a Cauchy surface the natural candidate is

```text
chi|_Sigma=0,
nabla_n chi|_Sigma=0.
```

Because `chi` obeys a second-order wave equation, these are the data whose
causal preservation should force `chi=0`.  The current certificate does not
claim the corresponding null-infinity uniqueness theorem: admissible
function spaces, tensor constraints, soft/Coulombic data, spatial-infinity
matching, and residual charges are still open.

## Physical interpretation

The ordinary helicity-`+/-2` graviton is the `chi=0` wave solution.  The
defect coefficients describe the additional data permitted by the repeated
operator `Box^2`.  A nonzero coefficient is evidence that a formal solution
is not Einstein, but it is not by itself evidence for an observable particle:
the full tensor constraints, residual quotient, presymplectic norm, and
surface charges must still be computed.

The full tensor replacement is therefore fail-closed.  The scalar theorem
does not decide whether `kappa`, `rho`, or their tensor analogues survive the
Bondi constraint hierarchy.

## Verification

```bash
python3 -m bridge.einstein_sector.einstein_defect_asymptotics --verify bridge/certificates/einstein_defect_asymptotics.json
python3 -m unittest bridge.einstein_sector.tests.test_einstein_defect_asymptotics
```
