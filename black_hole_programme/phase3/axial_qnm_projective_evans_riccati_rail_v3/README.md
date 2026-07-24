# Projective Evans/Riccati rail v3

This bounded successor consumes the first sixteen common-generator two-sided
Riccati exports at `r=32`.  For every panel it emits the typed projective
quantities

```text
Delta       = q_H       - q_out       + 2 I omega
Delta_tau   = q_H_tau   - q_out_tau
Delta_omega = q_H_omega - q_out_omega + 2 I
```

and audits the phase convention, fixed projective chart, shared omega
generator, post-normalization finiteness, and panel-local boundary
nonvanishing.

All panels 0--15 pass the co-location and nonvanishing gates.  The local-QNM
programme stops fail-closed because only 16 of 512 boundary panels have been
certified.  Independently, the present `Delta_tau` and `Delta_omega`
rectangular enclosures contain zero on every completed panel, so they cannot
yet certify a defective selector or a simple-root Newton denominator.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
