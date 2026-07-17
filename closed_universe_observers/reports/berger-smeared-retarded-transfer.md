# Rank-two Berger retarded detector transfer

## Result

The detector matrix is now computed on an exact two-polarization Maxwell
source sector.  This is a physical source-to-field-to-record calculation,
not the earlier dual-probe independence test.

Let

\[
\beta=\frac{2\sqrt{10}}3,
\qquad
u(t)=\frac{\sin(\beta t)}{\beta}.
\]

Choose one smooth switch profile `chi` before evaluating either detector:
`chi=0` for `t<=-1/2` and `chi=1` for `t>=-1/4`.  The two predeclared
potentials and currents are

\[
A_{0,\mathrm{ret}}=\chi u e^1,
\quad
A_{1,\mathrm{ret}}=\chi u e^2,
\qquad
J_b=(\partial_t^2+\beta^2)(\chi u)e^b.
\]

Because `(d_t^2+beta^2)u=0`, each current is supported only in the compact
switch-on slab.  The left-invariant horizontal one-forms are divergence-free,
so `delta J_b=0` exactly.  Directly in the four-dimensional exterior algebra,

\[
d\star d(ae^1)=-(a''+\beta^2a)e^{023}
              =\star((a''+\beta^2a)e^1),
\]

and the `e2` channel is identical.  Both potentials vanish before the source
slab and solve the full forced Maxwell equation.  Retarded uniqueness therefore
identifies them with `G_ret J_b`; no advanced solution or unevaluated kernel is
substituted.

## Detector evaluation

The detector clock centers `3/16` and `3/8` correspond to physical times
`1/4` and `1/2`.  Each clock half-width `1/64` corresponds to physical
half-width `1/48`.  The detector apparatus carries polarization two-forms
`P_0=e0 wedge e1` and `P_1=e0 wedge e2` in the Berger orthonormal coframe;
the local rods transport and localize these apparatus fields.  Thus `D0`
smears the `e01` electric component and `D1` smears `e02`, using smooth
nonnegative unit-mass weights in their local rod windows.  This probe-apparatus
covariance statement is not a raw-`D` or backreacting-apparatus theorem.

On those windows,

\[
\max_{\mathrm{windows}}\beta|t|
=\frac{25\sqrt{10}}{72}<\frac{25}{18}<\frac32<\frac\pi2.
\]

Thus the matching cosine is strictly positive throughout each support.  The
opposite electric polarization vanishes identically.  Consequently

\[
M_{ab}=Q_a[dG_{\rm ret}J_b]
=\begin{pmatrix}C_{00}&0\\0&C_{11}\end{pmatrix},
\]

where

\[
C_{00}=\int\rho_0\cos(\beta t)\,d\mathrm{vol}>0,
\qquad
C_{11}=\int\rho_1\cos(\beta t)\,d\mathrm{vol}>0.
\]

Hence `det(M)=C_00 C_11>0` and `rank(M)=2`.  The two source basis signals
produce persistent record vectors `(C_00,0)` and `(0,C_11)`, so the records
are physically distinguishable after retarded propagation.

## Scope boundary

The switch-on currents are smooth, conserved, compact in spacetime, and
retarded.  Their spatial support is nevertheless the full compact Berger
`S3`; they are homogeneous time-slice emitters, not spatially localized
emitter worldtubes.  The result therefore closes the physical rank-two
transfer gate for this exact source sector, while leaving the stronger
localized-emitter gate open.

Apparatus recoil, Maxwell and gravitational backreaction, raw-`D` and
`K_Berger` descent after adjoining sources, rods, and memories, a complete
interacting observer algebra, and every quantum claim remain open.

Verification:

```bash
python3 closed_universe_observers/generate_berger_smeared_retarded_transfer.py --check
python3 closed_universe_observers/verify_berger_smeared_retarded_transfer.py
python3 -m pytest -q closed_universe_observers/tests/test_berger_smeared_retarded_transfer.py
```
