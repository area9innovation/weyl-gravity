# Bondi/Bach radiative indicial theorem

## The exact result

The certificate
`bridge/certificates/bondi_bach_indicial.json` gives an exact
`REDUCED-MODE` theorem for the scalar amplitude of each Cartesian
transverse-traceless polarization of linearized pure-Weyl gravity on
Minkowski space.  It is the first radial boundary calculation in the
asymptotically flat Einstein-sector programme.  It is not the complete
tensor Bondi, gauge, or BV analysis.

The imported flat-space certificate proves

```text
B_1(h_TT) = -(1/4) Box^2 h_TT.
```

Use retarded coordinates

```text
ds^2 = -du^2 - 2 du dr + r^2 q_AB dx^A dx^B
```

and an angular eigenmode `Delta_S2 Y_L=-L Y_L`.  For one term
`r^(-s) f(u)Y_L`, direct differentiation gives

```text
Box[r^(-s)fY]
  = 2(s-1) r^(-s-1) f'Y
    + [s(s-1)-L] r^(-s-2) fY.
```

Applying this identity twice gives

```text
Box^2[r^(-s)fY]
  = 4s(s-1) r^(-s-2) f''Y
    + 4s(s^2-1-L) r^(-s-3) f'Y
    + [s(s-1)-L][(s+1)(s+2)-L] r^(-s-4) fY.
```

All coefficients are exact polynomials.

## Full radial recursions in this channel

Expand

```text
phi = sum_(j>=0) r^(-p-j) f_j(u)Y_L,
s_j = p+j,
f_j = 0 for j<0.
```

The wave subspace `Box phi=0` obeys

```text
2(s_j-1) d_u f_j
  + [s_(j-1)(s_(j-1)-1)-L] f_(j-1) = 0.
```

The Bach/biwave recursion is

```text
4s_j(s_j-1) d_u^2 f_j
  + 4s_(j-1)[s_(j-1)^2-1-L] d_u f_(j-1)
  + [s_(j-2)(s_(j-2)-1)-L]
    [(s_(j-2)+1)(s_(j-2)+2)-L] f_(j-2) = 0.
```

At leading radiative order this becomes

```text
4p(p-1) d_u^2 f_0 = 0.
```

Allowing freely varying radiative data therefore gives exactly two radial
indicial roots:

```text
p=0, p=1.
```

## Which root is Einstein?

| Root | Cartesian TT amplitude | Bondi angular perturbation | Unphysical angular perturbation | Role |
|---|---|---|---|---|
| `p=1` | `r^-1 f_0+O(r^-2)` | `h_AB=r C_AB+O(1)` | `h_tilde_AB=r^-1 C_AB+O(r^-2)` | Einstein radiative falloff. |
| `p=0` | `f_0+O(r^-1)` | `h_AB=r^2 A_AB+O(r)` | `h_tilde_AB=A_AB+O(r^-1)` | Extra leading Bach branch. |

For `p=1`, imposing the second-order Einstein wave equation starts with

```text
2 d_u f_1 - L f_0 = 0.
```

Thus the Einstein branch is not merely the `p=1` falloff: its subleading
coefficients also obey the wave recursion inside the larger biwave
recursion.

For `p=0`,

```text
Box phi = -2r^-1 d_u f_0 - Lr^-2 f_0 + O(r^-3 from f_1).
```

Consequently a time-dependent `f_0` is outside the Einstein wave kernel.
It also changes the leading unphysical boundary metric.

## Boundary selection—and its exact limitation

Fixing the unphysical angular metric at null infinity, equivalently imposing
Cartesian TT falloff `h=O(r^-1)` in this channel, excludes the `p=0` leading
boundary-metric deformation while retaining `p=1` radiation.  This is a
radial falloff condition at null infinity, not a condition imposed at a
future endpoint in retarded time.

This establishes only a **kinematic boundary selection**.  It does not yet
prove that:

- the full tensor Bach evolution preserves the selected phase space;
- retarded and advanced Green operators preserve it;
- the `p=0` data have nonzero surface charge rather than being proper gauge;
- all extra Weyl channels have been found;
- the resulting symplectic or scattering space equals Einstein's.

Accordingly `AF-E4` is only `PARTIAL`: a concrete selection condition is now
known, while causal closure remains open.  `AF-E8` is also only `PARTIAL`:
one extra radiative branch is identified, but tensor-coupled, soft, memory,
and Coulombic channels remain.

## Exceptional and coupled sectors

The displayed scalar coefficients degenerate at special angular values,
including `L=0` and `L=2`.  In the actual metric problem, transverse-traceless
constraints couple angular components and restrict which harmonics exist.
The scalar-amplitude calculation therefore must not be used to classify the
exceptional tensor modes by itself.

The next closure step is the full tensor Bondi-gauge recursion, followed by
the renormalized presymplectic flux and surface charges of the surviving
boundary fields.  Only then can the kinematic selection be tested for
`LORENTZIAN-CAUSAL` preservation.

## Verification

```bash
python3 -m bridge.einstein_sector.bondi_bach_indicial --verify bridge/certificates/bondi_bach_indicial.json
python3 -m unittest bridge.einstein_sector.tests.test_bondi_bach_indicial
```
