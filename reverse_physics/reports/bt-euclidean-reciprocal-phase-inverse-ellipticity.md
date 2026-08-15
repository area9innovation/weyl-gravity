# BT reciprocal-phase inverse ellipticity

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE

Lifecycle: NORMALIZED_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_PROVED

## Result

The apparent second-harmonic degeneracy in the normalized cosine--sine Ward
frame is controlled at the physical lowest-frequency scale. The control is
for the unregularized inverse matrix under the actual normalized BT Gibbs
measure.

On the periodic four-torus \(\Lambda_L=(\mathbb Z/L\mathbb Z)^4\), \(L\geq4\),
put

\[
 \pi_x={e^{-\psi_x}\over\sum_y e^{-\psi_y}},\qquad
 r_x=\sum_{y\sim x}{\pi_x\over\pi_y}-8,
\]

and define

\[
 z_2=\sum_x\pi_xe^{4\pi i x_\mu/L},\qquad
 c=|z_2|,\qquad \delta=1-c,\qquad
 s_L=\sin(2\pi/L).
\]

The new pointwise uncertainty theorem is

\[
 \boxed{\displaystyle
 \sum_x\pi_xr_x^2
 \geq {16s_L^4c^4\over\delta^2}.}
\]

For the complete lowest cosine--sine phase matrix

\[
 G_{ij}=\sum_x\pi_xh_i(x)h_j(x),
\]

the eigenvalues are \((1+c)/2\) and \((1-c)/2\). Thus

\[
                         \|G^{-1}\|_{\rm op}={2\over\delta}.
\]

Combining the pointwise theorem with the certified normalized Ward identity
gives

\[
 \mathbb E_{\mu_\lambda}\|G^{-1}\|_{\rm op}^2
 \leq16+
 {4\lambda^2(1-1/N)\over s_L^4}.
\]

Equivalently,

\[
 \boxed{\displaystyle
 \mathbb E_{\mu_\lambda}
 \left[\left(s_L^2\|G^{-1}\|_{\rm op}\right)^2\right]
 \leq16s_L^4+4\lambda^2(1-1/N)
 \leq16+4\lambda^2.}
\]

At \(\lambda=2/5\), the last bound is \(416/25\), uniformly in \(L\).
Since

\[
 s_L^2=\omega_L\cos^2(\pi/L),\qquad
 \omega_L=4\sin^2(\pi/L),
\]

and \(L\geq4\), this is the same scale as multiplying \(G^{-1}\) by the
lowest graph-Laplacian eigenvalue.

This controls the bare inverse phase factor at the expected scale. It does
not yet control its correlated products with the conjugate score or
connection derivative, the lowest field mode, or the interacting \(H^{-1}\)
moment.

## Reciprocal edge energy

Because \(\Omega\) is proportional to \(1/\pi\), the BT residual can be
written entirely on the open probability simplex:

\[
                         r_x=\sum_{y\sim x}{\pi_x\over\pi_y}-8.
\]

Its \(\pi\)-mean has an exact positive edge form. Pairing the two orientations
of each undirected edge gives

\[
 \begin{aligned}
 Q(\pi):=\sum_x\pi_xr_x
 &=\sum_{\{x,y\}}
 \left({\pi_x^2\over\pi_y}+{\pi_y^2\over\pi_x}
       -\pi_x-\pi_y\right)\\
 &=\sum_{\{x,y\}}
 {(\pi_x-\pi_y)^2(\pi_x+\pi_y)\over\pi_x\pi_y}.
 \end{aligned}
\]

Consequently \(Q(\pi)\geq0\), with equality only at the uniform probability
on a connected graph. Ordinary Cauchy--Schwarz over the probability \(\pi\)
then gives

\[
                         \sum_x\pi_xr_x^2\geq Q(\pi)^2.
\]

The reciprocal factors in \(Q\) are essential. Replacing this form with an
ordinary Hellinger energy would leave an artificial lattice-scale
regularization and would not control the genuine inverse of \(G\).

## Weighted phase uncertainty

If \(c>0\), choose \(\beta=\arg z_2\) and write

\[
                   \theta_x={4\pi x_\mu\over L}-\beta.
\]

Then

\[
             \sum_x\pi_x\cos\theta_x=c,\qquad
             \sum_x\pi_x(1-\cos\theta_x)=\delta.
\]

Let the sum below run over positive \(\mu\)-direction edges, once each.
Discrete summation by parts gives the exact identity

\[
 \left|\sum_x(\pi_{x+e_\mu}-\pi_x)
       \sin\left(\theta_x+{2\pi\over L}\right)\right|
 =2s_Lc.
\]

Apply Cauchy--Schwarz with the reciprocal edge form on one factor:

\[
 4s_L^2c^2\leq Q_\mu(\pi)B,
\]

where \(Q_\mu\leq Q\) is the \(\mu\)-edge part and

\[
 B=\sum_{\mu\text{-edges }\{x,y\}}
 {\,\pi_x\pi_y\over\pi_x+\pi_y}
 \sin^2\left({\theta_x+\theta_y\over2}\right).
\]

The decisive edge inequality is

\[
 {2ab\over a+b}\sin^2\left({u+v\over2}\right)
 \leq a(1-\cos u)+b(1-\cos v).
\]

To prove it, write

\[
 \sin\left({u+v\over2}\right)
 =\sin(u/2)\cos(v/2)+\cos(u/2)\sin(v/2)
\]

and apply weighted Cauchy--Schwarz with weights \(b,a\). Dropping the two
cosine squares then gives the displayed right side. Each vertex belongs to
two \(\mu\)-edges, so the factor \(1/2\) in the edge inequality cancels that
double incidence and yields

\[
                              B\leq\delta.
\]

Strict positivity of \(\pi\) and nonconstancy of the second-harmonic phase
give \(c<1\), hence \(\delta>0\). Therefore

\[
                 Q(\pi)\geq Q_\mu(\pi)
                 \geq {4s_L^2c^2\over\delta}.
\]

Squaring and using the site Cauchy inequality proves the boxed pointwise
theorem. If \(c=0\), its right side vanishes and the statement is immediate.

## Lift to the normalized Gibbs measure

The preceding theorem is deterministic. The normalized Ward-frame
certificate supplies the actual-Gibbs identity

\[
 \mathbb E_{\mu_\lambda}\sum_x\pi_xr_x^2
 =\lambda^2\mathbb E_{\mu_\lambda}
       \left(1-\sum_x\pi_x^2\right).
\]

Since \(\sum_x\pi_x^2\geq1/N\),

\[
 \mathbb E_{\mu_\lambda}{c^4\over\delta^2}
 \leq{\lambda^2(1-1/N)\over16s_L^4}.
\]

To remove the factor \(c^4\), split the normalized measure into
\(c<1/2\) and \(c\geq1/2\). On the first event \(\delta^{-2}\leq4\).
On the second, \(\delta^{-2}\leq16c^4\delta^{-2}\). Hence

\[
 \mathbb E_{\mu_\lambda}\delta^{-2}
 \leq4+{\lambda^2(1-1/N)\over s_L^4}.
\]

This is a true inverse moment, not an estimate for
\((G+\varepsilon I)^{-1}\). Substituting
\(\|G^{-1}\|_{\rm op}=2/\delta\) proves the volume-uniform scaled bound.

The same argument gives a lower-tail estimate. For \(0<u\leq1/2\),

\[
 \mathbb P_{\mu_\lambda}\{\delta\leq u\}
 \leq
 {\lambda^2(1-1/N)u^2\over
  16s_L^4(1-u)^4}.
\]

Thus configurations that make the phase matrix nearly rank one have a
quadratically small normalized tail after the correct frequency scaling.

## Exact tensor fixture

Take the periodic \(4^4\) torus and \(\varepsilon=1/10\). Put total
probability \(1-\varepsilon\) uniformly on the two even \(x_\mu\) slices and
total probability \(\varepsilon\) uniformly on the two odd slices. Every
even site then has probability \(9/1280\), and every odd site has probability
\(1/1280\).

The exact phase data are

\[
 c={4\over5},\qquad \delta={1\over5},\qquad s_L^2=1.
\]

The six transverse neighbors have the same probability as the center, so
only the two axial neighbors contribute:

\[
                     r_{\rm even}=16,\qquad
                     r_{\rm odd}=-{16\over9}.
\]

Direct summation gives

\[
 \sum_x\pi_xr_x^2={18688\over81},\qquad
 Q(\pi)={128\over9}.
\]

For the weighted phase Cauchy step,

\[
 B={9\over50},\qquad
 Q(\pi)B={64\over25}=(2s_Lc)^2.
\]

Thus weighted Cauchy is exactly saturated by this fixture. The final
pointwise lower bound is

\[
 {16c^4\over\delta^2}={4096\over25},
\]

and the exact ratio of the residual energy to this lower bound is

\[
                             {1825\over1296}>1.
\]

The simplex participation and diversity are \(41/6400\) and \(6359/6400\).
The independent verifier reconstructs the 256-site tensor counts, axial
ratios, edge harmonic factor, and every rational value without importing the
producer.

## Sharpness of the coefficient

Keep \(L=4\) but let \(0<\varepsilon<1/2\). The same alternating family has

\[
 c=1-2\varepsilon,\qquad\delta=2\varepsilon,
\]

\[
 r_{\rm even}={2c\over\varepsilon},\qquad
 r_{\rm odd}=-{2c\over1-\varepsilon},
\]

and

\[
 R_\pi=4c^2\left({1-\varepsilon\over\varepsilon^2}
                 +{\varepsilon\over(1-\varepsilon)^2}\right).
\]

The theorem's right side is \(4c^4/\varepsilon^2\), and their ratio is

\[
 {R_\pi\over4c^4/\varepsilon^2}
 ={(1-\varepsilon)+\varepsilon^3/(1-\varepsilon)^2\over c^2}
 \longrightarrow1.
\]

Therefore the universal coefficient \(16\) cannot be increased.

## Meaning for the reconstruction programme

The previous checkpoint left two possible failures entangled. The random
cosine--sine diffusion matrix might become almost rank one because the
reciprocal probability concentrates at one phase, or the associated
conjugate score might fail to be coercive. The new theorem separates them.

The first failure is now controlled: the unregularized inverse phase matrix
has the correct scaled second moment under the normalized interacting
measure. The remaining barrier is the score/operator side. The next
calculation should form the canonical two-phase marginal score

\[
 S_i=\sum_j(G^{-1})_{ij}Y_j
     -\sum_j X_{h_j}(G^{-1})_{ij},
\]

including the connection derivative. The newly proved inverse moment controls
the bare \(G^{-1}\) factor, but does not by itself prove integrability of
either correlated term. What is still needed is a joint integrability and
coercive or Witten-form estimate converting the canonical score into an
upper bound for the lowest Fourier field coordinate.

## Boundary

This result does not bound the canonical or original conjugate-score
quadratic form, the normalized lowest field mode, the interacting \(H^{-1}\)
moment, or its divergence. It establishes neither tightness nor a continuum
Euclidean measure. It does not change the existing scoped ordinary-OS
obstruction and has no Born, Krein, gravitational, or
LORENTZIAN-CAUSAL consequence. No literature-priority claim is made.

## Verification

Run sequentially under the 500 MB cap:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_reciprocal_phase_inverse_ellipticity.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_reciprocal_phase_inverse_ellipticity.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_reciprocal_phase_inverse_ellipticity

## Verification receipt

The final producer byte check passed in 0.04 seconds with peak RSS 20508 KiB.
The independent verifier passed all 17 checks in 0.10 seconds with peak RSS
29944 KiB. All 11 focused tests passed in 0.12 seconds with peak RSS 30812
KiB, including seven adversarial certificate mutations. Python compilation
passed in 0.04 seconds with peak RSS 15628 KiB. Every Python command ran under
the 500 MB virtual-memory cap.

The Science Forge planning import passed with 1671 nodes, zero invalid items,
and zero malformed events in 8.25 seconds with peak RSS 201740 KiB under
GOMEMLIMIT=300MiB and GOGC=50. Tier 2 uses the unchanged, content-addressed
normalized Ward-frame and finite-volume OS-obstruction inputs. Tier 3 was not
run because the lowest field moment, interacting \(H^{-1}\) estimate, and
continuum lifecycle states remain open. The Science Forge shadow rail was
skipped because no registered shadow input changed; that skip is not recorded
as a pass.
