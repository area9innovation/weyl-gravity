# Branch C reduced spectral bootstrap

## Result boundary

Dependency tag: `REDUCED-MODE`

The first Branch C artifact is an exact branch and provenance ledger, not a
determinant calculation. It is deliberately fail-closed while the classical
snapshot is unfrozen. Its lifecycle state is `CLASSIFIED` only in the narrow
sense that the already-certified reduced branch data have been inventoried;
it is not a classification of local BV counterterms or anomalies.

The common-schema result envelope is
`quantum-weyl/certificates/REDUCED_MODE_SPECTRAL_BOOTSTRAP.json`. It points to
the detailed machine proof receipt at
`quantum-weyl/spectral/reduced_modes/certificates/eal_branch_ledger.json`.

## Imported exact artifacts

| Artifact | Imported datum | Dependency tag |
|---|---|---|
| `covariant_completion/certificates/EAL_multiplicity_match.json` | all-energy field origins, thresholds, multiplicities, and the omitted `A_2` Killing band | `REDUCED-MODE` |
| `covariant_completion/certificates/curved_EAL_spectrum_all_level.json` | symbolic character identity, chirality completion, and low-level dimension regression | `REDUCED-MODE` |
| `covariant_completion/certificates/branch_residue_operators.json` | reduced-action residue formulae, elliptic orders, and `+E,-A,-L` signs | `REDUCED-MODE` |

The receipt records a SHA-256 digest for every imported file. The verifier
recomputes the parity-complete multiplicities and rational characters with
exact symbolic arithmetic rather than trusting displayed low-level values.

## Exact branch ledger

| Branch | Origin | Energy | Parity-complete multiplicity | Sign | Positive residue | Dependency tag |
|---|---|---:|---:|---:|---:|---|
| `E` | lower-frequency TT Bach branch | `N >= 2` | `2(N-1)(N+3)` | `+1` | `4(N+1)` | `REDUCED-MODE` |
| `A` | transverse-vector metric branch | `N >= 3` | `2(N-1)(N+1)` | `-1` | `2(N^2-4)` | `REDUCED-MODE` |
| `L` | upper-frequency TT Bach branch | `N >= 4` | `2(N-3)(N+1)` | `-1` | `4(N-1)` | `REDUCED-MODE` |

The energy-two transverse-vector Killing band is not an `A` metric mode:
its symmetrized gradient vanishes. This is the only zero-mode exclusion
currently promoted into the reduced ledger. A complete zero-mode policy is
still `NOT_COMPUTED`.

## Verified character identities

Dependency tag: `REDUCED-MODE`

The verifier derives the three branch characters and proves their sum equals

```text
Z(q) = 2 q^2 (5 + 5q - 4q^2)/(1-q)^3.
```

With the reduced invariant-form signs it also verifies

```text
Z_signed(q) = 2 q^2 (4q^2 - 11q + 5)/(1-q)^3.
```

The coefficients are checked against direct exact branch counting through
energy 40; the proof itself is the rational-function identity, not the
finite regression.

## Explicitly open bookkeeping

Dependency tag: `REDUCED-MODE`

The following fields are present and set to `NOT_COMPUTED`:

- branch kinetic eigenvalues and determinant contributions;
- full ghost and auxiliary multiplicities;
- complete zero-mode policy;
- determinant phases and signs beyond the reduced Krein ledger;
- measure normalization and contour policy;
- regularization and analytic extrapolation;
- rational reconstruction and one-loop coefficients.

Consequently this bootstrap supplies no evidence for Euclidean ellipticity,
Lorentzian causal products, the Slavnov identity, anomaly cancellation, or
the quantum master equation.

## Verification receipt

Dependency tag: `REDUCED-MODE`

Recorded at `2026-07-15T08:23:41+02:00`:

| Tier/check | Command scope | Elapsed | Status |
|---|---|---:|---:|
| Tier 0 | Python byte-compilation of the new producer and scoped test | `0.03 s` | `0` |
| Tier 0 | JSON parsing of both generated records and both new schemas | `0.12 s` | `0` |
| Scoped | deterministic producer with `--check` | `2.93 s` | `0` |
| Scoped | `test_reduced_mode_bookkeeping.py` | `2.12 s` | `0` |
| Tier 0 | common quantum result-schema validator | `0.02 s` | `0` |
| Tier 0 | `git diff --check -- quantum-weyl` | `<0.1 s` | `0` |

Tier 2 and Tier 3 were not triggered: this change is isolated bookkeeping,
does not alter an upstream classical/covariant producer, and verifies the
unchanged upstream inputs by their recorded hashes. No full-repository suite
or expensive certificate regeneration was run.
