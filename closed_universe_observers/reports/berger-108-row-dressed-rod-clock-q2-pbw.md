# Dressed six-rod temporal clock correction to `q2`

The six detector rods have nonstationary certified backgrounds.  Their linear
clock dressing is therefore not the identity map:

```text
R_dressed = R_raw - Theta e0(Rbar).
```

Preservation of the canonical one-form fixes the reciprocal cotangent shift
of `Theta_star`.  Exact differential-operator conjugation maps the full raw
temporal rod gauge orbit back to the already-certified spatial-only unary
operator with zero defect, so this repair does not reopen the unary gate.

The same conjugation applied to the raw full-Diff scalar BV tensor yields a
192-key additive `q2` correction on 17 output rows.  Its coefficients are
generated from the raw action and the background-dependent clock chart; none
is selected from the arity obstruction.  With this source assembled, the
former `+e0 e1 R0_1` witness and all six rod/rod-cotangent defect rows vanish.

The complete arity-two gate remains fail-closed on a separate typed
Maxwell--emitter common-action orbit.  Arity three, `K_Berger`, observer
morphism stability, the second-order-cone response, and the physical branch
remain inactive.
