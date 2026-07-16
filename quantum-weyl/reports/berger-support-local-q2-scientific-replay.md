# Complete Berger support-local q2 scientific replay

Dependency tag: `LOCAL-ALGEBRAIC`.

The quantum consumer independently replays the landed 54-row classical
operation at commit `7b352307eb2adb0dfb8e76b7d24f0bb94a37cc8d`. The input
contains 150,305 exact PBW coefficients over `Q(sqrt(10))`, on 39 nonzero
output rows, through total jet order six.

The symbolic readiness engine was not suitable for the full tensor: repeated
generic simplification caused expression growth inside the million-term
arity-two accumulation. The scientific backend instead represents every
coefficient as the exact pair `(a,b)` for `a+b*sqrt(10)` and implements

```text
(a,b)(c,d) = (ac+10bd, ad+bc).
```

This changes only coefficient representation. Noncommutative Berger PBW
reduction, the bilinear Leibniz rule, Koszul signs, and formal integration by
parts remain explicit.

All three scientific defects vanish coefficientwise:

```text
q1 q2 + q2(q1,-) + (-1)^|x| q2(-,q1) = 0
D q2 - q2(D,-) - q2(-,D) = 0
BV cyclicity defect = 0
```

The cyclic calculation uses the imported odd Darboux matrix, not an ordinary
even-pairing sign. With `dual(b)` read from its primal/dual polarization, the
lowered tensor obeys

```text
T(a,b,c) = (-1)^(dual(b)+parity(a)*parity(b)) T(c,a,b).
```

The complete replay took 65.21 seconds and peaked at 415,344 KiB RSS in the
recorded scientific run. Its phases were approximately 4.40 seconds parsing,
21.80 seconds for `q1/q2`, 10.80 seconds for `D/q2`, and 22.68 seconds for
cyclicity.

This closes the classical q2 scientific replay gate only. The transferred
bracket `ell2`, the prerequisite full four-dimensional unary `D`-Cartan
existence problem, the later arity-two primitive or obstruction,
causal/Hadamard data, QME restoration, and quantum corrections remain
uncomputed. The unary-before-binary order is fixed by
`BERGER_FULL_4D_D_CARTAN_GATE`.

Routine receipt validation is deliberately fast: it verifies the pinned input,
source manifest, result structure, and exact zero-defect hashes without
replaying the 150,305-term accumulation. Re-run the scientific calculation
explicitly when the replay implementation or a pinned input changes.

Fast affected checks:

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_support_local_q2_replay_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_support_local_q2_scientific_replay.py -v
```

Full exact replay (about 66 seconds on the recorded machine):

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_support_local_q2_replay_certificate --replay-check
```
