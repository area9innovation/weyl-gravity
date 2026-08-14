# BT conditional-mass escape obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

The BT lowest-mode marginal cannot be proved by bounding the raw conditional
second moment uniformly over every orthogonal background. On the fixed
periodic (6^4) lattice there is an exact sequence of backgrounds for which
the global fiber minima and almost all conditional probability move farther
and farther from the coordinate origin.

For every integer (m\geq2), define

\[
 a=(-1,-1,1,-3,3,1),\qquad
 h=(2,1,-1,-2,-1,1),
\]

and take

\[
 \eta_m=4m\log2\,a,\qquad t=u\log2.
\]

The background is mean zero and orthogonal to the lowest time-circle mode
(h). Let (q_m(u)) be the normalized one-dimensional Gibbs density along
the fiber (eta_m+(u\log2)h). Then

\[
 q_m\{u\geq-m\}\leq2^{-m}.
\]

Every global minimizer (u_m^*) of the fiber action satisfies (u_m^*<-m),
and

\[
 \mathbb E_{q_m}[u^2]\geq m^2(1-2^{-m}).
\]

Thus the background-uniform raw conditional second moment is unbounded even
at fixed volume. This is stronger than merely exhibiting a cheaper distant
point.

It is not divergence of the fully integrated marginal. The exceptional
backgrounds can receive extremely small marginal Gibbs weight. The live
problem is now cleanly split into a recentered conditional-width estimate and
an annealed estimate for the moving centers.

## Exact fiber

The fields are constant in the three spatial directions. Their full action is
(216) times the six-site time-cycle action

\[
 A_m(u)=\frac12\sum_{j=0}^{5}
 \left(2^{k_{j-1}(u)-k_j(u)}
       +2^{k_{j+1}(u)-k_j(u)}-2\right)^2,
\]

where

\[
                         k_j(u)=4m a_j+u h_j.
\]

At coupling (lambda=2/5), the full conditional weight is therefore

\[
                         e^{-1350 A_m(u)}\,du.
\]

The earlier centered-fiber certificate used the point (u=-4m). At this
point the coefficient vector is (4m(a-h)), with

\[
                      a-h=(-3,-2,2,-1,4,0).
\]

Its largest adjacent jump has absolute value five.

## Right-tail action barrier

Write (u=-m+v), with (v\geq0). At time site three, the exact residual is

\[
                  r_3=2^{16m+u}+2^{24m+u}-2.
\]

Consequently

\[
 r_3\geq2^{23m+v-1},\qquad
 A_m(-m+v)\geq 2^{46m-3}4^v=:C_m4^v.
\]

The elementary real inequality (4^v\geq1+v) now gives

\[
 \int_{-m}^{\infty}e^{-1350A_m(u)}\,du
 \leq \frac{e^{-1350C_m}}{1350C_m}.
\]

The logarithmic coordinate Jacobian is constant and cancels from normalized
probabilities.

## A certified well far from the origin

Put

\[
                 \delta_m=2^{-50m}.
\]

On (|u+4m|\leq\delta_m), every directed edge exponent has absolute value at
most (20m+2). Hence each residual is bounded by
(9\,2^{20m}), and

\[
                  A_m(u)\leq243\,2^{40m}=:M_m.
\]

The fiber normalization therefore obeys

\[
 Z_m\geq2\delta_m e^{-1350M_m}.
\]

For (m\geq2),

\[
 \frac{C_m}{M_m}
 =\frac{2^{6m-3}}{243}
 \geq\frac{512}{243}>1.
\]

Thus a point in the distant well has action below the action of every point
with (u\geq-m), proving (u_m^*<-m) for every global minimizer.

## Conditional probability comparison

Let

\[
 D_m=1350(C_m-M_m).
\]

The upper tail divided by the well lower bound gives

\[
 q_m\{u\geq-m\}
 \leq 2^{50m-1}e^{-D_m}
 \leq2^{50m-1-D_m}.
\]

Here (e>2). Also

\[
 D_m
 =1350\,2^{40m}(2^{6m-3}-243)
 \geq1350\cdot269\,m>51m,
\]

where (2^{40m}\geq m). It follows that the tail probability is at most
(2^{-m}). Since (u^2\geq m^2) on (u<-m), the displayed conditional
second-moment lower bound follows.

## What this changes

The preceding certificate ruled out a comparison with the action at (u=0).
The present theorem shows that this was not an artifact of selecting one
non-minimizing distant point:

- every global fiber minimum escapes the centered interval on this family;
- the normalized conditional mass escapes with it;
- no constant can bound the uncentered conditional second moment uniformly in
  the orthogonal background.

The appropriate decomposition for the actual marginal is therefore

\[
 \mathbb E[t^2]
 =\mathbb E[\operatorname{Var}(t\mid\eta)]
  +\mathbb E[(\mathbb E[t\mid\eta])^2].
\]

The first term requires a width estimate after moving with the fiber. The
second requires an annealed estimate under the marginal background weight.
Neither is proved here.

## Foundations consequence

The vectors, dyadic action fixtures, and all-(m) exponent comparisons are
finite exact arithmetic. The conditional probability estimate additionally
uses finite-dimensional coercive integration and the elementary inequalities
(4^v\geq1+v) and (e>2). No compactness or continuum selection is used.

This gives a precise dependency cut between the exact finite obstruction and
the still-missing volume-uniform analytic theorem. It does not establish a
weakest base or reverse-mathematical reversal.

## Boundaries

This certificate does not establish divergence of the integrated lowest-mode
marginal, divergence of the interacting (H^{-1}) moment, failure of a
uniformly recentered conditional variance, failure of an annealed center
estimate, tightness, a continuum Euclidean measure, a Born rule, a Krein
reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

Run sequentially:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_conditional_mass_escape_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_conditional_mass_escape_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_conditional_mass_escape_obstruction
```
