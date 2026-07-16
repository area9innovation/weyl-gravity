# Berger metric mixed-order Green realization contract

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The retained presentation has a generic rank-eight fourth-order symbol with
two clock/constraint carriers. The imported clock-reattached theorem now
shows this is a presentation effect: reversing the support-local clock SDR
restores a scalar biwave on all ten metric and five gauge directions.

The preferred fourth architecture is therefore
`CLOCK_REATTACHED_SUPPORT_LOCAL_SDR`, alongside the direct filtered,
differential-algebraic, and auxiliary-field routes. A direct retained solver
must classify its characteristic-rank strata. The clock-reattached route does
not: it now pins both the imported scalar-biwave witness and the certified
curved lower-order `QW+WQ` identity upstairs. The remaining analytic work is
to construct advanced and retarded Green operators for `P34`, establish their
causal support and cyclic adjointness, and prove support-local Green transport
back through the SDR.

All routes require exact proofs of both left and right inverse identities,
advanced/retarded support, propagation of constraints, formal-adjoint and
cyclic compatibility, `D`-equivariance, row completeness, and a zero-mode
policy. The clock route additionally requires the curved 34-row witness,
scalar null-cone control, and SDR transport. The curved witness is now
imported and exactly replayed; Green realization and transport remain open. A
principal-symbol factorization alone cannot pass.

Even a successful metric export does not implicitly promote the full 26-row
Green homotopy. Assembly with the already certified ghost and identity blocks
must pass the separate endpoint contract. Hadamard data and quantum execution
remain later stages.

Reproduce the interface receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_mixed_order_green_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_mixed_order_green_contract.py -v
```

The affected landed-curved-witness and metric-contract rails pass 19 tests
(9 exact adapter/import tests in 61.55 seconds and 10 contract/schema/mutation
tests in 0.58 seconds). The import and contract certificates reproduce from
their content-addressed sources. Tier 0 and the affected Lorentzian Tier 1/2
rails were run. The full classical chain and Tier 3 were not required because
the pinned classical input is content-addressed and no causal or quantum
lifecycle theorem is promoted.
