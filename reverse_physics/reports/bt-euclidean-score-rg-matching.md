# BT score logarithm and RG matching

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `COEFFICIENT_COMPUTED`

## Result

The logarithm found in the first nonlinear lowest-mode score is exactly of
the size compensated by asymptotic freedom on a fixed-physical-volume
continuum trajectory.  The analytic lattice asymptotic is

\[
 C_L=\frac{5}{16\pi^2}\log L+O(1).
\]

If $g$ denotes the unrescaled coupling multiplying $(\partial\phi)^2$ in the
perfect-square operator, its beta function begins

\[
 \beta_g=-\frac{5}{16\pi^2}g^3
         -\frac{15}{128\pi^4}g^5+O(g^7).
\]

Consequently a trajectory with inverse lattice spacing proportional to $L$
has

\[
 g_L^2\log L\longrightarrow\frac{8\pi^2}{5},
 \qquad
 g_L^2C_L\longrightarrow\frac12.
\]

Thus the leading logarithm does not obstruct the tuned continuum branch.  It
becomes a finite, nonzero contribution.  This is a coefficient calculation,
not an all-order resummation and not a nonperturbative Gibbs estimate.
The equality of the score residue and the physical one-loop beta coefficient,
both $5/(16\pi^2)$, is exact in the declared normalization; it is the key
reason the matched limit simplifies to $1/2$.

## Logarithmic residue

In the scaling annulus $p\ll |q|\ll1$, the lattice dispersion tends to the
continuum norm and the exact lattice vertex has leading form

\[
 V_3(p,q,-p-q)
 =-4\bigl(p^2q^2-(p\mathbin\cdot q)^2\bigr)+\text{higher lattice orders}.
\]

After the real-cosine normalization used by the predecessor certificate, the
summand becomes

\[
 \frac{V_3^2}{4p^4q^4(p+q)^4}
 =\frac{4\sin^4\theta}{|q|^4}
  +\text{integrable remainder}.
\]

For a uniform direction on $S^3$,

\[
 \mathbb E[\cos^2\theta]=\frac14,qquad
 \mathbb E[\cos^4\theta]=\frac18,qquad
 \mathbb E[\sin^4\theta]=\frac58.
\]

Using $|S^3|=2\pi^2$ and the Fourier measure
$d^4q/(2\pi)^4$ gives

\[
 4\frac58\frac{2\pi^2}{(2\pi)^4}
 =\frac{5}{16\pi^2}.
\]

To control the remainder, split momentum space into $|q|=O(p)$, the scaling
annulus, and a region bounded away from zero.  The inner rescaling and the
outer smooth region each contribute $O(1)$.  In the annulus, Taylor errors in
the lattice symbol integrate to $O(1)$.  On dyadic shells of radius $r$, the
mesh-to-integral error is $O(p/r)$; those errors are summable.  The
orthogonal-background correction that removes the real external cosine is
$O(L^{-4})$.  These bounds leave only the displayed logarithm.

The independently verified finite sums support the residue:

| pair | $(C_{2L}-C_L)/\log2$ | divided by $5/(16\pi^2)$ |
|---:|---:|---:|
| $4\to8$ | 0.04207 | 1.329 |
| $6\to12$ | 0.03736 | 1.180 |
| $8\to16$ | 0.03555 | 1.123 |
| $12\to24$ | 0.03381 | 1.068 |
| $16\to32$ | 0.03303 | 1.043 |

These binary64 slopes are supporting only; the annular argument determines
the coefficient.

## Coupling normalization

[Anderson, Bateman, Herzog and Turok](https://arxiv.org/abs/2608.12210)
define their renormalized cubic coupling with

\[
 \lambda_{3,b}=(4\pi)\mu^{\varepsilon/2}Z_3\lambda_{3,r}.
\]

On the perfect-square trajectory they write $\lambda_3=-\lambda$ and obtain

\[
 \beta_\lambda=-5\lambda^3-30\lambda^5+O(\lambda^7)
 \quad(\varepsilon=0).
\]

The lattice exponential coupling is the unrescaled coefficient
$g=4\pi\lambda$ at leading matching order.  Converting the beta function
therefore gives the coefficients displayed above.  The repository's earlier
one-loop RG certificate independently records
$\beta_g=-5g^3/(16\pi^2)$ in this physical normalization.

The two-loop solution is

\[
 g_L^2=\frac{8\pi^2}{5\log L}
 \left[1-\frac35\frac{\log\log L}{\log L}
 +O\left(\frac1{\log L}\right)\right],
\]

where the nonlogarithmic part of the last term is scheme dependent.

The imported Ward identity is

\[
 Z_3Z_\sigma^{1/2}=Z_4Z_\sigma=1,
 \qquad \gamma_\sigma=\frac{\beta_g}{g}
 \quad(\varepsilon=0).
\]

With the standard field RG equation
$\mu,d\sigma/d\mu=-\gamma_\sigma\sigma$, it follows that $g\sigma$ is RG
invariant.  This is exactly the exponential field variable appearing in the
positive lattice action.  It identifies the natural renormalized coordinate,
but it does not by itself control its Gibbs distribution.

## The two limits are different

For fixed physical torus size, decreasing the lattice spacing makes the
cutoff scale grow like $L$.  The asymptotically free tuning above is then the
relevant continuum trajectory and compensates the leading score logarithm.

For fixed lattice spacing, increasing $L$ instead increases physical volume
and sends the lowest external momentum to zero while the ultraviolet cutoff
and its bare coupling remain fixed.  One may not insert $g_L^2\sim1/\log L$
in that problem.  The source's perturbative infrared-finiteness theorem holds
for off-shell correlators at fixed nonzero external momentum; it does not
provide a bound uniform in the lowest momentum as it tends to zero.

Therefore this certificate restores the leading-log continuum-refinement
route but leaves the fixed-spacing large-volume estimate open.

## The ordinary lattice Ward identity lands on the wrong score

There is an exact nonperturbative finite-volume equation-of-motion identity.
For every fixed mean-zero direction $h$,

\[
 \mathbb E_\mu[(D_hS_g(\phi))^2]
 =\mathbb E_\mu[D_h^2S_g(\phi)].
\]

Equivalently, on every conditional fiber,

\[
 \mathbb E_{q_\eta}[V_\eta'(T)^2]
 =\mathbb E_{q_\eta}[V_\eta''(T)].
\]

Both follow by integrating the derivative of score times Boltzmann weight;
finite-volume coercivity removes the boundary term.  This identity evaluates
the score at the sampled $T$.  The center reduction instead requires the
score at the fixed coordinate zero, $V_\eta'(0)$.

The distinction cannot be removed by a general argument.  For

\[
 V_R(t,y)=\frac\kappa2(t-y)^2+\frac{y^2}{2R^2}
\]

with $(\kappa,R)=(2,5)$, the conditional full-score variance and expected
Hessian are both exactly $2$, while the annealed zero-fiber-score variance is
$100$.  Thus the ordinary Ward identity may be perfectly controlled while
the moving-center score is large.  This is a logical no-transfer theorem,
not an obstruction to an additional identity using BT locality.

## What remains

The next object is a specifically BT identity for the conditional zero-fiber
score as a projected composite insertion; the ordinary equation-of-motion
identity is insufficient.  It must decide
the all-order leading logarithms of that specific background-marginal
observable.  Even an all-order perturbative bound would still require a
nonperturbative multiscale estimate for the tuned lattice Gibbs measure.

No all-order score bound, nonperturbative center bound, integrated lowest-mode
moment, interacting $H^{-1}$ estimate, tightness, continuum identification,
Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_score_rg_matching.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_score_rg_matching.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_score_rg_matching
```

## Verification receipt

On the final tree, the deterministic producer byte check passed in 0.04
seconds (20620 KB), the independent verifier passed in 0.09 seconds (29316
KB), and all nine focused tests passed in 0.11 seconds (30680 KB).  Tier 0
Python compilation passed in 0.08 seconds (19684 KB), structured JSON parsing
passed in 0.03 seconds (14616 KB), and
`git -c core.preloadindex=false diff --check` passed in 0.04 seconds (11344
KB).

The affected Tier 2 chain included the predecessor cubic-score and RG
certificates, the new source transcription, the Paper 21 claim-map generator,
generated map, independent paper verifier, and PDF.  The paper verifier passed
in 0.07 seconds (26896 KB); the final two capped `pdflatex` passes each took
0.75 seconds, with peak RSS 53596 KB and 53752 KB.  Planning import produced
1609 nodes with zero invalid items and zero malformed events in 7.7 seconds.
Tier 3 was not run because this is a scoped working-draft coefficient and
method result, not a freeze, tag, or release.

One initial paper-generation command was run from `paper/` while retaining a
`paper/...` path and failed immediately with file-not-found.  It is recorded
as a failure, not a pass; the corrected root-relative generator/checker chain
is the passing Tier 2 receipt above.

The read-only Science Forge shadow rail exited advisory-pass but again
reported a fail-closed bridge audit caused by a Forge binary/stdlib hash
mismatch and compiler error `E9118`, plus corpus drift (1660 certificates
versus the 2026-07-19 baseline of 976).  These advisory substrate findings are
not counted as verification of this certificate.
