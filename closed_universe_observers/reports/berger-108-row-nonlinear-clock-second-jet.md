# Berger nonlinear clock second jet

The first-bidegree scalar unary gate now passes in the certified Berger
background quotient.  The generated correction has 95 PBW keys on 44 matrix
positions:

- 21 radial rod-action Hessian keys from
  `H_true=H+2 R H-3 R^2 eta+O(3)`;
- 9 Weyl-clock keys fixed by `q00(sigma)=-R` and the cotangent lift;
- 65 temporal-clock keys fixed by `q00(tau)=Theta` and the cotangent lift.

Every block is exactly odd-cyclic.  The radial block removes the old
output-27/input-4 coefficient `-49/20`.  The Weyl block removes all five free
`Theta* <- sigma` entries.  The temporal block removes all 43 free clock
doublet source entries and their paired metric-column defects.  The remaining
free `epsilon_R_squared` square has 261 PBW keys, but all 699 evaluated time
modes reduce exactly to zero in the pinned six-rod/Phi2 background differential
quotient.  The mixed `epsilon_R_squared*kappa` square remains freely zero.

This closes the unary activation gate requested by the nonlinear team.  It
authorizes the next apparatus calculation; it does not yet certify apparatus
`q2,q3`, `K_Berger` equivariance, observer-morphism stability, a restriction to
the second-order tangent cone, a physical-branch bridge, finite-parameter
causal propagation, or a quantum result.
