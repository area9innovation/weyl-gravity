# Typed biwave Volterra Green theorem import

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The quantum lane now pins and independently validates the classical theorem
for `A=P2 P1+V`, with normally hyperbolic factors and graph-bounded
`ord(V)<=2` on compact-Cauchy globally hyperbolic spacetimes. The consumer
checks the distinct source and solution resolvents, both factorial bounds,
both inverse identities, causal globalization, reversed adjoint factor order,
all proof hashes, source manifest, timed receipt, and the Berger and Nariai
specializations. The two consumer blobs are independently resolved at the
pinned commit and checked against their declared hashes and result IDs.

An independent noncommuting rational fixture reproduces the typed identities.
Conflating the source and solution resolvents produces a nonzero push-through
defect. The theorem remains conditional on an exact physical normal form and
its energy hypotheses. It supplies no Hadamard state, renormalized product,
QME disposition, or quantum theory.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.typed_biwave_volterra_theorem_import --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_typed_biwave_volterra_theorem_import
PYTHONPATH=quantum-weyl python3 -m unittest lorentzian.tests.test_typed_biwave_volterra_theorem_import
```
