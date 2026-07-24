# Bplus4 content-addressed successor chunk 02

This package resumes only the chunk-01 checkpoint and probes a larger
admissible panel before the proven fallback:

```text
primary   step -5/32, radius 5/64, order 120
fallback  step -1/8,  radius 1/16, order 96
```

The primary is accepted only when its validated exponential pre-tail is
finite, nonnegative, and below `1/2`.  The accepted boundary must pass exact
Taylor-coefficient equality and interval containment against an independently
expanded direct sixteen-state system.

The source and raw model stdout are ephemeral and content-addressed.  Only
the successor checkpoint and compact run manifest are retained.

Full `r=4`, `Bplus4`, `T_plus`, and Stokes claims remain false.
