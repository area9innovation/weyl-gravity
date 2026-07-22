# Phase 2: generic-ell axial selection counterexample

Work item: `sf:program/work/phase2-black-hole-general-l-axial-selection`
Result token: `BH_PHASE2_GENERIC_L_AXIAL_SELECTION_OBSTRUCTED_BY_CORRECTED_X0`
Dependency tags: `LOCAL-ALGEBRAIC` + `REDUCED-MODE`
Lifecycle: `CLASSIFIED`

## Disposition

The proposed modewise theorem

```text
R_formal,finite(ell,omega) = im E(ell,omega)
```

is false in the declared axial formal class.  For every integer `ell>=2`,
`Lambda=ell(ell+1)`, and real `omega!=0`, the rate-zero top curvature carrier
has `P=1+O(r^-1)` and hence nonzero `delta Ric[h]=psi`.  It is neither an
Einstein-image nor diffeomorphism mode on Ricci-flat Schwarzschild; the
axisymmetric conformal scalar also has no axial `phi` component.  Its corrected
metric lift has finite fixed-representative Lee--Wald radial pairing.

This is the first exact counterexample permitted by the work-item stop
condition.  The oscillatory `X2` sector is therefore left unclassified.

## Correct forcing and lift

The divergence constraint gives

```text
c = [r^2(P'+Q'+i omega Q)+2r(P+Q-Q')-2Q]/(Lambda-2).
```

Writing `F=H1'`, all three original metric rows are

```text
H0' = (-i omega-2M/r^2)H1 + (-1+2M/r)F + 2c,
H1' = F,
F'  = M20 H0 + M21 H1 + M22 F + 2r(c'-Q)/(r-2M).
```

Elimination yields the independently replayed scalar equation

```text
(r^2-2Mr)F'' +(2i omega r^2+2r+2M)F'
 +(6i omega r-Lambda)F
 = 2(r^2c''-r^2Q'-2rQ+2rc'-2c).
```

Both the scalar resonance and the `H0` integration resonance are compatible.
After setting the Einstein-lift freedom to zero, the original `F'` row fixes
the constant missed by a reconstruction from `H0'` alone:

```text
H0 = 2r^2/(Lambda-2)
     +(Lambda^2-2Lambda-4iM omega)/[4 omega^2(Lambda-2)]
     +O(r^-1),

H1 = -i(Lambda^2-2Lambda+4iM omega)
     /[2 omega^3(Lambda-2)] r^-1 + O(r^-3).
```

The carrier pivots are nonzero after the compatible `n=1` resonance, and the
metric `F` pivots are `2i omega(1-n)`, nonzero for every `n>=2`.  Thus these
heads extend uniquely to an all-orders formal lift modulo the declared
Einstein shift.

## Exact current and tail bound

In `M=1` units, with `hat_omega=M omega` understood for general mass, exact
angular reduction of the literal arbitrary-profile current gives

```text
F^v(E0,bar X0)
 = -8 i pi alpha_W Lambda
   (Lambda^2-2Lambda-6i hat_omega)
   /[hat_omega (Lambda-2)(2ell+1)] r^-2 + O(r^-3).
```

The bracket cannot vanish on the declared domain: its real part is
`Lambda(Lambda-2)>0` and its imaginary part is `-6 hat_omega!=0`.

For `X0|X0`, every coefficient at `p>=-1` vanishes exactly.  The literal
current has maximal rate-zero radial shifts

```text
h0h0: -3,   h0h1: -2,   h1h1: -1,
```

and radial derivative order three.  The only dangerous powers are `p=1` and
`p=-1`; at `p=-1` the `r^2 x constant` `h0h0` contribution and the
`r^2 x r^-1` `h0h1` contribution cancel.  After the retained `r^-1` jet every
omitted term contributes only `p<=-2`.  Adding `beta E0` changes the self
pairing only by the already-finite `E0|X0` and `E0|E0` rows, so finiteness is
representative-independent under the lift ambiguity.

## Exact defect in the inherited ell=2 fixture

`bh2c_flux_class.py` first replaces the radial source by the symbol `XSRC`
and then differentiates `H0'`.  Consequently `diff(XSRC,r)=0`, omitting

```text
2r c'(r)/(r-2M)
```

from the `F'` forcing.  Substitution back into the original Ricci row gives

```text
delta Ric_{r phi}[h_legacy] - Q S_ell = c'(r) S_ell.
```

For `X0`, this is `2 S_ell/(Lambda-2)+O(r^-2)`.  At the published fixture
`Lambda=6`, the residual is `S_2/2+O(r^-2)`, exactly nonzero.  Therefore the
inherited log tail and divergent `X0` table do not certify a solution of
`delta Ric[h]=psi`; the new result does not reproduce them and records the
reason precisely.

## Verification and boundaries

The independent verifier does not import either producer.  It derives the
carrier coefficients through `P3,Q3` from the two carrier rows, replays the
scalar resonance, checks all three original forced metric rows through every
jet that can affect `p>=-2`, rebuilds the literal Lee--Wald target
coefficients, derives the radial-shift filtration, rejects the dropped-`c'`
and changed-leading-coefficient mutations, and recovers the exact
`Lambda=6` residual.

This result does not establish convergence, horizon extendibility, a global
scattering state, an asymptotic phase space or Hilbert norm, the `X2` or polar
disposition, `omega=0`, QNMs, stability, particles, positivity, or a quantum
claim.

Tier 0 and Tier 1 pass. Tier 2 is not run because all prerequisite operators
and certificates are read-only dual-hash imports. Tier 3 is not run because
this is a scoped `CLASSIFIED` counterexample, not a freeze or release.

CLOSE-OUT: DONE — the first exact counterexample closes the stop condition: the corrected generic-ell axial X0 lift is non-Einstein and has finite radial Lee--Wald pairing, while the inherited ell=2 divergent fixture fails the original delta-Ricci forcing row by the explicit residual c'(r)S_ell.
EVIDENCE: black_hole_programme/phase2/general_l_axial_selection/receipt.json
