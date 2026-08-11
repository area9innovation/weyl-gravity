# Exact finite qubit interaction core

`FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1` supplies a deliberately small
local witness for four jobs that were previously represented only indirectly in
the intersection cube: finite observables, states and probabilities, dynamics,
and an actual interaction.  Every check is over Gaussian rationals.  No
floating-point spectral calculation or trigonometric approximation is used.

The carrier is the labelled algebra `M_4(Q(i))`.  The two subsystem observables
are `X tensor 1` and `1 tensor X`, and the interaction Hamiltonian is
`H = Z tensor Z`.  The checker proves that `delta(A)=i[H,A]` is a star
derivation and obeys Leibniz's rule.  It also checks a Bell density matrix,
obtaining the exact probabilities `P(00)=1/2` and `P(even)=1`.

For a nontrivial interaction witness, the checker evolves the product state
`|++><++|` to time `pi/4`.  Instead of approximating `sqrt(2)` or sine and
cosine, it forms the resulting density matrix directly from Gaussian-rational
phase ratios.  The result is a normalized rank-one density matrix whose
one-qubit reduction is exactly `I/2`; hence this particular interaction maps the
displayed product state to an entangled state.

The same finite carrier has the fundamental symmetry
`J=diag(1,1,-1,-1)`.  The checker establishes `J*=J`, `J^2=1`,
`H^sharp=H`, and scaled `J`-unitarity of the displayed time step.  This is a
finite Krein companion, not an infinite Krein completion or a probability rule
for indefinite norm.

## Foundational reading

Because all matrices are explicitly labelled and every loop is finite, the
witness can be formalized with primitive-recursive finite-array arithmetic and
interpreted in ZF without choosing representatives from an arbitrary family.
That is a sufficiency statement for this object.  It is not a reverse-
mathematical lower bound and it does not identify PRA, choice-free ZF, Bishop
constructivism, or finitism.

The combined cube obligation “interactions/renormalization/QME” must be read
narrowly here: the witness supplies the interaction part only.  It establishes
no Weyl vertex, renormalization, anomaly calculation, counterterm
classification, or quantum-master-equation restoration.  It also establishes
no continuum limit or `LORENTZIAN-CAUSAL` result.

## Verification

```text
python3 foundations/check_finite_qubit_interaction_core.py
python3 foundations/verify_finite_qubit_interaction_core.py
python3 -m unittest foundations.tests.test_finite_qubit_interaction_core
```
