# Fully rearranged BT lambda-nine parity selection

**Certificate:** `REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. **Lifecycle:** `COEFFICIENT_COMPUTED`.

## Result

The complete probability-order-\(\lambda^9\) coefficient of the covariantly
dressed fully rearranged packet experiment is exactly zero in both the public
Krein and positive Hilbert prescriptions.

Exact coupling/Fock-parity covariance gives
\(S_\lambda[\phi]=S_{-\lambda}[-\phi]\).  Coupling order therefore equals
total fluctuation Fock-parity change.  This parity is distinct from BT ghost
parity \(\kappa\).

For the three-particle source and detector,

\[
 Y(\lambda)=\lambda^4y_4+\lambda^5y_5+O(\lambda^6),
 \qquad \Pi_Fy_4=-y_4,\quad \Pi_Fy_5=+y_5.
\]

The complete \(y_5\) includes order-five dynamics, \(T_4\psi_1\) from the
first source correction, and the first covariant detector correction.  Both
Born forms commute with the self-adjoint parity, hence

\[
 q_9^{\rm public}=2\operatorname{Re}\langle y_4,y_5\rangle_K=0,
 \qquad
 q_9^{\rm Hilbert}=2\operatorname{Re}\langle y_4,y_5\rangle_H=0.
\]

Thus the current physical result sharpens to

\[
 q_{\rm click}=\lambda^8q_8+\lambda^{10}q_{10}+O(\lambda^{12})
\]

in parity order.  The common-Born \(q_8\) is certified; \(q_{10}\) is not.

An exact four-dimensional block witness independently gives zero cross term
for both metrics and a nonzero value 20 after a parity-breaking metric
mutation.

## Boundary and next gate

This does not compute or sign \(q_{10}\), prove finite-coupling positivity,
cover a detector held noncovariantly fixed under \(\lambda\mapsto-\lambda\),
complete spectator-overlap sectors, construct an all-time operator, establish
loops/KLN, Eq. (19), gravity/BV--BRST transfer, Lorentzian causality, or
literature priority.

The next calculation is the complete \(q_{10}\) ledger:
\(\|y_5\|^2+2\operatorname{Re}\langle y_4,y_6\rangle\), including the
order-six connected/loop block, second-order source and detector corrections,
and survival terms.  Total ghost-\(\kappa\) fixedness must then be checked
before calling \(q_{10}\) common-Born.

## Verification

All scientific Python, TeX and repository-test processes ran sequentially
under the 500 MB virtual-memory ceiling.

- Tier 0 passes: three Python files compile, all changed JSON parses, the
  strict Draft-2020-12 schema and certificate validate, an injected property
  is rejected, both TeX files contain zero carriage-return bytes, and scoped
  `git diff --check` is clean.
- The exact producer passes `20/20` in `0.02 s` at `16184 KiB`; the independent
  verifier passes `37/37` in `0.02 s` at `15356 KiB`; all `29` mutation tests
  pass in `0.015 s` (`0.05 s` wall) at `18556 KiB`.
- The fully rearranged common-Born, tagged parity-selection and compact
  dressed-source producer/verifier pairs all pass.  The six-command affected
  Tier-2 chain took `1.23 s` at `70236 KiB`.
- Papers V and VI compile twice with no undefined citations or references and
  no new overfull box.  Their PDFs have `79` pages and `738905` bytes, and
  `68` pages and `697307` bytes, with SHA-256
  `f57d1a67165b7daea9c3294949719aec11ec73f56ea5746363515b741af48c8b`
  and `50dd31632427315776b48225623ee973ef7f56bdbc04acf67cb5e24c8accdb64`.
  The builds took `1.10 s` at `51004 KiB` and `1.08 s` at `50920 KiB`.
- Tier 3 is fail-closed, not a repository-wide pass: `3166` tests ran in
  `707.055 s` (`708.19 s` wall) at `391196 KiB`, with the established `31`
  failures and `9` skips.  All `29` tests introduced here pass.  Older
  certificate drift and the concurrently growing fifteen-path `chain_imports`
  outside-reference list remain unresolved.
- The append-only planning fold accepts `1569` nodes with zero invalid items
  and zero malformed events in `1.47 s` at `14116 KiB`.  The advisory shadow
  exits zero by design in `1.05 s` at `33200 KiB`, but its bridge audit remains
  fail-closed at the known toolchain/stdlib `E9118` mismatch; its census finds
  `1624` certificates and `1405` verifiers.  A capped shadow attempt failed Go
  virtual-arena reservation and is not counted as a pass.

Tier 3 was required by the Paper V/VI theorem update.  No classical freeze,
QME state, residual transfer or `LORENTZIAN-CAUSAL` state changed.  The final
certificate SHA-256 before staging is
`3675c120b414be2e1e0db8621d6b1624b5bcf0ad6adbef20eb24f0995698e30d`.
