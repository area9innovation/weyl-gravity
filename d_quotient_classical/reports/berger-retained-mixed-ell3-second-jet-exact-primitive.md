# Retained mixed ell3 exact order-two physical primitive

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The complete mixed degree-zero physical-action redefinition problem through
summed differential order two is exactly trivializable. The order-two local
functional quotient has 39,170 independent variational-Euler coordinates
across all 550 two-gravity/two-Maxwell field multisets. Its multiplicity
pattern dimensions are 35 for `2+2`, 55 for `2+1+1`, and 91 for four distinct
fields.

An exact homogeneous correction to the frozen lower primitive has 4,276
nonzero coefficients: 34 zero-jet, first-jet counts `(33,109,118,173)`, and
3,809 second-jet coefficients. After adding it, the complete lower primitive
has 77 nonzero zero-jet coefficients and first-jet counts
`(76,195,206,273)`.

The independent replay proves:

- all 550 zero-page homogeneous equations vanish;
- all four 1,330-row first-page homogeneous equations vanish;
- all 10,043 nonzero order-two Euler target coordinates are reconstructed;
- missing, extra, and changed coordinates are all zero.

The basis-selection square was `5754 x 5754` with 26,578 nonzeros. Its
coefficients admit a conflict-free rationalization of `QQ(sqrt(10))`, after
which SuiteSparse SPEX 3.2.4 solved the row-cleared MPZ system exactly in
31.91 seconds with 662,048 kB peak RSS. Basis selection and SPEX are audit
tools only: the repository verifier trusts neither and instead replays the
exported primitive directly against the pinned exact tensors.
The 4,276 records live in a deterministic gzip chunk with independent
compressed-file and canonical-record hashes.

As a negative control, all 16 target coordinates untouched by second-jet
columns were tested as a coupled dual ansatz. The first-page cokernel
constraints have rank 14, leaving two combinations; the lower Schur condition
leaves one, and that final combination evaluates to zero on the target. Thus
the tempting one-coordinate defects do not define an obstruction.

This does not yet match the positive-jet ghost/antifield completion. It does
not decide the full cyclic deformation class, residual cohomology operation,
SDR independence, amplitudes, or any quantum statement. The next gate is the
positive-jet full-BV cotangent/ghost lift of this exact physical primitive.

## Verification receipt

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_second_jet_exact_primitive.py --check` | 58.54 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_second_jet_exact_primitive.py` | 58.81 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_second_jet_exact_primitive -v` | 61.39 s | PASS (7 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-second-jet-exact-primitive-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1.json` | 4.20 s | PASS |

Tier 2 is the complete affected physical certificate replay against the pinned
source and first-page certificates. Tier 3 is not required because this
promotes only the physical-action page and explicitly retains the full-BV and
deformation-class gates as open.
