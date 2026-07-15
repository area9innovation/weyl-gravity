# Authoritative retained Berger minimal-BV layout

The minimal clock SDR leaves exactly four bundle rows:

| degree | bundle | rank |
|---:|---|---:|
| -1 | spatial diffeomorphism ghost | 3 |
| 0 | dressed symmetric metric | 10 |
| 1 | dressed metric antifield | 10 |
| 2 | spatial ghost antifield / identity row | 3 |

The certificate fixes all 26 component IDs, their orthonormal-frame ordering,
dual involution, complex degrees, parity, and canonical cyclic pairing.  The
only allowed nonzero retained $q_1$ blocks are

\[
K_{\rm spatial},\qquad H_{\rm retained},\qquad -K_{\rm spatial}^{\sharp},
\]

of maximum differential orders $1,4,1$, respectively.  Their coefficients
are deliberately not supplied by this layout theorem.

The next two gates are separate:

```text
BERGER_RETAINED_MINIMAL_OPERATOR
BERGER_NONMINIMAL_COMPLETION
```

The first must derive the complete retained coefficients from the actual
coupled action and verify the Noether, adjoint, nilpotency, cyclicity, and
34-to-26-plus-8 decomposition identities.  Only after it passes may the
second gate add antighost, multiplier, and gauge-fixing rows.

The stable IDs and $q_1$ layout may be reused by the nonlinear classical
export, but this certificate contains neither $q_1$ coefficients nor
$q_2$, so it does not satisfy `CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT`.
