# BT low-action flat-potential convexity obstruction

## Result

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The flat-potential BT effective potential is nonconvex inside the action
region whose complement already has a certified exponential Gibbs tail.  The
obstruction occurs on the actual periodic four-dimensional lattice, not only
on the earlier three-vertex test graph.

On \(\Lambda=(\mathbb Z/16\mathbb Z)^4\), at the physical coupling
\(\lambda=2/5\), the exact rational witness below has

\[
 \frac{A}{N}=\frac{5121}{160}=32.00625<50.
\]

Nevertheless, the second derivative of the full negative logarithm of the
flat density is strictly negative in the declared direction.  More precisely,
the exact longitudinal calculation and a rigorous upper bound for all
nonzero transverse blocks give

\[
 D_h^2 V_{16^4}
 \leq
 -\frac{
 172511934113812002844255298492122939661512764763404478974825
 }{
 59081288175090511897125080246062762727536819609
 }
 <-2.9\times10^{12}.
\]

Thus the proposed shortcut

1. prove convexity on \(A<50N\), and
2. use the known bound
   \(\nu(A\geq50N)\leq\exp(-17N/5)\) on its complement

is obstructed as formulated.  This is a method obstruction.  It is not a
bad-volume sequence for the actual interacting moment and does not show that
the moment diverges.

## Exact two-well construction

Let the field depend only on the first coordinate,
\(\Omega_x=\omega_{x_1}\), with

\[
\begin{split}
(\omega_0,\ldots,\omega_{15})={}&
\left(4,\frac25,\frac1{25},\frac1{250},\frac1{2500},
\frac1{1000},\frac1{100},\frac1{10},1,\frac1{10},\right.\\
&\left.\frac1{100},\frac1{1000},\frac1{2500},\frac1{250},
\frac1{25},\frac25\right).
\end{split}
\]

Define

\[
 r_x=\frac{\Omega_{x-e_1}+\Omega_{x+e_1}}{\Omega_x}-2,
 \qquad u=r-\frac{36}{5}\mathbf1.
\]

The transverse constant directions contribute zero to \(r\).  The
ground-state transform proves that

\[
 K=-\Delta+\operatorname{diag}(r)\geq0,
 \qquad K\Omega=0,
\]

with a simple positive ground vector.  Hence the centered Schrödinger
operator has lowest eigenvalue \(\ell_0=-36/5\).  The potential direction is

\[
 h_x=\mathbf1_{x_1=0}-\mathbf1_{x_1=8}.
\]

The one-dimensional residual row is

\[
\left(-\frac95,\frac{81}{10},\frac{81}{10},\frac{81}{10},
\frac{21}{2},\frac{42}{5},\frac{81}{10},\frac{81}{10},
-\frac95,\frac{81}{10},\frac{81}{10},\frac{42}{5},
\frac{21}{2},\frac{81}{10},\frac{81}{10},\frac{81}{10}\right).
\]

It gives one-dimensional action \(5121/10\).  Replication over the
\(16^3\) transverse sites therefore leaves the four-dimensional action
density equal to \(5121/160\).

## Longitudinal curvature

For a centered potential \(u\), the exact flat density from
`REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_DETERMINANT_PUSHFORWARD_V1`
has effective potential

\[
 V(u)=\frac{\|u\|^2+N\ell_0(u)^2}{2\lambda^2}
       +\log\det{}'\!\left(H(u)-\ell_0(u)I\right).
\]

The producer obtains \(\ell_0'\), \(\ell_0''\), and the longitudinal
log-pseudodeterminant curvature by an exact bordered inverse.  In particular,

\[
 \ell_0''=
 -\frac{
 6728482722852693140424625000000
 }{
 10189088606001902723181089
 }<0.
\]

The independent rail does not reuse that pseudoinverse calculation.  It
interpolates the exact bivariate characteristic polynomial

\[
 p(t,z)=\det(K_1+t\operatorname{diag}(h)-zI)
\]

from 51 rational determinants, differentiates the implicit ground root, and
then differentiates \(-p_z\), the pseudodeterminant at that root.  The two
rails agree exactly.

## Bounding all transverse blocks

Fourier decomposition in the three transverse coordinates gives

\[
 K_4(t)=K_1(t)\otimes I+I\otimes\Delta_\perp.
\]

The zero transverse mode supplies the exact longitudinal
\(\log\det{}'K_1\) curvature.  For a nonzero transverse eigenvalue \(w\), put
\(M_w=K_1+wI\) and
\(K_1'=\operatorname{diag}(h)-\ell_0'I\).  Its contribution is

\[
 C_w=-\ell_0''\operatorname{tr}(M_w^{-1})
     -\operatorname{tr}\!\left((M_w^{-1}K_1')^2\right)
 \leq(-\ell_0'')\frac{16}{w}.
\]

The second trace is nonnegative after conjugating by \(M_w^{-1/2}\).  On
\(C_{16}\), every nonzero transverse mode obeys

\[
 w\geq2-2\cos(\pi/8)>\frac3{20}.
\]

The final strict inequality is exact: use
\(\cos(\pi/8)<37/40\), which reduces by positive squaring to
\(\sqrt2<569/400\), and then to the rational integer inequality
\(2<(569/400)^2\).  There are \(16^3-1=4095\) nonzero transverse modes, so

\[
 \sum_{w\ne0}C_w
 \leq 4095\frac{320}{3}(-\ell_0'')
 =436800(-\ell_0'').
\]

Adding this deliberately coarse positive upper bound to the exact
four-dimensional Gaussian curvature and the exact zero-mode determinant
curvature still leaves the displayed strictly negative rational number.

## Meaning and next calculation

The old three-vertex witness could have been dismissed as living in an
irrelevant high-action tail.  This witness cannot: it lies below the same
action-density threshold used by the certified exponential tail theorem and
it lives on a member of the physical \(L^4\) torus family.

What fails is global convexity of that entire nominal good region.  A smaller
region, a nonconvex localization argument, or a resolvent-adapted Stein field
could still control the Gibbs-weighted observable.  Conversely, the large
two-well resolvent suggests a possible bad-volume mechanism, but determinant
curvature alone is not a probability or moment lower bound.  The live gate is
therefore unchanged at the claim level: prove a genuinely Gibbs-weighted
noninduced resolvent/localization estimate, or construct a controlled volume
sequence for the actual interacting \(H^{-1}\) moment.

This result does not establish the normalized lowest-mode estimate, the
interacting \(H^{-1}\) bound or its failure, tightness, a continuum measure,
Born probabilities, Krein reconstruction, or Lorentzian physics.

## Reproducibility receipt

All claimed signs, derivatives, and bounds use exact rational arithmetic.
The floating decimal above is display-only.  The producer, independent
characteristic-polynomial verifier, schema validation, and mutation tests are
run under the repository's 500 MB memory cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_low_action_flat_convexity_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_low_action_flat_convexity_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_low_action_flat_convexity_obstruction
```

The measured scoped rail was: producer check 0.07 seconds at 21,408 KiB,
independent verifier 0.16 seconds at 29,576 KiB, and all 12 focused/mutation
tests 0.65 seconds at 31,000 KiB.  Python compilation took 0.04 seconds at
16,300 KiB.  JSON and schema parsing passed.

Tier 0 covers Python compilation, JSON/schema parsing, scoped
`git diff --check`, exact input hashes, and staged-diff inspection.  Tier 1 is
the three-command rail above.  Tier 2 rechecks the unchanged direct inputs by
content hash.  Tier 3 is not required because this is a bounded method
obstruction, not a freeze, theorem lifecycle promotion, shared-core change, or
release.  The advisory Science Forge shadow result is recorded fail-closed;
its pre-existing toolchain/baseline drift is not reported as a pass.  The
planning import passed with 1,643 nodes, zero invalid items, and zero malformed
events.  The advisory shadow rail reported the existing Forge binary/library
hash mismatch, `E9118` bridge-audit failure, and corpus-baseline drift (1,762
certificates versus the 2026-07-19 baseline of 976).  A first Go invocation
under the Python address-space cap also failed at runtime initialization; it
was rerun correctly with `GOMEMLIMIT=300MiB GOGC=50`, and that failed attempt
is retained here rather than reclassified as a pass.

Paper 21 is not changed at this checkpoint.  Its foundations authority chain
is independently generated, while this result narrows a method rather than
changing the open interacting-moment or reconstruction lifecycle state.
