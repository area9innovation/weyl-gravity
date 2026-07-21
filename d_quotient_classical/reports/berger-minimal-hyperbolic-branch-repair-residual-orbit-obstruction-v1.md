# Minimal hyperbolic branch repair: residual-orbit obstruction

The certified rank-one first-page branch defect can be cancelled at one
chosen null fibre by adjoining one real degree-zero direction and its cyclic
degree-one dual.  That two-row hyperbolic page completion is not a global
Berger-residual object.

In the certified plus/cross frame the rotational little-group generator is

```text
J = [[0, 2], [-2, 0]],   J^2 = -4 I.
```

The page boundary sends the proposed new field to the normalized plus class.
A one-dimensional real representation of connected `SO(2)` is trivial, so
the equivariance defect is `J beta_plus = -2 beta_cross`.  The functional
`(-1/2) coefficient_of(beta_cross)` evaluates it to one and annihilates the
complete real two-row ansatz.  Complexifying produces the two helicity lines,
but reality exchanges them and restores a two-dimensional real field space.

The exact tensor calculation gives the stronger statement in the declared
finite-free support-local tensor-row category.  In
the spatial STF2 basis `(h12,h13,h23,h11-h22,h11+h22-2h33)`, the three
rotation generators obey the `so(3)` relations, have Casimir `-6 I_5`, and
the orbit of the plus class has rank five.  Their commutant is one-dimensional,
so a zero-order equivariant page coupling is a scalar multiple of the STF2
identity; normalization fixes that scalar.  Cyclicity adds the dual STF2
bundle.  The minimum is therefore four added BV rows at one real null fibre
and ten rows for a global finite-free support-local tensor carrier.  A
separately typed nonfree projective module is outside this row-minimality
claim.

The landed rank-46 STF2 graph has the same ten-row representation content but
is contractible, so its image in the obstruction quotient is zero.  The next
candidate must instead be a noncontractible STF2 or equivalent mixed-bundle
rank-46 carrier.  Later filtered pages, q2/q3, and retained-ell3 compatibility
are not activated because the proposed two-row carrier fails the earlier
residual-equivariance gate.

EVIDENCE: d_quotient_classical/certificates/BERGER_MINIMAL_HYPERBOLIC_BRANCH_REPAIR_RESIDUAL_ORBIT_OBSTRUCTION_V1.json
CLOSE-OUT: OBSTRUCTED — the two-row page repair is not real residual-equivariant and forces a noncontractible STF2 orbit closure with ten added BV rows
