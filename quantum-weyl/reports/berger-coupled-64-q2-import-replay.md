# Coupled 64-row Berger (q_2): quantum import and replay

Dependency tag: `LOCAL-ALGEBRAIC`.

The quantum consumer pins classical commit
`456092fea92fe9507bb5de8776795a8abd748870` and imports the complete
gravity--clock--Maxwell binary BV operation without executing the classical
producer. The Maxwell payload is a 1,954-term sparse overlay on the already
replayed 150,305-term gravity payload, giving 152,259 exact coefficients in
`Q(sqrt(10))` on 64 rows.

The consumer independently checks both classical schemas, artifact and
composition hashes, all row hashes, strict PBW order, cohomological degree,
graded Koszul symmetry, support statistics, and the gravity-base seam.

The corrected export imports the pinned generator-conjugation audit: the
frozen dressed-complex generator is
(K_Berger=D-omega R). On the Maxwell rows it is represented by (e0), all
coefficients are constant, and `[e0,ea]=0`; the consumer thus replays the
(K_Berger)-derivation on all 1,954 overlay terms coefficientwise. Raw cylinder
(D) is affine with a nonzero zero-arity component. Raw-(D) equivariance and
Cartan flags remain false.

## Minimal missing-carrier theorem

The export does not contain a portable 64-row unary operator or cyclic
pairing. Therefore the quantum consumer cannot independently replay
`[q1,q2]=0` or BV cyclicity; producer-side booleans are not promoted. The
Maxwell unary contraction is also absent, so the first transferred mixed
vertex cannot yet be formed. The minimal requested exports are:

```text
BERGER_PORTABLE_64_ROW_UNARY_Q1
BERGER_PORTABLE_64_ROW_CYCLIC_PAIRING
BERGER_MAXWELL_UNARY_CONTRACTION
```

This is a classical BV import receipt. It is not a quantum correction,
restored QME, anomaly coefficient, causal result, or Hadamard theorem.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_64_q2_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_64_q2_import
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_64_q2_import.py -v
```

Tier-1 receipts on 2026-07-17: certificate check `PASS` in 0.55 s,
independent verifier `PASS` in 0.55 s, and six focused tests `PASS` in 0.58 s.
The shared Draft 2020-12 validation rail passed for this and the relative
readiness certificate in 0.12 s. Tier 2 was unnecessary because the unchanged
150,305-term gravity base and 1,954-term overlay are content-addressed and the
consumer replays every changed semantic check. Tier 3 was not run because no
freeze, shared-core change, release, or quantum lifecycle promotion occurred.
