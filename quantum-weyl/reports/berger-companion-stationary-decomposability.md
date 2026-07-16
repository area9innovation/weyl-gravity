# Berger companion stationary decomposability

The previous preflight certifies a Pauli--Jordan Schwartz kernel satisfying

\[
\operatorname{WF}(E_C)\subset
(\mathcal N^+\cup\mathcal N^-)
\times
(\mathcal N^+\cup\mathcal N^-).
\]

The Berger background, rough wave, \(V_2\), and order-zero Volterra coupling
are stationary. If \(U_s\) denotes global Berger time translation, then

\[
U_s C=C U_s.
\]

Conjugating an advanced or retarded Green operator by \(U_s\) preserves both
inverse identities and the corresponding causal support. Global same-sided
uniqueness therefore gives

\[
U_sG_C^\pm=G_C^\pm U_s.
\]

The Pauli--Jordan kernel is consequently invariant under simultaneous time
translation of both variables. Infinitesimally,

\[
(\mathcal L_{e_0,x}+\mathcal L_{e_0,x'})E_C=0.
\]

The scalar principal symbol of this first-order equation is
\(\tau+\tau'\). Kernel elliptic regularity implies

\[
\operatorname{WF}(E_C)\subset\{\tau+\tau'=0\}.
\]

Every nonzero null covector has nonzero time component. Therefore the two
null covectors in every wavefront pair have opposite time orientation, and

\[
\boxed{
\operatorname{WF}(E_C)\subset
(\mathcal N^+\times\mathcal N^-)
\cup
(\mathcal N^-\times\mathcal N^+)
}.
\]

Thus the retained twenty-row companion is null-cone decomposable in the
sense of Fewster's Definition 5.2.

This is not yet a Hadamard state. Decomposability constrains the causal
propagator; the next gate must construct a positive-frequency two-point
function with the required antisymmetric part, equation identities,
stationarity, and the project-specific Krein/BRST policy.

Primary scope reference:
[Fewster, *Hadamard states for decomposable Green-hyperbolic operators*](https://arxiv.org/abs/2503.12537).

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_companion_stationary_decomposability_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_companion_stationary_decomposability
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_companion_stationary_decomposability.py -v
```
