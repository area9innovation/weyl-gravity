# High-mode scalar interval-stability preflight

The first omitted form shell shows that `two_j=138` is not a converged input
cutoff.  Simply widening the existing independent-moment expansion is not a
stable successor.  Its central external-clock `s^0` coefficient is still
narrowly enclosed at scalar `two_j=140`, but at `two_j=256` the raw interval
has width greater than `6e8` because correlated cancellations were discarded.

The exact normalized-unitary bound intersects that interval with `[-1,1]`.
This restores a true enclosure but supplies no high-mode decay, so it cannot
close an infinite tail.  The physical-space alternative also remains open
because the repository has no validated Berger hyperbolic PDE solver.

The next gate is therefore a correlated direct oscillatory quadrature or
stable recurrence with pointwise unitary control.  It must overlap the
certified `two_j<=139` rail and enclose the central `two_j=256` sentinel with
width below `1/10` before an enlarged cutoff is selected.
