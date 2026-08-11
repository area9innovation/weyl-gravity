# BT oscillatory radical: no neutral endpoint matching

**Result:** `CLASSIFIED`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1`](../certificates/REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json)

## Result

On the published **fixed-vacuum oscillator grading**, the oscillatory and
squeezed-vacuum sectors cannot fix the three neutral endpoint constants.  In
Bateman--Turok's charge convention, creation and annihilation operators of the
same field carry the same boost charge:

\[
q(b_\Omega)=+1,
\qquad q(b_\Upsilon)=q(b_\Upsilon^\dagger)=-1.
\]

Consequently the oscillatory term in Eq. (33), which becomes
(e^{2iEt}b_\Upsilon^\dagger), has charge (-1), while every term in the
squeeze generator (Q_t) has charge (-2).  The BT/Krein dagger preserves
this charge.  Bateman--Turok further state that the transported remainder has
no positive-charge operators, and the independent radical-closure certificate
proves that tensor powers of their off-diagonal completeness kernel preserve
the strictly negative trace radical.

Every nontrivial product containing an oscillatory or (Q_t) insertion
therefore remains at strictly negative charge and has zero invariant trace.
It cannot change the charge-zero coefficients multiplying

\[
\delta_0+\delta_1,\qquad
\delta'_0-\delta'_1,\qquad
\delta''_0+\delta''_1.
\]

This closes the proposed oscillatory matching route by an exact charge
obstruction.  It does not rule out a neutral contribution from the full
pushforward projector.

The successor certificate
`REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1` sharpens that last boundary.
On the covariant broken-vacuum orbit carrier, the oscillatory term carries the
required factor $Z^2$ and the squeeze $Z^2(b_\Upsilon^\dagger)^2$ has total
charge zero.  Hence the theorem above remains valid on its declared
fixed-vacuum grading, but it cannot be used to discard the zero-mode-completed
neutral squeeze.  Conversely, setting $Z=1$ is not an invariant charge
quotient.  The full zero-mode trace remains missing.

## The actual missing object

The Letter publishes the pullback (R_t^\dagger bR_t), but the probability
requires the pushforward (R_tP R_t^\dagger).  It asserts only

\[
R_tR_t^\dagger=1,
\]

not (R_t^\dagger R_t=1).  Hence formally inverting the oscillator pullback
does not determine the coisometric range/defect contribution to the
pushforward projector.  The required data are (R_t^\dagger R_t),
(ker R_t), or the deferred order-(lambda) proof of Eq. (19).  A search on
2026-08-10 found no public arXiv version of the promised companion paper.

The neutral endpoint constants, `1/48` Gram, full NLO quotient trace, and
physical probability therefore remain uncomputed.  No `LORENTZIAN-CAUSAL`
claim is made.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_oscillatory_radical_no_matching.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_oscillatory_radical_no_matching.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_oscillatory_radical_no_matching
```

All rails use exact rational charge algebra.  The producer checks 13/13, the
independent verifier 7/7, and four focused/mutation tests pass under the
500000 KB cap.  Tier 2 and Tier 3 were not run; this is a scoped classification,
not a shared-input change, freeze, release, or theorem promotion.

Primary source: [Bateman--Turok, arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096),
Eq. (19) and Appendix C Eqs. (33)--(34).
