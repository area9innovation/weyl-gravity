# Fully rearranged BT bubble-with-bridge finite-time affiliation

**Certificate:**
REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1

**Tags:** LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE.
**Lifecycle:** COEFFICIENT_COMPUTED on the selected positive source packet.

## Result

The covariant bubble-with-bridge remainder is now affiliated with an actual
finite-duration third-Dyson graph.  The construction retains the full complex
renormalized bubble, all three vertex times, the bridge shell, and the local
MSbar forest term.  It does not multiply the energy-diagonal four-point
\(B_T\) into a tree graph.

For one labelled role \(R=(a;bc;def)\), call its vertices \(A,B,C\): \(A\)
is the one-leg junction, \(B\) the two-leg bubble leaf, and \(C\) the
three-leg tree leaf.  Let

\[
 \mathbf Q_R=\mathbf p_b+\mathbf p_c,
 \qquad
 \mathbf K_R=\mathbf p_d+\mathbf p_e+\mathbf p_f,
 \qquad E_K=|\mathbf K_R|.
\]

Define the full renormalized bubble time distribution by

\[
 b_{\mu,\mathbf Q}(\tau)
 =\int_{\mathbb R}{d\nu\over2\pi}e^{-i\nu\tau}
 \left\{\log{\mu^2\over-(\nu^2-|\mathbf Q|^2)-i0}+2\right\},
\]

and the bridge distribution by

\[
 d_{E_K}(\tau)={e^{-iE_K|\tau|}\over2E_K}.
\]

The exact switched scalar graph is

\[
 \boxed{
 J_{T,R}=\int_{[0,T]^3}dt_A\,dt_B\,dt_C\;
 e^{i(q_A^0t_A+q_B^0t_B+q_C^0t_C)}
 b_{\mu,\mathbf Q_R}(t_A-t_B)d_{E_K}(t_A-t_C).}
\]

The complete selected-source coefficient is

\[
 \boxed{
 T_{6,\mathrm{bb},T}
 ={4\over16\pi^2}\sum_{R=1}^{60}J_{T,R}W_R.}
\]

The factor four and the sixty exact species tensors are imported from the
covariant coefficient certificate.  No additional Dyson factorial occurs:
the six chronological sectors fill the three-time cube.

## Why this is off diagonal

Writing

\[
 F_T(x)=\int_0^T e^{ixt}\,dt,
\]

Fourier transformation of both internal time distributions gives the
equivalent exact pairing

\[
 \boxed{
 \begin{split}
 J_{T,R}={}&\int{d\nu\,d\rho\over(2\pi)^2}
 B_\mu(\nu,\mathbf Q_R)D_F(\rho,E_K)\\
 &\quad\times F_T(q_A^0-\nu-\rho)
 F_T(q_B^0+\nu)F_T(q_C^0+\rho),
 \end{split}}
\]

with

\[
 D_F(\rho,E_K)={i\over\rho^2-E_K^2+i0}.
\]

The numerator \(i\) is fixed, not optional: with the displayed inverse-Fourier
convention it gives exactly \(d_{E_K}(\tau)\).  Removing this single common
Feynman phase recovers the phase-stripped convention used for the covariant
coefficient.

The internal \(\nu\) and \(\rho\) coefficients cancel across the three window
arguments, whose sum is the total external energy.  There are nevertheless
two independent internal spectral energies at finite \(T\).

The preceding active-loop formula \(B_T(P)\) instead describes an
energy-diagonal second-Dyson tree--loop cross after division by the tree
duration.  It contains only the corresponding one-variable Fejér average.
The three-factor formula above is the missing object and shows directly why
\(B_T\) cannot be inserted multiplicatively.

## Six chronological sectors

The graph has two parallel \(A\!-\!B\) edges and one \(A\!-\!C\) bridge.
For each permutation of \(A,B,C\), the two intermediate defects are obtained
by cutting the internal edges between the earlier and later vertices.

All six sectors separate \(A\) and \(B\) across at least one interval:

- in four sectors only one intermediate defect contains
  \(E_1+E_2=2|\ell|+O(1)\);
- in the two sectors with \(C\) temporally between \(A\) and \(B\), both
  defects contain \(E_1+E_2\).

The four one-large-defect sectors carry the logarithmic subgraph boundary.
The two double-large sectors are already oscillatory-improved.  The equal-time
face \(t_A=t_B\) supports the local bubble counterterm.  Together their MSbar
extension is exactly the Fourier-defined \(b_{\mu,\mathbf Q}\), so no sector
or local face is silently dropped.

## The renormalized bubble as a distribution

Differentiating with respect to \(p=|\mathbf Q|\) gives, away from the local
extension,

\[
 {\partial b_{\mu,p}(\tau)\over\partial p}
 =-i e^{-ip|\tau|}.
\]

Consequently its nonlocal singularity has the form

\[
 b_{\mu,p}(\tau)
 =\operatorname{FP}{e^{-ip|\tau|}\over|\tau|}
 +a_{\mu,p}\delta(\tau),
\]

where the full complex Fourier master, including its finite \(+2\), fixes the
local coefficient.  The finite part acts on the induced compact test because
that test is Lipschitz:

\[
 h_R(\tau)-h_R(0)=O(|\tau|).
\]

Thus the apparent \(1/|\tau|\) singularity is removed by the defining local
subtraction.  The sharp switch is also controlled directly by the spectral
form, where every \(F_T\) is entire.

## Spectral convergence and the bridge shell

The exact window bound is

\[
 |F_T(x)|\le\min\left(T,{2\over|x|}\right).
\]

The bubble has only locally integrable logarithmic thresholds at
\(\nu=\pm|\mathbf Q|\).  The bridge is the standard tempered distribution

\[
 {1\over\rho^2-E_K^2+i0}
 =\operatorname{PV}{1\over\rho^2-E_K^2}
 -i\pi\delta(\rho^2-E_K^2).
\]

At large spectral energies the three window factors give:

- \(O(\log|\nu|/\nu^2)\) when \(\rho\) remains bounded;
- \(O(\rho^{-4})\) when \(\nu\) remains bounded;
- \(O(\log r/r^4)\) along the cancellation line
  \(\nu+\rho=O(1)\); and
- \(O(\log r/r^5)\) in generic two-dimensional cones.

These estimates are integrable and uniform on the declared compact packet.
The PV and delta pieces act on smooth finite-window factors.  Therefore the
six roles with \(K_R^2=0\) are finite distributional pairings at every fixed
\(T\); the covariant pole is never evaluated pointwise at their centers.

## Local forest and finite-time RG identity

The scale derivative is especially simple:

\[
 {\partial b_{\mu,\mathbf Q}(t_A-t_B)\over\partial\log\mu}
 =2\delta(t_A-t_B).
\]

It collapses the bubble endpoints and leaves precisely the switched
two-vertex bridge kernel already used in \(T_{4,T}\).  Combining this with

\[
 \sum_{R:C_R=C}W_R=40R_C
\]

gives the finite-time identity

\[
 \boxed{
 {\partial T_{6,\mathrm{bb},T}\over\partial\log\mu}
 ={5\over4\pi^2}T_{4,T}.}
\]

The running of \(\lambda^4T_{4,T}\) supplies the opposite coefficient, so

\[
 {\partial\over\partial\log\mu}
 \left(\lambda^4T_{4,T}+\lambda^6T_{6,\mathrm{bb},T}\right)
 =O(\lambda^8)
\]

in this forest sector.  This is a finite-time normalization theorem, not only
an asymptotic covariant check.

## Selected-source packet bound

At the certified rational center,

\[
 |\mathbf Q_R|^2\ge {32\over625}
\]

for all sixty roles.  The only \(E_K=0\) bridge is the hard all-in/all-out
channel, and all six of its species tensors annihilate
\(u_0=(|000\rangle+|111\rangle)/\sqrt2\).  Every source-surviving role obeys

\[
 E_K^2\ge {7169\over10625}.
\]

After shrinking the packet, write the uniform lower bridge energy as
\(E_{\min}>0\).  Then

\[
 |d_E|\le {1\over2E_{\min}},
\]

the bridge kernel is Lipschitz with constant \(1/2\), and the induced bubble
test satisfies

\[
 |h_R(0)|\le {T^2\over2E_{\min}}.
\]

The finite-part, logarithmic-threshold and bridge-pole estimates are therefore
uniform.  Each \(J_{T,R}\) is locally bounded for fixed \(T>0\).  Once the
common momentum delta is reduced, the finite sixty-tensor sum is a
Hilbert--Schmidt kernel on every sufficiently small compact finite-measure
selected-source packet.

This deliberately does not construct a full-carrier extension through the
zero-spatial hard mode.

## Covariant boundary

The three window factors have the translation-invariant relative-energy
boundary

\[
 \begin{split}
 &F_T(q_A^0-\nu-\rho)F_T(q_B^0+\nu)F_T(q_C^0+\rho)\\
 &\quad\longrightarrow
 F_T(\Omega)(2\pi)^2
 \delta(\nu+q_B^0)\delta(\rho+q_C^0).
 \end{split}
\]

Hence, with common phases restored consistently,

\[
 J_{T,R}
 ={iF_T(\Omega)B_{\overline{\mathrm{MS}}}(Q_R^2)
   \over K_R^2+i0}+R_{T,R},
\]

where \(R_{T,R}\) is defined by the exact finite-window distributional
pairing minus this comparison distribution.  The boundary is understood on
packet space, including at the six bridge shells.  After removing the
declared common bridge phase, it reproduces the phase-stripped covariant
predecessor without discarding the finite transient.

## Common-Born boundary and remaining physics

Every \(W_R\) is fixed by total species complement and the new scalar time
kernel acts only on momentum.  Therefore

\[
 T_{4,T}^{\sharp}T_{6,\mathrm{bb},T}
 +T_{6,\mathrm{bb},T}^{\sharp}T_{4,T}
 =T_{4,T}^{*}T_{6,\mathrm{bb},T}
 +T_{6,\mathrm{bb},T}^{*}T_{4,T}.
\]

Together with the triangle predecessor, the connected finite-time auxiliary
\(T_6\) loop is complete on the selected source packet.  Its common-Born
class is fixed, but its coherent value and sign are not.

Complete \(q_{10}\) still requires the \(y_5\) norm, all source/detector
components of \(y_6\), and vacuum/survival normalization.  Nothing here
proves Eq. (19), a scalar-projector pushforward, gravity/BV--BRST transfer, or
anything LORENTZIAN-CAUSAL.

## Verification receipt

All Python and TeX commands below ran sequentially under
`ulimit -v 500000`.  The repository-wide rail additionally used the sanitized
`PATH=/usr/local/bin:/usr/bin:/bin`.

| Tier | Command or rail | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0/1 | producer `--write --check` | PASS, 41/41 | 0.02 s | 16,472 KiB |
| 1 | independent verifier, including strict schema validation | PASS, 65/65 | 0.06 s | 24,352 KiB |
| 1 | focused adversarial mutation suite | PASS, 65 tests | 0.25 s | 25,208 KiB |
| 2 | five predecessor verifiers | PASS, 52/52, 45/45, 32/32, 24/24 and 52/52 | 1.10 s total | 75,592 KiB maximum |
| 2 | predecessor plus new affected tests | PASS, 211 tests | 8.40 s | 80,272 KiB |
| 0 | Paper V, two `pdflatex` passes | PASS | 0.51 s, 0.53 s | 51,120 KiB maximum |
| 0 | Paper VI, two `pdflatex` passes | PASS | 0.54 s each | 50,972 KiB maximum |
| 2 | Science Forge planning import/fold | PASS, 1,581 nodes; 0 invalid items; 0 malformed events | 5.94 s | 260,612 KiB |
| 3 | full `unittest discover` | **FAIL-CLOSED**, 3,390 tests: 31 failures, 9 skips | 707.635 s (11:48.68 wall) | 391,332 KiB |

The Tier-3 failures are the established historical certificate/hash drift in
older BT families plus the two `test_chain_imports` failures (including its
fifteen outside-reference findings).  Neither the new test module nor any of
the five affected predecessors appears in the thirty-one-failure list.  The
full rail is therefore not called a pass and promotes no repository-wide
freeze.

The advisory Science Forge shadow rail completed in 1.97 s with peak RSS
340,812 KiB.  It inventoried 1,630 certificates and 1,411 verifier files, but
reported the pre-existing Forge 0.0.2/stdlib mismatch, bridge-audit E9118, and
baseline corpus drift.  Advisory exit zero is not counted as certified
success.

The rebuilt Paper V PDF has 81 pages, 761,965 bytes and SHA-256
`583c7aba0709cceab889bff5c72697a4f8711146b196210cecdaa6a7593367de`.
Paper VI has 70 pages, 725,568 bytes and SHA-256
`b492dcba29881c7300766c247475ea669c2dacd9d21e89a3c9d192ed10066fdf`.
The final certificate SHA-256 is
`adbc12c3c45b35a17f1159ab89632a458d1cf8796da371bed80768f2f07d8320`.
There are no undefined references.  The existing overfull-box warnings occur
outside the newly added passages.

CLOSE-OUT: DONE -- the renormalized off-diagonal bubble time distribution,
three-window bridge convolution, six chronological sectors, finite-time
forest identity, bridge-shell pairing, packet bound and covariant boundary
are exact on the selected positive source packet.

EVIDENCE:
reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json
