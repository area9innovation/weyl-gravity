# Berger companion decomposability preflight

The twenty-row companion has principal symbol

\[
\sigma_2(C)=
\begin{pmatrix}
qI_{10}&0\\
\sigma_2(V_2)&qI_{10}
\end{pmatrix},
\qquad \det\sigma_2(C)=q^{20}.
\]

Consequently its characteristic set is exactly the metric null cone. The
typed Volterra certificate also supplies advanced and retarded Green
operators with causal support. These are necessary inputs, but they do not
prove a Hadamard condition.

Fewster's decomposability definition requires the Pauli--Jordan kernel to
satisfy

\[
\operatorname{WF}(E_C)\subset
(\mathcal N^+\times\mathcal N^-)
\cup(\mathcal N^-\times\mathcal N^+).
\]

The sign used for advanced-minus-retarded versus retarded-minus-advanced is
irrelevant to this inclusion, because multiplication by \(-1\) does not
change a wavefront set.

The exact null fixture exposes why the missing inclusion is not automatic.
On \(q=0\),

\[
\sigma_2(C)=
\begin{pmatrix}0&0\\v&0\end{pmatrix},
\qquad \sigma_2(C)^2=0,
\qquad \operatorname{rank}\sigma_2(C)=7.
\]

It is therefore nonzero, nilpotent and non-diagonalizable. The determinant
locates the characteristic covectors, but does not determine propagation of
the seven singular polarizations. In particular, neither causal support nor
convergence in finite-slab Sobolev norms fixes the orientation of the kernel
wavefront set.

The smallest missing carrier is now named:

```text
BERGER_COMPANION_PAULI_JORDAN_WAVEFRONT_THEOREM
```

It must construct the Schwartz kernel of \(E_C\) and prove the displayed
wavefront inclusion. Acceptable routes are a uniform Hörmander-topology
estimate for the Volterra series, a propagation/polarization theorem for the
nilpotent companion symbol, or a regular Green-hyperbolic transport theorem
whose kernel relation preserves the base null decomposition.

This preflight certifies the null characteristic cone and the exact Jordan
obstruction. It does not certify decomposability, a companion Hadamard
parametrix or state, BRST Hadamard data, a QME, or a quantum result.

Primary scope references:

- [Fewster, *Hadamard states for decomposable Green-hyperbolic operators*](https://arxiv.org/abs/2503.12537), Definition 5.2.
- [Dappiaggi--Drago, *Constructing Hadamard states via an extended Møller operator*](https://arxiv.org/abs/1506.09122), whose direct perturbation is a smooth order-zero potential rather than the present order-two \(V_2\).

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_companion_decomposability_preflight_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_companion_decomposability_preflight
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_companion_decomposability_preflight.py -v
```
