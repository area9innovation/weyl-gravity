# Exceptional polar Einstein--Maxwell complex

Date: 2026-07-16

`COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX` completes the standard polar linear
harmonic quotient on the fixed compact bundle.

For `ell=0`, exact tensor reduction gives no local mode at any nonzero
Fourier block: the Einstein kernel equals the periodic diffeomorphism image,
and Maxwell forces the electric coefficient to zero. The homogeneous
generalized zero block instead obeys

```text
K''=0,  C''=2K,  E'=0,
K=a+bt,  C=at^2+(b/3)t^3+c+dt,  E=Q_e.
```

Thus it retains the radion Jordan pair, the global `S1` circumference pair,
and electric charge. Uniform magnetic variation is absent because `P_N` is
fixed. The certified radion is `a=2`, giving `K=2,C=2t^2`.

For `ell=1`, the tracefree tensor harmonic vanishes. After fixing `h_A=0`,
the remaining smooth gauge vector is

```text
(2omega^2,-2komega,2k^2,-2,-1).
```

The invariant master is `Psi=U-K/2`. Algebraic gauge `K=0` is complete and
leaves

```text
(A,B,C,U)=(-2Psi,0,2Psi,Psi),
omega^2=k_n^2+4.
```

The apparent `s=0` branch is exactly gauge, with no global exception. By
`SO(3)` equivariance the physical mode is an `ell=1` triplet.

This finishes all polar `ell` at the linear reduced-mode level. Covariant
symplectic normalization, physical norm signs, and the extra fourth-order
adjoint blocks remain open.

Generator verification passed in `5.42 s`, the independent verifier in
`0.43 s`, and the nine-test suite in `5.31 s`. Tier 3 is not triggered because
symplectic and adjoint promotion gates remain open.
