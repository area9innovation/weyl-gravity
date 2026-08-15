# BT full-phase current-susceptibility gate

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

Removing the full lowest cosine--sine eigenspace makes the exact background
marginal translation invariant.  The two zero-fiber scores then combine into
the Fourier divergence of one explicit antisymmetric local current.  The
missing score theorem is equivalent to a single current-susceptibility bound.

The current supplies one external momentum factor exactly.  A rational
fixture shows that it does not supply the second factor pointwise.  That
factor must be a statistical theorem under the background Gibbs marginal.

## Full-phase center reduction

Let \(E_p=\operatorname{span}\{h_c,h_s\}\), with
\(h_c(x)=\cos(2\pi x_1/L)\) and \(h_s(x)=\sin(2\pi x_1/L)\).  Translations
rotate this pair and preserve \(E_p^\perp\), the action, and the exact
background marginal.  Since the certified curvature holds for every phase,

\[
 \operatorname{Hess}V_\eta\geq\kappa_L I_2,
 \qquad \kappa_L=\frac29N\omega_p^2.
\]

The conditional mode obeys
\(|m(\eta)|^2\leq|\nabla V_\eta(0)|^2/\kappa_L^2\).  Moreover,
\(\mathbb E[(T-m)\cdot\nabla V_\eta(T)]=2\) gives
\(\mathbb E[|T-m|^2\mid\eta]\leq2/\kappa_L\).  Therefore

\[
 \mathbb E_\nu|\nabla V_\eta(0)|^2\leq C_sN\omega_p^2
 \quad\Longrightarrow\quad
 \mathbb E|T|^2\leq\frac{36+81C_s}{2N\omega_p^2}.
\]

## Exact current identity

With \(w_{xy}=e^{\psi_y-\psi_x}\), set

\[
 r_x=\sum_{y\sim x}(w_{xy}-1),\qquad A=\frac12\sum_xr_x^2,
\]

and on the edge \(x\to x+e_i\) define

\[
 J_{x,i}=r_xw_{x,x+e_i}-r_{x+e_i}w_{x+e_i,x}.
\]

Direct differentiation and Fourier transformation give

\[
 \frac{\partial A}{\partial\psi_x}
 =-\sum_i(J_{x,i}-J_{x-e_i,i}),\qquad
 \widehat G(p)=\sum_i(e^{ip_i}-1)\widehat J_i(p).
\]

For an axial lowest momentum, the two real \(\phi\)-scores satisfy

\[
 s_c^2+s_s^2=\frac{\omega_p}{g^2}|\widehat J_1(p)|^2.
\]

Thus the missing score estimate is equivalent to

\[
 \mathbb E_{\nu_p}|\widehat J_1(p)|^2
 \leq C_Jg^2N\omega_p.
\]

## Pointwise second-factor obstruction

On the \(4^4\) torus, take a field constant in three coordinates with
positive time row \(\Omega=(1,1,2,4)\).  Subtracting the logarithmic mean
changes no weight.  Exact enumeration gives, per spatial site,

\[
 r=(3,1,\tfrac12,-\tfrac54),\qquad
 J=(2,\tfrac74,\tfrac{13}{8},-\tfrac{197}{16}).
\]

Consequently

\[
 \sum_tJ_t=-\frac{111}{16},\qquad
 \sum_{x\in(\mathbb Z/4\mathbb Z)^4}J_{x,1}=-444,
 \qquad A=378.
\]

The canonical current is not a periodic gradient and is not pointwise
divisible by another external momentum.  This does not rule out statistical
suppression of its low-frequency longitudinal structure factor.

## Remaining gate

The live target is the translation-invariant current bound above.  An
observable-weighted block decomposition may prove it; a translation-covariant
correlated multibubble sequence with divergent normalized current structure
factor would obstruct it.

No score theorem, interacting \(H^{-1}\) estimate, continuum measure, Born
rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result is claimed.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_current_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_current_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_current_gate
```

## Verification receipt

All Python and TeX commands were run with a 500 MB virtual-memory cap; the
Science Forge commands used `GOMEMLIMIT=300MiB`.

- Tier 0 passed: Python compilation, schema JSON parsing, generated-certificate
  parsing, and scoped `git diff --check` (0.01 s).
- The deterministic producer drift check passed in 0.03 s.
- The independent exact verifier passed in 0.09 s.  It re-enumerates all 256
  sites of the rational \(4^4\) fixture rather than reading the producer's
  intermediate current row, and compares the direct action gradient with the
  current divergence at every site.
- Nine direct and adversarial mutation tests passed in 0.21 s.
- The Paper 21 claim-map drift check and independent authority/boundary verifier
  passed in 0.14 s.
- Two `pdflatex` passes completed in 1.45 s and produced a 59-page PDF.  The
  second pass has no undefined citations, references, overfull boxes, or TeX
  errors.
- Science Forge imported 1630 nodes with zero invalid work items and zero
  malformed events in 6.09 s.
- The 2.07 s advisory Science Forge shadow rail remained fail-closed on its
  pre-existing Forge binary/stdlib mismatch (`E9118`) and reported the known
  corpus-baseline drift (1736 certificates versus the 2026-07-19 baseline of
  976).  Its advisory process exited zero; the failed bridge audit is recorded
  as a finding, not a pass.
- Tier 2 was not run: the three content-addressed upstream BT authorities and
  their operators are unchanged; their hashes were checked by the producer,
  independent verifier, and Paper 21 authority rail.
- Tier 3 was not run: this working-draft checkpoint changes no shared algebra,
  freeze/tag, lifecycle state, or release boundary.  It does not promote the
  open susceptibility, interacting score, \(H^{-1}\), or continuum claims.
