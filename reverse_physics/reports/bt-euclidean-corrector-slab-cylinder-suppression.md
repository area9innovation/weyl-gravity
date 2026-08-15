# BT corrector-slab cylinder suppression

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_CYLINDER_SUPPRESSION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The earlier fiber-stability result compared marginal densities at the exact
slab and at zero.  The comparison now extends to a real positive-radius event.

Let $\eta_L=(\log 2)n_L$ be the slice-valid localized slab.  On the six-row
buffer $t=-1,0,1,2,3,4$, write a reference configuration as

\[
 \psi_{t,s,x_2,x_3}=T_t+\zeta_{t,s,x_2,x_3},
 \qquad \lVert\zeta\rVert_\infty\leq\frac1{400},
\]

where the time-only field $T_t$ is arbitrary.  Adding $\eta_L$ changes
residuals only on rows $0,1,2,3$.

First set $\zeta=0$ and introduce the five positive time-edge ratios

\[
 A=\frac{q_{-1}}{q_0},\quad B=\frac{q_1}{q_0},\quad
 C=\frac{q_2}{q_1},\quad D=\frac{q_3}{q_2},\quad
 E=\frac{q_4}{q_3}.
\]

Exact expansion of the sixteen changed residual squares gives a Laurent
polynomial.  Every coefficient is nonnegative except the two terms $-2B$ and
$-2D^{-1}$.  Retaining their positive quadratic partners and completing
squares already proves

\[
 \sum_{t=0}^3\sum_{s\bmod4}
 \left(r_{t,s}(T+\eta_L)^2-r_{t,s}(T)^2\right)
 \geq \frac{349}{144}.
\]

The important new step is uniformity under $\zeta$.  Every directed edge
multiplier contributed by the perturbation lies in

\[
 \left[\frac{199}{200},\frac{200}{199}\right],
\]

because neighboring logarithmic perturbations differ by at most $1/200$.
The certificate independently relaxes every edge multiplier to this rational
interval and reconstructs all seventeen Laurent coefficients using exact
fraction interval arithmetic.  Only the same two linear terms can have
negative lower endpoints.  If

\[
 \alpha=\frac{13987109613}{6336160000},\qquad
 \beta=\frac{10549}{4975},\qquad
 c_0=\frac{54646591421}{25344640000},
\]

the two square completions give the uniform residual-square gap

\[
 g=c_0-\frac{\beta^2}{2\alpha}
 =\frac{403338322161150510073}{354498257782024320000}
 >1.1377.
\]

This enclosure includes all eight lattice neighbors.  The four inert-direction
neighbors were not silently frozen when the positive-radius perturbation was
introduced.

## Gibbs probability rather than point density

Let $C_0$ be the cylinder of all mean-log-gauge fields admitting such a
six-row decomposition; rows outside the buffer are unconstrained.  Let
$C_\eta=\eta_L+C_0$.  There are $(L/4)L^2=L^3/4$ replicated spatial periods and
inert-site pairs, while the BT action is one half the residual-square sum.
Therefore

\[
 A(\psi+\eta_L)-A(\psi)\geq \frac{g}{8}L^3
 \qquad(\psi\in C_0).
\]

Translation preserves Lebesgue measure and the mean-log slice, so the
normalized finite-volume Gibbs measure satisfies

\[
 \mu_\lambda(C_\eta)
 \leq \exp\left[-\frac{g}{8\lambda^2}L^3\right]
       \mu_\lambda(C_0)
 \leq \exp\left[-\frac{g}{8\lambda^2}L^3\right].
\]

At $\lambda=2/5$ this is

\[
 \mu_{2/5}(C_\eta)
 \leq \exp[-c_{\rm cyl}L^3],\qquad
 c_{\rm cyl}=
 \frac{403338322161150510073}{453757769960991129600}
 >0.8888.
\]

No event-volume estimate is needed: translation pairs the reference cylinder
with the slab cylinder before normalization.  Because $C_0$ is invariant under
the removed lowest cosine--sine row fields, the event descends to the exact
integrated background marginal.

## Boundary of the conclusion

This closes the positive-radius/entropy gate for one explicit structured slab
tube.  It does not prove that every configuration with a large lowest-mode
corrector contains such a tube, nor that many tubes can be translated
compatibly.  The corrector hyperuniformity, weighted-potential mass estimate,
current susceptibility, interacting $H^{-1}$ moment, and continuum limit
remain open.  No Born, Krein, or `LORENTZIAN-CAUSAL` promotion is made.

The next calculation is a deterministic corrector-to-block extraction lemma.
It must show that a large corrector forces a positive density of disjoint
costly flux motifs, or produce an explicit avoiding family.  Only after a
compatibility estimate for those motifs can this single-cylinder probability
bound become a corrector tail theorem.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_cylinder_suppression.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_cylinder_suppression.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_cylinder_suppression
```

## Verification receipt

- Tier 0 passed: changed Python files compile, structured data parse, and the
  scoped diff has no whitespace errors.  Python and TeX ran under a 500 MB
  virtual-memory cap.
- The deterministic producer drift check passed in 0.04 s.  The independent
  verifier passed in 0.09 s and reconstructs the interval polynomial without
  importing the producer; the scoped rails used at most 31 MB resident memory.
- Eleven direct and adversarial tests passed in 0.16 s.  They reject changes to the
  interval ledger, robust gap, action multiplicity, probability exponent,
  input hashes, dependency boundary, and open global-corrector gates.
- The Paper 21 generator drift check and independent claim verifier passed in
  0.15 s.  Two `pdflatex` passes took 1.56 s and produced a clean 61-page PDF.
- The planning import read 1634 nodes with zero invalid items and zero
  malformed events in 10.57 s.
- The 2.25 s advisory Science Forge shadow rail failed closed on the
  pre-existing Forge binary/stdlib mismatch (`E9118`) and reported corpus
  baseline drift (1747 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Tier 2 was not run because both content-addressed mathematical inputs and
  their shared action operator are unchanged; their hashes are verified.
- Tier 3 was not run because this is a single-family cylinder theorem, not the
  requested global $H^{-1}$ lifecycle promotion, a freeze, or a release.
