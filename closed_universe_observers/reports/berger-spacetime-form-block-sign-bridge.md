# Berger spacetime form-block sign bridge

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

For a spacetime `k`-form written as `dt wedge alpha + beta`, the Lorentzian
product pairing fixes

```text
d(alpha,beta)     = (partial_t beta - dSigma alpha, dSigma beta),
delta(alpha,beta) = (-deltaSigma alpha, partial_t alpha + deltaSigma beta).
```

Substitution of the exact Berger Peter–Weyl de Rham matrices gives zero
`d^2` and `delta^2` defects and

```text
d delta + delta d
  = diag(partial_t^2 + Delta_(k-1), partial_t^2 + Delta_k)
```

for Maxwell one-forms and emitter two-forms through the exact audit rail
`two_j=0,...,4`.  Flipping the temporal coderivative sign is detected.  This
fixes the component convention required by the per-shell recoil word; it does
not yet evaluate that word or any recoil interval.
