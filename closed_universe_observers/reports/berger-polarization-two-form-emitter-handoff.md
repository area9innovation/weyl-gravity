# Polarization two-form emitter handoff

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The selected effective emitter consists of two real massive two-forms
`K_0,K_1` on the invariant clock metric `gHat`:

```text
S_emit = -1/2 sum_b ( <dK_b,dK_b> + m_b^2 <K_b,K_b> )
         - sum_b g_b <h_b(Theta) K_b,dA>.
```

This is the standard massive two-form action, with no two-form gauge symmetry
for `m_b^2>0`.  Its Euler operator is `delta d+m_b^2`.  Taking its divergence
supplies the constraint on `delta K_b`; adjoining the derivative of that
constraint yields the normally hyperbolic `P_2+m_b^2` reduction.  Thus the
causal wave operator is derived rather than inserted as a physical
gauge-fixing term.  The compact functions `h_b(Theta)` switch the coupling
relationally.  Localized Cauchy data prepare each emitter without an external
spacetime drive.

The Maxwell current and reciprocal recoil equation are

```text
J_b = g_b delta_gHat(h_b K_b),       delta_gHat J_b=0,
(delta_gHat d+m_b^2) K_b = g_b h_b dA.
```

Thus conservation is off-shell and Maxwell gauge invariance is manifest.
The two cross blocks are adjoints from the same action.  Since they are first
order, the coupled gauge-fixed principal symbol remains the common `gHat`
wave cone.

Each two-form has six components.  Two fields and their cotangent partners
add 24 rows to the 84-row apparatus, producing ranks `(6,48,48,6)` and 108
rows total.  This document freezes that carrier and model.  The complete
108-row differential, causal chain contraction, actual emitted record rank,
recoil coefficient, emitter stress backreaction, and full Dirac algebra are
the next construction rather than claims of this handoff.
