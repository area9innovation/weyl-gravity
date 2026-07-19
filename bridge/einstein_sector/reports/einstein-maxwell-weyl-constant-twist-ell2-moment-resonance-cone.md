# Constant-twist ell=2 moment/resonance cone

For a nonzero constant twist rotated to the `z` axis, the complete shellwise
resonance kernel has sixteen complex dimensions: two axial/polar `m=0`
coefficients on each Einstein shell and twelve extra-primary coefficients.
The extra internal Gram form in direct source coordinates is

```text
G=diag(1296,208/3,9,22464).
```

Its nonzero-`m` internal kernel is

```text
K=span{polar_e1,-4*sqrt(3)*axial_e1+15*polar_e2},
```

and the full extra resonance kernel decomposes orthogonally as
`(K tensor V_2) direct_sum (K_perp tensor |m=0>)`.  The second summand is
rotationally neutral.  Hence the complete stabilizer intersection is given by
the usual spin-two equations on the two copies of `K`, together with

```text
(6+2*sqrt(3))*A_plus+(16/3)*A_extra
  -(6-2*sqrt(3))*A_minus=0.
```

These equations are necessary and sufficient for simultaneous vanishing of
`H,J_1,J_2,J_3` and every same-shell constant-twist position resonance in the
declared carrier.  A non-axisymmetric witness has
`c_-2=c_2=polar_e1`, `A_extra=18`, `A_plus=0`, and
`A_minus=24+8*sqrt(3)`.  Thus nonzero twist does not force the common cone to
the axisymmetric face.

The resonance/moment cone is not yet a bounded second-order extension
theorem.  The remaining gate is the complete nonresonant `L=1,3`
twist--wave inverse ledger and its combination with the wave self-source
correction.
