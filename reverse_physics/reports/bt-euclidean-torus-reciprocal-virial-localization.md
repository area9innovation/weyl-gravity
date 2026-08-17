# BT torus reciprocal-virial localization

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_RECIPROCAL_VIRIAL_LOCALIZATION_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

## Result

The unresolved low-action branch can be narrowed by an exact deformation
that was absent from the preceding virial certificates.  Let \(u=e^\psi>0\),

\[
 r_x=\sum_{y\sim x}\left({u_y\over u_x}-1\right),\qquad
 A={1\over2}\sum_xr_x^2,
\]

and write \(g=\nabla_\psi A\), \(R^2=\sum_xr_x^2\).  If \(J\) is the
derivative of the residual map and \(v_x=1/u_x\), then

\[
 \boxed{(Jv)_x=-{r_x\over u_x}.}
\]

Consequently, with

\[
 B=\sum_x{r_x^2\over u_x},
\]

scale invariance and Cauchy--Schwarz give the exact graph inequality

\[
 \boxed{
 Q={\lVert g\rVert_2^2\over R^2}
 \geq {B^2\over R^2\lVert v-\bar v\rVert_2^2}.}
\]

Normalize the irrelevant common scale so that \(\min_xu_x=1\).  Then
\(0<v_x\leq1\), and Popoviciu's variance inequality yields

\[
 \boxed{Q\geq {4B^2\over NR^2}={8\eta^2A\over N},
 \qquad \eta={B\over R^2}.}
\]

On \(T_L^4\), \(N=L^4\) and
\(\omega_L=4\sin^2(\pi/L)\), so

\[
 \boxed{{Q\over\omega_L^2}\geq {\eta^2A\over2\pi^4}.}
\]

This does not prove the all-field lower bound.  It proves that every possible
counterfamily with nonvanishing action must move its residual energy to
diverging field superlevels.

## Exact inverse-field identity

For a logarithmic variation \(w\), the residual derivative is

\[
 (Jw)_x=\sum_{y\sim x}{u_y\over u_x}(w_y-w_x).
\]

Putting \(w=v=1/u\) gives, vertex by vertex,

\[
\begin{aligned}
 (Jv)_x
 &=\sum_{y\sim x}{u_y\over u_x}
       \left({1\over u_y}-{1\over u_x}\right)\\
 &={8\over u_x}-{1\over u_x^2}\sum_{y\sim x}u_y
 =-{r_x\over u_x}.
\end{aligned}
\]

Since \(g=J^Tr\),

\[
 \langle g,v\rangle=\langle r,Jv\rangle=-B.
\]

The common rescaling \(u\mapsto cu\) leaves the action invariant, hence
\(\sum_xg_x=0\).  Centering \(v\) therefore does not change the pairing:

\[
 \langle g,v-\bar v\rangle=-B.
\]

The exact quotient floor follows immediately from Cauchy--Schwarz.  For
numbers in an interval of length one, Popoviciu gives variance at most
one quarter; hence \(\lVert v-\bar v\rVert_2^2\leq N/4\).

## Superlevel consequence

For any threshold \(K\geq1\), define the fraction of residual energy below
that height by

\[
 F_K={\sum_{u_x\leq K}r_x^2\over R^2}.
\]

Because \(1/u_x\geq1/K\) on this set,

\[
 \eta={B\over R^2}\geq {F_K\over K}.
\]

Thus the torus inequality sharpens to

\[
 \boxed{{Q\over\omega_L^2}
 \geq {A F_K^2\over2\pi^4K^2}.}
\]

If the normalized quotient tends to zero, then

\[
 {\sqrt A\,F_K\over K}\longrightarrow0.
\]

In particular:

- if \(\liminf A>0\), every fixed-\(K\) residual fraction tends to zero;
- if \(A\geq aL^4\) for fixed \(a>0\), every fixed-\(K\) residual fraction
  is \(o(L^{-2})\).

This is more than another generic method obstruction.  It identifies the
only surviving geometry for a positive-action counterfamily: essentially all
of its residual energy must escape through field heights diverging relative
to the global minimum.  The next proof step can therefore be a high-superlevel
boundary-current estimate rather than an unrestricted search over fields.

## Exact fixture

The certificate independently reconstructs the parity checkerboard on
\(T_4^4\), with \(u=1\) on even vertices and \(u=2\) on odd vertices.  Exact
rational arithmetic gives

\[
 R^2=10240,\quad A=5120=20N,\quad B=9216,\quad
 \eta={9\over10},
\]

and

\[
 \lVert v-\bar v\rVert_2^2=16,\qquad
 \langle g,v-\bar v\rangle=-9216.
\]

For this fixture the unrelaxed Cauchy quotient floor is saturated.  The
separate Popoviciu relaxation is also checked exactly.

## Numerical reconnaissance boundary

The accompanying continuation scout evaluates the complete nonlinear
quotient and its analytic derivative in the hyperoctahedral symmetry class.
It found localized, conformal-bubble-like branches.  Once their core is
resolved, those branches turn away from free-scale collapse.  This numerical
observation motivated the inverse-field deformation but is not evidence for
the theorem, a global minimum, or an asymptotic claim.  No floating-point
minimum enters the certificate.

## What remains

The theorem does not control the branch \(A\to0\), and a diverging threshold
\(K_L\) can outrun the displayed estimate.  The all-field torus
Polyak--Lojasiewicz inequality, a nonseparable polynomial-contrast
counterfamily, Witten/Poincare transfer, the interacting \(H^{-1}\) moment,
continuum reconstruction, Born/Krein interpretation, and every
LORENTZIAN-CAUSAL claim remain open.

The aligned next gate is to combine this residual superlevel localization
with the exact canonical edge current.  Either its high-superlevel boundary
has a torus-scale divergence floor, or the near-equality geometry specifies
the required nonseparable counterfamily.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_reciprocal_virial_localization.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_reciprocal_virial_localization.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_reciprocal_virial_localization

The exact commands, timings, memory ceilings, predecessor hash, planning and
paper checks, and higher-tier disposition are stored in the machine
certificate.
