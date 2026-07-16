# Berger typed companion Møller preflight

The base Hadamard certificate supplies local parametrices for the normally
hyperbolic tensor-wave factors. The retained metric operator is represented by
the twenty-row filtration

\[
B=\operatorname{diag}(\Box_2,\Box_2),\qquad
C_0=B+\begin{pmatrix}0&0\\V_2&0\end{pmatrix},\qquad
C=C_0+\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

The first triangular perturbation has square-zero Green incidence. Therefore
its source and solution maps are finite:

\[
T_{\rm sol}=I-G_{\rm diag}V,qquad
T_{\rm src}=I-VG_{\rm diag}.
\]

The exact noncommutative replay verifies

\[
C_0T_{\rm sol}=B,qquad T_{\rm src}C_0=B.
\]

Composing these maps with the separately typed Volterra resolvents gives

\[
M_{\rm sol}=R_{\rm sol}T_{\rm sol},\qquad
M_{\rm src}=T_{\rm src}R_{\rm src},
\]

and hence

\[
CM_{\rm sol}=B,qquad M_{\rm src}C=B.
\]

Formal adjunction reverses the causal side and the operator:

\[
(M_{{\rm sol},C}^{\rm ret})^\sharp
=M_{{\rm src},C^\sharp}^{\rm adv}.
\]

These identities identify the only correctly typed formal kernel candidate,

\[
H^+_{C,{\rm loc}}
=M_{{\rm sol},C}^{\rm ret}H_B^+
 M_{{\rm src},C^\sharp}^{\rm adv}.
\]

This formula is not yet a distribution. The next gate must prove that every
kernel composition is defined in the Hörmander sense, extend the Volterra
series to the required distribution spaces, preserve the (C^+) relation,
preserve smooth equation defects, include the factored ghost biwave, and show
that the (A_{10}) graph pullback is wavefront-safe. Until then no companion
Hadamard parametrix or global state is claimed.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_typed_companion_moller_preflight_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_typed_companion_moller_preflight
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_typed_companion_moller_preflight.py -v
```
