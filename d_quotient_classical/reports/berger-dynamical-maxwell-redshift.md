# Dynamical Maxwell redshift mode on the Berger clock

## Outcome

The prescribed characteristic ray in the first redshift preflight has been
replaced by a genuine source-free Maxwell solution.  In the orthonormal
Berger coframe,

\[
de^1=-(1/c)e^2\wedge e^3,\qquad
de^2=-(1/c)e^3\wedge e^1,\qquad
de^3=-(c/a^2)e^1\wedge e^2,
\]

take

\[
A_c=\cos(\beta t)e^1+\sin(\beta t)e^2,\qquad \beta=1/c.
\]

The horizontal coframe is a curl eigenspace with eigenvalue `-beta`, so
`ddot A+curl^2 A=0`.  Consequently `F=dA` obeys both source-free Maxwell
equations.  Its electric and magnetic fields have equal norm and zero inner
product, while its Poynting vector is the null Hopf direction `s=-e3`.

The hardened verifier also constructs `F` as a four-dimensional exterior
form with signature `(-,+,+,+)`, applies the Lorentzian Hodge star, and finds
both component dictionaries `dF={}` and `d star F={}`.  Thus the
field-equation result no longer relies only on the curl reduction.

## Relational observable

The local detector energy is

\[
\epsilon_v=T_{ab}u^au^b
=\beta^2\gamma(v)^2(1-v)^2,\qquad
u(v)=\gamma(v)(n+vs).
\]

To avoid pretending that the homogeneous background supplies a preferred
spatial base point, the observable is the normalized integral of this scalar
over the compact clock slice `theta=tau`.  It depends only on `F`, the
Weyl-invariant clock metric, and the relationally defined observer.  It is
therefore Maxwell-gauge invariant, Weyl invariant, and diffeomorphism
invariant.  The frequency ratio is extracted without a potential gauge:

\[
1+z=\sqrt{\mathcal E_e(\tau_e)/\mathcal E_r(\tau_r)}.
\]

Independently, the gauge-invariant complex field strength
`F_+=F_c+i F_s` obeys

\[
\star F_+=-iF_+,
\qquad
\mathcal L_{u(v)}F_+=-i\beta\gamma(v)(1-v)F_+.
\]

Squaring this Lie-derivative frequency reproduces `T_ab u^a u^b` exactly,
so the stress-energy ratio carries no untracked potential-amplitude
normalization.

At the rational fixture the exact values are

- `beta=2*sqrt(10)/3`;
- `nu_e=2*sqrt(10)/3` and `nu_r=sqrt(10)/3`;
- `E_e=40/9` and `E_r=10/9`;
- `1+z=2`, hence `z=1`;
- reception at `theta=3/8`, before a clock recrossing or Hopf wrap.

The SU(2) generator normalization gives primitive Hopf period `4 pi c`, not
`2 pi c`.  At the fixture the full fibre length is
`3*sqrt(10)*pi/5` and the half-fibre length is
`3*sqrt(10)*pi/10`.  The signal path has exact margin
`(-5 + 3*sqrt(10)*pi)/10>7/4`; the lifted clock chart has margin
`(-3 + 8*pi)/8>21/8`.

The real two-phase Maxwell block has nondegenerate symplectic pairing
`-32*pi**2` and positive energy coefficient
`32*sqrt(10)*pi**2/3`.  It introduces no negative physical
direction.

## Boundary of the result

This is an exact dynamical `G0` mode, not yet the complete `G1` signal sector.
The field is a global traveling mode rather than a compactly sourced retarded
pulse, and the endpoint observable is spatially averaged rather than
localized.  The Maxwell BV rows and their semidirect `q2` action on the
gravity-clock complex have not been exported, so the first nonlinear
gravity-Maxwell homological dressing remains open.  No backreaction,
phenomenology, or quantum claim is made.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json`.

## Verification

The exact generator and mutation guards, independent field-equation and
provenance replay, unit tests, and strict AJV Draft 2020-12 validation pass.
The two imported certificates are unchanged and content-addressed, so their
full producer chains were not rebuilt.  A full repository run is not
triggered by this isolated `G0` probe-mode theorem.
