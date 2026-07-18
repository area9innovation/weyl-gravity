# Berger complete per-shell recoil operator word

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The detector-selected preparation and recoil chain is now a typed generic
Peter–Weyl shell contraction.  Each shell has a Maxwell one-form block of
dimension `4(two_j+1)`, an emitter/two-form block of dimension
`6(two_j+1)`, and `two_j+1` passive right columns.  The exact word is

```text
tilde_u_b -> U_Eb -> h_b -> delta_2 -> G_A,ret -> d_1 -> h_c
          -> G_Ec,ret -> h_c -> delta_2 -> G_A,ret -> d_1 -> Q_a.
```

Here `G_Ec=(I+m_c^-2 d_1 delta_2)G_(wave_2+m_c^2)`.  Both occurrences of
`h_c` are necessary, and the switched coderivative contains the fixed
`+(partial_t h_c) alpha` spatial component.  The eight `(a,b,c)` words carry
`g_b g_c^2`; summing `c` gives four `(a,b)` streams.  Peter–Weyl
reconstruction uses `(two_j+1)/Vol_Berger` and sums every passive column.
The tail factor is indexed by the feedback emitter: each channel uses
`D_a C_c(m_c) E_A,b`, and the aggregate envelope sums its two `c` terms.

This completes the symbolic scalar integrand for arbitrary positive masses.
It does not choose numerical masses or couplings, declare a stopping goal, or
evaluate the four recoil intervals.
