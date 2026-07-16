# Berger companion Pauli--Jordan characteristic preflight

The repaired Volterra theorem converges in operator norm at every Sobolev
order on every finite slab. Smooth compactly supported sources therefore
produce smooth solutions continuously, and the compatible slab operators
glue globally. The Schwartz kernel theorem supplies distribution kernels for
both causal Green operators and hence for

\[
E_C=G_C^{\mathrm{adv}}-G_C^{\mathrm{ret}}.
\]

The two-sided inverse identities cancel in the difference:

\[
C E_C=0,
\qquad
E_C C=0.
\]

In kernel notation the second equation is the formal-adjoint equation in the
second variable. Because both the operator and its transpose map test
sections to smooth sections, the kernel has no wavefront component with only
one nonzero cotangent entry.

Kernel elliptic regularity now applies in both variables. The companion and
its formal adjoint have determinant \(q^{20}\), so

\[
\operatorname{WF}(E_C)\subset
(\mathcal N^+\cup\mathcal N^-)
\times
(\mathcal N^+\cup\mathcal N^-).
\]

This is stronger than causal support and weaker than decomposability. It
allows four orientation sectors, while Fewster decomposability permits only

\[
(\mathcal N^+\times\mathcal N^-)
\cup
(\mathcal N^-\times\mathcal N^+).
\]

The entire remaining gap is therefore

\[
\operatorname{WF}(E_C)\cap
\bigl((\mathcal N^+\times\mathcal N^+)
\cup(\mathcal N^-\times\mathcal N^-)\bigr)=\varnothing.
\]

The next result is named

```text
BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION
```

and may be proved by a common Hörmander-cone estimate for the same-sided
Volterra series, propagation from the diagonal causal normalization, or a
regular Green-hyperbolic transport with an explicit kernel relation.

This certificate does not claim that exclusion, decomposability, a Hadamard
state, BRST compatibility, a QME, or a quantum result.

Primary scope reference:
[Fewster, *Hadamard states for decomposable Green-hyperbolic operators*](https://arxiv.org/abs/2503.12537), Definition 5.2 and the characteristic-set observation following it.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_companion_pauli_jordan_characteristic_preflight_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_companion_pauli_jordan_characteristic_preflight
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_companion_pauli_jordan_characteristic_preflight.py -v
```
