# Weyl/Euler current transgression

Date: 2026-07-24  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The literal four-dimensional \(C^2\) current differs from the current of the
Ricci-factorized bulk action by the exact Euler transgression

\[
\omega_{C^2}-\omega_{\rm Ric}=d k_{E_4}.
\]

On linearized Einstein perturbations the Ricci bulk current vanishes.
For the axial Regge--Wheeler representatives the remaining literal current
is exactly a cut derivative,

\[
F^r_{EE}=\partial_t Q_{EE}.
\]

For smooth compact-frequency wave packets with support bounded away from
\(\omega=0\), the cut bilinear is Schwartz in time.  Its values at temporal
infinity vanish, so the integrated Einstein--Einstein flux is zero at every
finite-radius cylinder.  This establishes total isotropy of the Einstein
wave-packet subspace on the declared core.

The result does not set the monochromatic current to zero pointwise.  Null
and horizon limits require the separately declared bounds needed to
interchange the endpoint limit with time integration.  Nothing here makes
the mixed Einstein/additional pairing Euler-exact.

## Verification

```bash
cd black_hole_programme/phase4/weyl_euler_current_transgression_v1
python3 produce.py
python3 verify.py
python3 -m unittest -v test_transgression.py
```

The independent verifier re-derives the Fourier cut identity, checks imported
certificate hashes, and enforces the fail-closed claim flags.  Mutation tests
reject a changed curvature coefficient, a transgression-sign error, a
cut-current-sign error, pointwise-vanishing promotion, unconditional endpoint
interchange, and mixed-pairing promotion.

CLOSE-OUT: DONE — objective met; exact certificate and independent verification are pinned in `black_hole_programme/phase4/weyl_euler_current_transgression_v1/`.
EVIDENCE: `black_hole_programme/phase4/weyl_euler_current_transgression_v1/receipt.json`
