# Paper 17 causal Laplace-to-resonance bridge

Date: 2026-07-27

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Result

The certified axial \(\ell=2\) double pole is now connected to an actual
causal response.  On the gauge-invariant transverse-traceless parent sector,
let

\[
\mathcal E_m=\mathcal E+m\mathcal A,
\qquad m=\mu^2,
\]

and let \(G_m^{\rm ret}\) be its retarded Green operator on the Schwarzschild
domain of outer communications.  Normal hyperbolicity and Duhamel
differentiation give

\[
\left.\partial_mG_m^{\rm ret}\right|_{m=0}
=-G_0^{\rm ret}\mathcal A G_0^{\rm ret}.
\]

Consequently the pure-Weyl metric response on this reduced sector is

\[
G_{hh,{\rm W}}^{\rm ret}
=-\frac{1}{4\alpha_{\rm W}}
 \left.\partial_mG_m^{\rm ret}\right|_{m=0}
=\frac{1}{4\alpha_{\rm W}}
 G_0^{\rm ret}\mathcal A G_0^{\rm ret}.
\]

The sequential composition remains retarded.

With the paper's \(e^{+i\omega t}\) convention, the forward Laplace
transform is initially defined below the energy-growth line.  In that lower
half-plane it equals the ordinary resolvent, and its square-integrable
endpoint solutions are exactly future-horizon ingoing and
infinity-outgoing.  Compact source and observation cutoffs therefore give
the same transfer as the physical outgoing radial problem.

The complete Jost construction and fixed-domain exterior-complex-scaled
pencil uniquely continue this transfer into the certified QNM disk.  Its
principal Laurent coefficient is

\[
G_{-2}
=-\frac{\omega_n'(0)}{4\alpha_{\rm W}}P_n,
\qquad
\omega_n'(0)=\frac{2i}{3\omega_n}\kappa_n\ne0.
\]

Hence the nonzero rank-one second-order pole is a resonance pole of the
meromorphic continuation of a genuinely retarded, mode-reduced transfer
operator.

## Claim boundary

This closes the causal-origin question only at `REDUCED-MODE` scope.  It
does not establish:

- a full off-shell metric/BV retarded propagator;
- excitation by a real, temporally compact physical source;
- bounded Bondi reconstruction of the complete causal generalized state;
- a global inverse-Laplace contour deformation through the QNM disk;
- threshold, branch-cut, high-frequency, or non-pole remainder control;
- a complete retarded QNM expansion or global
  \(t e^{i\omega_n t}\) ringdown theorem;
- time-domain stability or a quantum statement.

The next gate is the contour shift from the lower-half-plane Laplace line,
with threshold and high-frequency estimates and bounded asymptotic
reconstruction.

## Evidence

Primary certificate:

`black_hole_programme/phase4/axial_qnm_causal_laplace_bridge_v1/certificate.json`

Commands:

```text
python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.produce
python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.verify
python3 -m unittest -v \
  black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.test_causal_bridge
python3 paper/verify_17_pure_weyl_extension_claim_map.py
python3 -m unittest -v paper.test_17_pure_weyl_extension_claim_map
python3 paper/verify_16_lorentzian_endpoint_nonselection_claim_map.py
python3 -m unittest -v paper.test_16_lorentzian_endpoint_nonselection_claim_map
```

Outcomes:

- causal bridge package: producer PASS, verifier PASS, 7 mutation tests
  PASS;
- Paper 17: claim-map verifier PASS, 17 tests PASS;
- Paper 16: claim-map verifier PASS, 23 tests PASS;
- Papers 00, 16, and 17 compile in two LaTeX passes;
- Paper 98 rebuilds successfully.

CLOSE-OUT: DONE — causal retarded origin of the mode-reduced meromorphic
double pole certified; inverse-Laplace contour deformation and full physical
waveform promotion remain open.
