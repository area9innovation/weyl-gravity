# BT torus sharp-virial action-density gate

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SHARP_VIRIAL_DENSITY_GATE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The residual action density of a collapsing BT four-torus family cannot stay
a fixed amount above \(32\).  Let

\[
 r_x={\Delta\Omega_x\over\Omega_x},\qquad
 A={1\over2}\sum_xr_x^2,\qquad
 Q={\|g\|_2^2\over\|r\|_2^2},\qquad N=L^4,
\]

where \(g\) is the complete log-field action gradient.  For every
\(0<\epsilon\leq32\),

\[
 \boxed{
 A\geq(32+\epsilon)L^4
 \quad\Longrightarrow\quad
 {Q\over\omega_L^2}\geq
 {\epsilon^2\over8192\pi^4}.}
\]

Consequently every sequence with \(Q/\omega_L^2\to0\) obeys

\[
 \boxed{
 \limsup_{L\to\infty}{A\over L^4}\leq32,
 \qquad
 \limsup_{L\to\infty}{W\over L^2}\leq8.}
\]

The previous certificate only forced \(A/L^4<488/5\) and \(W<16L^2\)
below one fixed floor.  The improvement comes from optimizing the virial
defect at a negative-residual vertex instead of bounding its two pieces
separately.  This is still not the all-field theorem: the sector with action
density at most \(32\) remains open.

## The sharp vertex defect

Put

\[
 s_x=\sum_{y\sim x}e^{\psi_y-\psi_x},\qquad
 r_x=s_x-8,
\]

and

\[
 t_x=\sum_{y\sim x}e^{\psi_y-\psi_x}
                    (\psi_y-\psi_x).
\]

The exact radial pairing is

\[
                         \langle\psi,g\rangle=\sum_xr_xt_x.
\]

For \(r_x\geq0\), the predecessor's convexity argument gives
\(r_xt_x\geq r_x^2\).  Suppose \(r_x<0\), and write \(s=s_x<8\).
Superadditivity of \(w\log w\) gives \(t_x\leq s\log s\).  For
\(0<s\leq1\), this makes \(r_xt_x\geq0\geq r_x^2-64\).  For
\(1<s<8\), the required inequality reduces exactly to

\[
 H(s):=16-s-(8-s)\log s\geq0.
\]

Now

\[
 H'(s)=\log s-{8\over s},\qquad
 H''(s)={1\over s}+{8\over s^2}>0.
\]

Thus an interior minimum, if present, is unique and satisfies
\(s\log s=8\).  It lies in \((4,8)\), and at that point

\[
 H(s)=24-s-{64\over s}\geq4,
\]

because \(4<s<8\) implies \(s+64/s\leq20\).  The endpoint values are
positive as well.  Hence, vertex by vertex,

\[
 r_xt_x\geq r_x^2-64,
\]

and therefore

\[
 \boxed{\langle\psi,g\rangle\geq2A-64N.}
\]

The constant \(64=8^2\) is attained as a limiting defect when \(s\to0\),
so this vertexwise argument cannot lower it.

## The density interval \(32<A/N<64\)

Write \(x=A/N\).  In this interval the sharp virial theorem gives

\[
                         \langle\psi,g\rangle\geq2(x-32)N.
\]

The exact edge-ratio estimate gives

\[
 W\leq8+\sqrt{2A}<8+\sqrt{128}L^2<13L^2.
\]

In mean-zero log gauge, the torus diameter bound and \(L\geq4\) imply

\[
 \|\psi\|_2
 \leq2L\,L^2\log(13L^2)<4L^4=4N.
\]

Here \(\log13<3\) and \(2\log L\leq L\), so
\(\log(13L^2)<3+L\leq2L\).  Cauchy--Schwarz now yields

\[
 \|g\|_2^2\geq{(x-32)^2\over4}.
\]

Since \(\|r\|_2^2=2A<128N\),

\[
 \boxed{NQ\geq{(x-32)^2\over512}.}
\]

Using \(\omega_L^2\leq16\pi^4/L^4=16\pi^4/N\) gives the normalized
version in the theorem.

## Joining the already-certified large-action branch

For \(64\leq x<488/5\), the sharp virial bound gives
\(\langle\psi,g\rangle\geq A\).  The predecessor's contrast and range
bounds apply throughout this bounded interval, giving

\[
                         NQ\geq2,
 \qquad {Q\over\omega_L^2}\geq{1\over8\pi^4}.
\]

For \(x\geq488/5\), the independently certified extensive-action theorem
gives

\[
 {Q\over\omega_L^2}\geq{61\over320\pi^4}
                         >{1\over8\pi^4}.
\]

Because \(\epsilon\leq32\), both large-density branches dominate
\(\epsilon^2/(8192\pi^4)\).  This proves the fixed-margin theorem without
assuming monotonicity outside the bounded interval.

Finally, collapse forces the positive part of \(A/N-32\) to vanish.  The
edge-ratio identity then gives

\[
 {W\over L^2}\leq{8\over L^2}+\sqrt{2A\over L^4},
\]

and hence the asymptotic coefficient \(8\).

## What remains

The live family is now confined to

\[
                         A\leq(32+o(1))L^4,
 \qquad W\leq(8+o(1))L^2.
\]

The next proof must use torus-specific scalar-curvature level sets or a
critical-dimension profile decomposition inside this sector.  The negative
alternative remains a genuinely nonseparable family satisfying these two
restrictions and driving the normalized quotient to zero.

This certificate does not establish the all-field torus inequality,
Witten/Poincare coercivity, the interacting \(H^{-1}\) moment, a continuum
measure, Born or Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_sharp_virial_density_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_sharp_virial_density_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_sharp_virial_density_gate
```

The producer passed 10/10 checks, the independent verifier 11/11, and the
focused mutation suite 11/11.  The unchanged affine-virial and
extensive-action predecessor verifiers also passed.  Planning imported 1,715
nodes with no invalid item or malformed event, and Paper 21's RF-90 claim map
verified before its 82-page PDF was rebuilt twice.  Exact timings, memory
ceilings, higher-tier disposition, and the advisory Science Forge boundary
are stored in the machine certificate.
