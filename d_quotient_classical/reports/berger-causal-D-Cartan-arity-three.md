# Causal cyclic Berger D-Cartan contraction through arity three

The complete 54-row result now closes the classical Cartan recurrence through
the first genuinely ternary stage.  With the cyclic unary and binary
primitives from the lower theorem, define

```text
A_D^(3) = [q3,iota_D,cyc^(1)] + [q2,iota_D,cyc^(2)] - L_D^(3).
```

The frozen action-derived export has `L_D^(3)=0`, satisfies the exact
arity-three L-infinity identity, and is a local D-derivation.  Applying the
cochain differential to `A_D^(3)` leaves two channels.  Their normalized
coefficients are `-1/2+1/2=0` by graded Jacobi, while the other vanishes by
`[D,q3]=0`.  Thus the complete source is closed without fitting or a mode
restriction.

The source is cyclic because cyclic coderivations are closed under their
graded bracket.  A raw causal primitive is

```text
R^(3) = -Lambda54,+ A_D^(3).
```

Tensoring its output with the frozen odd Darboux pairing gives a four-linear
tensor.  On that tensor—not on raw map coordinates—the correct cyclic
projection is

```text
Cyc_4 = (I+tau+tau^2+tau^3)/4.
```

The pairing audit checks all 54 rows, dual degrees and reverse orientations.
The C4 group law is exhausted over the actual degree classes, covering
978,736 admissible degree-zero row quartets with no defect.  Exact arithmetic
in `Q[C4]/(tau^4-1)` proves that `Cyc_4` is idempotent, commutes with the
cochain differential and fixes the cyclic source.  Therefore

```text
iota_D,cyc^(3) = Cyc_4 R^(3),
delta iota_D,cyc^(3) = -A_D^(3).
```

This is a full arbitrary-input four-dimensional classical result.  Its
support statement is deliberately precise: the local Taylor coefficients do
not enlarge support, while cyclic adjoint completion places the primitive in
the two-sided causal hull of the three input supports.  It is not claimed to
be separately retarded or advanced.  Hadamard data, a quantum ND3 theorem,
the QME and any required arity-four recurrence remain downstream gates.
