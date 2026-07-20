# Asymptotic Bach local-counterterm cohomology obstruction

## Result

The full tensor Lee--Wald potential of

\[
S_{C^2}=\frac{\alpha_B}{8}\int\sqrt{-g}\,C_{abcd}C^{abcd}
\]

is

\[
P^{abcd}=\frac{\alpha_B}{4}C^{abcd},\qquad
\Theta^a_{C^2}
=2\sqrt{-g}\left(
P^{abcd}\nabla_d\delta g_{bc}
-(\nabla_dP^{abcd})\delta g_{bc}
\right).
\]

This is derived before a Bondi, harmonic or transverse--traceless reduction.
On a flat background the \(\delta(\nabla P)\) term is retained even though
\(\bar C=0\).

The four-dimensional identity

\[
C^2=E_4+2R_{ab}R^{ab}-\frac23R^2
\]

then gives an invariant obstruction.  For two flat Einstein Jacobi fields,
\(\delta R_{ab}=0=\delta R\), the non-topological quadratic Hessian vanishes.
The Euler-density contribution has horizontally exact Lee--Wald current.
Thus the pure-\(C^2\) presymplectic class restricted to fixed-boundary
Einstein radiation is zero.

## Complete local ambiguity class

The declared counterterm class is every finite-order local covariant
Lee--Wald/JKM ambiguity made from the existing metric, conformal frame,
boundary normal and their finite jets, without a new independent boundary
field:

\[
L\mapsto L+dB,\qquad
\Theta\mapsto\Theta+\delta B+dY.
\]

The \(B\) term changes the current by
\(\delta_1\delta_2B-\delta_2\delta_1B=0\).  The \(Y\) term changes it by a
horizontal exact form,

\[
\omega\mapsto\omega+
d\bigl(\delta_1Y[h_2]-\delta_2Y[h_1]\bigr).
\]

This classification allows arbitrary finite derivative order and therefore
contains the first sufficient order for the four-derivative bulk action.
It proves that no choice of coefficients or tensor contractions inside this
class changes the zero horizontal class.

For compact-\(u\)-support radiative profiles, all endpoint and sphere
divergences integrate to zero.  An exact representative is therefore radical
on this wave-packet test space.  The desired Einstein news density is not
exact: on one polarization,

\[
w(f,g)=f\,\partial_u g-g\,\partial_u f
\]

has Euler derivatives \(E_f(w)=2\partial_u g\) and
\(E_g(w)=-2\partial_u f\).  The sign-mutated control
\(f\,\partial_u g+g\,\partial_u f=\partial_u(fg)\) has zero Euler image.

Hence:

\[
\boxed{
\text{local counterterms of the existing fields cannot produce a
nondegenerate fixed-boundary Einstein-radiative form in pure }C^2\text{
gravity}.}
\]

## What remains open

This does not exclude the enlarged \(p=0/p=1\) Bach boundary carrier.  The
pinned reduced calculation has a finite \(p=0\)-\(p=1\) cross term, so a
renormalized source--response phase space remains plausible.  A repair must
leave the local ambiguity class by adding at least one independent boundary
canonical momentum or edge variable, naturally a renormalized \(p=0/p=1\)
partner, or by changing the bulk Hessian through an Einstein--Hilbert scale or
compensator.

The following requested objects remain fail-closed:

- the full Bondi BV--BFV ghost and antifield falloffs;
- Coulombic and polyhomogeneous/Jordan data;
- the renormalized tensor \(p=0/p=1\) pairing;
- \(\mathscr I^-/i^0/\mathscr I^+\) corner matching;
- differentiable \(P_0\) and \(D_M\) charges.

The result is `LOCAL-ALGEBRAIC`, not `LORENTZIAN-CAUSAL`.  It makes no
particle, scattering, stability, positivity, unitarity or quantum claim.

## Evidence

- certificate:
  `bridge/certificates/ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1.json`;
- independent verifier:
  `bridge/einstein_sector/verify_asymptotic_bach_local_counterterm_cohomology_obstruction.py`;
- fail-closed atlas fragment:
  `residual_atlas/einstein-asymptotic-bach-local-counterterm-cohomology-fragment-v1.json`.

CLOSE-OUT: SHORTFALL — the fixed-boundary local-counterterm class is exactly obstructed, but the enlarged tensor p=0/p=1 BV--BFV phase space required by the work-item stop condition remains open
EVIDENCE: ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1
