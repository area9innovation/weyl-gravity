# Complete Berger retained 26-row q2 transfer

Dependency tag: `LOCAL-ALGEBRAIC`.

The complete 150,305-coefficient classical Berger operation was transferred
through the exact cyclic 54-to-26 SDR using exact `Q(sqrt(10))` arithmetic:

```text
q2_26 = pi_26 q2_54(iota_26 tensor iota_26).
```

The contraction support reduces the calculation to 78,627 inner-map
contributions and 54,236 outer Leibniz contributions. The canonical result has
54,236 nonzero PBW coefficients on all 26 output rows and maximum total jet
order four. Coefficientwise checks give

```text
q1_26 q2_26 + q2_26(q1_26,-) + (-1)^|x| q2_26(-,q1_26) = 0
odd-Darboux BV cyclicity defect = 0.
```

This operation lives on the retained 26-row complex. It is not yet the
minimal residual/cohomology `ell2`, and it does not evade the certified bare
unary D-Cartan obstruction. The next mathematical gates are the
characteristic symbol-cohomology carrier theorem and separate residual/BFV or
Lorentzian-causal extensions.

Fast receipt and mutation checks:

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_26_q2_transfer_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_26_q2_transfer.py -v
```

Full exact recomputation:

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_26_q2_transfer_certificate --replay-check
```
