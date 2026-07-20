# Berger temporal-cutoff companion Green family

The generic typed biwave Volterra theorem already allows smooth time-dependent
coefficients.  It therefore applies to the Berger interpolation

\[
A_\chi=\Box_2^2+\chi(t)V_2,
\qquad
C_\chi=
\begin{pmatrix}
\Box_2&-I\\
\chi(t)V_2&\Box_2
\end{pmatrix},
\]

where \(\chi=0\) on a past Cauchy neighborhood, \(\chi=1\) on a future
Cauchy neighborhood, and \(d\chi\) has temporally compact support.  Smooth
multiplication preserves the finite-slab Sobolev graph-domain bound for the
order-at-most-two operator \(V_2\).

The pinned theorem consequently supplies, for every such cutoff:

- global advanced and retarded Green operators for \(C_\chi\) and \(A_\chi\);
- both source- and solution-side inverse identities;
- causal support;
- nested-slab globalization;
- formal-adjoint causal reversal.

The past endpoint is the free companion

\[
C_{\rm free}=\begin{pmatrix}\Box_2&-I\\0&\Box_2\end{pmatrix},
\]

whose principal symbol is scalar normally hyperbolic.  The future endpoint is
the full Berger companion.  Thus the formerly requested classical cutoff
Green family is already a consequence of certified infrastructure; no new
stationary theorem is needed.

This does not yet transport a Hadamard state.  The missing analytic statement
is now the wavefront theorem through the compact transition slab: prove a
factorwise null kernel bound and opposite-orientation decomposition for
\(C_\chi\), or directly prove the cutoff response map is regular and has the
required cone action.  A global seed covariance with explicit BV/Krein and
physical-positivity policy is independently open, followed by the BRST Ward
identity.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_temporal_cutoff_companion_green_family_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_temporal_cutoff_companion_green_family
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_temporal_cutoff_companion_green_family.py -v
```

Tier receipt:
[`BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY_V1_TIER_RECEIPT.json`](../lorentzian/receipts/BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY_V1_TIER_RECEIPT.json).
