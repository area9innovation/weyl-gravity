# Paper 17 complete massive Jost crosswalk

Date: 27 July 2026

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete coupled axial massive-spin-two \(Q,Z\) system admits
parameter-analytic two-dimensional Jost planes at both Schwarzschild
endpoints near the certified \(\ell=2\) QNM:

- a matrix Frobenius plane for the future-horizon-ingoing exponent;
- a two-stage scalar/matrix Volterra plane for the infinity-outgoing
  exponent on the certified exterior-complex-scaled ray.

The endpoint uniqueness statements exclude the opposite Jost sign.  The
spin-one channel is a certified local unit, and its same-sign \(O(m)\)
mixing drops out of the first derivative of the spin-two Schur divisor.
Consequently,

\[
b_{\rm B}(\omega_n)
=\frac{3i\omega_n}{2}\partial_m a_{\rm phys}(\omega_n,0),
\]

and the complete massive axial QNM branch has nonzero signed
squared-mass velocity

\[
\omega_n'(0)=\frac{2i}{3\omega_n}\kappa_n\ne0.
\]

Propagating the certified selector and root enclosures gives the
conservative outer box

\[
\operatorname{Re}\omega_n'(0)\in[0.087,0.251],
\qquad
\operatorname{Im}\omega_n'(0)\in[-0.054,0.135].
\]

## Why the earlier leading-phase argument was insufficient

The superseded reports
`phase4-black-hole-paper17-jost-mass-slope-2026-07-25.md` and
`phase4-black-hole-paper17-complete-massive-crosswalk-2026-07-27.md`
correctly identified the endpoint linear term but did not prove that a
homogeneous difference contained no opposite-Jost component.  The present
Frobenius/Volterra construction supplies precisely that uniqueness
statement.  Historical records are retained; this report is their
successor.

## Evidence

Machine-readable certificate:

`black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/certificate.json`

Independent verifier and mutation tests:

```bash
python3 black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/produce.py
python3 black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/verify.py
python3 -m unittest \
  black_hole_programme.phase4.axial_massive_jost_crosswalk_v1.test_jost_crosswalk
```

Paper claim-map checks:

```bash
python3 paper/generate_17_pure_weyl_extension_claim_map.py --check
python3 paper/verify_17_pure_weyl_extension_claim_map.py
python3 -m unittest paper.test_17_pure_weyl_extension_claim_map
python3 paper/generate_16_lorentzian_endpoint_nonselection_claim_map.py --check
python3 paper/verify_16_lorentzian_endpoint_nonselection_claim_map.py
python3 -m unittest paper.test_16_lorentzian_endpoint_nonselection_claim_map
```

## Verification receipt

- Tier 0: Python compilation, generated-map freshness, JSON/schema checks,
  `git diff --check`, and two-pass PDF builds for Papers 00, 16, and 17
  passed. Paper 98 was rebuilt with its recorded Pandoc/XeLaTeX command.
- Tier 1: the new producer/verifier and four mutation tests passed.
- Tier 2: the complete first-jet, inverse-tortoise/ECS, selector,
  spin-one-unit, and new Jost-crosswalk verifiers passed. The selector must
  be invoked as a module because it uses package-relative imports.
- Broader release rail: all 53 paper tests passed. Phase-4 discovery ran
  86 substantive tests green and reported one import-context collection
  error; that module was rerun with its correct fully qualified path, where
  all 3 tests passed.

The initial direct-file invocation of the selector verifier was rejected
with a package-relative-import error and is not counted as a pass; the
correct module invocation passed.

## Claim boundary

This result does not establish:

- a global weighted exterior Fredholm domain;
- a retarded inverse-Laplace contour deformation;
- a complete QNM expansion or late-time theorem;
- standard asymptotic falloff for the constant generalized metric
  component;
- excitation by a real causal or specified astrophysical source.

CLOSE-OUT: DONE — endpoint-analytic complete massive axial Jost crosswalk
and nonzero signed squared-mass QNM velocity; global causal realization
remains open.
