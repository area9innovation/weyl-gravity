# BT full-phase weighted-current gate V2

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The V1 current reduction had the correct translation-invariant target, but its
rational current fixture did not lie in the full cosine--sine background
slice.  It ruled out a universal unweighted-gradient identity, not the
restriction actually used by the score theorem.  V2 closes that gap with an
exact slice-valid fixture and records the stronger structure found during the
audit.

For every positive periodic field \(\Omega_x=e^{\psi_x}\), define

\[
 r_x=\frac{(\Delta\Omega)_x}{\Omega_x},\qquad
 u_x=\frac{r_x}{\Omega_x^2},\qquad
 c_{xy}=\Omega_x\Omega_y.
\]

The canonical current is exactly

\[
 J_{xy}=c_{xy}(u_x-u_y),
 \qquad
 \sum_x\Omega_x^3u_x=\sum_x(\Delta\Omega)_x=0.
\]

Thus it is a gradient after inserting the fluctuating positive conductance
\(c_{xy}\).  It is not an ordinary unweighted periodic gradient.  The missing
score theorem is therefore a random-conductance flux-corrector or
hyperuniformity problem.

In mean-log gauge there is an exact two-part split

\[
 J_{x,i}=(u_x-u_{x+e_i})+K_{x,i},\qquad
 K_{x,i}=(\Omega_x\Omega_{x+e_i}-1)(u_x-u_{x+e_i}).
\]

For an axial momentum this gives

\[
 |\widehat J_1(p)|^2
 \leq2\omega_p|\widehat u(p)|^2+2|\widehat K_1(p)|^2.
\]

Consequently the current theorem follows from two precise subgates:

\[
 \mathbb E_{\nu_p}|\widehat u(p)|^2\leq C_u g^2N,
 \qquad
 \mathbb E_{\nu_p}|\widehat K_1(p)|^2
 \leq C_Kg^2N\omega_p.
\]

## Slice-valid exact fixture

On the \(4^4\) torus let \(\Omega_x=2^{n_x}\), where the exponent depends on
the first two coordinates and has time-by-space matrix

\[
 n=\begin{pmatrix}
 0&0&0&0\\
 0&0&1&-1\\
 0&1&0&-1\\
 0&0&0&0
 \end{pmatrix}.
\]

It is replicated over the other two axes.  Its total exponent and its lowest
axial cosine and sine projections all vanish exactly.  Hence the logarithmic
field lies in the mean-zero carrier intersected with \(E_p^\perp\).

Exact enumeration gives the active residual matrix

\[
 r=\begin{pmatrix}
 0&0&1&-\tfrac12\\
 -\tfrac12&2&-\tfrac94&5\\
 \tfrac12&-2&\tfrac32&3\\
 0&1&0&-\tfrac12
 \end{pmatrix}
\]

and forward time current

\[
 J_0=\begin{pmatrix}
 \tfrac12&-2&\tfrac{25}{8}&-\tfrac{41}{4}\\
 -1&5&-\tfrac{33}{8}&2\\
 \tfrac12&-3&\tfrac32&\tfrac{25}{4}\\
 0&1&-1&0
 \end{pmatrix}.
\]

After the inert replication,

\[
 \sum_xJ_{x,0}=-24,\qquad
 A=\frac{837}{2},\qquad
 \sum_{x,i}c_{x,x+e_i}(u_x-u_{x+e_i})^2
 =\frac{290295}{16}.
\]

The nonzero current zero mode proves that no ordinary periodic-gradient
identity holds even on the exact background slice.  The ordinary-gradient
part has zero periodic current mode, so the complete value \(-24\) is carried
by the conductance corrector \(K\).  This proves that the second subgate is
load-bearing.

## What the hidden gradient does and does not buy

For constant conductance, Fourier transformation of \(\nabla u\) supplies the
second external momentum factor immediately.  Here the conductance is itself
a nonlinear field.  Multiplication by \(c_{xy}\) mixes Fourier momenta, and the
slice-valid fixture shows that this mixing cannot be discarded pointwise.

The new exact target is to construct a stationary flux corrector or prove
directly that

\[
 \mathbb E_{\nu_p}|\widehat J_1(p)|^2
 \leq C_Jg^2N\omega_p.
\]

Large-conductance blocks must be controlled before the position and Fourier
sums are taken.  Translation invariance and the weighted-gradient identity
alone do not imply this estimate.

No annealed score theorem, interacting \(H^{-1}\) estimate, continuum measure,
Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result is claimed.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_weighted_current_gate_v2.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_weighted_current_gate_v2.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_weighted_current_gate_v2
```

## Verification receipt

- Tier 0 passed: Python compilation, schema/certificate JSON parsing, and the
  scoped diff check.  Python and TeX ran under a 500 MB virtual-memory cap.
- The deterministic producer drift check passed in 0.04 s.
- The independent verifier passed in 0.10 s.  It separately enumerates all 256
  sites, proves the V1 row has nonzero phase projections, reconstructs both V2
  matrices, and checks the weighted identity on all 1024 positive edges.
- Twelve direct and adversarial mutation tests passed in 0.23 s.
- The Paper 21 generator drift check and independent authority/boundary verifier
  passed in 0.15 s.
- Two `pdflatex` passes completed in 1.60 s and produced a clean 60-page PDF.
- The first planning-import invocation accidentally inherited the Python
  address-space `ulimit` and Go failed before startup while reserving its page
  summary.  It was not counted as a pass and changed no repository state.  The
  corrected Go-only invocation used `GOMEMLIMIT=300MiB` without that shell cap
  and imported 1631 nodes with zero invalid items and zero malformed events in
  6.82 s.
- The 2.18 s advisory Science Forge shadow rail again failed closed on the
  pre-existing Forge binary/stdlib mismatch (`E9118`) and reported corpus
  baseline drift (1738 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Tier 2 was not run because the two content-addressed inputs and their shared
  operators are unchanged; their hashes are checked independently.
- Tier 3 was not run because this is a working-draft correction and reduction,
  not a freeze, release, lifecycle promotion, or shared-core algebra change.
  The flux-corrector, susceptibility, score, \(H^{-1}\), and continuum gates all
  remain explicitly open.
