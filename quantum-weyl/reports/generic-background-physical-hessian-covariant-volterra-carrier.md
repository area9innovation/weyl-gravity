# Generic physical-Hessian covariant Volterra carrier

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The physical cubic trace-log row now has one generic covariant parameter
carrier.  Write the monic principal fourth-order operator as

\[
 H_0=L^2,
 \qquad
 G_0=H_0^{-1}=\int_0^\infty u e^{-uL}\,du,
\]

where (L=-\nabla^2) acts on traceless symmetric tensors.  Polarization in
three independently labelled external curvatures gives

\[
 \sum_{\sigma\in S_3}\frac16
 \operatorname{Tr}(G_0H_{1,\sigma_1}G_0H_{1,\sigma_2}G_0H_{1,\sigma_3})
 -\sum_{i=1}^3\frac12
 \operatorname{Tr}(G_0H_{1,i}G_0H_{2,jk}).
\]

Thus the decorated carrier has six ordered triangle cells and three local
contact cells.  The latter retain the (H_2) insertion as a contact replacing
the labelled pair ((H_{1,j},H_{1,k})); they are not inserted into the
interior triangle numerator.

For a triangle corner the proper times are

\[
 (u_1,u_2,u_3)=T(1-r,rt,r(1-t)).
\]

The exact Jacobian is (T^2r), and the three squared propagators give the
measure

\[
 T^5r^3(1-r)t(1-t).
\]

For a mixed contact cell,

\[
 (u_1,u_2)=T(x,1-x),
\]

with Jacobian (T) and squared-propagator measure

\[
 T^3x(1-x).
\]

Every one of the 18 resolved triangle boundary charts and six resolved
contact endpoints is extended with the same Mellin parameter (s) and scale
ratio (z=\mu^2/Q^2).  Minimal subtraction is therefore a single operation
on the decorated carrier.  The earlier rational equal-box prescription is
its exact evaluation pullback, rather than an unrelated cutoff comparison.

The certificate independently checks the cell enumeration, both Jacobians,
the squared-propagator weights, exact cyclicity on a noncommuting rational
matrix fixture, and

\[
 \frac{z^s}{s}=\frac1s+\log z+O(s).
\]

This closes the carrier problem only.  The generic (H_1H_2) tensor kernels
have not been evaluated on it, the renormalized mixed five-carrier rows have
not been assembled, and `M14` remains open.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_covariant_volterra_carrier --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_covariant_volterra_carrier
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_covariant_volterra_carrier
```

## Verification receipt

Recorded on 2026-07-19. The Python rails below were run concurrently; the
reported values are individual command wall times.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_covariant_volterra_carrier --check` | 1.71 s | PASS |
| 1 | `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_covariant_volterra_carrier` | 2.54 s | PASS |
| 1 | `PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_covariant_volterra_carrier` | 1.56 s | PASS, 5 tests |
| 2 | `PYTHONPATH=quantum-weyl python3 -m verify_active_frontier` | 2.14 s | PASS |
| 2 | `PYTHONPATH=quantum-weyl python3 -m atlas.verify_quantum_atlas_fragment` | 2.39 s | PASS |
| 2 | `python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py` | 0.25 s | PASS |
| 2 | `pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex` (two passes from `paper/`) | 7.81 s | PASS |
| 2 | `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/12-pure-weyl-one-loop-bv-anomaly-computational-supplement.tex` (three passes from the repository root) | 3.36 s | PASS |

The LaTeX logs contain no warning, undefined-reference, overfull, underfull,
or error lines. An initial supplement invocation from `paper/` was rejected
because its generated-table include is repository-root relative; it was not
counted as a pass. Tier 3 was not run because this is a scoped carrier
certificate, not a theorem freeze or lifecycle promotion.
