# BT seven-point tree and Cox-state selection

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

**Certificate:** `REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1`

## Result

The complete Bateman--Turok seven-point tree fixes the third leading ordered
count coefficient to

\[
 P_3(a)=\frac{9a^3}{8192}+o(a^3)
       =\frac{27a^3}{24576}+o(a^3).
\]

Together with the certified one- and two-count sectors, this gives

\[
 M_1(a)=\frac a{16},\qquad
 M_2(a)=\frac{5a^2}{256},\qquad
 M_3(a)=\frac{27a^3}{4096},
\]

and factorial cumulants

\[
 \kappa_1(a)=\frac a{16},\qquad
 \kappa_2(a)=\frac{a^2}{64},\qquad
 \kappa_3(a)=\frac{7a^3}{2048}.
\]

The gamma-Cox completion selected only from the first two moments would give
\(M_3=45a^3/4096\), or \(P_3=15a^3/8192\).  The tree result is three
fifths of that value, so gamma-Cox is ruled out.

The tree coefficient nevertheless remains inside the exact nonnegative-rate
moment cone.  It therefore selects a positive minimal two-atom Cox dilation
through three moments.  This is a concrete non-Gaussian resolution-local
state, not yet a complete physical probability or a dynamical spacetime
Møller operator.

## Complete seven-point tree

For seven labeled external legs,

\[
 V_3+2V_4=5.
\]

The exact topology counts are

\[
 \begin{array}{c|c}
 (V_3,V_4)&\hbox{trees}\\ \hline
 (5,0)&945\\
 (3,1)&1260\\
 (1,2)&280
 \end{array}
\]

for 2,485 trees in total.  The relative tree signs before the common
seven-delta-prime sign are \((-,+,-)\).

The seven-point cyclic chart consists of seven adjacent pair squares and
seven adjacent triple squares.  Momentum conservation identifies every
adjacent quartet square with the square of its complementary triple.  For
the nested four-daughter history, retain

\[
 \begin{aligned}
 x_0,x_1,s_{01}&\sim\delta\epsilon_1\epsilon_2,\\
 x_2,s_{012}&\sim\delta\epsilon_2,\\
 x_3,s_{0123}&\sim\delta,\\
 x_4,x_5,x_6&\sim\delta,
 \end{aligned}
\]

where the last three masses are square-free spectator jets.  The limits are
taken in the order \(\delta\to0\), \(\epsilon_1\to0\), then
\(\epsilon_2\to0\).

The complete amplitude starts at \(\delta^2\).  The three-spectator
coefficient of its square is identical at two unrelated exact producer hard
fixtures.  An independent verifier explicitly enumerates all 2,485 rooted
trees with the invariant triangle form of the cubic vertex at a third hard
fixture.

Define

\[
 A=(a_0-a_1)^2-2\tau_1(a_0+a_1)+2\tau_1^2,
\]

\[
 B=a_2A+2\tau_2(-A+3\tau_1^2),
\]

\[
 C=a_2B+2\tau_2^2(A+\tau_1^2),
\]

and

\[
 D=a_3C+2\tau_3(-C+3\tau_2^2A).
\]

The strong-order kernel is

\[
 K_7=\frac{3a_3^3CD}
 {128\tau_1^4\tau_2^4\tau_3^3}.
\]

As at six points, all tree topologies contribute before this compact
factorization; it is not an iterated-pole approximation.

## Three exact threshold reductions

For a two-body threshold define the invariant-cutoff moments

\[
 J_n(r)=\operatorname{FP}_{\Lambda\to\infty}
 \int_{(1+\sqrt r)^2}^{\Lambda}
 \frac{\sqrt{\lambda(u,1,r)}}{u^n}\,du.
\]

The outer reduction uses \(J_4\) and \(J_3\).  Both have unit
\(r\log r\) coefficient, and they send

\[
 CD\longmapsto C(-C+6\tau_2^2A).
\]

Expanding the latter in the middle parent invariant requires
\(J_5,J_4,J_3,J_2,J_1\).  The power-divergent \(J_1,J_2\) terms are
subtracted at fixed physical invariant \(u=\Lambda\).  All five moments
have the same unit \(r\log r\) coefficient.  Their exact coefficient sum
collapses to the inner kernel

\[
 (A+8\tau_1^2)(5A-8\tau_1^2).
\]

For the final threshold set \(r=m^2\) and rationalize by

\[
 u=1+m^2+m(z+z^{-1}).
\]

Fixed \(u=\Lambda\) means
\(z=m/\Lambda+O(\Lambda^{-2})\).  Only the logarithmic residues at
\(z=0\) and \(z=-m\) contribute to the nonanalytic coefficient.  They are

\[
 R_0=8(22m^4+13m^2+22),
\]

\[
 R_{-m}=\frac{2(1+m^2)(88m^4-151m^2+88)}{m^2-1}.
\]

Consequently the physical-cutoff (log m) coefficient is

\[
 -(R_0+R_{-m})
 =-\frac{2m^2(176m^4-99m^2-27)}{m^2-1}
 =-54m^2+O(m^4).
\]

Since \(r\log r=2m^2\log m\), the inner coefficient is \(-27\).
The raw three-threshold cocycle is therefore

\[
 \frac3{128}(-27)=-\frac{81}{128}.
\]

Seven external delta-prime distributions supply a minus sign, leaving the
signed coefficient \(+81/128\).  At fixed physical invariant, divergent
local subtraction coefficients are analytic in the external mass ratio and
cannot alter this nonanalytic coefficient.  A fixed-\(z\) cutoff is excluded
because it is external-mass dependent.

## Factorials

The seven-point phase factor before the external-mass kernel is

\[
 N_7=
 1024\frac1{2!5!}\frac12\frac1{2^3}
 \frac1{32^4}\,4^3
 =\frac1{61440}.
\]

Relative to the hard coefficient \(N_4=1/16\) and hard square-free kernel
\(3/2\), one selected nested history contributes

\[
 \frac{N_7}{N_4}\frac{81/128}{3/2}
 =\frac9{81920}.
\]

There are

\[
 \binom52\,3\,2=60
\]

labeled nested histories.  The ordered three-resolution simplex has volume
\(a^3/3!=a^3/6\).  Hence

\[
 60\frac16\frac9{81920}a^3=\frac{9a^3}{8192}.
\]

## Positive moment cone and state

For a scalar Cox process, conditionally on a nonnegative random rate \(Y\),
the interval count is Poisson with mean \(aY\).  Its leading factorial
moments are

\[
 M_n(a)=a^n\mathbb E[Y^n].
\]

The tree fixes

\[
 m_1=\frac1{16},\qquad
 m_2=\frac5{256},\qquad
 m_3=\frac{27}{4096}.
\]

Nonnegativity of \(Y\) gives the Stieltjes inequality

\[
 m_1m_3\ge m_2^2,
\]

or

\[
 m_3\ge\frac{m_2^2}{m_1}=\frac{25}{4096}.
\]

The tree exceeds this lower bound by \(1/2048\).  Thus scalar Cox
positivity survives seven points.

The gamma law with shape and scale \(1/4\) matches \(m_1,m_2\) but has
\(m_3=45/4096\), so it is excluded.  The unique intensity law supported on
at most two atoms and matching all three tree moments has

\[
 x_\pm=\frac{11\pm\sqrt{113}}{64},
\]

\[
 p_- =\frac{\sqrt{113}+7}{2\sqrt{113}},\qquad
 p_+ =\frac{\sqrt{113}-7}{2\sqrt{113}}.
\]

Both support points and both weights are strictly positive.  Its count
generating function is

\[
 G_a(z)=p_-e^{ax_-(z-1)}+p_+e^{ax_+(z-1)}.
\]

Let \(F_I\) be the certified rank-two coherent displacement with
\(\lVert F_I\rVert^2=|I|/16\).  On a bounded interval define

\[
 \omega_I(X)=\sum_{\sigma=\pm}p_\sigma
 \left\langle
 W(\sqrt{16x_\sigma}F_I)\Omega,
 XW(\sqrt{16x_\sigma}F_I)\Omega
 \right\rangle.
\]

This convex mixture is positive, normalized, locally normal, compatible
under interval inclusion, and translation covariant.  Equivalently it has a
controlled unitary dilation

\[
 U_I=\bigoplus_{\sigma=\pm}
 W(\sqrt{16x_\sigma}F_I)
\]

on a two-dimensional classical intensity carrier tensored with the local
bosonic Fock space.  Counts in disjoint intervals are conditionally
independent but marginally correlated.

This is the minimal-support Cox completion, not the unique positive process.
Total counts also do not determine whether the intensity is shared by all
three pair channels or decomposes into correlated channel intensities.

## Next discriminator and boundary

The two-atom completion predicts

\[
 m_4=\frac{73}{32768},\qquad
 P_4(a)=\frac{73a^4}{786432}+o(a^4),\qquad
 \kappa_4(a)=\frac{17a^4}{65536}.
\]

The complete eight-point quadruple-strongly-ordered tree is the next scalar
discriminator.  A channel-resolved seven-point projector is independently
needed to determine the three-channel intensity architecture.

This certificate does not establish a complete (2\to5) probability,
universal hard-angle independence, an all-order count law, a dynamical BT
zero mode, a spacetime-local Møller/LSZ operator, Eq. (19), anything
`LORENTZIAN-CAUSAL`, or a metric/BRST lift.

## Verification receipt

All symbolic jobs ran sequentially under `ulimit -v 500000`.  The exhaustive
producer and independent verifier are separate rails.  The verifier retains
all 2,485 rooted tree values, uses the invariant triangle cubic vertex, and
extracts threshold residues by the explicit derivative formula for poles of
known order rather than calling the producer's residue routine.

The close-out runs were:

| rail | exact command | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| exhaustive producer | `ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_seven_point_cox_selection.py --write --check` | 18/18 PASS | 38.51 s | 90,296 kB |
| independent verifier | `ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_seven_point_cox_selection.py` | 17/17 PASS | 19.43 s | 122,944 kB |
| mutation and unit suite | `ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_seven_point_cox_selection` | 15/15 PASS | 41.82 s | 122,820 kB |
| Paper V, second pass | `ulimit -v 500000; cd paper && pdflatex -interaction=nonstopmode -halt-on-error 05-interaction-obstructions.tex` | PASS | 0.41 s | 50,836 kB |
| Paper VI, second pass | `ulimit -v 500000; cd paper && pdflatex -interaction=nonstopmode -halt-on-error 06-einstein-weyl-interaction-obstructions.tex` | PASS | 0.43 s | 51,040 kB |
| Science Forge import | `FORGE_LIB=/home/alstrup/area9/tango/forge/lib /tmp/forgebin -run /home/alstrup/area9/tango/forge/tools/science-forge/sfc.forge -- import-program planning/work-items /tmp/bt7-science-forge-graph.json graph` | 1,388 nodes, 0 invalid items, 0 malformed events | -- | -- |

The advisory `ci/science-forge-shadow.sh` completed with exit zero while
reporting the pre-existing Forge toolchain/stdlib hash mismatch, compiler
diagnostic E9118 in the independent bridge audit, and corpus drift from 976
to 1,530 certificates.  Those advisory findings are not counted as a pass of
the bridge audit.

An exploratory mixed-sign hard fixture was interrupted after 517 seconds at
approximately 317,644 kB because exact polynomial-gcd simplification was
pathological.  It was neither an OOM nor a pass and contributes no evidence
to the certificate.  The two completed producer fixtures and distinct third
verifier fixture are the declared scope of hard-angle testing.

Tier 0 parse, structured-data, whitespace, and staged-diff checks and Tier 1
scoped tests were run.  Tier 2 was unnecessary because this is a new leaf
certificate over unchanged content-addressed predecessors; Tier 3 was not
run because no freeze, lifecycle promotion beyond `COEFFICIENT_COMPUTED`, or
shared core algebra changed.
