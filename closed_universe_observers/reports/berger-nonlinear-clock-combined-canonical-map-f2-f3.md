# Combined radial-temporal Berger clock canonical map through F3

The combined chart is fixed by one geometric formula, not by juxtaposing the separately certified submaps:

```text
y0=x0+Theta(x),  yi=xi,
gHat(y)=K^T (1+R(x(y)))^2 [eta+H-2R eta-B(Theta)](x(y)) K,
R_true(y)=R(x(y)).
```

Its field Taylor map has zero linear defect, 55 `F2` and 174 `F3` entries. Setting `Theta=0` reproduces the radial certificate, while setting `R=0` reproduces the temporal certificate. Five quadratic and 64 cubic mixed radial-temporal monomials are required.

The full Frechet Jacobian is lifted by signed formal adjunction in the noncommuting Berger PBW algebra. The adjoints are involutive and the canonical one-form inverse vanishes through cubic degree. All field and cotangent tensors reconstruct exactly from their factorial payloads.

This authorizes regeneration of scalar apparatus `q2/q3`; it does not certify those interactions or any downstream observer gate.
