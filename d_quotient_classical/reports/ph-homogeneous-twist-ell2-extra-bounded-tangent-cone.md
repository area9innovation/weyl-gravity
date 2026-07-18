# Plebanski--Hacyan homogeneous/twist--extra bounded tangent cone

The completed `k=0` homogeneous/twist times `ell=2` extra resonance matrix and
the five compact stabilizer moment maps have an exact common zero locus in the
declared nonzero-extra carrier.

Rotate the nonzero twist velocity to `B=beta e_z`.  Polynomial coefficient
elimination first gives `b=0`.  Every possible nonzero-`a` kernel of the
remaining time-linear pencil has a nonzero `polar_w1` constant output that
neither twist position nor `d` can cancel, so `a=0`.  On the resulting
12-dimensional leading kernel, one exact minor is

```text
(663364720915390660608/625) d^12,
```

hence `d=0`.  When the twist position has a transverse component the remaining
resonance kernel consists only of `m=0` tensors whose internal vector lies in
`ker(P)`.  Their extra angular moment is zero, so
`mu_J=-4 A cross B` eliminates that transverse component.  The aligned stratum
then has the full four extra multiplicities.

Consequently every nonzero-extra common-zero tangent is an `SO(3)` rotation of

```text
a=b=d=0,
C=x tensor |ell=2,m=0;n>,
A=alpha n,
B=beta n,
beta^2=Q_e^2/2+(2/3)X,
```

where `x` is any nonzero four-component axial/polar multiplicity vector,
`c,W_x` are spectators, and

```text
X=1296|x_a1|^2+(208/3)|x_a2|^2
  +22464|x_p1|^2+12288|x_p2|^2.
```

There is no additional off-axis branch in this carrier.  This closes the
necessary bounded common-zero locus, not second-order sufficiency.  The full
nonresonant `q2` output and exact off-shell block inverses are not exported, so
bounded and smooth-secular right inverses remain open; no compact-product
retarded BV complex is certified.
