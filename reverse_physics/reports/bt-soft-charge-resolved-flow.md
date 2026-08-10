# BT soft flow after charge resolution

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The full off-resonant kernel fixes the leading-log normalization before charge
projection, but the published fixed-vacuum oscillator grading does not yet
place that logarithm in the physical neutral pushforward.  The first exact
obstruction is charge-theoretic rather than numerical.

## The normalization match

Let

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix}
\]

be the BT one-particle Krein matrix.  The universal soft residue and parent
metric are

\[
 G_{\rm soft}=-\frac{E}{2r^3}J,
 \qquad g_{\rm parent}^{-1}=\frac{J}{2E}.
\]

Raising the parent index therefore gives

\[
 g_{\rm parent}^{-1}G_{\rm soft}
 =-\frac1{4r^3}\mathbf 1.
\]

The symmetric quadratic map contributes the certified Bose factor $1/2$, and

\[
 \int\frac{d\Omega}{(2\pi)^3}=\frac1{2\pi^2}.
\]

Thus the measured shell coefficient is

\[
 -\frac{\lambda^2}{16\pi^2}\frac{dr}{r}.
\]

Rescaling the lower resolution by $\epsilon\mapsto c\epsilon$ changes the
finite part by

\[
 +\frac{\lambda^2}{16\pi^2}\log c.
\]

The incoming $2!$ weight is common to the Born and real channels.  The outgoing
projector changes from $1/2!$ to $1/3!$, so each unordered pair carries the
exact ratio $2!/3!=1/3$.  With
$\eta=\lambda^2\log c/\pi^2$ this gives

\[
 \Delta P_{\rm pair}=+\frac{\eta}{48},
 \qquad
 \sum_{\rm three\ pairs}\Delta P_{\rm pair}=+\frac{\eta}{16}.
\]

Projector idempotence would force the hard block to be $-\eta/16$.  Multiplying
by the certified Born coefficient $3/32$ gives $-3/512$, exactly opposing the
complete real response.  Hence the previously fitted finite-carrier number is
now the exact unprojected soft-shell normalization.

## The charge obstruction

Under the published oscillator grading
$q(\Omega)=+1$, $q(\Upsilon)=-1$, with BT dagger preserving charge, the two
logarithmic contractions are:

| first daughter pair | partner pair | generator charges | residue |
|---|---|---:|---:|
| $\Omega\Omega$ | $\Upsilon\Upsilon$ | $(+1,-1)$ | $-1/4$ |
| $\Upsilon\Omega$ | $\Omega\Upsilon$ | $(-1,+1)$ | $-1/4$ |

They sum to $-1/2$.  No logarithmic row has both generator charges nonpositive.
If the one-sided nonpositive-image condition is imposed on the available
oscillator map before the Gram is formed, its logarithmic residue is therefore
exactly zero.

This is not a proof that the full BT construction gives zero.  The fixed vacuum
$\langle\Omega\rangle=\lambda^{-1}$ breaks the boost/exchange symmetry.  A
charge-covariant completion could include a background zero-mode operator and
regrade the displayed $\pm1$ pieces into the neutral pushforward.  But
neutralizing the two logarithmic rows requires both background charge shifts
$-1$ and $+1$.  Neither that bidirectional zero-mode algebra nor the complete
order-$\lambda$ pushforward $R_tP_2R_t^\dagger$ is published.
The official arXiv record was checked again on 2026-08-10: it still lists only
v1 of the six-page Letter, and exact-title searches returned no arXiv record
for the deferred companion.

There are consequently three live outcomes:

1. the completed background pushforward combines both signs into the neutral
   component, yielding the candidate $1/48$ per pair;
2. the one-sided projection removes the positive partners, yielding zero; or
3. positive charge survives without neutral completion, in which case the
   existing relative-radical positivity argument is not applicable.

The public data do not decide among them.  The physical neutral coefficient
therefore remains fail-closed.

## Finite-cutoff flow and regulator families

If $D$ is the number-lowering part of the off-resonant map, the formal
finite-cutoff canonical flow is

\[
 K_t=e^{-idt}D-e^{idt}D^\sharp,
 \qquad
 H_{\rm as}^{(1)}(t)=i\dot K_t
 =d\left(e^{-idt}D+e^{idt}D^\sharp\right).
\]

Thus $K_t^\sharp=-K_t$ and
$(H_{\rm as}^{(1)})^\sharp=H_{\rm as}^{(1)}$.  This explains how the Jordan
map can survive even though the ordinary one-denominator cubic kernel vanishes
pointwise: the Hamiltonian is proportional to $d$, while its long-time
integral recovers the boundary map.

The leading response is profile independent.  A sharp lower cutoff has

\[
 I_{\rm sharp}(\epsilon)=-C\log\frac{r_0}{\epsilon},
\]

while the smooth profile $f_a(r/\epsilon)=r/(r+a\epsilon)$ gives

\[
 I_a(\epsilon)=-C\log\frac{r_0+a\epsilon}{a\epsilon},
 \qquad C=\frac{\lambda^2}{16\pi^2}.
\]

Both obey

\[
 I(c\epsilon)-I(\epsilon)\longrightarrow C\log c.
\]

They differ by the finite scheme constant $C\log a$.  Response universality
does not select that finite matching constant.  Moreover, the logarithmic norm
means the zero-cutoff dressing is not trace class on the original Fock--Krein
representation.  A relative hard $S$-matrix would still need to be constructed.

## Disposition

Established exactly:

- the unprojected $1/48$ leading-log normalization per pair;
- the total $+1/16$ and forced hard $-1/16$ normalization ledger;
- sharp/smooth regulator-response universality;
- the formal finite-cutoff anti-Krein flow; and
- the fact that the complete logarithm is made solely from $+1/-1$ charge
  pairings and becomes zero under a prior one-sided nonpositive projection.

Not established:

- which charge outcome occurs in the full background-resolved pushforward;
- the physical neutral $1/48$ coefficient;
- a finite hard matching constant or hard $S$-matrix;
- incoming degenerate sectors, multiple-emission resummation, or the complete
  NLO quotient trace;
- beyond-tree positivity, a gravitational lift, or anything
  `LORENTZIAN-CAUSAL`.

The next object is not another endpoint prescription.  It is the
broken-vacuum zero-mode-resolved order-$\lambda$ proof of BT Eq. (19), or an
equivalent explicit construction of $R_tP_2R_t^\dagger$.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_soft_charge_resolved_flow.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_soft_charge_resolved_flow.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_soft_charge_resolved_flow
```

## Verification receipt (2026-08-10)

All commands ran sequentially with `ulimit -v 500000`.

- Python parse/compile: PASS, 0.06 s, 15,672 KB peak RSS.
- Exact producer replay: PASS 18/18, 0.05 s, 20,600 KB peak RSS.
- Method-distinct schema/charge/normalization verifier: PASS 7/7, 0.10 s,
  30,304 KB peak RSS after the final input-hash refresh.
- Mutation and producer/verifier tests, including a hard-sign mutation: PASS
  7/7, 0.72 s, 30,644 KB peak RSS.
- Full off-resonant predecessor tests: PASS 5/5, 0.71 s, 30,528 KB peak
  RSS.
- Inclusive-radical direct-consumer tests: the first run correctly failed
  2/12 because the BT digest update made its pinned input hash stale.
  The certificate was regenerated, changing only that SHA-256 field; producer
  replay then passed 13/13 in 0.05 s, its independent verifier passed 12/12 in
  0.13 s, and the full consumer suite passed 12/12 in 0.40 s (30,516 KB peak
  RSS).  The failed first run is not counted as a pass.
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each.  Times were
  0.55/0.46 s and, after the final wording clarification, 0.44/0.45 s
  respectively; peak RSS stayed below 51 MB.
- All five changed JSON artifacts parsed in 0.17 s; final PDF text witnesses
  passed in 0.11 s; scoped `git diff --check` passed.  A first literal PDF
  witness looked for a phrase split by line wrapping and was not counted; the
  corrected semantic witnesses were `generator charges` and `charge
  obstruction`.

Tier 2 stopped at the content-addressed direct consumers listed above: no
shared mathematical predecessor changed.  Tier 3 was not run because this is
neither a freeze/release nor a promotion beyond `CLASSIFIED`.  The Science
Forge coordinator import was not claimed: its Go runtime is known to exceed
the mandatory memory cap in this workspace, so the append-only event and work
item were syntax-checked directly and remain fail-closed with respect to a
coordinator pass.
