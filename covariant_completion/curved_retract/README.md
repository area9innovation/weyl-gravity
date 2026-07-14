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
- preservation of compact, spacelike-compact, and smooth support by every
  displayed map.

Not yet proved here:

- conjugation of the fully reconstructed curved `Q` to the split form;
- the curved inclusion and projection chain-map identities;
- `ip-1=Qk+kQ` for that actual curved operator;
- compatibility of every reattached trace and nonminimal curved row.

Accordingly, `curved_deformation_retract` remains false. Run

```bash
python3 symbolic/verify_conformal_curved_retract.py --emit --guards
```

to regenerate the focused certificates. The verifier deliberately refuses
`--claim-curved-deformation-retract`.
