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

## Corrected orientation and stop

The imported finite-radius current is \(F^r/(\pi\alpha_{\rm W})\).  The
Hermitian flux convention is \(iF^r/(\pi\alpha_{\rm W})\), and the future
horizon is the inner boundary of the exterior.  Its outward Gram is therefore

\[
G_{\mathcal H^+}=-Y^\dagger(i\widehat J)Y.
\]

An earlier diagnostic applied the factor of \(i\) with the wrong sign before
the inner-boundary reversal.  Correcting that typing makes the declared
orientation identity

\[
G_{\mathcal H^+}+C_+^\dagger G_+C_+
-C_-^\dagger G_-C_-=0
\]

numerically close: its relative max residual is approximately
\(1.294\times10^{-3}\).  The control with the horizon sign reversed is of
order one.  The remaining small residual does not establish conservation:
the horizon and infinity series are truncated and the radial transports are
not enclosed.

At 40 working digits, halving the horizon radial macro-step and moving the
infinity normalization radius from \(64\) to \(128\) reduces the recorded
radial embedded-step defect from \(6.16\times10^{-3}\) to
\(1.42\times10^{-4}\), but changes the relative conservation residual only
from \(1.294\times10^{-3}\) to \(1.248\times10^{-3}\).  The dominant
unvalidated error is therefore not the ordinary radial step size; it remains
in the formal horizon/endpoint truncation or its amplitude crosswalk.

The preview therefore supplies the orientation and amplitude conventions to
the validated rail, but no five-frequency scan is warranted until the exact
transport closes the same identity.

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
