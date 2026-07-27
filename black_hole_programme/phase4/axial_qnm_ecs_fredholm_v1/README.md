# Global ECS Fredholm realization of the axial QNM

This `REDUCED-MODE` package places the complete six-state axial Bach
resonance on a fixed, two-ended exterior-complex-scaled contour.  It proves
that

\[
\mathscr L_\theta(\omega):
H^1(\mathbb R;\mathbb C^6)\longrightarrow
L^2(\mathbb R;\mathbb C^6),
\qquad \theta=\frac{\pi}{4},
\]

is an analytic Fredholm pencil of index zero near the certified QNM.  The
horizon-ingoing and infinity-outgoing Jost spaces are respectively the
decaying spaces at the two ends of the contour.

The differentiated outgoing Jost germ grows only linearly relative to the
ordinary phase.  The same phase decays exponentially on the scaled ray, so
both the ordinary QNM and its generalized tangent belong to the single
fixed \(H^1\) domain.  Eliminating the two tail problems reduces the pencil
to invertible factors plus the certified \(3\times3\) connection matrix.
Its Smith valuations \((0,0,2)\) therefore give a nonzero rank-one
second-order pole of the full ECS radial inverse.

This is a global **complex-scaled radial** Fredholm theorem.  It is not an
uncut real-axis resolvent, a causal spacetime theorem, or a justification
of a retarded inverse-Laplace contour deformation.

Reproduce with:

```bash
python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.produce
python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.verify
python3 -m unittest -v \
  black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.test_ecs_fredholm
```
