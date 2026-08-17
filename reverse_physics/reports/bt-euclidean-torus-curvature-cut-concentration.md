# BT torus curvature and cut concentration

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_CURVATURE_CUT_CONCENTRATION_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

## Result

The reciprocal-virial theorem already proved that a positive-action sequence
whose complete residual-gradient quotient collapses at the free infrared scale
must push its residual energy above every fixed field height.  The present
result adds two independent necessities: its unweighted curvature must become
flat, and its canonical current must cancel across every height cut.

Let \(u=e^\psi>0\), normalize \(\min_xu_x=1\), and write

\[
 r_x=\sum_{y\sim x}\left({u_y\over u_x}-1\right),\qquad
 R^2=\sum_xr_x^2,qquad h_x={r_x\over u_x^2}.
\]

The complete logarithmic action gradient is exactly

\[
 g_x=\sum_{y\sim x}c_{xy}(h_y-h_x),
 \qquad c_{xy}=u_xu_y\geq1.
\]

Thus \(g\) is a weighted graph Laplacian applied to the curvature \(h\), not
an unrelated diagnostic.

## Spectral flatness

The associated edge energy obeys

\[
 E=\sum_{\{x,y\}}c_{xy}(h_x-h_y)^2
   =-\langle h,g\rangle
   =-\langle h-\bar h,g\rangle.
\]

On \(T_L^4\), with \(\omega_L=4\sin^2(\pi/L)\), the ordinary torus
Poincare inequality, \(c_{xy}\geq1\), and Cauchy--Schwarz give

\[
 \omega_L\lVert h-\bar h\rVert_2^2
 \leq E
 \leq\lVert h-\bar h\rVert_2\lVert g\rVert_2.
\]

Consequently

\[
 \boxed{{\lVert h-\bar h\rVert_2\over R}
 \leq\sqrt{{Q\over\omega_L^2}}},
 \qquad Q={\lVert g\rVert_2^2\over R^2}.
\]

Free-scale collapse therefore forces global unweighted-curvature flatness.
This remains compatible with a large residual because \(r=u^2h\): high field
weights can amplify an almost flat, small curvature.

## Height-cut current

For a threshold \(K\geq1\), put

\[
 S_K=\{x:u_x>K\},\quad s_K=|S_K|,\quad
 \Gamma_K=\sum_{x\in S_K}g_x.
\]

Cancellation of internal oriented edges gives the exact boundary formula

\[
 \Gamma_K=\sum_{\substack{x\notin S_K,\ y\in S_K\\x\sim y}}
 \left(r_x{u_y\over u_x}-r_y{u_x\over u_y}\right).
\]

Pairing \(g\) with the centered cut indicator proves

\[
 Q\geq {N\Gamma_K^2\over s_K(N-s_K)R^2}.
\]

Since \(N=L^4\), \(s_K(N-s_K)\leq N^2/4\), and
\(\omega_L^2\leq16\pi^4/N\),

\[
 \boxed{{Q\over\omega_L^2}
 \geq{\Gamma_K^2\over4\pi^4R^2}}.
\]

Thus every nontrivial fixed height cut in a collapsing sequence has
\(\Gamma_K/R\to0\).  This says net cancellation, not that every boundary edge
current is small.

## Combined concentration alternative

Let

\[
 F_K={\sum_{u_x\leq K}r_x^2\over R^2},
 \qquad m_K=|\{x:u_x\leq K\}|.
\]

The imported reciprocal-virial certificate gives

\[
 {Q\over\omega_L^2}\geq{A F_K^2\over2\pi^4K^2}.
\]

The present spectral estimate also gives

\[
 {|\bar h|\sqrt{m_K}\over R}
 \leq\sqrt{F_K}+\sqrt{Q/\omega_L^2}.
\]

Therefore, if the action stays bounded away from zero and the normalized
quotient tends to zero, then for every fixed \(K\):

- \(F_K\to0\): residual energy escapes above height \(K\);
- \(\lVert h-\bar h\rVert_2/R\to0\): curvature becomes flat;
- \(\Gamma_K/R\to0\): the height-cut current cancels.

If in addition the low set occupies a fixed positive fraction of the torus,
then \(\lVert h\rVert_2/R\to0\).  Any surviving residual is produced purely
through the multiplier \(u^2\).

In ordinary language, a counterexample can no longer be a merely tall or
localized bump.  It has to hide nearly all of its error at diverging field
height while making the underlying curvature look almost constant and making
the outward currents cancel at every fixed height.  That is a sharply smaller
target, but it is not yet a proof that no target exists.

## Exact fixture

The certificate reconstructs the parity checkerboard on \(T_4^4\), with
\(u=1\) on even vertices and \(u=2\) on odd vertices, using exact rational
arithmetic.  It checks the weighted energy identity, the spectral chain, the
boundary-current identity, the centered-indicator floor, and a low-height
residual fraction of exactly \(4/5\).  The independent verifier recomputes the
fixture without importing the producer.

## Claim boundary and next gate

This result does not establish the all-field torus inequality or construct a
collapsing family.  It does not compare \(h\) and \(r=u^2h\) uniformly, and it
does not prove a concentration--compactness theorem for the high-field
components.  Witten/Poincare transfer, the interacting \(H^{-1}\) moment,
continuum reconstruction, Born/Krein interpretation, and every
LORENTZIAN-CAUSAL claim remain open.

The next exact fork is now specific: either show that residual escape,
curvature flatness, and all-height cut-current cancellation are mutually
incompatible at positive action, or build a nonseparable polynomial-contrast
family satisfying all three and test whether its normalized quotient actually
collapses.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_curvature_cut_concentration.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_curvature_cut_concentration.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_curvature_cut_concentration

The certificate records content-pinned provenance, exact commands, timings,
higher-tier disposition, and the paper and planning receipts.
