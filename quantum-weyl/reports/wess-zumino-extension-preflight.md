# Wess–Zumino compensator extension preflight

The strict pure-Weyl one-loop breaking is nontrivial, but after adjoining a
shifting scalar

\[
Q\tau=\mathcal L_\xi\tau+\omega,
\qquad \widehat g=e^{-2\tau}g,
\]

the dressed metric has no Weyl variation. At every finite jet order,

\[
Q_W\tau_I=\omega_I,
\qquad Q_W\omega_I=0,
\qquad \{Q_W,h\}=N_{\tau,\omega}.
\]

This doublet contraction supplies explicit local primitives for the two even
classes:

\[
B_C=\int\sqrt g\,\tau C^2,
\]

\[
B_E=\int\sqrt g\left[
\tau E_4+4G^{\mu\nu}\partial_\mu\tau\partial_\nu\tau
-4(\Box\tau)(\partial\tau)^2+2(\partial\tau)^4
\right].
\]

Therefore

\[
Q_W\left({199\over30}B_C-{87\over20}B_E\right)
= {199\over30}[\omega C^2]-{87\over20}[\omega E_4]
\quad\bmod d_h.
\]

Within the declared AFN0 two-class sector, the strict boundary rank changes
from zero to two and the quotient dimension from two to zero. The one-loop
breaking is exact and removable there.

The machine replay uses the graded carrier `(B_C,B_E,A_C,A_E)`. Its exact
matrices satisfy `Q^2=0`, `Qh+hQ=I_4`, and `Qh != hQ`; the latter check guards
against accidentally forgetting the grading. It also verifies the dressed
metric weight cancellation `-2+2=0` independently of the displayed formula.

This is not yet a restored full BV QME. The repository still lacks the full
Diff×Weyl cotangent lift containing the `tau_star` row and an exhaustive
recomputation of extended `H04` and `H14`. Residual transfer remains
forbidden until those data pass independently.

Lifecycle:

```text
strict pure-Weyl BV QME          OBSTRUCTED_STRICT_FIELD_CONTENT
extended AFN0 breaking           EXACT_REMOVABLE
full compensator BV QME          NOT_CERTIFIED
residual quantum transfer        FORBIDDEN
```

Machine receipt:
`anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json`.
