# Lorentzian analytic contracts

This package contains fail-closed interfaces for causal Green operators,
Hadamard data, and later causal products.  Interface readiness is not an
analytic existence theorem.

The first contract is the retained 26-row Berger endpoint.  It requires both
advanced and retarded chain-homotopy identities, causal support, cyclic
adjointness, `D`-equivariance, row completeness, and an explicit zero-mode
policy.  Hadamard certification is a separate conditional stage.

Reproduce the current contract receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.green_endpoint_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_green_endpoint_contract.py -v
```
