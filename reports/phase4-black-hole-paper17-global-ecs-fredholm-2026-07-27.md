# Paper 17 global ECS Fredholm completion

Date: 2026-07-27

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete axial six-state Bach pencil now has a fixed-domain global
radial realization on a two-ended \(\theta=\pi/4\)
exterior-complex-scaled contour:

\[
\mathscr L_\theta(\omega):
H^1(\mathbb R;\mathbb C^6)\longrightarrow
L^2(\mathbb R;\mathbb C^6).
\]

On the certified QNM neighborhood:

- the horizon-ingoing space is the three-dimensional forward-unstable
  space at the left end and decays as the contour coordinate tends to
  \(-\infty\);
- the infinity-outgoing space is the three-dimensional forward-stable
  space at the right end;
- the asymptotic index is \(3+3-6=0\);
- the coefficient remainder is a compact \(H^1\to L^2\) perturbation;
- the pencil is holomorphic Fredholm of index zero on a fixed domain.

The differentiated infinity Jost tangent is bounded by a linear polynomial
times the selected exponentially decaying phase.  Hence it and its
derivative are square integrable:

\[
\int_0^\infty(1+t)^2e^{-2\rho t}\,dt
=\frac{2\rho^2+2\rho+1}{4\rho^3}<\infty.
\]

Thus the ordinary Einstein QNM and its generalized tangent lie in the same
fixed Sobolev domain.

Analytic elimination of the two tail problems reduces the pencil to
invertible factors plus the certified QNM connection matrix.  Its Smith
valuations \((0,0,2)\) give

\[
\mathscr L_\theta(\omega)^{-1}
=\frac{\Pi_{-2}^\theta}{(\omega-\omega_n)^2}
+\frac{\Pi_{-1}^\theta}{\omega-\omega_n}+O(1),
\qquad
\operatorname{rank}\Pi_{-2}^\theta=1.
\]

Compactly supported source/observation matrix elements agree with the
previously certified exterior outgoing cut-off inverse.

## Claim boundary

This closes the fixed-domain global **complex-scaled radial** Fredholm gate.
It does not establish:

- an uncut real-axis outgoing inverse on the standard asymptotically flat
  phase space;
- a Lorentzian-causal spacetime resolvent;
- bounded physical reconstruction on a causal real-axis domain;
- a physical inverse-Laplace contour deformation;
- threshold, branch-cut, high-frequency, or non-pole contour control;
- a complete QNM expansion or global retarded ringdown.

The remaining problem is therefore causal rather than local Fredholm:
construct a real-axis weighted realization compatible with physical
reconstruction and justify the retarded contour deformation.

## Evidence

Primary certificate:

`black_hole_programme/phase4/axial_qnm_ecs_fredholm_v1/certificate.json`

Commands:

```text
python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.produce
python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.verify
python3 -m unittest -v \
  black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.test_ecs_fredholm
python3 paper/verify_17_pure_weyl_extension_claim_map.py
python3 -m unittest -v paper.test_17_pure_weyl_extension_claim_map
python3 paper/verify_16_lorentzian_endpoint_nonselection_claim_map.py
python3 -m unittest -v paper.test_16_lorentzian_endpoint_nonselection_claim_map
```

Outcomes:

- ECS package: producer PASS, independent verifier PASS, 7 mutation tests
  PASS;
- Paper 17: claim-map verifier PASS, 16 tests PASS;
- Paper 16: claim-map verifier PASS, 23 tests PASS;
- Papers 00, 16, and 17 compile in two LaTeX passes with no undefined
  references; Paper 16 retains one pre-existing overfull-box warning;
- Paper 98 rebuilds successfully with Pandoc/XeLaTeX.

CLOSE-OUT: DONE — fixed-domain global ECS radial Fredholm pole certified;
causal real-axis and retarded-contour promotion remain open.
