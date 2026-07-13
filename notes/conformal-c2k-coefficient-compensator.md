# C2k: coefficient triangle and compensator bifurcation

## Why this checkpoint is needed

The rational number $199/30$ occurs in several related calculations, but the
objects carrying it must not be identified without an explicit convention
map.  We distinguish

\[
b_C^{\rm div},\qquad
\beta_t,\qquad
c_{\rm trace},\qquad
{\cal A}_{\rm BV}.
\]

They denote, respectively, a loop-divergence coefficient, a coupling beta
function, the coefficient of $C^2$ in a background trace anomaly, and a
ghost-number-one quantum-master-equation obstruction.  A determinant on a
background plus a classification of possible local anomaly classes does not
by itself compute the last object in the repository's BV conventions.

This checkpoint fixes the conversion between the first three and leaves the
fourth fail-closed.

## Signed counterterm and beta function

Write

\[
S=\kappa x I_C,\qquad
x={1\over t^2},\qquad
I_C=\int d^4x\sqrt{|g|}\,C^2,
\]

and continue to $d=4-\rho\epsilon$ with

\[
x_B=\mu^{-\rho\epsilon}
\left[
x+{k_{\rm ct}\over
\kappa(4\pi)^2\epsilon}
\right].
\]

Here $k_{\rm ct}$ is the **signed coefficient added to the action**.  If the
loop effective action contains

\[
\Gamma_{\rm div}^{(1)}
= {b_C^{\rm div}\over(4\pi)^2\epsilon}I_C,
\]

then cancellation means $k_{\rm ct}=-b_C^{\rm div}$.  Differentiating the
bare coefficient gives

\[
\boxed{
\beta_x={\rho k_{\rm ct}\over\kappa(4\pi)^2},
\qquad
\beta_t=-{\rho k_{\rm ct}\over2\kappa(4\pi)^2}t^3.}
\]

This formula isolates both the action normalization and the counterterm
sign.  For a fixed numerator $K$ and $\rho=1$, the comparison normalization
suggested for C2k gives

\[
\kappa={1\over2}
\quad\Longrightarrow\quad
{|\beta_t|\over t^3}={K\over(4\pi)^2},
\]

whereas the coefficient of magnitude $1/t^2$ used by Hamada gives

\[
\kappa=1
\quad\Longrightarrow\quad
{|\beta_t|\over t^3}={K\over2(4\pi)^2}
={K\over32\pi^2}.
\]

Thus the factor of two is exactly the change from $1/t^2$ to $1/(2t^2)$.
Hamada's Lorentzian action also has an overall sign, so signs should be
compared only after the Wick and counterterm conventions are aligned
([arXiv:1202.4538](https://arxiv.org/abs/1202.4538)).

## Evanescent Weyl variation

Declare the continuation convention

\[
\delta_\sigma I_C^{(d)}
=\rho\epsilon\,\Sigma_C,
\qquad
\Sigma_C=\int d^4x\sqrt{|g|}\,\sigma C^2.
\]

Then the pole counterterm has the finite variation

\[
\delta_\sigma S_{\rm ct}
={\rho k_{\rm ct}\over(4\pi)^2}\Sigma_C.
\]

If one instead quotes the loop divergence $b_C^{\rm div}=-k_{\rm ct}$, the
displayed sign reverses.  This is the precise pole-times-evanescence
mechanism used to derive the dilaton Wess--Zumino action in dimensional
regularization
([Baume--Keren-Zur, arXiv:1307.0484](https://arxiv.org/abs/1307.0484)).

Tseytlin's isolated conformal spin-two determinant gives

\[
a_2={87\over20},\qquad c_2={199\over30}
\]

in its background-anomaly convention
([arXiv:1309.0785](https://arxiv.org/abs/1309.0785)).  Hamada uses $199/30$
as the traceless-tensor contribution to a beta-function numerator and adds
$-1/15$ from his Riegert sector.  The exact arithmetic

\[
{199\over30}-{1\over15}={197\over30}
\]

does not erase the normalization map above.

## What is not yet a BV theorem

Local BRST cohomology classifies

\[
[c_{\rm W}C^2],\qquad[c_{\rm W}E_4]
\in H^{1,4}(s\mid d)
\]

as possible nontrivial Weyl anomalies; in particular, the type-A class has
nontrivial descent
([Boulanger, arXiv:0704.2472](https://arxiv.org/abs/0704.2472)).  This
classification does not determine their loop coefficients.  The repository
therefore records

\[
{\cal A}_{\rm BV}
=A_C[c_{\rm W}C^2]+A_E[c_{\rm W}E_4]+\cdots
\]

with $A_C,A_E$ **undetermined** until the one-loop master equation is
evaluated in the same field, ghost, measure, and action conventions.

Accordingly, the literature-seeded row

\[
\left({199\over30},0\right)
\]

is presently a target/background type-B projection in the even/odd residual
basis, not a direct machine derivation of $(A_C,A_E)$ and not yet a proof that
$Q_{\rm quantum}^2\ne0$.

## Minimal type-B compensator extension

Adjoin a compensator with, modulo the diffeomorphism terms,

\[
s\tau=c_{\rm W},\qquad sc_{\rm W}=0.
\]

Since $C^2$ is Weyl invariant in four dimensions,

\[
s(\tau C^2)=c_{\rm W}C^2.
\]

Thus $[c_{\rm W}C^2]$ becomes exact in the **extended** local complex.  The
type-B Wess--Zumino term is

\[
\Gamma_{\rm WZ,B}=c\int d^4x\sqrt{|g|}\,\tau C^2
\]

up to the chosen BRST and anomaly signs.

On the conformally flat cylinder, $\bar C=0$, so

\[
\tau C^2=\tau\,[C^{(1)}(h)]^2+O(4)
\]

begins at total field degree three.  The type-B Wess--Zumino term by itself
does not alter the quadratic metric/compensator Hessian around
$\bar\tau=0$.  This degree count is **not** a proof that the complete free
BRST complex or its $I_2$ pairing is unchanged after all anomaly sectors are
included.

## Type A changes the cylinder free problem

In the Baume--Keren-Zur convention the four-dimensional Wess--Zumino action
contains

\[
\Gamma_{\rm WZ}
=\int\sqrt{|g|}\left\{
c\tau C^2
-a\left[
\tau E_4
+4G^{\mu\nu}\partial_\mu\tau\partial_\nu\tau
-4(\Box\tau)(\partial\tau)^2
+2(\partial\tau)^4
\right]\right\}.
\]

For the unit/general-radius product cylinder, $k=r^{-2}$,

\[
R_{\mu\nu\rho\sigma}^2=12k^2,
\quad R_{\mu\nu}^2=12k^2,
\quad R=6k,
\]

so

\[
\bar C^2=0,\qquad\bar E_4=0,
\]

but

\[
\bar G^{tt}=-3\eta k,\qquad
\bar G^{ij}=-k\bar g^{ij}
\]

is nonzero, where $\eta=\pm1$ is the time signature.  The pure-compensator
quadratic block is therefore

\[
\boxed{
\Gamma_A^{(2)}\big|_{\tau\tau}
=-4a\int\sqrt{|\bar g|}\,
\bar G^{\mu\nu}\partial_\mu\tau\partial_\nu\tau.}
\]

For Lorentzian mostly-plus signature this isolated block has

\[
\left(3k\partial_t^2-k\Delta_{S^3}\right)\tau=0,
\qquad
\omega_l^2={k\,l(l+2)\over3}.
\]

There is also a possible quadratic mixed term

\[
-a\int\sqrt{|\bar g|}\,\tau E_4^{(1)}[h].
\]

Hence the displayed scalar frequency is only the $\tau\tau$ subblock, not a
physical-mode classification.  The complete gauge-fixed $h$--$\tau$ Hessian,
local BRST kernel, centered inventory, and reduced pairing must all be
recomputed for the full type-A/type-B completion.

## CHS historical precision

Tseytlin's 2013 calculation records the zeta-regularized vanishing of the
complete bosonic CHS $a_s$ sum under its stated prescription; its $c_s$
analysis retained a prescription ambiguity.  The later conically deformed
sphere calculation selects the $r=-1$ prescription and reports vanishing
regularized sums of both $a_s$ and $c_s$, together with the full
$S^4_q$ logarithmic divergence
([Beccaria--Tseytlin, arXiv:1707.02456](https://arxiv.org/abs/1707.02456)).
Neither free one-loop regularized result proves anomaly cancellation in a
complete interacting CHS theory.

## Exact certificate boundary

Run

```bash
python3 symbolic/verify_conformal_coefficient_triangle.py
```

The script verifies:

1. the general $\kappa$-dependent beta conversion;
2. the exact factor of two between the two action normalizations;
3. the pole-times-evanescence relation with an explicit signed counterterm;
4. separation of beta, background-trace, and unknown BV coordinates;
5. exact type-B trivialization after adjoining $\tau$;
6. the cylinder curvature invariants and Einstein tensor;
7. the type-B perturbative degree and nonzero type-A $\tau\tau$ block; and
8. the isolated $\tau$ harmonic frequency.

Fail-closed flags reject a direct BV coefficient, quantum BRST obstruction,
complete mixed Hessian, inherited $I_2$, full anomaly cancellation, and
interacting-CHS anomaly freedom.
