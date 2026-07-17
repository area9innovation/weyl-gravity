# Every fixed generic ell k=0 combined second-order cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For any one fixed integer `ell>=2`, let the real `k=0` tangent contain all
`m`, both axial and polar parities, both Einstein branches, and both extra
polarizations.  If its total compact stabilizer moment maps satisfy

```text
H=J_1=J_2=J_3=0,
```

then the complete quadratic Weyl--Maxwell source has a second-order
correction.

The missing structural step is now exact.  On each certified `p` or `q`
primary, the reduced quadratic action is a regular coefficient form times a
`1+1` Lorentz-scalar polynomial in `s=omega^2-k^2`.  Varying the homogeneous
circle metric gives terms proportional either to the on-shell polynomial or
to `k^2`; both vanish at `k=0`.  Hence the zero-frequency circle-pressure row
is zero.  Weyl tracelessness then gives `S_sphere=S_00/2`, while the integrated
homogeneous Maxwell equation is a total time derivative and has zero
zero-frequency coefficient.  Every scalar source therefore lies along

```text
(E00,E11,sphere,Maxwell1)=(1,0,1/2,0).
```

The coefficient is the calibrated constant-lapse moment map, so `H=0` kills
the entire scalar source.  At `L=1`, the only physical axial cokernel is the
rotation triplet and is killed by `J_i=0`; the polar block has no physical
zero cokernel.  Every `L>=2` zero block is invertible.  The exact all-`ell`
resonance theorem handles every nonzero-frequency block.

As an independent spectral fixture, the generic axial extra current gives at
`ell=3`, in the standard `e1,e2` basis and normalized sphere average,

```text
S_E00 = diag(-73440/7,-7208/63),
S_E11 = 0,
S_sphere = S_E00/2,
S_Maxwell1 = 0.
```

The same formula reproduces the direct four-dimensional `ell=2` Taub matrix
exactly.  Cross-`ell` superpositions remain open because their mixed
frequency arithmetic is not contained in the fixed-`ell` resonance theorem.

## Verification receipt

Date: 2026-07-18.

* Tier 0: scoped compilation and structured-data checks, `0.06 s`, passed.
* Tier 1: new producer replay, independent verifier, and four regression
  tests, `1.70 s`, passed.
* Tier 2: seven affected producer replays followed by seven independent
  verifiers and 23 tests, `7.80 s`, passed.  Unchanged exhaustive direct
  four-dimensional fixtures were checked by content hash.
* Tier 3 was not run because cross-`ell`, opposite-momentum,
  exceptional/global, and programme-wide freeze gates remain open.
