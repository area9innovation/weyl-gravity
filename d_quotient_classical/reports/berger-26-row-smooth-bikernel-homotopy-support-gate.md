# Retained-26 smooth-bikernel homotopy support gate

The certified advanced/retarded homotopies extend continuously in one kernel
variable to the standard past-compact, future-compact and time-compact smooth
LF spaces.  On these domains the same-sided support estimates,

```text
q26 Lambda26,+/- + Lambda26,+/- q26 = I,
```

smoothness and the graded advanced/retarded adjoint reversal all persist.

They do not extend by continuity to the full smooth compact-open Frechet
space.  Let `h` be a nonzero homogeneous solution and move a temporal cutoff
to past infinity.  Then

```text
f_n=P26(chi_n h) -> 0,
G26,+ f_n=chi_n h -> h != 0.
```

The advanced case follows by moving the reversed cutoff to future infinity.
This is a support/topology obstruction to the certified factorization
`Lambda26,+/-=W26 G26,+/-`, not a no-go for a different noncausal homotopy or
a directly equivariant Hadamard selection.

The imported Ward certificate exports only
`C26=[H26_plus,q26] is smooth`.  It supplies no past-, future- or
time-compact support statement in either variable, no harmonic support of the
smooth remainder and no serialized kernel.  Consequently `C26` is known to
belong only to the full smooth class where the factorized extension is
obstructed; membership in every positive one-sided domain is undecided.

CURRENT GATE: BLOCKED — require `C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER`
EVIDENCE: BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1
