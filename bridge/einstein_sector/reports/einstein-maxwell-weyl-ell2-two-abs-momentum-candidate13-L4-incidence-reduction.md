# Candidate-13 L4 incidence reduction

Candidate 13 is the final unclassified cross-fibre ideal and has a different
algebraic type from every preceding fibre.  Both source branches have two
internal components per parity, while both target parities are scalar.

The four exact internal matrices are invertible.  Exact rational intervals
show that the squared bilinear-form pencil has positive trace, determinant and
discriminant.  The real pencil therefore has four distinct generalized roots.
After simultaneous equivalence the all-`m` equations become

`sum_i A_i B_i=0`,

`sum_i lambda_i A_i B_i=0`

as two identities of binary octics, with `A_i,B_i` binary quartics.

The source choice `A_1=A_2=x^4`, `A_3=A_4=y^4` has an exact rank-18 minor
`-(lambda_1-lambda_2)^4(lambda_3-lambda_4)^5`.  Thus the rank-18 source set is
nonempty and open; over it the kernel is two-dimensional and the incidence
variety has an irreducible generic component of complex dimension 22.

The normal form also has a genuinely cross-eigenline solution.  Taking the
first three `A_i` equal to one nonzero quartic `F` and the corresponding
`B_i` proportional to `lambda_2-lambda_3`, `lambda_3-lambda_1`, and
`lambda_1-lambda_2` times a nonzero quartic `G` kills both octic sums.
Distinct roots make all three weights nonzero.  Thus candidate 13 cannot be
replaced by the one-eigenline factorization used for the regular pencils.

The entire coordinate boundary can nevertheless be removed from the remaining
top-dimensional gate.  If `s=0,1,2` of the four `A_i` are nonzero, the source
dimension and kernel dimension add to 20.  For `s=3`, the inactive `B` block
contributes five kernel dimensions and the active kernel is
`intersection_i A_i Sym^4`.  Unique factorization identifies its dimension as
`max(9-deg lcm(A_1,A_2,A_3),0)`.  The special locus with lcm degree `r<=8`
has source dimension at most `r+3`, hence incidence dimension at most 17; the
generic three-support locus has incidence dimension 20.  By symmetry the same
holds on the `B` boundary.  Therefore no component of dimension at least 21
is contained in the coordinate boundary; its generic point is in the
all-active torus.

The all-active rank stratification closes through a bundle calculation on
`P1`.  The source quadruple defines

`phi_A: O(-4)^4 -> O^2`,

whose columns are `A_i(1,lambda_i)^T`.  Write its kernel as `K_A` and its
torsion cokernel as `T_A`, of length `delta`.  At a point, let
`m_1<=m_2<=m_3<=m_4` be the four vanishing orders.  Every constant direction
minor is `lambda_j-lambda_i`, so the local Smith length is exactly
`m_1+m_2`.  A torsion point has at least three positive vanishing orders;
allowing its position to vary therefore costs at least `delta_z+1`
conditions.  Summing over the support gives

`codim{length(T_A)>=delta} >= delta+1`.

Split `K_A=O(-a) plus O(-b)`, with `a<=b`.  Degree and Riemann--Roch give

`a+b=16-delta`,

`dim ker L_A = h0(K_A(8)) = delta+2+q`,

where `q=h1(K_A(8))`.  If `q=0`, the torsion codimension bound makes the
total incidence dimension at most 21.  If `q>0`, then
`b=9+q`, `a=7-delta-q`, and a minimal polynomial syzygy has component degree
`d=a-4=3-delta-q`.  Since `K_A` is a subbundle of `O(-4)^4`, one has
`a>=4`; hence `delta+q<=3` and the finite table below is exhaustive.  Put
`X_i=A_iB_i`.  The two octic equations say that the
four `X_i` lie in the fixed two-dimensional kernel of the four pencil
directions, so

`X_i=alpha_i H+beta_i J`, `H,J in Sym^(d+4)`.

For fixed nonzero `H,J`, each `A_i` is a degree-four divisor of the
corresponding pencil member, a finite projective choice, followed by one
affine scale.  Projectivizing `(H,J)` bounds the source locus by dimension
`2d+13`; if one pencil member vanishes identically the smaller bound `d+12`
applies, and two cannot vanish because the directions are distinct.  The six
possible positive-`q` pairs

`(delta,q)=(0,1),(0,2),(0,3),(1,1),(1,2),(2,1)`

all have incidence dimension at most 20.  An independent verifier enumerates
the local valuation patterns and replays this finite table using exact integer
arithmetic.

Consequently every rank-drop stratum is at most dimension 21, while the
rank-18 open bundle is dimension 22.  The 18 bilinear generators therefore
have height 18 in the 40-variable polynomial ring and form an unmixed
complete intersection.  Unmixedness excludes every lower-dimensional stratum
as a component, leaving the closure of the irreducible rank-18 bundle as the
unique component.  The displayed rank-18 derivative in the `B` variables
makes that component generically reduced.  A one-minimal-prime unmixed ideal
that is reduced at its generic point is radical, so the ideal is prime.

Thus the complete candidate-13 cross-fibre zero variety is one irreducible
complex dimension-22 cone in ambient dimension 40.  Same-fibre quadratic
sources, the five Taub maps, bounded and smooth-secular correction classes,
and all residual, causal, observational and quantum interpretations remain
fail-closed.
