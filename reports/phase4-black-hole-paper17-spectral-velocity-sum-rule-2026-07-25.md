# Paper 17 spectral-velocity sum rule and contact-order law

## Result

Paper 17 now identifies the quotient of the Bach connection shear by the
scalar Evans function as a meromorphic spectral-velocity generating
function:

\[
\mathscr S(\omega)=\frac{b_{\rm B}(\omega)}{a(\omega,0)}
=\frac{i\omega}{2}\partial_m\log a(\omega,0)+h(\omega).
\]

On an analytic Evans domain, every simple nonzero QNM is a simple pole of
\(\mathscr S\), with

\[
\operatorname*{Res}_{\omega=\omega_n}\mathscr S(\omega)
=\kappa_n
=-\frac{i\omega_n}{2}\omega_n'(0).
\]

For a positively oriented contour containing only simple QNMs and no
boundary zero,

\[
\frac{1}{2\pi i}\oint_\Gamma\frac{b_{\rm B}}a\,d\omega
=\sum_{\omega_n\in\operatorname{int}\Gamma}\kappa_n,
\]

and therefore

\[
\sum_{\omega_n\in\operatorname{int}\Gamma}\omega_n\omega_n'(0)
=2i\,\frac{1}{2\pi i}\oint_\Gamma\frac{b_{\rm B}}a\,d\omega.
\]

The analytic endpoint-normalization term \(h\) drops out of the contour
integral.  For a reflection-symmetric contour, the selector sum is purely
imaginary.  This is an exact audit identity, not a validated multi-QNM
contour computation.

## Complete simple-QNM dichotomy

At every simple nonzero scalar QNM, with the spin-one factor a local unit,

\[
\omega_n'(0)\ne0
\Longleftrightarrow b_{\rm B}(\omega_n)\ne0
\Longleftrightarrow \operatorname{Smith}(T)=(0,0,2),
\]

whereas

\[
\omega_n'(0)=0
\Longleftrightarrow b_{\rm B}(\omega_n)=0
\Longleftrightarrow \operatorname{Smith}(T)=(0,1,1).
\]

If the velocity vanishes, the double coefficient vanishes but the simple
coefficient can remain:

\[
C_{-2}=0,\qquad C_{-1}=-\dot P_n.
\]

This distinguishes a semisimple shape-sensitive first jet
\((\dot P_n\ne0)\) from a first-jet-invisible resonance
\((\dot P_n=0)\).  The latter projected first derivative is holomorphic at
the QNM.

The critical determinant \(a^2\) cannot distinguish the two Smith
branches.  The shear, equivalently the transverse mass derivative, is the
missing unfolding datum.

## Contact-order pole hierarchy

Suppose the first nonzero mass derivative of a simple QNM occurs at order
\(q\):

\[
\omega_n(m)=\omega_n+\frac{\nu_{n,q}}{q!}m^q+O(m^{q+1}).
\]

For

\[
J_p=\frac{(-1)^p}{p!}\partial_m^pR_m\big|_{m=0},
\]

Paper 17 now proves

\[
\operatorname{poleord}_{\omega_n}J_p
\le\left\lfloor\frac pq\right\rfloor+1.
\]

For \(p<q\), resonance motion produces no pole enhancement, although
projector derivatives may retain a simple pole.  At the first visible jet,

\[
\operatorname{Coeff}_{(\omega-\omega_n)^{-2}}J_q
=\frac{(-1)^q}{q!}\nu_{n,q}P_n.
\]

For \(p=kq\), the top coefficient is

\[
(-1)^{kq}\left(\frac{\nu_{n,q}}{q!}\right)^kP_n.
\]

The previous \(p+1\) higher-jet law is retained as the transverse
specialization \(q=1\).  Tangential criticality \(q=2\) first produces a
double pole in the second jet, not automatically a triple pole.

## Independent verification

The verifier independently checks:

- the simple-zero residue and its sign;
- the weighted selector/velocity factor \(2i\);
- the reflection-pair reality property;
- the moving-pole decomposition when the first velocity vanishes;
- the contact-order bound by exact coefficient extraction for
  \(1\le q\le4\) and \(0\le p\le12\);
- the first-visible and repeated-multiple factorial coefficients;
- the declared Smith dichotomy and fail-closed claim boundary.

Seven new mutation tests reject changes to the residue sign, weighted-sum
factor, semisimple Smith branch, contact-order bound, first-visible
factorial, and the two forbidden numerical promotions.

## Claim boundary

Established:

- exact spectral-velocity residue theorem;
- exact multi-QNM contour sum rule on analytic simple-zero domains;
- exact reflection-symmetry audit;
- exact simple-QNM defective/semisimple first-jet dichotomy;
- exact shape-sensitive versus first-jet-invisible refinement;
- exact contact-order pole bound and leading coefficients;
- exact transverse \(q=1\) higher-jet specialization.

Not established:

- a validated numerical multi-QNM selector contour;
- nonvanishing of every individual selector in a contour;
- an overtone EP2 tower;
- a global retarded inverse-Laplace deformation;
- a global ringdown, stability, or quantum statement.

CLOSE-OUT: DONE — the Bach shear is now an exact spectral-flow generator,
and the higher-jet pole hierarchy is classified by spectral contact order.

EVIDENCE: `reports/PAPER17_SPECTRAL_VELOCITY_SUM_RULE_TIER_RECEIPT.json`
