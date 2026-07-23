# Axial global-connection numerical preview: frozen diagnostic

## Status

`UNVALIDATED-NUMERIC`; this report is design input for the validated global
connection rail, not a theorem.

At \(M\omega=1/2\), direct inward propagation of six physical asymptotic
modes numerically collapsed.  Replacing it with the phase-normalized
correction factorization

\[
Y(r)=B(r)D(r)Z(r)
\]

preserved the full six-dimensional asymptotic frame:

- the bare \(B(32)\) has numerical rank six and condition number
  \(2.083\times10^8\);
- the transported correction \(Z\) has numerical rank six;
- the corrected frame \(BZ\) has numerical rank six.

This is a concrete design input for the validated rail: propagate the
normalized correction or invariant subspaces, not six exponentially
separated physical columns.

## Point-frequency channel preview

The three future-horizon-regular columns
\((XH0a,XH0b,EH0)\) give numerical rank-three maps into both endpoint
subspaces:

\[
C_-:\mathbb C^3\to\operatorname{span}(XI0,XI1,EI0),
\qquad
C_+:\mathbb C^3\to\operatorname{span}(XI2,XI3,EI2).
\]

After applying the \(R=32\) amplitude-normalization crosswalk, the two
pulled-back endpoint forms both have pointwise numerical inertia
\((1,2,0)\).  Thus this preview suggests that horizon-regular data populate
both positive and negative endpoint directions.  It does **not** establish a
physical negative-flux scattering channel.

## Conservation failure and stop

The declared orientation identity

\[
G_{\mathcal H^+}+C_+^\dagger G_+C_+
-C_-^\dagger G_-C_-=0
\]

does not close: its relative max residual is approximately \(9.994\times
10^{-1}\).  Reversing only the candidate horizon sign reduces the residual to
approximately \(1.294\times10^{-3}\), but does not make it zero or certified.

The preview therefore localizes the next required audit to the
future-horizon outward/radial orientation and endpoint amplitude crosswalk.
No five-frequency scan is warranted until that typing is fixed.

There is also no \(\mathcal H^-\) basis, so this is not a two-ended scattering
map.

## Reproduction and checks

The point computation uses 30-decimal-digit `mpmath` arithmetic, the frozen
exact flow and exact-coefficient RK4 Richardson transport.  Its compact
machine-readable record is `pilot-diagnostic.json`.

Fast boundary checks:

```bash
python3 -m \
  black_hole_programme.phase3.axial_global_connection_numeric_preview.verify
python3 -m unittest \
  black_hole_programme.phase3.axial_global_connection_numeric_preview.test_preview
```

The expensive point calculation is implemented by `preview.py`; its output
is deliberately not accepted as certificate evidence.

## Does not establish

- a validated global connection or conservation theorem;
- a two-ended scattering matrix;
- a physical scattering channel or physical ghost;
- a uniform-in-frequency result;
- pole exclusion, stability, CPT positivity, unitarity, or a PDE scattering
  theorem.
