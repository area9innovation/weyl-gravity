# Asymptotically flat Einstein-sector bootstrap

## Result boundary

This is the first executable step toward the commissioned asymptotically flat
Einstein-sector theorem.  It establishes an exact `REDUCED-MODE` result for
linearized transverse-traceless fields on Minkowski space and defines the
null-infinity data and charge questions that must be solved next.  It does
not promote the full theorem to `LORENTZIAN-CAUSAL`.

The certificate is
`bridge/certificates/asymptotically_flat_einstein_bootstrap.json`; its builder
and verifier are `bridge/einstein_sector/asymptotic_bootstrap.py`.

## Exact linearized closure theorem

Fix one TT polarization and one spatial Fourier mode with
`q=|k|^2>0`.  Linearized pure-Weyl gravity has the Bach equation

```text
(d_t^2 + q)^2 h = 0.
```

Write its four Cauchy data as

```text
x = (h, d_t h, d_t^2 h, d_t^3 h).
```

The Einstein wave sector is the kernel of the two constraints

```text
e_0 = (d_t^2 + q)h,
e_1 = d_t(d_t^2 + q)h.
```

If `A_B` is the first-order Bach evolution matrix and `C_E` is the
two-row Einstein constraint matrix, exact rational-polynomial arithmetic
gives

```text
C_E A_B = A_E C_E,

A_E = [[0, 1], [-q, 0]].
```

Therefore `ker(C_E)` is invariant.  Equivalently, the embedding

```text
(h, d_t h) -> (h, d_t h, -q h, -q d_t h)
```

intertwines ordinary Einstein wave evolution with the fourth-order Bach
evolution.  Per helicity, general Bach data have dimension four and Einstein
data have dimension two.

This proves that linearized nonzero-frequency Einstein data do not source
the generalized fourth-order branch in the bulk.  It is stronger than the
bare statement that Einstein solutions happen to solve the Bach equation:
the defining two-jet constraint is explicitly evolution-invariant.

## What this does not prove

The theorem is modewise.  It does not yet establish:

- the `q=0` soft, Coulombic, or memory sectors;
- radial falloffs or regularity at null infinity;
- retarded/advanced support properties on the asymptotically flat complex;
- nonlinear preservation of `Ric(g)=0` inside `B(g)=0`;
- compatibility with boundary conditions at both ends of null infinity;
- a radiative symplectic or scattering equivalence.

In particular, modewise temporal invariance is not a Green-operator support
theorem.

## First null-infinity data declaration

The bootstrap selects a smooth conformal-completion rail

```text
g_tilde = Omega^2 g,
Omega = 0 and dOmega != 0 at I^+ and I^-,
I^+ ~= R x S^2 ~= I^-.
```

The Einstein seed fields are the sphere metric `q_AB`, trace-free Bondi
shear `C_AB`, news `N_AB=d_u C_AB`, mass aspect, and angular-momentum aspect.
The provisional radiative class allows memory and requires:

```text
C_AB has finite H^s(S^2) limits as u -> +/- infinity,
N_AB belongs to L^1_u H^s intersect L^2_u H^s,
s > 3 (declared, not claimed sharp).
```

This is a specified seed, not yet an admissibility theorem.  The missing
fourth-order Bach data are the second radiative canonical pair and its
falloffs, the soft/Coulombic sectors, spatial-infinity corner matching,
operator closure on weighted or polyhomogeneous spaces, and compatible
ghost/gauge falloffs.  `AF-E1` therefore remains `PARTIAL`.

## Gauge versus asymptotic charge

The closed-cylinder rule cannot be transported unchanged.  Its proof uses
both

```text
S^3 compact  =>  Gamma_sc = Gamma_smooth,
boundary empty  =>  surface-charge rank zero.
```

Neither implication applies at null infinity.

The bootstrap adopts the covariant-phase-space criterion:

- Diff x Weyl parameters vanishing near null infinity form the proper-gauge
  core;
- a boundary-preserving parameter is proper gauge only when its renormalized
  charge variation vanishes on every tangent direction and its reference
  charge is zero;
- otherwise it is an asymptotic symmetry and is not quotiented.

Thus time translations and BMS-type transformations cannot be declared
gauge merely because they were residual conformal generators on the
cylinder.  `AF-E3` remains `PARTIAL` until the pure-Weyl presymplectic
potential, boundary counterterms, finite charges, flux law, and charge
algebra are computed.

## Obligation status

| Obligation | Status after this bootstrap |
|---|---|
| `AF-E1` | `PARTIAL`: exact linearized TT data plus a declared Bondi seed; full weighted Bach space open. |
| `AF-E2` | `OPEN`: no null-infinity retarded/advanced complex. |
| `AF-E3` | `PARTIAL`: gauge/charge criterion fixed; conformal-gravity charges open. |
| `AF-E4` | `OPEN`: no causal boundary exclusion of the extra branch. |
| `AF-E5` | `PARTIAL`: exact linearized fixed-mode closure; nonlinear closure open. |
| `AF-E6` | `OPEN`: no Green/current-to-radiative-flux comparison. |
| `AF-E7` | `OPEN`: no scattering cohomology or helicity theorem. |
| `AF-E8` | `OPEN`: extra asymptotic Weyl channels unclassified. |

The next mathematical target should be the `q=0`/soft completion and a
linearized Bondi expansion of the Bach equation.  That calculation will say
which extra fourth-order data reach null infinity and will turn the
provisional function space into an operator-tested one.  Charge
renormalization can then be performed on the resulting boundary fields.

## Sources

- A. Ashtekar and M. Streubel, *Symplectic Geometry of Radiative Modes and
  Conserved Quantities at Null Infinity*, Proc. Roy. Soc. A 376 (1981) 585,
  <https://doi.org/10.1098/rspa.1981.0109>.
- R. M. Wald and A. Zoupas, *A General Definition of Conserved Quantities in
  General Relativity and Other Theories of Gravity*,
  <https://arxiv.org/abs/gr-qc/9911095>.
- I. Lovrekovic, *Canonical charges and asymptotic symmetries in four
  dimensional conformal gravity*, <https://arxiv.org/abs/1505.05820>.  This
  is a charge-method control with generalized Fefferman--Graham boundaries,
  not an asymptotically flat result.

## Verification

```bash
python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json
python3 -m unittest bridge.einstein_sector.tests.test_asymptotic_bootstrap
```
