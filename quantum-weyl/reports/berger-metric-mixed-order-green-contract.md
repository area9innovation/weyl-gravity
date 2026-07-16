# Berger metric mixed-order Green realization contract

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The remaining retained endpoint is not a scalar rank-ten biwave problem. Its
fourth-order principal block has generic rank eight with two exact polynomial
clock/constraint carriers. The characteristic-rank stratification remains
open, so rank eight is not asserted pointwise on every characteristic
covector.

This contract accepts three possible architectures: a filtered mixed-order
system, a first-order differential-algebraic reduction, or an auxiliary-field
reduction. Any of them must export exact forward and backward equivalence
maps, advanced and retarded operators for both the metric and
metric-antifield blocks. The four explicit ghost/identity endpoint factor
records still owed by the classical source are recorded as downstream
full-endpoint assembly inputs; they do not block the independent metric
verdict.

Acceptance requires exact proofs of both left and right inverse identities,
advanced/retarded support, characteristic-rank stratification, propagation of
the clock and Weyl constraints, formal-adjoint and cyclic compatibility,
`D`-equivariance, row completeness, and a zero-mode policy. A principal-symbol
factorization alone cannot pass.

Even a successful metric export does not implicitly promote the full 26-row
Green homotopy. Assembly with the already certified ghost and identity blocks
must pass the separate endpoint contract. Hadamard data and quantum execution
remain later stages.

Reproduce the interface receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_mixed_order_green_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_mixed_order_green_contract.py -v
```

The combined endpoint-factor, full-endpoint-contract, and metric-contract rail
passes 20 tests in 26.7 seconds. Strict AJV Draft 2020-12 validation passes for
all three checked certificates, and the physical metric-export schema compiles
in strict mode. Tier 0 and the affected Lorentzian Tier 1 rail were run. Tier 2
and Tier 3 were not required because no mathematical input, shared operator,
freeze, lifecycle theorem, or release claim changed.
