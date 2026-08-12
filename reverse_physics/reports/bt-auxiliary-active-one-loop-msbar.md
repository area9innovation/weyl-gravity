# BT auxiliary active one-loop coefficient in MSbar

Certificate: `REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
Lifecycle: `COEFFICIENT_COMPUTED` for the covariant active loop.

## Result

The complete real finite active one-loop differential coefficient in the
declared auxiliary MSbar scheme is

\[
 \boxed{
 {d\sigma_{\rm active,\overline{MS}}^{(6)}\over d\Omega}
 ={5\lambda^6\over256\pi^4s}
 (L_s+L_t+L_u+6),
 \qquad L_X=\log{\mu^2\over|X|}.}
\]

The previously certified logarithm is the first three terms. The new finite
constant is `+6`: one `+2` from each of the three massless bubble channels.
This is not inferred from the beta function. It follows from the exact
Feynman-parameter integral and an independent auxiliary species contraction.

This closes the finite covariant active-loop calculation. It does not yet
identify that kernel with the second-order finite-duration BT Dyson operator
used by the connected tree experiment. Therefore the complete tagged `q6`
probability remains unpromoted.

## Exact species tensor

Write `g=lambda^2`. The auxiliary vertex tensor divided by `g` is two when
its four external fields contain two `Omega` and two `Upsilon`, and zero
otherwise. The propagator metric is cross-only.

There are six neutral external assignments, labelled by the two positions
occupied by `Omega`. Contracting two vertices with symmetry factor `1/2`
gives the following channel weights:

| Omega labels | s | t | u |
|---|---:|---:|---:|
| `01` | 2 | 4 | 4 |
| `02` | 4 | 2 | 4 |
| `03` | 4 | 4 | 2 |
| `12` | 4 | 4 | 2 |
| `13` | 4 | 2 | 4 |
| `23` | 2 | 4 | 4 |

Every row is a permutation of `(2,4,4)`, and every channel column sums to
twenty. The positive tree vector is `d_S=2`; its complement-pairing norm is

\[
 \langle d,d\rangle_J=24.
\]

The tree-loop pairing is

\[
 \langle d,b\rangle_J=40(B_s+B_t+B_u).
\]

Including the loop factor gives the relative interference

\[
 {2\Re\langle A_{\rm tree},A_{\rm loop}\rangle
  \over \langle A_{\rm tree},A_{\rm tree}\rangle}
 ={5g\over24\pi^2}(B_s+B_t+B_u).
\]

Multiplying the independently certified Born density
`3 lambda^4/(32 pi^2 s)` reproduces the independently certified hard-log
coefficient `5/256`. Thus the species normalization is not fitted to the
answer.

## Finite bubble

After MSbar pole subtraction, the real massless scalar bubble is

\[
 B_X=-\int_0^1dx\,
 \log\left({x(1-x)|X|\over\mu^2}\right).
\]

Since

\[
 \int_0^1\log x\,dx
 =\int_0^1\log(1-x)\,dx=-1,
\]

we obtain

\[
 \boxed{B_X=L_X+2.}
\]

For timelike `s`, the bubble also has the standard cut imaginary part. It is
orthogonal to the real tree in the virtual interference computed here. Its
unitarity role belongs to the separate cut/inclusive ledger.

The finite `+6` is MSbar-specific. A finite coupling redefinition shifts a
local multiple of the tree along with the definition of `lambda(mu)`. The
logarithmic coefficient and one-loop beta coefficient remain universal.

## Tagged central coefficient

At

\[
 s={64\over25}\kappa^2,
 \qquad t=u=-{32\over25}\kappa^2,
\]

put

\[
 L_*=\log{25\mu^2\over64\kappa^2}
 +2\log{25\mu^2\over32\kappa^2}.
\]

The local active click coefficient is

\[
 \boxed{
 q_{\rm active,\overline{MS}}^{(6)}
 ={125\lambda^6\Delta\Omega
 \over16384\pi^4\kappa^2\operatorname{Area}}(L_*+6).}
\]

Here `DeltaOmega` denotes a local angular cell coefficient. For a finite
window the logarithm must be integrated rather than frozen at its center.

## Exact hard window

For `theta0<=theta<=pi-theta0`, define

\[
 a={1-\cos\theta_0\over2},\qquad c=\cos\theta_0.
\]

Then

\[
 I(a)=\int_a^{1-a}-\log[z(1-z)]\,dz
 =2c-2(1-a)\log(1-a)+2a\log a.
\]

The exact finite loop contribution in the window is

\[
 \boxed{
 \sigma_{\rm active,\overline{MS}}^{(6)}
 ={5\lambda^6\over64\pi^3s}
 \left[c\left(3\log{\mu^2\over s}+6\right)+I(a)\right].}
\]

It is finite for every `0<a<1/2`.

## Compact hard packet kernel

After removing the common four-momentum delta, restrict the two-body coarea
to compact supports satisfying

\[
 0<\rho\le |s|,|t|,|u|\le R.
\]

Every real bubble obeys

\[
 |B_X|\le 2+max\left(
 \left|\log{\mu^2\over\rho}\right|,
 \left|\log{\mu^2\over R}\right|\right).
\]

Each species row has absolute coefficient sum ten. The finite species tensor
and logarithms are therefore bounded on the compact product support, making
the reduced covariant packet kernel Hilbert--Schmidt.

This is a covariant hard packet kernel. It is not yet a proof of equality
with a sharp-switch finite-time Dyson kernel, whose transient pieces and
local Hamiltonian counterterm have not been derived.

## Remaining barrier

The next calculation is no longer the covariant loop integral. It is the
carrier-affiliation theorem:

1. construct the second-order finite-duration auxiliary Dyson kernel;
2. renormalize its local ultraviolet term in the same MSbar convention;
3. identify its covariant boundary with the kernel above;
4. retain and control its finite-time transient terms; and
5. only then add it to the certified connected-tree compact functional.

Until that is done, the complete tagged `q6` coefficient, its sign, general
Eq. (19), all-order positivity, and every gravity or Lorentzian claim remain
open.

## Source and claim boundary

The auxiliary action is imported from Bateman and Turok,
*Escape from Ostrogradsky via Hidden Ghost Parity*, arXiv:2607.00096v1. The
Born normalization, beta function and hard logarithm are imported through
content-addressed predecessor certificates. The six-species contraction,
finite MSbar constant, hard-window integral and compact-kernel bound are this
repository's calculations. No literature-priority claim is made.

This result does not establish a finite-duration Hamiltonian loop, the
complete tagged probability, real--virtual/KLN completion, an all-time
operator, general Eq. (19), all-order positivity, gravity or metric BV--BRST
transfer, a restored gravitational QME, or anything `LORENTZIAN-CAUSAL`.

## Verification receipt

- Tier 0: the changed Python files compile and all four structured JSON files
  parse under the cap in `0.02 s` with peak RSS `14,928 KB`; the scoped diff
  passes `git diff --check`. Paper 05 compiles twice, with its final pass
  taking `0.47 s`, peak RSS `51,012 KB`, and producing 57 pages (`649,035`
  bytes). Paper 06 compiles twice, with its final pass taking `0.49 s`, peak
  RSS `50,784 KB`, and producing 54 pages (`635,685` bytes). No new overfull
  boxes are introduced; only the previously recorded paragraphs remain.
- Tier 1: the exact producer passes 25/25 checks in `0.52 s` with peak RSS
  `71,264 KB`; the method-distinct verifier passes 28/28 checks in `0.41 s`
  with peak RSS `72,296 KB`; and 15 tests including 14 adversarial mutations
  pass in `0.63 s` with peak RSS `72,944 KB`. All scientific rails run
  sequentially under the 500 MB virtual-memory cap.
- Tier 2 inputs are unchanged and content addressed; no predecessor producer
  is rerun.
- Tier 3 is not required because no freeze, release, shared core, QME state,
  residual transfer, or Lorentzian theorem is promoted.
- The Science Forge fold accepts 1,511 nodes including the work item and
  append-only DONE event, with zero invalid items and zero malformed events.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_auxiliary_active_one_loop_msbar.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_auxiliary_active_one_loop_msbar.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_auxiliary_active_one_loop_msbar
```

CLOSE-OUT: DONE — the complete finite real covariant active loop is computed
in MSbar; finite-duration BT Dyson affiliation is the remaining carrier gate.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json`
