# BT torus global virial compatibility

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GLOBAL_VIRIAL_COMPATIBILITY_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

## Result

Reciprocal-edge compatibility lowers the action-density ceiling for every
possible collapsing BT four-torus family from \(32\) to \(11\).  On a finite
8-regular graph, let

\[
 s_x=\sum_{y\sim x}e^{\psi_y-\psi_x},\qquad
 r_x=s_x-8,\qquad
 A={1\over2}\sum_xr_x^2,
\]

and let \(g=\nabla_\psi A\).  The new global virial theorem is

\[
 \boxed{\langle\psi,g\rangle\geq2A-22N.}
\]

Consequently, on \(T_L^4\), for every \(0<\epsilon\leq32\),

\[
 \boxed{
 A\geq(11+\epsilon)L^4
 \quad\Longrightarrow\quad
 {Q\over\omega_L^2}\geq
 {\epsilon^2\over8192\pi^4},}
 \qquad
 Q={\|g\|_2^2\over\|r\|_2^2}.
\]

Every sequence with \(Q/\omega_L^2\to0\) must therefore satisfy

\[
 \boxed{
 \limsup_{L\to\infty}{A\over L^4}\leq11,
 \qquad
 \limsup_{L\to\infty}{W^2\over L^4}\leq22.}
\]

Equivalently, its largest neighboring-field ratio has asymptotic coefficient
at most \(\sqrt{22}\), rather than the previous coefficient \(8\).

This still does not prove the all-field inequality.  The sub-\(11\)
action-density sector remains open.

## Why the isolated-vertex bound was not sharp globally

Put

\[
 t_x=\sum_{y\sim x}e^{\psi_y-\psi_x}
                    (\psi_y-\psi_x).
\]

The exact radial pairing is

\[
                         \langle\psi,g\rangle=\sum_xr_xt_x.
\]

At fixed \(s=\sum_iw_i\), Jensen and superadditivity give the two extremal
bounds

\[
 t\leq s\log s\quad(0<s<8),\qquad
 t\geq s\log(s/8)\quad(s\geq8).
\]

Therefore the vertex defect \(r^2-rt\) is at most

\[
 \Phi_-(s)=(8-s)^2+(8-s)s\log s,\qquad 0<s<8,
\]

or

\[
 \Phi_+(s)=(s-8)^2-(s-8)s\log(s/8),\qquad s\geq8.
\]

The predecessor bounded each vertex by \(64\).  That bound is sharp as
\(s\to0\), but a graph cannot have \(s_x\to0\) at every vertex: every small
edge ratio appears reciprocally at its other endpoint.  The exact identity is

\[
 \sum_x(s_x-8)
 =\sum_{\{x,y\}}\left(
 {\Omega_y\over\Omega_x}+{\Omega_x\over\Omega_y}-2\right)\geq0.
\]

The correct object is therefore an affine, rather than constant, majorant of
\(\Phi\).

## Exact affine majorant

For every \(s>0\),

\[
 \boxed{\Phi(s)+{21\over4}(s-8)\leq22.}
\]

For \(0<s<8\), subtracting the right-hand side leaves

\[
 s\left[(8-s)\log s+s-{43\over4}\right].
\]

For \(s\leq1\) this is negative directly.  Above one, the bracket has
derivative \(8/s-\log s\), so its unique possible maximum satisfies
\(s\log s=8\).  The rational Taylor partial sum

\[
 1+{16\over9}+{(16/9)^2\over2}+{(16/9)^3\over6}
 ={11579\over2187}>{9\over2}
\]

shows that the maximizer lies above \(9/2\); it lies below \(8\) because
\(\log8>1\).  At the maximizer the bracket is

\[
 s+{64\over s}-{75\over4}
 \leq{337\over18}-{75\over4}<0.
\]

For \(s\geq8\), put \(y=s/8-1\).  The elementary inequality

\[
 \log(1+y)\geq{2y\over2+y}
\]

follows because the derivative of the difference is
\(y^2/[(1+y)(2+y)^2]\).  It reduces the affine-majorant claim to

\[
 p(y)=64y^3-42y^2-62y+44\geq0.
\]

On \(0\leq y\leq1\), \(p\) has only one positive critical point.  Since
\(p'(83/100)>0\), that minimum lies below \(83/100\).  Using
\(96y^2=42y+31\) at the critical point gives

\[
 p(y)={1895-2278y\over48}
 >{1895-2278(83/100)\over48}>0.
\]

For \(y\geq1\),

\[
 p(y)\geq22y^2-62y+44
       =2(11y^2-31y+22)>0,
\]

because the last quadratic has discriminant \(-7\).  This proves the
majorant on both branches without numerical optimization.

Summing it over vertices and using reciprocal-edge compatibility yields

\[
 \sum_x(r_x^2-r_xt_x)
 \leq22N-{21\over4}\sum_x(s_x-8)\leq22N,
\]

which is exactly the boxed global virial theorem.

## Four-torus consequence

Write \(x=A/N\), with \(N=L^4\).  When \(11<x<64\),

\[
 \langle\psi,g\rangle\geq2(x-11)N.
\]

As in the predecessor,

\[
 W\leq8+\sqrt{2A}<13L^2,\qquad
 \|\psi\|_2<4N.
\]

Cauchy--Schwarz and \(\|r\|_2^2=2A<128N\) give

\[
 \boxed{NQ\geq{(x-11)^2\over512}},
\qquad
 \boxed{{Q\over\omega_L^2}
        \geq{(x-11)^2\over8192\pi^4}}.
\]

Above \(x=64\), the already-certified middle and extensive-action branches
give \(Q/\omega_L^2\geq1/(8\pi^4)\).  Since
\(\epsilon^2/8192\leq1/8\) for \(0<\epsilon\leq32\), the branches join to
give the stated fixed-margin theorem.

Collapse then forces the positive part of \(A/L^4-11\) to vanish.  Finally,

\[
 {W\over L^2}\leq{8\over L^2}+\sqrt{2A\over L^4}
\]

gives the contrast-square coefficient \(22\).

## What remains

The live family is confined to

\[
 A\leq(11+o(1))L^4,\qquad
 W\leq(\sqrt{22}+o(1))L^2.
\]

The next step must control the scalar-curvature superlevel currents or
classify concentration profiles inside this genuinely low-action sector.
The negative alternative remains a nonseparable family satisfying these
restrictions and driving the normalized quotient to zero.

This certificate does not establish the all-field torus inequality,
Witten/Poincare coercivity, the interacting \(H^{-1}\) moment, a continuum
measure, Born or Krein reconstruction, or anything LORENTZIAN-CAUSAL.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_global_virial_compatibility.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_global_virial_compatibility.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_global_virial_compatibility

The producer passed 10/10 checks, the independent verifier 12/12, and the
focused mutation suite 12/12.  The unchanged sharp-virial predecessor also
passed.  Planning imported 1,716 nodes with no invalid item or malformed
event, and Paper 21's RF-91 claim map verified before its 83-page PDF was
rebuilt twice.  Exact timings, memory ceilings, higher-tier disposition, and
the advisory Science Forge boundary are stored in the machine certificate.
