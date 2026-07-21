# Two-phase counterflow trace/charge preflight

## Result

The smallest two-positive-phase, auxiliary-diagonal-(U(1)) successor has one
passing classical preflight stratum, but it is not the round cylinder.  The
selected stratum is the stationary Berger background

\[
a=1,\qquad c^2=\frac9{40},
\]

restricted to a fixed relative-charge leaf.  Its exact parameters are

\[
f_1^2=f_2^2=2,\quad \Omega=\frac34,\quad
\alpha_B=5,\quad \alpha_R=0,\quad
M_P^2=-\frac16,\quad V_0=\frac{119}{1920}.
\]

After the complete homogeneous lapse and diagonal Gauss reduction, its trace
quadratic form is

\[
L^{(2)}_{\rm red}=\frac18\dot u^2-\frac{659}{1920}u^2.
\]

Thus the velocity Hessian is (1/4>0), the Hamiltonian is positive, and the
two simple characteristic roots are

\[
\lambda=\pm i\sqrt{\frac{659}{240}}.
\]

This activates the separately scoped causal-BV-parent work item.  It does not
itself construct that parent.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Exact diagonal/relative decomposition

For

\[
F=f_1^2+f_2^2,\qquad
\chi=\frac{f_1^2\theta_1+f_2^2\theta_2}{F},\qquad
\psi=\theta_1-\theta_2,\qquad
\mu^2=\frac{f_1^2f_2^2}{F},
\]

the producer and independent verifier both establish

\[
f_1^2(d\theta_1-A)^2+f_2^2(d\theta_2-A)^2
=F(d\chi-A)^2+\mu^2(d\psi)^2.
\]

The auxiliary (A_0) equation is

\[
Q_{\rm diag}=F(\dot\chi-A_0)=0.
\]

It removes the diagonal phase and leaves a positive neutral relative direction
when (f_i^2>0).  No Maxwell term has been added.

## Stationary loci

Write (C=\mu^2\Omega^2>0), let (R) be the spatial scalar curvature, and
let (eta N/a) be the homogeneous conformal-Bach contribution.  Static
stationarity gives

\[
U(\Phi_0)=C-\beta,
\qquad
\Phi_0=\frac{3C/2-2\beta}{R},
\]

\[
M_P^2=2\Phi_0-4\alpha_RR,
\qquad
V_0=C-\beta-\alpha_RR^2.
\]

On the unit round cylinder, (R=6), (eta=0), so

\[
M_P^2=\frac C2-24\alpha_R,
\qquad
V_0=C-36\alpha_R,
\]

with (alpha_B) arbitrary.

On the frozen Berger background, the anisotropic metric equation also fixes

\[
\alpha_B=\frac{80C}{9},\qquad \frac\beta C=\frac{961}{1080}.
\]

The complete linear coefficient locus is

\[
\alpha_R=\frac{19040}{615627}C-\frac{6400}{22801}V_0,
\qquad
M_P^2=-\frac{80}{151}C+\frac{320}{151}V_0.
\]

The selected branch is the unique (alpha_R=0) slice of this locus, for
which (V_0/C=119/1080).

## Action-derived Dirac/Gauss reduction

With (a=e^{u/2}), (N=e^n), (Phi=\Phi_0+z), and
(psi=\Omega t+p), the exact homogeneous action density is expanded before
any constraint is imposed.  Its algebraic equations give

\[
A_0=\dot c,
\qquad
n=\frac{\dot p}{\Omega}+\frac32u.
\]

The homogeneous shift has no independent scalar zero mode and enforces the
closed spatial-diffeomorphism constraint.  Substitution gives, for
(alpha_R\ne0),

\[
L^{(2)}_{\rm red}
=\frac{3(\beta-3C/4)}R\dot u^2
-3\dot u\dot z
+(\beta-3C/2)u^2
-Ruz-\frac{z^2}{4\alpha_R}.
\]

The velocity Hessian has determinant (-9) and inertia ((1,1)) on every
nonzero-(alpha_R) stationary stratum.  Those strata are therefore excluded
by a split scalar pair independently of their characteristic roots.

For (alpha_R=0), the cylinder reduces to

\[
-\frac{3C}{8}\dot u^2-\frac{3C}{2}u^2,
\]

with negative kinetic sign and real roots (lambda=\pm2).  It is obstructed.

The active counterflow also contributes a nonzero order-zero trace row.  With
all other reduced variations set to zero, the local Euler row contains

\[
2(\beta-3C/2)u.
\]

This coefficient is nonzero on both declared backgrounds.  Consequently an
arbitrary compactly supported pure-(u) variation is not a kernel direction.
This is a local Hessian statement, not a support-local Green theorem.

## Characteristic and Jordan ledger

For (alpha_R\ne0), put

\[
b=\frac\beta C,\qquad
t=\frac{\alpha_RR^2}{C},\qquad
y=\frac{\lambda^2}{R}.
\]

The exact roots are

\[
y_\pm=\frac{4b+8t-3\pm\sqrt{(4b-3)^2+48t}}{24t}.
\]

Repeated roots occur at

\[
t_D=-\frac{(4b-3)^2}{48},
\]

where each square-root branch has a size-two Jordan block.  A double zero root
occurs at (t_0=3/2-b), again with a size-two Jordan block.  The certificate
stores the exact cylinder and Berger thresholds.  These refinements do not
rescue the nonzero-(alpha_R) branch because its kinetic inertia is already
split.

## Four Hamiltonian generators

The four generators must not be conflated:

- diagonal (U(1)): (Q_{\rm diag}=0) by Gauss, hence gauge;
- relative shift (R_{\rm rel}): Hamiltonian (Q_{\rm rel}), charged on the
  unrestricted union and presymplectic-null only on a fixed-(Q_{\rm rel})
  leaf;
- (D): Hamiltonian (Omega Q_{\rm rel}) modulo the closed diffeomorphism
  constraint, so it remains charged on the unrestricted union;
- (K=D-\Omega R_{\rm rel}): zero Hamiltonian modulo the closed
  diffeomorphism constraint and a stabilizer of the stationary clock.

The lapse equation implies (delta Q_{\rm rel}=0) in the linearized selected
solution space.  Hence that space lies on a fixed-charge leaf, where (D) is
presymplectic-null.  This does **not** promote unrestricted (D) to gauge and
does not identify diagonal (U(1)) neutrality with (D)-neutrality.

## Claim boundary and next gate

The certificate establishes an exact homogeneous Hessian, constraint,
inertia, characteristic/Jordan and charge preflight for the serialized action
and backgrounds.  It does not establish a support-local BV complex, a spatial
gravity principal symbol, Green hyperbolicity, a causal propagator, a
Hadamard state, or any quantum claim.

The next admissible work item is the full support-local causal BV parent for
the selected fixed-charge Berger stratum.  That successor must independently
derive the local field equations and gauge complex; it may not extrapolate the
homogeneous pass into a causal theorem.

## Evidence

- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json`
- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_PAYLOAD_V1.json`
- `d_quotient_classical/compensator/verify_two_phase_counterflow_trace_charge_preflight.py`
- `residual_atlas/two-phase-counterflow-trace-charge-preflight-fragment-v1.json`
