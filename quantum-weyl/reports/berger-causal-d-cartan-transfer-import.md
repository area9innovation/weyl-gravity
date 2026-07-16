# Conditional causal Berger D-Cartan transfer import

The exact classical transfer theorem at commit
`f6c42ce5e65318d6e982223999abdcefad10edb5` is now pinned to the imported
54→26 contraction, full support-local `q_2`, retained `q_2`, and the
bare-complex unary obstruction.

The consumer independently reduces the universal-algebra identities. Under
`q Lambda_s + Lambda_s q = 1` and `[q,D]=[Lambda_s,D]=0`, the unary primitive is

\[
\iota^{(1)}_{D,s}=\Lambda_sD.
\]

For `A_D,s^(2)=[q_2,iota_D,s^(1)]`, closure follows conditionally and
the raw graded-symmetric primitive is

\[
\iota^{(2)}_{D,s,\mathrm{raw}}=-\Lambda_sA^{(2)}_{D,s}.
\]

This is a conditional transfer theorem, not the endpoint construction.  The
retained causal Green homotopy and cyclic completion are still absent. The
rank-one wave extension is now imported; the active PDE gate is
`BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS`. The theorem's logical
hypothesis remains the 26-row causal Green homotopy.

Dependency boundary: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.  No Hadamard,
QME, residual/BFV, or quantum claim is made.

Scoped verification receipts:

```text
PYTHONPATH=quantum-weyl python -m transfer.berger_causal_d_cartan_transfer_import_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/transfer/tests/test_berger_causal_d_cartan_transfer_import.py -v
```

The three mutation-sensitive import tests complete in under one second. Tier
0 and the affected Tier 1/2 chain were run. Tier 3 was not required because
the classical inputs are content-addressed and no causal lifecycle state is
promoted.
