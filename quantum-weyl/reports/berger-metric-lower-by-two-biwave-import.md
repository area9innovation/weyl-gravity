# Berger metric lower-by-two biwave import

The quantum consumer pins classical commit
`db099319b79b7fa9e107347fe24fc534a104c09c`. Because that source predates a
producer-side JSON schema, the consumer enforces an exact fail-closed field
contract and pins the certificate, producer, test, report, raw transport and
both generated sparse operators by Git blob hash.

The fast receipt validates both internal sparse-record hashes, the order and
entry ledgers, and all 92 degree-two nondivisibility witnesses. The independent
replay then verifies

\[
A_{10}=\Box_2^2+V_2,\qquad \operatorname{ord}V_2\leq2
\]

against the pinned raw `P34` metric block. It also reproduces the ranks
`9,10,7,10` at exact rational Berger and momentum fixtures. This replay takes
seconds and is the normal quantum test rail; the roughly 150-second geometric
reconstruction remains a classical scientific test.

The result rules out only a factorization fixing the canonical rough-wave
factor on the same ten-component bundle. Mixed-bundle, unequal-subprincipal,
higher-rank prolongation and causal Volterra/Levi constructions remain open.
No advanced/retarded inverse, causal support theorem, Hadamard state, QME or
quantum claim is produced.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.metric_lower_by_two_biwave_import_certificate --fast-check
PYTHONPATH=quantum-weyl python -m lorentzian.metric_lower_by_two_biwave_import_certificate --replay-check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_metric_lower_by_two_biwave_import.py -v
```
