# Berger recoil detector/form binding

`BERGER_RECOIL_DETECTOR_FORM_BINDING` assembles each finite D0/D1
advanced-Maxwell detector image in the same component-major basis used by the
exact Berger de Rham matrices.  For every `two_j=0,...,4` and passive column,
the callable returns the spacetime one-form polynomial ordered as temporal
scalar followed by the three spatial coframe blocks.

The second callable applies
`Dhat_1(alpha,beta)=(partial_t beta-dSigma alpha,dSigma beta)`.  Because the
certificate polynomial uses `T=t_detector_center-t`, the physical derivative
is `partial_t=-partial_T`; reversing that sign changes the exact fixture.  The
reported output remainder includes the derivative of the omitted cosine tail,
not merely the pre-derivative value remainder, and propagates the temporal and
spatial tails through interval enclosures of `d0` and `d1`.

This closes the first physical form stage in the coupling-stripped preparation
word.  Switch multiplication, the advanced massive-two-form Green image,
Cauchy trace, positive-energy dual and all recoil scalars remain open.
