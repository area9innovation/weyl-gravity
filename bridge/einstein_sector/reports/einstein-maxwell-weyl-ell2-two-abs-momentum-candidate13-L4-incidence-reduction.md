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

This is not yet the complete ideal theorem.  The remaining gate is a rank-
stratification bound for all-active degenerate source quadruples.  Until that bound
is proved, the full candidate-13 zero variety, same-fibre sources, Taub joins
and every correction class remain fail-closed.
