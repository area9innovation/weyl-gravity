# Phase 2 generic-ℓ polar Schwarzschild disposition

## Outcome

The generic-Λ polar programme advances through the literal slice-current and
branch-preflight gates, but not through the sourced metric-jet gate. The exact
result is therefore a substantive `SHORTFALL`, not a parity-complete selection
theorem.

Established for \(\Lambda=\ell(\ell+1)\), integer \(\ell\ge2\), Schwarzschild
mass \(m>0\), and real \(\omega\ne0\):

- the invariant scalar/vector/STF even harmonics and their exact norm table;
- the complete trace-coupled Bianchi cascade;
- all seven symbolic-Λ rows of \(\delta R_{ab}=\psi_{ab}\);
- a triangular metric DAE with pivots
  \((B_h,A_h',K_h',C_h'')\) and retained \(vv,vr,\mathrm{angP}\)
  constraints;
- the conformal-radical quotient and its formal traceless-slice reachability;
- the action-derived, sphere-integrated Lee–Wald slice density \(F^v\) for
  arbitrary polar metric pairs;
- the generic homogeneous metric master and the physical traceless-slice Bach
  carrier rates and powers;
- exact leading source-forcing data for all six extra-carrier branches;
- serialized depth-2 metric jets for the three zero-shell branches and
  oscillatory branch index 1 from exact per-branch fraction-field RREF.

Not established: sourced metric jets satisfying all seven rows, their log
degrees beyond the finite pilot depth, the full RREF pivot-wall exceptional
set, or the branch-specialized nonzero EE/EX/XX coefficients. Consequently
no generic-ℓ polar finite-norm selection theorem is promoted.

## Harmonic and reconstruction results

The even STF harmonic is

\[
Y^{\rm TF}_{AB}=D_A D_B Y+\frac{\Lambda}{2}\gamma_{AB}Y,
\qquad
D^A Y^{\rm TF}_{AB}=-\frac{\Lambda-2}{2}D_BY.
\]

Relative to \(N_\Lambda=\int |Y|^2\), the scalar, vector, and STF norms are

\[
1,\qquad \Lambda,\qquad \frac{\Lambda(\Lambda-2)}2.
\]

The Bianchi cascade solves \((D,E_c,G_c)\) with pivots

\[
-\Lambda/r^2,\qquad-\Lambda/r^2,\qquad(2-\Lambda)/(2r^2).
\]

The Ricci-to-metric DAE has common denominator

\[
2\Lambda r^3(\Lambda-2)(r-2m).
\]

Thus the only representation walls are \(\Lambda=0,2\), i.e. the excluded
\(\ell=0,1\) sectors. The \(vv\), \(vr\), and angular-scalar rows are retained
as explicit constraints rather than inferred from the four pivot rows.

The conformal direction is

\[
h_{ab}=\sigma g_{ab},\qquad
(A_h,B_h,C_h,K_h)=(-(1-2m/r)\sigma,\sigma,0,\sigma).
\]

For \(\sigma=e^{i\omega v}s(r)P_\ell\), the scalar wave operator has formal
pivots

\[
2i\omega(p+1),\qquad
-2i\omega(p+1+4im\omega)
\]

on the zero and \(-2i\omega\) shells. At the unique resonant powers, the log
generalized pivots are \(2i\omega\) and \(-2i\omega\), both nonzero. Hence the
trace is removable on the declared exponential-polyhomogeneous finite-log
module.

## Literal \(F^v\) current

The producer uses `LinearizedTheta(...).omega(left,right)[0]`, not the radial
flux component \(F^r\), and integrates with the sphere measure
\(r^2\,dx\,d\phi\). Before selecting modes, the angular density reduces
exactly to

\[
A\,P_\ell^2+C(1-x^2)(P_\ell')^2.
\]

The mixed \(P_\ell P_\ell'\) coefficient and the reduction defect are both
exactly zero. Applying

\[
\int_{-1}^1P_\ell^2dx=\frac2{2\ell+1},\qquad
\int_{-1}^1(1-x^2)(P_\ell')^2dx=\frac{2\Lambda}{2\ell+1}
\]

and the \(2\pi\) azimuthal factor gives the serialized generic-Λ radial-jet
bilinear. No sampled harmonic or unevaluated angular integral remains.

The expanded expression has 272 terms and exactly 79 nonzero oriented
radial-jet signatures. A coarser unordered component/order projection has 23
support classes, but that projection is not an algebraic reduction and is not
used to discard the (AB) or (AK) terms. The maximum derivative orders are
three on (A,K) and two on (B,C); the maximum coefficient radial weight is
(+2). Direct substitution of the constraint-compatible zero-shell profile
gives the first XX coefficient at metric depth 2:

\[
\frac{8i\pi\alpha\omega}{3(2\ell+1)}
\left(4B_{1a}B_{1b}+3i\omega B_{1a}C_{2b}
-3i\omega B_{1b}C_{2a}-4\omega^2C_{2a}C_{2b}\right).
\]

The oscillatory (+2) and (+1) layers cancel, so its first discriminating
current coefficient also consumes metric depth 2. This is a current-depth
statement, not all-seven constraint closure.

## Generic branch preflight

The old polar homogeneous Jordan warning is resolved rather than inherited.
The chain-adapted metric system collapses to

\[
r(r-2m)C_h''+2i(-im+\omega r^2-ir)C_h'
  +i(i\Lambda+6\omega r)C_h=0.
\]

Its powers are

\[
-3,\qquad 1-4im\omega
\]

on the zero and oscillatory shells, with recurrence diagonal
\(-2i\omega(k-3)\). The generalized zero-shell mode is a degree-one
polynomial, not a log or fractional power.

On the formally reachable traceless Ricci slice, the generic Bach-carrier
power polynomials are

\[
(s+1)(s+2)(s+3)
\]

and

\[
(s+1+4im\omega)(s+2+4im\omega)(s+3+4im\omega).
\]

Both are exactly Λ-independent. Substitution of their six leading vectors
into the metric DAE gives forcing powers \(r^1\) on the zero shell and
\(r^{1-4im\omega}\) on the oscillatory shell. Every leading coefficient has
the common representation denominator \(\Lambda(\Lambda-2)\), with no new
allowed-ℓ wall. These data identify candidate metric powers \(2\) and
\(1-4im\omega\), but do not certify all-seven-row jet closure.

The DomainMatrix pilot supersedes the earlier multivariate-GCD implementation.
At depth 2, zero branches 0, 1, and 2 solve in 8.17, 10.27, and 14.48 seconds
with log degree 0. Oscillatory branch 1 solves in 167.99 seconds and requires
log degree 1 at this finite depth. Oscillatory branches 0 and 2 return no
result within separate 180-second bounds. Those are computational non-results,
not mathematical obstructions.

The solved metric coefficients have only \(\Lambda\) and \(\Lambda-2\) in
their reduced denominators. The RREF pivot denominators have not yet been
exposed and classified, so additional generic-field walls are not excluded.

## First missing exact object

```text
SYMBOLIC_LAMBDA_SOURCED_POLAR_METRIC_JETS_WITH_ALL_SEVEN_CONSTRAINTS
```

The next implementation must cache the six simple projected powers, expose
the fraction-field pivot denominators, and independently verify
\(vv\), \(vr\), and angular-scalar residuals through the jet depth consumed by
the literal current. Only then may it substitute the modes into \(F^v\), give
the EE/EX/XX leading coefficients, and classify their exact exceptional set.

Current depth 2 is not constraint depth. For branch labels \(j=1,2,3\), both
shells conservatively require metric depths \(3,4,5\), hence carrier depths
\(7,8,9\), because reconstruction consumes four source derivatives. The
shallower oscillatory power is not assumed until the missing constraints prove
it. The first specific bottleneck is oscillatory branch index 0 at metric
depth 2; the worst requested closure is metric depth 5/carrier depth 9.

The existing ℓ=2 fixture still shows the relevant power filtration: full XX
entries move under Einstein shifts, while their divergent leading class is
unchanged because the Einstein and EX tails are lower power. That fixture is a
control only and is not promoted to generic ℓ.

## Claim boundary

No claim is made about a generic polar selection theorem, asymptotically flat
phase space, Hilbert norm, stability, scattering, quasinormal modes, ringdown,
positivity, particles, or quantum theory. No terminal axial conclusion is
imported or modified; the independent join imports it directly.

CLOSE-OUT: SHORTFALL — the generic polar harmonic, seven-row reconstruction, conformal quotient, literal F^v current and filtration, homogeneous master, Bach-carrier powers, six-branch forcing preflight, and four depth-2 sourced-lift pilots are exact; sourced all-seven metric jets, pivot-wall classification, and the nonzero EE/EX/XX exceptional-set theorem remain open.
EVIDENCE: black_hole_programme/phase2/general_l_polar/certificate.json
MISSING-DEP: Construct fraction-free per-branch sourced metric jets, verify vv/vr/angP through the current depth, and evaluate the exact generic-Λ F^v EE/EX/XX leading coefficients and exceptional set.
