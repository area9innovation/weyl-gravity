# BT extended squeeze carrier: a vector repair without a Born trace

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The ordinary Fock--Krein obstruction can be bypassed at the level of the
vacuum vector, but only by changing the representation. The full Appendix-C
pair exponential imposes two conditions that were not visible from its first
two-particle sector alone: every individual pair amplitude must have modulus
less than one, and the squared amplitudes must be summable. Every positive
topology uniformly equivalent to the ordinary BT topology fails the first
condition at sufficiently small momentum.

An explicit infrared-weighted topology satisfies both conditions per unit
volume. Its inverse metric is unbounded at zero momentum, so it is an
inequivalent completion, not a different bounded fundamental symmetry on the
same Krein space. Moreover, it only constructs the image vacuum. It does not
construct the cross-Krein operator map or the positive cyclic generalized-Born
trace required by Eq. (19).

## 1. The full exponential adds a contraction condition

For one unordered pair $\{\mathbf p,-\mathbf p\}$, let

\[
 A_{\mathbf p}^{*}
 =\frac{c_{\Upsilon,\mathbf p}^{\dagger}}{\sqrt{\rho(\mathbf p)}}
\]

be the normalized positive creator. Combining the ordered $\mathbf p$ and
$-\mathbf p$ terms in Appendix C gives

\[
 z(\mathbf p)=\frac{\rho(\mathbf p)}{4|\mathbf p|^2}.
\]

The pair contribution to the vacuum is therefore

\[
 e^{zA_{\mathbf p}^{*}A_{-\mathbf p}^{*}}|0\rangle
 =\sum_{n\ge0}z^n|n_{\mathbf p},n_{-\mathbf p}\rangle.
\]

The $1/n!$ from the exponential cancels the $n!$ produced by the two
creation strings. Consequently

\[
 \left\|e^{zA_{\mathbf p}^{*}A_{-\mathbf p}^{*}}|0\rangle\right\|^2
 =\sum_{n\ge0}|z|^{2n}
 =\frac1{1-|z|^2}
\]

if and only if $|z|<1$. The full box state factorizes over unordered pairs:

\[
 \|\Psi\|^2=\prod_{\{\mathbf p,-\mathbf p\}}
 (1-|z(\mathbf p)|^2)^{-1}.
\]

It exists as a Fock vector only when

\[
 \sup_{\mathbf p}|z(\mathbf p)|<1,
 \qquad
 \sum_{\{\mathbf p,-\mathbf p\}}|z(\mathbf p)|^2<\infty.
\]

The second condition reproduces the previous first-sector summability test.
The first, modewise contraction condition is stronger in the infrared.

## 2. Why every equivalent BT topology fails

Uniform equivalence means $0<m\le\rho(\mathbf p)\le M<\infty$. In a box,
$p_{\min}=2\pi/L$, hence

\[
 |z(p_{\min})|
 \ge\frac{mL^2}{16\pi^2}.
\]

For $L\ge4\pi/\sqrt m$, at least one pair has $|z|\ge1$, and its geometric
norm series already diverges. Thus the full exponential fails mode by mode
before the massless thermodynamic limit is reached. At fixed finite box it is
always defined order by order, but it is a genuine vector only when every box
mode also satisfies the contraction bound. This sharpens the earlier report's
finite-volume wording.

For a power weight $\rho(p)\sim p^\alpha$, square summability requires only
$\alpha>1/2$, whereas modewise contraction requires

\[
 \alpha>2,\qquad\hbox{or}\qquad
 \alpha=2\ \hbox{with limiting coefficient below four}.
\]

Any such weight tends to zero and is inequivalent to the ordinary topology.

## 3. An explicit weighted vacuum carrier

Choose $\mu>0$, $0<\gamma<1$, and

\[
 \rho_\mu(p)=
 \frac{4\gamma\mu^2p^2}{p^2+\mu^2}.
\]

Then

\[
 z_\mu(p)=\frac{\gamma\mu^2}{p^2+\mu^2},
 \qquad \sup_p|z_\mu(p)|=\gamma<1.
\]

It behaves as $p^2$ in the infrared but approaches a constant in the
ultraviolet. It therefore fixes the low-momentum contraction without creating
a new ultraviolet divergence. The unordered square-sum density is

\[
 \frac12\int\frac{d^3p}{(2\pi)^3}|z_\mu(p)|^2
 =\frac{\gamma^2\mu^3}{16\pi},
\]

using

\[
 \int_0^\infty\frac{x^2\,dx}{(1+x^2)^2}=\frac\pi4.
\]

Since $x\le-\log(1-x)\le x/(1-\gamma^2)$ for
$0\le x\le\gamma^2$, the full logarithmic norm density is finite and bounded
by

\[
 \frac{\gamma^2\mu^3}{16\pi}
 \le\frac1V\log\|\Psi\|^2
 \le\frac{\gamma^2\mu^3}{16\pi(1-\gamma^2)}.
\]

This is the constructive progress: the pair-product vacuum exists in each
finite box and has a finite infrared norm density.

But

\[
 \rho_\mu(p)^{-1}\sim p^{-2}.
\]

The associated $\kappa_{\rho_\mu}$ is unbounded relative to the ordinary BT
completion. The total logarithmic norm remains extensive in $V$, and the
normalized overlap with the ordinary vacuum decays exponentially to zero.
The thermodynamic carrier is therefore an inequivalent infinite-product or
algebraic representation, not a vector limit in the original Fock space.

## 4. Why a standard extended Bogoliubov theorem does not finish the job

After Hilbertization, normalized cross modes can be chosen as

\[
 A=\sqrt\rho\,c_\Omega,\qquad
 A^*=c_\Upsilon^\dagger/\sqrt\rho,
\]

\[
 D=c_\Upsilon/\sqrt\rho,\qquad
 D^*=\sqrt\rho\,c_\Omega^\dagger.
\]

The BT generator is

\[
 Q=\sum_{\{\mathbf p,-\mathbf p\}}z(p)
 \bigl(A_{\mathbf p}^*A_{-\mathbf p}^*
       -D_{\mathbf p}D_{-\mathbf p}\bigr).
\]

Its positive Hilbert adjoint is not $-Q$. Correspondingly, the raw shear
$A\mapsto A+zA^*$ has $u=1,v=z$ and

\[
 u^2-v^2=1-z^2\ne1.
\]

For the exact fixture $z=1/2$, the left side is $3/4$. A standard positive
Bogoliubov transformation with the same ratio $v/u=z$ would instead require

\[
 u^2=\frac1{1-z^2}=\frac43,\qquad
 v^2=\frac{z^2}{1-z^2}=\frac13.
\]

That normalization changes the displayed BT oscillator map. It would require
Eqs. (16)--(21), including the projector pushforward, to be rederived.

Lill's generic construction demonstrates that positive-Hilbert bosonic
Bogoliubov transformations can be implemented on an algebraic extension even
without the Shale--Stinespring condition. Its hypotheses require the positive
bosonic Bogoliubov relations on a suitable domain. Its generic extended state
space is an algebraic quotient supporting formal operator action; it does not
by itself supply a positive Hilbert inner product, the BT cross-Krein analogue,
or BT's cyclic generalized-Born trace. It is therefore an architecture source,
not a theorem that can be imported verbatim here.

## 5. Disposition

Established exactly:

- the full pair-exponential convergence conditions;
- modewise failure of every uniformly equivalent ordinary BT topology;
- the stronger $\alpha\ge2$ infrared threshold;
- an explicit inequivalent weight with contraction below one and finite norm
  density;
- the unbounded inverse metric and vanishing thermodynamic vacuum overlap;
- failure of the raw BT shear to satisfy the positive-Hilbert Bogoliubov
  relation;
- the exact boundary of existing extended-implementation theorems.

Not established:

- the full BT operator map on the weighted carrier;
- a positive cyclic generalized-Born trace there;
- Eq. (19), the physical $1/48$, or a complete NLO probability;
- a gravitational/BRST lift or anything `LORENTZIAN-CAUSAL`.

The carrier trilemma is now explicit:

1. keep the ordinary BT topology and lose the full vacuum vector;
2. use the weighted topology and change representation;
3. use a formal extended operator space and still supply the missing physical
   pairing and trace.

The next gate is a genuine architecture choice: construct a cross-Krein
extended implementer and cyclic weight on the weighted thermodynamic sector,
or replace the BT shear by its positive-normalized map and rederive the claimed
embedding.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_extended_squeeze_carrier.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_extended_squeeze_carrier.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_extended_squeeze_carrier
```

## Verification receipt (2026-08-11)

All scoped commands ran sequentially with `ulimit -v 500000`.

- Python parse/compile: PASS, 0.05 s, 15,980 KB peak RSS.
- Exact producer replay: PASS 26/26, 0.04 s, 20,644 KB peak RSS.
- Method-distinct schema, factorial-series, geometric-norm, contraction,
  power-threshold, weighted-density, adjoint, import-boundary, provenance, and
  claim verifier: PASS 14/14, 0.11 s, 30,244 KB peak RSS.
- Producer, verifier, and six decisive mutations: PASS 8/8, 1.62 s,
  30,384 KB peak RSS. Mutations changed the pair amplitude, contraction
  threshold, weighted density, positive Bogoliubov relation, theorem-import
  boundary, and trace claim; every mutation was rejected.
- Content-addressed affected chain: inclusive-radical PASS 12/12 in 0.44 s
  (30,360 KB), fixed-vacuum oscillatory PASS 4/4 in 0.31 s (29,868 KB),
  soft-charge flow PASS 7/7 in 0.90 s (30,552 KB), zero-mode trilemma PASS 7/7
  in 1.10 s (30,348 KB), and corrected ordinary squeeze audit PASS 8/8 in
  1.41 s (30,416 KB).
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each. Paper V
  took 0.49/0.48 s; the final Paper VI passes took 0.49/0.52 s. Peak RSS was
  below 51 MB. The first two Paper VI attempts failed on a missing math
  delimiter in the new sentence; that edit defect was corrected and is not
  counted as a pass. PDF text witnesses found the full-exponential,
  infrared-weight, inequivalent-carrier, positive-Hilbert import-boundary, and
  missing cyclic-trace statements.
- The new schema, certificate, work item, and append-only event parsed as JSON.
  The event's FNV-1a id reproduced exactly. The manual event-v0 fallback is
  used because the coordinator's Go startup is already certified to exceed the
  mandatory cap; no coordinator pass is claimed.
- The advisory Science Forge shadow rail was not rerun. Its immediately prior
  same-session invocation aborted two read-only corpus-index helpers and then
  stalled until interrupted; repeating that failed advisory path is not a
  scoped verification criterion and would not promote this certificate.

Tier 2 stopped at the content-addressed affected chain above. Tier 3 was not
run because this is a `CLASSIFIED` reduced-mode carrier result, not a freeze,
release, shared-core change, or lifecycle theorem promotion.
