# Exceptional polar `ell=0` nonzero-Fourier target

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exceptional target was derived directly from the four-dimensional
Weyl--Maxwell equations on the fixed magnetic bundle.  The fields are
`(A,B,C,K,T,X)`, where `(T,X)` is the global difference of two bundle
connections.  No generic `ell>=2` master operator was specialized.

After the action row normalization, the Fourier Hessian factorizes as

```text
H = (1/2) v_g v_g^T direct-sum v_A v_A^T,
v_g = (k^2,2k omega,omega^2,k^2-omega^2),
v_A = (k,omega).
```

For every real `(omega,k)!=(0,0)`, this has rank two.  The two diffeomorphism
columns, Weyl column, and `U(1)` column have rank four and exhaust the kernel.
Formal self-adjointness therefore makes the left cokernel exactly the adjoint
gauge/Noether space.

At the phase-sensitive static channel `omega=0`, `k=+/-2k_input`, a compatible
action source obeys

```text
S_B=S_C=S_X=0,  S_A=S_K.
```

For the second-order sign convention `L Phi^(2)=-S`, one correction is

```text
A=K=-S_A/k^4,  T=-S_T/k^2,  B=C=X=0.
```

Hence this channel has no physical Taub obstruction.  The statement is about
smooth global second-order solvability; it does not imply boundedness on a
nonzero-frequency resonant shell.

## Verification

The producer directly repeats the curvature calculation.  The independent
verifier checks hashes, schema, gauge identities, formal self-adjointness,
rank factorization, the static kernel, and the displayed right inverse.
