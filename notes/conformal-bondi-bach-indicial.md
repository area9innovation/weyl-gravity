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

## Which root is Einstein-compatible?

| Root | Cartesian TT amplitude | Bondi angular perturbation | Unphysical angular perturbation | Role |
|---|---|---|---|---|
| `p=1` | `r^-1 f_0+O(r^-2)` | `h_AB=r C_AB+O(1)` | `h_tilde_AB=r^-1 C_AB+O(r^-2)` | Einstein-compatible falloff, but not automatically Einstein. |
| `p=0` | `f_0+O(r^-1)` | `h_AB=r^2 A_AB+O(r)` | `h_tilde_AB=A_AB+O(r^-1)` | Extra leading Bach branch. |

For `p=1`, define

```text
kappa(x) = 2 d_u f_1 - L f_0.
```

The next Bach recursion is only

```text
4 d_u kappa = 0.
```

It therefore permits arbitrary `u`-independent angular data `kappa(x)`.
The Einstein wave subspace is the stricter condition `kappa=0`.  Consequently
`p=1` is an Einstein-compatible falloff containing both the Einstein wave
subspace and a same-falloff non-Einstein Bach datum.  Radial falloff alone
does not distinguish them.

For `p=0`,

```text
Box phi = -2r^-1 d_u f_0 - Lr^-2 f_0 + O(r^-3 from f_1).
```

The first two wave recursions require

```text
d_u f_0=0,
L f_0=0.
```

Thus for `L` nonzero, every nonzero `p=0` leading datum lies outside the wave
kernel, even when it is time-independent.  The scalar `L=0` case permits only
a time-independent leading datum at these orders.  A nonzero `p=0` datum
also changes the leading unphysical boundary metric.

## Boundary selection—and its exact limitation

The geometric candidate condition is

```text
delta h_tilde_AB restricted to null infinity = 0
```

in the selected conformal completion.  In the chosen flat Cartesian TT
representative this corresponds to the diagnostic falloff `h_ij=O(r^-1)`;
gauge-invariant equivalence between those formulations is not yet proved.
The condition excludes the leading `p=0` boundary-metric deformation while
retaining `p=1` falloff.  It does **not** remove the `kappa(x)` datum within
that falloff.  It is radial data at null infinity, not a condition at a
future endpoint in retarded time.

This establishes only a **kinematic boundary selection**.  It does not yet
prove that:

- the surviving `p=1` datum `kappa(x)` is excluded;
- the full tensor Bach evolution preserves the selected phase space;
- retarded and advanced Green operators preserve it;
- the `p=0` data have nonzero surface charge rather than being proper gauge;
- all extra Weyl channels have been found;
- the resulting symplectic or scattering space equals Einstein's.

Accordingly `AF-E4` is only `PARTIAL`: a concrete selection condition removes
the leading `p=0` branch, but it does not isolate Einstein even in the reduced
recursion.  `AF-E8` is also only `PARTIAL`: the leading `p=0` branch and the
same-falloff `p=1` obstruction are identified, while tensor-coupled, soft,
memory, and Coulombic channels remain.

## Exceptional and coupled sectors

The displayed scalar coefficients degenerate at `L=0` and `L=2`.  These are
scalar-recurrence degeneracies, not certified physical spin-2 exceptional
modes.  In the actual metric problem, transverse-traceless constraints couple
angular components and the angular spectrum must be recomputed with tensor
or spin-weighted harmonics.  The scalar-amplitude calculation therefore must
not classify exceptional tensor modes by itself.

## Machine hardening

The version-2 certificate does not trust the displayed recurrence strings.
It directly applies `Box` and `Box^2` to a symbolic radial term, then extracts
coefficients from finite five-term series at three integer radial weights and
compares them with both recursions.  It also binds a JSON schema, the schema
hash, the generator path and hash, the base commit, and the imported flat-TT
operator hash.

The next closure step is the full tensor Bondi-gauge recursion, followed by
the renormalized presymplectic flux and surface charges of the surviving
boundary fields.  Only then can the kinematic selection be tested for
`LORENTZIAN-CAUSAL` preservation.

The certificate now carries an `OPEN_FAIL_CLOSED` tensor-completion gate.  It
requires the full Bondi metric ansatz, every independent inverse-radius Bach
row, the radial and supplementary constraints, tensor or spin-weighted
angular operators, residual Diff x Weyl transformations, and a decision on
whether `kappa` survives those tensor constraints.  The existing local and
cylinder Bach machinery does not itself supply this null-boundary hierarchy,
so `full_tensor_bondi_recursion_constructed` remains false.

## Verification

```bash
python3 -m bridge.einstein_sector.bondi_bach_indicial --verify bridge/certificates/bondi_bach_indicial.json
python3 -m unittest bridge.einstein_sector.tests.test_bondi_bach_indicial
```
