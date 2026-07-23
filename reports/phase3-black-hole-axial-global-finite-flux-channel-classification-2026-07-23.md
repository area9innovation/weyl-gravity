# Phase 3 axial global finite-flux channel classifier

Date: 23 July 2026

## Disposition

The downstream classifier is implemented but **not activated**:

```text
MISSING_GLOBAL_CONNECTION
```

The exact axial endpoint wave-packet spaces and their Lee--Wald Grams are
available.  The validated, correlated horizon-to-infinity connection handoff
is not.  A formal infinity vector, a point-frequency scout, or the current
v5 runtime shortfall is not accepted as a substitute.

## Frozen crosswalk

The raw horizon initializer is ordered

```text
XH0a, XH0b, EH0, XHplus, EHout, XHminus
```

and its future-regular columns are exactly `[0,1,2]`.  The public order is

```text
XH0a, XH0b, XHplus, XHminus, EH0, EHout
```

where the same selector is `[0,1,4]`.  The classifier verifies the complete
permutation before touching a matrix.

The infinity order is

```text
XI0, XI1, XI2, XI3, EI0, EI2
```

with `Iminus=[0,1,4]` and `Iplus=[2,3,5]`.

## Implemented algebra

For a validated \(6\times3\) connection \(T\), the consumer forms

\[
C_-=P_-T,\qquad C_+=P_+T,
\]

and

\[
g_-=C_-^\dagger G_-C_-,
\qquad
g_+=C_+^\dagger G_+C_+.
\]

It computes exact image and kernel dimensions, realifies the Hermitian
pullbacks without sampled eigenvectors, and separates the trace-map kernel
from the physical radical:

\[
\dim\operatorname{rad}(\operatorname{im}C_\pm)
=\operatorname{nullity}(g_\pm)-\operatorname{nullity}(C_\pm),
\qquad
\dim P_\pm=\operatorname{rank}(g_\pm).
\]

The two additional horizon origins and the Einstein origin are tracked
separately through the physical quotient.

If a future-horizon Gram is supplied, the required conservation identity is

\[
G_{\mathcal H^+}+g_+-g_-=0.
\]

When \(C_-\) is invertible this defines a one-sided relation from
\(\mathscr I^-\) to
\(\mathcal H^+\oplus\mathscr I^+\).  It is never called a full scattering
matrix because the \(\mathcal H^-\) incoming block is absent.

## Synthetic verification

Exact tests cover:

- positive full-rank endpoint forms;
- indefinite full-rank endpoint forms;
- a populated radical distinct from the trace-map kernel;
- a two-dimensional off-diagonal hyperbolic plane;
- orientation-correct conservation and one-sided \(J\)-isometry;
- refusal of an incorrect horizon conservation sign.

Mutation tests delete an additional coordinate, apply the public selector to
the raw initializer, swap endpoint orientation, identify radial current with
null flux, flatten an exceptional wall, infer positivity from inertia, and
invent a global connection.  Every mutation is rejected.

## Required activation handoff

The missing
`axial_global_connection_matrix_v5/chunks/channel-handoff-v6.json` artifact
must provide correlated validated \(6\times3\)
connection enclosures on a finite rational cover, whole-cell ranks and
kernels, exceptional-cell dispositions, pulled-back realified Gram
certificates, the future-horizon outward Gram, current conservation, and
uniform multiplier bounds for the \(L^2\) wave-packet extension.

The exact constant-matrix classifier used by the synthetic tests is a
correctness oracle only.  It is not an interval-cell proof and cannot activate
the physical result by itself.

## Claim boundary

This scaffold establishes no global Einstein or additional channel, no
scattering matrix, and no CPT, stability, positivity, particle, or unitarity
result.

CLOSE-OUT: SHORTFALL — the fail-closed classifier and its exact synthetic
algebra are implemented, but the validated global connection handoff needed
for a Schwarzschild channel theorem does not yet exist

MISSING-DEP: phase3-axial-global-channel-handoff-v1 with complete whole-cell
connection, rank, Gram, conservation, exceptional-cell and multiplier
evidence
