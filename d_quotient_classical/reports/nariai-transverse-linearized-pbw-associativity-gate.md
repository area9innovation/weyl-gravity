# Transverse linearized PBW associativity gate

The current jet-aware first-variation PBW backend is not associative on the
typed triple `M_parent o L1_corrected o (K p0)`.  The base associator is zero,
but its first variation contains `209`
coefficients.  Its first normalized witness is

```text
word=[], row=0, column=0
coefficient=7*sqrt(2)/16, multiplier=8*sqrt(2)/7
normalized value=1
```

This is decisive because `Phi=M L1` is replayed exactly, while the shifted
chain follows abstractly from `M d_parent=0`, `d_aut L0=L1 K`, `p0 L0=1`, and
`p0(1-L0 p0)=0`.  Thus the previously reported 207-coefficient shifted-chain
defect is a backend artifact, not an operator obstruction.  The Phi-only rank
screens remain valid only as linear algebra relative to that superseded
backend target.

The next gate is a coefficient-jet-aware associative PBW replay.  No
transverse rank-310 SDR or causal theorem is promoted here.
