# Berger 26-row Green/Hadamard endpoint contract

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The certified 54-to-26 reduction leaves one analytic endpoint.  The new
portable contract accepts that endpoint only when it supplies content-hashed
operators for

```text
q26, Lambda_plus, Lambda_minus, pairing26, D26
```

and independent proofs of both chain-homotopy identities, advanced/retarded
support, cyclic adjointness, `D`-equivariance, row completeness, and the
declared zero-mode policy.  A Green certificate may leave Hadamard data open;
promotion to a Green-plus-Hadamard result additionally requires the wavefront,
bisolution, CCR, BRST, and positivity/Krein checks.

The checked-in receipt is
`INTERFACE_READY_PARTIAL_ENDPOINT_FACTORS_RECEIVED`. The ghost and identity
endpoint factors have landed, while the metric and metric-antifield blocks
remain open. The receipt pins the partial-input certificate and records the
still-missing explicit PBW records for both normally hyperbolic factors and
their formal adjoints.

The two-row exact fixture tests only the algebraic chain, adjoint, and
equivariance mechanics. It has no causal geometry and supplies no complete
physical propagator. The full 26-row Green homotopy and Hadamard stage remain
blocked.
