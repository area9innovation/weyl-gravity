# Phase 3 axial endpoint bases: exact reconstruction obstruction

Result token:
`BH_PHASE3_AXIAL_ENDPOINT_METRIC_BASIS_OBSTRUCTED_BY_OMITTED_VPHI_ROW`.

## Result

The corrected Phase-2 axial Ricci carrier supplies an exact, complete
four-dimensional formal endpoint basis on Schwarzschild.  At infinity its
branches have

\[
(\mu,\sigma)=(0,0),(0,-1),
(-2i\omega,-4i\omega),(-2i\omega,-4i\omega-1),
\]

in the `M=1` convention.  At the horizon the residue exponents are

\[
0,0,-4i\omega,-2-4i\omega.
\]

The repeated zero exponent has geometric multiplicity two.  The singular
pair differs by the integer two, but the exact order-two cokernel obstruction
vanishes.  Hence all four carrier branches are log-free for real nonzero
frequency.  The frozen pilot interval
`M omega in [1/2,3/4]` contains no carrier exceptional point.

The corresponding complete **metric** endpoint basis cannot yet be built
from the imported reconstruction operator.  The generic-ell 3x3 system was
derived from

\[
\delta R_{x\phi}=c,
\qquad
\delta R_{r\phi}=q,
\]

but does not impose the required third equation
`delta R_{v phi}=p`.  Its advertised generalized polynomial solution at
`ell=2`,

\[
H_1=1,
\qquad
H_0=-i\omega r+2+\frac2r,
\]

has the exact omitted-row residual

\[
\frac{\delta R_{v\phi}}{S_2}
=\frac{3i(\omega-2i)}{r^2}.
\]

This is nonzero for every real frequency in the pilot interval.  The mode is
therefore a solution of the two-row subsystem, not a basis vector of the
complete Ricci reconstruction problem.

## Interpretation

This is a fail-closed endpoint-basis result, not a failure of the carrier
equation.  The corrected Phase-2 `X0` calculation retains the differentiated
forcing

\[
\frac{2r(c'-Q)}{r-2M}.
\]

That repairs the earlier differentiated-source defect, but its verifier checks
`row_x`, `H1'=F` and `row_f`; the middle equation is definitional, not the
omitted `v phi` Ricci row.  The Phase-2 `X0` lift therefore now
**requires re-audit** against `delta Ric_{v phi}=P`.  The polynomial control
above does not itself disprove `X0`.

The new obstruction says that lifting **all four** carrier directions requires
the full three-row differential-algebraic reconstruction system and its
constraint-propagation identity.  Until that object is constructed—and `X0`
is rechecked within it—the dimension, labels and endpoint jets of the complete
Bach metric basis are not defined.

The successor-ready equations, the algebraic constraint and the minimal
six-vector repair contract are frozen in
`black_hole_programme/phase3/axial_endpoint_bases/repair-interface.json`.

## Scope

Established:

- exact carrier endpoint multiplicities and the compatible horizon
  resonance;
- exact l=2 omitted Ricci row from a direct delta-Gamma derivation;
- exact nonzero residual of the spurious polynomial mode;
- no excluded real point in the frozen pilot interval.

Not established:

- a complete reconstructed metric basis;
- horizon-to-infinity matching;
- a finite-flux quotient or scattering channel;
- any pole, stability, CPT, particle or quantum statement.

## Verification

```text
PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_endpoint_bases/produce.py --check
PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_endpoint_bases/verify.py
python3 -m unittest black_hole_programme.phase3.axial_endpoint_bases.tests.test_endpoint_bases
python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-axial-endpoint-bases-fragment-v1.json
```

The verifier recomputes the omitted row through the independent
`LinearizedBach` implementation.  Mutation tests change the polynomial lift,
attempt an invalid metric-basis promotion and exercise the resonant carrier
branch.

CLOSE-OUT: OBSTRUCTED — the complete four-dimensional Ricci-carrier endpoint basis is exact and log-free on the pilot interval, but a complete reconstructed metric endpoint basis is not defined because the inherited subsystem omits the independent `delta Ric_{v phi}=P` compatibility row. The Phase-2 corrected sourced `X0` lift therefore requires re-audit before any global connection or flux claim.

EVIDENCE: `black_hole_programme/phase3/axial_endpoint_bases/receipt.json`
