# Berger cutoff companion Hermitian dilation

The non-Hermitian metric companion now has a canonical auxiliary analytic
carrier.  If \(C\) is the real Green-hyperbolic companion and \(C^\dagger\)
its formal adjoint, define

\[
\widetilde C=\operatorname{diag}(C,C^\dagger),
\qquad
H=\begin{pmatrix}0&I\\ I&0\end{pmatrix}.
\]

The fibre form \(H\) is nondegenerate, indefinite and Hermitian, and

\[
H^{-1}\widetilde C^{\dagger_0}H=\widetilde C.
\]

Together with the componentwise real structure and block-diagonal causal
Green operators, this makes the free, cutoff and full dilations real formally
Hermitian Green-hyperbolic operators.

The free and cutoff dilations agree on a past Cauchy neighbourhood; the cutoff
and full dilations agree on a future Cauchy neighbourhood.  Fewster Theorem
3.5(e) therefore supplies two Cauchy GreenHyp morphism legs, and Lemma 5.15(c)
makes each regular.

This dilation is an auxiliary indefinite metric-sector carrier.  It does not
prove that the raw companion is formally Hermitian, identify the doubled and
undoubled quantum theories, or supply the full graded BV realization.  The
cone action of the regular morphisms, same-orientation wavefront exclusion and
a global seed covariance remain open before Hadamard transport.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_cutoff_companion_hermitian_dilation_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_cutoff_companion_hermitian_dilation
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_cutoff_companion_hermitian_dilation.py -v
```

Tier receipt:
[`BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION_V1_TIER_RECEIPT.json`](../lorentzian/receipts/BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION_V1_TIER_RECEIPT.json).
