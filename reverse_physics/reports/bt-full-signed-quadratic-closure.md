# BT full signed quadratic closure

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The public composite map and the complete leading Appendix-C inverse determine
more than the resonant two-annihilator slice.  Once every opposite-sign
oscillatory inverse image is included, the old cubic endpoint rows cancel
exactly.  The completed quadratic oscillator map is canonical, time
independent, and endpoint regular on finite nonendpoint modes.

This gives the first positive piece of Eq. (19): on the covariant zero-mode
carrier, the finite-mode quadratic pushforward satisfies the decomposition
through order \(\lambda\), with a neutral correction and
\(Q_1=0\).  It does not prove the continuum or all-order statement.

The candidate \(1/48\) logarithm is not present in this completed public-data
kernel.  A nonzero physical coefficient would have to enter through the
remaining squeezed-vacuum/dynamical-zero-mode projector trace or through data
not contained in the public map.

## 1. The missing inverse images

Use sign \(s=+1\) for an annihilator and \(s=-1\) for a creator.  The complete
leading inverse of Appendix C gives one preimage for a target
\(b_\Omega(s,p)\),

\[
 a_2(s,p)\supset 4e^2 b_\Omega(s,p),
\]

but three preimages for a target \(b_\Upsilon(s,p)\):

\[
 a_1(s,p)\supset b_\Upsilon(s,p),
\]

\[
 a_2(s,p)\supset-2ise\,t\,b_\Upsilon(s,p),
\]

\[
 a_2(-s,-p)\supset-e^{-2iset}b_\Upsilon(s,p).
\]

The resonant calculation retained the first two and omitted the third.  The
third preimage is not itself resonant in the source \(a\) variables.  If its
signed source energy is \(S\) and the target energy is \(E\), symplectic
extraction supplies

\[
 e^{i(E-S)t}.
\]

For every inverse preimage,

\[
 (\hbox{target signs}-\hbox{source signs})
 +(\hbox{inverse phase exponents})=(0,0).
\]

Thus the off-resonant phase cancels the Appendix-C oscillatory phase.  The
opposite-sign preimage contributes to the same time-independent target
coefficient and cannot be discarded before the sum.

The certificate enumerates 128 exact parent/preimage contributions across the
four target-sign sectors.  Every phase closes separately.

## 2. Exact cancellation of the endpoint rows

For target signs \((s_1,s_2)\), set

\[
 E=s_1e_1+s_2e_2.
\]

After summing all inverse images, the complete kernel is

\[
 \delta b_\Omega
 =\frac{E}{2e_1e_2}\,b_\Omega^{(s_1)}b_\Omega^{(s_2)},
\]

\[
 \delta b_\Upsilon
 =-\frac{s_2}{2e_1}\,
 b_\Omega^{(s_1)}b_\Upsilon^{(s_2)}
 -\frac{s_1}{2e_2}\,
 b_\Upsilon^{(s_1)}b_\Omega^{(s_2)}.
\]

Every other species row vanishes.  In particular, the three rows responsible
for the resonant-only cubic endpoint Gram become zero:

\[
 \delta b_\Omega[\Omega,\Upsilon]=0,
 \qquad
 \delta b_\Omega[\Upsilon,\Omega]=0,
 \qquad
 \delta b_\Upsilon[\Upsilon,\Upsilon]=0.
\]

For example, the old constant
\(1/(8e_2^3)\) in
\(\delta b_\Omega[\Omega,\Upsilon]\) is canceled by the opposite-sign
\(a_2\) preimage.  Its secular terms cancel between the same-sign
\(a_1\) and \(a_2\) preimages.  The nine contributions to the old
\(\Upsilon\Upsilon\) row cancel in the same way.

No \(t\) or \(t^2\) coefficient survives.

## 3. Canonicality is restored

The resonant-only slice did not contain enough information to test the cubic
canonical Ward identity.  The completed signed kernel does.  For
\(P=x+y\), let \(F\) denote the annihilation--annihilation row and \(G\) the
mixed row.  Exact cross-CCR preservation is

\[
\begin{split}
0={}&x\bigl(
F_A{}_{\bar D C}(x,y)+F_A{}_{C\bar D}(y,x)
\bigr)\\
&+P\bigl(
G_D{}_{\bar A C}(P,y)+G_D{}_{C\bar A}(y,P)
\bigr).
\end{split}
\]

The formula holds identically channel by channel.  The independent verifier
also evaluates all eight species triples on six exact rational energy pairs,
for 48 zero-defect rows.  Therefore the annihilation--annihilation and mixed
sectors are the two commutator faces of one anti-Krein cubic generator; the
opposite-sign terms are not optional additions.

## 4. The complete parent Gram

Contracting daughter slots with the BT off-diagonal metric gives

\[
 G_{\Omega\Omega}=0,
 \qquad
 G_{\Omega\Upsilon}=G_{\Upsilon\Omega}=0,
 \qquad
 G_{\Upsilon\Upsilon}=2s_1s_2.
\]

The parent inverse metric is off diagonal.  Hence the parent-raised trace
contains only

\[
 G_{\Omega\Upsilon}+G_{\Upsilon\Omega}=0.
\]

There is no \(dr/r\) distribution, no endpoint normalization constant, and no
soft trace-ideal growth in the completed quadratic parent trace.  Applying the
previous normalization ledger to the exact zero residue gives

\[
 \Delta P_{\mathrm{pair}}^{\mathrm{quadratic}}=0.
\]

The earlier \(1/48\) was a correct conditional normalization of the
resonant-only cross residue.  It is not the coefficient of the completed
signed quadratic map.  Likewise, the finite logarithmic-cell projector theorem
remains an exact conditional matrix theorem, but its choice
\(a^2=1/48\) is not instantiated by this completed kernel.

## 5. Eq. (19) through order lambda

The surviving annihilation--annihilation rows have the unique orbit power
\(Z^{-1}\).  Including it makes each cubic generator component neutral.  The
covariantly completed squeeze generator is neutral as well.

For any finite-mode neutral projector \(P_0\), write the inverse pushforward as

\[
 P(\lambda)=P_0+\lambda[K,P_0]+O(\lambda^2).
\]

Since

\[
 q(K)=q(P_0)=0,
\]

the first correction is neutral.  Therefore, on this declared sector,

\[
 R_tP_0R_t^\dagger
 =P_{\mathrm{neutral}}+Q_{\mathrm{negative}}+O(\lambda^2),
\]

with

\[
 P_{\mathrm{neutral}}=P_0+\lambda[K,P_0],
 \qquad Q_{\mathrm{negative}}=0.
\]

This proves the Eq. (19) form through order \(\lambda\) for the finite-mode,
zero-mode-completed quadratic carrier.  It also shows why the fixed-vacuum
negative-radical argument cannot be used for this completion: the actual
completed generator is neutral.

## 6. What remains physical

Established exactly:

- the complete public-data signed quadratic kernel at order \(\lambda\);
- cancellation of all off-resonant and inverse oscillatory phases;
- cancellation of the resonant-only cubic endpoint rows;
- the order-\(\lambda\) cross-CCR Ward identities;
- zero parent-raised quadratic soft logarithm;
- the finite-mode Eq. (19) decomposition through order \(\lambda\), with
  \(Q_1=0\).

Not established:

- the continuum/all-order Eq. (19) theorem;
- the squeezed-vacuum contribution to the transported detector projector on
  the zero-mode trace domain;
- the full dynamical \(p=0\) module;
- the physical replacement of \(1/48\) by zero;
- a complete NLO probability, gravitational/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

The next calculation is now unique within the public data: compute the
zero-mode-completed squeezed-vacuum contribution to the same finite detector
projector and semifinite trace.  Finite-core cyclicity suggests it cannot
restore a nonzero trace, but that must be checked on the actual local
thermodynamic domain before a physical zero is claimed.

## 7. Verification receipt

All scientific commands are run sequentially under a 500,000 KB virtual-memory
cap.

Tier 0 passed:

- `python3 -m py_compile reverse_physics/bt_full_signed_quadratic_closure.py reverse_physics/verify_bt_full_signed_quadratic_closure.py reverse_physics/tests/test_bt_full_signed_quadratic_closure.py` — 0.03 s, 16,612 KB peak RSS;
- `python3 -m json.tool` on the work item, Science Forge event, schema, and certificate — 0.14 s, 15,304 KB peak RSS;
- `git diff --check -- <scoped paths>` — 0.00 s, 11,160 KB peak RSS.

The certificate was generated by
`python3 reverse_physics/bt_full_signed_quadratic_closure.py` in 0.14 s
with 21,532 KB peak RSS.  Tier 1 then passed:

- `python3 reverse_physics/bt_full_signed_quadratic_closure.py --check` — 20/20 checks, 0.09 s, 21,260 KB peak RSS;
- `python3 reverse_physics/verify_bt_full_signed_quadratic_closure.py` — 13/13 independent checks, 0.14 s, 31,212 KB peak RSS;
- `python3 -m unittest -v reverse_physics.tests.test_bt_full_signed_quadratic_closure` — 9/9 tests, including seven claim mutations, 1.37 s, 31,088 KB peak RSS.

Both consuming papers compiled twice with `pdflatex -interaction=nonstopmode
-halt-on-error` from `paper/`.  Paper V took 0.41 s per pass and at most
50,752 KB peak RSS; Paper VI took 0.44 s per pass and at most 50,876 KB peak
RSS.  Both final PDFs have stable page counts (29 and 37 pages), with no
undefined reference or fatal LaTeX error.

Tier 2 was not run because no shared operator or predecessor certificate
changed: all imported mathematical inputs are content-addressed in the new
certificate.  Tier 3 was not run because this is neither a freeze/release nor
an all-order or continuum theorem promotion.  The Science Forge transition is
an append-only manual `event-v0` fallback with a reproduced FNV-1a identifier;
no successful external coordinator pass is claimed.
