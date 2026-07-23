# Axial global-connection numerical preview

This directory is an isolated numerical reconnaissance rail for the
Schwarzschild axial \(\ell=2\) Bach connection problem.

It imports the frozen exact six-state flow, the certified horizon and
infinity normal forms, the exact finite-radius Lee–Wald current, and the exact
endpoint flux Grams.  It evaluates the five point frequencies

\[
M\omega\in\left\{\frac12,\frac9{16},\frac58,\frac{11}{16},\frac34\right\}.
\]

The integration uses arbitrary-precision arithmetic and exact-coefficient
RK4 Richardson extrapolation.  The horizon series and infinity series are
truncated, and neither their errors nor the radial transport are enclosed by
intervals.  Consequently every output is typed:

```text
UNVALIDATED-NUMERIC
does_not_establish
```

The frozen one-frequency result is `pilot-diagnostic.json`; its interpretation
and stop condition are in `report.md`.  Run the exploratory five-frequency
driver only after the horizon orientation crosswalk is repaired:

```bash
python3 -m black_hole_programme.phase3.axial_global_connection_numeric_preview.preview
```

Run fast sanity tests:

```bash
python3 -m unittest \
  black_hole_programme.phase3.axial_global_connection_numeric_preview.test_preview
```

The code computes the \(6\times3\) coefficient map from the three
future-horizon-regular columns to the complete infinity basis, its
\(\mathscr I^-\) and \(\mathscr I^+\) blocks, pulled-back endpoint Grams, the
outward future-horizon Gram obtained independently from the exact radial
current at \(r=4\), and the diagnostic conservation residual

\[
G_{\mathcal H^+}+C_+^\dagger G_+C_+
-C_-^\dagger G_-C_-=0.
\]

The frozen pilot intentionally stopped because the declared conservation
orientation did not close.  There is also no past-horizon basis in this
calculation.  It is therefore not a
two-ended scattering map, even if the numerical conservation residual is
small.
