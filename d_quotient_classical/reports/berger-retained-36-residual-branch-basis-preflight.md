# Retained 36-row residual branch-basis preflight

The quantum branch-projection consumer is structurally ready, and the exact
36-row unary differential, typed cyclic pairing, and accepted mixed
`ell3` tensor are available.  The requested V1 manifest nevertheless cannot
be issued against the current input contract.

The contract declares the sole coefficient field `Q(sqrt(10))` while its
claim boundary requires the normalized parity basis

```text
e = (W_+^2 + W_-^2)/sqrt(2)
o = (W_+^2 - W_-^2)/sqrt(2).
```

Exactly, `sqrt(2)` is not in `Q(sqrt(10))`.  If
`sqrt(2)=a+b sqrt(10)` for rational `a,b`, squaring forces `2ab=0` and
`a^2+10b^2=2`; either branch would require a rational square root of `2` or
`1/5`.  SymPy's exact algebraic-field coercion independently rejects the
membership.

The recommended V2 repair keeps operator coefficients in `Q(sqrt(10))` and
declares the deformation normalization over `Q(sqrt(2),sqrt(10))`.  An exact
alternative is the unnormalized parity basis, whose Gram matrix is `2 I2`.
The displayed Gram calculation is a conditional basis-change receipt using a
chiral `I2`; V2 must import the certified chiral pairing and derive this Gram
rather than assume it.

V2 must also type the dynamical and deformation carriers separately, declare
the exact mode/support sector before calling its branch list exhaustive,
replace free-form Maxwell branch names with canonical carrier records, and
specify the complexification and antilinear real structure.  Every map needs
source/target ranks and degrees, its coefficient field, chain identities,
pairing pullback, parity/reality/`K_Berger` intertwining, and a completeness
witness.  Euler--Lagrange and transgression normalizations need pinned
orientation and mutation-tested zero witnesses.

This field repair does not supply the still-missing dynamical projector.  The
retained SDR does not by itself identify Einstein-like, extra-Weyl, and
Maxwell solution branches.  Those carriers and their inclusion/projection,
pairing, parity, real structure, and `K_Berger` weights must be constructed in
a declared dynamical mode or support sector.  Their present absence is not a
nonexistence theorem, and no branch-space `ell3` projection is authorized by
this preflight.
