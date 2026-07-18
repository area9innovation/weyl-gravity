# Nariai automorphism cyclic Bach extension

The curvature-corrected automorphism constraint complex has the canonical
odd-cotangent Bach extension.  In eight blocks its total rank is
`288` and its middle is the Hessian of

```text
1/2 <h,B_action h> + <lambda,M^D a-Phi h>.
```

Exact checks:

- abstract `Q^2` modulo the certified coefficient identities: `True`;
- abstract odd cyclicity: `True`;
- coefficient defect `M^D d_aut-Phi K p0`: `0`;
- coefficient defect `B_action K p0`: `0`;
- strict metric graph chain map: `True`;
- metric odd-pairing pullback: `True`.

The result is local and differential.  Cotangent rows are the forced formal
adjoints of the primal rows under the serialized pairings; they were not fit
independently.  No SDR, quasi-isomorphism, or Green homotopy is claimed.

Next gate: `C_G2_NARIAI_AUTOMORPHISM_SUPPORT_LOCAL_SDR`.
