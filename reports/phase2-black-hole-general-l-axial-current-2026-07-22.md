# Phase 2: all-ell axial Schwarzschild Einstein current

Work item: `sf:program/work/phase2-black-hole-general-l-axial-current`  
Result token: `BH_PHASE2_GENERAL_L_AXIAL_EINSTEIN_CURRENT_NONVANISHING`  
Dependency tags: `LOCAL-ALGEBRAIC` + `REDUCED-MODE`  
Lifecycle: `CLASSIFIED`

## Disposition

The literal-current gate closes on the axial Einstein image. For Schwarzschild
mass `M>0`, nonzero Weyl coupling `alpha_W`, integer `ell>=2`,
`Lambda=ell(ell+1)`, and real `omega!=0`, both formal Einstein branches have
the fixed-representative sphere-integrated Lee--Wald slice density

```text
F^v(E,bar E) = A_EE r^-2 + O(r^-3),
```

with an exactly nonzero coefficient. This is an all-ell Einstein-finiteness
theorem for the radial form. It is not an extra-branch selection theorem, a
Hilbert norm, a scattering flux topology, or an asymptotic phase-space
construction.

## Exact coefficients and normalization

For the polynomial branch, use the legacy-compatible normalization

```text
H1 = 1/2,
H0 = -i omega r/2 + (Lambda-2)/4 + M/r.
```

For the oscillatory branch, normalize the master `F=dH1/dr` to unit leading
coefficient in

```text
exp(-2 i omega r) r^(1-4 i M omega).
```

In `M=1` units the coefficients are

```text
A_E0 = -4 i pi alpha_W omega Lambda(Lambda-2)/(2 ell+1),

A_E2(unit F)
     = -i pi alpha_W Lambda(Lambda-2)
       /[omega^3(2 ell+1)].
```

Under `E -> c E`, the coefficient transforms as `A_EE -> |c|^2 A_EE`.
Consequently nonvanishing and the radial power are basis-independent even
though the displayed coefficient is not.

The former `ell=2` certificate used a frequency-dependent E2 basis. Its exact
scale is

```text
kappa = 96 omega^5 /[(2 omega-i) G(Lambda,omega)],
```

so `A_E2(legacy)=|kappa|^2 A_E2(unit F)`. At `Lambda=6` this reproduces the
published rational coefficient byte-for-byte. The apparent `G=0` wall is a
normalization wall only; it is absent from the natural unit-`F` current.

## Evaluated angular reduction

The literal current is built with an arbitrary axial profile before any mode
is selected. For

```text
S_ell=-(1-x^2) P_ell'(x)
```

the exact identities

```text
S_ell'  = Lambda P_ell,
S_ell'' = Lambda P_ell'
```

reduce the sphere integral to four evaluated norms:

```text
integral P_ell^2                 = 2/(2 ell+1),
integral x P_ell P_ell'         = 2 ell/(2 ell+1),
integral (P_ell')^2             = Lambda,
integral x^2 (P_ell')^2         = Lambda(2 ell-1)/(2 ell+1).
```

No generic Legendre integral remains. The factors `Lambda` and `Lambda-2`
show directly that the only angular zeros are the excluded representations
`ell=0,1`.

## Exact legacy-wall exclusion

Write `u=omega^2`. If the complex normalization polynomial `G` vanished at
real nonzero frequency, its real part and `Im(G)/(12 omega)` would have a
common real root in `u`. Their exact resultant is a signed factor `2^24`
times

```text
H(Lambda)=3 Lambda^5-5 Lambda^4-582 Lambda^3
          +2112 Lambda^2-2691 Lambda+1647.
```

At the first two allowed representations,

```text
H(6)  = -47331,
H(12) = -89397.
```

For `ell>=4`, put `ell=k+4`. Then

```text
H((k+4)(k+5))
= 3 k^10 + 135 k^9 + 2725 k^8 + 32490 k^7
  + 252803 k^6 + 1334853 k^5 + 4808061 k^4
  + 11545578 k^3 + 17433941 k^2 + 14610501 k
  + 4936627,
```

whose coefficients are all strictly positive for integer `k>=0`. Thus the
resultant never vanishes on the discrete physical angular domain, so `G`
has no common real zero there.

## Frequency, mass, and representative boundaries

The producer declares `omega>0` to make conjugation exact in SymPy. Every
coefficient is pure imaginary and odd in frequency, while every wall
denominator is real and even. Therefore

```text
A_EE(-omega)=-A_EE(omega)=conjugate(A_EE(omega)),
```

which proves the full real `omega!=0` statement and preserves nonvanishing.

The calculation uses `M=1`. For general `M>0`, replace frequency in every
dimensionless wall polynomial by `hat_omega=M omega`; the remaining overall
power is fixed by the declared mode normalization and cannot create a zero.

The result uses the same `LinearizedTheta` representative of the
`alpha_W C^2` action as the earlier BH2C certificate. Regular angular exact
forms integrate to zero on the closed sphere. No invariance claim is made
under unrestricted radial symplectic-potential exact-form redefinitions.

## Literal controls and independent rail

- `ell=2` is recomputed directly from `P2`, yielding
  `A_E0=-96 i pi alpha_W omega/5` and
  `A_E2(unit F)=-24 i pi alpha_W/(5 omega^3)`; the exact legacy rescaling
  reproduces both old BH2C entries.
- `ell=3` is recomputed directly from
  `P3=(5x^3-3x)/2`, yielding
  `A_E0=-480 i pi alpha_W omega/7` and
  `A_E2(unit F)=-120 i pi alpha_W/(7 omega^3)`.
- The independent verifier does not import the producer. It uses the explicit
  `P3`, the VbGeo Schouten/Kulkarni--Nomizu curvature engine, independently
  derives the `Lambda=12` master series, rebuilds the literal Lee--Wald
  current, and independently recomputes the wall resultant.
- Mutation tests reject sampled-mode promotion, unevaluated-angular-integral
  promotion, exponent-only promotion, extra-branch selection, and provenance
  format collapse.

## Tier disposition

- Tier 0: Python compilation, JSON parsing, scoped `git diff --check`, and
  exact changed-path inspection pass.
- Tier 1: deterministic producer replay, independent explicit-`P3`/VbGeo
  literal-current replay, seven structural/mutation/provenance tests, and
  residual-atlas validation pass.
- Tier 2: not run because all mathematical and engine inputs are read-only and
  imported by both SHA256 and Git-blob identity; no shared input changed.
- Tier 3: not run because this is a scoped `CLASSIFIED` theorem, not a freeze,
  release, or shared-core change.

CLOSE-OUT: DONE — the literal sphere-integrated axial Einstein Lee--Wald r^-2 coefficients are derived for every integer ell>=2 and real omega!=0, their exact nonvanishing domain is certified, ell=2 is reproduced, and ell=3 is independently replayed.
EVIDENCE: black_hole_programme/phase2/general_l_axial_current/receipt.json
