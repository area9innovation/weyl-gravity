# Curved generalized-auxiliary retract

This package isolates what follows exactly from the covariant
ordinary-derivative action from what still depends on reconstructing the
complete curved four-row BV differential.

Proved here:

- the pointwise inverse
  `A_g^{-1}s = -2s + (2/3)g tr_g(s)`;
- the nonlinear completion-of-square shift
  `phi_hat = phi - A_g^{-1}G^b(g,b)`;
- its finite-order tangent transformation;
- the local type-II BV generating functional and its cotangent lift;
- the exact pointwise 36-dimensional generalized-auxiliary contraction after
  the split;
- a single 66-row `FourRowQConjugation` kernel which extracts `i`, `p`, and
  `k` from one supplied differential and verifies every SDR identity;
- an exhaustive row ledger for the four minimal BV rows and the reattached
  pointwise trace/Weyl and nonminimal summands;
- preservation of compact, spacelike-compact, and smooth support by every
  displayed map.

The conjugation kernel is regression-tested against the exact Fourier
complex.  It is ready to consume the canonical-normal-form curved `Q`, but a
Fourier regression is not used as evidence for the curved coefficient
identity.

The action-factorized curved `Q` is now conjugated exactly.  The transformed
operator is the direct sum of the metric BV complex and the three universal
generalized-auxiliary arrows.  Consequently both chain maps,
`ip-1=Qk+kQ`, and every reattached trace/nonminimal row are certified without
waiting for the expanded derivative table needed by the separate wave
operator/globalization theorem.

Accordingly, `curved_deformation_retract` is true. Run

```bash
python3 symbolic/verify_conformal_curved_retract.py --emit --guards
```

to regenerate the focused certificates.
