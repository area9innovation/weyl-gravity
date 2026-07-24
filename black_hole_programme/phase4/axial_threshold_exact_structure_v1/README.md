# Axial threshold exact structure v1

This exact `LOCAL-ALGEBRAIC` / `REDUCED-MODE` package verifies the
zero-frequency spin-two and spin-one Regge--Wheeler solutions and the
threshold structure of the reduced projective extension cocycle.

It certifies:

- the horizon-normalized polynomial zero modes;
- explicit logarithmic reduction-of-order companions;
- decay of those companions at infinity and their logarithmic horizon
  singularity;
- the exact decomposition of the reduced cocycle through \(V_1-V_2\);
- an elementary spin-two primitive for the leading threshold source.

It does **not** certify the two-region Volterra matching needed for a
punctured zero-free interval of the outgoing Jost functions. The displayed
Jost coefficients, absorption probabilities, determinant asymptotic, and
\(b/a^2\) scaling remain targets, not theorem fields.

Run:

```bash
python3 -m black_hole_programme.phase4.axial_threshold_exact_structure_v1.produce
python3 -m black_hole_programme.phase4.axial_threshold_exact_structure_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_threshold_exact_structure_v1.test_threshold
```
