# 108-row polarization-emitter unary and first recoil

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

At the zero-emitter background, the selected two-form model adds the unary
blocks

```text
A -> K_b^+       -g_b h_b dA,
K_b -> A^+       -g_b delta(h_b K_b),
K_b -> K_b^+     (delta d+m_b^2)K_b.
```

Maxwell gauge paths vanish by `d^2=0`, while the path to the Maxwell ghost
antifield vanishes by `delta^2=0`.  The cross blocks are adjoints because they
are derivatives of one Hessian.  Thus the new unary is nilpotent and cyclic
over the imported coefficientwise 84-row ring.  The certificate explicitly
lists rows 84--107 in two-form component order `01,02,03,12,13,23`, verifies
that the new odd pairing has rank 24, and gives the six row-indexed operator
blocks.

For the massive two-form Euler operator,

```text
G_E,+/- = (I+m^-2 d delta) G_(P2+m2),+/-
```

is an exact two-sided same-sided Green operator.  Coupling it to Maxwell and
expanding the formal Neumann inverse gives the first recoil term

```text
G_A^(2) = sum_b G_A g_b delta h_b G_Eb g_b h_b d G_A.
```

An independent three-channel fixture verifies both Euler inverse identities
through quadratic order and detects deletion of this term.  This establishes
the 108-row unary and first formal recoil Euler Green operator.  It does not
promote that Euler fixture to a full 108-row BV chain contraction: the
deformed inclusion, projection, and homotopy maps remain to be exported.  It
also does not yet choose two free emitter Cauchy data sets with a verified
rank-two detector matrix, evaluate the detector recoil integral, or include
emitter stress and clock backreaction.
