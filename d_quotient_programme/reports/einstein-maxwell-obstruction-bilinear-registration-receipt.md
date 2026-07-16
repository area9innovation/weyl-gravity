# Einstein--Maxwell obstruction-bilinear registration receipt

Date: 2026-07-16

The programme imports commit
`61b0bff20d5dc551831e85a73119903254c3edb9` and certificate
`bridge/certificates/einstein_maxwell_obstruction_bilinear.json` with SHA-256
`35f11f43b7d4ea80c2a39cbc40ba24bff58da1e56cf9fe74b27f59317b58654d`.

The registered phase space is the declared four-dimensional compact fixture
span, and the codomain is the constant-lapse component of the adjoint
cokernel. The verdict
`G1_CONSTANT_LAPSE_OBSTRUCTION_BILINEAR_ON_FIXTURE_SPAN` must not be promoted
to the complete harmonic theorem.

The contribution records the exact polarized matrix, harmonic selection
rules, fixed-versus-variable charge cokernel change, and relative Taub
interpretation. The complete linear domain, full cokernel, and surviving
equal-harmonic polarization blocks remain open.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The command passed in `0.19 s`, including exact regeneration, evidence hashes,
and mutation guards. This satisfies the affected Tier-2 programme chain. Tier
3 was not run because the contribution is a scoped `G1` classification, not a
full harmonic freeze, lifecycle promotion, or release.
