# BT Abel--Naimark asymptotic dilation

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Abel-regularized large-time evolution of the certified formal BT soft
Hamiltonian generates exactly the logistic cutoff profile of the existing
detector-resolution theorem.  Thus the logarithmic resolution translation is
not merely cutoff bookkeeping: inverse Abel time moves the detector profile.
The same calculation proves that the ordinary coherent wave columns still do
not converge strongly.  A canonical Naimark carrier realizes the missing
positive orthogonal increments, but it does not identify the public
field-map generator with the physical S-matrix splitting operator.

## Abel time becomes resolution scale

The certified off-resonant formal flow has leading soft Hamiltonian

\[
 H_{\rm as}^{(1)}(t)
 =d\bigl(e^{-idt}D+e^{idt}D^\sharp\bigr).
\]

For \(\epsilon>0\), define its Abel integral by

\[
 K_\epsilon=-i\int_0^\infty
 e^{-\epsilon t}H_{\rm as}^{(1)}(t)\,dt.
\]

The coefficients of \(D\) and \(D^\sharp\) are

\[
 A_\epsilon(d)=\frac{-id}{\epsilon+id},\qquad
 B_\epsilon(d)=\frac{-id}{\epsilon-id}
              =-\overline{A_\epsilon(d)}.
\]

Hence \(K_\epsilon^\sharp=-K_\epsilon\), and

\[
 |A_\epsilon(d)|^2=\frac{d^2}{\epsilon^2+d^2}.
\]

On a nonzero physical soft ray \(d=\alpha r\), introduce
\(y=-\log r\), \(T=1/\epsilon\), and

\[
 R=\log(\alpha/\epsilon)=\log(\alpha T).
\]

Then the norm profile is exactly

\[
 q_R(y)=\frac{1}{1+e^{2(y-R)}}.
\]

Increasing inverse Abel time by a factor \(c\) translates \(R\) by
\(\log c\).  On a finite physical soft chart \(y\geq y_0\), its cumulative
norm is

\[
 I_R=\frac12\log\bigl(1+e^{2(R-y_0)}\bigr),
\]

and therefore

\[
 I_{R+\log c}-I_R\longrightarrow\log c.
\]

The certificate records exact rational fixtures for the Abel coefficients and
an explicit decreasing upper bound on the finite-chart boundary correction.

## The ordinary strong limit still fails

The coherent amplitude profile is

\[
 A_R(y)=\frac{-i e^{R-y}}{1+i e^{R-y}}.
\]

Two columns separated by a fixed scale ratio \(c=e^a>1\) obey

\[
 \lim_{R\to\infty}
 \int |A_{R+a}(y)-A_R(y)|^2dy
 =a\tanh(a/2)
 =\log(c)\frac{c-1}{c+1}.
\]

This is positive, so the Abel columns are not Cauchy.  It is also strictly
smaller than the positive detector response \(\log c\).  Consequently the
detector shell cannot be interpreted as the literal difference of two
coherent time columns.  Abel damping derives the moving profile, but does not
remove the previously certified strong-Møller obstruction.

## Canonical orthogonal-increment carrier

Differentiate the logistic profile with respect to its resolution origin:

\[
 p_s(y)=\partial_s q_s(y)=\frac12\operatorname{sech}^2(y-s),
 \qquad \int_{\mathbb R}p_s(y)\,dy=1.
\]

On

\[
 \mathcal K_N=L^2(\mathbb R_s\mathbin\times\mathbb R_y,ds\,dy)
 \otimes\mathbb C^3,
\]

define the purified shell

\[
 \Xi_{R,a}(s,y)=
 \mathbf1_{[R,R+a]}(s)\sqrt{p_s(y)/a}.
\]

It has unit norm.  Shells supported on disjoint \(s\)-intervals are
orthogonal, joint translation \((s,y)\mapsto(s+b,y+b)\) is exact, and the
observable \(y\)-marginal is

\[
 \int_R^{R+a}\frac{p_s(y)}a\,ds
 =\frac{q_{R+a}(y)-q_R(y)}a.
\]

This is a canonical probability purification of the detector shell.  The
extra \(s\) coordinate records resolution/noise history.  It is not a new
spacetime dimension.

## Physical leading-log response and object boundary

The independently certified physical five-point process supplies Gram density
\(1/48\) per unordered final pair.  For three orthogonal channels,

\[
 G_{R,a}h=\sqrt{a/48}\sum_{i=1}^3\Xi_{R,a,i},
 \qquad \|G_{R,a}h\|^2=\frac a{16}.
\]

Physical-shell pseudo-unitarity forces hard survival response \(-a/16\), so
the inclusive leading-log response is zero.  Multiplication by the Born
coefficient \(3/32\) gives the absolute pair \(+3/512,-3/512\) in the usual
common units.

Two inputs remain deliberately separate:

- The logistic profile comes from Abel integration of the certified formal
  off-resonant \(R_t\)/field-map Hamiltonian.
- The coefficient \(1/48\) comes from the physical five-point S-matrix
  process.

What has been identified is their common detector-resolution automorphism and
positive profile.  What has not been identified is the operator: the public
number-lowering \(D\) has not been proved to have the physical splitting
operator's Krein species and phase.

## Boundary and next gate

The result constructs a leading-log reduced-mode probability dilation with a
genuine time-to-resolution mechanism.  It does not construct complete
incoming and outgoing degenerate sectors, a full dressed Møller operator, a
local LSZ/AQFT affiliation, the finite NLO constant, multiple-emission
composition, beyond-tree positivity, Eq. (19), a gravitational/BRST lift, or
anything `LORENTZIAN-CAUSAL`.

The next decisive calculation is amplitude-level collinear factorization of
the complete physical BT five-point process, including Krein species and
phase, followed by comparison with the Abel-regularized off-resonant \(D\)
after zero-mode completion.  Equality would identify this dilation with the
physical asymptotic Hamiltonian on the outgoing cylinder.  A mismatch would
be the first exact operator obstruction.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_abel_naimark_asymptotic_dilation.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_abel_naimark_asymptotic_dilation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_abel_naimark_asymptotic_dilation
```

Tier 2 is unnecessary because the four imported mathematical certificates are
unchanged and content-addressed; no shared operator, source schema, or direct
consumer changed.  Tier 3 is unnecessary because this is not a freeze,
release, shared-core change, or promotion to a full S-matrix, finite NLO,
Eq. (19), or `LORENTZIAN-CAUSAL` theorem.  Unrun tiers are not passes.

Final scoped receipt, 2026-08-11; every Python and TeX process ran
sequentially under the 500 MB virtual-memory cap:

| Tier | Command | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0 | compile three Python files; parse work item, event, certificate, and schema | PASS | 0.22 s | 16,088 KB |
| 1 producer | exact Abel/profile/dilation producer | PASS, 25/25 | 0.05 s | 20,648 KB |
| 1 independent | schema, source, coefficient, obstruction, and marginal verifier | PASS, 17/17 | 0.13 s | 30,292 KB |
| 1 mutations | ten tests, including eight decisive scientific mutations | PASS | 1.12 s | 30,496 KB |
| papers | Paper V, final second pass | PASS | 0.42 s | 50,692 KB |
| papers | Paper VI, final second pass | PASS; no warning or overfull box | 0.43 s | 50,508 KB |

PDF text extraction independently found the inverse-Abel resolution
translation, coherent non-Cauchy obstruction, auxiliary-coordinate boundary,
and non-identification of the public \(R_t\) and physical splitting operators.
The new Paper V passage introduces no overfull box; that paper retains four
unrelated pre-existing boxes and its pre-existing PDF-string warnings.  Paper
VI has no overfull box or warning.  A scoped added-line audit finds no
changelog phrasing in either manuscript.

The Science Forge coordinator appended terminal event
96685339351e729b.  The work-item source remains immutable and the event is a
separate content-addressed transition.
