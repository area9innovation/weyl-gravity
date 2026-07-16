# Berger Hadamard construction gate

The repaired causal v2 chain supplies advanced and retarded Green homotopies
on all 54 gauge-fixed rows. Their difference supplies the causal-commutator
infrastructure. It does **not** select a two-point function or a quantum state.

Two existing state-side inputs are useful but remain deliberately weaker:

- the positive-frequency ledger is a `D`-finite, `SO(4)`-finite reduced-mode
  polarization;
- the one-particle ledger identifies an infinite-index Krein structure, but
  explicitly is not a distributional completion.

The construction gate therefore keeps every Hadamard and quantum flag false
and records the shortest certified route:

1. construct rough-wave and ghost-wave Hadamard parametrices;
2. transport them through the typed companion/Volterra Møller maps;
3. verify the left and right BRST Ward identities on the retained 26 rows;
4. lift through the support-local cyclic contraction to all 54 rows;
5. add a smooth zero-mode completion and state the covariant Krein/positivity
   policy;
6. certify bisolution, graded CCR, hermiticity, wavefront set, stationarity,
   row coverage and both BRST identities.

The next analytic object is therefore
`BERGER_BASE_WAVE_HADAMARD_PARAMETRIX`, not a QME or anomaly coefficient.
This entire gate is preflight: no 54-row distributional covariance, Hadamard
wavefront theorem, renormalized product or Lorentzian quantum result is
claimed.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_hadamard_construction_gate_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_hadamard_construction_gate.py -v
```
