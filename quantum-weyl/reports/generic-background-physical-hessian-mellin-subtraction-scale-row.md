# Physical Hessian Mellin-subtraction scale row

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The equal-box physical triangle/bubble fixture now has a reproducible global
minimal-subtraction extension. Each of the six labelled triangle orderings is
split into its three largest-barycentric sectors. In sector (i),

\[
 \alpha_i=1-r,\qquad \alpha_j=rt,\qquad \alpha_k=r(1-t),
\]

with the exact piecewise upper bound implied by
(alpha_i\geq\alpha_j,\alpha_k). The three sectors cover the simplex up to
measure-zero ties. Each bubble is split into the left and right half-intervals.
All eighteen labelled triangle corners and six bubble endpoints use the same
Mellin parameter (s) and scale ratio (z=mu^2/Q^2).

The logarithmic model is

\[
 \frac{z^s}{s}=\frac1s+\log z+O(s).
\]

Minimal subtraction removes only the (1/s) pole. The exact residues are

\[
 \operatorname{Res}_{H_1^3}=-\frac{1975}{72},\qquad
 \operatorname{Res}_{H_1H_2}=\frac{2704}{27},
\]

and therefore

\[
 \boxed{
 \frac{\partial\Gamma_{\rm fixture}^{\rm MS}}
      {\partial\log\mu^2}
 =\frac1{(4\pi)^2}\frac{15707}{216}}
\]

at the declared equal-box TT fixture. Thus (15707/216) is not merely a
common-cutoff diagnostic: it is the exact scale row of this fixed Mellin
extension. A (mu)-independent finite local subtraction can shift the finite
constant but cannot change this coefficient.

This still does not provide the generic covariant Volterra lift. In
particular, it does not assemble the generic mixed rows, dispose the `M14`
relative class, or determine a repository form factor.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_mellin_subtraction_scale_row --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_mellin_subtraction_scale_row
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_mellin_subtraction_scale_row
```

## Verification receipt

Recorded on 2026-07-19:

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_mellin_subtraction_scale_row --check` | 2.10 s | PASS |
| 1 | `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_mellin_subtraction_scale_row` | 0.25 s | PASS |
| 1 | `PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_mellin_subtraction_scale_row` | 1.97 s | PASS, 4 tests |
| 2 | `PYTHONPATH=quantum-weyl python3 -m verify_active_frontier` | 0.55 s | PASS |
| 2 | `PYTHONPATH=quantum-weyl python3 -m atlas.verify_quantum_atlas_fragment` | 2.70 s | PASS |
| 2 | `python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py` | 0.14 s | PASS |

Tier 3 was not run because no theorem-freeze or lifecycle promotion and no
shared core-algebra change occurred.
