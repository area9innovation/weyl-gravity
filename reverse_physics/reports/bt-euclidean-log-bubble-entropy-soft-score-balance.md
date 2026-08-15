# BT logarithmic-bubble entropy and soft-score balance

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_ENTROPY_SOFT_SCORE_BALANCE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The bad logarithmic bubbles lie below the action threshold needed for a bare
energy-versus-position-entropy proof.  They nevertheless carry two powers of
their radius in the lowest-mode score.  Squaring that soft insertion cancels
their four-dimensional positional entropy.

Thus an energy-only Peierls or union-bound proof is obstructed, but the
bubbles do not obstruct the score estimate at dilute observable-weighted
power counting.  The next viable architecture is an observable-weighted
block or polymer estimate that preserves the soft factor.

## An exact subcritical wall

Use the quintic smoothstep

\[
                 W(z)=10z^3-15z^4+6z^5
\]

on two reflected logarithmic ramps of width \(\delta=7/2\), with no plateau,
and set

\[
                    \psi'(r)=-\frac53\frac{w(s)}r,
                    \qquad s=\log(r/r_-).
\]

The field is constant inside and outside the annulus and is \(C^3\).  After
removing the common positive factor \(2\pi^2\), exact polynomial integration
gives

\[
 Q=\frac{476450}{14553},\qquad
 C=-\frac{6500}{297},\qquad
 P=\frac{11151875}{680238}.
\]

Therefore

\[
 A_{\rm red}=\frac{Q+2C+P}{2}
 =\frac{1965963925}{733296564}<\frac{16}{5},
\]

and

\[
 D_{\rm red}=Q+3C+2P
 =-\frac{2157475}{16665831}<0.
\]

No floating-point value decides either comparison.

## Why action alone cannot make the bubbles rare

On the tuned refinement branch,

\[
                  g_L^2\log L\longrightarrow\frac{8\pi^2}{5}.
\]

The full continuum action is \(A_*=2\pi^2A_{\rm red}\), so one resolved
bubble has bare weight

\[
 e^{-A_L/g_L^2}=L^{-\beta+o(1)},\qquad
 \beta=\frac54A_{\rm red}
 =\frac{9829819625}{2933186256}.
\]

Choose its lattice radius as \(K_L=\lceil\log L\rceil\).  The bubble is both
resolved and small compared with the torus, and separated blocks supply
\(L^{4+o(1)}\) placements.  Since

\[
 4-\beta=\frac{1902925399}{2933186256}>0,
\]

the count times the single-profile weight grows rather than shrinks.  A proof
that assigns each placement only its classical action cost cannot establish
bubble rarity.

This is not a probability lower bound.  A profile has zero Lebesgue measure,
and the calculation does not control its fluctuation neighborhood, the
partition function, background cross terms, or multibubble interactions.

## Why the same bubbles are soft in the target observable

For the continuum residual

\[
                  R_\psi=\Delta\psi+|\nabla\psi|^2,
\]

the directional action derivative is

\[
 D_hA(\psi)=\int R_\psi
       \left(\Delta h+2\nabla\psi\mathbin\cdot\nabla h\right).
\]

Scale and translate the wall by
\(\psi_{R,z}(x)=\psi_0((x-z)/R)\).  Shift invariance removes the constant
Taylor term.  Radial reflection gives

\[
          \int R_0(y)\nabla\psi_0(y)\,dy=0,
\]

so the linear term also vanishes.  Taylor's theorem then yields

\[
                    |D_hA(\psi_{R,z})|\leq C R^2.
\]

The same cancellation survives finite-difference sampling.  Write
\(G_x=\partial A_L/\partial\psi_x\).  Exact shift invariance gives
\(\sum_xG_x=0\), while reflection around the bubble center \(z\) gives
\(\sum_xG_x(x-z)=0\).  Consistency of the sampled smooth wall gives
\(\sum_x|G_x||x-z|^2=O(K^2)\).  Applying the second-order Taylor remainder
of the cosine therefore proves, uniformly in the center,

\[
               |D_{h_L}A_L|=O\!\left((K/L)^2\right).
\]

Because \(S_g(\phi)=A(g\phi)/g^2\), its \(\phi\)-score is \(g^{-1}D_hA\).
The placement count and squared insertion therefore balance as

\[
 \left(\frac LK\right)^4
 e^{-A_L/g_L^2}
 \frac1{g_L^2}\left(\frac KL\right)^4
 =O\!\left(g_L^{-2}L^{-\beta+o(1)}\right)\longrightarrow0.
\]

An additional logarithmic sum over resolved scales still tends to zero.
This is the precise sense in which the bubbles proliferate in a bare count
but remain harmless in the dilute lowest-score power count.

## Remaining gate

The actual BT measure can contain overlapping bubbles, correlated phases,
non-bubble backgrounds, and nontrivial fluctuation volumes.  The next theorem
must decompose the whole zero-fiber score into localized blocks while keeping
the quadratic external-momentum factor before summing positions and scales.
An interacting multibubble construction that defeats this cancellation is the
corresponding falsification branch.

This certificate proves neither the actual annealed score bound nor the
interacting \(H^{-1}\) estimate.  It constructs no continuum measure and has
no Born, Krein, or `LORENTZIAN-CAUSAL` consequence.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_log_bubble_entropy_soft_score_balance.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_log_bubble_entropy_soft_score_balance.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_log_bubble_entropy_soft_score_balance
```

## Tier receipt

- Tier 0: Python compilation and certificate/schema/event JSON parsing passed.
  The generated-appendix freshness check passed.  The two-pass Paper 21 build
  and undefined-reference/overfull-box scan passed in 1.58 seconds.  Scoped
  `git diff --check` and exact staged-diff inspection passed before commit.
- Tier 1: producer replay passed in 0.04 seconds; the independent
  sparse-polynomial verifier passed in 0.08 seconds; nine direct and mutation
  tests passed in 0.10 seconds.  The Paper 21 claim-map producer and verifier
  each passed in 0.07 seconds.
- Tier 2 was not run because the three imported mathematical inputs are
  unchanged and content-pinned.  Their direct Paper 21 consumer was checked.
- Tier 3 was not run because this is a scoped Euclidean method result, not a
  freeze, release, shared-core change, or lifecycle promotion.
- The append-only programme fold imported 1629 nodes with zero invalid items
  and zero malformed events.  The advisory Science Forge shadow rail ran but
  did not certify: its bridge audit again hit the external Forge
  toolchain/library mismatch (`E9118`), and its corpus census reported baseline
  drift.  Those advisory findings do not establish or invalidate this result.
