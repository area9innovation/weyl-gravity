# Exceptional dipole / `ell=2` extra difference matrix

All eight axisymmetric bilinear inputs were computed directly from the
four-dimensional Weyl--Maxwell Euler operator.  The exceptional mode is taken
on the conjugate `+omega_e` shell and the `ell=2` extra mode on the
`-2*omega_e` shell, so the output lies at `-omega_e` in the exceptional
`L=1` block.

After projection on the physical exceptional adjoint witnesses, six columns
vanish.  The two survivors are

```text
R_ax  = -(768/5) conj(x_exceptional_axial) y_extra_polar_e2,
R_pol = -(864/5) conj(x_exceptional_polar) y_extra_polar_e2.
```

Thus the same second polar `ell=2` extra amplitude is the unique axisymmetric
control for both exceptional `L=1` channels.  Combining with the certified
`d` pivots gives two explicit complex equations.  The remaining gate is to
assemble their `SO(3)` tensor, impose the exceptional `L=2` self-defect and
its `d` control column, and intersect with all five moment maps.  The current
certificate does not promote the complete bounded cone, nonzero momentum,
causal propagation, residual descent, particles or quantum states.
