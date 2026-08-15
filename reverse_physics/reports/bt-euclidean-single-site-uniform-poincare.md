# BT one-site uniform Poincare theorem

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_UNIFORM_POINCARE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

Every quotient-site conditional law of the four-dimensional BT lattice model
obeys

\[
 \boxed{
 \operatorname{Var}(f\mid\eta\in h_o^\perp)
 \leq \frac12\,
 \mathbb E\!\left[(D_{h_o}f)^2
 \mid\eta\in h_o^\perp\right],
 \qquad h_o=\delta_o-N^{-1}\mathbf1.}
\]

Here the mean-zero carrier is decomposed orthogonally as
\(H=\operatorname{span}(h_o)\oplus h_o^\perp\).  The constant is independent
of the frozen orthogonal background, lattice volume, chosen quotient-site
direction, and nonzero coupling.  This is the first certified uniform
nonconvex conditional spectral-gap estimate in this BT programme.

It is a local conditional theorem.  It does not yet imply a global Poincare
inequality, Witten one-form coercivity, or the interacting \(H^{-1}\) moment.
The missing step is quantitative control of how one site's conditional center
responds when neighboring sites move.

## Centering the exact fiber

The predecessor proves that every quotient-site fiber has a unique minimum.
For \(\eta\in h_o^\perp\), shift invariance gives

\[
 A(\eta+s h_o)=A(\eta+s\delta_o),
\]

so this is exactly the one-site algebra used below, without leaving the
mean-zero carrier.  Move its minimum to \(s=0\), set \(t=e^s\), and write the
centered coefficients as

\[
 u=Ae^{-z_*},\qquad v=C_2e^{2z_*},\qquad
 c=C_1e^{z_*}=u^2-8u-v.
\]

The incident-edge inequality gives

\[
 u^2v\geq8^3=512.
\]

The exact radial derivative is

\[
 F'(s)=u^2(t-t^{-2})+8u(t^{-1}-t)+v(t^2-t).
\]

The key new theorem is

\[
                         \boxed{sF'(s)\geq8s^2.}
\]

This is stronger than saying that the minimum has positive curvature.  It
controls the slope everywhere along both tails, while still allowing the
previously certified negative second derivative at intermediate points.

## Right tail

For \(t>1\), put

\[
 a=t-t^{-2},\qquad b=t^2-t,\qquad d=t-t^{-1}.
\]

Splitting the \(au^2\) term in half, completing a square against \(-8du\),
and using \(v\geq512/u^2\) gives

\[
 F'(\log t)\geq32(t-1)
 \left[
 \sqrt{t+1+t^{-1}}
 -\frac{(t+1)^2}{t^2+t+1}
 \right].
\]

The bracket is at least \(1/4\).  After squaring the positive sides and
clearing denominators, the claim is the positivity for \(t\geq1\) of

\[
 16+23t+6t^2-19t^3+6t^4+23t^5+16t^6.
\]

The negative power-basis coefficient is harmless.  Substitution \(t=1+y\)
gives

\[
 71+213y+455y^2+555y^3+361y^4+119y^5+16y^6,
\]

whose coefficients are all positive.  Therefore

\[
 F'(s)\geq8(e^s-1)\geq8s\qquad(s\geq0).
\]

## Left tail

Put \(r=e^{-s}>1\) and then \(r=w^2\).  The same square completion gives

\[
 -F'(-\log r)\geq32(r-1)
 \left[
 \sqrt{\frac{r^2+r+1}{r^3}}
 -\frac{(r+1)^2}{r(r^2+r+1)}
 \right].
\]

The bracket is at least \(1/[2(w+1)]\).  Clearing the squared inequality
produces a degree-fourteen polynomial in \(w\); after \(w=1+y\), its
coefficients are

\[
 (71,326,1231,4024,9860,17592,23278,23300,
 17826,10416,4588,1480,331,46,3).
\]

They are all strictly positive.  Hence

\[
 -F'(-\log r)\geq16(\sqrt r-1)
 \geq8\log r,
\]

which completes \(sF'(s)\geq8s^2\) on the left.

## From radial slope to a spectral gap

For the conditional log-coordinate density, put

\[
 V(s)=F(s)/\lambda^2,
 \qquad \rho=8/\lambda^2.
\]

On the right, \(V'(s)\geq\rho s\).  Thus for \(y\geq x>0\),

\[
 V(y)-V(x)\geq\frac\rho2(y^2-x^2)
 \geq\rho x(y-x).
\]

Consequently,

\[
 \int_x^\infty e^{-V(y)}dy
 \leq\frac{e^{-V(x)}}{\rho x},
 \qquad
 \int_0^x e^{V(y)}dy\leq xe^{V(x)}.
\]

Their product is at most \(1/\rho=\lambda^2/8\).  Reflection gives the same
bound on the left.  The classical weighted Hardy criterion bounds each
half-line constant by four times this product, so

\[
 C_{P,\psi}\leq\frac{\lambda^2}{2}.
\]

Since \(\psi=\lambda\phi\), the coordinate rescaling cancels \(\lambda^2\)
and yields \(C_{P,\phi}\leq1/2\).

The imported analytic result is Benjamin Muckenhoupt's weighted Hardy
inequality; see [the original 1972 paper](https://doi.org/10.4064/sm-44-1-31-38).
The exact BT radial derivative estimate and its uniform conditional
consequence are the new content.

## Meaning and next calculation

In ordinary language, choose the mean-zero direction that raises one site
relative to the common level of all sites, and freeze every orthogonal field
direction.  That one-dimensional probability distribution may have a dent,
but it cannot become broad or nearly split.  It relaxes at a uniformly
controlled rate.

That is one half of a local-to-global argument.  The other half is influence:
how much does the conditional mean along \(h_o\) move when an orthogonal
neighboring background direction changes?  Differentiating the conditional
mean turns that response into a conditional covariance.  The new \(1/2\)
Poincare constant can bound the covariance once the derivative of the local
score is written exactly.  Its Fourier symbol must then be compared with
bilaplacian scaling.  A subcritical symbol advances the Witten Schur estimate;
an unbounded one is the next exact obstruction.

## Boundary

This theorem does not establish a one-site logarithmic-Sobolev inequality,
a global Poincare inequality, volume-uniform Witten coercivity, the normalized
lowest-mode or interacting \(H^{-1}\) bound, tightness, or a continuum measure.
It does not restore ordinary OS positivity at \(\lambda=0.4\), and it has no
Born, Krein, or `LORENTZIAN-CAUSAL` consequence.

Paper 21 is not edited because the global interacting-moment and
reconstruction lifecycle states remain open.  The certificate and this report
are the publication surface for the local conditional theorem.

## Reproducibility

Run under the 500 MB Python cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_single_site_uniform_poincare.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_single_site_uniform_poincare.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_single_site_uniform_poincare
```

The independent verifier evaluates the two recorded polynomials against the
cleared radical identities at complete rational interpolation sets, rebuilds
their shifted coefficients independently, and checks exact radial fixtures.
Tier 0 also compiles Python, validates the JSON/schema, checks the predecessor
hash, runs the scoped diff check, and inspects staged paths.  Tier 2 uses the
unchanged predecessor by content hash.  Tier 3 is not triggered because this
is a local conditional estimate, not a global lifecycle promotion or freeze.
