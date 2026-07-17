# Berger generator conjugation audit

With

```text
R(T1,T2)=(-T2,T1),
T=exp(omega t R)((rho,0)+psi),
K=D-omega R,
```

exact differentiation gives

```text
exp(-omega t R) D T = partial_t psi + omega R psi + omega R(rho,0),
exp(-omega t R) K T = partial_t psi.
```

Thus the frozen all-row rule `e_0 I_54` represents `K`, whose background is
fixed.  Raw cylinder translation `D` is affine in these coordinates and has
nonzero zero-arity component `(0,omega rho)`.

Result: `BERGER_GENERATOR_CONJUGATION_AUDIT`.  The prior unary-through-ternary certificates
remain exact after being interpreted as a `K`-Cartan theorem.  They do not
construct the affine `D`-Cartan homotopy.
