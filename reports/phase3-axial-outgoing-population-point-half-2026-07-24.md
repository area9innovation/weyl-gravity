# Phase 3 axial outgoing-population point certificate

Date: 2026-07-24
Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
Lifecycle: `COEFFICIENT_COMPUTED`

## Established

At Schwarzschild \(M=1\), axial \(\ell=2\), and \(\omega=1/2\), two
independently replayed Arb transport geometries certify

\[
|A_{{\rm out},2}|>0.07331708402944288,\qquad
|A_{{\rm out},1}|>0.45928736814965915.
\]

The exact outgoing RW/RW/spin-one boundary filtration turns these scalar
bounds into a full-system theorem.  Successive projection to the spin-one,
carrier spin-two, and metric spin-two quotients proves

\[
\ker T_+(1/2)=0,\qquad T_+(1/2)\in GL(3,\mathbb C).
\]

Thus all three outgoing axial trace directions are populated by
future-horizon-regular global solutions at this frequency.

The exact Stokes identity then gives, without explicit assembly of \(T_+\),

\[
\mathcal O
=T_-^\dagger G_-T_- -H_{\mathcal H^+}
=T_+^\dagger G_+T_+.
\]

Since \(G_+\) is nondegenerate with inertia \((1,2,0)\),

\[
\det\mathcal O(1/2)\ne0,\qquad
\operatorname{inertia}\mathcal O(1/2)=(1,2,0)
\]

for \(\alpha_{\rm W}>0\).

## Receipts

- Scalar transport:
  `black_hole_programme/phase3/axial_scalar_reflection_point_half_v1/`
- Full outgoing-population bridge:
  `black_hole_programme/phase3/axial_outgoing_population_point_half_v1/`

The bridge receipt records producer replay, independent verification,
mutation tests, Python compilation, JSON-schema validation, and scoped
diff checks.

## Does not establish

- interval-wide or all-positive-frequency invertibility of \(T_+\);
- the explicit entries of \(T_+\) or extension mixing amplitudes;
- a raw-frame numerical lower bound for \(\det\mathcal O\);
- a QNM Smith selector or Green-resolvent pole;
- limiting absorption, time-domain boundedness, decay, or quantum unitarity.

The explicit outgoing transport and \(H_4\) continuation remain valuable as
independent amplitude and end-to-end audits, but they are no longer logical
prerequisites for the pointwise population theorem.
