# Complete retained Berger minimal BV operator

The full 26-row minimal differential is now coefficientwise exact in the
ordered invariant-frame PBW basis.  It contains the spatial diffeomorphism
generator, the action-derived matter-coupled Berger Hessian, and the cyclic
dual identity row.

The curved Bach block was derived from the Schouten formula on the actual
nonzero-Weyl Berger background.  Its expansion has nonzero terms at every
differential order from zero through four.  The order-four block agrees with
the independently derived principal matrix, while the background formula
reproduces the separately certified Berger Bach tensor.

Exact PBW composition proves

```text
H_retained K_spatial = 0
minus_K_spatial_sharp H_retained = 0
H_retained^sharp = H_retained
q1_retained^2 = 0
```

All entries are finite-order differential operators with invariant
coefficients and therefore preserve support.  This promotes
`BERGER_RETAINED_MINIMAL_OPERATOR` only.  Nonminimal gauge-fixing rows and the
causal Green contraction remain the next analytic work; q2 and the arity-two
D-Cartan contraction remain downstream.
