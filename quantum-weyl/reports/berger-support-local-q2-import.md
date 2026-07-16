# Complete Berger support-local q2 import

The quantum programme now pins and independently consumes classical commit
`7b352307eb2adb0dfb8e76b7d24f0bb94a37cc8d`. The imported operation is the
complete arbitrary-input classical `q2` on the 54-row gauge-fixed Berger BV
complex:

```text
54 output rows
39 nonzero output rows
4,624 nonzero (output,left,right) blocks
150,305 exact PBW coefficients
maximum total jet order 6
coefficient field Q(sqrt(10))
```

The consumer independently reproduces the payload file and canonical hashes,
matches both classical dependencies to the already frozen quantum unary and
`D` imports, verifies the authoritative row and parity ledgers, rejects
floating-point coefficients, checks cohomological degree, strict PBW order,
the declared jet bound, all row statistics, and every graded Koszul mate.

The classical payload is specialized at

```text
alpha_B = 5
u = 3*sqrt(10)/20
v = 2*sqrt(10)/3.
```

This specialization is explicit because the older arrival fixture used the
symbolic coefficient ring `Q(alpha_B,u,v)`, whereas the scientific export uses
the exact quadratic field `Q(sqrt(10))`.

The import does not merely inherit the producer's identity claims. Independent
quantum-side replay of `q1/q2`, `D/q2`, and BV cyclicity remains a separate
gate. Transfer, Cartan, causal, anomaly, QME, and quantum flags remain false
until their own computations complete.

Reproduce the import with:

```bash
python3 quantum-weyl/transfer/berger_support_local_q2_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_support_local_q2_import.py
```

