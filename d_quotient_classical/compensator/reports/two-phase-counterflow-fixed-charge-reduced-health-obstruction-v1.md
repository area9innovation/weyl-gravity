# Two-phase counterflow fixed-charge reduced-health obstruction

## Result

The certified 70-component parent is causal and its homogeneous dressed-trace
block is positive.  Nevertheless, it does **not** pass the requested physical
fixed-charge reduction: fixing (Q_{m rel}) and quotienting the relative
shift removes the entire relative-clock Darboux pair.

This is the first exact failed PASS condition.  The later all-Hodge physical
sign and characteristic census is therefore not promoted.

## Derived fixed-charge fibre

Retain the global charge coordinate explicitly.  In the degree-ordered basis

\[
(r_R;delta\psi_0,\delta Q_{m rel};\epsilon_Q)
\]

of degrees ((-1;0,0;1)), the derived level-set differential is

\[
d r_R=\delta\psi_0,
\qquad
d(\delta Q_{m rel})=\epsilon_Q.
\]

The producer serializes the exact (4\times4) matrix and the homotopy

\[
S(\delta\psi_0)=r_R,
\qquad
S(\epsilon_Q)=\delta Q_{m rel},
\]

and verifies

\[
d^2=0,
\qquad
dS+Sd=1.
\]

Thus the cohomology dimensions in degrees ((-1,0,1)) are

\[
\boxed{(0,0,0)}.
\]

The independent verifier recomputes both ranks and the homotopy identity
without importing the producer.

## Symplectic reduction

Before fixing charge, the global relative sector has Darboux basis

\[
(\delta\psi_0,\delta Q_{m rel}),
\qquad
\Omega_R=
\begin{pmatrix}0&1\\-1&0\end{pmatrix}.
\]

On the level tangent (delta Q_{m rel}=0), the pullback is zero and

\[
\operatorname{rad}\Omega_R|_{Q_{m rel}}
=\operatorname{span}\{\delta\psi_0\}
=\operatorname{im}L_{R_{m rel}}.
\]

Therefore

\[
\boxed{
\ker(dQ_{m rel})/\operatorname{im}L_{R_{m rel}}=0.
}
\]

The zero mode was retained until these maps were explicit; it was not deleted
by an elliptic or harmonic projector.  The full shifted four-dimensional
derived pairing is nondegenerate, while its degree-zero physical quotient has
rank zero and no positive relative-clock direction.

## Sector ledger

- The 16-component diagonal-(U(1)) addition is exactly contractible.
- The imported cyclic (54\to26) SDR removes the 28 clock, nonminimal and
  gauge-fixing rows.
- In that SDR, the relative phase row is paired with the temporal
  diffeomorphism ghost and the radial scale row with the Weyl ghost.
- (H^1(S^3)=0), while scalar constants, exact and coexact sectors were
  retained until their declared contractions.
- The dressed homogeneous trace

  \[
  u=(\widehat h_{11}+\widehat h_{22}+\widehat h_{33})/3
  \]

  remains in the retained metric carrier with

  \[
  L_2=\frac18\dot u^2-\frac{659}{1920}u^2.
  \]

The positive trace does not repair the missing physical clock direction.
The retained 26-row unary carrier remains causally certified, but a complete
all-Hodge physical cohomology/sign/Jordan theorem was not needed to decide
this gate and is recorded as not reached.

## (Q_{\rm diag},Q_{\rm rel},D,K)

On the unrestricted parent:

- (Q_{\rm diag}=0) by Gauss;
- (Q_{m rel}\ne0) is global;
- (D) is charged with (H_D=\Omega Q_{m rel});
- (K=D-\Omega R_{m rel}) is the null helical stabilizer.

On the fixed-charge fibre,

\[
\iota_D\Omega=\Omega\,\delta Q_{m rel}=0.
\]

Both (R_{m rel}) and (D) are null and disappear on the quotient; (D)
and (K) agree only **after** that quotient.  They are not identified on the
unrestricted parent.

## Terminal disposition

The requested PASS required all of:

1. one positive relative-clock direction survives;
2. no negative physical scalar survives;
3. healthy reduced propagation;
4. (D) is null on the fixed leaf.

Condition 4 passes, but condition 1 fails exactly: the relative-clock quotient
dimension is zero.  The terminal result is therefore

```text
OBSTRUCTED_FIXED_CHARGE_REDUCTION_REMOVES_RELATIVE_CLOCK
```

This is classical `LOCAL-ALGEBRAIC`/`REDUCED-MODE` evidence with the unary
parent imported under `LORENTZIAN-CAUSAL`.  It establishes no Hadamard,
quantum positivity, nonlinear (q_2), observer, Einstein-source, QME,
particle, scattering or unitarity claim.

## Evidence

- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json`
- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1.json`
- `d_quotient_classical/compensator/verify_two_phase_counterflow_fixed_charge_reduced_health.py`
- `residual_atlas/two-phase-counterflow-fixed-charge-reduced-health-fragment-v1.json`

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1_TIER_RECEIPT
