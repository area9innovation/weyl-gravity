# Berger finite nested time convolution

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The public `evaluate_nested_green_time_convolution_interval` callable composes
any nonempty list of supplied polynomial interval Green-kernel enclosures on a
finite rational time slab.  Retarded time uses `x=t-t_left`; advanced time uses
`x=t_right-t`.  Every coefficient follows from the exact beta integral, and a
uniform rational remainder is propagated at every stage.

The two-stage exact fixture gives `x^3/3+x^4/12`.  A fixture with nonzero
source and kernel remainders gives the rigorous upper bound `61/200`.

This closes a causal polynomial convolution engine, not the physical binding
of the actual Berger Maxwell/massive kernels, switches, detector coefficients
or form-block contractions.  It therefore does not yet construct an
`I_abc[two_j,k]` interval or satisfy the complete nested-convolution readiness
row.
