# BT affine virial and actual action-density theorem

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The failed homogeneous virial shortcut can be repaired by an additive term
proportional to volume.  On every connected finite (q)-regular undirected
graph, define

\[
 w_{xy}=e^{\psi_y-\psi_x},\qquad
 s_x=\sum_{y\sim x}w_{xy},\qquad
 r_x=s_x-q,
\]

and

\[
 A(\psi)=\frac12\sum_xr_x^2,
 \qquad
 D(\psi)=\psi\mathbin{\cdot}\nabla A(\psi).
\]

Then

\[
 D(\psi)\geq
 2A(\psi)-Nq^2\left(1+\frac14\log q\right).
\]

For the four-dimensional periodic BT lattice, (q=8).  The positive
degree-four Taylor partial sum for (e^{7/10}) is

\[
 1+\frac7{10}+\frac{(7/10)^2}{2}
 +\frac{(7/10)^3}{6}+\frac{(7/10)^4}{24}
 =\frac{482921}{240000}>2.
\]

Thus (log2<7/10), (log8<21/10), and the completely rational version is

\[
                  D(\psi)\geq2A(\psi)-\frac{488}{5}N.
\]

This theorem does not contradict the predecessor's exact fixture with
(D/A<2): the new inequality contains an additive volume defect.

## Vertexwise proof

Put

\[
 t_x=\sum_{y\sim x}w_{xy}\log w_{xy}.
\]

Direct differentiation gives (D=\sum_xr_xt_x).  There are three scalar
cases.

If (s_x\geq q), convexity of (u\log u) gives

\[
 t_x\geq s_x\log(s_x/q)\geq s_x-q=r_x,
\]

so (r_xt_x\geq r_x^2).  The second inequality is
(y\log y\geq y-1) for (y\geq1).

If (s_x<q), superadditivity of (u\log u) gives
(t_x\leq s_x\log s_x).  For (s_x\leq1), both (r_x) and (t_x) are
nonpositive, so their product is nonnegative.  For (1<s_x<q),

\[
 r_xt_x\geq-(q-s_x)s_x\log q
             \geq-\frac{q^2}{4}\log q.
\]

Finally, every negative residual obeys (r_x^2\leq q^2).  Therefore

\[
 2A
 \leq \sum_{r_x\geq0}r_x^2+Nq^2
 \leq D+N\frac{q^2}{4}\log q+Nq^2,
\]

which is the stated inequality.

## Actual Gibbs action density

In the mean-zero coordinates (psi=\lambda\phi), the actual finite-volume
measure is proportional to

\[
                  e^{-A(\psi)/\lambda^2}\,d\psi.
\]

Radial integration by parts on its (N-1) dimensional carrier gives

\[
              \mathbb E_\mu[D]=\lambda^2(N-1).
\]

Combining this identity with the rational affine virial theorem gives

\[
 \frac1N\mathbb E_\mu[A]
 \leq \frac{244}{5}
      +\frac{\lambda^2}{2}\left(1-\frac1N\right).
\]

At (lambda=2/5), uniformly in volume,

\[
 \frac1N\mathbb E_\mu[A]\leq\frac{1222}{25},
 \qquad
 \mathbb E_\mu\sqrt{1+\frac AN}
 \leq\frac{\sqrt{1247}}5.
\]

The second inequality is Jensen's inequality.  It supplies exactly the
annealed half-action-density factor left open by the previous certificate.
The numerical constant is deliberately crude; its volume independence is
the relevant point.

## Bilaplacian consequence and remaining barrier

The previously certified envelope

\[
                 A\geq\frac{B_\psi^2}{16q^2N}
\]

now yields actual-measure bounds

\[
 \frac{\mathbb E_\mu[B_\psi^2]}{N^2}
 \leq\frac{1251328}{25},
 \qquad
 \frac{\mathbb E_\mu[B_\phi]}N
 \leq40\sqrt{1222}
 \quad(\lambda=2/5).
\]

These are genuine interacting Gibbs estimates, not reference-measure
estimates.  They are nevertheless not the requested (H^{-1}) theorem.
Bilaplacian energy density can concentrate in the lowest lattice modes, and
the deterministic comparison to the continuum (H^{-1}) norm then loses a
power of the lattice length.

The remaining live route is therefore sharply isolated.  One must prove
global positivity or supply a variational replacement for the orthogonal
Hessian block, and then prove the surviving half-action-density curvature
bound.  The present theorem already controls its annealed weight.  If that
curvature route fails, the next object is the normalized lowest-mode marginal.

## Boundaries

This result does not establish a homogeneous inequality (D\geq cA), global
convexity, a positive global Schur complement, an interacting (H^{-1})
moment, tightness, a continuum measure, a Born rule, a Krein reconstruction,
or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_affine_virial_action_density.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_affine_virial_action_density.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_affine_virial_action_density
```
