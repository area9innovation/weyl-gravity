# Lorentzian analytic contracts

This package contains fail-closed interfaces for causal Green operators,
Hadamard data, and later causal products.  Interface readiness is not an
analytic existence theorem.

The first contract is the retained 26-row Berger endpoint.  It requires both
advanced and retarded chain-homotopy identities, causal support, cyclic
adjointness, `D`-equivariance, row completeness, and an explicit zero-mode
policy.  Hadamard certification is a separate conditional stage.

The first physical input has also landed: the ghost and dual identity
endpoint blocks are Green hyperbolic by exact normally-hyperbolic
factorization.  The import independently replays all four `QW+WQ` blocks and
the generic rank-eight-plus-two metric principal boundary. Characteristic-rank
stratification remains open, so rank eight is not asserted on every
characteristic covector. The metric Green realization—and therefore the full
26-row endpoint—remains open.

The clock-reattached principal theorem has now been independently imported.
It resolves the retained rank-eight presentation upstairs as scalar biwaves
on the 34-row minimal complex. The preferred route is to complete the curved
lower-order `QW+WQ` witness there and transport Green operators back through
the support-local clock SDR. Direct retained routes remain allowed, but only
with characteristic-rank stratification.

Reproduce the current contract receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.green_endpoint_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_green_endpoint_contract.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_endpoint_factor_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_endpoint_factor_import.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.clock_reattached_principal_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_clock_reattached_principal_import.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_mixed_order_green_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_mixed_order_green_contract.py -v
```
