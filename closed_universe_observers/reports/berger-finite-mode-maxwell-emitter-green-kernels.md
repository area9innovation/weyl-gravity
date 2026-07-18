# Finite-mode Maxwell and emitter Green kernels

For every exact Peter--Weyl spatial block `A`, define

```text
S_A(tau)=sum_(n>=0) (-A)^n tau^(2n+1)/(2n+1)!
        =sin(tau sqrt(A))/sqrt(A).
```

The definition includes the massless zero-eigenvalue limit `S_0=tau` and
requires no numerical diagonalization.  `H(t-s)S_A(t-s)` and
`H(s-t)S_A(s-t)` give the finite-mode retarded and advanced kernels.
Maxwell uses the spatial `Delta_0,Delta_1` blocks; the massive two-form uses
`Delta_1+m_b^2,Delta_2+m_b^2`, followed by the certified Proca correction.

The Cauchy jump and wave equation are exact through the audited series orders.
A finite spectral truncation is not support-local.  Full causal support and
the recoil coefficient still require the complete profile expansion and a
validated infinite-mode tail.
