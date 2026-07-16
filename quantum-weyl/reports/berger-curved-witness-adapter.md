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

The authoritative export subsequently landed at commit
`96c28b554f1d1eb548edb2b12def0a9ff853473b`.  It contains complete portable
records for `W34`, its declared target `P34`, and the 34-row pairing.  The
separate import certificate pins that landing commit and replays the
scientific candidate rather than replacing the historical readiness receipt.

The adapter is ready for the authoritative export. It checks

```text
q34 W34 + W34 q34 - P34
```

exactly in the invariant-frame PBW algebra and separately checks cyclicity of
`q34` and `W34`. A nonzero result returns the first highest-order PBW
coefficient functional normalized to pair to one with the defect. A zero
result records the exact operator hashes but still does not authorize Green
inversion. Exact zero and nonzero mechanics fixtures exercise both branches;
they remain interface tests rather than substitutes for the landed scientific
export.
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

The raw adapter invocation for the landed export is:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.curved_witness_adapter \
  --input path/to/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json \
  --repository-root .
```

## Authoritative scientific verdict

The pinned export passes exactly:

```text
q34^2 = 0
pairing34 is nondegenerate
q34 is cyclic for pairing34
q34 W34 + W34 q34 = P34
W34 is cyclic for pairing34
```

Thus the verdict is `ADMISSIBLE_EXACT_CURVED_WITNESS`.  The certified operator
hashes are `9585c1e9...` for `W34`, `a59ac9a4...` for `P34`, and `cedcbc90...`
for `pairing34`.  The result is a classical BV/curved-operator statement.  No
advanced or retarded inverse, causal support theorem, Hadamard state, or
Lorentzian QME follows from it.

Reproduce the pinned import with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.curved_witness_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_curved_witness_import.py -v
```

## Verification receipt

| Rail | Elapsed | Result |
|---|---:|---|
| Readiness certificate regeneration and independent `--check` | 11.66 s (`--check`) | PASS |
| Six scoped exact unit/mutation tests | 41.76 s | PASS |
| Readiness certificate under AJV Draft 2020-12 strict mode | 2.80 s | PASS |
| Future export schema compilation under AJV Draft 2020-12 strict mode | 1.45 s | PASS |
| Pinned authoritative import replay and three import/provenance tests | 26.84 s | PASS |
| Six adapter primitive/obstruction/mutation tests after landing | 34.99 s | 5 PASS, 1 stale-receipt failure before regeneration |
| Final combined adapter/import rail (9 tests) | 61.55 s | PASS |

The unit rail covers exact companion transport, reconstructed unary
nilpotency, an exact-zero primitive branch, a nonzero normalized obstruction
branch with named field content, a forged operator hash, and a mutated
coordinate transport. The initially reported stale-receipt failure was the
expected consequence of changing this content-addressed report; the readiness
receipt was regenerated before the final check. Tier 2 is the pinned import
and full scientific replay recorded by the new certificate. Tier 3 was not
run: this promotes one affected classical BV input gate, not a quantum
lifecycle state, Lorentzian causal theorem, freeze, or release.
