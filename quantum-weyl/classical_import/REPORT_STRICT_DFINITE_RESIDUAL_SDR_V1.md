# Strict D-finite residual SDR export v1

**Result:** `STRICT_DFINITE_RESIDUAL_SDR_V1`

**Lifecycle:** `CLASSIFIED`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

The strict pure-Weyl finite harmonic SDR is now a portable exact object rather
than an internal matrix hash.  The ordered direct sum contains
**4490 full coordinates** and
**470 residual coordinates**.
It serializes `q0`, `q_res_0`, `iota_cl`, `pi_cl`, and `s_cl` block by block.

| Energy | Full dimension | Residual dimension | nonzero q0 | nonzero s_cl |
|---:|---:|---:|---:|---:|
| 2 | 230 | 10 | 110 | 110 |
| 3 | 440 | 40 | 200 | 200 |
| 4 | 758 | 82 | 338 | 338 |
| 5 | 1216 | 136 | 540 | 540 |
| 6 | 1846 | 202 | 822 | 822 |

The independent receiver uses only standard-library exact rational sparse
arithmetic.  It reconstructs the expected BGG-split arrows from the declared
sector ledger and replays all eight identities, rather than trusting producer
booleans.

## Foundational strength

For this fixed five-block fixture, primitive-recursive arithmetic suffices:
the bases and witnesses are finite, explicitly enumerated, and all equality
questions reduce to exact integer sparse-matrix multiplication.  No form of
Choice and no completed infinity enters the certified replay.  This statement
does **not** transfer to the all-energy direct sum or continuum field carrier.

## Gate-A effect

The three historically absent portable maps and four associated identities
are now receiver-replayable in the `D`-finite split category.  Gate A remains
`FAIL_CLOSED`: the payload is not the common full support-local strict carrier,
does not include the complete nonminimal field domain or M4 pairing, and does
not supply strict `q2` or `D`.

## Exact commands

```bash
python3 quantum-weyl/classical_import/build_strict_dfinite_residual_sdr.py --check
python3 quantum-weyl/classical_import/check_strict_dfinite_residual_sdr.py
python3 quantum-weyl/classical_import/verify_strict_dfinite_residual_sdr.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_dfinite_residual_sdr.py
```

## What this does not establish

- the common full support-local classical Gate-A snapshot.
- the complete vector and scalar nonminimal field domain.
- an arbitrary-support, smooth, distributional or causal residual contraction.
- strict noncompact SO(4,2) equivariance of the chosen representative SDR.
- the full cyclic pairing required by M4.
- strict support-local q2 or D.
- a Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer.
