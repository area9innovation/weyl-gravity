# Complete two-angle BT coherence difference at q8

Certificate:
`REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED` for the relative coefficient.  The absolute
order-`lambda8` probabilities remain `NOT_COMPUTED`.

## Result

The unknown complete order-`lambda6` output does not obstruct the entire
coherent-versus-recorded probability difference at order `lambda8`.

On the selected tagged carrier write the complete output as

\[
 X(\lambda)=\lambda^2X_2+\lambda^4X_4+\lambda^6X_6
 +O(\lambda^8).
\]

Here every coefficient is complete: it includes all connected,
disconnected, loop, counterterm, source and detector terms allowed at that
order.  Exact total-Fock parity removes every odd selected block between the
declared odd input and output packet projectors.  Exhausting the five ordered
coefficient pairs whose orders add to eight therefore gives

\[
 (2,6),(3,5),(4,4),(5,3),(6,2),
\]

with the two odd pairs zero.  Up to Hermitian conjugation only two classes
survive.  For the recorded identity effect,

\[
 q_8[I_2]=2\operatorname{Re}\langle X_2,X_6\rangle
 +\lVert X_4\rVert^2.
\]

For the certified off-diagonal effect

\[
 E_\epsilon=P_++(1-\epsilon)P_-,\qquad 0<\epsilon\leq1,
\]

the corresponding coefficient is

\[
 q_8[E_\epsilon]
 =2\operatorname{Re}\langle X_2,E_\epsilon X_6\rangle
 +\langle X_4,E_\epsilon X_4\rangle.
\]

The fixed-energy leading angle vector is symmetric, so

\[
 E_\epsilon X_2=X_2.
\]

Self-adjointness now decides the apparently missing cross without computing
`X6`:

\[
 \langle X_2,E_\epsilon X_6\rangle
 =\langle E_\epsilon X_2,X_6\rangle
 =\langle X_2,X_6\rangle.
\]

It follows that the entire relative coefficient is

\[
 \boxed{
 q_8[E_\epsilon]-q_8[I_2]
 =-{\epsilon\over2}
 \lVert X_4(c_1)-X_4(c_2)\rVert^2\leq0.}
\]

At the pure coherent endpoint `epsilon=1`, the loss relative to the recorded
detector is exactly one half of the squared angle variation of the complete
order-`lambda4` output.

## Why this is the complete difference

The predecessor identified the displayed variance as the first known
detector-sensitive term, but left open whether other order-eight objects
could change it.  The exhaustive coefficient ledger shows that they cannot.

- The possible `X3-X5` cross is absent because both selected odd blocks
  vanish by exact Fock parity.
- The `X2-X6` cross exists and is needed for either absolute coefficient,
  but it is identical for both effects because the effect fixes `X2`.
- The `X4` norm is therefore the only detector-sensitive class at this
  order, and its antisymmetric projection is exactly the variance above.

This reasoning does not assume a special value of `X6`.  It applies to the
complete complex output on every internal positive-output coordinate because
the angle effect is tensored with the identity there.

## Exact separating fixture

Take

\[
 \epsilon={2\over5},\qquad
 X_2=\left({2\over3}-{i\over5}\right)(1,1),
\]

\[
 X_4=(1+2i,-3+i),\qquad
 X_6=\left({7\over4}-{2i\over3},-{5\over6}+{9i\over7}\right).
\]

Direct exact convolution gives the same `X2-X6` cross, `307/315`, for both
detectors.  The complete recorded fixture coefficient is `5032/315`, the
coherent one is `3961/315`, and their difference is `-17/5`, exactly the
variance prediction.

## What remains unknown

This relative theorem does not compute either absolute coefficient.  Those
still require:

1. the complete `X4` Gram data, including the separate fibre norms and their
   cross-angle overlap; and
2. the complete `2 Re<X2,X6>` interference, including all amplitude-order-six
   dynamics and renormalization conditions.

Knowing a difference without knowing either absolute value is not a logical
gap.  The missing term is common to both measurements and cancels exactly in
their comparison.

## Physical boundary

The sign has a direct operational meaning: among this detector family,
coherent erasure cannot increase the order-eight coefficient relative to
recording the angle.  It removes the antisymmetric-angle part of `X4`.

It does not follow that BT dynamics selects `epsilon`, the relative phase or
this apparatus.  The result is restricted to two orthogonal equal-normalized
hard modes.  It supplies no continuum-angle detector, forward endpoint,
real--virtual/KLN completion, all-time scattering operator, Eq. (19), metric
BV--BRST transfer, restored QME, residual transfer, gravity result or
anything `LORENTZIAN-CAUSAL`.  No literature-priority claim is made.

## Independent rail

The producer uses symbolic arbitrary complex `X2`, `X4` and `X6` coordinates
and exhausts coefficient pairs algebraically.  The independent verifier uses
only exact `Fraction` arithmetic.  It reconstructs the probability
coefficient by direct polynomial convolution for a separating grid of
complex amplitudes and four nonzero detector strengths.  It independently
rechecks input hashes, parity data, the exact fixture and every claim
boundary.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.03 s, 14,732 KB peak RSS.
- The first final `git diff --check` inherited the scientific memory cap and
  failed because Git could not create its threaded lstat helper.  It is not
  counted as a pass; the same scoped diff check passed immediately outside
  the scientific address-space shell, where Git bookkeeping is run.
- Exact producer replay: PASS 24/24, 0.39 s, 68,240 KB peak RSS.
- Independent `Fraction`/convolution verifier: PASS 27/27, 0.20 s,
  24,004 KB peak RSS.
- Scoped tests: PASS 25/25 in 1.34 s (1.41 s enclosing wall time),
  24,868 KB peak RSS.  These include 24 adversarial mutations.
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each under the
  same cap.  The final passes took 0.48 s and 0.51 s at 50,668 KB and
  50,728 KB peak RSS.  The PDFs have 61 pages (668,050 bytes) and 57 pages
  (649,781 bytes), respectively.  No new overfull box is introduced by the
  inserted theorem; the logged overfull boxes predate these locations.
- Tier 3: FAIL-CLOSED, 2,317 tests in 688.468 s, with 31 failures and 9
  skips; the enclosing timed process took 689.50 s and peaked at 391,316 KB.
  Every new q8 producer, verifier, schema and mutation test passed.  The
  failures are older content-addressed producer, verifier and chain-import
  rails and do not establish a repository-wide pass.
- The advisory Science Forge shadow invocation was manually terminated after
  approximately 53 s because it stalled inside the external `cbp` grep shim
  after two helper calls aborted.  It is recorded as STALLED/NOT A PASS; no
  bridge-audit or coverage result is claimed from this invocation.

Tier 3 was required because Papers V and VI strengthen the relative q8
statement from a known term to a complete coefficient.  Its older failures
remain failures and do not alter the independently passing scoped chain.

Commands:

    ulimit -v 500000; python3 reverse_physics/bt_two_angle_q8_coherence_difference.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_q8_coherence_difference.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_q8_coherence_difference
