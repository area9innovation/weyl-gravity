# Berger causal endpoint-factor import

The first nontrivial part of the Berger causal Green problem is now imported
from the authoritative classical complex and independently replayed on the
quantum side. This is a partial `LORENTZIAN-CAUSAL` result, not a full causal
BV construction.

The retained 26 rows decompose degreewise as `3 + 10 + 10 + 3`. The ghost
three-row endpoint is exactly the composition

```text
alpha_B Box_1 o (F_spatial K_spatial),
```

whose two factors have scalar Lorentzian principal symbol. Its dual identity
endpoint follows by formal adjoint factorization. The consumer reconstructs
all four exported `QW+WQ` blocks from the pinned PBW matrices, checks the
ghost biwave principal symbol exactly, and replays the metric principal
kernel.

The metric and metric-antifield endpoints remain open. Their fourth-order
principal block has **generic** rank eight: two exact polynomial null carriers
give the upper bound, while an exact rank-eight specialization gives the
generic lower bound. Its two generic kernel directions are carried by the
temporal-diffeomorphism clock and Weyl constraint. Rank stratification on the
characteristic set has not been classified and further rank drops have not
been excluded. These are constraint carriers, not new residual particle
states, and this import introduces no negative physical direction.

Consequently neither the retained 26-row nor the lifted 54-row causal chain
homotopy is constructed. Hadamard data, renormalized time-ordered products,
and Lorentzian quantum execution remain unauthorized. The next theorem is
`BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION`.

Reproduce the receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_endpoint_factor_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_endpoint_factor_import.py -v
```

Tier 0 and this scoped Tier 1 rail are the applicable checks. The transitive
classical chain is content-addressed at commit
`b6caaddde5bce3480ef4d91e6b0c2824b98050dd`; no shared algebra or theorem
lifecycle is promoted, so Tier 2 and Tier 3 are not required.
