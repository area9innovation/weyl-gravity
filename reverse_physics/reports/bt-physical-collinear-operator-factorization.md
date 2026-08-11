# BT physical collinear operator factorization

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

**Certificate:** `REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1`

## Result

The certified five-point probability coefficient can be lifted back to an
explicit amplitude-level splitting map on the declared external mass-jet
cylinder.  That map is not the completed public order-λ quadratic
(R_t) map.  The distinction is exact and basis independent: the physical
Gram has rank two, whereas the raised public Gram is a nonzero rank-one
nilpotent.

This establishes a physical leading collinear operator only on a reduced
two-component external jet fibre.  It does not construct a complete Møller or
S operator, complete scattering sectors, a finite NLO probability, or the
all-order Eq. (19).

## Five-point components

Write

\[
 A_5=\frac{M_5}{8\lambda^3}=\delta^2C+O(\delta^3),
 \qquad x_i=\delta a_i,\qquad t_{01}=\delta\tau .
\]

On the square-free spectator quotient relevant to
\([a_2a_3a_4]C^2\), the complete 25-tree amplitude is

\[
 C=L(a_2+a_3+a_4)+Q(a_2a_3+a_2a_4+a_3a_4)+\cdots,
\]

where

\[
 L=-\frac{(a_0-a_1)^2}{4\tau},\qquad
 Q=\frac{2\tau(a_0+a_1)-(a_0-a_1)^2}{4\tau^2}.
\]

The omitted terms cannot contribute to the square-free three-spectator
coefficient.  Hence

\[
 [a_2a_3a_4]C^2=6LQ=-\frac32\rho,
\qquad
 \rho=\frac{(a_0-a_1)^2
 [2\tau(a_0+a_1)-(a_0-a_1)^2]}{4\tau^3}.
\]

For positive unequal daughter masses and
\(\tau>(\sqrt{a_0}+\sqrt{a_1})^2\), one has \(\rho>0\).

## Four-point parent and splitting map

The complete reduced four-point tree, with the two daughters recombined into
a parent coefficient (p), is

\[
 A_4=\frac{M_4}{4\lambda^2}=\delta^2H+O(\delta^3),
\]

\[
 H=\frac12\bigl(p^2+a_2^2+a_3^2+a_4^2
 +pa_2+pa_3+pa_4+a_2a_3+a_2a_4+a_3a_4\bigr).
\]

Therefore
\([pa_2a_3a_4]H^2=3/2\).  For each of the three singleton/complement
partitions, use the parent constant/linear jet basis and its one-leg
delta-prime cross pairing

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

The hard components are ((1/2,1/2)), while the five-point components are
\((Q,L)\).  Thus the physical splitting map is

\[
 T=\operatorname{diag}(2Q,2L),\qquad
 T^\sharp=JT^TJ=\operatorname{diag}(2L,2Q).
\]

The fifth delta-prime contributes the already certified minus sign, giving

\[
 -T^\sharp T=\rho I_2.
\]

Equivalently, the physical Gram follows directly from the amplitude ratio,

\[
 -\frac{[a_2a_3a_4]C^2}{[pa_2a_3a_4]H^2}=\rho.
\]

The global Feynman (i) phase is common to the four- and five-point trees and
cancels in their ratio.  The displayed (T) is therefore real in this BT
convention; the reverse block is fixed by Krein skew-adjointness.

## Normalization

The integrated five-point finite part shifts by (-3\log(c)/8).  Since its
kernel is (-3\rho/2), the corresponding integrated response of \(\rho\)
is (+\log(c)/4).  The remaining amplitude-square, factorial,
three-body-factorization and inner-angle ratio is

\[
 4\times\frac13\times\frac1{16}=\frac1{12}.
\]

Consequently the physical response is exactly

\[
 \frac1{12}\frac14\log(c)=\frac1{48}\log(c)
\]

per unordered pair.  This derives the previously certified coefficient from
the explicit map rather than fitting its norm.

## Public (R_tD) comparison

For same daughter signs, the completed public quadratic map has covariant
parent Gram

\[
 G_{\rm public}=\begin{pmatrix}0&0\\0&2\end{pmatrix}.
\]

Raising its parent index with (J) gives

\[
 N_{\rm public}=JG_{\rm public}
 =\begin{pmatrix}0&2\\0&0\end{pmatrix},\qquad
 N_{\rm public}^2=0.
\]

It is nonzero, rank one, and nilpotent.  The physical raised Gram is
\(\rho I_2\): it has rank two, determinant \(\rho^2>0\), and minimal
polynomial (x-\rho).  Similarity, a nonzero scalar normalization, channel
rephasing, covariant zero-mode dressing, Abel multiplication, and enlargement
of the output Naimark carrier cannot change rank or Jordan type.  Therefore
none can identify the public quadratic (D) with the physical (T) on this
jet cylinder.

The physical process uses both null halves of the parent dipole jet.  The
public map supplies only one nilpotent Gram direction.  Matching the total
probability number cannot manufacture the missing direction.

## Verification

The producer constructs the five-point jet from the published dot-product
vertices and the four-point jet from invariant Källén exchange graphs.  The
independent exhaustive verifier reverses those methods: invariant triangle
vertices for five points and an explicit dot-product graph construction for
four points.  Exact rational fixtures check the Gram above threshold, and
mutation tests reject coefficient, sign, rank, Jordan, normalization, object
identification, lifecycle-promotion, and Eq. (19) changes.

The auxiliary Naimark coordinate from the preceding certificate remains a
resolution/noise label, not a spacetime or physical dimension.

## Verification receipt

All symbolic Python commands ran sequentially with `ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python byte-compile; JSON parse of work item, event, schema, and certificate | PASS | 0.4 s | below cap |
| 0 | `git diff --check` on the scoped package and paper paths | PASS | below 0.3 s | negligible |
| 1 | producer exact reproduction | PASS, 22/22 | 1.44 s | 73,344 KB |
| 1 | independent method-distinct verifier with `--exhaustive` | PASS, 18/18 | 1.59 s | 77,804 KB |
| 1 | focused producer/verifier and eight mutation tests | PASS, 10/10 | 2.18 s | 73,600 KB |
| 1 | two-pass Paper V and Paper VI PDF builds | PASS | 0.87 s / 0.91 s | 50,912 KB / 50,928 KB |
| advisory | Science Forge shadow rail | advisory exit 0; bridge audit not counted as PASS because the installed Forge binary/stdlib mismatch triggers `E9118`; corpus census reports baseline drift | 2.7 s | not measured |

Tier 2 was unnecessary because every imported certificate is unchanged and
content-addressed, and this package is a new leaf with no generated consumer
beyond the two rebuilt papers.  Tier 3 was not run: there is no freeze,
release, shared-core change, lifecycle promotion of an existing result, or
Lorentzian theorem.  No skipped or advisory check is recorded as a pass.
