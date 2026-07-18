# Finite-harmonic second-order tangent-cone theorem

Let a first-order solution `u` have finite harmonic support and let every
quadratic output channel be included.  In block `j`, write the second-order
equation as

\[
L_j v_j=-S_j(u,u).
\]

First restrict the equation target to the kernel of every Noether identity
row and remove gauge-null correction columns (or take a complete gauge
slice).  For a declared correction category `C`, let the remaining adjoint
cokernel annihilate `im L_j^C`; its pairings with `S_j(u,u)` are
the obstructions.  Identify its certified stabilizer subspace with the
moment maps `mu_X(u)` and call a complementary basis `R_j^C(u)`, so no
functional is counted twice.  Then

\[
\mathcal Z_2^{\mathcal C}
=\{u:\mu_X(u)=0,\ R_j^{\mathcal C}(u)=0\ \text{for every }j\}.
\]

Necessity is the adjoint pairing of the second-order equation.  Sufficiency
follows because the vanishing pairings put each compatible source in the
image of the block operator; the declared finite blockwise right inverses
then assemble `v`.  Completeness of the harmonic output list, Noether rows,
gauge reduction, and right inverses is essential.

## Correction categories are different theorems

For the audited resonant block,

\[
(\partial_t-i\omega)v=e^{i\omega t},
\]

there is no bounded finite-quasiperiodic correction: the resonant coefficient
is an adjoint-cokernel obstruction.  In the smooth-secular category,

\[
v=t e^{i\omega t}
\]

solves the equation exactly.  For a compatible compact source, the retarded
formula

\[
v(t)=\int_{-\infty}^t e^{i\omega(t-s)}f(s)\,ds
\]

solves it with future support.  The causal statement concerns compact sources
and is not an identification with the eternal Fourier problem.

The exact finite fixture contains one persistent static moment-map cokernel
and one resonant cokernel.  Its tangent cones are therefore

```text
bounded/quasiperiodic:  mu_X = 0 and R_res = 0
smooth secular:         mu_X = 0
causal/retarded:        mu_X = 0  (compatible compact sources and a declared retarded inverse)
```

This is an abstract reduction theorem and adversarial category audit.  It
does not classify a new background or establish all-orders integrability.
