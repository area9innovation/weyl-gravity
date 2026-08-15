# BT finite-volume twist-response gate

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_TWIST_RESPONSE_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The $p^2$ coefficient found in the expected Hessian is only the positive
half of a physical twist response.  This checkpoint derives the complete
finite-volume identity and measures the missing subtraction.

Insert a uniform real twist $\theta$ on the positive and negative bonds of
axis $\mu$:

\[
 r_x(\theta)=t_{x,x+e_\mu}e^\theta
 +t_{x,x-e_\mu}e^{-\theta}
 +\sum_{y\sim x,\,y-x\perp e_\mu}t_{xy}-2D,
\]

where $t_{xy}=e^{\psi_y-\psi_x}$, and put

\[
 A_\theta=\frac12\sum_xr_x(\theta)^2.
\]

The first two derivatives are

\[
 I_\mu=A_\theta'(0)
 =\sum_xr_x(t_{x,x+e_\mu}-t_{x,x-e_\mu})
 =\sum_xJ_{x,\mu},
\]

and

\[
 D_\mu=A_\theta''(0)
 =\sum_x\left[(t_+-t_-)^2+r_x(t_++t_-)\right].
\]

Thus $I_\mu$ is exactly the zero mode of the certified weighted current.
Hypercubic reflection gives $\mathbb E I_\mu=0$.

For

\[
 Z_L(\theta)=\int_H e^{-A_\theta/\lambda^2}\,d\psi,
 \qquad
 f_L(\theta)=-\frac1N\log Z_L(\theta),
\]

differentiation under the finite-volume integral gives

\[
 \boxed{
 \lambda^2 f_L''(0)
 =\frac1N\mathbb E D_\mu
 -\frac{1}{N\lambda^2}\operatorname{Var}(I_\mu)
 =\alpha_L-\chi_L.}
\]

Here

\[
 \chi_L=\frac{\operatorname{Var}(I_\mu)}{N\lambda^2}\geq0.
\]

The axis average of $\mathbb E D_\mu/N$ is exactly the previously certified

\[
 \alpha_L=-(b_L+4c_L+6d_L).
\]

This identification is not inferred from the numerical fixture.  Put
$U=\mathbb E[t_+^2]$, $V=\mathbb E[t_+t_-]$, let $W$ be a product of two
distinct oriented axes, and put $R=\mathbb E[r t_+]$.  The identity
$s=q+r=\sum t$ gives

\[
 q\mathbb E[t_+]+R=U+V+(2D-2)W.
\]

The orbit formula first gives

\[
 \alpha=2q\mathbb E[t_+]+4R-4V-4(D-1)W.
\]

Substitution cancels $W$ and yields

\[
 \alpha=2U-2V+2R=\mathbb E[D_\mu]/N,
\]

which proves the general finite-volume equality.

Consequently, $\alpha_L$ by itself is a diamagnetic curvature, not a
helicity modulus or physical stiffness.  The only unconditional sign relation
is

\[
                     \lambda^2f_L''(0)\leq\alpha_L.
\]

## Exact fixture

On $C_6\times C_6$, use the positive profile
$(1,2,1,1/2,1,1)$ along the first axis.  Exact rational differentiation
gives

\[
 (I_1,I_2)=(0,0),
 \qquad
 \left(\frac{D_1}{N},\frac{D_2}{N}\right)
 =\left(\frac73,\frac23\right).
\]

Their axis average is $3/2$, exactly matching the expected-Hessian fixture
coefficient.  This checks the local-symbol/twist identification without
floating-point arithmetic.

## Full-Gibbs observation

The independent local Metropolis chain measured both terms at
$\lambda=0.4$:

| $L$ | $\alpha_L$ | $\chi_L$ | $\lambda^2f_L''(0)$ | $f_L''(0)$ |
|---:|---:|---:|---:|---:|
| 6 | $0.097125(750)$ | $0.00021984(115)$ | $0.096905(746)$ | $0.605659$ |
| 8 | $0.095533(585)$ | $0.00021257(112)$ | $0.095321(587)$ | $0.595755$ |

The displayed uncertainties are delete-one-block jackknife errors where
applicable.  The subtractive term is about $0.23\%$ and $0.22\%$ of
$\alpha_L$, respectively.  It is extensive—$\operatorname{Var}(I_\mu)$
grows with volume—but has a small stable density.  No cancellation of the
$p^2$ curvature is observed.

These are two finite chains using one sampler and binary64 arithmetic.  They
do not prove that the thermodynamic limit exists or remains positive.

The full observation can be reproduced separately from the fast commit rail:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_twist_response_experiment.py --reproduce
```

## Why this still does not prove the continuum estimate

A uniform twist spans only four one-form directions.  Witten coercivity must
control every low-momentum one-form direction.  The logical family

\[
                  W_\epsilon=\operatorname{diag}(1,\epsilon)
\]

has a unit Rayleigh quotient in the declared twist direction while the
orthogonal inverse response is $1/\epsilon$.  At $\epsilon=1/100$, the
twist response remains one and the missed inverse response is 100.  This is
an exact obstruction to the inference “positive uniform twist response
implies global Witten coercivity.”  It is not a BT counterexample.

The next object must therefore be an inhomogeneous edge twist
$\theta_{x,\mu}$.  Its response kernel is schematically

\[
 \frac1{\lambda^2}\mathbb E D_{(x,\mu),(y,\nu)}
 -\frac1{\lambda^4}\operatorname{Cov}
   (I_{x,\mu},I_{y,\nu}).
\]

The longitudinal and transverse Ward projections must be derived before
absolute values are taken.  A uniform lower bound over the lowest Fourier
shells, followed by an explicit Schur transfer to the full Witten one-form
operator, would finally address the Fourier-mode upper bounds needed for the
interacting $H^{-1}$ estimate.

No positive thermodynamic helicity modulus, current-correlation decay,
Witten coercivity, interacting $H^{-1}$ estimate or divergence, continuum
measure, Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result is
claimed.  Paper 21 is not changed because no reconstruction or global-moment
lifecycle state is promoted.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_twist_response_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_twist_response_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_twist_response_gate
ulimit -v 500000; python3 reverse_physics/bt_euclidean_twist_response_experiment.py --smoke
```

## Verification receipt

- The deterministic producer passed 20/20 checks in 0.04 s at 20,708 KiB.
- The non-importing verifier passed 8/8 checks in 0.11 s at 29,836 KiB.
- Eleven direct and adversarial tests passed in 0.13 s at 30,536 KiB.
- The memory-bounded observer smoke rail passed in 0.33 s at 22,188 KiB.
- The $L=6$ and $L=8$ observation runs took 10.30 s and 15.20 s at
  18,828 KiB and 20,184 KiB, respectively.
- The planning importer accepted 1,680 nodes with zero invalid items and zero
  malformed events in 1.31 s under `GOMEMLIMIT=300MiB` and `GOGC=50`.
- The 3.29 s advisory Science Forge wrapper exited zero, but the bridge audit
  failed closed because the referenced external `bp2transformer` verifier
  lacks `sympy`; the coverage rail also reported drift (1,827 certificates
  versus baseline 976).  These are failures/drift, not scientific passes.
- Tier 2 does not rebuild the unchanged content-addressed expected-Hessian
  and weighted-current inputs.  Tier 3 is not run because this is not an
  $H^{-1}$, reconstruction, freeze, release, shared-core, or Lorentzian
  lifecycle promotion.
