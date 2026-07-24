# Bplus4 content-addressed successor chunk 01

This package resumes only from the certified `r=247/8` correlated outgoing
checkpoint.  It advances one adaptive high-order panel and emits a new
content-addressed checkpoint without replaying the transport from infinity or
from `r=31`.

The runtime selection contract is:

1. try step `-1/8`, coefficient radius `1/16`, order `96`;
2. accept it only when the validated exponential pre-tail is finite,
   nonnegative, and below `1/2`;
3. otherwise rebuild with step `-1/16`, radius `1/32`, order `64`;
4. refuse if the fallback pre-tail is not below `1/2`.

The accepted boundary is checked once against the independently expanded
direct sixteen-state system.  Exact Taylor coefficients must agree and the
interval difference must contain zero.

Only `checkpoint.json` and the compact `run_manifest.json` are retained.  The
temporary generated source, binary, and raw model stdout are addressed by
hash but not duplicated in the repository.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1.test_chunk01
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_bplus4_chunk01_v1.audit
```

The full `r=4` frame, `T_plus`, and Stokes remain fail-closed.
