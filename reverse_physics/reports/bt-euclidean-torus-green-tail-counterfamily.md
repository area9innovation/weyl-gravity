# BT torus Green-tail counterfamily

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GREEN_TAIL_COUNTERFAMILY_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

## Result

The complete deterministic BT residual-gradient quotient has no positive
all-field lower bound at the free four-torus infrared scale. There is an
explicit sequence of positive, genuinely four-way coupled fields \(u_n\) on
\(T_{L_n}^4\) such that

\[
 0<c\leq \lVert r_n\rVert_2^2\leq C,\qquad
 {\max u_n\over\min u_n}\leq C L_n^{5/12},
\]

but

\[
 \boxed{\quad
 {Q_n\over\omega_{L_n}^2}
 ={\lVert g_n\rVert_2^2\over
 \omega_{L_n}^2\lVert r_n\rVert_2^2}
 \longrightarrow0.\quad}
\]

Here

\[
 r_n={\Delta u_n\over u_n},\qquad
 g_n=J_{\log u_n}^{\,T}r_n,\qquad
 \omega_L=4\sin^2(\pi/L).
\]

This realizes the negative branch of the programme's main deterministic
fork. The earlier lower bounds were genuine but necessarily conditional:
small action, fixed field height, simple bubbles, one-phase hierarchies,
independent tensor phases, and several high-contrast sectors all miss the
compensated Green tail used here.

## Why the earlier bubbles failed

A critical four-dimensional bubble has the local form

\[
 U_\lambda(x)={\lambda\over\lambda^2+|x|^2},
 \qquad -\Delta_{\mathbb R^4}U_\lambda=8U_\lambda^3.
\]

Its BT curvature \(\Delta U_\lambda/U_\lambda^3\) is constant. Cutting the
bubble off and replacing its tail by a constant changes that curvature by
order one across the cutoff shell. The shell's complete gradient is exactly
of the torus free scale. This explains the positive endpoints in the
previous periodic and repaired-bubble certificates.

The present construction does not cut the bubble off. It puts its source on
the torus, subtracts the source mean, and solves the periodic Poisson equation.
The compensating positive source is therefore spread through the entire
Green tail. The field is lifted above the minimum only after that exact
compatibility correction.

## The family

Use the integer subsequence

\[
 L_n=n^{24},\qquad
 \lambda_n=n^{16}=L_n^{2/3},\qquad
 R_n=n^{21}=L_n^{7/8},
\]

and

\[
 \epsilon_n={\lambda_n\over R_n^2}=n^{-26}.
\]

Let \(d_L\) be the centered Euclidean distance on the periodic lattice and
define the rational positive source

\[
 f_n(x)={8\lambda_n^3\over
              (\lambda_n^2+d_{L_n}(x,0)^2)^3}.
\]

Let \(v_n\) be the unique mean-zero solution of

\[
 -\Delta v_n=f_n-\bar f_n,\qquad
 \bar f_n={1\over L_n^4}\sum_x f_n(x),
\]

and set

\[
 u_n^0=v_n-\min v_n+\epsilon_n.
\]

Every object is defined at finite volume. No continuum interpolation or
choice of a complement is involved: the inverse is the mean-zero inverse of
the explicit periodic graph Laplacian.

The final four-way coupling is

\[
 p_n(x)=\prod_{a=1}^4\sin{2\pi x_a\over L_n},\qquad
 \delta_n={1\over n},
\]

\[
 \boxed{\quad u_n=u_n^0(1+\delta_np_n).\quad}
\]

For \(n\geq2\), \(|\delta_np_n|\leq1/2\), so \(u_n\) is positive.

## Discrete Green and annular lemma

The analytic core is a deterministic lattice estimate. If
\(1\ll\lambda\ll R\ll L\), \(\epsilon=\lambda/R^2\), and
\(R^3\ll\lambda L^2\), the preceding source and mean-zero Poisson solution
obey

\[
 u^0(x)\asymp
 {\lambda\over\lambda^2+d_L(x,0)^2}+\epsilon.
\]

The same comparison holds after the appropriate scale factors for finite
differences through order four. Moreover,

\[
 \sum_x f(x)\asymp\lambda,\qquad
 \bar f\asymp{\lambda\over L^4}.
\]

There are universal constants \(0<c<C<\infty\) such that

\[
 c\leq\left\|{\Delta u^0\over u^0}\right\|_2^2\leq C
\]

and, for the complete logarithmic action gradient,

\[
 \boxed{
 \lVert g(u^0)\rVert_2^2
 \leq C\left(
 \lambda^{-8}
 +{\lambda^4\over R^8}
 +{R^4\over L^8}
 +{\lambda^4\over R^4L^4}
 \right).}
\]

### Green-kernel proof

The mean-zero kernel has the exact Fourier representation

\[
 G_L(x)={1\over L^4}
 \sum_{\substack{k\in T_L^4\\k\ne0}}
 {e^{2\pi i k\cdot x/L}\over
  4\sum_{a=1}^4\sin^2(\pi k_a/L)}.
\]

Dyadically splitting the modes at \(|k|\sim L/\rho\) and summing by parts in
each coordinate gives, for \(0\leq j\leq4\),

\[
 |D^jG_L(x)|
 \leq {C_j\over(1+d_L(x,0))^{2+j}}+{C_j\over L^{2+j}}.
\]

Convolving these estimates with \(f\), and splitting both variables into
the regions

\[
 d\lesssim\lambda,\qquad
 2^j\lambda\lesssim d\lesssim2^{j+1}\lambda,\qquad
 d\gtrsim R,
\]

gives the displayed potential and differentiated comparisons. The lattice
shell with radius \(\rho\) contains \(O(\rho^4)\) points, while

\[
 f(x)\lesssim{\lambda^3\over(\lambda+d)^6}.
\]

Thus the source mass is \(O(\lambda)\); the ball \(d\leq\lambda\) supplies
the matching lower bound.

### Action bounds

The exact Poisson equation gives

\[
 r^0=-{f-\bar f\over u^0}.
\]

On \(d\leq\lambda\), \(f\asymp\lambda^{-3}\) and
\(u^0\asymp\lambda^{-1}\), so \(|r^0|\asymp\lambda^{-2}\) on
\(\asymp\lambda^4\) sites. This proves the positive lower bound.

For the upper bound, dyadic shells give

\[
 {f\over u^0}\lesssim
 \begin{cases}
 \lambda^2/(\lambda+d)^4,&d\leq R,\\
 \lambda^2R^2/d^6,&d>R,
 \end{cases}
\]

while the mean-source contribution is bounded by \(d^2/L^4\) below \(R\)
and by \(R^2/L^4\) above it. Squaring and summing the shells yields

\[
 \lVert r^0\rVert_2^2
 \leq C\left(
 1+{\lambda^4\over R^4}
 +{R^8\over L^8}
 +{R^4\over L^4}\right)\leq C.
\]

### Complete-gradient bound

Put

\[
 h={r^0\over(u^0)^2}={\Delta u^0\over(u^0)^3},\qquad
 c_{xy}=u_x^0u_y^0.
\]

The exact BT identity is

\[
 g(u^0)=L_c h.
\]

In the bubble core the constant curvature \(-8\) is annihilated by \(L_c\).
The remaining curvature splits into four terms:

| term | squared complete-gradient contribution |
|---|---:|
| lattice finite-difference defect | \(O(\lambda^{-8})\) |
| lift \(u^0-U_\lambda\sim\epsilon\) across \(d\sim R\) | \(O(\lambda^4/R^8)\) |
| uniform compensating source \(\bar f\) | \(O(R^4/L^8)\) |
| periodic image variation | \(O(\lambda^4/(R^4L^4))\) |

For completeness, the discrete product estimate behind every row is

\[
 |L_ch(x)|
 \leq C\left[
 \max_{y\sim x}c_{xy}\max_{|z-x|\leq2}|D^2h(z)|
 +\max_{|z-x|\leq2}|Dc(z)|\max_{|z-x|\leq2}|Dh(z)|
 \right].
\]

The differentiated Green comparisons insert the relevant scale into this
formula. In the lift region, for example,

\[
 c\asymp{\lambda^2\over R^4},\qquad
 |D^2h|\lesssim R^{-2},
\]

so \(|g|\lesssim\lambda^2/R^6\) on \(O(R^4)\) sites, giving
\(\lambda^4/R^8\). The other three rows follow by the same shell
calculation. This proves the annular lemma without using the floating-point
scout.

## Stability of the four-way coupling

For the product sine mode,

\[
 |D^jp_n|\leq C_jL_n^{-j}.
\]

Near the bubble core it has the stronger bound
\(|p_n(x)|\leq C(d/L_n)^4\). Expanding the exact neighboring ratios of
\(u_n=u_n^0(1+\delta_np_n)\), using the Green comparisons in the core and
the \(L^{-j}\) bounds in the tail, gives

\[
 \lVert r(u_n)-r(u_n^0)\rVert_2=O(\delta_n),
\]

\[
 \lVert g(u_n)-g(u_n^0)\rVert_2
 =O\left({\delta_n\over L_n^2}\right).
\]

The residual lower bound therefore survives for all sufficiently large
\(n\), while the extra squared gradient is
\(O(\delta_n^2/L_n^4)\).

## Exact nonseparability

The base \(u_n^0\) is even in every coordinate. Hence

\[
 \sum_xp_n(x)\log u_n^0(x)=0.
\]

Reflection in one coordinate pairs every value \(p\) with \(-p\), and

\[
 p\log(1+\delta p)-p\log(1-\delta p)
 =p\log{1+\delta p\over1-\delta p}>0
\]

for \(p\ne0\). Therefore

\[
 \sum_xp_n(x)\log u_n(x)>0.
\]

The tensor mode \(p_n\) is orthogonal to every sum
\(\sum_af_a(x_a)\). Thus \(\log u_n\) is not additively separable and
\(u_n\) cannot be a product of one-coordinate fields.

There is also an elementary four-point witness. At coordinates
\(x_3=x_4=L/4\), varying \(x_1,x_2\) between \(L/4\) and \(3L/4\) leaves
the radial base unchanged while changing the perturbation sign. The
corresponding product minor is

\[
 (u^0)^2\big[(1+\delta)^2-(1-\delta)^2\big]
 =4\delta(u^0)^2>0.
\]

## Power balance

For \(L\geq4\), \(\sin(\pi/L)\geq2/L\), hence

\[
 \omega_L^2\geq{256\over L^4}.
\]

On the selected integer scales, the four base terms become

\[
 L_n^4\lambda_n^{-8}=n^{-32},
\]

\[
 {L_n^4\lambda_n^4\over R_n^8}=n^{-8},\qquad
 {R_n^4\over L_n^4}=n^{-12},\qquad
 {\lambda_n^4\over R_n^4}=n^{-20}.
\]

The explicit coupling contributes \(\delta_n^2=n^{-2}\). Since the
residual norm stays bounded below,

\[
 {Q_n\over\omega_{L_n}^2}
 \leq C\left(n^{-32}+n^{-8}+n^{-12}+n^{-20}+n^{-2}\right)
=O(n^{-2})\longrightarrow0.
\]

The certificate stores the five defining powers \((24,16,21,-26,-1)\) as
integers.  Its independent verifier recomputes every exponent above, the
lift identity \(-26=16-2(21)\), the annular condition
\(3(21)-16-2(24)=-1<0\), and the contrast exponent
\(2(21)-2(16)=10\).  The limiting conclusion is therefore not accepted by
matching prewritten asymptotic strings alone.

The field contrast is

\[
 {\max u_n\over\min u_n}
 \leq C{R_n^2\over\lambda_n^2}
 =Cn^{10}=CL_n^{5/12}.
\]

It is polynomial, while nearest-neighbor ratios remain uniformly bounded.

## Exact finite fixture

The machine certificate solves the rational Poisson problem on the
15 hyperoctahedral orbits of \(T_4^4\), with
\(\lambda=2\), \(\epsilon=1/8\), and \(\delta=1/2\). It expands the result
to all 256 vertices and computes the complete residual and logarithmic
gradient using Fraction arithmetic. The stored four-point product minor
is strictly positive. The independent verifier reconstructs the orbit
system with a separately implemented rational elimination and repeats the
full 256-site calculation without importing the producer.

This fixture checks the exact finite construction, Poisson compatibility,
gradient convention, positivity, and nonseparability. The growing-volume
limit is proved by the Green/annular estimates, not inferred from this small
fixture or from floating-point data.

## Relation to the preceding concentration theorems

After normalizing \(\min u_n=1\), the bubble height is of order
\(R_n^2/\lambda_n^2\to\infty\). Its residual remains in the bubble core.
Thus fixed-height residual escape occurs. The rescaled curvature becomes
flat relative to \(\lVert r_n\rVert_2\), and every fixed height-cut current
cancels. The action stays bounded away from zero. The family therefore
realizes, rather than evades, every necessity condition in RF-93--RF-95.

## Claim boundary

This theorem refutes only the all-field deterministic residual-gradient
floor. It does not show that these fields are typical under the interacting
Gibbs measure, collapse the full Witten one-form quotient, or make the actual
interacting \(H^{-1}\) moment diverge. It establishes no tightness result,
continuum measure, reflection-positive reconstruction, Born rule, Krein
interpretation, or LORENTZIAN-CAUSAL statement.

The next research gate is consequently probabilistic rather than
deterministic: determine the Gibbs cost and Witten response of the certified
Green-tail tube.

## Verification

    ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_euclidean_torus_green_tail_counterfamily.py --check
    ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_euclidean_torus_green_tail_counterfamily.py
    ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_green_tail_counterfamily
    ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -s reverse_physics/tests -p 'test_bt_euclidean_torus_*.py'

The producer passed 9/9 checks, the independent verifier passed 13/13, the
adversarial package passed 14/14 tests, and the complete affected torus rail
passed 143/143 tests.  The predecessor replay passed 11/11.  The exact
exponent verifier rejects a mutation of any defining scale.

The repository-wide Tier-3 rail was also run to completion under the pinned
Python 3.12.13 environment: 4,701 tests, 33 failures, zero errors and nine
skips in 1,040.13 seconds.  This is explicitly **not recorded as a pass**.
Thirty-two of the failing test IDs reproduce on the untouched source commit
`7b547b73`; the remaining order-dependent chain-scan test passes alone.  Thus
the affected rail shows no regression, while the inherited repository-wide
release rail remains non-green.  The certificate retains that distinction
rather than hiding the global failures.

Planning import accepted 1,721 nodes with no invalid item and no malformed
event.  The paper claim map passed its independent verifier and two
`pdflatex` passes produced the 87-page paper.  The advisory Science Forge
shadow exited zero but reported the existing Forge/stdlib `E9415` bridge
drift and a coverage-baseline drift; neither advisory result is evidence for
the theorem.

The C scout in reverse_physics/experiments/ is explicitly
hypothesis-generation only. No floating-point output is used by the
certificate or theorem.
