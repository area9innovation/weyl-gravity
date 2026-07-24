# Axial QNM two-sided projective mismatch preflight v1

This package assembles the physical logarithmic-derivative mismatch at `r=32`
from the certified outgoing and horizon projective artifacts:

```text
Delta       = q_H - q_out + 2 i omega
Delta_tau   = q_H_tau - q_out_tau
Delta_omega = q_H_omega - q_out_omega + 2 i
```

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

It stops fail-closed at boundary nonvanishing when the serialized independent
endpoint remainders contain zero. No argument-principle, K0, interval-Newton,
QNM, EP2, or causal claim is made.
