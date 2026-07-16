# Berger curved clock-reattached witness adapter

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The existing classical exports contain more of the curved step than their
headline lifecycle flag suggests. The exact (5\times10) companion, the
(10\times12) raw-from-dressed metric map, and the transported (5\times12)
gauge condition satisfy coefficientwise

```text
T_raw o raw_metric_from_dressed = A_dressed.
```

The portable 34-row unary differential is also reconstructed exactly and is
nilpotent. No new companion coefficient solve is required.

The source does not, however, export a complete `W34`, its declared target
`P34`, or the 34-row cyclic pairing as a portable operator record. The checked
scientific receipt therefore retains `INPUT_BLOCKED`. It does not infer these
objects or promote `BERGER_CURVED_CLOCK_REATTACHED_WITNESS`.

The adapter is ready for the authoritative export. It checks

```text
q34 W34 + W34 q34 - P34
```

exactly in the invariant-frame PBW algebra and separately checks cyclicity of
`q34` and `W34`. A nonzero result returns the first highest-order PBW
coefficient functional normalized to pair to one with the defect. A zero
result records the exact operator hashes but still does not authorize Green
inversion. Exact zero and nonzero mechanics fixtures exercise both branches;
they are explicitly not scientific substitutes for the missing export.
The interface also hashes the authoritative 34-row layout. Every nonzero
witness reports its input/output field names and degrees, derivative
multi-index, and total `(D)`-weight, rather than leaving a basis-ambiguous
numeric matrix coordinate. The unary `q34` record is hashed as part of the
same coordinate contract. A nonzero coefficient is an obstruction to the
submitted candidate's certification; it is not a global nonexistence theorem
for every possible curved witness.

Reproduce with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.curved_witness_adapter_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_curved_witness_adapter.py -v
```

When the authoritative export lands, evaluate it with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.curved_witness_adapter \
  --input path/to/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json \
  --repository-root .
```

## Verification receipt

| Rail | Elapsed | Result |
|---|---:|---|
| Readiness certificate regeneration and independent `--check` | 11.66 s (`--check`) | PASS |
| Six scoped exact unit/mutation tests | 41.76 s | PASS |
| Readiness certificate under AJV Draft 2020-12 strict mode | 2.80 s | PASS |
| Future export schema compilation under AJV Draft 2020-12 strict mode | 1.45 s | PASS |

The unit rail covers exact companion transport, reconstructed unary
nilpotency, an exact-zero primitive branch, a nonzero normalized obstruction
branch with named field content, a forged operator hash, and a mutated
coordinate transport. Tier 2 was not required because no authoritative
classical operator, shared algebra backend, or downstream physical
certificate changed. Tier 3 was not run because this is an input-blocked
consumer interface, not a freeze or theorem promotion.
