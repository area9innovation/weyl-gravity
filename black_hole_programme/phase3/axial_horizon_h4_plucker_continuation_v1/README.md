# Chunked q00 Plücker continuation

This package continues the certified q00
\(\Lambda^3(\mathbb C^6)\) transport beyond shell 3, segment 0 without
rerunning an ever-growing monolith.

The boundary exporter is an instrumented copy of the exact predecessor
source. It reproduces all 13 certified predecessor checkpoints and emits
the complete 40-row degree-four Taylor enclosure. Each subsequent chunk
embeds that state bit-for-bit, names its input payload hash, and emits a new
state only after every requested segment and all 45 Plücker relation checks
pass.

The bounded chain consists of:

1. the remaining three segments of shell 3;
2. the four segments of shell 4;
3. shell 5, only if shell 4 passes.

Execution stops at the first typed refusal. No failing chunk emits a shared
output state.

From the standalone `weyl-gravity` repository root:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.\
axial_horizon_h4_plucker_continuation_v1.run_bounded

PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.\
axial_horizon_h4_plucker_continuation_v1.test_continuation

PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.\
axial_horizon_h4_plucker_continuation_v1.verify
```

This is a bounded representation audit. It does not establish the complete
23-shell transport, endpoint amplitudes, or scattering.
