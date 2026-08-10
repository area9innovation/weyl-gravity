# Bateman--Turok order-lambda (R_t) Jordan kernel

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1`](../certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json)

## What changed

The first nonlinear, cross-multiplicity part of the Bateman--Turok map can be
derived from their public Eq. (16); it does not have to be fitted to the
required `1/48` projector norm.  The derivation exposes an internal label
inconsistency in the Letter's Appendix C and then finds an exact cancellation
of the apparent Jordan secular growth on the two-field carrier.

This crosses the previous `order-lambda R_t kernel not available` gate.  It
does **not** yet produce the complete probability, because the derived kernel
has non-integrable collinear endpoint poles and still needs a physical
distributional extension together with the omitted oscillatory sectors.

## Appendix C consistency check

Equation (31), as printed, assigns the ordinary mode to (a_1) and the
growing mode to (a_2):

\[
 \phi^+\sim e^{-iEt}\left[a_1+(1+2iEt)a_2\right].
\]

But direct application of the symplectic extractor used in the same appendix
gives two facts:

- \(\Box\phi\) selects the growing oscillator, so Eq. (32) requires that
  oscillator to be (a_1);
- the ordinary term in Eq. (33) is (a_2/(4E^2)), while its secular and
  oscillatory terms carry (a_1).

Thus Eq. (31) cannot imply both Eqs. (32) and (33) with the printed labels.
Exchanging (a_1\leftrightarrow a_2) in Eq. (31) repairs both equations:

\[
 \phi^+\sim e^{-iEt}\left[a_2+(1+2iEt)a_1\right].
\]

The commutator algebra is symmetric under this exchange, so the public Letter
does not determine whether Eq. (31) or Eqs. (32)--(33) contain the
typographical error.  The certificate makes only the internal-consistency
claim and declares the repair used for the calculation.

## Dynamical kernel from Eq. (16)

Expanding the two composite fields gives

\[
 R^\dagger\Omega R
 =\lambda^{-1}+\phi+\frac{\lambda}{2}\phi^2+O(\lambda^2),
\]

\[
 R^\dagger\Upsilon R
 =\Box\phi+\lambda\left[(\partial\phi)^2-\phi\Box\phi\right]
 +O(\lambda^2).
\]

For collinear positive-energy daughters with (E=e_1+e_2), write the
time-polynomial part of a product mode as (P(t)).  The exact resonant
symplectic rule is

\[
 \omega_{\rm res}[P]=iP'(t)+2EP(t).
\]

After removing the common factors
\(lambda(2e_1)^{-3}(2e_2)^{-3}\) and the momentum delta function, the
(\Omega) kernel in the repaired (a) basis is

\[
\begin{array}{c|cc}
 &a_2(e_2)&a_1(e_2)\\ \hline
a_2(e_1)&2E&2e_1+4iEe_2t\\
a_1(e_1)&2e_2+4iEe_1t&
4i(e_1^2+e_2^2)t-8Ee_1e_2t^2
\end{array}
\]

and the (\Upsilon) kernel is

\[
\begin{array}{c|cc}
 &a_2(e_2)&a_1(e_2)\\ \hline
a_2(e_1)&0&8Ee_2(e_1-e_2)\\
a_1(e_1)&8Ee_1(e_2-e_1)&-8E(e_1^2+e_2^2).
\end{array}
\]

These entries are derived coefficients, not a projector ansatz.

## The secular cancellation

On the two-annihilator sector the repaired leading inverse map is

\[
 a_1=b_\Upsilon,
 \qquad
 a_2=4e^2b_\Omega-2iet\,b_\Upsilon.
\]

Substituting this into the two tables cancels every (t) and (t^2) term.
After restoring the mode densities, the time-independent result is

\[
\begin{aligned}
 \delta b_\Omega={}&
 \frac{E}{2e_1e_2}b_\Omega b_\Omega
 +\frac{1}{8e_2^3}b_\Omega b_\Upsilon
 +\frac{1}{8e_1^3}b_\Upsilon b_\Omega,\\
 \delta b_\Upsilon={}&
 \frac{E(e_1-e_2)}{2e_1e_2^2}b_\Omega b_\Upsilon
 +\frac{E(e_2-e_1)}{2e_1^2e_2}b_\Upsilon b_\Omega\\
 &-\frac{E(e_1^2+e_2^2)}{8e_1^3e_2^3}
 b_\Upsilon b_\Upsilon.
\end{aligned}
\]

In particular, the (b_\Upsilon b_\Upsilon) coefficient in
\(\delta b_\Omega\) cancels to zero.  The result is the same in the incoming
and outgoing limits on this sector.  This is the explicit version of the
paper's statement that growing modes cancel from scattering data, but only
for the two-annihilator coefficient computed here; the oscillatory creation
and squeezed-vacuum sectors remain open.

A formal finite-wave-packet anti-Krein generator follows without fitting:

\[
 K_\downarrow=\frac{b_\Upsilon^\dagger\delta b_\Omega+
 b_\Omega^\dagger\delta b_\Upsilon}{2E},
 \qquad K=K_\downarrow-K_\downarrow^\dagger.
\]

It obeys (K^\dagger=-K), and its parent number-lowering commutator generates
the displayed map on finite nonendpoint wave packets.  This is not yet an
operator on the continuum Fock--Krein space.

## The next barrier is now precise

Contracting the two **ordered** daughter slots with the published off-diagonal
metric \([b_\Omega(e),b_\Upsilon^\dagger(e)]=2e\), before any Bose factor or
phase-space measure is applied, gives

\[
 G_{\Omega\Omega}=\frac{1}{8e_1^2e_2^2},\qquad
 G_{\Upsilon\Upsilon}=
 -\frac{2E^2(e_1-e_2)^2}{e_1^2e_2^2},
\]

\[
 G_{\Omega\Upsilon}=G_{\Upsilon\Omega}=
 -\frac{E^2(e_1^2+e_2^2-e_1e_2)}{2e_1^3e_2^3}.
\]

Its determinant is strictly negative for (e_1,e_2>0), as appropriate for a
raw Krein carrier rather than a positive probability.  More decisively, with
(e_1=zE), (e_2=(1-z)E), the cross entry has cubic poles at both
(z=0) and (z=1).  It is not an ordinary locally integrable splitting
density.  Therefore one cannot simply square and integrate this kernel to
obtain `1/48`.

The next calculation must construct a common plus/distributional endpoint
extension, include the oscillatory and vacuum-squeeze pieces of the
transported projector, and then evaluate the neutral quotient trace.  That
calculation, not a fitted finite matrix, will decide whether the dynamically
derived Gram is `1/48` per unordered pair.

## Claim boundary

The certificate establishes an exact reduced scalar coefficient kernel and a
formal finite-mode canonical lift.  It does not establish which Appendix C
display is mistyped, a full (R_{\pm\infty}) limit, a continuum dressed-state
or KLN theorem, the `1/48` coefficient, a complete NLO probability, a tensor
or BRST lift, or anything `LORENTZIAN-CAUSAL`.

Primary source: [Bateman--Turok, arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096),
Eq. (16) and Appendix C Eqs. (31)--(33).

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_rt_jordan_kernel.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_rt_jordan_kernel.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_rt_jordan_kernel
```

The producer uses exact Gaussian-rational Laurent polynomials.  The verifier
does not import it: it reconstructs the mode inversion at three rational
energy splittings, contracts the independent carrier table with the Krein
metric, checks the cubic endpoint residue, and rejects label, Gram, and claim
promotion mutations.

Final scoped receipt, 2026-08-10:

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` on producer and verifier | 0.03 s | 16,580 KB | PASS |
| 0 | `json.tool` on certificate and schema | 0.06 s | 14,892 KB | PASS |
| 1 producer | producer `--check` | 0.04 s | 21,292 KB | PASS, 18/18 |
| 1 independent | verifier | 0.10 s | 30,580 KB | PASS, 12/12 |
| 1 focused | 11 unit and mutation tests | 0.52 s | 30,536 KB | PASS |
| papers | Paper 05 final pass | 0.41 s | 50,936 KB | PASS |
| papers | Paper 06 final pass | 0.46 s | 50,780 KB | PASS |
| advisory | `ci/science-forge-shadow.sh` | 25.6 s | not reported | NOT A PASS: memory-capped `cbp callers/where` aborted; advisory wrapper returned |

Every command ran sequentially under `ulimit -v 500000`.  Paper 05 retains
only its three pre-existing small overfull boxes, at most 4.21 pt; Paper 06
has no overfull boxes.  Tier 2 was not run because no mathematical input,
shared operator, schema, or generated artifact used by another certificate
chain changed.  Tier 3 was not run because this is not a freeze, release,
paper-theorem promotion, or shared-core change.  The skipped tiers are not
passes.

The advisory Science Forge shadow rail was attempted under the same cap.  Its
`cbp callers` and `cbp where` subprocesses aborted, and the advisory wrapper
continued by design.  This is recorded as a failed/skipped audit component,
not as a pass; no claim or lifecycle state depends on it.

The completed Jordan-kernel work item is closed by an append-only
`OBSTRUCTED` event at the exact continuum-domain failure, and the endpoint
projector successor is active.  The event records the manual `event-v0`
fallback because the memory-capped Science Forge Go writer is known to fail
before execution while reserving its page-summary address space; the cap was
not relaxed and the coordinator launch is not claimed as a pass.
