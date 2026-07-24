# Phase 3 axial outgoing-population real-cell certificate

Date: 2026-07-24
Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
Lifecycle: `COEFFICIENT_COMPUTED`

## Established

For Schwarzschild \(M=1\), axial \(\ell=2\), and every
\[
0.49995\le\omega\le0.50005,
\]
two Arb Taylor/defect geometries certify the uniform scalar bounds
\[
|A_{{\rm out},2}|>0.011326240435330133,\qquad
|A_{{\rm out},1}|>0.14680548488890086.
\]
The frequency is represented by one real Arb ball; its coefficient
variation is accumulated into the validated spatial defect at every step.
The result is not inferred from a finite set of samples.

The exact pure-outgoing RW/RW/spin-one boundary filtration then gives
\[
\ker T_+(\omega)=0,\qquad
T_+(\omega)\in GL(3,\mathbb C)
\]
at every frequency in the cell.  Hence all three outgoing axial trace
directions are populated throughout a nonzero real-frequency interval.

Exact Stokes conservation also gives
\[
{\cal O}
=T_-^\dagger G_-T_- -H_{\mathcal H^+}
=T_+^\dagger G_+T_+.
\]
Therefore \({\cal O}(\omega)\) is nondegenerate with inertia \((1,2,0)\)
throughout the declared cell for \(\alpha_{\rm W}>0\).

## Analytic consequences

Assume the selected scalar outgoing Jost coefficients and typed factor
connection are holomorphic in connected complex neighbourhoods of the
positive real axis away from the separate threshold \(\omega=0\).  The
strict cell bounds show that neither scalar coefficient is identically zero.
Their positive-real zero sets are therefore locally finite.  Consequently
\[
T_+(\omega)\in GL(3,\mathbb C)
\]
on an open dense, full-measure subset of \((0,\infty)\); any outgoing rank
loss is confined to isolated scalar reflection zeros.

On the certified compact cell \(I_0=[0.49995,0.50005]\), continuity and
uniform invertibility imply that multiplication by \(T_+(\omega)\) is a
bounded isomorphism of \(L^2(I_0;\mathbb C^3)\).  Every square-integrable
outgoing packet in this cell therefore has a unique horizon-regular
preimage, and the pointwise Stokes identity integrates to the exact
band-limited pseudo-isometry.

More generally, on any compact \(I\Subset(0,\infty)\), the locally finite
exceptional set has measure zero.  Multiplication by \(T_+\) is injective
with dense range on \(L^2(I;\mathbb C^3)\).  It is a bounded isomorphism
when \(I\) contains no exceptional frequency; if \(I\) contains an actual
reflection zero, continuity makes the multiplier fail to be bounded below,
so its range is dense and nonclosed.

## Machine authorities

- `black_hole_programme/phase3/axial_scalar_reflection_cell_half_v1/`
- `black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/`

## Does not establish

- absence or location of isolated reflection zeros outside the cell;
- pointwise outgoing population at every frequency of the pilot interval;
- explicit \(T_+\) entries or extension mixing amplitudes;
- a raw-frame numerical determinant enclosure for \({\cal O}\);
- a QNM Smith selector or Green-resolvent pole;
- a uniform inverse bound on the full positive axis;
- limiting absorption, full time-domain boundedness, decay, or quantum
  unitarity.
