# Conformal-cylinder Jacobi certificates

This note records the lightweight algebraic certificates implemented in
`symbolic/verify_conformal_jacobi_factorization.py`.  Their inputs are the
exact curved-cylinder densities independently computed by
`symbolic/verify_conformal_aal_vertex.py`; the script does not repeat that
large curvature expansion.

## Convention

SymPy's `jacobi(k, alpha, beta, x)` uses the weight

```text
(1-x)^alpha (1+x)^beta,       -1 < x < 1.
```

For `x=2u-1`,

```text
(1-x)^alpha (1+x)^beta dx
 =2^(alpha+beta+1) (1-u)^alpha u^beta du.
```

After removing this irrelevant positive constant, the shifted weight is

```text
u^beta (1-u)^alpha,           0 < u < 1.
```

This parameter order matters below.

## AAL

Set

```text
n1=2J1,  n2=2J2,  N=n1+n2=2S,
u=t^2/(1+t^2),
du/dt=2t/(1+t^2)^2.
```

The C1b curvature runs found

```text
D_AAL(t)=C t[(N-2)t^2-1]/(1+t^2)^(N-1),
I_AAL(t)=2D_AAL(t)/(1+t^2).
```

Here `D` is the coordinate density before `d beta`, while `I(t)dt` is the
measured radial differential.  The exact change of variables gives

```text
I_AAL(t)dt
 = C (1-u)^(N-3)[(N-1)u-1]du
 = C (1-u)^(N-3) P_1^(N-3,0)(2u-1)du.
```

The quotient by the beta weight and Jacobi polynomial is exactly `C` and is
independent of `u`.  Equivalently,

```text
I_AAL(t)dt=d[-C u(1-u)^(N-2)]
           =d[-C t^2/(1+t^2)^(N-1)].
```

For physical vector harmonics `n1,n2>=2`, the primitive vanishes at both
endpoints.  Jacobi orthogonality can also be checked directly from the two
beta moments

```text
C[(N-1) B(2,N-2)-B(1,N-2)]=0.
```

This is a symbolic all-spin proof of the **Jacobi implication**: any AAL
curvature density having the displayed C1b form integrates to zero.  It is
not yet a derivation that the full Weyl curvature density has that form for
arbitrary `(J1,J2)`.  The proposed normalization

```text
C_J1,J2=64(2J1+1)(2J2+1)(S-1)a_J1 a_J2 l_S
```

is verified against all four computed curvature certificates, but remains a
four-case fit until the general harmonic recurrence proof is supplied.
Moreover, the curvature certificates are oscillator/mode-representative
coefficients.  Their promotion to physical BRST matrix elements remains
conditional on the auxiliary/canonical descent and the compact
conformal-Killing reducibility/global-charge audit.

## EAA in both directions

The independently assembled `E2 A3 -> A5` and `A5 -> E2 A3` curvature runs
both give

```text
K=sqrt(21)/(160 pi^3),
D_EAA(t)=K t(3t^2-1)/(1+t^2)^4,
I_EAA(t)=2D_EAA(t)/(1+t^2).
```

The normalized harmonic overlap is nevertheless nonzero:

```text
int_S3 A5^* E2 A3=-1/(2 pi).
```

Under the same variable change,

```text
I_EAA(t)dt
 =K(1-u)^2(4u-1)du
 =K(1-u)^2 P_1^(2,0)(2u-1)du
 =d[-K u(1-u)^3].
```

Thus EAA is not a contiguous-relation variant: it is exactly the same
degree-one shifted-Jacobi orthogonality mechanism, with `(alpha,beta)=(2,0)`.
Both primitives vanish at `u=0,1`, and both directed integrated coefficients
vanish separately.  Consequently, in the ordered channel basis
`(|E2 A3>,|A5>)`,

```text
V_EAA=0,
J_EAA=-I_2,
J_EAA V_EAA-V_EAA^dagger J_EAA=0.
```

The `J` form plays no role in producing the zero; it only verifies the
resulting adjoint source after the two dynamical coefficients have vanished.

## Reproduction

```bash
python3 symbolic/verify_conformal_jacobi_factorization.py
```

Expected final line:

```text
CONFORMAL JACOBI FACTORIZATION: ALL PASS
```
