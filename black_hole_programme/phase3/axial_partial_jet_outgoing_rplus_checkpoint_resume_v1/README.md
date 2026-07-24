# Outgoing `R+` mixed checkpoint and restart

Serializes the complete correlated `IvTaylor4_omega tensor dual_tau` state at
`r=63/2`, including all five exact retained coefficient matrices, IEEE-754
remainder endpoint bits, the common omega generator and the radial restart
metadata.

The restart source is generated solely from the checkpoint and advances the
next 16 panels to `r=31`.  Its terminal serialized state is compared exactly
with an independent 32-panel reference.  The checkpoint loader is also
compiled separately and round-tripped bit exactly.

Complementary columns, `K_plus`, `T_plus`, reflection, scattering and flux
remain fail closed.
