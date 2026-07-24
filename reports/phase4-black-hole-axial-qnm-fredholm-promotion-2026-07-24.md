# Phase 4 axial QNM Fredholm promotion A

The certified connection-level axial QNM exceptional point has been promoted
to an exact second-order pole theorem for a declared finite-interval radial
boundary-value inverse.

## Result

At the enclosed simple spin-two Schwarzschild QNM, the phase-factored
six-state operator

\[
\mathscr L(\omega)Y=
\left(
Y'-\mathbb A(r,\omega)Y,\,
B_H(\omega)Y(r_H),\,
B_I(\omega)Y(r_I)
\right)
\]

is an analytic Fredholm pencil of index zero from
\(H^1([r_H,r_I];\mathbb C^6)\) to
\(L^2([r_H,r_I];\mathbb C^6)\oplus\mathbb C^3\oplus\mathbb C^3\).
Here \(r_H,r_I\) are fixed ordinary radii in the certified continuation
domains, and the boundary maps annihilate the selected horizon-regular and
infinity-outgoing planes.

The initial-value map

\[
Y\mapsto(Y'-\mathbb A Y,Y(r_H))
\]

is an analytic isomorphism.  Variation of constants and finite-dimensional
boundary elimination reduce \(\mathscr L\) exactly to the identity on
\(L^2\) plus the effective boundary matrix

\[
M(\omega)=B_I(\omega)\Phi(r_I,r_H;\omega)H(\omega).
\]

The latter equals the certified factor-adapted QNM connection matrix up to
analytic invertible endpoint units.  Importing its certified Smith
valuations \((0,0,2)\) gives

\[
\mathscr L(\omega)^{-1}
=
\frac{\Pi_{-2}}{(\omega-\omega_n)^2}
+\frac{\Pi_{-1}}{\omega-\omega_n}
+O(1),
\qquad
\operatorname{rank}\Pi_{-2}=1.
\]

The leading range is the source-Einstein root line.  The exact axial
reconstruction identifies it with the nonzero metric kernel state
\((H_1,H_1')\), so the leading coefficient is not annihilated by metric
reconstruction.

## Scope

This closes Fredholm promotion A only.  The result is a finite-interval
`REDUCED-MODE` radial Green-operator theorem.  It does **not** establish:

- a causal exterior spacetime resolvent;
- a Laplace-contour deformation;
- control of the inverse transform away from the pole;
- a \(t e^{i\omega_n t}\) term for physical initial data or sources;
- time-domain stability, completeness, particle or quantum claims.

Those requirements define Fredholm promotion B.

## Verification

```text
python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.produce
python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.test_fredholm
```

The verifier independently solves a different exact block boundary matrix,
recovers its \(z^{-2}\) coefficient and verifies that its rank is one.
Mutation tests reject Smith-rank drift, causal/time-domain promotion,
physical-reconstruction deletion and imported-certificate hash drift.

EVIDENCE: `black_hole_programme/phase4/axial_qnm_fredholm_promotion_v1/certificate.json`

CLOSE-OUT: DONE — the finite-interval radial analytic Fredholm inverse has a
nonzero rank-one second-order pole at the certified axial QNM; retarded
time-domain promotion remains separate.
