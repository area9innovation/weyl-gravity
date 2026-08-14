# Complete BT order-g4 UV-local noncancellation

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `COMPLETE_ORDER_G4_UV_LOCAL_CANCELLATION_OBSTRUCTED`

## Result

The complete order-$g^4$ coefficient of the annealed zero-fiber-score moment
has now been assembled.  On any fixed, inversion-symmetric ultraviolet
momentum carrier, its signed corrections cannot cancel the power term found
in the isolated quartic-score square.

The reason is a mismatch of soft degrees.  The cubic score is quadratically
soft in the external lowest momentum $p$, while the quartic and quintic
scores are linearly soft.  Consequently the square of the quartic score
starts at $p^2$.  Every other term in the complete coefficient either contains
the quadratically soft cubic score or contains two such factors.  The apparent
$p^3$ cross terms vanish by the $p\leftrightarrow-p$ symmetry of the real
cosine, so those corrections start at $p^4$.

This closes local or diagram-by-diagram cancellation in the ultraviolet.  It
does not yet decide the unrestricted lattice sum.  A full cancellation could
only be nonuniform across momentum regions: the shrinking infrared complement
would have to generate a signed $p^2$ term and cancel the fixed positive
ultraviolet contribution after summation.

## Exact action and score expansion

For $y_\delta=d_\delta\phi$, define

\[
 a=\sum_\delta y_\delta,
 \quad b=\sum_\delta y_\delta^2,
 \quad c=\sum_\delta y_\delta^3,
 \quad d=\sum_\delta y_\delta^4.
\]

The exponential residual gives

\[
 g^{-1}R(g\phi)
 =a+\frac g2b+\frac{g^2}{6}c+\frac{g^3}{24}d+O(g^4).
\]

Squaring it in the positive action yields

\[
\begin{split}
 S_1&=\frac12\sum_xa_xb_x,\\
 S_2&=\sum_x\left(\frac{a_xc_x}{6}+\frac{b_x^2}{8}\right),\\
 S_3&=\sum_x\left(\frac{a_xd_x}{24}+\frac{b_xc_x}{12}\right).
\end{split}
\]

At zero fiber coordinate, write

\[
 s_g(\eta)=D_hS_g(\eta)
 =gA+g^2B+g^3C+O(g^4),
\]

with $A=D_hS_1$, $B=D_hS_2$, and $C=D_hS_3$.

## Integrating the free fiber

The free lowest-mode coordinate $T$ is Gaussian with

\[
                         v=\mathbb E_0[T^2]
                          =\frac{2}{N\omega_p^2}.
\]

Write the first two interaction polynomials on a fiber as

\[
 S_1(\eta+Th)=\alpha_0+\alpha_1T+\alpha_2T^2+\alpha_3T^3
\]

and

\[
 S_2(\eta+Th)=\beta_0+\beta_1T+\beta_2T^2
               +\beta_3T^3+\beta_4T^4.
\]

Expanding the logarithm of the conditional fiber integral gives the effective
background action

\[
 W_g=S_{0,\perp}+gW_1+g^2W_2+O(g^3),
\]

where

\[
 W_1=\alpha_0+v\alpha_2
\]

and

\[
\begin{split}
 W_2={}&\beta_0+v\beta_2+3v^2\beta_4\\
 &-\frac12\left[
 v\alpha_1^2
 +v^2(2\alpha_2^2+6\alpha_1\alpha_3)
 +15v^3\alpha_3^2\right].
\end{split}
\]

These are exact finite-dimensional Gaussian moments, not a saddle-point
approximation.

## Complete normalized coefficient

Let $\nu_0$ be the free orthogonal-background Gaussian law.  Parity gives
$\mathbb E_0W_1=0$.  Set

\[
 r_2=\frac12W_1^2-W_2,
 \qquad z_2=\mathbb E_0r_2.
\]

Expansion of both the numerator and the background partition function then
gives

\[
 \boxed{
 M_4=\mathbb E_0\left[
 B^2+2AC-2ABW_1+A^2\left(\frac12W_1^2-W_2-z_2\right)
 \right]. }
\]

There is a useful independent normal form.  The square root of the normalized
background density is

\[
 \sqrt{\frac{d\nu_g}{d\nu_0}}
 =1-\frac g2W_1
 +g^2\left(\frac18W_1^2-\frac12W_2-\frac12z_2\right)
 +O(g^3).
\]

Multiplying this by $s_g$ and taking its free squared norm reproduces the
boxed formula.  An exact rational two-state fixture independently checks the
normalization and gives the same coefficient $-211/12$ in the direct and
square-root forms.  The negative fixture value is only an algebra check; it
is not BT data.

## Why ultraviolet cancellation is impossible

Restrict every internal momentum to fixed inversion-symmetric compact boxes
away from zero, the conditioned $\pm p$ block, and all internal soft
singularities.  On this carrier:

- $A=O(|p|^2)$ by the exact lattice cubic/Heron identity;
- $B=O(|p|)$, and its exact quarter-period derivative is $-1/3$;
- $C=O(|p|)$ because every field leg in every $S_3$ monomial occurs in a
  directed-edge factor $e^{ik\cdot\delta}-1$;
- $W_1$ and $W_2$ introduce no inverse external power.  In four dimensions
  $v=2/(N\omega_p^2)$ remains bounded on the refinement sequence.

The term orders in the boxed formula are therefore

\[
 B^2=O(p^2),\quad AC=O(p^3),\quad ABW_1=O(p^3),\quad
 A^2(\cdots)=O(p^4).
\]

The complete real-cosine moment is even under $p\mapsto-p$.  Analytic cubic
terms on the fixed carrier vanish, so the two cross terms actually begin at
$p^4$.  The exact nonzero derivative of $B$ supplies an open set on which its
third-Wiener-chaos square has a strictly positive $p^2$ coefficient.

Hence the complete UV-local $p^2$ coefficient is precisely the positive
coefficient from $B^2$.  Measure normalization, projection, the quintic score,
and lower-score cross terms cannot cancel it on the same fixed carrier.

## Remaining barrier

The theorem does not justify exchanging the external Taylor expansion with
the unrestricted lattice momentum sums.  Momentum regions whose distance
from zero shrinks with $p$ are excluded from the fixed-carrier proof.  They
can have nonuniform propagator bounds.

The next calculation is therefore sharply defined: decompose every Wick
contraction in the boxed formula into fixed ultraviolet carriers and the
$p$-dependent infrared complement.  Either prove that all signed complement
terms are $O(N\omega_p^2\log^k L)$, which is too small to cancel the positive
$O(N\omega_p)$ contribution, or compute an exact complement coefficient at
the $N\omega_p$ scale.

No sign or scaling theorem for the unrestricted $M_4$, nonperturbative
annealed score bound, normalized lowest-mode estimate, interacting $H^{-1}$
moment, tightness, continuum identification, Born rule, Krein reconstruction,
or `LORENTZIAN-CAUSAL` result is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_uv_noncancellation.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_uv_noncancellation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_uv_noncancellation
```

## Verification receipt

The final bounded run used the exact commands above under the 500 MB virtual
memory cap.  The producer check took 0.04 s (20,544 KB peak), the independent
verifier 0.10 s (29,104 KB), all nine focused tests 0.14 s (30,580 KB), and
Python compilation 0.05 s.  The generated Paper 21 claim-map check and its
independent verifier took 0.07 s each.  Two PDF passes took 0.80 s and 0.77 s
and produced a 53-page manuscript.  The affected cubic-score, RG-matching,
and quartic-score predecessor verifiers passed in 1.27 s, 0.10 s, and 0.09 s.

The append-only planning import folded 1,612 nodes with zero invalid items and
zero malformed events in 7.22 s under `GOMEMLIMIT=300MiB`.  The advisory
Science Forge shadow rail completed in 3.14 s and reported the existing
bridge-audit environment failure (`sympy` absent in the referenced external
tree) plus corpus-baseline drift (1,663 certificates versus the 2026-07-19
baseline of 976).  These advisory findings are not passes and were not used to
promote the result.

Tier 0 and the scoped Tier 1 suite passed.  Tier 2 was limited to the three
direct mathematical predecessors because no shared operator or schema was
changed.  Tier 3 was not run: the unrestricted order-$g^4$ coefficient and
every continuum, reconstruction, freeze, and release gate remain open.  The
exact staged diff and content hashes are inspected immediately before the
coherent commit.
