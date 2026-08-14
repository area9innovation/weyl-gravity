# BT zero-fiber Ward-weight obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_ZERO_FIBER_WARD_WEIGHT_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `CLASSIFIED`

## Result

A constrained or integrated-marginal Ward identity does not directly see the
background distribution needed by the annealed-center theorem.  It sees a
different distribution, biased by the conditional density at the zero fiber.
Removing that bias pointwise is impossible in the actual BT lattice.

Write

\[
 V_\eta(t)=S(\eta+th),\qquad
 Z_\eta=\int_{\mathbb R}e^{-V_\eta(t)}dt,
 \qquad q_\eta(t)=\frac{e^{-V_\eta(t)}}{Z_\eta}.
\]

The background marginal is

\[
 \nu(d\eta)=\frac{Z_\eta}{Z}d\eta,
\]

and the fully integrated density of the mode coordinate is

\[
 \rho(t)=\mathbb E_\nu[q_\eta(t)].
\]

If $s_\eta=V_\eta'(0)$ and $H_\eta=V_\eta''(0)$, differentiation gives

\[
 \rho'(0)=-\mathbb E_\nu[q_\eta(0)s_\eta],
 \qquad
 \rho''(0)=\mathbb E_\nu[q_\eta(0)(s_\eta^2-H_\eta)].
\]

These are exact finite-dimensional identities.  Their important feature is
the factor $q_\eta(0)$.

## What the constrained measure changes

Fixing the mode coordinate to zero produces the constrained background law

\[
 \mu_0(d\eta)
 =\frac{e^{-V_\eta(0)}}{Z\rho(0)}d\eta.
\]

Its relation to the true background marginal is

\[
 \frac{d\mu_0}{d\nu}=\frac{q_\eta(0)}{\rho(0)},
 \qquad
 \frac{d\nu}{d\mu_0}=\frac{\rho(0)}{q_\eta(0)}.
\]

Thus a local constrained insertion gives

\[
 \frac{\rho''(0)}{\rho(0)}
 =\mathbb E_{\mu_0}[s_\eta^2-H_\eta],
\]

whereas the center reduction needs

\[
 \mathbb E_\nu[s_\eta^2]
 =\rho(0)\mathbb E_{\mu_0}
   \left[\frac{s_\eta^2}{q_\eta(0)}\right].
\]

The reciprocal density contains the whole fiber normalization,
$1/q_\eta(0)=Z_\eta e^{V_\eta(0)}$.  It is therefore not a local insertion.
This is the precise barrier: a Ward identity at the constrained slice has the
wrong background weighting.

## Exact general no-transfer fixture

For

\[
 V_R(t,y)=\frac\kappa2(t-y)^2+\frac{y^2}{2R^2},
\]

the background marginal is $y\sim N(0,R^2)$, the conditional law is
$t\mid y\sim N(y,1/\kappa)$, and $s_y=-\kappa y$.  The desired unweighted
moment is

\[
 \mathbb E_\nu[s_y^2]=\kappa^2R^2.
\]

Conditioning on $t=0$ changes the $y$ variance to
$R^2/(1+\kappa R^2)$, so the weighted score moment becomes

\[
 \frac{\mathbb E_\nu[q_y(0)s_y^2]}{\rho(0)}
 =\frac{\kappa^2R^2}{1+\kappa R^2}.
\]

At $(\kappa,R)=(2,5)$ these are respectively $100$ and $100/51$;
$\rho''(0)/\rho(0)=-2/51$.  As $R$ grows, the constrained quantities remain
bounded while the desired score moment diverges.  Hence weighted marginal
data do not imply the unweighted target in general.

## The obstruction occurs inside BT

The predecessor certificates provide a fixed $6^4$ BT family indexed by
integers $m\geq2$.  In its coordinate $u$, the conditional potential is
strictly convex, its unique minimizer lies below $-m$, and

\[
 q_m\{u\geq-m\}\leq2^{-m}.
\]

Let $q_m^{(u)}$ denote this density with respect to $du$.  It is decreasing on
$[-m,0]$.  Consequently

\[
 m q_m^{(u)}(0)
 \leq\int_{-m}^{0}q_m^{(u)}(u)du
 \leq q_m^{(u)}\{u\geq-m\}
 \leq2^{-m},
\]

and hence

\[
 q_m^{(u)}(0)\leq\frac{2^{-m}}m,
 \qquad
 \frac1{q_m^{(u)}(0)}\geq m2^m.
\]

Because $t=u\log2$, the density used in the disintegration is
$q_{\eta_m}^{(t)}(0)=q_m^{(u)}(0)/\log2$.  The fixed coordinate conversion
does not alter the conclusion: there is no positive background-uniform lower
bound on the zero-fiber conditional density, even at fixed BT volume.  A proof that divides a
constrained Ward identity by a pointwise lower bound on $q_\eta(0)$ is
therefore obstructed.

This does **not** prove that the annealed score diverges.  The runaway
backgrounds can be extremely rare under $\nu$.  The next estimate must retain
that Gibbs rarity and control the joint tail of score size and inverse
conditional density.  Equivalently, it must compare the action cost of moving
the fiber center with the resulting center displacement.  On the tuned
fixed-physical-volume branch it must also respect the already certified RG
normalization.

## What remains

The live target remains

\[
 \mathbb E_\nu[V_\eta'(0)^2]\lesssim N\omega_L^2.
\]

Neither the annealed score/center moment, the integrated lowest-mode moment,
the actual interacting $H^{-1}$ estimate, tightness, continuum
identification, a Born rule, Krein reconstruction, nor anything
`LORENTZIAN-CAUSAL` is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_zero_fiber_ward_weight_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_zero_fiber_ward_weight_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_zero_fiber_ward_weight_obstruction
```

## Verification receipt

On the final tree, the deterministic producer byte check passed in 0.04
seconds (20200 KB), the independent verifier passed in 0.09 seconds (29196
KB), and all nine focused tests passed in 0.11 seconds (30568 KB).  The four
direct predecessor verifiers passed sequentially in 0.40 seconds (30624 KB).
Tier 0 Python compilation passed in 0.05 seconds (19440 KB), structured JSON
parsing passed in 0.01 seconds (11524 KB), and the scoped diff check passed in
0.04 seconds (11432 KB).

The Paper 21 claim-map generator/checker chain passed in 0.14 seconds (30372
KB).  The final two capped `pdflatex` passes took 0.75 and 0.76 seconds, with
peak RSS 53320 KB and 53404 KB, and produced the 51-page PDF.  Planning import produced 1610
nodes with zero invalid items and zero malformed events in 7.26 seconds
(209952 KB under `GOMEMLIMIT=300MiB`).

The first planning-event attempt was run with both a 500 MB address-space cap
and Go's heap cap.  The Go runtime failed before executing the coordinator
because it could not reserve its page-summary address space; no event was
written.  The successful retry retained `GOMEMLIMIT=300MiB` and appended event
sequence 8.  The failed attempt is not counted as a pass.

The read-only Science Forge shadow rail exited advisory-pass in 2.15 seconds
(340440 KB) but again reported a fail-closed bridge audit caused by a Forge
binary/standard-library hash mismatch and compiler error `E9118`, plus corpus
drift (1661 certificates versus the 2026-07-19 baseline of 976).  Those
advisory substrate findings are not verification of this certificate.

Tier 3 was not run because this classifies and obstructs a proof method
without changing shared core algebra or promoting a freeze, continuum, or
reconstruction theorem.  The exact scoped diff and final staged content
hashes are inspected immediately before commit.
