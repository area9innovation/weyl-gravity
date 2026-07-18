# One-loop Slavnov (Q_1) disposition

> **Active refinement.** This receipt remains authoritative for the exact
> rank-two local-counterterm ambiguity and the non-uniqueness of complete
> `Q1`. The later
> [`ANOMALY_INDUCED_NONLOCAL_GAMMA1`](anomaly-induced-nonlocal-gamma1.md)
> receipt supplies one conditional Paneitz/Riegert representative for the
> anomaly-induced Euclidean part of `Gamma1`. The later
> [`FLAT_TT_LOGARITHMIC_GAMMA1`](flat-tt-logarithmic-gamma1.md) receipt fixes
> the universal nonzero-momentum flat-TT logarithmic coefficient and scale
> response. The subsequent
> [`CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1`](curvature-squared-covariant-log-gamma1.md)
> receipt makes that term covariant through curvature order two and places the
> first operator-choice ambiguity at order three. The additive finite `C2/R2`
> normalization, cubic completion, global Green data, and complete `Q1` remain
> open.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The compensator-extended one-loop local Euclidean QME is restored, and the
coefficient-bearing local counterterm contribution is fixed:

\[
C_1^{\rm WZ}=-(4\pi)^{-2}
\left({199\over30}B_C-{87\over20}B_E\right),
\qquad
Q_1^{\rm WZ}=(C_1^{\rm WZ},\cdot).
\]

Because (C_1^{\rm WZ}) has antifield number zero, this Hamiltonian vector
field vanishes on fields and ghosts and acts through the Euler derivatives on
the cotangent rows. This is a certified contribution to (Q_1), not the
complete renormalized operator.

## Exact non-uniqueness witness

The extended local counterterm quotient has basis

\[
C(\widehat g)^2,\quad E_4(\widehat g),\quad
R(\widehat g)^2,\quad C(\widehat g)\widetilde C(\widehat g).
\]

On flat Euclidean momentum (p=(1,0,0,0)), use a traceless transverse
polarization (h_{11}=1,h_{22}=-1) and the conformal polarization
(h_{\mu\nu}=\delta_{\mu\nu}). Exact contraction of the linearized curvature
gives the response matrix

\[
\begin{pmatrix}
1&0&0&0\\
0&0&9&0
\end{pmatrix}.
\]

It has rank two. Thus finite (C^2) and (R^2) normalization choices change
the bulk Hamiltonian vector field independently. The Euler and Pontryagin
columns have zero compactly supported bulk Euler derivative; their boundary
and global content is not discarded.

Consequently, QME restoration alone does not determine a unique (Q_1).
The current repository also lacks the finite nonlocal part of
(\Gamma_1^{\rm ren}), a renormalized BV Laplacian or time-ordered product,
and finite (C^2/R^2) normalization conditions.

## Lifecycle

```text
local compensator QME       QME_RESTORED (one-loop, local Euclidean, tau-adic)
WZ Hamiltonian Q1 piece     CERTIFIED
complete renormalized Q1    NO_CERTIFIED_OPERATOR
extended contraction        NOT_SUPPLIED
residual transfer           FORBIDDEN
quantum D-Cartan defect      NOT_COMPUTABLE_FROM_CURRENT_INPUTS
Bridge 4                    NO_CERTIFIED_MAP
Bridge 5                    NO_CERTIFIED_MAP_BRIDGE_2_ABSENT
```

This is not a Lorentzian QME, state, positivity, particle, or residual theorem.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.one_loop_slavnov_q1_disposition --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_one_loop_slavnov_q1_disposition
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_one_loop_slavnov_q1_disposition.py
```
