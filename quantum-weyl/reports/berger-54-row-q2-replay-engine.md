# Berger 54-row q2 exact replay engine

## Outcome

The quantum consumer can now independently replay all three support-local
arity-two identities as soon as the committed classical Berger `q2` arrives:

\[
q_1q_2+q_2(q_1,-)+(-1)^{|x|}q_2(-,q_1)=0,
\]

\[
Dq_2-q_2(D,-)-q_2(-,D)=0,
\]

and graded cyclicity of

\[
T(x,y,z)=\langle q_2(x,y),z\rangle
\]

modulo exact integration by parts. This is tagged `LOCAL-ALGEBRAIC`.

The implementation is independent of the classical q2 producer. It imports
only the already pinned 54-row unary differential, helical `D` action and
cyclic pairing, and records the exact `q1`, `D54`, `iota`, `pi`, `S`, and
pairing hashes in the certificate. Operator composition is performed over

```text
Q(alpha_B,u,v) tensor U(e_Berger)
```

in the ordered PBW basis `e0^n0 e1^n1 e2^n2 e3^n3`, with the Berger frame
commutators encoded and tested on the quantum side.

## Fixture and mutation receipt

The implementation fixture is deliberately non-scientific. It contains the
single degree-compatible field-field-to-equation coefficient

```text
q2[27,5,5] = alpha_B*u/2.
```

All three identities vanish exactly on that fixture. Three sensitivity
branches prove that a final zero is not being returned vacuously:

- changing output row `27 -> 28` creates two localized `q1/q2` defects on
  output row 49;
- the same mutation creates two localized cyclicity defects involving rows
  `(5,5,6)` and `(6,5,5)`;
- changing `D` on row 5 from `e0` to `e1` creates a localized nonzero
  derivation defect on output row 27.

Every defect is emitted as exact PBW exponents and a symbolic coefficient,
with a canonical hash of the complete (possibly sampled) defect ledger.

## Scientific boundary

This work certifies the replay implementation, not the incoming scientific
tensor. The classical team's in-progress q2 producer is neither imported nor
executed. Consequently the following remain false:

```text
CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED
SCIENTIFIC_ARITY_TWO_IDENTITIES_REPLAYED
TRANSFERRED_ELL2_COMPUTED
INTERACTING_CARTAN_VERDICT
QUANTUM_CLAIM
```

When a committed portable tensor passes the arrival adapter, the next action
is one call to `replay_parsed_q2`. A failure will name the exact output/input
rows, left/right PBW words and coefficient rather than returning an opaque
global defect.

## Reproduction

The focused suite is intentionally separate from the slow global suite:

```bash
python3 quantum-weyl/transfer/berger_54_row_q2_replay_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_54_row_q2_replay.py
```

The checked artifact is
`quantum-weyl/transfer/certificates/BERGER_54_ROW_Q2_REPLAY_ENGINE.json`.
