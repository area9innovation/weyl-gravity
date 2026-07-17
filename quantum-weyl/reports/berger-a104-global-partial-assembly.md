# Berger global partial A104 assembly

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

## Result

The two exact sector-local rank-40 Cauchy operators are now embedded into the
frozen 104-row ordering.  The metric block occupies global indices

```text
6..25, 58..77
```

and the metric-antifield block occupies

```text
26..45, 78..97.
```

The retained 26-row endpoint is certified degree-block diagonal.  Therefore
all off-degree coordinates in the Cauchy operator are structural zeros.  The
global receipt certifies

```text
total coordinates:                 10816
known coordinates:                 10528
known exact block coordinates:      3200
known structural-zero coordinates:  7328
unknown coordinates:                 288
```

The only unknown coordinates are the two diagonal endpoint blocks:

```text
ghost_A12:     0..5, 52..57
identity_A12: 46..51, 98..103
```

The emitted sparse `global_A104_partial` artifact and its independent
`global_A104_known_entry_mask` remove any ambiguity between an exact zero and
an entry that has not yet been computed.

## Endpoint insertion contract

The next classical package must export the four exact 3-by-3 factor records

```text
F_spatial_K_spatial
Box_1_spatial_covector
F_spatial_K_spatial_formal_adjoint
Box_1_spatial_covector_formal_adjoint
```

with frozen row order, differential-axis order, exact coefficient ring,
source commit and internal hash.  The consumer must replay the two factor
compositions, formal adjoints, second-order graph companions, invertible
temporal leading matrices and the derived rank-12 Cauchy blocks.  Those blocks
then enter only through the two global index lists above.

The dedicated strict schema
`berger-endpoint-a24-cauchy-export-v1.schema.json` defines the complete future
payload, including the four sparse factor records, both derived `A12` blocks
and eight mandatory exact checks.  Its content hash is frozen into this
certificate.

## Cauchy BRST contract

The receipt separately freezes two required exact artifacts:

```text
q52_companion: 52 x 52
q_Cauchy_104: 104 x 104
```

The package must prove degree (+1), nilpotency, exact companion/first-jet
prolongation and, after both endpoint slots are populated,

\[
[A_{104},q_{\mathrm{Cauchy}}]=0.
\]

This prevents a coefficientwise `A104` from being mistaken for a
BRST-compatible Cauchy complex.

## Claim boundary

This is an exact global indexing and insertion theorem.  The endpoint and
BRST contracts are frozen but unpopulated.  Full `A104`, the Cauchy Lagrange
or Krein form, closedness, spectral isolation, Hadamard data, QME restoration
and quantum conclusions remain open.

## Verification receipt

The strict Draft 2020-12 schema, focused tests, certificate freshness check
and independent verifier replay the global embeddings, file and internal
hashes, mask counts, exact slot coverage and fail-closed mutations.

Both new schemas pass `Draft202012Validator.check_schema`; the emitted global
certificate also passes a full Draft 2020-12 instance validation.  The focused
stationary/preflight/global chain runs 26 tests.
