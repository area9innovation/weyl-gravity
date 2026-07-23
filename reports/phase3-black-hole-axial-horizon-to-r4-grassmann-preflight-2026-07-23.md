# Phase-3 axial future-horizon transport preflight

## Result

This work item closes as an exact numerical-method shortfall:

\[
\boxed{\texttt{VALIDATED\_METHOD\_SHORTFALL\_NOT\_PHYSICS}.}
\]

For strict four-dimensional pure Weyl gravity on Schwarzschild with \(M=1\),
\(\ell=2\), and the shared frequency cell
\(M\omega\in[1/2,129/256]\), no validated parameter-correlated real
\(12\times6\) map from the future-horizon-regular space to \(r=4\) is emitted.

The work nevertheless isolates the failure sharply.  The future-horizon
Frobenius section, sheared axial system, public/raw basis crosswalk, and
standard-state conversion were rendered into exact Forge rails.  Three
full-column controls and one graph-reset control then refused before
promotion.

## Failed controls

1. A wide endpoint remainder, restricted to the narrow pilot cell, grows
   rapidly and traps at shell 11.
2. An exact order-three shared-generator initializer at \(\rho=2^{-22}\)
   also traps at shell 11.
3. Moving the start to \(\rho=2^{-40}\) reduces the uniform Frobenius tail to
   \[
   \frac{63569435}
   {2241348481419257701750001150984192},
   \]
   but the full-column enclosure still traps at shell 13.
4. A one-shell graph calculation with four-panel resets reconstructs the
   regular subspace, but one rank certificate remains false and its
   reconstructed width exceeds the direct control.

The third control is decisive for diagnosis: the growth is not caused by an
insufficiently small horizon start or by the analytic Frobenius tail.  A full
coefficient box forgets the invariant three-complex-dimensional regular
plane and admits complementary directions.

## Exact successor

The next method must propagate the regular plane and its amplitudes
separately.  In a complex Grassmann chart it should integrate

\[
Z'=A_{JI}+A_{JJ}Z-ZA_{II}-ZA_{IJ}Z,
\qquad
X'=(A_{II}+A_{IJ}Z)X,
\]

or apply the equivalent exact Möbius update

\[
M=\Phi_{II}+\Phi_{IJ}Z,\qquad
N=\Phi_{JI}+\Phi_{JJ}Z,\qquad
Z_+=NM^{-1}.
\]

The reviewed initial pivot is

\[
I=(P',Q,H_1),\qquad J=(P,Q',\rho F),
\]

with real row maps

\[
I_{\mathbb R}=(1,2,8,5,6,10),\qquad
J_{\mathbb R}=(0,3,9,4,7,11).
\]

Every right solve and chart reset must be certified, the shared generator
7315 must be retained, the \(6\times6\) amplitude must be tracked separately,
and failure to find a rank-six chart must refuse rather than widen.

## Interface and orientation

The future-regular raw selector `(0,1,2)` corresponds to public horizon
columns `(0,1,4)`, namely `XH0a`, `XH0b`, and `EH0`.

At \(r=4\), the standard real state order is

```text
Re(P), Re(Pprime), Re(Q), Re(Qprime), Re(H1), Re(F),
Im(P), Im(Pprime), Im(Q), Im(Qprime), Im(H1), Im(F).
```

For later global Stokes matching, the exterior orientation at the future
horizon is the negative of the increasing-\(r\) radial-current orientation.
This convention is recorded here only as an interface contract.

## Claim boundary

This shortfall does not establish a horizon-to-\(r=4\) map, a global
connection matrix, a populated endpoint channel, flux conservation,
scattering, stability, CPT positivity, or a physical ghost.  It also does not
indicate a singularity in the Bach flow.

The machine-readable evidence is in
`black_hole_programme/phase3/axial_horizon_to_r4_transport_preflight/`.

CLOSE-OUT: SHORTFALL — the horizon-to-r4 map is not emitted; the numerical-method boundary and exact successor are certified.

MISSING-DEP: PARAMETER_CORRELATED_VALIDATED_GRASSMANN_RICCATI_FLOW
