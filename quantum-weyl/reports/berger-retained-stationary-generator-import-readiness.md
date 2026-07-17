# Berger retained stationary-generator import readiness

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The quantum repository now has a fail-closed consumer for the classical result
`BERGER_RETAINED_26_STATIONARY_GENERATOR_V1`.  A candidate manifest must pin a
classical Git commit and the file and internal hashes of four exact PBW
operator matrices:

- `A104`;
- `q_Cauchy_104`;
- `G_Cauchy_104`;
- `real_structure_104`.

Every matrix must use the frozen 104-row Cauchy ordering.  The consumer
independently replays (q^2=0), ([A,q]=0), nondegeneracy and BRST
compatibility of (G), Krein skew-adjointness of (A), and the involution,
intertwining and pairing identities for the real structure.  A small exact
accepted carrier and a nonnilpotent mutation exercise the acceptance logic.

The input is not present, so the result remains
`CONSUMER_READY_STATIONARY_CARRIER_INPUT_NOT_SUPPLIED`.  Moreover, spectral
isolation of zero is deliberately excluded from the finite PBW import: it is
a theorem about a closed realization on the declared mixed Sobolev/Krein
space.  After an algebraic import passes, the next scientific result is the
zero/Jordan spectral ledger.

No stationary carrier, zero-frequency ledger, covariance, Hadamard state,
physical positivity, renormalized product, QME, particle interpretation or
quantum theorem is claimed.
