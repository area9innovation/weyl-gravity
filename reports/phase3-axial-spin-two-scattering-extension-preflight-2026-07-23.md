# Axial spin-two scattering-extension coefficient preflight

## Disposition

`CLASSIFIED — METHOD_SHORTFALL`

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The certified triangular filtration does determine the local repeated-factor
extension exactly.  In the metric/carrier Regge--Wheeler companion frames,

\[
\partial_r
\binom{x_{\rm metric}}{x_{\rm carrier}}
=
\begin{pmatrix}
A_{\rm RW}&\mathcal E_{\rm RW}\\
0&A_{\rm RW}
\end{pmatrix}
\binom{x_{\rm metric}}{x_{\rm carrier}},
\qquad
\mathcal E_{\rm RW}=U_{\rm metric}\,S\,J_{\rm carrier}.
\]

The machine certificate prints the exact rational rank-one matrix
`\mathcal E_RW`.  It is not a pointwise scalar multiple of
`\partial_\omega A_RW`.

There is also an exact negative test for a global rational gauge.  If

\[
\mathcal E_{\rm RW}
=q(\omega)\partial_\omega A_{\rm RW}
+B'+BA_{\rm RW}-A_{\rm RW}B
\]

with rational `B`, taking traces makes the rightmost three terms
`(\operatorname{tr}B)'`.  A rational derivative has zero residues, but the
residue of
`\operatorname{tr}(\mathcal E_{\rm RW}
-q\partial_\omega A_{\rm RW})` at `r=2` is exactly `4iq`.  Hence any such
rational identity forces `q=0`.  This does not cover logarithmic
spectral-phase derivatives in endpoint-analytic gauges.

## The invariant germ class

At a simple damped spin-two zero `omega_star`, let `O` be the analytic-germ
DVR and `a=A_in,2`.  Filtration-preserving analytic equivalences reduce the
repeated block to

\[
\begin{pmatrix}a&c\\0&a\end{pmatrix},
\qquad c\longmapsto u c+a d .
\]

Thus the invariant is

\[
[c]\in O/(A_{{\rm in},2}),
\]

defined up to multiplication by a unit.  This is the class that selects the
local Smith valuations.

The proposed congruence

\[
c\equiv q A_{{\rm in},2}'\pmod{A_{{\rm in},2}}
\]

has an important algebraic boundary: at a simple zero,
`[A_in,2']` is a unit in the quotient.  Therefore an unspecified `q` always
exists and is uniquely

\[
[q]=[c]\,[A_{{\rm in},2}']^{-1}.
\]

Existence of `q` is consequently tautological.  The nontrivial questions are
whether a separately prescribed structural `q` has this class and whether
`[q]`, equivalently `[c]`, is nonzero.  Neither is decided by the available
Jost data.

## Minimal successor input

The repository currently supplies the exact short-range potential, symbolic
incoming/outgoing amplitudes, real-frequency Wronskian identity, and rational
endpoint factor frames.  It does not supply a certified complex QNM germ.

A decisive computation minimally requires:

1. a certified `omega_star` in `Im(omega)>0` with
   `A_in,2(omega_star)=0` and `A_in,2'(omega_star)!=0`;
2. horizon-normalized QNM and compatible adjoint-QNM germs holomorphic
   through `omega_star`, in patches resolving every Frobenius frame event;
3. a convergent contour, complex-scaled, or explicitly renormalized pairing
   \(\Gamma_*=\langle\psi_*^{\rm adj},
   \mathcal E_{\rm RW}(\omega_*)\psi_*\rangle\);
4. an exact normalization identity relating `Gamma_star` to `c(omega_star)`
   and to `A_in,2'(omega_star)`.

Without these data, no closed symbolic `c`, nonzero `[q]`, or Smith case is
certified.  The convention remains `exp(+I*omega*t)`, so the damped half-plane
is `Im(omega)>0`.

This result does not establish a QNM location, time-domain stability, CPT
positivity, particles, unitarity, or a `LORENTZIAN-CAUSAL` quantum theorem.

Machine receipts:

- `black_hole_programme/phase3/axial_spin_two_scattering_extension_preflight/certificate.json`
- `black_hole_programme/phase3/axial_spin_two_scattering_extension_preflight/receipt.json`
- `black_hole_programme/phase3/axial_spin_two_scattering_extension_preflight/verify.py`

EVIDENCE: black_hole_programme/phase3/axial_spin_two_scattering_extension_preflight/certificate.json
MISSING-DEP: certified damped spin-two QNM and adjoint germs together with a convergent Fredholm pairing that computes the invariant extension class
CLOSE-OUT: SHORTFALL — the exact local extension and rational-gauge obstruction are certified, but the scattering class and local Smith type remain undefined without the missing analytic germs.
