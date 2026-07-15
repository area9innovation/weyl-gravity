# Einstein--Maxwell product-incidence receipt

Date: 2026-07-15

## Result

The `LOCAL-ALGEBRAIC` certificate
`EINSTEIN_MAXWELL_PRODUCT_INCIDENCE` establishes a positive, exact
same-metric and same-Maxwell-field intersection of cosmological
Einstein--Maxwell and pure Weyl--Maxwell solution loci.

On `M_2(k_1) x Sigma_2(k_2)`, the common nondegenerate branch is

```text
Lambda=(k_1+k_2)/2
rho=(k_2-k_1)/(2*kappa)
alpha_B*kappa*(k_1+k_2)=3.
```

Its flat critical specialization is `R^(1,1) x S^2`; a spatial translation
quotient gives compact Cauchy topology `S^1 x S^2`. A rational fixture
`(k_1,k_2,alpha_B,kappa,Lambda,E,P)=(0,1,3,1,1/2,0,1)` satisfies both metric
equations componentwise.

The lifecycle state is `CLASSIFIED`. The tangent BV comparison remains
`OPEN`, and no clock, causal, scattering, observable, or quantum claim is
promoted.

## Verification

The generator derives all curvature and stress tensors in exact SymPy
arithmetic. The independent consumer rechecks the tensor blocks, both metric
equations, the flat specialization, the rational fixture, and the optional
`U(1)` flux-quantization relation.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile bridge/einstein_sector/einstein_maxwell_product_incidence.py bridge/einstein_sector/verify_einstein_maxwell_product_incidence.py bridge/einstein_sector/tests/test_einstein_maxwell_product_incidence.py` | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on the schema and generated certificate | < 0.1 s each | PASS |
| 1 | `python3 -m bridge.einstein_sector.einstein_maxwell_product_incidence --verify bridge/certificates/einstein_maxwell_product_incidence.json` | 0.78 s | PASS |
| 1 | `python3 bridge/einstein_sector/verify_einstein_maxwell_product_incidence.py` | 0.68 s | PASS |
| 1 | `python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_product_incidence` | 0.97 s | PASS (7 tests) |

Tier 2 was not run because this adds an isolated, content-addressed
background certificate and does not change a mathematical input, shared
operator, schema, or artifact consumed by an existing certificate chain.

Tier 3 is not required because this is a new scoped background
classification, not a freeze/tag, quantum lifecycle promotion, shared-core
algebra change, or release.

## Pre-existing shared-tree changes

The session began with in-progress Berger contraction and quantum transfer
edits. None belongs to or is included in this theorem package.
