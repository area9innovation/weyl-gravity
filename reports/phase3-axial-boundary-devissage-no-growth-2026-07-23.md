# Phase 3 axial boundary devissage and separated-mode no-growth

Date: 23 July 2026

## Result

The exact three-factor filtration of the complete axial \(\ell=2\) Bach
system is compatible with the physical separated-mode boundary class in the
lower half frequency plane:

\[
\text{future-horizon regular}
\quad+\quad
\text{zero incoming / pure outgoing at infinity}.
\]

The repository convention is

\[
e^{+i\omega v}
=e^{+i\omega t}e^{+i\omega r_*}.
\]

Consequently exponential growth means
\(\operatorname{Im}\omega<0\).  In precisely that half-plane the horizon
factor \(e^{+i\omega r_*}\) and infinity outgoing factor
\(e^{-i\omega r_*}\) both decay on a constant-\(t\) slice.

The factor filtration may therefore be restricted to this boundary class,
and successive quotient elimination gives

\[
\boxed{
\text{No complete axial }\ell=2\text{ Bach separated mode is both
future-horizon regular and pure outgoing when }\operatorname{Im}\omega<0.
}
\]

This is a separated-mode spectral no-growth theorem.  It is not a
time-domain decay or complete PDE stability theorem.

## Scalar diagonal factors

The complete six-state system has the exact filtered diagonal factors

\[
L_{\rm RW}^{(2)},\qquad
L_{\rm RW}^{(2)},\qquad
L_x\simeq L_{\rm RW}^{(1)}.
\]

After the previously certified scalar gauges, their Schrödinger operators
are

\[
H_s=-D_{r_*}^2+V_s,
\]

with

\[
V_2=\frac{6(r-2)(r-1)}{r^4},
\qquad
V_1=\frac{6(r-2)}{r^3}.
\]

Both are nonnegative on \(r>2\).  If a scalar factor obeys the two declared
boundary conditions in the lower half-plane, its Schrödinger radial
function is \(L^2(dr_*)\) and

\[
\int\left(|\psi'|^2+V_s|\psi|^2\right)dr_*
=
\omega^2\int|\psi|^2dr_*.
\]

For \(\operatorname{Re}\omega\ne0\) and
\(\operatorname{Im}\omega<0\), the right side has a nonreal coefficient.
For \(\operatorname{Re}\omega=0\), it has \(\omega^2<0\).
Neither is compatible with the real nonnegative left side for a nonzero
mode.  Thus the spin-two and spin-one scalar boundary kernels both vanish.

## Exact future-horizon germ filtration

The future-horizon-regular carrier plane has basis
\((XH0a,XH0b)\).  Its spin-one quotient amplitudes are

\[
A=4\omega^2-3i\omega+4,
\qquad
B=4(\omega-i)(2\omega-i).
\]

The combination

\[
RH=XH0a-\frac{A}{B}XH0b
\]

kills the quotient and lies in the carrier spin-two submodule.  The three
factor amplitudes are

\[
\begin{aligned}
RH &: \frac{i\omega(4\omega-i)}{2(\omega-i)},\\
SH=XH0b &: 4(\omega-i)(2\omega-i),\\
EH=EH0 &: -\frac{i\omega(4\omega-i)}{4(\omega-i)}.
\end{aligned}
\]

They are all nonzero in the lower half-plane.  The recurrence factors
\(n+4i\omega\) and \(n+2+4i\omega\) also cannot vanish there: writing
\(\omega=a-i\kappa\), \(\kappa>0\), their real parts are respectively
\(n+4\kappa\) and \(n+2+4\kappa\).

Thus the local exact filtration restricts to the future-horizon-regular
germ space without a collision or missing factor line.

## Exact pure-outgoing infinity germ filtration

Applying the exact quotient \(y=r^2(r-2)L_{\rm RW}P\) to the certified
oscillatory carrier heads gives

\[
\pi_x(XI2)=2(16\omega^2-4i\omega-5),
\qquad
\pi_x(XI3)=-2i\omega.
\]

Therefore

\[
RO
=XI2-\frac{i(16\omega^2-4i\omega-5)}{\omega}XI3
\]

is the outgoing carrier spin-two line, while \(SO=XI3\) lifts the spin-one
quotient.  Their scalar outgoing amplitudes are

\[
RO:1,\qquad SO:-2i\omega.
\]

Independently applying the exact Einstein master map

\[
\Psi=\frac{(1-2/r)H_1+H_0}{r}
\]

to the \(EI2\) head gives the nonzero outgoing amplitude

\[
EO=EI2:\frac12.
\]

Hence the pure-outgoing germ space has the same exact three-step factor
filtration.  The rational reconstruction denominator
\(\omega r-2i\) cannot vanish for \(r>2\) in the lower half-plane.

The theorem needs exactness of the local endpoint germ filtrations and
exact kernel identification on the simultaneous two-ended space.  It does
not assume that an arbitrary quotient solution admits a global two-ended
lift.

This preservation statement is intrinsic.  It uses the exact chain maps

\[
J:M_{\rm RW}\longrightarrow M_{A4},
\qquad
K:M_{A4}\longrightarrow M_x,
\qquad
KJ=0,
\]

and the Einstein-kernel master map \(U\), together with the weighted
spin-one variable

\[
y=r^2(r-2)K_0(u).
\]

These maps act on the weighted ingoing/outgoing germ modules themselves.
The displayed endpoint bases only witness their ranks.  Consequently the
zeros and poles of a chosen frame normalization are irrelevant to the
lower-half-plane boundary theorem.  The only reconstruction denominators
needed intrinsically are \(\omega\) and \(\omega r-2i\), neither of which
vanishes for \(\operatorname{Im}\omega<0\), \(r>2\).

## Successive quotient elimination

Let \(u\) be a complete six-state Bach mode in the declared lower-half-plane
boundary class.

1. Project \(u\) to the spin-one \(L_x\) quotient.  Boundary preservation
   makes this a spin-one scalar mode with both boundary conditions.  The
   energy theorem forces the quotient to vanish.
2. Exactness puts the Ricci carrier in the spin-two Regge--Wheeler
   submodule.  Its scalar master again has both boundary conditions, so it
   vanishes.
3. The remaining solution lies in the metric Einstein-kernel
   Regge--Wheeler factor.  Its master also vanishes.

Therefore \(u=0\).

This argument is insensitive to whether the full differential module
splits as a direct sum.  The certified filtration and boundary-compatible
kernel identifications are sufficient.

## Intrinsic regularized Evans product

For each scalar spin \(s\), normalize the future-horizon-regular Jost
solution to unit horizon amplitude and write

\[
\psi_{H,s}
=A_{{\rm in},s}e^{+i\omega r_*}
{}+
 A_{{\rm out},s}e^{-i\omega r_*}
\]

at infinity.  The intrinsic factor Evans function is

\[
\boxed{
E_{\rm reg}(\omega)
=A_{{\rm in},2}(\omega)^2A_{{\rm in},1}(\omega).
}
\]

It removes the rational endpoint-frame prefactor appearing in the
coordinate determinant of \(T_-\).  The factor multiplicities are two
spin-two copies and one spin-one copy.  The energy argument proves

\[
E_{\rm reg}(\omega)\ne0
\qquad
\text{for }\operatorname{Im}\omega<0.
\]

## Exact next gate at a simple damped spin-two QNM

The no-growth theorem does not determine the multiplicity structure of a
damped upper-half-plane spin-two QNM.  Let \(\omega_*\) be a simple zero of
the scalar spin-two Evans factor and set

\[
\delta=\omega-\omega_*.
\]

Let \(\mathcal O\) be the discrete valuation ring of analytic germs at
\(\omega_*\).  After filtration-preserving analytic left and right
equivalences, the two spin-two copies in the full filtered system reduce
locally to

\[
\begin{pmatrix}
a(\omega)&c(\omega)\\
0&a(\omega)
\end{pmatrix}.
\]

Under a further filtration-preserving frame change,

\[
c\longmapsto u\,c+a\,d,
\qquad
u\in\mathcal O^\times,\quad d\in\mathcal O.
\]

Therefore

\[
\boxed{[c]\in\mathcal O/(a)}
\]

is the invariant extension class, up to multiplication by a unit.  If

\[
\operatorname{ord}(a)=m,
\qquad
\operatorname{ord}(c)=n,
\]

then the two Smith valuations are exactly

\[
\boxed{
\min(m,n),
\qquad
2m-\min(m,n).
}
\]

For a simple scalar zero \(m=1\), \(n=0\) gives
\(\operatorname{diag}(1,\delta^2)\), whereas \(n\ge1\) gives
\(\operatorname{diag}(\delta,\delta)\).

The leading extension coefficient can be tested through the Fredholm
pairing

\[
\Gamma_*
=
\left\langle
\psi_*^{\rm adj},
\mathcal E(\omega_*)\psi_*
\right\rangle,
\]

where \(\mathcal E\) is the exact off-diagonal extension and the QNM and
adjoint QNM are normalized in regular analytic endpoint patches.
At a simple zero, \(c(\omega_*)\) is a normalization multiple of
\(\Gamma_*\), but neither factor is certified nonzero here.  A more
structural next test is the congruence

\[
\boxed{
c\equiv q\,A_{{\rm in},2}'\pmod{A_{{\rm in},2}}.
}
\]

Computing \(\Gamma_*\) requires a boundary-convergent adjoint pairing in
regular local patches.  No Smith case is selected here; this is the exact
next extension gate.  In particular, neither the spectral-derivative
congruence nor nonvanishing of \(q\) modulo \(A_{{\rm in},2}\) is claimed.

## Positive-real direct-integral context

The all-\(\omega>0\) endpoint Witt decomposition uses the weighted majorant

\[
a(\omega)=\frac{576\omega}{5},
\qquad
b(\omega)=\frac{32}{15\omega}.
\]

Thus an all-positive-frequency direct integral belongs to this weighted
majorant topology rather than an unweighted coordinate norm.  The
\(\omega=0\) threshold remains separate.

## Upper-half-plane frame events

The points

\[
\omega=\frac i4,\qquad \frac i2,\qquad i
\]

lie in the **damped** upper half-plane under \(e^{+i\omega t}\).  They are
exactly where the chosen horizon or reconstruction frames exhibit:

* \(4\omega-i=0\), an Einstein horizon collision and the reconstruction
  wall at \(r=8\);
* \(2\omega-i=0\), a carrier horizon collision and the wall at \(r=4\);
* \(\omega-i=0\), a spin-one Frobenius resonance and the wall at \(r=2\).

They are therefore recorded only as damped
Frobenius/reconstruction-frame events.  Deciding whether the intrinsic
regularized Evans function vanishes or remains nonzero at any of them
requires local analytic patches and is open.

## Claim boundary

The result does not establish:

* time-domain boundedness, decay, completeness or a full PDE stability
  theorem;
* absence of damped upper-half-plane quasinormal frequencies;
* the regularized Evans status of \(i/4,i/2,i\);
* the Fredholm extension pairing or Smith type at a simple damped
  spin-two QNM;
* polar parity or general \(\ell\);
* positivity, CPT completion, particles, ghosts, unitarity or nonlinear
  stability.

EVIDENCE: black_hole_programme/phase3/axial_boundary_devissage_no_growth/receipt.json
CLOSE-OUT: DONE — exact boundary dévissage excludes growing axial ell=2
separated modes while preserving the stated time-domain and damped-QNM
limitations.
