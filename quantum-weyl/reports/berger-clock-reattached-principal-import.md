# Berger clock-reattached principal import

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The authoritative classical principal witness is now pinned and independently
replayed without importing its producer. Reattaching the eight contractible
clock rows restores the temporal-diffeomorphism and Weyl generators on the
34-row minimal presentation. The consumer reconstructs the five-generator
gauge symbol, normalized companion, fibre identification, and verifies

```text
J H_4 + K_1 T = (zeta^2)^2 I_10,
T K_1           = (zeta^2)^2 I_5.
```

Thus the preferred principal architecture is a support-local clock
reattachment with scalar null cone `zeta^2=0`. The rank-eight symbol of the
retained presentation is not treated as a principal no-go or as a requirement
to classify a singular characteristic variety before using the certified SDR.

This is not a curved or causal theorem. Lower PBW orders of the companion, the
exact 34-row cyclic `QW+WQ` identity, advanced and retarded Green operators,
transport back to 26 rows, and Hadamard data remain open. The immediate gate
is `BERGER_CURVED_CLOCK_REATTACHED_WITNESS`.

Reproduce with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.clock_reattached_principal_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_clock_reattached_principal_import.py -v
```
