# Phase 3 axial complete-reconstruction repair

## Result

The omitted Schwarzschild axial Ricci row has been incorporated exactly.  In
the ingoing-EF, axial \(\ell=2\), \(M=1\) conventions, let

\[
C=\frac{\delta R_{v\phi}}{S_2}-P.
\]

After imposing the previously used \(x\phi\) and \(r\phi\) differential
rows, the third row becomes an algebraic constraint.  Direct differentiation
with the exact Ricci-carrier and metric flows gives

\[
C'=-\frac{2}{r}C,
\qquad
\kappa=r^2C=\text{constant}.
\]

Thus the complete reconstruction is the \(\kappa=0\) fibre.  Solving that
constraint for \(H_0\) gives a block-triangular six-state system

\[
(P,P',Q,Q',H_1,F),\qquad F=H_1',
\]

with a four-dimensional Ricci-carrier quotient and a two-dimensional
Einstein kernel:

\[
0\longrightarrow \mathcal E_{\rm ker}^{2}
\longrightarrow \mathcal E_{\rm Bach,ax}^{6}
\longrightarrow \mathcal E_{\rm Ricci}^{4}
\longrightarrow0.
\]

For every solution of the reduced flow, the algebraically reconstructed
\(H_0\) satisfies all three equations

\[
\delta R_{v\phi}=P S_2,
\qquad
\delta R_{r\phi}=Q S_2,
\qquad
\delta R_{x\phi}=c X_2
\]

identically.  An independent `LinearizedBach` rail rederives the three Ricci
rows from the metric perturbation and verifies those identities.

## Endpoint bases

At each endpoint, the four imported carrier columns are lifted by the exact
forced two-state kernel equation.  The two homogeneous kernel columns are
then appended.  This produces six independent columns at the horizon and six
at infinity.

At the horizon, the only forced-lift resonances are:

* the two analytic carrier columns at \(s=0,n=0\);
* the lower singular column at \(s=-2-4i\omega,n=1\).

All three cokernel obstructions vanish exactly.  Every later lift pivot is

\[
(s+n)(s+n+1+4i\omega),
\]

and is nonzero on real \(\omega\in[1/2,3/4]\).  The certificate records exact
carrier leading vectors and canonical \(H_1\) heads.

At infinity, the two complete kernel branches are

\[
(\mu,\sigma)=(0,0),
\qquad
(-2i\omega,1-4i\omega),
\]

with post-indicial pivots \(\mp2i\omega n\).  The four additional columns are
the canonical formal variation-of-constants lifts of the imported
\(XI0,XI1,XI2,XI3\) carrier basis.  The certificate includes exact
machine-readable \((P,Q)\) coefficient heads for all four columns, including
the two lower-power columns whose leading \(P\) coefficient vanishes.
Termwise integration retains any forced polyhomogeneous logarithm rather
than discarding it.

There is no real exceptional frequency in the pilot interval.  The recorded
complex walls include \(\omega=0\), \(\omega=i\), and \(\omega=2i\); the last
is where the transverse polynomial vector itself enters the complete fibre
and the displayed repair normalization changes.

## Phase-2 \(X0\) and legacy \(E0\)

The corrected Phase-2 rate-zero lift has

\[
C_{X0}=\frac{i(\omega-18i)}{2\omega^2}\,r^{-2}.
\]

The transverse polynomial two-row vector

\[
T:\quad H_1=1,
\qquad H_0=-i\omega r+2+\frac2r
\]

has

\[
C_T=3i(\omega-2i)r^{-2}.
\]

Therefore

\[
X0_{\rm complete}=X0_{\rm Phase2}+\alpha T,
\qquad
\alpha=-\frac{\omega-18i}{6\omega^2(\omega-2i)}
\]

lies exactly on \(C=0\).  The old `E0` is \(T/2\), so it is not itself a
complete Einstein solution and that label is superseded.

The Phase-2 finite-pairing interpretation is not preserved automatically.
The repair adds an \(O(r)\) term to \(H_0\) and a constant term to \(H_1\), so
the current must be recalculated on the true complete kernel.  An independent
literal-current audit finds that the oscillatory \(C=0\) Einstein kernel
crosses repaired \(X0\) divergently, with leading terms

\[
\frac{48\pi\alpha_W\omega^3(4\omega+i)}5
e^{-2i\omega r}r^{3-4i\omega}
\]

and the reverse-frequency conjugate counterpart.  Both coefficients are
nonzero on the real pilot interval.  Only the rate-zero kernel shear preserves
the former finite class; unrestricted representative independence fails.
This warning is not promoted here to a flux theorem.

For completeness, the exact rate-zero formal coefficient audit has no
coefficient at \(p\geq-1\) and gives at \(p=-2\):

\[
\begin{aligned}
X|X&=\frac{32i\pi\alpha_W(540-\omega^2)}
{15\omega^3(\omega^2+4)},\\
EI0|X&=-\frac{32i\pi\alpha_W(25\omega+18i)}
{5\omega(\omega+2i)},\\
X|EI0&=-\frac{32i\pi\alpha_W(25\omega-18i)}
{5\omega(\omega-2i)},\\
EI0|EI0&=-\frac{384i\pi\alpha_W\omega}{5}.
\end{aligned}
\]

Here the complete rate-zero kernel has

\[
H_1=1+\frac{3i(\omega-2i)}{2\omega^2}r^{-2}+\cdots,
\qquad
H_0=-i\omega r+2+\frac{\omega+6i}{2\omega}r^{-1}+\cdots,
\]

and decomposes as \(EI0=T-3i(\omega-2i)R/\omega^2\).  This table is an
asymptotic formal audit, not a global finite-flux phase space.

## Exact scope

Established:

* the complete three-row local reconstruction;
* conservation of \(\kappa=r^2C\);
* exact six-dimensional solution-space splitting;
* six formal horizon and six formal infinity columns;
* compatible horizon lift resonances;
* the all-row \(X0\) repair and supersession of legacy `E0`.

Not established:

* convergence of the endpoint series;
* horizon-to-infinity matching or a connection matrix;
* a finite-flux phase space or scattering channel;
* stability, QNMs, CPT positivity, particles, or unitarity;
* the polar counterpart.

## Verification

```text
PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_complete_reconstruction_repair/produce.py --check
PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_complete_reconstruction_repair/verify.py
PYTHONPATH=black_hole_programme python3 black_hole_programme/phase3/axial_complete_reconstruction_repair/mutations.py
python3 -m unittest black_hole_programme.phase3.axial_complete_reconstruction_repair.tests.test_repair
python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-axial-complete-reconstruction-repair-fragment-v1.json
```
