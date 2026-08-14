# BT quartic-score power obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `ISOLATED_FIXED_ORDER_ROUTE_OBSTRUCTED`

## Result

The cubic score logarithm is not the last obstruction in a proof that treats
the Taylor coefficients separately.  The square of the next, quartic score
polynomial has a power divergence:

\[
 \frac{\mathbb E_0[Q_L^2]}{N\omega_L^2}
 \geq \frac{c}{\omega_L}
 \geq c' L^2
\]

for all sufficiently large $L$, with positive constants independent of
$L$.  Here $Q_L$ is the coefficient of $g^2$ in the zero-fiber score and the
expectation is under the free bilaplacian Gaussian conditioned on the real
lowest cosine being zero.

This is an isolated positive term, not the complete order-$g^4$ coefficient
of the interacting background-marginal score.  At that order there are also
signed corrections from the Gibbs density, normalization, higher lattice
Taylor terms, and lower-score cross terms.  Those terms can in principle
cancel the power divergence.  The theorem therefore obstructs a positive
term-by-term proof; it does not prove that the actual interacting score or
moment diverges.

## Exact quartic lattice score

For the exponential BT residual, write

\[
 g^{-1}R_x(g\phi)
 =a_x+\frac g2b_x+\frac{g^2}{6}c_x+O(g^3),
\]

where

\[
 a_x=\sum_\delta d_\delta\phi,
 \qquad b_x=\sum_\delta(d_\delta\phi)^2,
 \qquad c_x=\sum_\delta(d_\delta\phi)^3.
\]

Expanding $S_g=(2g^2)^{-1}\sum_xR_x(g\phi)^2$ gives

\[
 S_0=\frac12\sum_xa_x^2,
 \quad S_1=\frac12\sum_xa_xb_x,
 \quad S_2=\sum_x\left(\frac{a_xc_x}{6}+\frac{b_x^2}{8}\right).
\]

For a real lowest cosine $h$, the quartic zero-fiber score is

\[
 Q_L=D_hS_2
 =\sum_x\left[
 \frac{(D_ha_x)c_x+a_x(D_hc_x)}6
 +\frac{b_xD_hb_x}{4}
 \right]_{\phi=\eta},
 \qquad \eta\perp h.
\]

This identity is an exact Taylor-coefficient extraction from the positive
lattice action.

## Fourier kernel and exact soft fixture

Let

\[
 d_\delta(k)=e^{ik\cdot\delta}-1,
 \qquad
 B_j(k_1,\ldots,k_j)=
 \sum_\delta\prod_{a=1}^j d_\delta(k_a).
\]

The fully symmetric four-leg kernel is

\[
\begin{split}
 K_4(k_1,k_2,k_3,k_4)=\frac1{24}\Bigl[&
 \sum_i B_1(k_i)B_3(k_1,\ldots,\widehat{k_i},\ldots,k_4)\\
 &+B_2(k_1,k_2)B_2(k_3,k_4)\\
 &+B_2(k_1,k_3)B_2(k_2,k_4)\\
 &+B_2(k_1,k_4)B_2(k_2,k_3)\Bigr].
\end{split}
\]

At the exact fixture

\[
 p=(\varepsilon,0,0,0),\quad
 q=(\pi/2,0,0,0),\quad
 r=(0,\pi/2,0,0),\quad
 s=-p-q-r,
\]

Gaussian-rational dual-number arithmetic gives

\[
 K_4(0,q,r,-q-r)=0,
 \qquad
 \left.\frac{dK_4}{d\varepsilon}\right|_{\varepsilon=0}
 =-\frac13.
\]

Thus the external soft degree is genuinely linear.  It cannot be improved to
quadratic by momentum conservation.  This agrees with the continuum vertex
classification in the primary [Anderson--Bateman--Herzog--Turok
paper](https://arxiv.org/abs/2608.12210), but the lattice kernel and fixture
above are derived independently.

## Power lower bound

The exact nonzero derivative has a fixed open neighborhood on which
$|K_4|\geq c_0|p|$.  Choose disjoint compact boxes around the displayed
$q,r,s$ values, away from zero and from the conditioned external cosine
block.  For large $L$, the $q$ and $r$ boxes each contain order $N$ lattice
momenta, while $s=-p-q-r$ stays inside its box after shrinking them.

The third homogeneous Wiener-chaos norm of $Q_L$ is a sum of squared
symmetric kernels divided by positive free propagator denominators.  Keeping
only these boxes is therefore a rigorous lower bound.  The boxes contribute
order $N^2$ ordered pairs, each with kernel square at least a constant times
$|p|^2$.  The score normalization contributes $N^{-1}$, giving

\[
 \mathbb E_0[Q_L^2]\geq c_1N|p|^2
                    \geq c_2N\omega_L.
\]

Division by the required $N\omega_L^2$ scale proves the theorem.  Finally,
$\omega_L=4\sin^2(\pi/L)\leq4\pi^2/L^2$ gives quadratic growth.

The constants are existential but rigorous: they come from a fixed open
neighborhood of an exact nonzero fixture.  No Monte Carlo value enters the
proof.

## Numerical preflight

The dependency-free binary64 program samples the exact free Gaussian by a
radix-two FFT and evaluates the position-space polynomial above using
$O(L^4)$ memory.

| $L$ | samples | $\operatorname{Var}(Q_L)/(N\omega_L^2)$ | divided by $L^2$ |
|---:|---:|---:|---:|
| 4 | 20000 | 0.0025322 | 0.0001583 |
| 8 | 5000 | 0.0083901 | 0.0001311 |
| 16 | 500 | 0.0335743 | 0.0001311 |
| 32 | 40 | 0.107396 | 0.0001049 |

The $L=32$ row is deliberately low statistics.  These observations support
the power count only; the open-box/Wiener-chaos argument proves it.

## Consequence for the continuum route

On the tuned refinement trajectory, $g_L^2$ decreases only as $1/\log L$.
Thus $g_L^4$ cannot by itself compensate an isolated $L^2$ term.  The exact
cubic logarithm/beta-function match is therefore insufficient as a proof of
the whole score estimate.

The next calculation must assemble the **complete** order-$g^4$
background-marginal coefficient.  Its score, Gibbs-density, normalization,
projection, and higher lattice-Taylor pieces must be placed in a common
Wiener-chaos basis.  Either the perfect-square identities cancel every
$L^2$ contribution, leaving a logarithmic RG problem, or a power term
survives and must be tested against the actual running trajectory.

No complete order-$g^4$ coefficient, nonperturbative annealed score, center
moment, integrated lowest-mode estimate, interacting $H^{-1}$ moment,
tightness, continuum identification, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` result is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_quartic_score_power_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_quartic_score_power_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_quartic_score_power_obstruction
ulimit -v 500000; cc -O3 -std=c11 -Wall -Wextra -pedantic -fsyntax-only reverse_physics/bt_euclidean_quartic_score_preflight.c
```

## Verification receipt

The final bounded run used the exact commands above under the 500 MB virtual
memory cap.  The producer check took 0.04 s (20,840 KB peak), the independent
verifier 0.10 s (29,384 KB), all nine focused tests 0.14 s (30,400 KB), and
the C syntax check 0.02 s (18,764 KB).  A compiled deterministic $L=4$,
100-sample smoke run took 0.18 s (44,168 KB).  Python compilation took
0.05 s.  The generated Paper 21 claim-map check and independent verifier took
0.06 s and 0.07 s, and two PDF passes took 0.79 s and 0.76 s.  The affected
cubic-score, RG-matching, and Ward-weight predecessor verifiers passed in
1.27 s, 0.09 s, and 0.09 s.

The append-only planning import folded 1,611 nodes with zero invalid items and
zero malformed events in 7.32 s under `GOMEMLIMIT=300MiB`.  The advisory
Science Forge shadow rail completed in 4.31 s and reported the existing
bridge-audit environment failure (`sympy` absent in the referenced external
tree) plus the expected corpus-baseline drift (1,662 certificates versus the
2026-07-19 baseline of 976).  Advisory findings are not passes and were not
used to promote this claim.

Tier 0 and the scoped Tier 1 suite passed.  Tier 2 was limited to the three
direct certificate predecessors because no shared mathematical input or
schema changed.  Tier 3 was not run: this is an isolated fixed-order method
obstruction and does not promote a continuum, reconstruction, freeze, or
release theorem.  The exact staged diff and content hashes are inspected
immediately before the coherent commit.
