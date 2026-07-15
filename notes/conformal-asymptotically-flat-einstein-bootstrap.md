# Asymptotically flat Einstein-sector bootstrap

## Result boundary

This is the first executable step toward the commissioned asymptotically flat
Einstein-sector theorem.  It establishes an exact `REDUCED-MODE` result for
linearized transverse-traceless fields on Minkowski space, classifies the
two leading radiative Bondi/Bach indicial roots in that reduced channel, and
defines the null-infinity data and charge questions that must be solved
next.  It does not promote the full theorem to `LORENTZIAN-CAUSAL`.

The certificate is
`bridge/certificates/asymptotically_flat_einstein_bootstrap.json`; its builder
and verifier are `bridge/einstein_sector/asymptotic_bootstrap.py`.  The exact
operator premise has its own certificate,
`bridge/certificates/flat_tt_bach_operator.json`.

The radial calculation has its own certificate,
`bridge/certificates/bondi_bach_indicial.json`, and is derived in
`notes/conformal-bondi-bach-indicial.md`.

## Exact flat TT Bach reduction

The bootstrap no longer assumes the flat TT equation.  Starting from the
linearized Riemann and Weyl tensors with signature `(-,+,+,+)`, the off-shell
two-polarization calculation verifies

```text
tr(h)=0,
div(h)=0,
R_1=0,
Ric_1=-Box h_TT/2,
tr(C_1)=0,
B_1(h_TT)=-(1/4) Box^2 h_TT.
```

The Bach convention here is
`B_mn=partial^r partial^s C_mrns`.  Both `h_plus` and `h_cross` carry the same
operator, and its exact commutator with the helicity generator vanishes.  An
action variation may rescale the geometric Bach tensor; a nonzero overall
factor does not change its kernel.

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

- the soft, Coulombic, or memory sectors;
- radial falloffs or regularity at null infinity;
- retarded/advanced support properties on the asymptotically flat complex;
- nonlinear preservation of `Ric(g)=0` inside `B(g)=0`;
- compatibility with boundary conditions at both ends of null infinity;
- a radiative symplectic or scattering equivalence.

In particular, modewise temporal invariance is not a Green-operator support
theorem.

### Three distinct zero-mode questions

The polynomial matrix identity also holds after the algebraic substitution
`q=0`.  This describes the spatially homogeneous Fourier oscillator
`d_t^4 h=0`; such a plane wave is normally excluded by asymptotically flat
spatial falloff.

It is not the same as either:

- the zero-frequency limit of radiative data, with memory and large-gauge
  structure; or
- Coulombic mass and angular-momentum aspects constrained along null
  infinity.

The earlier shorthand “`q=0` soft/Coulombic sector” is therefore retired.
The next Bondi calculation concerns the latter two boundary sectors, not
merely substitution of zero into the oscillator matrix.

## First exact radial boundary rail

For each flat Cartesian TT polarization, the certified equation is
`Box^2 phi=0`.  In retarded coordinates, the series

```text
phi=sum_(n>=0) r^(-p-n) f_n(u)Y_L
```

has radiative indicial polynomial `4p(p-1)` and therefore roots `p=0,1`.
The `p=1` branch has Einstein-compatible `1/r` Cartesian falloff and does not
change the unphysical boundary metric, but Bach permits an additional
`u`-independent datum `kappa=2 d_u f_1-Lf_0`; Einstein requires `kappa=0`.
The `p=0` branch has `O(1)`
Cartesian amplitude, produces `h_AB=O(r^2)`, and changes that boundary
metric.  Fixing the unphysical boundary metric therefore removes leading
`p=0` data kinematically while retaining both Einstein radiation and the
same-falloff `p=1` Bach obstruction.

This does not prove causal preservation, a full tensor recursion, a charge
classification, or scattering equivalence.  It moves `AF-E4` and `AF-E8`
from `OPEN` to `PARTIAL` without promoting either full claim.

## Einstein-defect formulation

The reduced theorem now introduces

```text
chi_mn=Box h_mn^TT=-2 Ric_1_mn.
```

Then Bach is `Box chi=0`, while Einstein is `chi=0`.  The complete radial
map and its certificate are documented in
`notes/conformal-einstein-defect-asymptotics.md`.

Within the `p=1` metric falloff, `kappa` is only the first nonzero candidate
coefficient of `chi`.  The next coefficient `rho` obeys

```text
6 d_u rho+(6-L)kappa=0.
```

Thus `kappa=0` implies `rho` is u-independent, not zero.  Einstein selection
requires all admissible characteristic and corner data of `chi` to vanish.
The causal theorem establishing that implication remains open.

## First null-infinity data declaration

The bootstrap selects a smooth conformal-completion rail

```text
g_tilde = Omega^2 g,
Omega = 0 and dOmega != 0 at I^+ and I^-,
I^+ ~= R x S^2 ~= I^-.
```

The Einstein seed fields are the sphere metric `q_AB`, trace-free Bondi
shear `C_AB`, news `N_AB=d_u C_AB`, mass aspect, and angular-momentum aspect.
No single provisional topology is prematurely declared physical.  Three
rails are kept separate:

| Rail | Candidate condition | Status |
|---|---|---|
| Finite-flux completion | `N_AB in L^2_u H^s(S^2)`, with `s>3` declared but not sharp | Candidate; endpoint shear not required. |
| Strong scattering core | `N_AB in L^1_u H^s intersect L^2_u H^s`, with finite endpoint shear | Candidate dense core; density not proved. |
| Soft/memory extension | Completion by soft, memory, and possibly distributional endpoint data | Topology open. |

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

## Two conformal freedoms

Two transformations must not be conflated:

```text
physical Weyl gauge:       g -> exp(2 sigma) g,
compactification frame:   (g_tilde,Omega) -> (omega^2 g_tilde,omega Omega).
```

The first acts on the physical field and is gauge only for boundary-preserving
parameters with zero renormalized charge.  The second changes the unphysical
representative of the same conformal completion.  They remain distinct until
an explicit boundary map identifies a common zero-charge action.  The
intersection is open and is part of `AF-E3`.

## Machine contract

The bootstrap now has a versioned JSON schema at
`bridge/einstein_sector/schema/asymptotic_bootstrap.schema.json`.  Every
obligation carries both the dependency tag of its partial receipt, when one
exists, and the required `LORENTZIAN-CAUSAL` tag for closure.  The verifier
rejects a missing obligation, an unknown tag, or promotion of any full
asymptotic claim.

## Obligation status

| Obligation | Status after this bootstrap |
|---|---|
| `AF-E1` | `PARTIAL`: exact linearized TT, `p=0,1`, and Einstein-defect radial recursions plus a declared Bondi seed; full tensor weighted Bach space open. |
| `AF-E2` | `OPEN`: no null-infinity retarded/advanced complex. |
| `AF-E3` | `PARTIAL`: gauge/charge criterion fixed; conformal-gravity charges open. |
| `AF-E4` | `PARTIAL`: Einstein is `chi=0`; fixed boundary metric and `kappa=0` are each insufficient, and causal zero-defect preservation is open. |
| `AF-E5` | `PARTIAL`: exact linearized fixed-mode closure; nonlinear closure open. |
| `AF-E6` | `OPEN`: no Green/current-to-radiative-flux comparison. |
| `AF-E7` | `OPEN`: no scattering cohomology or helicity theorem. |
| `AF-E8` | `PARTIAL`: the `p=0` defect and `p=1` `kappa,rho` tower are identified; tensor, soft, Coulombic, and corner data remain open. |

The next mathematical target is the full tensor Bondi-gauge recursion,
including the exceptional harmonics and the soft/Coulombic completion.
That calculation must test whether the reduced `p=0,1` classification
survives all constraints.  Charge renormalization and causal Green-operator
preservation can then be tested on the resulting boundary fields.

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
- A. Hell, D. Lust, and G. Zoupanos, *On the Ghost Problem of Conformal
  Gravity*, <https://arxiv.org/abs/2306.13714>.  Its flat-space perturbative
  boundary analysis is a control showing that a simple boundary condition
  need not recover the general Einstein solution; it is not a Bondi or
  `LORENTZIAN-CAUSAL` theorem.

## Verification

```bash
python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json
python3 -m bridge.einstein_sector.flat_tt_bach --verify bridge/certificates/flat_tt_bach_operator.json
python3 -m bridge.einstein_sector.bondi_bach_indicial --verify bridge/certificates/bondi_bach_indicial.json
python3 -m unittest bridge.einstein_sector.tests.test_asymptotic_bootstrap
```
