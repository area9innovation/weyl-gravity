# Horizon center self-map repair v1

This package isolates panel 77 at the horizon seed
`r=2+2^-22`.  It audits the seed `q`, `eta`, and `xi` radii and the
first-step quadratic self-map, then compares a bounded grid of legitimate
repairs.

The accepted repair replaces the cancellation-prone binary64 expression for
the smaller quadratic root by the algebraically equivalent interval formula

```text
2 qc / (-qb + sqrt(qb^2 - 4 qa qc)).
```

The candidate is enlarged by the exact rational factor `1000001/1000000`
and the original strict self-map inequality is still required.  No refusal
threshold is lowered.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
