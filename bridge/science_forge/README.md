# Science Forge imports

This directory contains bounded imports of results computed in the independent
[`area9innovation/tango`](https://github.com/area9innovation/tango) repository.
An import pins the source commit and artifact hashes, checks the exact values
used locally, and preserves the upstream claim boundary.  It does not silently
turn external evidence into a theorem freeze.

The first import records the exact sixth-order Pais--Uhlenbeck obstruction at
the `5:3` and `7:1` resonances.  Verify the self-contained import with:

```bash
python3 bridge/science_forge/verify_science_forge_pu_order6_import.py
python3 -m pytest bridge/science_forge/tests -q
```

For the stronger source checkout gate, check out Tango at the pinned commit and
run:

```bash
python3 bridge/science_forge/verify_science_forge_pu_order6_import.py \
  --source-root /path/to/tango
```

The source certificate records that its original emission used a dirty
development-toolchain checkout.  The import therefore includes a second replay
from a `git archive` of the pinned commit: a fresh compiler built with Go 1.25.8
reproduced all 31 exact checks and all three SymPy golden comparisons.  The
general all-coprime hierarchy remains conjectural despite this clean replay.
