# Phase 3 exact-point axial infinity carrier transport

Date: 23 July 2026

## Result

`CLASSIFIED — EXACT_POINT_INFINITY_PLANES_REACH_R4`

Dependency tags: `LORENTZIAN-CAUSAL`, `REDUCED-MODE`.

At

\[
M\omega=\frac{4097}{8192},
\]

the two Ricci-carrier infinity planes

\[
I^-_R=\operatorname{span}(XI0,XI1),\qquad
I^+_R=\operatorname{span}(XI2,XI3)
\]

have been transported from \(r=32M\) to \(r=4M\).  The certified chain uses
220 radial factors of width \(1/8\), followed by 128 factors of width
\(1/256\) in the terminal half-unit interval.  Eleven staged Grassmann
transports preserve rank four for each plane.  Because the same certified
invertible fundamental flow acts on both planes, their rank-eight endpoint
direct sum remains transverse at \(r=4M\).

The final exact-point stage has payload hash

```text
f1132afe140b7842d1129bb8e585872bef7981998f3c3723bfb24cb092b0361a
```

## What changed during the calculation

The coarser \(1/64\) terminal cover failed at the first \(r<4.5M\) graph
update even though every carrier factor itself had certified rank eight.
Refining only the last half-unit to \(1/256\), and serializing each huge
exact rational centre as an exact dyadic recentering plus outward interval
remainder, removed that artifact.  All 128 refined factors and all four
terminal transport stages pass.

This is a genuine completion of the infinity-side carrier infrastructure.
It is not the direct outgoing theorem.

## Horizon-side shortfall

The exact-point future-horizon plane was also tested with general dyadic
moving frames.  This removed the earlier coordinate-chart failure, but did
not remove radial interval wrapping: shell-boundary widths grew
approximately as

```text
0.0498, 0.213, 0.822, 3.17, 12.35, 48.23, ...
```

Eight exact frame changes per logarithmic shell produced essentially the
same boundary widths.  The missing substrate is therefore a shared-radial
Taylor model or Lohner affine state enclosure with certified QR/Grassmann
reconditioning, not another chart search.  The existing Forge request
`phase3-ivlinode-qr-lohner-reconditioning` now records this exact sentinel.

Separately, the action-derived future-horizon Lee--Wald Gram has exact
inertia \((1,2,0)\).  Its indefiniteness means Stokes conservation does not
give a semidefinite shortcut to the outgoing projection rank.

## Claim boundary

This result does **not** establish

* the future-horizon-regular plane at \(r=4M\);
* \(\det C^+_R\ne0\) or any fixed rank of \(C^+_R\);
* any rank or nonvanishing theorem for \(T^+\);
* an open frequency interval;
* a populated finite-flux scattering channel;
* a flux sign, ghost, stability, CPT or unitarity result.

The independent analytic theorem for \(T^-\) remains the global result:
the incoming block is invertible throughout \(M\omega\in[1/2,3/4]\).  The
present certificate supplies the exact-point infinity plane needed by a
future direct outgoing/reflection join.

## Verification

```bash
python3 -m \
  black_hole_programme.phase3.axial_infinity_carrier_plane_to_r4_exact_point.verify
python3 -m pytest -q \
  black_hole_programme/phase3/axial_infinity_carrier_plane_to_r4_exact_point/tests
```

CLOSE-OUT: CLASSIFIED — both exact-point infinity Ricci-carrier planes reach
\(r=4M\) with certified dimensions and transversality; the horizon join and
outgoing rank remain blocked on the validated radial Taylor/Lohner substrate.
