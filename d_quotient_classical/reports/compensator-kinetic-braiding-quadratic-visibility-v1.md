# Minimal kinetic-braiding quadratic visibility

## Result

The complete polynomial of the lowest potentially nontrivial degree is

\[
G(X)=g_0+\beta X.
\]

The constant term is horizontally exact:

\[
g_0\int\sqrt{-\widehat g}\,\widehat\Box\theta
=g_0\int d(*_{\widehat g}d\theta).
\]

The first nonexact term is therefore the cubic Galileon

\[
S_3=\beta\int\sqrt{-\widehat g}\,
X\,\widehat\Box\theta.
\]

Its full metric--clock quadratic Hessian is identically zero on the required
constant-clock unit cylinder.  On the stationary-gradient Berger fixture it
instead has a nonzero rank-two scalar block.  Consequently Berger visibility
does not repair the cylinder:

\[
\boxed{
\delta^2S_3\big|_{\rm cylinder}=0,\qquad
\operatorname{rank}\delta^2S_3\big|_{\rm Berger,scalar}=2.
}
\]

This closes only the Level-2A visibility gate.  It selects no action and
constructs no reduced ADM or causal theory.

## Frozen inputs

The calculation imports:

```text
COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1
sha256 9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533
source f64be4a5793764ebf8871d5f1a83bd736aed7fc1

COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1
sha256 8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba
source b0ee2bea23af4af809bc0a50956c3e37d944e72f
```

Thus the result consumes the independently frozen quadratic \(P(X)\) no-go
and its exact open-background stability theorem.  It does not reconstruct or
weaken either input.

## Why \(X\widehat\Box\theta\) is the first term

At polynomial degree zero, \(G(X)=g_0\) gives only a boundary functional.  At
degree one, the remaining term has scalar Euler expression

\[
2\beta\left[
(\nabla_a\nabla_b\theta)(\nabla^a\nabla^b\theta)
-(\Box\theta)^2
\right],
\]

which is nonzero on a generic jet.  The certificate retains the exact witness
\(H_{00}=H_{11}=1\), \(\Box\theta=0\), for which the displayed expression
divided by \(\beta\) is \(4\).

Therefore \(\beta X\) is not being kept merely because it resembles a familiar
template: it is the unique nonexact direction in the complete degree-one
polynomial family, up to scale.

## Complete covariant second variation

Let

\[
v_a=\nabla_a\bar\theta,\qquad
X_{\rm bar}=v^av_a,
\]

and suppose

\[
\nabla_av_b=0,\qquad
\widehat\Box\bar\theta=0.
\]

For a perturbation \((h_{ab},\phi)\), define

\[
x(h,\phi)
=-h^{ab}v_av_b+2v^a\nabla_a\phi,
\]

\[
b(h,\phi)
=\widehat\Box\phi
-\left(\nabla_ah^{ab}-\frac12\nabla^bh\right)v_b.
\]

Then, modulo compact-support or closed-slice boundary terms,

\[
\delta^2S_3[(h,\phi),(j,\psi)]
=\beta\int\sqrt{-\widehat g}
\left[x(h,\phi)b(j,\psi)+x(j,\psi)b(h,\phi)\right].
\]

This is the full Hessian.  It is not a homogeneous scalar truncation.  The
inverse metric, volume density, lapse, shift, spatial trace and tracefree
metric, clock, Levi--Civita connection and boundary terms are all included.

The factorization follows without dropping second-order metric terms.  The
numerical background constant satisfies

\[
X_{\rm bar}\int\sqrt{-\widehat g}\,\widehat\Box\theta
=X_{\rm bar}\int d(*_{\widehat g}d\theta)
\]

for every perturbed field.  After subtracting that exact functional,
\(X-X_{\rm bar}\) and \(\widehat\Box\theta\) both vanish at the background, so
only their first-variation product remains.

## Unit cylinder

On

\[
\widehat g=-dt^2+d\Omega_3^2,\qquad
\bar\theta=\text{constant},
\]

one has \(v_a=0\).  Hence

\[
x(h,\phi)=0
\]

for every metric--clock perturbation, including lapse, shift and all spatial
metric components.  Although

\[
b(h,\phi)=\widehat\Box\phi,
\]

the full bilinear Hessian is zero because every term contains \(x\).

The machine stores an \(11\times11\) zero matrix spanning the clock and all ten
symmetric metric components, rank
zero, and an identically zero symbol at every covector.

This is stronger than a homogeneous check:

\[
\delta^2S_3\big|_{\rm cylinder}=0
\]

on the complete local metric--clock carrier.  The braiding term begins at
cubic perturbative order there.

Therefore the degree-one \(P(X)+G(X)\widehat\Box\theta\) family leaves the
imported cylinder quadratic operator unchanged, including its dressed-trace
row, split gravity--auxiliary pair and raw-\(D\) witnesses.

## Berger fixture

On the static Berger product let

\[
\bar\theta=\nu t,\qquad \nu=\frac34.
\]

Write

\[
h_{00}=-2n,\qquad
k=\bar\gamma^{ij}h_{ij},\qquad
r=\bar\nabla^is_i,
\]

\[
\chi=D\phi-\nu n,\qquad
K=\frac12(Dk-2r).
\]

The complete first variations reduce to

\[
x=-2\nu\chi,
\qquad
b=-D\chi+\Delta_{\rm B}\phi-\nu K.
\]

Thus

\[
S_3^{(2)}
=2\beta\nu\int\sqrt{\bar\gamma}\,
\chi(D\chi-\Delta_{\rm B}\phi+\nu K).
\]

After removing the explicit time-boundary terms

\[
\beta\nu D(\chi^2),\qquad
-\beta\nu D[(\bar\nabla\phi)^2],
\]

the quadratic action is

\[
S_3^{(2)}
=2\beta\nu^2\int\sqrt{\bar\gamma}\,
\left[\chi K+n\Delta_{\rm B}\phi\right].
\]

It acts only on the scalar clock/lapse/trace/shift-divergence block.
Transverse shift and transverse-tracefree spatial metric perturbations are
zero directions of this term.

In the derived scalar order \((\phi,n,k,r)\), with
\(D^\sharp=-D\) and \(\Delta^\sharp=\Delta\), the exact symbol after removing
the common factor \(\beta\nu^2\) is

\[
\begin{pmatrix}
0&2\Delta&-D^2&2D\\
2\Delta&0&-\nu D&2\nu\\
-D^2&\nu D&0&0\\
-2D&2\nu&0&0
\end{pmatrix}.
\]

Every \(3\times3\) minor vanishes.  For \(\Delta\ne0\), the
\((\phi,n)\) minor is \(-4\Delta^2\); for \(D\ne0\), the
\((\phi,k)\) minor is \(-D^4\).  Hence the rank is exactly two at every
nonzero scalar covector.

The two exact null vectors are the scalar diffeomorphisms

\[
(\nu,D,0,-\Delta)^T,\qquad
(0,0,2\Delta,D\Delta)^T.
\]

This also checks formal self-adjointness and prevents a gauge direction from
being mistaken for a new physical clock mode.

## Independent rail

The verifier does not import the producer.  It reconstructs
\(\delta X\) and \(\delta\Box\theta\) from a four-dimensional indexed jet:

\[
\delta\Gamma^\lambda_{\mu\nu}
=\frac12\bar g^{\lambda\rho}
(\partial_\mu h_{\nu\rho}+\partial_\nu h_{\mu\rho}
-\partial_\rho h_{\mu\nu}).
\]

It independently specializes the result to lapse, shift divergence, spatial
trace and clock jets, checks the two formal gauge null vectors, proves the
rank upper bound from all \(3\times3\) minors, and proves the lower bound with
the two complementary exact minors.

Mutation tests reject:

- a nonzero cylinder metric--clock Hessian entry;
- a Berger symbol sign change;
- a false rank-four promotion;
- retaining a certified boundary term as dynamics;
- identifying Berger visibility with cylinder visibility;
- selecting an action;
- causal or quantum promotion.

## Claim boundary

This theorem covers only

\[
G(X)=g_0+\beta X
\]

at the first nonexact polynomial degree, on the declared unit-cylinder and
Berger fixtures.  It is not a no-go for higher \(G(X)\), Horndeski/DHOST
curvature couplings, other backgrounds, new fields or enlarged gauge groups.

It establishes no reduced ADM health, selected action, causal Green parent,
nonlinear \(q_2\), Hadamard state, anomaly/QME result, particle space,
scattering, positivity or unitarity.

## Evidence

```text
d_quotient_classical/certificates/
  COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1.json

d_quotient_classical/compensator/
  kinetic_braiding_quadratic_visibility.py
  verify_kinetic_braiding_quadratic_visibility.py

d_quotient_classical/schema/
  compensator-kinetic-braiding-quadratic-visibility-v1.schema.json
```

CLOSE-OUT: DONE — the complete degree-one kinetic-braiding visibility gate is
certified; the cylinder Hessian is identically zero and the separate Berger
scalar block has exact rank two.
