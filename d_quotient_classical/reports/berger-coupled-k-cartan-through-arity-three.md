# Coupled Berger K-Cartan contraction through arity three

The theorem concerns the background stabilizer
`K_Berger=D-omega R`.  It does not concern raw cylinder `D`, whose action on
fluctuations has a nonzero zeroth Taylor component.

Write `delta=[q1,-]`.  The certified 64-row causal homotopy satisfies
`[q1,Lambda_64]=1` and commutes with `K`.  Hence cyclic completion of
`Lambda_64 K` gives the unary primitive

```text
[q1,iota_K^(1)] = K.
```

At arity two the source is

```text
A_K^(2)=[q2,iota_K^(1)]-L_K^(2),   L_K^(2)=0.
```

Its differential is `-[q2,K]`, which vanishes coefficientwise on all 64
rows by the imported action-derived K-derivation identity.  Applying the
causal homotopy and the tensorized `Cyc_3` Reynolds projector therefore gives
a cyclic primitive `iota_K^(2)`.

At arity three,

```text
A_K^(3)=[q3,iota_K^(1)]+[q2,iota_K^(2)]-L_K^(3),   L_K^(3)=0.
```

The exact arity-three L-infinity identity reduces its differential to two
Jacobi channels with normalized coefficients `-1/2+1/2=0`; the remaining
channel is `[K,q3]=0`.  Thus `-Cyc_4 Lambda_64 A_K^(3)` is the required
cyclic ternary primitive.  The typed odd pairings and the tensorized C3/C4
group laws are audited on all 64 full rows and all 36 retained rows.

## Retained transfer

The typed cyclic 64-to-36 SDR intertwines K.  Standard finite rooted-tree
homological transfer therefore sends both the L-infinity operations and the
Cartan homotopy to the retained carrier.  The new Maxwell-mixed coefficients
are explicit: retained mixed ell2 has 1,474 terms and retained mixed ell3 has
25,950 contact terms.  For ell3, the only nonzero raw exchange lies in the
contractible full row 38 and is annihilated by projection, so the explicit
mixed export agrees with the transferred operation.

Local Taylor operations do not enlarge support.  The unary Green homotopies
remain same-sided; cyclic completion of higher primitives gives the stated
two-sided causal-hull bound.  No separately retarded higher cyclic primitive
is claimed.  Raw affine D, arity four, all-orders convergence, Hadamard
products, the QME, anomaly cancellation, and quantum claims remain open.
