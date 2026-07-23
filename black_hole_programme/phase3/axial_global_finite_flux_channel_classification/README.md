# Axial global finite-flux channel classification

This package is the fail-closed Phase-3 join between the validated
horizon-to-infinity connection and the exact null-endpoint wave-packet flux
forms.

Its frozen pilot scope is:

- strict linearized four-dimensional pure \(C^2\) Weyl gravity;
- Schwarzschild exterior with \(M=1\);
- axial \(\ell=2\);
- \(M\omega\in[1/2,129/256]\), subdivided into 16 exact contiguous cells;
- the future-horizon-regular three-complex-dimensional domain;
- the one-sided relation
  \(\mathscr I^-\to\mathcal H^+\oplus\mathscr I^+\).

The missing \(\mathcal H^-\) incoming block is explicit.  The package never
calls the available one-sided relation a full two-ended scattering matrix.

## Evidence flow

1. `produce.py` and `certificate.json` record the pre-activation contract and
   refuse every global-channel promotion while the typed handoff is absent.
2. The upstream handoff verifier independently replays the connection,
   endpoint pullbacks, action-current identity, rank/inertia witnesses and
   uniform multiplier bounds.
3. `activate.py` imports that handoff, independently repeats the affine
   pullback/rank/inertia and multiplier algebra, and writes
   `activated-certificate.json`.
4. `verify_activated.py` does not import the activation producer.  It checks
   that every activated statement is a scope-preserving logical consequence
   of the independently verified handoff.

The validated radial solvers retain a shared degree-two frequency model.
`taylor2_adapter.py` supplies the explicit evidence boundary into the affine
handoff schema: it absorbs \(A_2e^2\), with \(e^2\in[0,1]\), into an outward
remainder and recovers the complex block from the realified solve by an
outer affine hull.  It does not discard the quadratic term or replace the
shared frequency by independent interval generators.

The activated certificate classifies, cell by cell:

- populated dimensions and physical quotient dimensions at
  \(\mathscr I^\pm\);
- pulled-back flux inertia and horizon outward inertia;
- Einstein/additional origin restrictions and their mixed block;
- exact current orientation
  \(G_{\mathcal H^+}+g_+-g_-=0\);
- whole-cell inverse and multiplier bounds;
- the induced one-sided \(J\)-isometry;
- every unresolved cell, without continuity across it.

## Commands

Before the handoff lands, activation and its independent verifier must return
the typed `NOT_ACTIVATED` disposition.

```bash
python3 -m black_hole_programme.phase3.axial_global_finite_flux_channel_classification.produce --check
python3 -m black_hole_programme.phase3.axial_global_finite_flux_channel_classification.verify
python3 -m black_hole_programme.phase3.axial_global_finite_flux_channel_classification.activate
python3 -m black_hole_programme.phase3.axial_global_finite_flux_channel_classification.verify_activated
python3 -m unittest black_hole_programme.phase3.axial_global_finite_flux_channel_classification.tests.test_classifier
python3 -m unittest black_hole_programme.phase3.axial_global_finite_flux_channel_classification.tests.test_taylor2_adapter
python3 -m black_hole_programme.phase3.axial_global_finite_flux_channel_classification.mutations
```

## Claim boundary

Even a fully certified pilot does not establish the remainder of
\([129/256,3/4]\), polar parity, other angular momenta, upper-half-plane pole
exclusion, nonlinear stability, a positive CPT metric, a Hadamard state,
particles, or quantum unitarity.  A negative endpoint or populated flux
direction is a classical indefinite channel, not by itself a quantum ghost.
