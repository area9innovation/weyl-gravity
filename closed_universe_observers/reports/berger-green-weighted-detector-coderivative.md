# Green-weighted detector coderivative

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

For each fixed detector profile, the four-dimensional coderivative of
`chi_a dTheta wedge dR_a` has a temporal scalar block from the spatial
coderivative and a spatial one-form block from the clock derivative.  The
latter must not be replaced by its zero unweighted clock moment.

On the advanced support interval, boundary flatness of the exact compact
clock bump permits integration by parts.  Thus the spatial block is weighted
by the derivative of the sine Green kernel, namely its cosine kernel, while
the temporal scalar block is weighted by the sine kernel itself.  The
artifact exports both blocks through `two_j=4` as interval polynomials in
`T=t_detector_center-t`, uniformly over the matching emitter-switch support.
An exact rational bound encloses the omitted entire-series terms.

This is the finite-mode advanced Maxwell image.  It is not the full Green
image: modes above `two_j=4` and their infinite spatial-harmonic tail remain
open.  The subsequent `h_a dA_a^adv` massive-two-form image, positive-energy
Cauchy coefficients, absolute-`g^3` recoil, nonlinear closure and quantum
claims also remain open.
