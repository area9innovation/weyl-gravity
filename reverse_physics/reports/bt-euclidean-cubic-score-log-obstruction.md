# BT cubic-score logarithmic obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `FIXED_ORDER_VOLUME_UNIFORM_SCORE_ROUTE_OBSTRUCTED`

## Result

The first nonlinear coefficient of the missing annealed score estimate is not
uniform in four-dimensional lattice size.  For the lowest real
cosine mode, its free-Gaussian coefficient obeys the rigorous bound

\[
 C_L\geq \frac{J_L}{4665600},\qquad
 J_L=\#\{j\geq0:16\,2^j\leq L\}.
\]

Thus $C_L$ grows at least logarithmically.  This obstructs a proof which
expands at fixed bare coupling and bounds each perturbative coefficient
uniformly in $L$.

It does **not** prove that the full interacting score or moment diverges.
Running coupling, wave-function renormalization, cancellations between
orders, or a genuinely nonperturbative estimate remain possible.

## Exact lattice vertex

Write

\[
 S_\lambda(\phi)=\frac1{2\lambda^2}\sum_xR_x(\lambda\phi)^2,
 \qquad
 R_x(\psi)=\sum_{\delta}\left(e^{\psi_{x+\delta}-\psi_x}-1\right),
\]

where the sum is over directed nearest neighbours.  With
$\phi_x=N^{-1/2}\sum_kz_ke^{ikx}$ and

\[
 \omega_k=4\sum_{j=1}^4\sin^2(k_j/2),
\]

the cubic action is

\[
 S_\lambda^{(3)}=\frac{\lambda}{6\sqrt N}
 \sum_{p+q+r=0}V_3(p,q,r)z_pz_qz_r,
\]

where, for $a=\omega_p$, $b=\omega_q$, and $c=\omega_r$,

\[
 V_3=a^2+b^2+c^2-2(ab+ac+bc).
\]

The three numbers $\sqrt a,\sqrt b,\sqrt c$ obey the triangle inequalities
for $p+q+r=0$.  Heron's identity therefore gives

\[
 V_3=-16\mathcal A^2\leq0,
 \qquad |V_3|\leq4\min(ab,ac,bc).
\]

This is the exact lattice version of the derivative factor on every
interaction leg.  The logarithm below is not caused by losing that soft
factor; it is caused by summing the remaining marginal four-dimensional
phase space.

An independent position/Fourier normalization fixture uses
$\phi_x=\cos(\pi x_1/2)+\cos(\pi x_2/2)+
\cos(\pi(x_1+x_2)/2)$ on the $4^4$ lattice.  Directly evaluating
$\frac12\sum_x\Delta\phi_x\sum_\delta(\phi_{x+\delta}-\phi_x)^2$ gives
$-1024$.  Its six Fourier modes, twelve ordered resonant triples, amplitude
$8$, and vertex $-16$ reproduce the same value from the momentum formula.

## Leading zero-fiber score

At $\lambda=0$, the background is the free mean-zero Gaussian restricted to
the hyperplane orthogonal to the real external cosine.  Before that one-mode
projection, the first nonlinear complex score is

\[
 Q_p=\frac1{2\sqrt N}\sum_q
 V_3(p,q,-p-q)z_qz_{-p-q}.
\]

Wick contraction and conversion to the real cosine coordinate give

\[
 \operatorname{Var}_{0}[V_\eta'(0)]
 =\lambda^2N\omega_p^2C_L+O(\lambda^3),
\]

with the unprojected reference sum

\[
 C_L^{\rm full}=\frac1{4N\omega_p^2}
 \sum_{q\ne0,-p}
 \frac{V_3(p,q,-p-q)^2}
 {\omega_q^2\omega_{p+q}^2}.
\]

The orthogonal-background coefficient is $C_L=C_L^{\rm full}-\delta_L$.
Here $\delta_L$ removes the real external-cosine/internal-doubled-mode block:
it equals
$V_3(p,p,-2p)^2/(4N\omega_p^4\omega_{2p}^2)$ for $L>4$ and twice this at
$L=4$, where $2p$ is self-conjugate.  The momentum boxes used below avoid
this block, so the projection changes the finite-size values but not the
logarithmic lower bound.

## Exact logarithmic lower bound

Take $p=(1,0,0,0)$ in integer momentum units.  For every dyadic
$M=1,2,4,\ldots$ with $16M\leq L$, select the $M^4$ momenta

\[
 q_1\in[M,2M),\quad q_2\in[4M,5M),\quad
 q_3,q_4\in[0,M).
\]

Write $\omega_q=x+u$ and $\omega_{p+q}=y+u$, separating the axial and
transverse dispersions.  Direct algebra gives

\[
 V_3(\omega_p,x+u,y+u)=V_3(\omega_p,x,y)-4\omega_pu
 \leq-4\omega_pu.
\]

The last inequality is again the one-dimensional Heron inequality.  The
elementary bounds $\sin s\geq2s/\pi$, $\sin s\leq s$, and $\pi^2<10$ give

\[
 256\frac{M^2}{L^2}\leq u\leq1080\frac{M^2}{L^2},
 \qquad x,y\leq u.
\]

Every box therefore contributes at least $1/4665600$ to $C_L$.  The boxes
are disjoint, avoid the removed cosine block, and are independent nonnegative
Gaussian quadratic blocks.  This proves the stated logarithmic lower bound.

## Finite-sum diagnostic

The direct binary64 sums are supporting only:

| $L$ | $C_L$ | $C_L/\log L$ |
|---:|---:|---:|
| 4 | 0.06377 | 0.04600 |
| 6 | 0.08175 | 0.04563 |
| 8 | 0.09293 | 0.04469 |
| 12 | 0.10765 | 0.04332 |
| 16 | 0.11757 | 0.04240 |
| 24 | 0.13109 | 0.04125 |
| 32 | 0.14047 | 0.04053 |

The exact theorem establishes unboundedness; the table only shows that the
asymptotic mechanism is already visible at small sizes.

## Consequence for the programme

The physical reading of the logarithm depends on scale setting: at fixed
physical torus size it is a refinement/ultraviolet logarithm, while at fixed
lattice spacing it accompanies the soft lowest-momentum/large-volume limit.
The correct next calculation must declare that branch.  For matched physical
volume we need the finite-volume Ward/RG identity and must test whether the
asymptotically free trajectory keeps $\lambda_L^2C_L$ bounded; at fixed
spacing we need the corresponding uniform soft-volume control.  Either
perturbative matching still would not be a Gibbs theorem.  A nonperturbative
multiscale estimate must then control the background marginal before the
lowest-mode and Fourier-shell gates can close.

The annealed score bound, normalized interacting lowest-mode moment,
interacting $H^{-1}$ moment, tightness, continuum identification, Born rule,
Krein reconstruction, and every `LORENTZIAN-CAUSAL` claim remain open.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_cubic_score_log_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_cubic_score_log_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_cubic_score_log_obstruction
```

## Verification receipt

On the final tree, the deterministic producer byte check passed in 0.39
seconds (20868 KB), the independent direct-sum verifier passed in 1.23 seconds
(29352 KB), and all eight focused tests passed in 3.93 seconds (30388 KB).
The Paper 21 authority/hash/boundary verifier passed in 0.07 seconds (26920
KB).  Its two final `pdflatex -interaction=batchmode -halt-on-error` passes
each took 0.74 seconds, at 53724 KB and 53544 KB peak RSS.

Tier 0 Python compilation passed in 0.05 seconds (19472 KB).  The first
memory-capped `git diff --check` invocation could not create Git's preload
thread and is recorded as a failure, not a pass; the retry
`git -c core.preloadindex=false diff --check` passed in 0.09 seconds (12888
KB).  The affected Tier 2 chain comprised the center reduction, this
successor, the Paper 21 claim-map generator, generated map, independent paper
verifier, and PDF.  Tier 3 was not run because this is a scoped working-draft
method obstruction, not a freeze, release, shared-core change, or promotion
of a quantum lifecycle state.

The read-only Science Forge shadow rail exited advisory-pass but reported a
fail-closed bridge audit caused by a Forge binary/stdlib hash mismatch and
compiler error `E9118`, plus corpus-count drift (1659 certificates versus the
2026-07-19 baseline of 976).  These are advisory substrate/baseline findings;
they are not counted as passing verification of this certificate.
